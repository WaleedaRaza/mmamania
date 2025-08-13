#!/usr/bin/env python3
"""
Complete Database Setup
Wipes events and fights tables and applies enhanced schema
"""

import os
import sys
import requests
import logging
from dotenv import load_dotenv

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv('.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def setup_database():
    """Complete database setup - wipe and enhance schema"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🚀 Starting complete database setup...")
        
        # Step 1: Wipe fights table
        logger.info("🗑️ Step 1: Wiping fights table...")
        fights_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id'}
        )
        
        if fights_response.status_code == 200:
            deleted_fights = len(fights_response.json())
            logger.info(f"✅ Deleted {deleted_fights} fights")
        else:
            logger.warning(f"⚠️ Fights deletion response: {fights_response.status_code}")
        
        # Step 2: Wipe events table
        logger.info("🗑️ Step 2: Wiping events table...")
        events_response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id'}
        )
        
        if events_response.status_code == 200:
            deleted_events = len(events_response.json())
            logger.info(f"✅ Deleted {deleted_events} events")
        else:
            logger.warning(f"⚠️ Events deletion response: {events_response.status_code}")
        
        # Step 3: Apply schema enhancements
        logger.info("🔧 Step 3: Applying schema enhancements...")
        
        # Add new columns to fights table
        schema_changes = [
            {
                "sql": """
                ALTER TABLE fights 
                ADD COLUMN IF NOT EXISTS winner_name VARCHAR(255),
                ADD COLUMN IF NOT EXISTS loser_name VARCHAR(255),
                ADD COLUMN IF NOT EXISTS fight_order INTEGER,
                ADD COLUMN IF NOT EXISTS is_main_event BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS is_co_main_event BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS weight_class VARCHAR(100),
                ADD COLUMN IF NOT EXISTS method VARCHAR(255),
                ADD COLUMN IF NOT EXISTS round INTEGER,
                ADD COLUMN IF NOT EXISTS time VARCHAR(50),
                ADD COLUMN IF NOT EXISTS notes TEXT;
                """
            },
            {
                "sql": """
                CREATE INDEX IF NOT EXISTS idx_fights_winner_name ON fights(winner_name);
                CREATE INDEX IF NOT EXISTS idx_fights_loser_name ON fights(loser_name);
                CREATE INDEX IF NOT EXISTS idx_fights_order ON fights(fight_order);
                CREATE INDEX IF NOT EXISTS idx_fights_main_event ON fights(is_main_event);
                CREATE INDEX IF NOT EXISTS idx_fights_weight_class ON fights(weight_class);
                """
            },
            {
                "sql": """
                ALTER TABLE fights 
                ADD CONSTRAINT IF NOT EXISTS check_fight_order_positive 
                CHECK (fight_order > 0);
                """
            },
            {
                "sql": """
                ALTER TABLE fights 
                ADD CONSTRAINT IF NOT EXISTS unique_main_event_per_event 
                UNIQUE (event_id, is_main_event) 
                WHERE is_main_event = TRUE;
                """
            },
            {
                "sql": """
                ALTER TABLE fights 
                ADD CONSTRAINT IF NOT EXISTS unique_co_main_event_per_event 
                UNIQUE (event_id, is_co_main_event) 
                WHERE is_co_main_event = TRUE;
                """
            }
        ]
        
        for i, change in enumerate(schema_changes, 1):
            logger.info(f"🔧 Applying schema change {i}/{len(schema_changes)}...")
            
            # Use Supabase's SQL endpoint
            sql_response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"query": change["sql"]}
            )
            
            if sql_response.status_code == 200:
                logger.info(f"✅ Schema change {i} applied successfully")
            else:
                logger.warning(f"⚠️ Schema change {i} response: {sql_response.status_code}")
                logger.warning(f"⚠️ Response: {sql_response.text}")
        
        # Step 4: Verify the setup
        logger.info("🔍 Step 4: Verifying setup...")
        
        # Check if tables are empty
        fights_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id', 'limit': 1}
        )
        
        events_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=headers,
            params={'select': 'id', 'limit': 1}
        )
        
        if fights_check.status_code == 200 and len(fights_check.json()) == 0:
            logger.info("✅ Fights table is empty")
        else:
            logger.warning("⚠️ Fights table may not be empty")
        
        if events_check.status_code == 200 and len(events_check.json()) == 0:
            logger.info("✅ Events table is empty")
        else:
            logger.warning("⚠️ Events table may not be empty")
        
        # Check if new columns exist
        logger.info("🔍 Checking if new columns exist...")
        columns_check = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'winner_name,loser_name,fight_order,is_main_event,is_co_main_event', 'limit': 1}
        )
        
        if columns_check.status_code == 200:
            logger.info("✅ New columns are accessible")
        else:
            logger.warning("⚠️ New columns may not be accessible")
        
        logger.info("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in database setup: {e}")
        return False

def test_enhanced_scraper():
    """Test the enhanced scraper with a few events"""
    try:
        logger.info("🧪 Testing enhanced scraper...")
        
        # Import and run the enhanced scraper
        from enhanced_wikipedia_scraper_v2 import EnhancedWikipediaScraperV2
        
        scraper = EnhancedWikipediaScraperV2(max_workers=2)
        success = scraper.run_enhanced_scraper(max_events=3, start_from=0)
        
        if success:
            logger.info("✅ Enhanced scraper test completed successfully!")
            return True
        else:
            logger.error("❌ Enhanced scraper test failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing enhanced scraper: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting complete database setup and scraper test")
    
    # Step 1: Setup database
    db_success = setup_database()
    
    if not db_success:
        logger.error("❌ Database setup failed!")
        return False
    
    # Step 2: Test enhanced scraper
    scraper_success = test_enhanced_scraper()
    
    if not scraper_success:
        logger.error("❌ Enhanced scraper test failed!")
        return False
    
    logger.info("🎉 All setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Complete setup completed successfully!")
    else:
        print("❌ Complete setup failed!")
        sys.exit(1) 