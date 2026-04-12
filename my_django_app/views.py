from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

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
def tasks_by_weekday(request):
    weekday = request.query_params.get('weekday')

    weekdays_map = {
        'monday': 2,
        'tuesday': 3,
        'wednesday': 4,
        'thursday': 5,
        'friday': 6,
        'saturday': 7,
        'sunday': 1,
        'понедельник': 2,
        'вторник': 3,
        'среда': 4,
        'четверг': 5,
        'пятница': 6,
        'суббота': 7,
        'воскресенье': 1,
    }

    tasks = Task.objects.all()

    if weekday:
        weekday_number = weekdays_map.get(weekday.lower())
        if weekday_number is None:
            return Response(
                {'message': 'Invalid weekday value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        tasks = tasks.filter(deadline__week_day=weekday_number)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


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


class SubTaskPagination(PageNumberPagination):
    page_size = 5


class SubTaskListCreateView(APIView):
    def get(self, request):
        task_title = request.query_params.get('task_title')
        status_filter = request.query_params.get('status')

        subtasks = SubTask.objects.all().order_by('-created_at')

        if task_title:
            subtasks = subtasks.filter(task__title=task_title)

        if status_filter:
            subtasks = subtasks.filter(status=status_filter)

        paginator = SubTaskPagination()
        paginated_subtasks = paginator.paginate_queryset(subtasks, request)
        serializer = SubTaskSerializer(paginated_subtasks, many=True)
        return paginator.get_paginated_response(serializer.data)

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