import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_docs.db"
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
def sample_pdf_file():
    # Create a simple text file for testing
    file_content = b"This is a test document content for the RAG system."
    return ("test.txt", io.BytesIO(file_content), "text/plain")


class TestDocumentUpload:
    def test_upload_valid_document(self, client, sample_pdf_file):
        filename, file_obj, content_type = sample_pdf_file
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["filename"] == filename
        assert data["status"] == "uploaded"

    def test_upload_invalid_file_type(self, client):
        file_content = b"Invalid file content"
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.xyz", io.BytesIO(file_content), "application/octet-stream")}
        )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    def test_upload_oversized_file(self, client):
        # Create a file larger than 50MB (simulated)
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
        )
        
        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["detail"]

    def test_list_documents(self, client, sample_pdf_file):
        # Upload a document first
        filename, file_obj, content_type = sample_pdf_file
        client.post(
            "/api/v1/documents/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        
        # List documents
        response = client.get("/api/v1/documents/")
        assert response.status_code == 200
        documents = response.json()
        assert len(documents) == 1
        assert documents[0]["original_filename"] == filename

    def test_get_document_by_id(self, client, sample_pdf_file):
        # Upload a document first
        filename, file_obj, content_type = sample_pdf_file
        upload_response = client.post(
            "/api/v1/documents/upload",
            files={"file": (filename, file_obj, content_type)}
        )
        document_id = upload_response.json()["document_id"]
        
        # Get document by ID
        response = client.get(f"/api/v1/documents/{document_id}")
        assert response.status_code == 200
        document = response.json()
        assert document["id"] == document_id
        assert document["original_filename"] == filename

    def test_get_nonexistent_document(self, client):
        response = client.get("/api/v1/documents/999")
        assert response.status_code == 404