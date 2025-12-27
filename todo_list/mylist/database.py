"""
Database module for Task management using raw SQL (No ORM).
Handles all database operations for tasks table.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger('mylist')

# Database path
DB_PATH = Path(__file__).resolve().parent.parent / 'db.sqlite3'


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class TaskNotFoundError(Exception):
    """Exception raised when a task is not found."""
    pass


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures proper connection handling and error logging.
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        logger.debug("Database connection established")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseError(f"Failed to connect to database: {e}")
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def init_database():
    """
    Initialize the database and create the tasks table if it doesn't exist.
    Table schema:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - title: TEXT NOT NULL
        - description: TEXT
        - due_date: TEXT (ISO format date)
        - status: TEXT (pending, in_progress, completed)
        - created_at: TEXT (ISO format datetime)
        - updated_at: TEXT (ISO format datetime)
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DatabaseError(f"Failed to initialize database: {e}")


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a sqlite3.Row to a dictionary."""
    return dict(row) if row else None


def create_task(title: str, description: str = None, due_date: str = None, 
                status: str = 'pending') -> Dict[str, Any]:
    """
    Create a new task in the database.
    
    Args:
        title: Task title (required)
        description: Task description (optional)
        due_date: Due date in YYYY-MM-DD format (optional)
        status: Task status - pending, in_progress, completed (default: pending)
    
    Returns:
        Dictionary containing the created task data
    
    Raises:
        DatabaseError: If the task creation fails
        ValueError: If required fields are missing or invalid
    """
    if not title or not title.strip():
        logger.warning("Attempted to create task with empty title")
        raise ValueError("Task title is required and cannot be empty")
    
    valid_statuses = ['pending', 'in_progress', 'completed']
    if status not in valid_statuses:
        logger.warning(f"Invalid status provided: {status}")
        raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
    
    # Validate due_date format if provided
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            logger.warning(f"Invalid due_date format: {due_date}")
            raise ValueError("Due date must be in YYYY-MM-DD format")
    
    now = datetime.now().isoformat()
    
    insert_sql = """
    INSERT INTO tasks (title, description, due_date, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(insert_sql, (title.strip(), description, due_date, status, now, now))
            conn.commit()
            task_id = cursor.lastrowid
            logger.info(f"Task created successfully with ID: {task_id}")
            return get_task_by_id(task_id)
    except sqlite3.Error as e:
        logger.error(f"Failed to create task: {e}")
        raise DatabaseError(f"Failed to create task: {e}")


def get_all_tasks(status: str = None, sort_by: str = 'created_at', 
                  order: str = 'desc') -> List[Dict[str, Any]]:
    """
    Retrieve all tasks from the database with optional filtering and sorting.
    
    Args:
        status: Filter by status (optional)
        sort_by: Field to sort by (default: created_at)
        order: Sort order - asc or desc (default: desc)
    
    Returns:
        List of task dictionaries
    """
    valid_sort_fields = ['id', 'title', 'due_date', 'status', 'created_at', 'updated_at']
    valid_orders = ['asc', 'desc']
    
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'
    if order.lower() not in valid_orders:
        order = 'desc'
    
    if status:
        query = f"SELECT * FROM tasks WHERE status = ? ORDER BY {sort_by} {order.upper()}"
        params = (status,)
    else:
        query = f"SELECT * FROM tasks ORDER BY {sort_by} {order.upper()}"
        params = ()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            tasks = [row_to_dict(row) for row in rows]
            logger.debug(f"Retrieved {len(tasks)} tasks")
            return tasks
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve tasks: {e}")
        raise DatabaseError(f"Failed to retrieve tasks: {e}")


def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single task by its ID.
    
    Args:
        task_id: The ID of the task to retrieve
    
    Returns:
        Task dictionary or None if not found
    
    Raises:
        TaskNotFoundError: If the task is not found
    """
    query = "SELECT * FROM tasks WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (task_id,))
            row = cursor.fetchone()
            if row:
                logger.debug(f"Retrieved task with ID: {task_id}")
                return row_to_dict(row)
            else:
                logger.warning(f"Task not found with ID: {task_id}")
                raise TaskNotFoundError(f"Task with ID {task_id} not found")
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve task: {e}")
        raise DatabaseError(f"Failed to retrieve task: {e}")


def update_task(task_id: int, title: str = None, description: str = None,
                due_date: str = None, status: str = None) -> Dict[str, Any]:
    """
    Update an existing task.
    
    Args:
        task_id: The ID of the task to update
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        status: New status (optional)
    
    Returns:
        Updated task dictionary
    
    Raises:
        TaskNotFoundError: If the task is not found
        ValueError: If invalid values are provided
    """
    # First, verify the task exists
    existing_task = get_task_by_id(task_id)
    
    # Build update fields
    updates = []
    params = []
    
    if title is not None:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        updates.append("title = ?")
        params.append(title.strip())
    
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    
    if due_date is not None:
        if due_date:  # Not empty string
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Due date must be in YYYY-MM-DD format")
        updates.append("due_date = ?")
        params.append(due_date if due_date else None)
    
    if status is not None:
        valid_statuses = ['pending', 'in_progress', 'completed']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        updates.append("status = ?")
        params.append(status)
    
    if not updates:
        logger.debug(f"No updates provided for task ID: {task_id}")
        return existing_task
    
    # Add updated_at
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(task_id)
    
    update_sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(update_sql, params)
            conn.commit()
            logger.info(f"Task updated successfully with ID: {task_id}")
            return get_task_by_id(task_id)
    except sqlite3.Error as e:
        logger.error(f"Failed to update task: {e}")
        raise DatabaseError(f"Failed to update task: {e}")


def delete_task(task_id: int) -> bool:
    """
    Delete a task from the database.
    
    Args:
        task_id: The ID of the task to delete
    
    Returns:
        True if deletion was successful
    
    Raises:
        TaskNotFoundError: If the task is not found
    """
    # Verify the task exists
    get_task_by_id(task_id)
    
    delete_sql = "DELETE FROM tasks WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(delete_sql, (task_id,))
            conn.commit()
            logger.info(f"Task deleted successfully with ID: {task_id}")
            return True
    except sqlite3.Error as e:
        logger.error(f"Failed to delete task: {e}")
        raise DatabaseError(f"Failed to delete task: {e}")


def search_tasks(query: str) -> List[Dict[str, Any]]:
    """
    Search tasks by title or description.
    
    Args:
        query: Search query string
    
    Returns:
        List of matching task dictionaries
    """
    search_sql = """
    SELECT * FROM tasks 
    WHERE title LIKE ? OR description LIKE ?
    ORDER BY created_at DESC
    """
    search_pattern = f"%{query}%"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(search_sql, (search_pattern, search_pattern))
            rows = cursor.fetchall()
            tasks = [row_to_dict(row) for row in rows]
            logger.debug(f"Search for '{query}' returned {len(tasks)} results")
            return tasks
    except sqlite3.Error as e:
        logger.error(f"Failed to search tasks: {e}")
        raise DatabaseError(f"Failed to search tasks: {e}")


def get_task_statistics() -> Dict[str, int]:
    """
    Get task statistics (count by status).
    
    Returns:
        Dictionary with task counts by status
    """
    stats_sql = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
    FROM tasks
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(stats_sql)
            row = cursor.fetchone()
            return {
                'total': row['total'] or 0,
                'pending': row['pending'] or 0,
                'in_progress': row['in_progress'] or 0,
                'completed': row['completed'] or 0
            }
    except sqlite3.Error as e:
        logger.error(f"Failed to get task statistics: {e}")
        raise DatabaseError(f"Failed to get task statistics: {e}")
