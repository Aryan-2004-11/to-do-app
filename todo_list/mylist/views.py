"""
Template Views for Task Management Web Interface.
Renders HTML templates and integrates with API endpoints.
"""

import logging
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse

from .database import (
    get_all_tasks, get_task_by_id, create_task, update_task, delete_task,
    get_task_statistics, TaskNotFoundError, DatabaseError, init_database
)

logger = logging.getLogger('mylist')


class TaskListView(View):
    """
    View for displaying the list of tasks.
    GET / - Display all tasks with filtering options
    """
    
    def get(self, request):
        """Render the task list template."""
        try:
            # Initialize database if needed
            init_database()
            
            # Get query parameters for filtering
            status_filter = request.GET.get('status', '')
            sort_by = request.GET.get('sort_by', 'created_at')
            order = request.GET.get('order', 'desc')
            
            logger.info(f"TaskListView - status={status_filter}, sort_by={sort_by}, order={order}")
            
            # Get tasks with filters
            tasks = get_all_tasks(
                status=status_filter if status_filter else None,
                sort_by=sort_by,
                order=order
            )
            
            # Get statistics
            stats = get_task_statistics()
            
            context = {
                'tasks': tasks,
                'stats': stats,
                'current_status': status_filter,
                'current_sort': sort_by,
                'current_order': order,
                'status_choices': ['pending', 'in_progress', 'completed'],
                'sort_choices': [
                    ('created_at', 'Created Date'),
                    ('updated_at', 'Updated Date'),
                    ('due_date', 'Due Date'),
                    ('title', 'Title'),
                    ('status', 'Status'),
                ],
            }
            
            return render(request, 'mylist/task_list.html', context)
            
        except DatabaseError as e:
            logger.error(f"Database error in TaskListView: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'Database error occurred. Please try again later.'
            })
        except Exception as e:
            logger.exception(f"Unexpected error in TaskListView: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'An unexpected error occurred.'
            })


class TaskCreateView(View):
    """
    View for creating a new task.
    GET /tasks/new/ - Display the create task form
    POST /tasks/new/ - Process the form and create task
    """
    
    def get(self, request):
        """Render the create task form."""
        context = {
            'status_choices': ['pending', 'in_progress', 'completed'],
            'form_action': 'create',
        }
        return render(request, 'mylist/task_form.html', context)
    
    def post(self, request):
        """Process the form and create a new task."""
        try:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            due_date = request.POST.get('due_date', '').strip()
            status = request.POST.get('status', 'pending')
            
            logger.info(f"TaskCreateView POST - Creating task: {title}")
            
            # Validate title
            if not title:
                return render(request, 'mylist/task_form.html', {
                    'error': 'Title is required',
                    'status_choices': ['pending', 'in_progress', 'completed'],
                    'form_data': request.POST,
                    'form_action': 'create',
                })
            
            # Create task
            create_task(
                title=title,
                description=description if description else None,
                due_date=due_date if due_date else None,
                status=status
            )
            
            return HttpResponseRedirect(reverse('task_list') + '?message=created')
            
        except ValueError as e:
            logger.warning(f"Validation error in TaskCreateView: {e}")
            return render(request, 'mylist/task_form.html', {
                'error': str(e),
                'status_choices': ['pending', 'in_progress', 'completed'],
                'form_data': request.POST,
                'form_action': 'create',
            })
        except DatabaseError as e:
            logger.error(f"Database error in TaskCreateView: {e}")
            return render(request, 'mylist/task_form.html', {
                'error': 'Database error occurred. Please try again.',
                'status_choices': ['pending', 'in_progress', 'completed'],
                'form_data': request.POST,
                'form_action': 'create',
            })
        except Exception as e:
            logger.exception(f"Unexpected error in TaskCreateView: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'An unexpected error occurred.'
            })


class TaskDetailView(View):
    """
    View for displaying a single task.
    GET /tasks/<id>/ - Display task details
    """
    
    def get(self, request, task_id):
        """Render the task detail template."""
        try:
            logger.info(f"TaskDetailView - task_id={task_id}")
            task = get_task_by_id(task_id)
            
            context = {
                'task': task,
            }
            return render(request, 'mylist/task_detail.html', context)
            
        except TaskNotFoundError as e:
            logger.warning(f"Task not found: {task_id}")
            return render(request, 'mylist/error.html', {
                'error_message': f'Task with ID {task_id} not found.'
            }, status=404)
        except DatabaseError as e:
            logger.error(f"Database error in TaskDetailView: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'Database error occurred.'
            })


