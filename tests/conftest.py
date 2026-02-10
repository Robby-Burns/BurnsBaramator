import pytest
import os
import sqlite3
from db.manager import DatabaseManager

@pytest.fixture
def db_manager(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_jobs.db"
    manager = DatabaseManager(str(db_path))
    yield manager
    manager.close()

@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    class MockLLM:
        def generate(self, system, user):
            return "Mocked response"
        
        def generate_structured(self, system, user, schema):
            return {"score": 85.0, "feedback": "Good match", "company": "TestCorp", "role": "TestRole"}
            
    return MockLLM()
