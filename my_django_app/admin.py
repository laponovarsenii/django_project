from django.contrib import admin

from .models import Task, SubTask, Category


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "deadline", "created_at")
    list_filter = ("status", "created_at", "deadline", "categories")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    filter_horizontal = ("categories",)
    date_hierarchy = "created_at"


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "task", "status", "deadline", "created_at")
    list_filter = ("status", "created_at", "deadline", "task")
    search_fields = ("title", "description", "task__title")
    ordering = ("-created_at",)
    autocomplete_fields = ("task",)
    date_hierarchy = "created_at"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)