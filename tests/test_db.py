import pytest
from db.manager import DatabaseManager

def test_save_listing(db_manager):
    job_id = db_manager.save_listing(
        url="http://example.com/job1",
        company="Test Corp",
        role="Engineer",
        description="Do work",
        source="test"
    )
    assert job_id is not None
    
    # Test duplicate prevention
    job_id_2 = db_manager.save_listing(
        url="http://example.com/job1",
        company="Test Corp",
        role="Engineer",
        description="Do work",
        source="test"
    )
    assert job_id_2 is None

def test_application_workflow(db_manager):
    job_id = db_manager.save_listing(
        url="http://example.com/job2",
        company="Test Corp",
        role="Engineer",
        description="Do work",
        source="test"
    )
    
    app_id = db_manager.save_application(
        job_id=job_id,
        resume_version="Resume v1",
        cover_letter_version="CL v1",
        tribunal_score=95.0
    )
    assert app_id is not None
    
    db_manager.mark_application_submitted(app_id)
    
    cursor = db_manager.conn.cursor()
    cursor.execute("SELECT status FROM applications WHERE application_id = ?", (app_id,))
    assert cursor.fetchone()[0] == 'submitted'
