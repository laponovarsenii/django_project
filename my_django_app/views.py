from django.http import HttpResponse

from django.http import HttpResponse
from django.core.serializers import serialize
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from my_django_app.serealizers.task_serealizer import TaskSerializer
from my_django_app.models import Task

def hello(request):
    your_name = "Arsenii"
    return HttpResponse(f"Hello {your_name}")

@api_view(['POST'])
def create_new_task(request) ->Response:
    serializer = TaskSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_tasks(request, pk=None) ->Response:

    if pk == None:
        tasks = Task.objects.all()

        if not tasks:
            return Response(
                data=[],
                status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(tasks, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
    )
    else:
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist as err:
            return Response(
                data={
                    'message': f"Task with id {pk} does not exist",
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TaskSerializer(task)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

from django.db.models import Count

@api_view(['GET'])
def task_stats(request):
    # Debug print: выведите все id/status
    for t in Task.objects.all():
        print(f"ID={t.id}, status=<{t.status}>")

    # Считаем все задачи
    total_tasks = Task.objects.count()

    # Считаем задачи по каждому статусу (группируем по всем, какие есть!)
    status_counts = {}
    for t in Task.objects.values_list('status', flat=True).distinct():
        status_counts[t] = Task.objects.filter(status=t).count()

    # Считаем просроченные задачи
    overdue_tasks = Task.objects.filter(
        deadline__lt=timezone.now()
    ).exclude(status='completed').count()

    data = {
        "total_tasks": total_tasks,
        "tasks_by_status": status_counts,
        "overdue_tasks": overdue_tasks,
    }
    return Response(data)
