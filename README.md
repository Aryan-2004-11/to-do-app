# To-Do List Application

A full-featured To-Do List web application built with Django, featuring RESTful APIs and a web interface for task management.

## 📋 Features

- **CRUD Operations**: Create, Read, Update, and Delete tasks
- **RESTful API**: JSON-based API endpoints for all operations
- **Web Interface**: User-friendly HTML templates with responsive design
- **Raw SQL**: Database operations using raw SQL (no ORM)
- **Filtering & Sorting**: Filter tasks by status, sort by various fields
- **Search**: Search tasks by title or description
- **Statistics**: View task counts by status
- **Logging**: Comprehensive logging for debugging and monitoring
- **Exception Handling**: Proper error handling throughout the application
- **Automated Tests**: Full test coverage using pytest

## 🗂️ Project Structure

```
todo_list/
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite database (created on first run)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── todo_list/                # Django project settings
│   ├── __init__.py
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Root URL configuration
│   └── wsgi.py                  # WSGI configuration
│
├── mylist/                    # Main application
│   ├── __init__.py
│   ├── apps.py                  # App configuration
│   ├── database.py              # Raw SQL database operations
│   ├── api_views.py             # REST API views
│   ├── views.py                 # Template views
│   ├── urls.py                  # URL routing
│   └── templates/
│       └── mylist/
│           ├── base.html        # Base template
│           ├── task_list.html   # Task list page
│           ├── task_form.html   # Create/Edit form
│           ├── task_detail.html # Task detail page
│           ├── task_confirm_delete.html
│           └── error.html       # Error page
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_database.py         # Database operation tests
│   ├── test_api.py              # API endpoint tests
│   └── test_views.py            # Template view tests
│
├── docs/                        # Documentation
│   └── API_DOCUMENTATION.md     # API reference
│
└── logs/                        # Log files
    └── mylist.log             # Application logs
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todo_list
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create logs directory**
   ```bash
   mkdir -p logs
   ```

5. **Run the application**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Web Interface: http://localhost:8000/
   - API Endpoints: http://localhost:8000/api/tasks/

## 📝 Usage

### Web Interface

1. **View Tasks**: Navigate to http://localhost:8000/ to see all tasks
2. **Create Task**: Click "Add New Task" button or go to http://localhost:8000/tasks/new/
3. **View Task Details**: Click on a task title or "View" button
4. **Edit Task**: Click "Edit" button on any task
5. **Delete Task**: Click "Delete" button and confirm

### API Endpoints

| Method | Endpoint             | Description          |
|--------|----------------------|----------------------|
| GET    | /api/tasks/          | List all tasks       |
| POST   | /api/tasks/          | Create a new task    |
| GET    | /api/tasks/{id}/     | Get a specific task  |
| PUT    | /api/tasks/{id}/     | Update a task        |
| PATCH  | /api/tasks/{id}/     | Partial update       |
| DELETE | /api/tasks/{id}/     | Delete a task        |
| GET    | /api/tasks/stats/    | Get task statistics  |

### API Examples

**Create a task:**
```bash
curl -X POST "http://localhost:8000/api/tasks/" \
    -H "Content-Type: application/json" \
    -d '{"title": "Learn Django", "description": "Complete the tutorial", "due_date": "2024-12-31", "status": "pending"}'
```

**List all tasks:**
```bash
curl "http://localhost:8000/api/tasks/"
```

**Filter by status:**
```bash
curl "http://localhost:8000/api/tasks/?status=pending"
```

**Update a task:**
```bash
curl -X PUT "http://localhost:8000/api/tasks/1/" \
    -H "Content-Type: application/json" \
    -d '{"status": "completed"}'
```

**Delete a task:**
```bash
curl -X DELETE "http://localhost:8000/api/tasks/1/"
```

For complete API documentation, see [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

## 🧪 Running Tests

The project uses pytest for automated testing.

**Run all tests:**
```bash
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
pytest tests/test_api.py
```

**Run with coverage report:**
```bash
pytest --cov=mylist --cov-report=html
```

### Test Categories

- **test_database.py**: Tests for raw SQL database operations
- **test_api.py**: Tests for REST API endpoints
- **test_views.py**: Tests for web interface views

## 🗄️ Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**Note**: No Django ORM is used. All database operations are performed using raw SQL.

## 📊 Logging

The application logs all operations to:
- Console output (during development)
- `logs/mylist.log` file

Log levels include:
- DEBUG: Detailed operation information
- INFO: General operation logs
- WARNING: Validation errors, missing resources
- ERROR: Database errors, unexpected exceptions

## ⚠️ Exception Handling

The application handles the following exceptions:

- **ValueError**: Invalid input data (status, date format, empty title)
- **TaskNotFoundError**: Task with given ID doesn't exist
- **DatabaseError**: Database connection or query failures
- **APIException**: API-specific errors (invalid JSON, etc.)

All exceptions are caught and return appropriate HTTP status codes with descriptive error messages.

## 🔧 Configuration

Key settings in `todo_list/settings.py`:

- **DEBUG**: Set to `False` in production
- **SECRET_KEY**: Change in production
- **DATABASE**: SQLite by default, can be changed to PostgreSQL/MySQL
- **LOGGING**: Configure log levels and handlers

## 🚀 Deployment Considerations

1. **Set DEBUG=False** in production
2. **Generate a new SECRET_KEY**
3. **Configure ALLOWED_HOSTS**
4. **Use a production database** (PostgreSQL recommended)
5. **Set up proper logging** to external service
6. **Use a WSGI server** (gunicorn, uWSGI)
7. **Configure static files** serving

## 📄 License

This project is created for educational purposes as part of an assignment.

## 👤 Author

[Your Name]

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Pytest Documentation](https://docs.pytest.org/)
