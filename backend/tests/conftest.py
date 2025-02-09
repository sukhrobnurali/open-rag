import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base


@pytest.fixture(scope="session")
def temp_db():
    """Create a temporary database for testing"""
    db_fd, db_path = tempfile.mkstemp()
    yield f"sqlite:///{db_path}"
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def test_db_session(temp_db):
    """Create a test database session"""
    engine = create_engine(temp_db, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_openai_responses():
    """Mock OpenAI API responses for testing"""
    return {
        "embedding": [0.1] * 1536,  # Mock embedding vector
        "completion": "This is a test response from the AI."
    }