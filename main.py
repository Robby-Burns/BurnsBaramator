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
        with open(path, 'r') as f:
            return yaml.safe_load(f)

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
    barometer = BurnsBarometer()
    barometer.run_full_cycle()
    barometer.cleanup()

if __name__ == "__main__":
    # Ensure storage directories exist
    os.makedirs("storage/logs", exist_ok=True)
    
    # If running on Cloud (Koyeb/Railway/Fly), use scheduler
    if os.getenv("CLOUD_MODE"):
        logger.info("Starting Scheduler for Cloud Mode...")
        # Run once immediately
        job()
        # Then schedule every 6 hours
        schedule.every(6).hours.do(job)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # Local run
        job()
