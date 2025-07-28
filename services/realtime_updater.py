#!/usr/bin/env python3
"""
Real-time Data Updater
Orchestrates the complete data pipeline from CSV/JSON to Firestore
"""

import logging
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.firestore_service import FirestoreService
from processors.rankings_processor import RankingsProcessor
from processors.fighters_processor import FightersProcessor
from processors.events_processor import EventsProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealtimeUpdater:
    def __init__(self):
        """Initialize the real-time updater"""
        self.firestore = FirestoreService()
        self.rankings_processor = RankingsProcessor()
        self.fighters_processor = FightersProcessor()
        self.events_processor = EventsProcessor()
        
        # Track upload results
        self.upload_results = {
            'rankings': False,
            'fighters': False,
            'events': False,
            'metadata': False
        }
    
    def run_complete_sync(self) -> bool:
        """Run the complete data sync pipeline"""
        try:
            logger.info("🚀 Starting complete data sync pipeline...")
            
            # Step 1: Run scrapers to get fresh data
            if not self._run_scrapers():
                logger.error("❌ Scrapers failed, aborting sync")
                return False
            
            # Step 2: Process and upload rankings
            if not self._sync_rankings():
                logger.error("❌ Rankings sync failed")
            
            # Step 3: Process and upload fighters
            if not self._sync_fighters():
                logger.error("❌ Fighters sync failed")
            
            # Step 4: Process and upload events
            if not self._sync_events():
                logger.error("❌ Events sync failed")
            
            # Step 5: Update global metadata
            if not self._update_metadata():
                logger.error("❌ Metadata update failed")
            
            # Step 6: Generate sync report
            self._generate_sync_report()
            
            # Check overall success
            success_count = sum(self.upload_results.values())
            total_count = len(self.upload_results)
            
            if success_count == total_count:
                logger.info("🎉 Complete data sync successful!")
                return True
            elif success_count > 0:
                logger.warning(f"⚠️ Partial sync successful ({success_count}/{total_count})")
                return True
            else:
                logger.error("❌ Complete data sync failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in complete sync: {e}")
            return False
    
    def _run_scrapers(self) -> bool:
        """Run all scrapers to get fresh data"""
        try:
            logger.info("🔄 Running scrapers to get fresh data...")
            
            # Run rankings scraper
            logger.info("📊 Running UFC rankings scraper...")
            result1 = subprocess.run([
                "python3", "scrapers/ufc/quick_rankings_scraper.py"
            ], capture_output=True, text=True)
            
            if result1.returncode != 0:
                logger.error(f"❌ Rankings scraper failed: {result1.stderr}")
                return False
            
            # Run fighter profiles scraper
            logger.info("👤 Running fighter profiles scraper...")
            result2 = subprocess.run([
                "python3", "scrapers/ufc/quick_fighter_profile_scraper.py"
            ], capture_output=True, text=True)
            
            if result2.returncode != 0:
                logger.error(f"❌ Fighter profiles scraper failed: {result2.stderr}")
                return False
            
            # Run Wikipedia events scraper
            logger.info("📚 Running Wikipedia events scraper...")
            result3 = subprocess.run([
                "python3", "scrapers/wikipedia/comprehensive_wikipedia_scraper.py"
            ], capture_output=True, text=True)
            
            if result3.returncode != 0:
                logger.error(f"❌ Wikipedia events scraper failed: {result3.stderr}")
                return False
            
            logger.info("✅ All scrapers completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error running scrapers: {e}")
            return False
    
    def _sync_rankings(self) -> bool:
        """Sync rankings data to Firestore"""
        try:
            logger.info("🔄 Syncing rankings data...")
            
            # Process rankings
            rankings = self.rankings_processor.process_rankings_csv()
            
            if not rankings:
                logger.error("❌ No rankings data to sync")
                return False
            
            # Validate rankings
            if not self.rankings_processor.validate_rankings(rankings):
                logger.error("❌ Rankings validation failed")
                return False
            
            # Upload to Firestore
            success = self.firestore.upload_rankings(rankings)
            
            if success:
                logger.info(f"✅ Successfully synced {len(rankings)} rankings")
                self.upload_results['rankings'] = True
                return True
            else:
                logger.error("❌ Failed to upload rankings to Firestore")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing rankings: {e}")
            return False
    
    def _sync_fighters(self) -> bool:
        """Sync fighters data to Firestore"""
        try:
            logger.info("🔄 Syncing fighters data...")
            
            # Process fighters
            fighters = self.fighters_processor.process_fighters_csv()
            
            if not fighters:
                logger.error("❌ No fighters data to sync")
                return False
            
            # Validate fighters
            if not self.fighters_processor.validate_fighters(fighters):
                logger.error("❌ Fighters validation failed")
                return False
            
            # Upload to Firestore
            success = self.firestore.upload_fighters(fighters)
            
            if success:
                logger.info(f"✅ Successfully synced {len(fighters)} fighters")
                self.upload_results['fighters'] = True
                return True
            else:
                logger.error("❌ Failed to upload fighters to Firestore")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing fighters: {e}")
            return False
    
    def _sync_events(self) -> bool:
        """Sync events data to Firestore"""
        try:
            logger.info("🔄 Syncing events data...")
            
            # Process events
            events = self.events_processor.process_events_json()
            
            if not events:
                logger.error("❌ No events data to sync")
                return False
            
            # Validate events
            if not self.events_processor.validate_events(events):
                logger.error("❌ Events validation failed")
                return False
            
            # Filter to recent events (last year)
            recent_events = self.events_processor.filter_recent_events(events, days=365)
            
            # Upload to Firestore
            success = self.firestore.upload_events(recent_events)
            
            if success:
                logger.info(f"✅ Successfully synced {len(recent_events)} events")
                self.upload_results['events'] = True
                return True
            else:
                logger.error("❌ Failed to upload events to Firestore")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing events: {e}")
            return False
    
    def _update_metadata(self) -> bool:
        """Update global metadata"""
        try:
            logger.info("🔄 Updating global metadata...")
            
            # Get data counts from Firestore
            counts = self.firestore.get_data_counts()
            
            # Prepare metadata
            metadata = {
                'total_fighters': counts.get('fighters', 0),
                'total_events': counts.get('events', 0),
                'total_rankings': counts.get('rankings', 0),
                'data_sources': ['UFC.com', 'Wikipedia'],
                'last_sync': datetime.now().isoformat()
            }
            
            # Update metadata
            success = self.firestore.update_metadata(metadata)
            
            if success:
                logger.info("✅ Successfully updated metadata")
                self.upload_results['metadata'] = True
                return True
            else:
                logger.error("❌ Failed to update metadata")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating metadata: {e}")
            return False
    
    def _generate_sync_report(self):
        """Generate a sync report"""
        try:
            logger.info("📊 Generating sync report...")
            
            # Get data counts
            counts = self.firestore.get_data_counts()
            
            # Create report
            report = {
                'sync_timestamp': datetime.now().isoformat(),
                'upload_results': self.upload_results,
                'data_counts': counts,
                'success_rate': f"{sum(self.upload_results.values())}/{len(self.upload_results)}"
            }
            
            # Save report
            report_file = f"sync_reports/sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("sync_reports", exist_ok=True)
            
            import json
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📄 Sync report saved to: {report_file}")
            
            # Log summary
            logger.info("📊 Sync Summary:")
            logger.info(f"  - Rankings: {'✅' if self.upload_results['rankings'] else '❌'}")
            logger.info(f"  - Fighters: {'✅' if self.upload_results['fighters'] else '❌'}")
            logger.info(f"  - Events: {'✅' if self.upload_results['events'] else '❌'}")
            logger.info(f"  - Metadata: {'✅' if self.upload_results['metadata'] else '❌'}")
            logger.info(f"  - Total Rankings: {counts.get('rankings', 0)}")
            logger.info(f"  - Total Fighters: {counts.get('fighters', 0)}")
            logger.info(f"  - Total Events: {counts.get('events', 0)}")
            
        except Exception as e:
            logger.error(f"❌ Error generating sync report: {e}")
    
    def test_connection(self) -> bool:
        """Test Firestore connection"""
        return self.firestore.test_connection()

if __name__ == "__main__":
    # Test the real-time updater
    updater = RealtimeUpdater()
    
    # Test connection
    if updater.test_connection():
        print("✅ Firestore connection successful")
        
        # Run complete sync
        success = updater.run_complete_sync()
        
        if success:
            print("🎉 Complete sync successful!")
        else:
            print("❌ Complete sync failed")
    else:
        print("❌ Firestore connection failed") 