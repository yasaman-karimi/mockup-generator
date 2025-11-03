from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import GenerateMockupView, TaskStatusView, MockupListView, RegisterView

urlpatterns = [
    path(
        "api/v1/mockups/generate/",
        GenerateMockupView.as_view(),
        name="generate-mockups",
    ),
    path("api/v1/tasks/<str:task_id>/", TaskStatusView.as_view(), name="task-status"),
    path("api/mockups/", MockupListView.as_view(), name="mockup-list"),
    # Auth
    path("api/v1/auth/register/", RegisterView.as_view(), name="register"),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
]
