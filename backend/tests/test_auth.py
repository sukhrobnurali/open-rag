import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.auth.auth import get_password_hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


class TestAuthentication:
    def test_register_user(self, client, test_user_data):
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert data["is_active"] is True
        assert data["is_admin"] is False

    def test_register_duplicate_user(self, client, test_user_data):
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register same email again
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user_data):
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        response = client.post("/api/v1/auth/login", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user_data):
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try login with wrong password
        wrong_data = test_user_data.copy()
        wrong_data["password"] = "wrongpassword"
        
        response = client.post("/api/v1/auth/login", json=wrong_data)
        assert response.status_code == 401

    def test_get_current_user(self, client, test_user_data):
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post("/api/v1/auth/login", json=test_user_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]

    def test_protected_route_without_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403