import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database-agnostic manager (SQLite/PostgreSQL) using SQLAlchemy.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        # Default to SQLite if no URL provided
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///jobs.db")
        
        # Handle "postgres://" vs "postgresql://" for SQLAlchemy compatibility
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)
            
        self.engine = create_engine(self.db_url)
        self.initialize_db()
    
    def initialize_db(self):
        """Create tables if they don't exist."""
        # Check if using SQLite to create directory
        if self.db_url.startswith("sqlite"):
            db_path = self.db_url.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

        # Common Schema (compatible with both SQLite and Postgres)
        # Note: We use TEXT for most fields to be safe, but Postgres supports specific types.
        # SQLAlchemy handles the dialect differences if we used ORM models, 
        # but for raw SQL we need to be careful.
        
        # We'll use a simple check to see if tables exist, or just IF NOT EXISTS
        
        with self.engine.connect() as conn:
            # Listings Table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS listings (
                    job_id VARCHAR(32) PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    company TEXT NOT NULL,
                    role TEXT NOT NULL,
                    location TEXT,
                    job_type TEXT,
                    description TEXT NOT NULL,
                    date_posted VARCHAR(32),
                    date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    company_careers_url TEXT,
                    careers_page_verified BOOLEAN DEFAULT FALSE,
                    application_status VARCHAR(32) DEFAULT 'new',
                    fit_score FLOAT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Applications Table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS applications (
                    application_id VARCHAR(32) PRIMARY KEY,
                    job_id VARCHAR(32) NOT NULL UNIQUE,
                    status VARCHAR(32),
                    resume_version TEXT,
                    cover_letter_version TEXT,
                    tribunal_final_score FLOAT,
                    submitted_at TIMESTAMP,
                    user_approved BOOLEAN DEFAULT FALSE,
                    feedback TEXT,
                    FOREIGN KEY(job_id) REFERENCES listings(job_id)
                );
            """))
            
            # Cache Table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS company_careers_cache (
                    company VARCHAR(255) PRIMARY KEY,
                    careers_url TEXT,
                    last_verified TIMESTAMP,
                    is_valid BOOLEAN DEFAULT TRUE,
                    verification_notes TEXT
                );
            """))
            
            # Audit Log
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id SERIAL PRIMARY KEY,
                    job_id VARCHAR(32),
                    action VARCHAR(64),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                );
            """) if "postgresql" in self.db_url else text("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    FOREIGN KEY(job_id) REFERENCES listings(job_id)
                );
            """))
            
            # Indexes (Postgres/SQLite syntax slightly different for IF NOT EXISTS on indexes)
            # We'll skip explicit index creation in this raw SQL block to avoid errors, 
            # or wrap in try/except.
            try:
                conn.execute(text("CREATE INDEX idx_status ON listings(application_status);"))
            except Exception:
                pass # Index likely exists

            conn.commit()
            
        logger.info(f"Database initialized at {self.db_url}")
    
    def generate_job_id(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def is_duplicate(self, url: str) -> bool:
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT job_id FROM listings WHERE url = :url"), {"url": url})
            return result.fetchone() is not None
    
    def save_listing(self, url: str, company: str, role: str, description: str, source: str, **kwargs) -> Optional[str]:
        if self.is_duplicate(url):
            return None
        
        job_id = self.generate_job_id(url)
        
        # Prepare params
        params = {
            "job_id": job_id,
            "url": url,
            "company": company,
            "role": role,
            "description": description,
            "source": source,
            "location": kwargs.get("location"),
            "job_type": kwargs.get("job_type"),
            "date_posted": kwargs.get("date_posted"),
            "company_careers_url": kwargs.get("company_careers_url"),
            "careers_page_verified": kwargs.get("careers_page_verified", False)
        }
        
        query = text("""
            INSERT INTO listings (
                job_id, url, company, role, description, source, location, job_type, 
                date_posted, company_careers_url, careers_page_verified
            ) VALUES (
                :job_id, :url, :company, :role, :description, :source, :location, :job_type,
                :date_posted, :company_careers_url, :careers_page_verified
            )
        """)
        
        try:
            with self.engine.connect() as conn:
                conn.execute(query, params)
                conn.commit()
            return job_id
        except Exception as e:
            logger.error(f"Failed to save listing: {e}")
            return None

    def get_recent_unprocessed_listings(self, days: int = 15, limit: int = 50) -> List[Dict]:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = text("""
            SELECT * FROM listings
            WHERE date_found > :cutoff_date 
              AND application_status = 'new'
            ORDER BY date_found DESC
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {"cutoff_date": cutoff_date, "limit": limit})
            # Convert rows to dicts
            return [dict(row._mapping) for row in result]

    def update_fit_score(self, job_id: str, score: float, notes: str = ""):
        query = text("""
            UPDATE listings
            SET fit_score = :score, notes = :notes, application_status = 'analyzed', updated_at = CURRENT_TIMESTAMP
            WHERE job_id = :job_id
        """)
        with self.engine.connect() as conn:
            conn.execute(query, {"score": score, "notes": notes, "job_id": job_id})
            conn.commit()

    def update_application_status(self, job_id: str, status: str):
        query = text("""
            UPDATE listings
            SET application_status = :status, updated_at = CURRENT_TIMESTAMP
            WHERE job_id = :job_id
        """)
        with self.engine.connect() as conn:
            conn.execute(query, {"status": status, "job_id": job_id})
            conn.commit()

    def save_application(self, job_id: str, resume_version: str, cover_letter_version: str, tribunal_score: float, user_approved: bool = False) -> str:
        import uuid
        application_id = str(uuid.uuid4())[:12]
        
        query = text("""
            INSERT INTO applications (
                application_id, job_id, status, resume_version, 
                cover_letter_version, tribunal_final_score, user_approved
            ) VALUES (
                :app_id, :job_id, 'draft', :resume, :cl, :score, :approved
            )
        """)
        
        with self.engine.connect() as conn:
            conn.execute(query, {
                "app_id": application_id,
                "job_id": job_id,
                "resume": resume_version,
                "cl": cover_letter_version,
                "score": tribunal_score,
                "approved": user_approved
            })
            conn.commit()
        return application_id

    def mark_application_submitted(self, application_id: str):
        query = text("""
            UPDATE applications
            SET status = 'submitted', submitted_at = CURRENT_TIMESTAMP
            WHERE application_id = :app_id
        """)
        with self.engine.connect() as conn:
            conn.execute(query, {"app_id": application_id})
            conn.commit()

    def cache_company_careers_url(self, company: str, careers_url: str, is_valid: bool = True, notes: str = ""):
        # Upsert logic differs between SQLite and Postgres.
        # For simplicity, we'll try update, if 0 rows, then insert.
        
        with self.engine.connect() as conn:
            # Try Update
            result = conn.execute(text("""
                UPDATE company_careers_cache 
                SET careers_url = :url, is_valid = :valid, verification_notes = :notes, last_verified = CURRENT_TIMESTAMP
                WHERE company = :company
            """), {"url": careers_url, "valid": is_valid, "notes": notes, "company": company})
            
            if result.rowcount == 0:
                # Insert
                conn.execute(text("""
                    INSERT INTO company_careers_cache (company, careers_url, is_valid, verification_notes, last_verified)
                    VALUES (:company, :url, :valid, :notes, CURRENT_TIMESTAMP)
                """), {"company": company, "url": careers_url, "valid": is_valid, "notes": notes})
            
            conn.commit()

    def get_cached_careers_url(self, company: str) -> Optional[str]:
        query = text("SELECT careers_url FROM company_careers_cache WHERE company = :company AND is_valid = :valid")
        with self.engine.connect() as conn:
            result = conn.execute(query, {"company": company, "valid": True})
            row = result.fetchone()
            return row[0] if row else None

    def audit_log(self, job_id: Optional[str], action: str, details: str = ""):
        query = text("INSERT INTO audit_log (job_id, action, details) VALUES (:job_id, :action, :details)")
        with self.engine.connect() as conn:
            conn.execute(query, {"job_id": job_id, "action": action, "details": details})
            conn.commit()

    def close(self):
        self.engine.dispose()
