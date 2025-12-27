"""
Tests for the REST API endpoints.
"""

import json
import pytest


class TestTaskListAPI:
    """Tests for GET /api/tasks/ and POST /api/tasks/"""
    
    def test_get_tasks_empty(self, api_client, temp_db):
        """Test GET /api/tasks/ when no tasks exist."""
        response = api_client.get('/api/tasks/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['tasks'] == []
        assert data['data']['count'] == 0
    
    def test_get_tasks_with_data(self, api_client, multiple_tasks, temp_db):
        """Test GET /api/tasks/ with existing tasks."""
        response = api_client.get('/api/tasks/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['count'] == 3
        assert len(data['data']['tasks']) == 3
    
    def test_get_tasks_filter_by_status(self, api_client, multiple_tasks, temp_db):
        """Test GET /api/tasks/?status=pending"""
        response = api_client.get('/api/tasks/', {'status': 'pending'})
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['count'] == 1
        assert data['data']['tasks'][0]['status'] == 'pending'
    
    def test_get_tasks_with_search(self, api_client, multiple_tasks, temp_db):
        """Test GET /api/tasks/?search=Pending"""
        response = api_client.get('/api/tasks/', {'search': 'Pending'})
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['count'] == 1
    
    def test_create_task_success(self, api_client, temp_db):
        """Test POST /api/tasks/ with valid data."""
        payload = {
            'title': 'New Task',
            'description': 'Task description',
            'due_date': '2024-12-31',
            'status': 'pending'
        }
        
        response = api_client.post(
            '/api/tasks/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['title'] == 'New Task'
        assert data['data']['task']['id'] is not None
    
    def test_create_task_minimal(self, api_client, temp_db):
        """Test POST /api/tasks/ with only title."""
        payload = {'title': 'Minimal Task'}
        
        response = api_client.post(
            '/api/tasks/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['data']['task']['title'] == 'Minimal Task'
        assert data['data']['task']['status'] == 'pending'
    
    def test_create_task_missing_title(self, api_client, temp_db):
        """Test POST /api/tasks/ without title."""
        payload = {'description': 'No title'}
        
        response = api_client.post(
            '/api/tasks/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'title' in data['error'].lower()
    
    def test_create_task_invalid_status(self, api_client, temp_db):
        """Test POST /api/tasks/ with invalid status."""
        payload = {'title': 'Test', 'status': 'invalid'}
        
        response = api_client.post(
            '/api/tasks/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
    
    def test_create_task_invalid_json(self, api_client, temp_db):
        """Test POST /api/tasks/ with invalid JSON."""
        response = api_client.post(
            '/api/tasks/',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestTaskDetailAPI:
    """Tests for GET/PUT/DELETE /api/tasks/<id>/"""
    
    def test_get_task_success(self, api_client, sample_task, temp_db):
        """Test GET /api/tasks/<id>/ for existing task."""
        response = api_client.get(f'/api/tasks/{sample_task["id"]}/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['id'] == sample_task['id']
        assert data['data']['task']['title'] == sample_task['title']
    
    def test_get_task_not_found(self, api_client, temp_db):
        """Test GET /api/tasks/<id>/ for non-existent task."""
        response = api_client.get('/api/tasks/99999/')
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
    
    def test_update_task_success(self, api_client, sample_task, temp_db):
        """Test PUT /api/tasks/<id>/ with valid data."""
        payload = {'title': 'Updated Title', 'status': 'completed'}
        
        response = api_client.put(
            f'/api/tasks/{sample_task["id"]}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['task']['title'] == 'Updated Title'
        assert data['data']['task']['status'] == 'completed'
    
    def test_update_task_partial(self, api_client, sample_task, temp_db):
        """Test PATCH /api/tasks/<id>/ with partial update."""
        payload = {'status': 'in_progress'}
        
        response = api_client.patch(
            f'/api/tasks/{sample_task["id"]}/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['data']['task']['status'] == 'in_progress'
        assert data['data']['task']['title'] == sample_task['title']  # Unchanged
    
    def test_update_task_not_found(self, api_client, temp_db):
        """Test PUT /api/tasks/<id>/ for non-existent task."""
        payload = {'title': 'Updated'}
        
        response = api_client.put(
            '/api/tasks/99999/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_delete_task_success(self, api_client, sample_task, temp_db):
        """Test DELETE /api/tasks/<id>/ for existing task."""
        response = api_client.delete(f'/api/tasks/{sample_task["id"]}/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        # Verify task is deleted
        response = api_client.get(f'/api/tasks/{sample_task["id"]}/')
        assert response.status_code == 404
    
    def test_delete_task_not_found(self, api_client, temp_db):
        """Test DELETE /api/tasks/<id>/ for non-existent task."""
        response = api_client.delete('/api/tasks/99999/')
        
        assert response.status_code == 404


class TestTaskStatisticsAPI:
    """Tests for GET /api/tasks/stats/"""
    
    def test_get_statistics_empty(self, api_client, temp_db):
        """Test GET /api/tasks/stats/ when no tasks exist."""
        response = api_client.get('/api/tasks/stats/')
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['statistics']['total'] == 0
    
    def test_get_statistics_with_tasks(self, api_client, multiple_tasks, temp_db):
        """Test GET /api/tasks/stats/ with existing tasks."""
        response = api_client.get('/api/tasks/stats/')
        
        assert response.status_code == 200
        data = response.json()
        stats = data['data']['statistics']
        
        assert stats['total'] == 3
        assert stats['pending'] == 1
        assert stats['in_progress'] == 1
        assert stats['completed'] == 1


class TestAPIResponseFormat:
    """Tests for API response format consistency."""
    
    def test_success_response_format(self, api_client, temp_db):
        """Test that success responses have correct format."""
        response = api_client.get('/api/tasks/')
        data = response.json()
        
        assert 'success' in data
        assert data['success'] is True
        assert 'data' in data or 'message' in data
    
    def test_error_response_format(self, api_client, temp_db):
        """Test that error responses have correct format."""
        response = api_client.get('/api/tasks/99999/')
        data = response.json()
        
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
