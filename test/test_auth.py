import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db, SessionLocal

client = TestClient(app)

@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=SessionLocal().get_bind())
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=SessionLocal().get_bind())

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/users/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "test123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

def test_register_duplicate_email():
    """Test registration with duplicate email"""
    # First registration
    client.post(
        "/api/users/register",
        json={
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "test123"
        }
    )
    
    # Second registration with same email
    response = client.post(
        "/api/users/register",
        json={
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "test123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success():
    """Test successful login"""
    # Register user first
    client.post(
        "/api/users/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "test123"
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "loginuser",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password():
    """Test login with wrong password"""
    # Register user
    client.post(
        "/api/users/register",
        json={
            "email": "wrongpass@example.com",
            "username": "wronguser",
            "password": "correct123"
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/api/auth/login",
        data={
            "username": "wronguser",
            "password": "wrong123"
        }
    )
    assert response.status_code == 401

def test_get_current_user():
    """Test getting current user info"""
    # Register and login
    client.post(
        "/api/users/register",
        json={
            "email": "current@example.com",
            "username": "currentuser",
            "password": "test123"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "currentuser",
            "password": "test123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "currentuser"