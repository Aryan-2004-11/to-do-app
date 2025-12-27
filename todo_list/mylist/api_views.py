"""
API Views for Task Management.
Handles RESTful API endpoints for CRUD operations on tasks.
Uses raw SQL through the database module (No ORM, No generic ViewSets).
"""

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .database import (
    create_task, get_all_tasks, get_task_by_id, update_task, delete_task,
    search_tasks, get_task_statistics, TaskNotFoundError, DatabaseError
)

logger = logging.getLogger('mylist')


class APIException(Exception):
    """Base exception for API errors."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def api_response(data=None, message=None, success=True, status=200):
    """
    Standardized API response format.
    
    Args:
        data: Response data (optional)
        message: Response message (optional)
        success: Whether the request was successful
        status: HTTP status code
    
    Returns:
        JsonResponse with standardized format
    """
    response_data = {
        'success': success,
    }
    if message:
        response_data['message'] = message
    if data is not None:
        response_data['data'] = data
    
    return JsonResponse(response_data, status=status)


def error_response(message, status=400, errors=None):
    """
    Standardized error response format.
    
    Args:
        message: Error message
        status: HTTP status code
        errors: Additional error details (optional)
    
    Returns:
        JsonResponse with error format
    """
    response_data = {
        'success': False,
        'error': message,
    }
    if errors:
        response_data['errors'] = errors
    
    logger.warning(f"API Error Response: {message} (Status: {status})")
    return JsonResponse(response_data, status=status)


def parse_json_body(request):
    """
    Parse JSON body from request.
    
    Args:
        request: Django HTTP request object
    
    Returns:
        Parsed JSON data as dictionary
    
    Raises:
        APIException: If JSON parsing fails
    """
    try:
        if request.body:
            return json.loads(request.body.decode('utf-8'))
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise APIException("Invalid JSON format", 400)


@method_decorator(csrf_exempt, name='dispatch')
class TaskListAPIView(View):
    """
    API endpoint for listing and creating tasks.
    
    GET /api/tasks/ - List all tasks
        Query Parameters:
            - status: Filter by status (pending, in_progress, completed)
            - sort_by: Sort field (id, title, due_date, status, created_at, updated_at)
            - order: Sort order (asc, desc)
            - search: Search query for title/description
    
    POST /api/tasks/ - Create a new task
        Request Body (JSON):
            - title: string (required)
            - description: string (optional)
            - due_date: string YYYY-MM-DD (optional)
            - status: string (optional, default: pending)
    """
    
    def get(self, request):
        """Handle GET request - List all tasks."""
        try:
            # Get query parameters
            status = request.GET.get('status')
            sort_by = request.GET.get('sort_by', 'created_at')
            order = request.GET.get('order', 'desc')
            search_query = request.GET.get('search')
            
            logger.info(f"GET /api/tasks/ - status={status}, sort_by={sort_by}, order={order}, search={search_query}")
            
            # If search query provided, use search function
            if search_query:
                tasks = search_tasks(search_query)
            else:
                tasks = get_all_tasks(status=status, sort_by=sort_by, order=order)
            
            return api_response(
                data={'tasks': tasks, 'count': len(tasks)},
                message=f"Retrieved {len(tasks)} tasks"
            )
            
        except DatabaseError as e:
            logger.error(f"Database error in TaskListAPIView.get: {e}")
            return error_response("Database error occurred", 500)
        except Exception as e:
            logger.exception(f"Unexpected error in TaskListAPIView.get: {e}")
            return error_response("An unexpected error occurred", 500)
    
    def post(self, request):
        """Handle POST request - Create a new task."""
        try:
            data = parse_json_body(request)
            
            # Validate required fields
            title = data.get('title')
            if not title:
                return error_response("Title is required", 400)
            
            description = data.get('description')
            due_date = data.get('due_date')
            status = data.get('status', 'pending')
            
            logger.info(f"POST /api/tasks/ - Creating task: {title}")
            
            task = create_task(
                title=title,
                description=description,
                due_date=due_date,
                status=status
            )
            
            return api_response(
                data={'task': task},
                message="Task created successfully",
                status=201
            )
            
        except APIException as e:
            return error_response(e.message, e.status_code)
        except ValueError as e:
            logger.warning(f"Validation error in TaskListAPIView.post: {e}")
            return error_response(str(e), 400)
        except DatabaseError as e:
            logger.error(f"Database error in TaskListAPIView.post: {e}")
            return error_response("Database error occurred", 500)
        except Exception as e:
            logger.exception(f"Unexpected error in TaskListAPIView.post: {e}")
            return error_response("An unexpected error occurred", 500)


@method_decorator(csrf_exempt, name='dispatch')
class TaskDetailAPIView(View):
    """
    API endpoint for single task operations.
    
    GET /api/tasks/<id>/ - Get a specific task
    PUT /api/tasks/<id>/ - Update a task
    DELETE /api/tasks/<id>/ - Delete a task
    """
    
    def get(self, request, task_id):
        """Handle GET request - Get a specific task."""
        try:
            logger.info(f"GET /api/tasks/{task_id}/")
            task = get_task_by_id(task_id)
            return api_response(data={'task': task})
            
        except TaskNotFoundError as e:
            return error_response(str(e), 404)
        except DatabaseError as e:
            logger.error(f"Database error in TaskDetailAPIView.get: {e}")
            return error_response("Database error occurred", 500)
        except Exception as e:
            logger.exception(f"Unexpected error in TaskDetailAPIView.get: {e}")
            return error_response("An unexpected error occurred", 500)
    
    def put(self, request, task_id):
        """Handle PUT request - Update a task."""
        try:
            data = parse_json_body(request)
            
            logger.info(f"PUT /api/tasks/{task_id}/ - Updating task")
            
            task = update_task(
                task_id=task_id,
                title=data.get('title'),
                description=data.get('description'),
                due_date=data.get('due_date'),
                status=data.get('status')
            )
            
            return api_response(
                data={'task': task},
                message="Task updated successfully"
            )
            
        except APIException as e:
            return error_response(e.message, e.status_code)
        except TaskNotFoundError as e:
            return error_response(str(e), 404)
        except ValueError as e:
            logger.warning(f"Validation error in TaskDetailAPIView.put: {e}")
            return error_response(str(e), 400)
        except DatabaseError as e:
            logger.error(f"Database error in TaskDetailAPIView.put: {e}")
            return error_response("Database error occurred", 500)
        except Exception as e:
            logger.exception(f"Unexpected error in TaskDetailAPIView.put: {e}")
            return error_response("An unexpected error occurred", 500)
    
    def patch(self, request, task_id):
        """Handle PATCH request - Partially update a task."""
        # PATCH and PUT have the same behavior in this implementation
        return self.put(request, task_id)
    
    def delete(self, request, task_id):
        """Handle DELETE request - Delete a task."""
        try:
            logger.info(f"DELETE /api/tasks/{task_id}/")
            delete_task(task_id)
            return api_response(message="Task deleted successfully")
            
        except TaskNotFoundError as e:
            return error_response(str(e), 404)
        except DatabaseError as e:
            logger.error(f"Database error in TaskDetailAPIView.delete: {e}")
            return error_response("Database error occurred", 500)
        except Exception as e:
            logger.exception(f"Unexpected error in TaskDetailAPIView.delete: {e}")
            return error_response("An unexpected error occurred", 500)


@method_decorator(csrf_exempt, name='dispatch')
class TaskStatisticsAPIView(View):
    """
    API endpoint for task statistics.
    
    GET /api/tasks/stats/ - Get task statistics
    """
    
    def get(self, request):
        """Handle GET request - Get task statistics."""
        try:
            logger.info("GET /api/tasks/stats/")
            stats = get_task_statistics()
            return api_response(data={'statistics': stats})
            
        except DatabaseError as e:
            logger.error(f"Database error in TaskStatisticsAPIView.get: {e}")
            return error_response("Database error occurred", 500)
        except Exception as e:
            logger.exception(f"Unexpected error in TaskStatisticsAPIView.get: {e}")
            return error_response("An unexpected error occurred", 500)
