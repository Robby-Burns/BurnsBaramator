import logging
import os
import yaml
import time
import schedule
import sentry_sdk
from dotenv import load_dotenv
from db.manager import DatabaseManager
from utils.llm_client import LLMClient
from agents.scout import Scout
from agents.barometer import Barometer
from agents.mirror import Mirror
from agents.tribunal import Tribunal
from agents.gatekeeper import Gatekeeper

# Load environment variables
load_dotenv()

# Initialize Sentry if DSN is present
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("storage/logs/barometer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BurnsBarometer:
    """Orchestrates the entire job application workflow."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.db = DatabaseManager()
        try:
            self.llm = LLMClient(config_path)
            logger.info("LLM Client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Client: {e}")
            sentry_sdk.capture_exception(e)
            self.llm = None
        
        # Initialize agents
        if self.llm:
            self.scout = Scout(self.db, self.llm, self.config)
            self.barometer = Barometer(self.db, self.llm, self.config)
            self.mirror = Mirror(self.db, self.llm)
            self.tribunal = Tribunal(self.db, self.llm, self.config)
        else:
            self.scout = None
            self.barometer = None
            self.mirror = None
            self.tribunal = None
            
        self.gatekeeper = Gatekeeper(self.db)
    
    def _load_config(self, path: str):
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {path}")
            logger.info("Using default configuration")
            return {
                "settings": {
                    "job_title": os.getenv("JOB_TITLE", "Software Engineer"),
                    "industries": os.getenv("INDUSTRIES", "Technology").split(","),
                    "locations": os.getenv("LOCATIONS", "Remote").split(",")
                }
            }

    def run_full_cycle(self):
        """Execute one complete cycle: Scout -> Barometer -> Mirror -> Tribunal -> Gatekeeper."""
        logger.info("=== Burns Barometer Cycle Started ===")
        
        try:
            # 1. Scout
            if self.scout:
                self.scout.run_mission()
            
            # 2. Barometer
            if self.barometer:
                self.barometer.run_analysis_cycle()
                    
            # 3. Mirror
            if self.mirror:
                self.mirror.run_generation_cycle()

            # 4. Tribunal
            if self.tribunal:
                self.tribunal.run_review_cycle(self.mirror)
            
            # 5. Gatekeeper (Interactive - only if running locally)
            # On Cloud, we skip this blocking step.
            if os.getenv("CLOUD_MODE") is None:
                if self.gatekeeper:
                    self.gatekeeper.request_approval()
            else:
                logger.info("Running in CLOUD_MODE: Skipping interactive Gatekeeper.")
                
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            sentry_sdk.capture_exception(e)
        
        logger.info("=== Burns Barometer Cycle Complete ===")
    
    def cleanup(self):
        """Close all connections."""
        self.db.close()

def job():
    """Wrapped job function with full error handling."""
    try:
        logger.info("Starting job execution...")
        barometer = BurnsBarometer()
        barometer.run_full_cycle()
        barometer.cleanup()
        logger.info("Job completed successfully")
    except Exception as e:
        logger.error(f"Critical Job Error: {e}")
        sentry_sdk.capture_exception(e)
        # Don't re-raise - let the scheduler continue

def health_check():
    """Simple health check that runs periodically."""
    logger.info("Health check: Worker is alive")

if __name__ == "__main__":
    # Ensure storage directories exist
    os.makedirs("storage/logs", exist_ok=True)
    
    # Check for CLOUD_MODE (set in Fly.io/Railway env vars)
    is_cloud = os.getenv("CLOUD_MODE", "false").lower() == "true"
    
    if is_cloud:
        logger.info("Starting Scheduler for Cloud Mode (24/7)...")
        logger.info(f"CLOUD_MODE: {os.getenv('CLOUD_MODE')}")
        logger.info(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
        logger.info(f"ANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
        
        # Schedule the job every 6 hours
        schedule.every(6).hours.do(job)
        
        # Schedule health check every 5 minutes
        schedule.every(5).minutes.do(health_check)
        
        # Keep alive loop - run job on first iteration
        first_run = True
        logger.info("Entering keep-alive loop...")
        
        while True:
            try:
                # Run job immediately on startup
                if first_run:
                    logger.info("Running initial job...")
                    job()
                    first_run = False
                
                # Run pending scheduled jobs
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                sentry_sdk.capture_exception(e)
                # Don't crash - keep the loop running
                time.sleep(60)
        
        logger.info("Scheduler stopped")

    else:
        # Local run (Run once and exit)
        logger.info("Starting Local Run...")
        job()
        logger.info("Local Run Complete.")
