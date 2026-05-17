from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskListCreateView, TaskRetrieveUpdateDestroyView,
    SubTaskListCreateView, SubTaskRetrieveUpdateDestroyView,
    CategoryViewSet, tasks_by_weekday, task_stats,
    MyTasksListView, MySubTasksListView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='tasks-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='tasks-detail'),
    path('tasks/my/', MyTasksListView.as_view(), name='tasks-my'),
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtasks-list-create'),
    path('subtasks/<int:pk>/', SubTaskRetrieveUpdateDestroyView.as_view(), name='subtasks-detail'),
    path('subtasks/my/', MySubTasksListView.as_view(), name='subtasks-my'),
    path('tasks/by-weekday/', tasks_by_weekday, name='tasks-by-weekday'),
    path('tasks/stats/', task_stats, name='task-stats'),
    path('', include(router.urls)),
]