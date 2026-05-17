from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, filters, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from my_django_app.models import Task, SubTask, Category
from my_django_app.serealizers.task_serealizer import (
    TaskSerializer,
    TaskDetailSerializer,
    SubTaskSerializer,
    SubTaskCreateSerializer,
    CategorySerializer,
    CategoryCreateSerializer,
)

from .permissions import (
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsAuthenticatedCreateReadOnly,
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
    permission_classes = [IsAuthenticatedCreateReadOnly] 

    def get_queryset(self):
        queryset = Task.objects.all()

        status_value = self.request.query_params.get('status')
        deadline_value = self.request.query_params.get('deadline')

        if status_value:
            queryset = queryset.filter(status=status_value)

        if deadline_value:
            queryset = queryset.filter(deadline=deadline_value)

        return queryset

    def perform_create(self, serializer):

        for owner_field in ('author', 'user', 'owner', 'created_by', 'creator'):
            if owner_field in serializer.fields or hasattr(serializer.Meta.model, owner_field):
                serializer.save(**{owner_field: self.request.user})
                return
        try:
            serializer.save(owner=self.request.user)
        except TypeError:
            serializer.save()

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]


@api_view(['GET'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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


class SubTaskListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticatedCreateReadOnly]

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

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except TypeError:
            serializer.save()


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubTaskSerializer
        return SubTaskCreateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateSerializer
        return CategorySerializer

    @action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        return Response({
            'category_id': category.id,
            'category_name': category.name,
            'tasks_count': category.tasks.count(),
        })

class MyTasksListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user).order_by('-created_at')


class MySubTasksListView(generics.ListAPIView):
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubTask.objects.filter(owner=self.request.user).order_by('-created_at')