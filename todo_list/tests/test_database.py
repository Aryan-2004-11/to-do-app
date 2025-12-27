"""
Tests for the database module (raw SQL operations).
"""

import pytest
from mylist.database import (
    TaskNotFoundError, DatabaseError
)


class TestCreateTask:
    """Tests for create_task function."""
    
    def test_create_task_with_all_fields(self, temp_db):
        """Test creating a task with all fields provided."""
        task = temp_db.create_task(
            title="Complete Project",
            description="Finish the Django project",
            due_date="2024-12-25",
            status="pending"
        )
        
        assert task['id'] is not None
        assert task['title'] == "Complete Project"
        assert task['description'] == "Finish the Django project"
        assert task['due_date'] == "2024-12-25"
        assert task['status'] == "pending"
        assert task['created_at'] is not None
        assert task['updated_at'] is not None
    
    def test_create_task_with_minimum_fields(self, temp_db):
        """Test creating a task with only required fields."""
        task = temp_db.create_task(title="Simple Task")
        
        assert task['id'] is not None
        assert task['title'] == "Simple Task"
        assert task['description'] is None
        assert task['due_date'] is None
        assert task['status'] == "pending"
    
    def test_create_task_empty_title_raises_error(self, temp_db):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            temp_db.create_task(title="")
        
        assert "title is required" in str(exc_info.value).lower()
    
    def test_create_task_whitespace_title_raises_error(self, temp_db):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError):
            temp_db.create_task(title="   ")
    
    def test_create_task_invalid_status_raises_error(self, temp_db):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            temp_db.create_task(title="Test", status="invalid_status")
        
        assert "status must be one of" in str(exc_info.value).lower()
    
    def test_create_task_invalid_date_format_raises_error(self, temp_db):
        """Test that invalid date format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            temp_db.create_task(title="Test", due_date="25-12-2024")
        
        assert "YYYY-MM-DD" in str(exc_info.value)
    
    def test_create_task_with_all_statuses(self, temp_db):
        """Test creating tasks with all valid statuses."""
        for status in ['pending', 'in_progress', 'completed']:
            task = temp_db.create_task(title=f"Task - {status}", status=status)
            assert task['status'] == status


class TestGetAllTasks:
    """Tests for get_all_tasks function."""
    
    def test_get_all_tasks_empty(self, temp_db):
        """Test getting tasks when database is empty."""
        tasks = temp_db.get_all_tasks()
        assert tasks == []
    
    def test_get_all_tasks_returns_all(self, multiple_tasks, temp_db):
        """Test getting all tasks without filters."""
        tasks = temp_db.get_all_tasks()
        assert len(tasks) == 3
    
    def test_get_all_tasks_filter_by_status(self, multiple_tasks, temp_db):
        """Test filtering tasks by status."""
        pending_tasks = temp_db.get_all_tasks(status='pending')
        assert len(pending_tasks) == 1
        assert pending_tasks[0]['status'] == 'pending'
        
        completed_tasks = temp_db.get_all_tasks(status='completed')
        assert len(completed_tasks) == 1
        assert completed_tasks[0]['status'] == 'completed'
    
    def test_get_all_tasks_sort_by_title(self, multiple_tasks, temp_db):
        """Test sorting tasks by title."""
        tasks = temp_db.get_all_tasks(sort_by='title', order='asc')
        titles = [t['title'] for t in tasks]
        assert titles == sorted(titles)
    
    def test_get_all_tasks_sort_order_desc(self, multiple_tasks, temp_db):
        """Test descending sort order."""
        tasks = temp_db.get_all_tasks(sort_by='id', order='desc')
        ids = [t['id'] for t in tasks]
        assert ids == sorted(ids, reverse=True)


class TestGetTaskById:
    """Tests for get_task_by_id function."""
    
    def test_get_task_by_id_success(self, sample_task, temp_db):
        """Test retrieving an existing task by ID."""
        task = temp_db.get_task_by_id(sample_task['id'])
        assert task['id'] == sample_task['id']
        assert task['title'] == sample_task['title']
    
    def test_get_task_by_id_not_found(self, temp_db):
        """Test retrieving a non-existent task."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            temp_db.get_task_by_id(99999)
        
        assert "99999" in str(exc_info.value)


