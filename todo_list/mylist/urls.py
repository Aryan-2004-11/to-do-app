"""
URL configuration for mylist.
Defines routes for both API endpoints and web interface.
"""

from django.urls import path
from .views import (
    TaskListView, TaskCreateView, TaskDetailView, 
    TaskEditView, TaskDeleteView
)
from .api_views import (
    TaskListAPIView, TaskDetailAPIView, TaskStatisticsAPIView
)

urlpatterns = [
    # =====================
    # Web Interface Routes
    # =====================
    path('', TaskListView.as_view(), name='task_list'),
    path('tasks/new/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:task_id>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:task_id>/edit/', TaskEditView.as_view(), name='task_edit'),
    path('tasks/<int:task_id>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    
    # =====================
    # API Routes
    # =====================
    # Task list and create
    path('api/tasks/', TaskListAPIView.as_view(), name='api_task_list'),
    
    # Task statistics (must be before task_id route to avoid conflict)
    path('api/tasks/stats/', TaskStatisticsAPIView.as_view(), name='api_task_stats'),
    
    # Single task operations
    path('api/tasks/<int:task_id>/', TaskDetailAPIView.as_view(), name='api_task_detail'),
]
