import logging
import os
import yaml
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
        
        # 1. Scout
        if self.scout:
            try:
                self.scout.run_mission()
            except Exception as e:
                logger.error(f"Scout mission failed: {e}")
        
        # 2. Barometer
        if self.barometer:
            try:
                self.barometer.run_analysis_cycle()
            except Exception as e:
                logger.error(f"Barometer cycle failed: {e}")
                
        # 3. Mirror
        if self.mirror:
            try:
                self.mirror.run_generation_cycle()
            except Exception as e:
                logger.error(f"Mirror cycle failed: {e}")

        # 4. Tribunal
        if self.tribunal:
            try:
                self.tribunal.run_review_cycle(self.mirror)
            except Exception as e:
                logger.error(f"Tribunal cycle failed: {e}")
        
        # 5. Gatekeeper (Interactive)
        if self.gatekeeper:
            try:
                self.gatekeeper.request_approval()
            except Exception as e:
                logger.error(f"Gatekeeper session failed: {e}")
        
        logger.info("=== Burns Barometer Cycle Complete ===")
    
    def cleanup(self):
        """Close all connections."""
        self.db.close()

if __name__ == "__main__":
    # Ensure storage directories exist
    os.makedirs("storage/logs", exist_ok=True)
    
    barometer = BurnsBarometer()
    barometer.run_full_cycle()
    barometer.cleanup()
