# API Documentation

## Overview

The To-Do List API provides RESTful endpoints for managing tasks. All endpoints accept and return JSON data.

## Base URL

```
http://localhost:8000/api/
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message describing what went wrong"
}
```

---

## Endpoints

### 1. List All Tasks

Retrieve all tasks with optional filtering and sorting.

**Endpoint:** `GET /api/tasks/`

**Query Parameters:**

| Parameter | Type   | Required | Description                                    |
|-----------|--------|----------|------------------------------------------------|
| status    | string | No       | Filter by status: pending, in_progress, completed |
| sort_by   | string | No       | Sort field: id, title, due_date, status, created_at, updated_at (default: created_at) |
| order     | string | No       | Sort order: asc, desc (default: desc)         |
| search    | string | No       | Search in title and description               |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/tasks/?status=pending&sort_by=due_date&order=asc"
```

**Example Response:**
```json
{
    "success": true,
    "message": "Retrieved 2 tasks",
    "data": {
        "tasks": [
            {
                "id": 1,
                "title": "Complete project",
                "description": "Finish the Django project",
                "due_date": "2024-12-25",
                "status": "pending",
                "created_at": "2024-12-01T10:00:00.000000",
                "updated_at": "2024-12-01T10:00:00.000000"
            },
            {
                "id": 2,
                "title": "Review code",
                "description": "Code review for PR #123",
                "due_date": "2024-12-28",
                "status": "pending",
                "created_at": "2024-12-02T14:30:00.000000",
                "updated_at": "2024-12-02T14:30:00.000000"
            }
        ],
        "count": 2
    }
}
```

---

### 2. Create a Task

Create a new task.

**Endpoint:** `POST /api/tasks/`

**Request Body:**

| Field       | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| title       | string | Yes      | Task title (cannot be empty)                     |
| description | string | No       | Task description                                 |
| due_date    | string | No       | Due date in YYYY-MM-DD format                    |
| status      | string | No       | Task status: pending, in_progress, completed (default: pending) |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/tasks/" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "New Task",
        "description": "Task description here",
        "due_date": "2024-12-31",
        "status": "pending"
    }'
```

**Example Response (201 Created):**
```json
{
    "success": true,
    "message": "Task created successfully",
    "data": {
        "task": {
            "id": 3,
            "title": "New Task",
            "description": "Task description here",
            "due_date": "2024-12-31",
            "status": "pending",
            "created_at": "2024-12-15T09:00:00.000000",
            "updated_at": "2024-12-15T09:00:00.000000"
        }
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "error": "Title is required"
}
```

---

### 3. Get a Specific Task

Retrieve a single task by ID.

**Endpoint:** `GET /api/tasks/<id>/`

**Path Parameters:**

| Parameter | Type    | Description     |
|-----------|---------|-----------------|
| id        | integer | Task ID         |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/tasks/1/"
```

**Example Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "task": {
            "id": 1,
            "title": "Complete project",
            "description": "Finish the Django project",
            "due_date": "2024-12-25",
            "status": "pending",
            "created_at": "2024-12-01T10:00:00.000000",
            "updated_at": "2024-12-01T10:00:00.000000"
        }
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "error": "Task with ID 999 not found"
}
```

---

### 4. Update a Task

Update an existing task. Supports both full (PUT) and partial (PATCH) updates.

**Endpoint:** `PUT /api/tasks/<id>/` or `PATCH /api/tasks/<id>/`

**Path Parameters:**

| Parameter | Type    | Description     |
|-----------|---------|-----------------|
| id        | integer | Task ID         |

**Request Body:**

| Field       | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| title       | string | No       | New task title                                   |
| description | string | No       | New task description                             |
| due_date    | string | No       | New due date in YYYY-MM-DD format                |
| status      | string | No       | New status: pending, in_progress, completed      |

**Example Request:**
```bash
curl -X PUT "http://localhost:8000/api/tasks/1/" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Updated Task Title",
        "status": "completed"
    }'
```

**Example Response (200 OK):**
```json
{
    "success": true,
    "message": "Task updated successfully",
    "data": {
        "task": {
            "id": 1,
            "title": "Updated Task Title",
            "description": "Finish the Django project",
            "due_date": "2024-12-25",
            "status": "completed",
            "created_at": "2024-12-01T10:00:00.000000",
            "updated_at": "2024-12-15T11:30:00.000000"
        }
    }
}
```

---

### 5. Delete a Task

Delete a task by ID.

**Endpoint:** `DELETE /api/tasks/<id>/`

**Path Parameters:**

| Parameter | Type    | Description     |
|-----------|---------|-----------------|
| id        | integer | Task ID         |

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/tasks/1/"
```

**Example Response (200 OK):**
```json
{
    "success": true,
    "message": "Task deleted successfully"
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "error": "Task with ID 999 not found"
}
```

---

### 6. Get Task Statistics

Retrieve task count statistics grouped by status.

**Endpoint:** `GET /api/tasks/stats/`

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/tasks/stats/"
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "statistics": {
            "total": 10,
            "pending": 4,
            "in_progress": 3,
            "completed": 3
        }
    }
}
```

---

## HTTP Status Codes

| Status Code | Description                                    |
|-------------|------------------------------------------------|
| 200         | OK - Request successful                        |
| 201         | Created - Resource created successfully        |
| 400         | Bad Request - Invalid request data             |
| 404         | Not Found - Resource not found                 |
| 500         | Internal Server Error - Server error occurred  |

---

## Data Model

### Task Object

| Field       | Type     | Description                                    |
|-------------|----------|------------------------------------------------|
| id          | integer  | Unique identifier (auto-generated)             |
| title       | string   | Task title (required)                          |
| description | string   | Task description (optional)                    |
| due_date    | string   | Due date in YYYY-MM-DD format (optional)       |
| status      | string   | Status: pending, in_progress, completed        |
| created_at  | datetime | ISO format timestamp of creation               |
| updated_at  | datetime | ISO format timestamp of last update            |

---

## Validation Rules

1. **Title**: Required, cannot be empty or whitespace-only
2. **Status**: Must be one of: `pending`, `in_progress`, `completed`
3. **Due Date**: Must be in `YYYY-MM-DD` format if provided

---

## Error Handling

All errors are returned with a consistent format:

```json
{
    "success": false,
    "error": "Descriptive error message"
}
```

Common error scenarios:
- Missing required fields (400)
- Invalid field values (400)
- Resource not found (404)
- Invalid JSON format (400)
- Server errors (500)

---

## Example: Complete CRUD Workflow

```bash
# 1. Create a task
curl -X POST "http://localhost:8000/api/tasks/" \
    -H "Content-Type: application/json" \
    -d '{"title": "Learn Django", "status": "pending"}'

# 2. List all tasks
curl -X GET "http://localhost:8000/api/tasks/"

# 3. Get specific task
curl -X GET "http://localhost:8000/api/tasks/1/"

# 4. Update task status
curl -X PATCH "http://localhost:8000/api/tasks/1/" \
    -H "Content-Type: application/json" \
    -d '{"status": "completed"}'

# 5. Delete task
curl -X DELETE "http://localhost:8000/api/tasks/1/"
```
