# Burns Barometer: Automated Job Scout & Application System

**A persistent multi-agent system designed to find, filter, and apply for jobs automatically.**

---

## 1. Tech Stack Requirements

- **Language:** Python 3.10+
- **Database:** SQLite (to track `job_id`, `company`, `role`, `date_found`, `application_status`, and prevent duplicates)
- **LLM Integration:** Anthropic Claude (via API) or OpenAI
- **Web Scraping:** Playwright or Beautiful Soup (for dynamic/static content)
- **Resume Generation:** Python-Markdown + ReportLab (PDF export)
- **Task Scheduling:** APScheduler (for recurring Scout runs)
- **Logging:** Python's built-in `logging` module

---

## 2. System Architecture

### Core Components

#### **The Scout (Job Scraper)**
Searches LinkedIn, Indeed, and company career pages based on user criteria (e.g., "Senior/Staff Product PM in AI/DevTools"). Filters jobs posted in the last 15 days and validates job listings against company career pages to prevent ghost jobs.

#### **The Barometer (Fit Analysis)**
Analyzes job descriptions against the user's "Strategic Narrative" (founder background, technical leadership, product vision) and assigns a **Fit Score (0-100%)**.

#### **The Mirror (Resume/Cover Letter Generator)**
Creates a Markdown-based resume and tailored cover letter using Claude's API. Adapts language and emphasis to match each job description's keywords and tone.

#### **The Tribunal (Quality Feedback Loop)**
A multi-persona review system (ATS Specialist, Recruiter, Hiring Manager) that critiques drafts. If score < 90/100, sends feedback back to The Mirror for refinement.

#### **The Gatekeeper (Human Approval)**
Pauses before submission and requests explicit user approval. Shows side-by-side comparisons of application materials vs. job description.

---

## 3. File Structure

```
burns-barometer/
├── README.md
├── requirements.txt
├── config.example.yaml
├── config.yaml (gitignored)
│
├── agents/
│   ├── __init__.py
│   ├── scout.py                 # The Scout (web scraper)
│   ├── barometer.py             # The Barometer (fit analysis)
│   ├── mirror.py                # The Mirror (resume/CL generator)
│   ├── tribunal.py              # The Tribunal (feedback loop)
│   ├── gatekeeper.py            # The Gatekeeper (approval handler)
│   └── prompts.py               # Centralized LLM prompts
│
├── db/
│   ├── __init__.py
│   ├── manager.py               # Database Manager
│   ├── models.py                # SQLAlchemy models (optional)
│   └── schema.sql               # Initial schema
│
├── utils/
│   ├── __init__.py
│   ├── llm_client.py            # LLM API wrapper
│   ├── file_handler.py          # Resume/CL file I/O
│   ├── validators.py            # URL, email, text validation
│   └── logger.py                # Logging configuration
│
├── storage/
│   ├── resumes/                 # Generated resume markdowns
│   ├── cover_letters/           # Generated cover letters
│   ├── applications/            # Submitted applications (audit trail)
│   └── logs/                    # System logs
│
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_scout.py
│   ├── test_barometer.py
│   ├── test_mirror.py
│   └── test_tribunal.py
│
├── strategic_narrative.yaml     # User's background & narrative
├── main.py                      # Entry point & orchestrator
└── scheduler.py                 # Background job scheduling
```

---

## 4. Database Manager

### Schema Design

```sql
CREATE TABLE listings (
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

CREATE TABLE applications (
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

CREATE TABLE company_careers_cache (
    company TEXT PRIMARY KEY,
    careers_url TEXT,
    last_verified TIMESTAMP,
    is_valid BOOLEAN DEFAULT 1,
    verification_notes TEXT
);

CREATE INDEX idx_status ON listings(application_status);
CREATE INDEX idx_date_found ON listings(date_found);
CREATE INDEX idx_company ON listings(company);
```

### Database Manager Code

