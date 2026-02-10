import pytest
from agents.barometer import Barometer
from agents.mirror import Mirror

def test_barometer_analysis(db_manager, mock_llm_client):
    config = {'barometer': {'min_fit_score': 60}}
    barometer = Barometer(db_manager, mock_llm_client, config)
    
    # Mock narrative loading
    barometer.narrative = {"name": "Test Narrative"}
    
    job = {
        'job_id': '123',
        'company': 'Test Corp',
        'role': 'Engineer',
        'description': 'Python dev'
    }
    
    score = barometer.analyze(job)
    assert score == 85.0

def test_mirror_generation(db_manager, mock_llm_client):
    mirror = Mirror(db_manager, mock_llm_client)
    # Mock master source loading
    mirror.master_source = "# Master Resume"
    
    job = {
        'job_id': '123',
        'company': 'Test Corp',
        'role': 'Engineer',
        'description': 'Python dev'
    }
    
    resume, cl = mirror.generate(job)
    assert resume == "Mocked response"
    assert cl == "Mocked response"
