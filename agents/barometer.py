import logging
import yaml
import json
from typing import Dict, Any, List
from db.manager import DatabaseManager
from utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class Barometer:
    """
    The Barometer: Analyzes job listings against the user's Strategic Narrative
    to assign a Fit Score (0-100%).
    """
    
    def __init__(self, db_manager: DatabaseManager, llm_client: LLMClient, config: Dict):
        self.db = db_manager
        self.llm = llm_client
        self.config = config
        self.narrative = self._load_narrative()
        
        # Weights from config
        self.weights = config.get('barometer', {})
        self.min_fit_score = self.weights.get('min_fit_score', 0) # Default 0 means no elimination
        
    def _load_narrative(self) -> Dict:
        """Load the strategic narrative from YAML."""
        try:
            with open("strategic_narrative.yaml", "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error("strategic_narrative.yaml not found!")
            return {}

    def analyze(self, job: Dict) -> float:
        """
        Analyze a single job listing and return a fit score.
        """
        logger.info(f"Analyzing fit for: {job['company']} - {job['role']}")
        
        system_prompt = """
        You are The Barometer, a career strategist agent. 
        Your goal is to analyze a job description against a candidate's strategic narrative and technical competencies.
        
        You must assign a Fit Score from 0 to 100 based on alignment.
        
        Scoring Criteria:
        - 90-100: Perfect match. Role aligns with core narrative, requires candidate's specific unique mix of skills (e.g. Ops + AI).
        - 75-89: Strong match. Most requirements met, good narrative alignment.
        - 60-74: Moderate match. Some gaps, or role is generic.
        - <60: Poor match. Role is irrelevant or requires skills the candidate explicitly lacks.
        
        Output JSON format:
        {
            "score": float,
            "reasoning": "string explanation",
            "matched_narrative": "Name of the best fitting narrative from the list",
            "gaps": ["list of missing skills/requirements"],
            "strengths": ["list of strong matches"]
        }
        """
        
        user_prompt = f"""
        CANDIDATE NARRATIVE:
        {json.dumps(self.narrative, indent=2)}
        
        JOB LISTING:
        Company: {job['company']}
        Role: {job['role']}
        Description: {job['description'][:10000]} 
        
        Analyze the fit.
        """
        
        try:
            analysis = self.llm.generate_structured(system_prompt, user_prompt, {})
            score = float(analysis.get('score', 0))
            
            # Save analysis to notes
            notes = f"Narrative: {analysis.get('matched_narrative')}\n"
            notes += f"Reasoning: {analysis.get('reasoning')}\n"
            notes += f"Strengths: {', '.join(analysis.get('strengths', []))}\n"
            notes += f"Gaps: {', '.join(analysis.get('gaps', []))}"
            
            # Update DB
            self.db.update_fit_score(job['job_id'], score, notes)
            
            return score
            
        except Exception as e:
            logger.error(f"Barometer analysis failed for {job['job_id']}: {e}")
            return 0.0

    def run_analysis_cycle(self):
        """
        Fetch unprocessed jobs and analyze them.
        """
        logger.info("Barometer analysis cycle started.")
        
        # Get jobs that are 'new' (scouted but not analyzed)
        # Note: db.get_recent_unprocessed_listings returns dicts
        jobs = self.db.get_recent_unprocessed_listings(limit=20)
        
        logger.info(f"Found {len(jobs)} jobs to analyze.")
        
        for job in jobs:
            self.analyze(job)
            
        logger.info("Barometer analysis cycle complete.")