```python
# db/manager.py

import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for job listings and applications."""
    
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
    
    def initialize_db(self):
        """Create database and tables if they don't exist."""
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
        CREATE INDEX IF NOT EXISTS idx_source ON listings(source);
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
        
        Args:
            url: Job posting URL
            company: Company name
            role: Job title
            description: Full job description
            source: Source (LinkedIn, Indeed, etc.)
            location: Job location
            job_type: Full-time, Contract, etc.
            date_posted: Date job was posted
            company_careers_url: Official company careers page URL
            careers_page_verified: Whether the listing was verified on careers page
        
        Returns:
            job_id if successful, None if duplicate
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
        """
        Fetch recent job listings not yet analyzed.
        
        Args:
            days: Only get jobs posted in the last N days
            limit: Maximum number of listings to return
        
        Returns:
            List of job listing dictionaries
        """
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
        """Update application status (new, reviewed, approved, submitted, rejected)."""
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


# Usage Example
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Test saving a listing
    job_id = db.save_listing(
        url="https://example.com/jobs/123",
        company="Acme Corp",
        role="Senior Product Manager",
        description="Looking for a talented PM...",
        source="LinkedIn",
        location="San Francisco, CA",
        job_type="Full-time",
        date_posted="2025-02-09",
        company_careers_url="https://careers.acme.com/jobs/123",
        careers_page_verified=True
    )
    
    if job_id:
        print(f"Job saved with ID: {job_id}")
        db.update_fit_score(job_id, 85.5, "Strong match for PM role")
    
    db.close()
```

---

## 5. Preventing "Ghost Jobs": Careers Page Verification

### Problem Statement

Job listings can be "ghost jobs"—positions posted on LinkedIn or Indeed but no longer available on the company's official careers page. This wastes time and resources.

### Solution: The Gatekeeper's Careers Page Validator

**Implementation in The Scout:**

```python
# agents/scout.py (excerpt)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class CareerPageValidator:
    """Validates that a job listing exists on the company's official careers page."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_careers_url(self, company_name: str, job_url: str) -> Optional[str]:
        """
        Attempt to find the company's official careers page URL.
        
        Strategy:
        1. Check database cache first
        2. Common patterns (careers.company.com, company.com/careers, etc.)
        3. Search company website for "Careers" link
        4. Use LinkedIn company page to find careers URL
        """
        # Check cache
        cached_url = self.db.get_cached_careers_url(company_name)
        if cached_url:
            logger.info(f"Using cached careers URL for {company_name}")
            return cached_url
        
        # Strategy 1: Common patterns
        common_patterns = [
            f"https://careers.{company_name.lower()}.com",
            f"https://{company_name.lower()}.com/careers",
            f"https://{company_name.lower()}.com/jobs",
            f"https://www.{company_name.lower()}.com/careers",
        ]
        
        for pattern in common_patterns:
            if self._validate_url(pattern):
                self.db.cache_company_careers_url(company_name, pattern, True, "Found via pattern matching")
                return pattern
        
        # Strategy 2: Extract domain from job URL and look for careers page
        if job_url:
            domain = self._extract_domain(job_url)
            careers_url = self._scrape_careers_link_from_domain(domain)
            if careers_url:
                self.db.cache_company_careers_url(company_name, careers_url, True, "Found via domain scraping")
                return careers_url
        
        # Cache negative result
        self.db.cache_company_careers_url(company_name, "", False, "Careers URL not found")
        return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract base domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc
    
    def _validate_url(self, url: str) -> bool:
        """Check if URL is reachable and returns 200."""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to validate {url}: {e}")
            return False
    
    def _scrape_careers_link_from_domain(self, domain: str) -> Optional[str]:
        """Scrape the main website to find careers link."""
        try:
            response = self.session.get(f"https://{domain}", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for "Careers" links
            careers_patterns = ['careers', 'jobs', 'join', 'apply', 'work with us']
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                link_href = link['href']
                
                if any(pattern in link_text for pattern in careers_patterns):
                    full_url = urljoin(f"https://{domain}", link_href)
                    if self._validate_url(full_url):
                        return full_url
            
            return None
        except Exception as e:
            logger.warning(f"Failed to scrape {domain}: {e}")
            return None
    
    def verify_job_on_careers_page(self, job_title: str, company: str, careers_url: str) -> bool:
        """
        Verify that the job listing exists on the company's official careers page.
        
        Returns:
            True if job found on careers page, False otherwise
        """
        if not careers_url:
            logger.warning(f"No careers URL provided for {company}")
            return False
        
        try:
            response = self.session.get(careers_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Normalize job title for matching (remove common suffixes)
            normalized_title = job_title.lower().replace(" - ", " ").replace("(", "").replace(")", "")
            key_words = normalized_title.split()[:3]  # Check first 3 words
            
            matches = sum(1 for word in key_words if word in page_text)
            if matches >= 2:  # At least 2 keywords must match
                logger.info(f"✓ Job verified on {company} careers page")
                return True
            else:
                logger.warning(f"✗ Job NOT found on {company} careers page - likely ghost job")
                return False
        
        except Exception as e:
            logger.error(f"Error verifying job on careers page: {e}")
            return False


class Scout:
    """The Scout: Finds and scrapes job listings from multiple sources."""
    
    def __init__(self, db_manager, llm_client):
        self.db = db_manager
        self.llm = llm_client
        self.validator = CareerPageValidator(db_manager)
    
    def scrape_and_save(self, job_url: str, company: str, role: str, description: str, source: str):
        """
        Scrape job and save to DB only if verified on careers page.
        """
        # Step 1: Find official careers URL
        careers_url = self.validator.find_careers_url(company, job_url)
        
        # Step 2: Verify job on careers page
        is_verified = False
        if careers_url:
            is_verified = self.validator.verify_job_on_careers_page(role, company, careers_url)
        
        if not is_verified:
            logger.warning(f"Skipping ghost job: {company} - {role}")
            self.db.audit_log(None, "ghost_job_rejected", f"{company} - {role}")
            return None
        
        # Step 3: Save to database only if verified
        job_id = self.db.save_listing(
            url=job_url,
            company=company,
            role=role,
            description=description,
            source=source,
            company_careers_url=careers_url,
            careers_page_verified=True
        )
        
        return job_id
```

