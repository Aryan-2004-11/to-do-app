"""
Tests for the web interface views.
"""

import pytest


class TestTaskListView:
    """Tests for the task list view."""
    
    def test_task_list_view_empty(self, client, temp_db):
        """Test task list view with no tasks."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'No tasks found' in response.content
    
    def test_task_list_view_with_tasks(self, client, multiple_tasks, temp_db):
        """Test task list view with existing tasks."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Task 1 - Pending' in response.content
        assert b'Task 2 - In Progress' in response.content
        assert b'Task 3 - Completed' in response.content
    
    def test_task_list_view_filter_status(self, client, multiple_tasks, temp_db):
        """Test task list view with status filter."""
        response = client.get('/', {'status': 'pending'})
        
        assert response.status_code == 200
        assert b'Task 1 - Pending' in response.content
        # Other tasks should not be visible
        assert b'Task 2 - In Progress' not in response.content
    
    def test_task_list_view_shows_statistics(self, client, multiple_tasks, temp_db):
        """Test that task list shows statistics."""
        response = client.get('/')
        
        assert response.status_code == 200
        # Check for stats display
        assert b'Total Tasks' in response.content


class TestTaskCreateView:
    """Tests for the task create view."""
    
    def test_task_create_view_get(self, client, temp_db):
        """Test GET request to create view shows form."""
        response = client.get('/tasks/new/')
        
        assert response.status_code == 200
        assert b'Create New Task' in response.content
        assert b'<form' in response.content
    
    def test_task_create_view_post_success(self, client, temp_db):
        """Test POST request to create view creates task."""
        response = client.post('/tasks/new/', {
            'title': 'New Test Task',
            'description': 'Test description',
            'due_date': '2024-12-31',
            'status': 'pending'
        })
        
        # Should redirect to task list
        assert response.status_code == 302
        assert 'message=created' in response.url
    
    def test_task_create_view_post_missing_title(self, client, temp_db):
        """Test POST request without title shows error."""
        response = client.post('/tasks/new/', {
            'description': 'No title',
            'status': 'pending'
        })
        
        assert response.status_code == 200
        assert b'Title is required' in response.content


class TestTaskDetailView:
    """Tests for the task detail view."""
    
    def test_task_detail_view_success(self, client, sample_task, temp_db):
        """Test viewing an existing task."""
        response = client.get(f'/tasks/{sample_task["id"]}/')
        
        assert response.status_code == 200
        assert sample_task['title'].encode() in response.content
    
    def test_task_detail_view_not_found(self, client, temp_db):
        """Test viewing a non-existent task."""
        response = client.get('/tasks/99999/')
        
        assert response.status_code == 404
        assert b'not found' in response.content.lower()


class TestTaskEditView:
    """Tests for the task edit view."""
    
    def test_task_edit_view_get(self, client, sample_task, temp_db):
        """Test GET request to edit view shows form with data."""
        response = client.get(f'/tasks/{sample_task["id"]}/edit/')
        
        assert response.status_code == 200
        assert b'Edit Task' in response.content
        assert sample_task['title'].encode() in response.content
    
    def test_task_edit_view_post_success(self, client, sample_task, temp_db):
        """Test POST request to edit view updates task."""
        response = client.post(f'/tasks/{sample_task["id"]}/edit/', {
            'title': 'Updated Task Title',
            'description': 'Updated description',
            'due_date': '2025-01-15',
            'status': 'completed'
        })
        
        # Should redirect to task list
        assert response.status_code == 302
        assert 'message=updated' in response.url
    
    def test_task_edit_view_not_found(self, client, temp_db):
        """Test editing a non-existent task."""
        response = client.get('/tasks/99999/edit/')
        
        assert response.status_code == 404


class TestTaskDeleteView:
    """Tests for the task delete view."""
    
    def test_task_delete_view_get_confirmation(self, client, sample_task, temp_db):
        """Test GET request shows confirmation page."""
        response = client.get(f'/tasks/{sample_task["id"]}/delete/')
        
        assert response.status_code == 200
        assert b'Delete Task' in response.content
        assert sample_task['title'].encode() in response.content
    
    def test_task_delete_view_post_success(self, client, sample_task, temp_db):
        """Test POST request deletes task."""
        response = client.post(f'/tasks/{sample_task["id"]}/delete/')
        
        # Should redirect to task list
        assert response.status_code == 302
        assert 'message=deleted' in response.url
        
        # Verify task is deleted
        response = client.get(f'/tasks/{sample_task["id"]}/')
        assert response.status_code == 404
    
    def test_task_delete_view_not_found(self, client, temp_db):
        """Test deleting a non-existent task."""
        response = client.get('/tasks/99999/delete/')
        
        assert response.status_code == 404
