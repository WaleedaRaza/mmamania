#!/usr/bin/env python3
"""
Test script to populate events and fights with winner/loser data
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

class TestWinnerDisplay:
    def __init__(self):
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
    
    def create_test_events_and_fights(self):
        """Create test events and fights with winner/loser data"""
        logger.info("🚀 Creating test events and fights with winner/loser data")
        
        # Test event 1
        event1_data = {
            'name': 'UFC 300: Test Event',
            'date': '2024-04-13',
            'venue': 'T-Mobile Arena',
            'location': 'Las Vegas, Nevada'
        }
        
        event1_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=self.supabase_headers,
            json=event1_data
        )
        
        if event1_response.status_code == 201:
            event1_id = event1_response.json()['id']
            logger.info(f"✅ Created event: {event1_data['name']} (ID: {event1_id})")
            
            # Create fights for event 1
            fights1 = [
                {
                    'event_id': event1_id,
                    'fighter1_name': 'Alex Pereira',
                    'fighter2_name': 'Jamahal Hill',
                    'weight_class': 'Light Heavyweight',
                    'status': 'completed',
                    'result': {
                        'winner_name': 'Alex Pereira',
                        'method': 'KO/TKO',
                        'round': '1',
                        'time': '3:14'
                    }
                },
                {
                    'event_id': event1_id,
                    'fighter1_name': 'Zhang Weili',
                    'fighter2_name': 'Yan Xiaonan',
                    'weight_class': 'Strawweight',
                    'status': 'completed',
                    'result': {
                        'winner_name': 'Zhang Weili',
                        'method': 'Decision (unanimous)',
                        'round': '5',
                        'time': '5:00'
                    }
                },
                {
                    'event_id': event1_id,
                    'fighter1_name': 'Justin Gaethje',
                    'fighter2_name': 'Max Holloway',
                    'weight_class': 'Lightweight',
                    'status': 'completed',
                    'result': {
                        'winner_name': 'Max Holloway',
                        'method': 'KO/TKO',
                        'round': '5',
                        'time': '4:59'
                    }
                }
            ]
            
            for fight in fights1:
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=self.supabase_headers,
                    json=fight
                )
                if response.status_code == 201:
                    logger.info(f"✅ Created fight: {fight['fighter1_name']} vs {fight['fighter2_name']}")
                else:
                    logger.error(f"❌ Failed to create fight: {response.status_code} - {response.text}")
        
        # Test event 2
        event2_data = {
            'name': 'UFC 301: Test Event 2',
            'date': '2024-05-04',
            'venue': 'Jeunesse Arena',
            'location': 'Rio de Janeiro, Brazil'
        }
        
        event2_response = requests.post(
            f"{SUPABASE_URL}/rest/v1/events",
            headers=self.supabase_headers,
            json=event2_data
        )
        
        if event2_response.status_code == 201:
            event2_id = event2_response.json()['id']
            logger.info(f"✅ Created event: {event2_data['name']} (ID: {event2_id})")
            
            # Create fights for event 2
            fights2 = [
                {
                    'event_id': event2_id,
                    'fighter1_name': 'Steve Erceg',
                    'fighter2_name': 'Alexandre Pantoja',
                    'weight_class': 'Flyweight',
                    'status': 'completed',
                    'result': {
                        'winner_name': 'Alexandre Pantoja',
                        'method': 'Decision (unanimous)',
                        'round': '5',
                        'time': '5:00'
                    }
                },
                {
                    'event_id': event2_id,
                    'fighter1_name': 'Michel Pereira',
                    'fighter2_name': 'Ihor Potieria',
                    'weight_class': 'Light Heavyweight',
                    'status': 'completed',
                    'result': {
                        'winner_name': 'Michel Pereira',
                        'method': 'Submission',
                        'round': '1',
                        'time': '0:54'
                    }
                }
            ]
            
            for fight in fights2:
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/fights",
                    headers=self.supabase_headers,
                    json=fight
                )
                if response.status_code == 201:
                    logger.info(f"✅ Created fight: {fight['fighter1_name']} vs {fight['fighter2_name']}")
                else:
                    logger.error(f"❌ Failed to create fight: {response.status_code} - {response.text}")
        
        logger.info("🎉 Test events and fights created successfully!")

def main():
    tester = TestWinnerDisplay()
    tester.create_test_events_and_fights()

if __name__ == "__main__":
    main() 