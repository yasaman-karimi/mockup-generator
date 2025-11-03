from celery.result import AsyncResult
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Mockup, MockupJob
from .serializers import (
    GenerateMockupSerializer,
    MockupSerializer,
    RegisterSerializer,
)
from .tasks import generate_mockups_task


class GenerateMockupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateMockupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = MockupJob.objects.create(
            user=request.user,
            text=serializer.validated_data["text"],
            font=serializer.validated_data.get("font"),
            text_color=serializer.validated_data.get("text_color", "#000000"),
            shirt_colors=serializer.validated_data.get(
                "shirt_color", ["yellow", "black", "white", "blue"]
            ),
            status="PENDING",
        )

        task = generate_mockups_task.delay(job.id)
        job.task_id = task.id
        job.save(update_fields=["task_id"])

        return Response(
            {
                "task_id": task.id,
                "status": "PENDING",
                "message": "Image generation has started",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class TaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id: str):
        job = get_object_or_404(MockupJob, task_id=task_id, user=request.user)
        async_result = AsyncResult(task_id)
        state = async_result.state or job.status

        results = []
        if state == "SUCCESS" or job.status == "SUCCESS":
            for m in job.mockups.order_by("-created_at").select_related("job"):
                results.append(
                    {
                        "image_url": (
                            request.build_absolute_uri(m.image.url) if m.image else None
                        ),
                        "created_at": m.created_at.isoformat().replace("+00:00", "Z"),
                    }
                )

        return Response(
            {
                "task_id": task_id,
                "status": state,
                "results": results,
            }
        )


class MockupListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MockupSerializer

    def get_queryset(self):
        return (
            Mockup.objects.select_related("job")
            .filter(job__user=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            serializer.to_representation(user), status=status.HTTP_201_CREATED
        )