class TaskEditView(View):
    """
    View for editing an existing task.
    GET /tasks/<id>/edit/ - Display the edit form
    POST /tasks/<id>/edit/ - Process the form and update task
    """
    
    def get(self, request, task_id):
        """Render the edit task form."""
        try:
            task = get_task_by_id(task_id)
            
            context = {
                'task': task,
                'status_choices': ['pending', 'in_progress', 'completed'],
                'form_action': 'edit',
            }
            return render(request, 'mylist/task_form.html', context)
            
        except TaskNotFoundError as e:
            logger.warning(f"Task not found for edit: {task_id}")
            return render(request, 'mylist/error.html', {
                'error_message': f'Task with ID {task_id} not found.'
            }, status=404)
        except DatabaseError as e:
            logger.error(f"Database error in TaskEditView.get: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'Database error occurred.'
            })
    
    def post(self, request, task_id):
        """Process the form and update the task."""
        try:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            due_date = request.POST.get('due_date', '').strip()
            status = request.POST.get('status', 'pending')
            
            logger.info(f"TaskEditView POST - Updating task: {task_id}")
            
            # Validate title
            if not title:
                task = get_task_by_id(task_id)
                return render(request, 'mylist/task_form.html', {
                    'task': task,
                    'error': 'Title is required',
                    'status_choices': ['pending', 'in_progress', 'completed'],
                    'form_data': request.POST,
                    'form_action': 'edit',
                })
            
            # Update task
            update_task(
                task_id=task_id,
                title=title,
                description=description if description else None,
                due_date=due_date if due_date else None,
                status=status
            )
            
            return HttpResponseRedirect(reverse('task_list') + '?message=updated')
            
        except TaskNotFoundError as e:
            logger.warning(f"Task not found for update: {task_id}")
            return render(request, 'mylist/error.html', {
                'error_message': f'Task with ID {task_id} not found.'
            }, status=404)
        except ValueError as e:
            logger.warning(f"Validation error in TaskEditView: {e}")
            try:
                task = get_task_by_id(task_id)
            except:
                task = None
            return render(request, 'mylist/task_form.html', {
                'task': task,
                'error': str(e),
                'status_choices': ['pending', 'in_progress', 'completed'],
                'form_data': request.POST,
                'form_action': 'edit',
            })
        except DatabaseError as e:
            logger.error(f"Database error in TaskEditView: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'Database error occurred.'
            })


class TaskDeleteView(View):
    """
    View for deleting a task.
    GET /tasks/<id>/delete/ - Display confirmation page
    POST /tasks/<id>/delete/ - Delete the task
    """
    
    def get(self, request, task_id):
        """Render the delete confirmation page."""
        try:
            task = get_task_by_id(task_id)
            
            context = {
                'task': task,
            }
            return render(request, 'mylist/task_confirm_delete.html', context)
            
        except TaskNotFoundError as e:
            logger.warning(f"Task not found for delete: {task_id}")
            return render(request, 'mylist/error.html', {
                'error_message': f'Task with ID {task_id} not found.'
            }, status=404)
        except DatabaseError as e:
            logger.error(f"Database error in TaskDeleteView.get: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'Database error occurred.'
            })
    
    def post(self, request, task_id):
        """Delete the task."""
        try:
            logger.info(f"TaskDeleteView POST - Deleting task: {task_id}")
            delete_task(task_id)
            return HttpResponseRedirect(reverse('task_list') + '?message=deleted')
            
        except TaskNotFoundError as e:
            logger.warning(f"Task not found for delete: {task_id}")
            return render(request, 'mylist/error.html', {
                'error_message': f'Task with ID {task_id} not found.'
            }, status=404)
        except DatabaseError as e:
            logger.error(f"Database error in TaskDeleteView: {e}")
            return render(request, 'mylist/error.html', {
                'error_message': 'Database error occurred.'
            })
