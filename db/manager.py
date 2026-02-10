import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for job listings and applications."""
    
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
    
    def initialize_db(self):
        """Create database and tables if they don't exist."""
        # Ensure db directory exists if path contains directories
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        schema = """
        CREATE TABLE IF NOT EXISTS listings (
            job_id TEXT PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            job_type TEXT,
            description TEXT NOT NULL,
            date_posted DATE,
            date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            is_verified BOOLEAN DEFAULT 0,
            company_careers_url TEXT,
            careers_page_verified BOOLEAN DEFAULT 0,
            application_status TEXT DEFAULT 'new',
            fit_score REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS applications (
            application_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL UNIQUE,
            status TEXT,
            resume_version TEXT,
            cover_letter_version TEXT,
            tribunal_final_score REAL,
            submitted_at TIMESTAMP,
            user_approved BOOLEAN DEFAULT 0,
            feedback TEXT,
            FOREIGN KEY(job_id) REFERENCES listings(job_id)
        );
        
        CREATE TABLE IF NOT EXISTS company_careers_cache (
            company TEXT PRIMARY KEY,
            careers_url TEXT,
            last_verified TIMESTAMP,
            is_valid BOOLEAN DEFAULT 1,
            verification_notes TEXT
        );
        
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY(job_id) REFERENCES listings(job_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_status ON listings(application_status);
        CREATE INDEX IF NOT EXISTS idx_date_found ON listings(date_found);
        CREATE INDEX IF NOT EXISTS idx_company ON listings(company);
        """
        
        cursor.executescript(schema)
        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")
    
    def generate_job_id(self, url: str) -> str:
        """Generate a unique job ID from URL hash."""
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def is_duplicate(self, url: str) -> bool:
        """Check if a job URL already exists in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT job_id FROM listings WHERE url = ?", (url,))
        return cursor.fetchone() is not None
    
    def save_listing(
        self,
        url: str,
        company: str,
        role: str,
        description: str,
        source: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        date_posted: Optional[str] = None,
        company_careers_url: Optional[str] = None,
        careers_page_verified: bool = False
    ) -> Optional[str]:
        """
        Save a job listing to the database.
        Returns job_id if successful, None if duplicate.
        """
        if self.is_duplicate(url):
            logger.warning(f"Duplicate job URL: {url}")
            return None
        
        job_id = self.generate_job_id(url)
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO listings (
                    job_id, url, company, role, location, job_type, description,
                    date_posted, source, company_careers_url, careers_page_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, url, company, role, location, job_type, description,
                date_posted, source, company_careers_url, careers_page_verified
            ))
            self.conn.commit()
            self.audit_log(job_id, "listing_created", f"Added from {source}")
            logger.info(f"Saved job listing: {job_id} - {company} {role}")
            return job_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to save listing: {e}")
            return None
    
    def get_recent_unprocessed_listings(self, days: int = 15, limit: int = 50) -> List[Dict]:
        """Fetch recent job listings not yet analyzed."""
        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT * FROM listings
            WHERE date_found > ? 
              AND application_status = 'new'
            ORDER BY date_found DESC
            LIMIT ?
        """, (cutoff_date, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_fit_score(self, job_id: str, score: float, notes: str = ""):
        """Update a job's fit score and status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE listings
            SET fit_score = ?, notes = ?, application_status = 'analyzed', updated_at = CURRENT_TIMESTAMP
            WHERE job_id = ?
        """, (score, notes, job_id))
        self.conn.commit()
        self.audit_log(job_id, "fit_score_updated", f"Score: {score}")
    
    def update_application_status(self, job_id: str, status: str):
        """Update application status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE listings
            SET application_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE job_id = ?
        """, (status, job_id))
        self.conn.commit()
        self.audit_log(job_id, "status_updated", f"Status: {status}")
    
    def save_application(
        self,
        job_id: str,
        resume_version: str,
        cover_letter_version: str,
        tribunal_score: float,
        user_approved: bool = False
    ) -> str:
        """Save draft application with tribunal feedback."""
        import uuid
        application_id = str(uuid.uuid4())[:12]
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO applications (
                application_id, job_id, status, resume_version, 
                cover_letter_version, tribunal_final_score, user_approved
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            application_id, job_id, "draft", resume_version,
            cover_letter_version, tribunal_score, user_approved
        ))
        self.conn.commit()
        self.audit_log(job_id, "application_drafted", f"App ID: {application_id}")
        return application_id
    
    def mark_application_submitted(self, application_id: str):
        """Mark an application as officially submitted."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE applications
            SET status = 'submitted', submitted_at = CURRENT_TIMESTAMP
            WHERE application_id = ?
        """, (application_id,))
        self.conn.commit()
    
    def cache_company_careers_url(self, company: str, careers_url: str, is_valid: bool = True, notes: str = ""):
        """Cache a company's careers page URL."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO company_careers_cache (company, careers_url, is_valid, verification_notes, last_verified)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (company, careers_url, is_valid, notes))
        self.conn.commit()
    
    def get_cached_careers_url(self, company: str) -> Optional[str]:
        """Retrieve cached careers URL for a company."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT careers_url, is_valid FROM company_careers_cache
            WHERE company = ? AND is_valid = 1
        """, (company,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def audit_log(self, job_id: Optional[str], action: str, details: str = ""):
        """Log system actions for audit trail."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (job_id, action, details)
            VALUES (?, ?, ?)
        """, (job_id, action, details))
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
