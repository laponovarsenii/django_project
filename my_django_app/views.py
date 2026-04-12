from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from my_django_app.models import Task, SubTask
from my_django_app.serealizers.task_serealizer import (
    TaskSerializer,
    TaskDetailSerializer,
    SubTaskSerializer,
    SubTaskCreateSerializer,
)


def hello(request):
    your_name = "Arsenii"
    return HttpResponse(f"Hello {your_name}")


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Task.objects.all()

        status_value = self.request.query_params.get('status')
        deadline_value = self.request.query_params.get('deadline')

        if status_value:
            queryset = queryset.filter(status=status_value)

        if deadline_value:
            queryset = queryset.filter(deadline=deadline_value)

        return queryset


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer


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

    queryset = Task.objects.all()

    if weekday:
        weekday_number = weekdays_map.get(weekday.lower())
        if weekday_number is None:
            return Response(
                {'message': 'Invalid weekday value'},
                status=400
            )
        queryset = queryset.filter(deadline__week_day=weekday_number)

    serializer = TaskSerializer(queryset, many=True)
    return Response(serializer.data)


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


class SubTaskListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    pagination_class = SubTaskPagination

    def get_queryset(self):
        queryset = SubTask.objects.all().order_by('-created_at')

        task_title = self.request.query_params.get('task_title')
        status_value = self.request.query_params.get('status')
        deadline_value = self.request.query_params.get('deadline')

        if task_title:
            queryset = queryset.filter(task__title=task_title)

        if status_value:
            queryset = queryset.filter(status=status_value)

        if deadline_value:
            queryset = queryset.filter(deadline=deadline_value)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubTaskSerializer
        return SubTaskCreateSerializer


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubTaskSerializer
        return SubTaskCreateSerializer