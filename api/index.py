from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys

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
    db = DatabaseManager("jobs.db") # Note: In Vercel serverless, SQLite is read-only or ephemeral. 
                                    # For production Vercel, use Postgres (Neon/Supabase).
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT a.*, l.company, l.role, l.url, l.fit_score
        FROM applications a
        JOIN listings l ON a.job_id = l.job_id
        WHERE a.status = 'reviewed'
        ORDER BY l.fit_score DESC
    """)
    jobs = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jobs

# Note: For full Vercel deployment, we'd need to migrate DB to Postgres
# and move the heavy agent logic to background workers (Celery/Inngest)
# as Vercel functions have timeout limits (10s-60s).
