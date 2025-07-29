import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any
import schedule
import time
import threading

from ..core.database import get_db
from .ufc_scraper_service import UFCScraperService

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scraper_service = UFCScraperService()
        self.is_running = False
        self.scheduler_thread = None
        
    def start_scheduler(self):
        """
        Start the background scheduler
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        
        # Schedule jobs
        schedule.every(6).hours.do(self._update_rankings_job)
        schedule.every(12).hours.do(self._update_fighters_job)
        schedule.every(1).day.do(self._update_all_data_job)
        
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Scheduler started successfully")
    
    def stop_scheduler(self):
        """
        Stop the background scheduler
        """
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """
        Run the scheduler loop
        """
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _update_rankings_job(self):
        """
        Job to update rankings
        """
        try:
            logger.info("Running scheduled rankings update...")
            db = next(get_db())
            asyncio.run(self.scraper_service.update_rankings(db))
            logger.info("Scheduled rankings update completed")
        except Exception as e:
            logger.error(f"Error in scheduled rankings update: {e}")
    
    def _update_fighters_job(self):
        """
        Job to update fighters
        """
        try:
            logger.info("Running scheduled fighters update...")
            db = next(get_db())
            asyncio.run(self.scraper_service.update_fighters(db))
            logger.info("Scheduled fighters update completed")
        except Exception as e:
            logger.error(f"Error in scheduled fighters update: {e}")
    
    def _update_all_data_job(self):
        """
        Job to update all data
        """
        try:
            logger.info("Running scheduled full data update...")
            db = next(get_db())
            results = asyncio.run(self.scraper_service.update_all_data(db))
            logger.info(f"Scheduled full data update completed: {results}")
        except Exception as e:
            logger.error(f"Error in scheduled full data update: {e}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scheduler
        """
        return {
            "is_running": self.is_running,
            "next_rankings_update": schedule.next_run(),
            "next_fighters_update": schedule.next_run(),
            "next_full_update": schedule.next_run(),
            "last_run": datetime.utcnow().isoformat(),
            "jobs": [
                {
                    "name": "rankings_update",
                    "frequency": "6 hours",
                    "next_run": schedule.next_run()
                },
                {
                    "name": "fighters_update", 
                    "frequency": "12 hours",
                    "next_run": schedule.next_run()
                },
                {
                    "name": "full_data_update",
                    "frequency": "24 hours", 
                    "next_run": schedule.next_run()
                }
            ]
        }
    
    def trigger_manual_update(self, update_type: str = "rankings") -> Dict[str, Any]:
        """
        Manually trigger an update
        """
        try:
            logger.info(f"Triggering manual {update_type} update...")
            db = next(get_db())
            
            if update_type == "rankings":
                success = asyncio.run(self.scraper_service.update_rankings(db))
            elif update_type == "fighters":
                success = asyncio.run(self.scraper_service.update_fighters(db))
            elif update_type == "all":
                results = asyncio.run(self.scraper_service.update_all_data(db))
                success = all(results.values())
            else:
                return {"success": False, "error": f"Unknown update type: {update_type}"}
            
            return {
                "success": success,
                "update_type": update_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in manual update: {e}")
            return {
                "success": False,
                "error": str(e),
                "update_type": update_type,
                "timestamp": datetime.utcnow().isoformat()
            }

# Global scheduler instance
scheduler_service = SchedulerService() 