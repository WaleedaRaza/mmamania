import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging

# Add the data directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))

from scrapers.ufc_scraper import UFCScraper
from processors.ufc_data_processor import UFCDataProcessor
from ..models.ranking import Ranking
from ..models.fighter import Fighter

logger = logging.getLogger(__name__)

class UFCScraperService:
    def __init__(self):
        self.scraper = UFCScraper()
        self.processor = UFCDataProcessor()
    
    async def update_rankings(self, db: Session) -> bool:
        """
        Update rankings in the database by scraping and processing UFC data
        """
        try:
            logger.info("Starting rankings update...")
            
            # Scrape raw data
            raw_data = self.scraper.scrape_all_data()
            if not raw_data or not raw_data.get('rankings'):
                logger.error("No rankings data scraped")
                return False
            
            # Process the data
            processed_data = self.processor.process_raw_data(raw_data)
            if not processed_data or not processed_data.get('rankings'):
                logger.error("No rankings data processed")
                return False
            
            # Clear existing rankings
            db.query(Ranking).delete()
            
            # Insert new rankings
            rankings_data = processed_data['rankings']
            for ranking_data in rankings_data:
                ranking = Ranking(
                    division=ranking_data['division'],
                    rank=ranking_data['rank'],
                    fighter_name=ranking_data['fighter_name'],
                    record=ranking_data['record_string'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(ranking)
            
            # Commit changes
            db.commit()
            
            logger.info(f"Successfully updated {len(rankings_data)} rankings")
            return True
            
        except Exception as e:
            logger.error(f"Error updating rankings: {e}")
            db.rollback()
            return False
    
    async def update_fighters(self, db: Session) -> bool:
        """
        Update fighters in the database
        """
        try:
            logger.info("Starting fighters update...")
            
            # Scrape raw data
            raw_data = self.scraper.scrape_all_data()
            if not raw_data or not raw_data.get('fighters'):
                logger.error("No fighters data scraped")
                return False
            
            # Process the data
            processed_data = self.processor.process_raw_data(raw_data)
            if not processed_data or not processed_data.get('fighters'):
                logger.error("No fighters data processed")
                return False
            
            # Clear existing fighters
            db.query(Fighter).delete()
            
            # Insert new fighters
            fighters_data = processed_data['fighters']
            for fighter_data in fighters_data:
                fighter = Fighter(
                    name=fighter_data['name'],
                    record=fighter_data['record_string'],
                    weight_class=fighter_data.get('top_division', ''),
                    ufc_ranking=fighter_data.get('top_rank'),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(fighter)
            
            # Commit changes
            db.commit()
            
            logger.info(f"Successfully updated {len(fighters_data)} fighters")
            return True
            
        except Exception as e:
            logger.error(f"Error updating fighters: {e}")
            db.rollback()
            return False
    
    async def update_all_data(self, db: Session) -> Dict[str, bool]:
        """
        Update all UFC data (rankings, fighters, events, fights)
        """
        results = {}
        
        # Update rankings
        results['rankings'] = await self.update_rankings(db)
        
        # Update fighters
        results['fighters'] = await self.update_fighters(db)
        
        # TODO: Add events and fights updates
        
        return results
    
    def get_scraping_status(self) -> Dict[str, any]:
        """
        Get the status of the scraper and last successful scrape
        """
        try:
            # This would typically check the database for last update times
            # For now, return basic status
            return {
                "scraper_status": "ready",
                "last_successful_scrape": None,
                "scraping_frequency": "6 hours",
                "data_sources": ["UFC Official Website"]
            }
        except Exception as e:
            logger.error(f"Error getting scraping status: {e}")
            return {
                "scraper_status": "error",
                "error": str(e)
            } 