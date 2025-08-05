#!/usr/bin/env python3
"""
Populate Rankings Fixed
Populate the scraped rankings back into the database with correct data structure
"""

import os
import sys
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv('scripts/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def load_rankings_data():
    """Load the scraped rankings data"""
    try:
        with open('data/real_dynamic_rankings.json', 'r') as f:
            data = json.load(f)
        
        rankings = data.get('rankings', [])
        logger.info(f"📊 Loaded {len(rankings)} rankings from file")
        return rankings
    except Exception as e:
        logger.error(f"❌ Error loading rankings: {str(e)}")
        return []

def get_or_create_fighter(fighter_name):
    """Get or create a fighter in the database"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        
        # First, try to get existing fighter
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            existing_fighters = response.json()
            if existing_fighters:
                return existing_fighters[0]['id']
        
        # Create new fighter
        fighter_data = {
            'name': fighter_name,
            'weight_class': None,
            'record': None,
            'ufc_ranking': None
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/fighters",
            headers=headers,
            json=fighter_data
        )
        
        if response.status_code == 201:
            # Handle empty response body
            try:
                return response.json()['id']
            except (ValueError, KeyError):
                # If response is empty, try to get the fighter by name
                fetch_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/fighters?name=eq.{fighter_name}",
                    headers=headers
                )
                if fetch_response.status_code == 200:
                    fighters = fetch_response.json()
                    if fighters:
                        return fighters[0]['id']
                return None
        else:
            return None
            
    except Exception as e:
        return None

def create_ranking(ranking_data):
    """Create a ranking in the database"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Get or create fighter
        fighter_id = get_or_create_fighter(ranking_data['name'])
        if not fighter_id:
            logger.warning(f"⚠️ Could not get/create fighter: {ranking_data['name']}")
            return None
        
        # Determine rank type
        rank_type = "champion" if ranking_data.get('isChampion', False) else "contender"
        
        # Create ranking
        ranking_to_create = {
            'fighter_id': fighter_id,
            'weight_class': ranking_data['weight_class'],
            'rank_position': ranking_data['rank_position'],
            'rank_type': rank_type
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rankings",
            headers=headers,
            json=ranking_to_create
        )
        
        if response.status_code == 201:
            # Handle empty response body
            try:
                return response.json()['id']
            except (ValueError, KeyError):
                # If response is empty, try to get the ranking by fighter and division
                fetch_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/rankings?fighter_id=eq.{fighter_id}&weight_class=eq.{ranking_data['weight_class']}",
                    headers=headers
                )
                if fetch_response.status_code == 200:
                    rankings = fetch_response.json()
                    if rankings:
                        return rankings[0]['id']
                return None
        else:
            return None
            
    except Exception as e:
        return None

def populate_rankings():
    """Populate all rankings into the database"""
    logger.info("🚀 Starting Rankings Population")
    logger.info("=" * 50)
    
    # Load rankings data
    rankings = load_rankings_data()
    if not rankings:
        logger.error("❌ No rankings data found")
        return
    
    # Populate rankings
    created_count = 0
    failed_count = 0
    
    for ranking in rankings:
        try:
            ranking_id = create_ranking(ranking)
            if ranking_id:
                created_count += 1
                rank_type = "👑 CHAMPION" if ranking.get('isChampion', False) else f"#{ranking['rank_position']}"
                logger.info(f"✅ Created ranking: {ranking['name']} - {ranking['weight_class']} {rank_type}")
            else:
                failed_count += 1
                logger.warning(f"❌ Failed to create ranking: {ranking['name']}")
        except Exception as e:
            failed_count += 1
            logger.error(f"❌ Error creating ranking: {str(e)}")
    
    logger.info(f"🎉 Rankings population completed!")
    logger.info(f"✅ Created: {created_count}")
    logger.info(f"❌ Failed: {failed_count}")
    logger.info("=" * 50)

if __name__ == "__main__":
    populate_rankings() 