from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import settings


class Task(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_PENDING = "pending"
    STATUS_BLOCKED = "blocked"
    STATUS_DONE = "done"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_PENDING, "Pending"),
        (STATUS_BLOCKED, "Blocked"),
        (STATUS_DONE, "Done"),
    ]

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    categories = models.ManyToManyField("Category", related_name="tasks", blank=True)

    last_notified_status = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,  # временно True, чтобы миграция не сломала существующие строки
        blank=True,
    )

    deadline = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    created_date = models.DateField(editable=False, default=timezone.localdate)

    class Meta:
        db_table = "task_manager_task"
        ordering = ["-created_at"]
        verbose_name = "Task"

    def __str__(self):
        return self.title


class SubTask(models.Model):
    STATUS_NEW = Task.STATUS_NEW
    STATUS_IN_PROGRESS = Task.STATUS_IN_PROGRESS
    STATUS_PENDING = Task.STATUS_PENDING
    STATUS_BLOCKED = Task.STATUS_BLOCKED
    STATUS_DONE = Task.STATUS_DONE

    STATUS_CHOICES = Task.STATUS_CHOICES

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subtasks',
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )

    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_manager_subtask"
        ordering = ["-created_at"]
        verbose_name = "SubTask"

    def __str__(self):
        return self.title


class CategoryActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CategoryActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "task_manager_category"
        verbose_name = "Category"

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])