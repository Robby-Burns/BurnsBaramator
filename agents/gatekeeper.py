import logging
import os
import webbrowser
import platform
import subprocess
from typing import Dict, List
from db.manager import DatabaseManager

logger = logging.getLogger(__name__)

class Gatekeeper:
    """
    The Gatekeeper: The final human-in-the-loop approval step.
    Presents reviewed applications to the user for manual submission.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_pending_approvals(self) -> List[Dict]:
        """Fetch applications that have passed the Tribunal review."""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT a.*, l.company, l.role, l.url, l.fit_score
            FROM applications a
            JOIN listings l ON a.job_id = l.job_id
            WHERE a.status = 'reviewed'
            ORDER BY l.fit_score DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def request_approval(self):
        """
        Interactive CLI loop for user approval.
        """
        pending = self.get_pending_approvals()
        
        if not pending:
            print("\n=== Gatekeeper: No pending applications to approve. ===\n")
            return

        print(f"\n=== Gatekeeper: {len(pending)} applications waiting for your approval ===\n")
        
        for app in pending:
            self._process_single_application(app)
            
    def _process_single_application(self, app: Dict):
        """Handle user interaction for a single application."""
        print("-" * 60)
        print(f"ROLE:    {app['role']}")
        print(f"COMPANY: {app['company']}")
        print(f"FIT:     {app['fit_score']}/100")
        print(f"SCORE:   {app['tribunal_final_score']}/100 (Tribunal)")
        print("-" * 60)
        
        while True:
            choice = input("\n[O]pen files & URL | [S]ubmitted | [R]eject | [S]kip > ").lower().strip()
            
            if choice == 'o':
                self._open_resources(app)
            elif choice == 's': # Submitted (Mark as done)
                self.db.mark_application_submitted(app['application_id'])
                self.db.update_application_status(app['job_id'], 'submitted')
                print(f"✓ Marked {app['company']} as SUBMITTED.")
                break
            elif choice == 'r': # Reject
                self.db.update_application_status(app['job_id'], 'user_rejected')
                print(f"✗ Rejected application for {app['company']}.")
                break
            elif choice == 'skip' or choice == 'n': # Skip for now
                print("Skipping...")
                break
            else:
                print("Invalid option.")

    def _open_resources(self, app: Dict):
        """Open the job URL and the folder containing generated files."""
        # Open Job URL
        print(f"Opening Job URL: {app['url']}")
        webbrowser.open(app['url'])
        
        # Open Folder (Cross-platform)
        # We need to find where the files are. 
        # They are in storage/resumes and storage/cover_letters
        # But we don't store the exact filename in DB (oops, we stored the content).
        # We need to reconstruct the filename or search for it.
        # In Mirror.generate, we used: f"{safe_company}_{job['job_id']}_{timestamp}"
        # But we didn't save the filename to DB.
        # Workaround: Search for files containing the job_id in the filename.
        
        resume_file = self._find_file("storage/resumes", app['job_id'])
        cl_file = self._find_file("storage/cover_letters", app['job_id'])
        
        if resume_file:
            self._open_file(resume_file)
        else:
            print("Warning: Resume file not found.")
            
        if cl_file:
            self._open_file(cl_file)
        else:
            print("Warning: Cover Letter file not found.")

    def _find_file(self, directory: str, job_id: str) -> str:
        """Find a file in directory containing job_id."""
        try:
            for f in os.listdir(directory):
                if job_id in f:
                    return os.path.join(directory, f)
        except FileNotFoundError:
            return None
        return None

    def _open_file(self, filepath: str):
        """Open a file with the default system application."""
        print(f"Opening file: {filepath}")
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))
