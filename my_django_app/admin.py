from django.contrib import admin

from .models import Task, SubTask, Category


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ("title", "description", "status", "deadline")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "short_title", "status", "deadline", "created_at")
    list_filter = ("status", "created_at", "deadline", "categories")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    filter_horizontal = ("categories",)
    date_hierarchy = "created_at"
    inlines = (SubTaskInline,)

    @admin.display(description="Заголовок")
    def short_title(self, obj: Task) -> str:
        title = obj.title or ""
        return f"{title[:10]}..." if len(title) > 10 else title


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "task", "status", "deadline", "created_at")
    list_filter = ("status", "created_at", "deadline", "task")
    search_fields = ("title", "description", "task__title")
    ordering = ("-created_at",)
    autocomplete_fields = ("task",)
    date_hierarchy = "created_at"
    actions = ("mark_done",)

    @admin.action(description="Отметить выбранные подзадачи как выполненные")
    def mark_done(self, request, queryset):
        queryset.update(status=SubTask.STATUS_DONE)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)