from django.contrib import admin
from .models import Mockup, MockupJob


@admin.register(MockupJob)
class MockupJobAdmin(admin.ModelAdmin):
    list_display = ("id", "task_id", "status", "text", "created_at")
    search_fields = ("task_id", "text")


@admin.register(Mockup)
class MockupAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "shirt_color", "created_at")
    list_filter = ("shirt_color",)
    search_fields = ("text",)
