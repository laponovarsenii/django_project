"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from my_django_app.views import (
    hello,
    task_stats,
    tasks_by_weekday,
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    SubTaskListCreateView,
    SubTaskRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", hello),

    path("tasks/", TaskListCreateView.as_view()),
    path("tasks/<int:pk>/", TaskRetrieveUpdateDestroyView.as_view()),
    path("tasks-by-weekday/", tasks_by_weekday),
    path("task_stats/", task_stats),

    path("subtasks/", SubTaskListCreateView.as_view()),
    path("subtasks/<int:pk>/", SubTaskRetrieveUpdateDestroyView.as_view()),
]