class TestUpdateTask:
    """Tests for update_task function."""
    
    def test_update_task_title(self, sample_task, temp_db):
        """Test updating task title."""
        updated = temp_db.update_task(sample_task['id'], title="Updated Title")
        
        assert updated['title'] == "Updated Title"
        assert updated['description'] == sample_task['description']
    
    def test_update_task_status(self, sample_task, temp_db):
        """Test updating task status."""
        updated = temp_db.update_task(sample_task['id'], status="completed")
        assert updated['status'] == "completed"
    
    def test_update_task_multiple_fields(self, sample_task, temp_db):
        """Test updating multiple fields at once."""
        updated = temp_db.update_task(
            sample_task['id'],
            title="New Title",
            description="New Description",
            status="in_progress"
        )
        
        assert updated['title'] == "New Title"
        assert updated['description'] == "New Description"
        assert updated['status'] == "in_progress"
    
    def test_update_task_not_found(self, temp_db):
        """Test updating a non-existent task."""
        with pytest.raises(TaskNotFoundError):
            temp_db.update_task(99999, title="New Title")
    
    def test_update_task_empty_title_raises_error(self, sample_task, temp_db):
        """Test that empty title raises ValueError on update."""
        with pytest.raises(ValueError):
            temp_db.update_task(sample_task['id'], title="")
    
    def test_update_task_invalid_status_raises_error(self, sample_task, temp_db):
        """Test that invalid status raises ValueError on update."""
        with pytest.raises(ValueError):
            temp_db.update_task(sample_task['id'], status="invalid")
    
    def test_update_task_updates_timestamp(self, sample_task, temp_db):
        """Test that update modifies the updated_at timestamp."""
        import time
        time.sleep(0.1)  # Ensure time difference
        
        updated = temp_db.update_task(sample_task['id'], title="Changed")
        assert updated['updated_at'] > sample_task['updated_at']


class TestDeleteTask:
    """Tests for delete_task function."""
    
    def test_delete_task_success(self, sample_task, temp_db):
        """Test deleting an existing task."""
        result = temp_db.delete_task(sample_task['id'])
        assert result is True
        
        # Verify task is deleted
        with pytest.raises(TaskNotFoundError):
            temp_db.get_task_by_id(sample_task['id'])
    
    def test_delete_task_not_found(self, temp_db):
        """Test deleting a non-existent task."""
        with pytest.raises(TaskNotFoundError):
            temp_db.delete_task(99999)


class TestSearchTasks:
    """Tests for search_tasks function."""
    
    def test_search_tasks_by_title(self, multiple_tasks, temp_db):
        """Test searching tasks by title."""
        results = temp_db.search_tasks("Pending")
        assert len(results) == 1
        assert "Pending" in results[0]['title']
    
    def test_search_tasks_by_description(self, multiple_tasks, temp_db):
        """Test searching tasks by description."""
        results = temp_db.search_tasks("First")
        assert len(results) == 1
        assert "First" in results[0]['description']
    
    def test_search_tasks_no_results(self, multiple_tasks, temp_db):
        """Test search with no matching results."""
        results = temp_db.search_tasks("nonexistent")
        assert results == []
    
    def test_search_tasks_case_insensitive(self, temp_db):
        """Test that search is case-insensitive."""
        temp_db.create_task(title="UPPERCASE Task")
        
        results = temp_db.search_tasks("uppercase")
        assert len(results) == 1


class TestGetTaskStatistics:
    """Tests for get_task_statistics function."""
    
    def test_get_statistics_empty(self, temp_db):
        """Test statistics when database is empty."""
        stats = temp_db.get_task_statistics()
        
        assert stats['total'] == 0
        assert stats['pending'] == 0
        assert stats['in_progress'] == 0
        assert stats['completed'] == 0
    
    def test_get_statistics_with_tasks(self, multiple_tasks, temp_db):
        """Test statistics with multiple tasks."""
        stats = temp_db.get_task_statistics()
        
        assert stats['total'] == 3
        assert stats['pending'] == 1
        assert stats['in_progress'] == 1
        assert stats['completed'] == 1
