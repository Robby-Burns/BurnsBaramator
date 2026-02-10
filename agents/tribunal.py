import logging
import json
from typing import Dict, Tuple, List
from db.manager import DatabaseManager
from utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class Tribunal:
    """
    The Tribunal: A multi-persona review system that critiques application materials.
    If the score is below threshold, it provides feedback for refinement.
    """
    
    def __init__(self, db_manager: DatabaseManager, llm_client: LLMClient, config: Dict):
        self.db = db_manager
        self.llm = llm_client
        self.config = config
        self.personas = config.get('tribunal', {}).get('personas', ["ATS Specialist", "Recruiter", "Hiring Manager"])
        self.min_score = config.get('tribunal', {}).get('min_approval_score', 90)

    def review(self, job: Dict, resume_md: str, cl_md: str) -> Tuple[float, str]:
        """
        Conduct a multi-persona review of the application materials.
        Returns: (final_score, aggregated_feedback)
        """
        logger.info(f"Tribunal convening for: {job['company']} - {job['role']}")
        
        scores = []
        feedbacks = []
        
        for persona in self.personas:
            score, feedback = self._conduct_review(persona, job, resume_md, cl_md)
            scores.append(score)
            feedbacks.append(f"**{persona}**: {feedback}")
            
        final_score = sum(scores) / len(scores)
        aggregated_feedback = "\n\n".join(feedbacks)
        
        logger.info(f"Tribunal verdict: {final_score}/100")
        return final_score, aggregated_feedback

    def _conduct_review(self, persona: str, job: Dict, resume_md: str, cl_md: str) -> Tuple[float, str]:
        """Ask a specific persona to review the materials."""
        
        system_prompt = f"""
        You are a {persona} reviewing a job application.
        
        Your Goal: Critique the Resume and Cover Letter against the Job Description.
        
        Scoring Criteria (0-100):
        - <70: Reject. Major gaps, typos, or irrelevance.
        - 70-89: Good. Solid match, but could be sharper.
        - 90-100: Excellent. Perfect tailoring, compelling narrative, clear impact.
        
        Output JSON format:
        {{
            "score": float,
            "feedback": "Specific, actionable feedback for improvement."
        }}
        """
        
        user_prompt = f"""
        JOB DESCRIPTION:
        Company: {job['company']}
        Role: {job['role']}
        Description: {job['description'][:5000]}
        
        RESUME:
        {resume_md[:5000]}
        
        COVER LETTER:
        {cl_md[:3000]}
        
        Review as a {persona}.
        """
        
        try:
            review = self.llm.generate_structured(system_prompt, user_prompt, {})
            return float(review.get('score', 0)), review.get('feedback', 'No feedback provided.')
        except Exception as e:
            logger.error(f"Tribunal review failed for {persona}: {e}")
            return 0.0, "Error during review."

    def run_review_cycle(self, mirror_agent):
        """
        Fetch drafted applications, review them, and refine if necessary.
        """
        logger.info("Tribunal review cycle started.")
        
        # Get applications in 'drafted' status
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT a.*, l.company, l.role, l.description 
            FROM applications a
            JOIN listings l ON a.job_id = l.job_id
            WHERE a.status = 'drafted'
        """)
        
        applications = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Found {len(applications)} drafts to review.")
        
        for app in applications:
            resume_md = app['resume_version']
            cl_md = app['cover_letter_version']
            job = {
                'job_id': app['job_id'],
                'company': app['company'],
                'role': app['role'],
                'description': app['description']
            }
            
            # Initial Review
            score, feedback = self.review(job, resume_md, cl_md)
            
            # Refinement Loop (max 2 iterations to save tokens/time)
            iteration = 0
            while score < self.min_score and iteration < 2:
                logger.info(f"Score {score} < {self.min_score}. Requesting refinement (Iteration {iteration+1})...")
                
                # Ask Mirror to refine based on feedback
                # We need to extend Mirror to support refinement
                # For now, we'll just re-generate with feedback injected into prompt
                # But Mirror.generate doesn't take feedback. 
                # Let's add a _refine method to Mirror or just pass it here if we modify Mirror.
                
                # Since we can't easily modify Mirror in this step without context switching,
                # let's assume we can call a refine method. If not, we'll skip refinement for this MVP step.
                # Ideally, we'd update Mirror.py to have a refine() method.
                
                # Let's try to use the LLM directly here to refine, or update Mirror.
                # Updating Mirror is cleaner. I will assume Mirror has a refine method or I will add it.
                # For this specific file write, I can't edit Mirror.py.
                # So I will implement a local refinement helper here using the LLM.
                
                resume_md, cl_md = self._refine_materials(job, resume_md, cl_md, feedback)
                score, feedback = self.review(job, resume_md, cl_md)
                iteration += 1
            
            # Save final result
            cursor.execute("""
                UPDATE applications 
                SET status = 'reviewed', 
                    tribunal_final_score = ?, 
                    feedback = ?,
                    resume_version = ?,
                    cover_letter_version = ?
                WHERE application_id = ?
            """, (score, feedback, resume_md, cl_md, app['application_id']))
            self.db.conn.commit()
            
            logger.info(f"Application {app['application_id']} reviewed. Final Score: {score}")

        logger.info("Tribunal review cycle complete.")

    def _refine_materials(self, job: Dict, resume_md: str, cl_md: str, feedback: str) -> Tuple[str, str]:
        """Refine materials based on feedback."""
        system_prompt = """
        You are an expert editor. Improve the Resume and Cover Letter based on the feedback provided.
        Return the updated Resume and Cover Letter in Markdown format.
        Separate them with '---SPLIT---'.
        """
        
        user_prompt = f"""
        JOB: {job['company']} - {job['role']}
        
        FEEDBACK:
        {feedback}
        
        CURRENT RESUME:
        {resume_md}
        
        CURRENT COVER LETTER:
        {cl_md}
        
        Refine both documents.
        """
        
        response = self.llm.generate(system_prompt, user_prompt)
        
        try:
            parts = response.split('---SPLIT---')
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
            else:
                return resume_md, cl_md # Fallback if split fails
        except:
            return resume_md, cl_md
