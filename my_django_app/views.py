from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from my_django_app.models import Task, SubTask
from my_django_app.serealizers.task_serealizer import (
    TaskSerializer,
    SubTaskSerializer,
    SubTaskCreateSerializer,
)


def hello(request):
    your_name = "Arsenii"
    return HttpResponse(f"Hello {your_name}")


@api_view(['POST'])
def create_new_task(request) -> Response:
    serializer = TaskSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_tasks(request, pk=None) -> Response:
    if pk is None:
        tasks = Task.objects.all()

        if not tasks:
            return Response(
                data=[],
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TaskSerializer(tasks, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
    else:
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
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


@api_view(['GET'])
def task_stats(request):
    total_tasks = Task.objects.count()

    status_counts = {}
    for t in Task.objects.values_list('status', flat=True).distinct():
        status_counts[t] = Task.objects.filter(status=t).count()

    overdue_tasks = Task.objects.filter(
        deadline__lt=timezone.now()
    ).exclude(status='completed').count()

    data = {
        "total_tasks": total_tasks,
        "tasks_by_status": status_counts,
        "overdue_tasks": overdue_tasks,
    }
    return Response(data)


class SubTaskListCreateView(APIView):
    def get(self, request):
        subtasks = SubTask.objects.all()
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    def get_object(self, pk):
        try:
            return SubTask.objects.get(pk=pk)
        except SubTask.DoesNotExist:
            return None

    def get(self, request, pk):
        subtask = self.get_object(pk)
        if subtask is None:
            return Response(
                {'message': f'SubTask with id {pk} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        subtask = self.get_object(pk)
        if subtask is None:
            return Response(
                {'message': f'SubTask with id {pk} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubTaskCreateSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subtask = self.get_object(pk)
        if subtask is None:
            return Response(
                {'message': f'SubTask with id {pk} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