---

## 6. System Orchestration

### Main Entry Point

```python
# main.py

import logging
from datetime import datetime
from agents.scout import Scout
from agents.barometer import Barometer
from agents.mirror import Mirror
from agents.tribunal import Tribunal
from agents.gatekeeper import Gatekeeper
from db.manager import DatabaseManager
from utils.llm_client import LLMClient
from utils.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


class BurnsBarometer:
    """Orchestrates the entire job application workflow."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.db = DatabaseManager()
        self.llm = LLMClient()
        
        self.scout = Scout(self.db, self.llm)
        self.barometer = Barometer(self.db, self.llm)
        self.mirror = Mirror(self.db, self.llm)
        self.tribunal = Tribunal(self.db, self.llm)
        self.gatekeeper = Gatekeeper(self.db)
    
    def run_full_cycle(self):
        """Execute one complete cycle: Scout → Barometer → Mirror → Tribunal → Gatekeeper."""
        logger.info("=== Burns Barometer Cycle Started ===")
        
        # 1. Scout: Find recent unprocessed jobs
        recent_jobs = self.db.get_recent_unprocessed_listings()
        logger.info(f"Found {len(recent_jobs)} recent unprocessed jobs")
        
        for job in recent_jobs:
            try:
                # 2. Barometer: Analyze fit
                fit_score = self.barometer.analyze(job)
                self.db.update_fit_score(job['job_id'], fit_score)
                logger.info(f"Fit score for {job['role']}: {fit_score}/100")
                
                # Skip low-fit jobs
                if fit_score < 50:
                    self.db.update_application_status(job['job_id'], 'rejected_low_fit')
                    continue
                
                # 3. Mirror: Generate resume + cover letter
                resume_md, cl_md = self.mirror.generate(job)
                
                # 4. Tribunal: Multi-persona review
                tribunal_score, feedback = self.tribunal.review(job, resume_md, cl_md)
                
                # Iterate if needed
                iteration = 0
                while tribunal_score < 90 and iteration < 3:
                    logger.info(f"Rewriting application (iteration {iteration + 1}, score: {tribunal_score})")
                    resume_md, cl_md = self.mirror.refine(job, feedback)
                    tribunal_score, feedback = self.tribunal.review(job, resume_md, cl_md)
                    iteration += 1
                
                # 5. Gatekeeper: Ask for user approval
                application_id = self.db.save_application(
                    job['job_id'], resume_md, cl_md, tribunal_score
                )
                
                approved = self.gatekeeper.request_approval(job, resume_md, cl_md, tribunal_score)
                
                if approved:
                    self.db.mark_application_submitted(application_id)
                    self.db.update_application_status(job['job_id'], 'submitted')
                    logger.info(f"✓ Application submitted for {job['role']}")
                else:
                    self.db.update_application_status(job['job_id'], 'user_rejected')
                    logger.info(f"✗ Application rejected by user for {job['role']}")
            
            except Exception as e:
                logger.error(f"Error processing job {job['job_id']}: {e}")
                self.db.update_application_status(job['job_id'], 'error')
        
        logger.info("=== Burns Barometer Cycle Complete ===")
    
    def cleanup(self):
        """Close all connections."""
        self.db.close()


if __name__ == "__main__":
    barometer = BurnsBarometer()
    barometer.run_full_cycle()
    barometer.cleanup()
```

