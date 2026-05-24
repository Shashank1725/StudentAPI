import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token():
    """Helper to get authentication token"""
    # Register user
    client.post(
        "/api/users/register",
        json={
            "email": "taskuser@example.com",
            "username": "taskuser",
            "password": "test123"
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "taskuser",
            "password": "test123"
        }
    )
    return response.json()["access_token"]

def test_create_task():
    """Test task creation"""
    token = get_auth_token()
    
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "pending"
    assert "id" in data

def test_get_tasks():
    """Test getting all tasks"""
    token = get_auth_token()
    
    # Create a task
    client.post(
        "/api/tasks/",
        json={"title": "Task 1", "description": "First task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get tasks
    response = client.get(
        "/api/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1

def test_get_single_task():
    """Test getting a single task"""
    token = get_auth_token()
    
    # Create task
    create_response = client.post(
        "/api/tasks/",
        json={"title": "Single Task", "description": "Get this task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Get task
    response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "Single Task"

def test_update_task():
    """Test updating a task"""
    token = get_auth_token()
    
    # Create task
    create_response = client.post(
        "/api/tasks/",
        json={"title": "Original Title", "description": "Original description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Update task
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "urgent"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["priority"] == "urgent"

def test_complete_task():
    """Test marking task as completed"""
    token = get_auth_token()
    
    # Create task
    create_response = client.post(
        "/api/tasks/",
        json={"title": "Task to Complete"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Complete task
    response = client.post(
        f"/api/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["completed_at"] is not None

def test_delete_task():
    """Test deleting a task"""
    token = get_auth_token()
    
    # Create task
    create_response = client.post(
        "/api/tasks/",
        json={"title": "Task to Delete"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Delete task
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"
    
    # Verify task is deleted
    get_response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404