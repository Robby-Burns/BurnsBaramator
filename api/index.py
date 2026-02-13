from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys
from sqlalchemy import text

# Add parent directory to path so we can import from agents/db/utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.manager import DatabaseManager

app = FastAPI()

class JobRequest(BaseModel):
    url: str
    company: str
    role: str

@app.get("/")
def read_root():
    return {"status": "Burns Barometer is running"}

@app.get("/jobs/pending")
def get_pending_jobs():
    """Get jobs waiting for approval (Gatekeeper API)."""
    # Use default DB URL from env (handles both SQLite and Postgres)
    db = DatabaseManager() 
    
    with db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT a.*, l.company, l.role, l.url, l.fit_score
            FROM applications a
            JOIN listings l ON a.job_id = l.job_id
            WHERE a.status = 'reviewed'
            ORDER BY l.fit_score DESC
        """))
        jobs = [dict(row._mapping) for row in result]
    
    db.close()
    return jobs
