#!/usr/bin/env python3
"""
Firestore Data Scheduler
Automated scheduler for real-time data updates to Firestore
"""

import schedule
import time
import logging
import sys
import os
from datetime import datetime
import subprocess

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.realtime_updater import RealtimeUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/firestore_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FirestoreScheduler:
    def __init__(self):
        """Initialize the scheduler"""
        self.updater = RealtimeUpdater()
        self.is_running = False
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
    
    def start_scheduler(self):
        """Start the automated scheduler"""
        try:
            logger.info("🚀 Starting Firestore Data Scheduler...")
            
            # Test connection first
            if not self.updater.test_connection():
                logger.error("❌ Firestore connection failed, cannot start scheduler")
                return False
            
            # Schedule jobs
            self._schedule_jobs()
            
            self.is_running = True
            logger.info("✅ Scheduler started successfully")
            
            # Run initial sync
            logger.info("🔄 Running initial sync...")
            self._run_sync_job()
            
            # Keep scheduler running
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            self.stop_scheduler()
            return True
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")
            return False
    
    def _schedule_jobs(self):
        """Schedule all jobs"""
        try:
            # Daily sync at 6 AM
            schedule.every().day.at("06:00").do(self._run_sync_job)
            logger.info("📅 Scheduled daily sync at 6:00 AM")
            
            # Weekly full sync on Sundays at 2 AM
            schedule.every().sunday.at("02:00").do(self._run_full_sync_job)
            logger.info("📅 Scheduled weekly full sync on Sundays at 2:00 AM")
            
            # Test sync every 4 hours (for development)
            schedule.every(4).hours.do(self._run_test_sync_job)
            logger.info("📅 Scheduled test sync every 4 hours")
            
        except Exception as e:
            logger.error(f"❌ Error scheduling jobs: {e}")
    
    def _run_sync_job(self):
        """Run the standard sync job"""
        try:
            logger.info("🔄 Starting scheduled sync job...")
            
            start_time = datetime.now()
            
            # Run the sync
            success = self.updater.run_complete_sync()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if success:
                logger.info(f"✅ Scheduled sync completed successfully in {duration:.2f} seconds")
            else:
                logger.error(f"❌ Scheduled sync failed after {duration:.2f} seconds")
            
            # Log job completion
            self._log_job_completion("sync", success, duration)
            
        except Exception as e:
            logger.error(f"❌ Error in sync job: {e}")
            self._log_job_completion("sync", False, 0, str(e))
    
    def _run_full_sync_job(self):
        """Run the full sync job with additional processing"""
        try:
            logger.info("🔄 Starting scheduled full sync job...")
            
            start_time = datetime.now()
            
            # Run the sync
            success = self.updater.run_complete_sync()
            
            # Additional full sync tasks
            if success:
                self._run_cleanup_tasks()
                self._run_analytics_tasks()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if success:
                logger.info(f"✅ Full sync completed successfully in {duration:.2f} seconds")
            else:
                logger.error(f"❌ Full sync failed after {duration:.2f} seconds")
            
            # Log job completion
            self._log_job_completion("full_sync", success, duration)
            
        except Exception as e:
            logger.error(f"❌ Error in full sync job: {e}")
            self._log_job_completion("full_sync", False, 0, str(e))
    
    def _run_test_sync_job(self):
        """Run a test sync job (for development)"""
        try:
            logger.info("🔄 Starting test sync job...")
            
            start_time = datetime.now()
            
            # Run the sync
            success = self.updater.run_complete_sync()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if success:
                logger.info(f"✅ Test sync completed successfully in {duration:.2f} seconds")
            else:
                logger.error(f"❌ Test sync failed after {duration:.2f} seconds")
            
            # Log job completion
            self._log_job_completion("test_sync", success, duration)
            
        except Exception as e:
            logger.error(f"❌ Error in test sync job: {e}")
            self._log_job_completion("test_sync", False, 0, str(e))
    
    def _run_cleanup_tasks(self):
        """Run cleanup tasks during full sync"""
        try:
            logger.info("🧹 Running cleanup tasks...")
            
            # Clean up old sync reports (keep last 30 days)
            self._cleanup_old_reports()
            
            # Clean up old log files (keep last 7 days)
            self._cleanup_old_logs()
            
            logger.info("✅ Cleanup tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Error in cleanup tasks: {e}")
    
    def _run_analytics_tasks(self):
        """Run analytics tasks during full sync"""
        try:
            logger.info("📊 Running analytics tasks...")
            
            # Generate analytics reports
            self._generate_analytics_report()
            
            logger.info("✅ Analytics tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Error in analytics tasks: {e}")
    
    def _cleanup_old_reports(self):
        """Clean up old sync reports"""
        try:
            import glob
            from datetime import datetime, timedelta
            
            # Keep reports from last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            report_files = glob.glob("sync_reports/sync_report_*.json")
            
            for report_file in report_files:
                try:
                    # Extract date from filename
                    filename = os.path.basename(report_file)
                    date_str = filename.replace("sync_report_", "").replace(".json", "")
                    file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    
                    if file_date < cutoff_date:
                        os.remove(report_file)
                        logger.info(f"🗑️ Removed old report: {report_file}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not process report file {report_file}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up old reports: {e}")
    
    def _cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            import glob
            from datetime import datetime, timedelta
            
            # Keep logs from last 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            
            log_files = glob.glob("logs/*.log")
            
            for log_file in log_files:
                try:
                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                    
                    if file_mtime < cutoff_date:
                        os.remove(log_file)
                        logger.info(f"🗑️ Removed old log: {log_file}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not process log file {log_file}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up old logs: {e}")
    
    def _generate_analytics_report(self):
        """Generate analytics report"""
        try:
            # Get data counts
            counts = self.updater.firestore.get_data_counts()
            
            # Create analytics report
            analytics = {
                'timestamp': datetime.now().isoformat(),
                'data_counts': counts,
                'data_health': self._assess_data_health(counts),
                'recommendations': self._generate_recommendations(counts)
            }
            
            # Save analytics report
            analytics_file = f"analytics/data_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("analytics", exist_ok=True)
            
            import json
            with open(analytics_file, 'w') as f:
                json.dump(analytics, f, indent=2)
            
            logger.info(f"📊 Analytics report saved to: {analytics_file}")
            
        except Exception as e:
            logger.error(f"❌ Error generating analytics report: {e}")
    
    def _assess_data_health(self, counts: dict) -> dict:
        """Assess the health of the data"""
        try:
            health = {
                'overall_score': 0,
                'rankings_health': 0,
                'fighters_health': 0,
                'events_health': 0,
                'issues': []
            }
            
            # Assess rankings health
            rankings_count = counts.get('rankings', 0)
            if rankings_count >= 150:
                health['rankings_health'] = 100
            elif rankings_count >= 100:
                health['rankings_health'] = 75
            elif rankings_count >= 50:
                health['rankings_health'] = 50
            else:
                health['rankings_health'] = 25
                health['issues'].append("Low rankings count")
            
            # Assess fighters health
            fighters_count = counts.get('fighters', 0)
            if fighters_count >= 150:
                health['fighters_health'] = 100
            elif fighters_count >= 100:
                health['fighters_health'] = 75
            elif fighters_count >= 50:
                health['fighters_health'] = 50
            else:
                health['fighters_health'] = 25
                health['issues'].append("Low fighters count")
            
            # Assess events health
            events_count = counts.get('events', 0)
            if events_count >= 10:
                health['events_health'] = 100
            elif events_count >= 5:
                health['events_health'] = 75
            elif events_count >= 2:
                health['events_health'] = 50
            else:
                health['events_health'] = 25
                health['issues'].append("Low events count")
            
            # Calculate overall score
            health['overall_score'] = (
                health['rankings_health'] + 
                health['fighters_health'] + 
                health['events_health']
            ) // 3
            
            return health
            
        except Exception as e:
            logger.error(f"❌ Error assessing data health: {e}")
            return {'overall_score': 0, 'issues': [str(e)]}
    
    def _generate_recommendations(self, counts: dict) -> list:
        """Generate recommendations based on data counts"""
        try:
            recommendations = []
            
            rankings_count = counts.get('rankings', 0)
            fighters_count = counts.get('fighters', 0)
            events_count = counts.get('events', 0)
            
            if rankings_count < 150:
                recommendations.append("Increase rankings scraping frequency")
            
            if fighters_count < 150:
                recommendations.append("Increase fighter profiles scraping frequency")
            
            if events_count < 10:
                recommendations.append("Expand Wikipedia events scraping to more events")
            
            if not recommendations:
                recommendations.append("Data health is good, maintain current scraping schedule")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def _log_job_completion(self, job_type: str, success: bool, duration: float, error: str = None):
        """Log job completion details"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'job_type': job_type,
                'success': success,
                'duration_seconds': duration,
                'error': error
            }
            
            # Save to job log
            job_log_file = "logs/job_completions.json"
            
            import json
            try:
                with open(job_log_file, 'r') as f:
                    job_log = json.load(f)
            except FileNotFoundError:
                job_log = []
            
            job_log.append(log_entry)
            
            # Keep only last 100 entries
            if len(job_log) > 100:
                job_log = job_log[-100:]
            
            with open(job_log_file, 'w') as f:
                json.dump(job_log, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error logging job completion: {e}")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        try:
            self.is_running = False
            logger.info("🛑 Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
    
    def get_schedule_info(self) -> dict:
        """Get information about scheduled jobs"""
        try:
            jobs = schedule.get_jobs()
            
            schedule_info = {
                'total_jobs': len(jobs),
                'jobs': []
            }
            
            for job in jobs:
                schedule_info['jobs'].append({
                    'job': str(job.job_func),
                    'next_run': str(job.next_run),
                    'interval': str(job.interval)
                })
            
            return schedule_info
            
        except Exception as e:
            logger.error(f"❌ Error getting schedule info: {e}")
            return {'total_jobs': 0, 'jobs': []}

if __name__ == "__main__":
    # Create and start the scheduler
    scheduler = FirestoreScheduler()
    
    print("🚀 Starting Firestore Data Scheduler...")
    print("📅 Scheduled jobs:")
    print("  - Daily sync at 6:00 AM")
    print("  - Weekly full sync on Sundays at 2:00 AM")
    print("  - Test sync every 4 hours")
    print("🛑 Press Ctrl+C to stop")
    
    # Start the scheduler
    scheduler.start_scheduler() 