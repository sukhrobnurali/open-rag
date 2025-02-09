import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Advanced RAG System API"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_query_health():
    response = client.get("/api/v1/query/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_documents_list():
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_document_upload():
    # Test uploading invalid file type
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.xyz", b"test content", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


def test_query_without_question():
    response = client.post(
        "/api/v1/query/",
        json={"question": ""}
    )
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_nonexistent_document():
    response = client.get("/api/v1/documents/99999")
    assert response.status_code == 404