---

## 7. Key Constraints & Principles

### Absolute Truthfulness
- Never exaggerate qualifications or experiences in resumes
- Tailor language, not claims
- Flag discrepancies between user narrative and job requirements

### Human-in-the-Loop
- Always pause before submission
- Show side-by-side comparison: application vs. job description
- Allow user to reject, request rewrites, or approve

### Efficiency
- Cache company careers URLs to avoid repeated lookups
- Rate limit API calls (1 request/second for scraping)
- Deduplicate jobs before processing

### Auditability
- Maintain complete audit log of all actions
- Store all versions of resume/cover letter
- Track tribunal feedback for each application

---

## 8. Next Steps

1. **Implement LLM Client** (`utils/llm_client.py`) — wrapper around Anthropic API
2. **Develop Agent Prompts** (`agents/prompts.py`) — detailed system prompts for each agent
3. **Build The Barometer** (`agents/barometer.py`) — Fit Score logic
4. **Build The Mirror** (`agents/mirror.py`) — Resume/CL generation
5. **Build The Tribunal** (`agents/tribunal.py`) — Multi-persona feedback
6. **Build The Gatekeeper** (`agents/gatekeeper.py`) — User approval interface
7. **Write Tests** — Unit tests for each agent and DB operations
8. **Deploy Scheduler** (`scheduler.py`) — Run cycles on a schedule (daily, etc.)

---

## 9. Configuration Template

```yaml
# config.yaml

llm:
  provider: "anthropic"  # or "openai"
  model: "claude-opus-4-5-20251101"
  api_key: "${ANTHROPIC_API_KEY}"
  temperature: 0.7

database:
  path: "jobs.db"
  backup_interval_days: 7

scout:
  sources:
    - "linkedin"
    - "indeed"
    - "careers_pages"
  keywords:
    - "Senior Product Manager"
    - "Staff PM"
    - "AI/ML Product"
  locations:
    - "San Francisco, CA"
    - "Remote"
  max_age_days: 15
  rate_limit_seconds: 1

barometer:
  min_fit_score: 50
  weight_seniority: 0.3
  weight_tech_stack: 0.25
  weight_domain_match: 0.25
  weight_growth_opportunity: 0.2

tribunal:
  personas:
    - "ATS Specialist"
    - "Recruiter"
    - "Hiring Manager"
  min_approval_score: 90

gatekeeper:
  require_user_approval: true
  show_comparison: true

logging:
  level: "INFO"
  file: "storage/logs/barometer.log"
```

---

## 10. Success Metrics

- **Application Submission Rate:** % of reviewed jobs resulting in submissions
- **Average Fit Score:** Distribution of quality matches
- **Tribunal Refinement Cycles:** Average iterations needed to reach 90/100
- **Ghost Job Detection:** % of jobs rejected due to careers page mismatch
- **Time Saved:** Manual hours vs. automated processing

---

**Version:** 1.0  
**Last Updated:** February 9, 2025  
**Owner:** Senior AI Engineer  
**Status:** Design Complete — Ready for Implementation
