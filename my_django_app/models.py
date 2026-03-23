from django.db import models
from django.utils import timezone


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

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
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


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "task_manager_category"
        verbose_name = "Category"

    def __str__(self):
        return self.name