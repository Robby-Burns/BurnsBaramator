import logging
import os
import json
from datetime import datetime
from typing import Dict, Tuple
from db.manager import DatabaseManager
from utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class Mirror:
    """
    The Mirror: Generates tailored resumes and cover letters based on the 
    Master Resume Source and the specific job description.
    """
    
    def __init__(self, db_manager: DatabaseManager, llm_client: LLMClient):
        self.db = db_manager
        self.llm = llm_client
        self.master_source = self._load_master_source()
        
        # Ensure storage directories exist
        os.makedirs("storage/resumes", exist_ok=True)
        os.makedirs("storage/cover_letters", exist_ok=True)

    def _load_master_source(self) -> str:
        """Load the Master Resume Source Markdown file."""
        try:
            with open("docs/BURNS_MASTER_RESUME_SOURCE.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error("docs/BURNS_MASTER_RESUME_SOURCE.md not found!")
            return ""

    def generate(self, job: Dict) -> Tuple[str, str]:
        """
        Generate a tailored resume and cover letter for a specific job.
        Returns: (resume_markdown, cover_letter_markdown)
        """
        logger.info(f"Generating application materials for: {job['company']} - {job['role']}")
        
        # 1. Generate Resume
        resume_md = self._generate_resume(job)
        
        # 2. Generate Cover Letter
        cl_md = self._generate_cover_letter(job, resume_md)
        
        # 3. Save to disk
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = "".join(x for x in job['company'] if x.isalnum())
        filename_base = f"{safe_company}_{job['job_id']}_{timestamp}"
        
        resume_path = f"storage/resumes/{filename_base}_resume.md"
        cl_path = f"storage/cover_letters/{filename_base}_cl.md"
        
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write(resume_md)
            
        with open(cl_path, "w", encoding="utf-8") as f:
            f.write(cl_md)
            
        return resume_md, cl_md

    def _generate_resume(self, job: Dict) -> str:
        """Use LLM to generate a tailored resume from the master source."""
        system_prompt = """
        You are The Mirror, an expert resume writer. 
        Your goal is to generate a TAILORED resume for a specific job using ONLY the content from the Master Resume Source.
        
        RULES:
        1. DO NOT invent experiences. Use the "Master Resume Source" as your database of facts.
        2. Select the most relevant "Strategic Narrative" from the source based on the job description.
        3. Choose the most relevant bullets from "Reusable Bullets by Theme" and "Professional Experience".
        4. Quantify impact using the "Achievements & Impact" section.
        5. Format strictly in Markdown.
        6. Keep it to 2 pages max (concise).
        7. Header should include Name, Email, Phone, Location, and Links as found in the source.
        
        STRUCTURE:
        # Name
        ## Contact Info
        
        ## Professional Summary
        [Tailored summary based on the selected Narrative]
        
        ## Skills
        [Relevant Technical Competencies]
        
        ## Experience
        [Selected roles and bullets relevant to this job]
        
        ## Projects
        [Relevant Consulting & AI Projects]
        
        ## Education & Certifications
        """
        
        user_prompt = f"""
        MASTER RESUME SOURCE:
        {self.master_source}
        
        TARGET JOB:
        Company: {job['company']}
        Role: {job['role']}
        Description: {job['description'][:10000]}
        
        Generate the tailored resume in Markdown.
        """
        
        return self.llm.generate(system_prompt, user_prompt)

    def _generate_cover_letter(self, job: Dict, resume_context: str) -> str:
        """Use LLM to generate a tailored cover letter."""
        system_prompt = """
        You are The Mirror, an expert career coach.
        Your goal is to write a compelling, tailored cover letter.
        
        RULES:
        1. Use the "Cover Letter Templates" section from the Master Resume Source.
        2. Select the template that best fits the target role (e.g., AI PM, Staff Engineer, Ops Leader).
        3. Personalize the [HOOK] and [PROOF POINTS] based on the job description.
        4. Maintain the voice of Robert Burns (Operator + Builder, pragmatic, safety-first).
        5. Format in Markdown.
        """
        
        user_prompt = f"""
        MASTER RESUME SOURCE:
        {self.master_source}
        
        GENERATED RESUME CONTEXT:
        {resume_context[:2000]}...
        
        TARGET JOB:
        Company: {job['company']}
        Role: {job['role']}
        Description: {job['description'][:5000]}
        
        Generate the tailored cover letter in Markdown.
        """
        
        return self.llm.generate(system_prompt, user_prompt)

    def run_generation_cycle(self):
        """
        Fetch analyzed jobs (fit score > threshold) and generate materials.
        """
        logger.info("Mirror generation cycle started.")
        
        # Get jobs that are 'analyzed' but not yet 'drafted'
        # We need to query the DB for this. 
        # Since db manager doesn't have a specific method for this state transition yet,
        # we'll fetch 'analyzed' jobs and check if they have an application entry.
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT * FROM listings 
            WHERE application_status = 'analyzed' 
            AND fit_score >= ?
        """, (self.db.get_recent_unprocessed_listings.__defaults__[0] if False else 60,)) # Hardcoded 60 for now, should come from config
        
        # Better approach: Add a method to DB manager or just execute query here
        # Let's use the config threshold
        min_score = 60 # Default
        
        cursor.execute("""
            SELECT l.* FROM listings l
            LEFT JOIN applications a ON l.job_id = a.job_id
            WHERE l.application_status = 'analyzed'
            AND l.fit_score >= ?
            AND a.application_id IS NULL
        """, (min_score,))
        
        jobs = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Found {len(jobs)} jobs to generate materials for.")
        
        for job in jobs:
            try:
                resume_md, cl_md = self.generate(job)
                
                # Save draft application to DB
                # Tribunal score is 0 initially
                self.db.save_application(
                    job_id=job['job_id'],
                    resume_version=resume_md,
                    cover_letter_version=cl_md,
                    tribunal_score=0.0
                )
                
                self.db.update_application_status(job['job_id'], 'drafted')
                
            except Exception as e:
                logger.error(f"Mirror generation failed for {job['job_id']}: {e}")

        logger.info("Mirror generation cycle complete.")
