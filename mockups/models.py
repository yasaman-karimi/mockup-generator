from django.db import models
from django.conf import settings


class MockupJob(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("STARTED", "STARTED"),
        ("SUCCESS", "SUCCESS"),
        ("FAILURE", "FAILURE"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mockup_jobs",
    )
    task_id = models.CharField(max_length=100, blank=True, null=True)
    text = models.TextField()
    font = models.CharField(max_length=100, blank=True, null=True)
    text_color = models.CharField(max_length=7, default="#000000")
    shirt_colors = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Job {self.id} ({self.status})"


class Mockup(models.Model):
    COLOR_CHOICES = (
        ("yellow", "yellow"),
        ("black", "black"),
        ("white", "white"),
        ("blue", "blue"),
    )

    job = models.ForeignKey(MockupJob, on_delete=models.CASCADE, related_name="mockups")
    text = models.TextField()
    font = models.CharField(max_length=100, blank=True, null=True)
    text_color = models.CharField(max_length=7, default="#000000")
    shirt_color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    image = models.ImageField(upload_to="mockups/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Mockup {self.id} - {self.shirt_color}"
