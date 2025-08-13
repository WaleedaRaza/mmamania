#!/usr/bin/env python3
"""
Apply Schema Changes
Apply the new columns to the fights table using Supabase REST API
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv('.env')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def apply_schema_changes():
    """Apply schema changes to the fights table"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Read the SQL script
        with open('scripts/add_fight_columns.sql', 'r') as f:
            sql_script = f.read()
        
        logger.info("📝 SQL script loaded successfully")
        logger.info(f"📊 Script length: {len(sql_script)} characters")
        
        # Try to execute the SQL using Supabase's rpc endpoint
        logger.info("🚀 Attempting to apply schema changes...")
        
        # Split the SQL into individual statements
        statements = []
        current_statement = ""
        
        for line in sql_script.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_statement += line + " "
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
        
        logger.info(f"📊 Found {len(statements)} SQL statements to execute")
        
        # Execute each statement individually
        successful_statements = 0
        
        for i, statement in enumerate(statements):
            if not statement.strip():
                continue
                
            logger.info(f"🔧 Executing statement {i+1}/{len(statements)}")
            
            try:
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                    headers=headers,
                    json={'query': statement}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Statement {i+1} executed successfully")
                    successful_statements += 1
                else:
                    logger.warning(f"⚠️ Statement {i+1} failed: {response.status_code}")
                    logger.warning(f"⚠️ Response: {response.text}")
                    
            except Exception as e:
                logger.error(f"❌ Error executing statement {i+1}: {e}")
        
        logger.info(f"📊 Schema changes summary:")
        logger.info(f"   ✅ Successful statements: {successful_statements}")
        logger.info(f"   ❌ Failed statements: {len(statements) - successful_statements}")
        
        # Verify the changes by checking if new columns exist
        logger.info("🔍 Verifying schema changes...")
        
        verify_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fights",
            headers=headers,
            params={'select': 'id,winner_name,loser_name,fight_order,is_main_event,is_co_main_event,method,round,time,notes', 'limit': 1}
        )
        
        if verify_response.status_code == 200:
            logger.info("✅ New columns are accessible via REST API")
            return True
        else:
            logger.warning(f"⚠️ Could not verify columns: {verify_response.status_code}")
            logger.warning(f"⚠️ Response: {verify_response.text}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error applying schema changes: {e}")
        return False

if __name__ == "__main__":
    success = apply_schema_changes()
    if success:
        print("✅ Schema changes applied successfully!")
    else:
        print("❌ Schema changes failed!")
        exit(1) 