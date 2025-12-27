"""
Pytest configuration and fixtures for To-Do List tests.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')

import django
django.setup()


@pytest.fixture(scope='function')
def temp_db():
    """Create a temporary database for testing."""
    import mylist.database as db_module
    
    # Store original path
    original_path = db_module.DB_PATH
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
    temp_file.close()
    
    # Set the new path
    db_module.DB_PATH = Path(temp_file.name)
    
    # Initialize the database
    db_module.init_database()
    
    yield db_module
    
    # Cleanup: restore original path and delete temp file
    db_module.DB_PATH = original_path
    try:
        os.unlink(temp_file.name)
    except OSError:
        pass


@pytest.fixture
def sample_task(temp_db):
    """Create a sample task for testing."""
    task = temp_db.create_task(
        title="Test Task",
        description="This is a test task description",
        due_date="2024-12-31",
        status="pending"
    )
    return task


@pytest.fixture
def multiple_tasks(temp_db):
    """Create multiple tasks for testing."""
    tasks = []
    
    tasks.append(temp_db.create_task(
        title="Task 1 - Pending",
        description="First task",
        due_date="2024-12-01",
        status="pending"
    ))
    
    tasks.append(temp_db.create_task(
        title="Task 2 - In Progress",
        description="Second task",
        due_date="2024-12-15",
        status="in_progress"
    ))
    
    tasks.append(temp_db.create_task(
        title="Task 3 - Completed",
        description="Third task",
        due_date="2024-12-20",
        status="completed"
    ))
    
    return tasks


@pytest.fixture
def client():
    """Create a Django test client."""
    from django.test import Client
    return Client()


@pytest.fixture
def api_client():
    """Create a Django test client for API requests."""
    from django.test import Client
    client = Client()
    client.defaults['content_type'] = 'application/json'
    return client
