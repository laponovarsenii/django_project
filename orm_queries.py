import os
import django
from datetime import timedelta


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject.settings")
django.setup()

from django.utils import timezone
from my_django_app.models import Task, SubTask



today = timezone.localdate()

# -----------------------
# CREATE (Создание)
# -----------------------
task = Task.objects.create(
    title="Prepare presentation",
    description="Prepare materials and slides for the presentation",
    status="New",
    deadline=today + timedelta(days=3),
)

SubTask.objects.create(
    task=task,
    title="Gather information",
    description="Find necessary information for the presentation",
    status="New",
    deadline=today + timedelta(days=2),
)

SubTask.objects.create(
    task=task,
    title="Create slides",
    description="Create presentation slides",
    status="New",
    deadline=today + timedelta(days=1),
)

# -----------------------
# READ (Чтение)
# -----------------------

# 1) Tasks со статусом "New".
new_tasks = Task.objects.filter(status="New")
print("\n--- Tasks with status='New' ---")
for t in new_tasks:
    print(f"[Task #{t.id}] {t.title} | status={t.status} | deadline={t.deadline}")

# 2) SubTasks с просроченным статусом "Done":
overdue_done_subtasks = SubTask.objects.filter(
    status="Done",
    deadline__lt=today,
)
print("\n--- SubTasks with status='Done' but due date has expired ---")
for st in overdue_done_subtasks:
    print(
        f"[SubTask #{st.id}] {st.title} | status={st.status} | deadline={st.deadline} | task={st.task_id}"
    )

# -----------------------
# UPDATE (Изменение)
# -----------------------

# 1) Изменить статус "Prepare presentation" на "In progress".
Task.objects.filter(title="Prepare presentation").update(status="In progress")

# 2) Измените срок выполнения для "Gather information" на два дня назад.
SubTask.objects.filter(title="Gather information", task=task).update(
    deadline=today - timedelta(days=2)
)

# 3) Измените описание для "Create slides" на "Create and format presentation slides".
SubTask.objects.filter(title="Create slides", task=task).update(
    description="Create and format presentation slides"
)


task.refresh_from_db()
print("\n--- After updates ---")
print(f"[Task #{task.id}] {task.title} | status={task.status} | deadline={task.deadline}")

for st in SubTask.objects.filter(task=task).order_by("id"):
    print(
        f"[SubTask #{st.id}] {st.title} | status={st.status} | deadline={st.deadline} | desc={st.description}"
    )

# -----------------------
# DELETE (Удаление)
# -----------------------
# 1) Удалите задачу "Prepare presentation" и все ее подзадачи.

Task.objects.filter(title="Prepare presentation").delete()

print("--- Deleted task Prepare presentation ---")

