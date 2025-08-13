#!/usr/bin/env python3
"""
Update Main Events
Update existing fights with correct main event identification
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def update_main_events():
    """Update existing fights with correct main event identification"""
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        logger.info("🔧 Updating main event identification...")
        
        # Define the correct main events based on the enhanced scraper analysis
        main_event_updates = {
            # UFC 318: Holloway vs. Poirier 3
            'fb44ab8d-8746-4905-bf6c-39d0cf5c6a8b': {
                'main_event': 'Ryan Spann vs Łukasz Brzeski',
                'co_main_event': 'Brunno Ferreira vs Jackson McVey'
            },
            # UFC on ABC: Whittaker vs. de Ridder
            '10834ee1-9414-4098-bf34-e56533d66a73': {
                'main_event': 'Reinier de Ridder vs Robert Whittaker',
                'co_main_event': 'Petr Yan vs Marcus McGhee'
            },
            # UFC on ESPN: Taira vs. Park
            'aa3c04bc-5947-46b3-a450-8180b9874174': {
                'main_event': 'Austin Bashi vs John Yannis',
                'co_main_event': 'Andrey Pulyaev vs Nick Klein'
            },
            # UFC 317: Topuria vs. Oliveira
            'ca38bd5a-efc6-4477-887c-ccbbd4850ee0': {
                'main_event': 'Ilia Topuria vs Charles Oliveira',
                'co_main_event': 'Alexandre Pantoja vs Kai Kara-France'
            },
            # UFC on ESPN: Lewis vs. Teixeira
            '2c3f4409-51e8-44d7-af46-d9bec84bf6a7': {
                'main_event': 'Derrick Lewis vs Tallison Teixeira',
                'co_main_event': 'Gabriel Bonfim vs Stephen Thompson'
            }
        }
        
        for event_id, main_events in main_event_updates.items():
            logger.info(f"\n🎯 Updating event: {event_id}")
            
            # Get all fights for this event
            fights_response = requests.get(
                f"{SUPABASE_URL}/rest/v1/fights",
                headers=headers,
                params={
                    'event_id': f'eq.{event_id}',
                    'select': 'id,winner_name,loser_name,fight_order,is_main_event,is_co_main_event'
                }
            )
            
            if fights_response.status_code == 200:
                fights = fights_response.json()
                logger.info(f"   📊 Found {len(fights)} fights")
                
                # Reset all main event flags
                for fight in fights:
                    fight_id = fight['id']
                    winner = fight.get('winner_name', '')
                    loser = fight.get('loser_name', '')
                    fight_name = f"{winner} vs {loser}"
                    
                    # Check if this is the main event or co-main event
                    is_main_event = fight_name == main_events['main_event']
                    is_co_main_event = fight_name == main_events['co_main_event']
                    
                    if is_main_event or is_co_main_event:
                        logger.info(f"      Setting {fight_name} as {'MAIN EVENT' if is_main_event else 'CO-MAIN EVENT'}")
                        
                        # Update the fight
                        update_response = requests.put(
                            f"{SUPABASE_URL}/rest/v1/fights",
                            headers=headers,
                            params={'id': f'eq.{fight_id}'},
                            json={
                                'is_main_event': is_main_event,
                                'is_co_main_event': is_co_main_event
                            }
                        )
                        
                        if update_response.status_code == 200:
                            logger.info(f"      ✅ Updated fight flags")
                        else:
                            logger.warning(f"      ⚠️ Failed to update fight: {update_response.status_code}")
            else:
                logger.warning(f"   ⚠️ Error getting fights: {fights_response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating main events: {e}")
        return False

if __name__ == "__main__":
    success = update_main_events()
    if success:
        print("✅ Main event updates completed!")
    else:
        print("❌ Main event updates failed!")
        exit(1) 