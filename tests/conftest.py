import pytest
import os
import sys
import sqlite3

# Add project root to Python path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
