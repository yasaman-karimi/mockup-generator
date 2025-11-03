from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mockup, MockupJob


class GenerateMockupSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=500)
    font = serializers.CharField(
        max_length=100, required=False, allow_null=True, allow_blank=True
    )
    text_color = serializers.RegexField(
        regex=r"^#[0-9A-Fa-f]{6}$", required=False, default="#000000"
    )
    shirt_color = serializers.ListField(
        child=serializers.ChoiceField(choices=["yellow", "black", "white", "blue"]),
        required=False,
        allow_empty=True,
    )

    def validate(self, attrs):
        # default to all colors if not provided
        if not attrs.get("shirt_color"):
            attrs["shirt_color"] = ["yellow", "black", "white", "blue"]
        return attrs


class MockupSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Mockup
        fields = [
            "id",
            "text",
            "image_url",
            "font",
            "text_color",
            "shirt_color",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request is not None and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class TaskStatusResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    status = serializers.CharField()
    results = MockupSerializer(many=True, required=False)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_username(self, value):
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user

    def to_representation(self, instance):
        return {"id": instance.id, "username": instance.username}
