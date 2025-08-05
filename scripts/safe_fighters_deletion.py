#!/usr/bin/env python3
"""
Safe Fighters Deletion
Safely delete fighters table records while checking foreign key constraints
"""

import os
import sys
import requests
import logging
from dotenv import load_dotenv

load_dotenv('scripts/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def check_foreign_key_constraints():
    """Check if there are any foreign key constraints that would prevent fighter deletion"""
    logger.info("🔍 Checking foreign key constraints...")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Check if fights table has any records that reference fighters
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights?select=id,fighter1_id,fighter2_id&limit=1",
            headers=headers
        )
        if response.status_code == 200:
            fights = response.json()
            if fights:
                logger.warning(f"⚠️ Found {len(fights)} fights that reference fighters")
                return False
            else:
                logger.info("✅ No fights found - safe to delete fighters")
        
        # Check if rankings table has any records that reference fighters
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/rankings?select=id,fighter_id&limit=1",
            headers=headers
        )
        if response.status_code == 200:
            rankings = response.json()
            if rankings:
                logger.warning(f"⚠️ Found {len(rankings)} rankings that reference fighters")
                return False
            else:
                logger.info("✅ No rankings found - safe to delete fighters")
        
        logger.info("✅ All foreign key constraints checked - safe to proceed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking constraints: {str(e)}")
        return False

def delete_all_fighters():
    """Delete all fighters from the database"""
    logger.info("🗑️ Deleting all fighters...")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # First, get the count of fighters
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fighters?select=id",
            headers=headers
        )
        
        if response.status_code == 200:
            fighters = response.json()
            logger.info(f"📊 Found {len(fighters)} fighters to delete")
            
            if len(fighters) == 0:
                logger.info("✅ No fighters to delete")
                return True
        
        # Delete all fighters
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/fighters",
            headers=headers,
            params={'name': 'not.is.null'}  # Delete all fighters
        )
        
        if response.status_code == 200:
            deleted_fighters = response.json()
            logger.info(f"✅ Successfully deleted {len(deleted_fighters)} fighters")
            return True
        else:
            logger.error(f"❌ Error deleting fighters: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during fighter deletion: {str(e)}")
        return False

def verify_fighters_deleted():
    """Verify that all fighters have been deleted"""
    logger.info("🔍 Verifying fighters have been deleted...")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fighters?select=id&limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            fighters = response.json()
            if fighters:
                logger.warning(f"⚠️ Found {len(fighters)} fighters still in database")
                return False
            else:
                logger.info("✅ All fighters successfully deleted!")
                return True
        else:
            logger.error(f"❌ Error checking fighters: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying fighters: {str(e)}")
        return False

def run_safe_fighters_deletion():
    """Run the complete safe fighters deletion process"""
    logger.info("🚀 Starting Safe Fighters Deletion")
    logger.info("=" * 50)
    
    # Step 1: Check foreign key constraints
    logger.info("📋 Step 1: Checking Foreign Key Constraints")
    logger.info("-" * 40)
    if not check_foreign_key_constraints():
        logger.error("❌ Foreign key constraints prevent deletion. Aborting.")
        return
    
    # Step 2: Delete all fighters
    logger.info("📋 Step 2: Deleting All Fighters")
    logger.info("-" * 40)
    if not delete_all_fighters():
        logger.error("❌ Failed to delete fighters. Aborting.")
        return
    
    # Step 3: Verify deletion
    logger.info("📋 Step 3: Verifying Deletion")
    logger.info("-" * 40)
    if not verify_fighters_deleted():
        logger.error("❌ Fighters not fully deleted. Aborting.")
        return
    
    logger.info("🎉 Safe fighters deletion completed successfully!")
    logger.info("=" * 50)

if __name__ == "__main__":
    run_safe_fighters_deletion() 