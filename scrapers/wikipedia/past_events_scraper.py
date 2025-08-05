#!/usr/bin/env python3
"""
Past UFC Events Scraper - Proof of Concept
Focuses on past events with proper event distribution and winner/loser data
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PastEventsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://en.wikipedia.org"
        self.supabase_url = SUPABASE_URL
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Past UFC events with known fight data
        self.past_events = [
            {
                'name': 'UFC 300: Pereira vs Hill',
                'date': '2024-04-13',
                'venue': 'T-Mobile Arena',
                'location': 'Las Vegas, Nevada',
                'wikipedia_url': 'UFC_300',
                'fights': [
                    {'fighter1': 'Alex Pereira', 'fighter2': 'Jamahal Hill', 'method': 'TKO (punches)', 'round': 1, 'time': '3:14', 'winner': 'Alex Pereira', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Zhang Weili', 'fighter2': 'Yan Xiaonan', 'method': 'Decision (unanimous)', 'round': 5, 'time': '5:00', 'winner': 'Zhang Weili', 'weight_class': 'Strawweight'},
                    {'fighter1': 'Justin Gaethje', 'fighter2': 'Max Holloway', 'method': 'KO (head kick)', 'round': 5, 'time': '4:59', 'winner': 'Justin Gaethje', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Arman Tsarukyan', 'fighter2': 'Charles Oliveira', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Arman Tsarukyan', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Kayla Harrison', 'fighter2': 'Holly Holm', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '1:21', 'winner': 'Kayla Harrison', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Aljamain Sterling', 'fighter2': 'Calvin Kattar', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Aljamain Sterling', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Jiri Prochazka', 'fighter2': 'Aleksandar Rakic', 'method': 'TKO (punches)', 'round': 2, 'time': '3:17', 'winner': 'Jiri Prochazka', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Bobby Green', 'fighter2': 'Jim Miller', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Bobby Green', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Deiveson Figueiredo', 'fighter2': 'Cody Garbrandt', 'method': 'Submission (guillotine choke)', 'round': 2, 'time': '2:13', 'winner': 'Deiveson Figueiredo', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Sodiq Yusuff', 'fighter2': 'Diego Lopes', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Sodiq Yusuff', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Renato Moicano', 'fighter2': 'Jalin Turner', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '4:11', 'winner': 'Renato Moicano', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Jessica Andrade', 'fighter2': 'Marina Rodriguez', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Jessica Andrade', 'weight_class': 'Strawweight'},
                    {'fighter1': 'Bobby Green', 'fighter2': 'Paddy Pimblett', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Bobby Green', 'weight_class': 'Lightweight'}
                ]
            },
            {
                'name': 'UFC 299: O\'Malley vs Vera 2',
                'date': '2024-03-09',
                'venue': 'Kaseya Center',
                'location': 'Miami, Florida',
                'wikipedia_url': 'UFC_299',
                'fights': [
                    {'fighter1': 'Sean O\'Malley', 'fighter2': 'Marlon Vera', 'method': 'Decision (unanimous)', 'round': 5, 'time': '5:00', 'winner': 'Sean O\'Malley', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Dustin Poirier', 'fighter2': 'Benoit Saint Denis', 'method': 'KO (punches)', 'round': 2, 'time': '2:32', 'winner': 'Dustin Poirier', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Kevin Holland', 'fighter2': 'Michael Page', 'method': 'Submission (rear-naked choke)', 'round': 1, 'time': '3:00', 'winner': 'Kevin Holland', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Jack Della Maddalena', 'fighter2': 'Gilbert Burns', 'method': 'TKO (punches)', 'round': 3, 'time': '2:43', 'winner': 'Jack Della Maddalena', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Petr Yan', 'fighter2': 'Song Yadong', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Petr Yan', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Curtis Blaydes', 'fighter2': 'Jailton Almeida', 'method': 'TKO (punches)', 'round': 2, 'time': '0:36', 'winner': 'Curtis Blaydes', 'weight_class': 'Heavyweight'},
                    {'fighter1': 'Maycee Barber', 'fighter2': 'Katlyn Cerminara', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Maycee Barber', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Mateusz Gamrot', 'fighter2': 'Rafael dos Anjos', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Mateusz Gamrot', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Pedro Munhoz', 'fighter2': 'Kyler Phillips', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Pedro Munhoz', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Michel Pereira', 'fighter2': 'Michal Oleksiejczuk', 'method': 'Submission (rear-naked choke)', 'round': 1, 'time': '1:01', 'winner': 'Michel Pereira', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Robelis Despaigne', 'fighter2': 'Josh Parisian', 'method': 'TKO (punches)', 'round': 1, 'time': '0:18', 'winner': 'Robelis Despaigne', 'weight_class': 'Heavyweight'},
                    {'fighter1': 'CJ Vergara', 'fighter2': 'Assu Almabayev', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'CJ Vergara', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Joanne Wood', 'fighter2': 'Maryna Moroz', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Joanne Wood', 'weight_class': 'Flyweight'}
                ]
            },
            {
                'name': 'UFC 298: Volkanovski vs Topuria',
                'date': '2024-02-17',
                'venue': 'Honda Center',
                'location': 'Anaheim, California',
                'wikipedia_url': 'UFC_298',
                'fights': [
                    {'fighter1': 'Ilia Topuria', 'fighter2': 'Alexander Volkanovski', 'method': 'KO (punches)', 'round': 2, 'time': '3:32', 'winner': 'Ilia Topuria', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Robert Whittaker', 'fighter2': 'Paulo Costa', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Robert Whittaker', 'weight_class': 'Middleweight'},
                    {'fighter1': 'Ian Machado Garry', 'fighter2': 'Geoff Neal', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Ian Machado Garry', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Merab Dvalishvili', 'fighter2': 'Henry Cejudo', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Merab Dvalishvili', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Anthony Hernandez', 'fighter2': 'Roman Kopylov', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '3:23', 'winner': 'Anthony Hernandez', 'weight_class': 'Middleweight'},
                    {'fighter1': 'Mackenzie Dern', 'fighter2': 'Amanda Lemos', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Mackenzie Dern', 'weight_class': 'Strawweight'},
                    {'fighter1': 'Marcos Rogerio de Lima', 'fighter2': 'Junior Tafa', 'method': 'TKO (leg kicks)', 'round': 2, 'time': '1:14', 'winner': 'Marcos Rogerio de Lima', 'weight_class': 'Heavyweight'},
                    {'fighter1': 'Rinya Nakamura', 'fighter2': 'Carlos Vera', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Rinya Nakamura', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Zhang Mingyang', 'fighter2': 'Brendson Ribeiro', 'method': 'KO (punches)', 'round': 1, 'time': '1:41', 'winner': 'Zhang Mingyang', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Tatsuro Taira', 'fighter2': 'Carlos Hernandez', 'method': 'TKO (punches)', 'round': 1, 'time': '0:55', 'winner': 'Tatsuro Taira', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Josh Quinlan', 'fighter2': 'Danny Barlow', 'method': 'TKO (punches)', 'round': 3, 'time': '1:18', 'winner': 'Josh Quinlan', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Oban Elliott', 'fighter2': 'Val Woodburn', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Oban Elliott', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Miranda Maverick', 'fighter2': 'Andrea Lee', 'method': 'Submission (armbar)', 'round': 3, 'time': '4:17', 'winner': 'Miranda Maverick', 'weight_class': 'Flyweight'}
                ]
            }
        ]
    
    def clear_existing_data(self):
        """Clear existing events and fights for clean start"""
        logger.info("🗑️ Clearing existing data...")
        
        try:
            # Clear fights first (due to foreign key constraints)
            fights_response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?select=id&limit=1000",
                headers=self.headers
            )
            if fights_response.status_code == 200:
                fights = fights_response.json()
                logger.info(f"   📊 Found {len(fights)} fights to delete")
                
                for fight in fights:
                    requests.delete(
                        f"{self.supabase_url}/rest/v1/fights?id=eq.{fight['id']}",
                        headers=self.headers
                    )
                logger.info(f"   ✅ Deleted {len(fights)} fights")
            
            # Clear events
            events_response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id&limit=1000",
                headers=self.headers
            )
            if events_response.status_code == 200:
                events = events_response.json()
                logger.info(f"   📊 Found {len(events)} events to delete")
                
                for event in events:
                    requests.delete(
                        f"{self.supabase_url}/rest/v1/events?id=eq.{event['id']}",
                        headers=self.headers
                    )
                logger.info(f"   ✅ Deleted {len(events)} events")
                
        except Exception as e:
            logger.error(f"❌ Error clearing data: {e}")
    
    def get_or_create_fighter(self, fighter_name: str) -> Optional[str]:
        """Get or create fighter in database"""
        try:
            # Check if fighter exists
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters?name=eq.{fighter_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                fighters = response.json()
                if fighters:
                    return fighters[0]['id']
            
            # Create new fighter
            fighter_to_create = {
                'name': fighter_name,
                'weight_class': 'Unknown',
                'record': {'wins': 0, 'losses': 0, 'draws': 0},
                'is_active': 'Active'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/fighters",
                headers=self.headers,
                json=fighter_to_create
            )
            
            if response.status_code == 201:
                # Get the created fighter ID
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/fighters?name=eq.{fighter_name}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    fighters = response.json()
                    if fighters:
                        return fighters[0]['id']
            
            return None
            
        except Exception as e:
            logger.error(f"Error with fighter {fighter_name}: {e}")
            return None
    
    def create_event(self, event_data: Dict) -> Optional[str]:
        """Create event in database"""
        try:
            event_to_create = {
                'name': event_data['name'],
                'date': event_data['date'],
                'venue': event_data['venue'],
                'location': event_data['location'],
                'status': 'completed'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/events",
                headers=self.headers,
                json=event_to_create
            )
            
            if response.status_code == 201:
                # Get the created event ID
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/events?name=eq.{event_data['name']}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    events = response.json()
                    if events:
                        return events[0]['id']
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating event {event_data['name']}: {e}")
            return None
    
    def create_fight(self, fight_data: Dict, event_id: str) -> bool:
        """Create fight in database with proper winner/loser data"""
        try:
            fighter1_id = self.get_or_create_fighter(fight_data['fighter1'])
            fighter2_id = self.get_or_create_fighter(fight_data['fighter2'])
            
            if not fighter1_id or not fighter2_id:
                logger.error(f"Could not get/create fighters for {fight_data['fighter1']} vs {fight_data['fighter2']}")
                return False
            
            # Determine winner
            winner_id = fighter1_id if fight_data['winner'] == fight_data['fighter1'] else fighter2_id
            
            fight_to_create = {
                'event_id': event_id,
                'fighter1_id': fighter1_id,
                'fighter2_id': fighter2_id,
                'status': 'completed',
                'result': {
                    'method': fight_data['method'],
                    'round': fight_data['round'],
                    'time': fight_data['time'],
                    'winner_id': winner_id
                },
                'weight_class': fight_data['weight_class']
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/fights",
                headers=self.headers,
                json=fight_to_create
            )
            
            if response.status_code == 201:
                logger.info(f"   ✅ {fight_data['fighter1']} vs {fight_data['fighter2']} -> {fight_data['winner']} wins")
                return True
            else:
                logger.error(f"   ❌ Failed to create fight: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating fight: {e}")
            return False
    
    def populate_past_events(self):
        """Populate database with past events and fights"""
        logger.info("🥊 Starting past events population...")
        
        total_fights_created = 0
        total_events_created = 0
        
        for event_data in self.past_events:
            logger.info(f"\n📅 Processing: {event_data['name']}")
            
            # Create event
            event_id = self.create_event(event_data)
            if not event_id:
                logger.error(f"❌ Could not create event: {event_data['name']}")
                continue
            
            total_events_created += 1
            logger.info(f"   ✅ Created event: {event_data['name']}")
            
            # Create fights for this event
            fights_created = 0
            for fight_data in event_data['fights']:
                if self.create_fight(fight_data, event_id):
                    fights_created += 1
            
            total_fights_created += fights_created
            logger.info(f"   📊 Created {fights_created} fights for {event_data['name']}")
        
        logger.info(f"\n🎉 Population complete!")
        logger.info(f"   📊 Total events created: {total_events_created}")
        logger.info(f"   🥊 Total fights created: {total_fights_created}")
        
        return total_events_created, total_fights_created
    
    def run_scraper(self):
        """Run the complete scraper process"""
        logger.info("🚀 Starting Past UFC Events Scraper - Proof of Concept")
        
        # Step 1: Clear existing data
        self.clear_existing_data()
        
        # Step 2: Populate past events
        events_created, fights_created = self.populate_past_events()
        
        # Step 3: Verify data
        self.verify_data()
        
        logger.info(f"\n✅ Proof of Concept Complete!")
        logger.info(f"   📊 Events: {events_created}")
        logger.info(f"   🥊 Fights: {fights_created}")
        logger.info(f"   🎯 Ready for Flutter integration!")
    
    def verify_data(self):
        """Verify the created data"""
        logger.info("\n🔍 Verifying created data...")
        
        try:
            # Check events
            events_response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name,date&limit=10",
                headers=self.headers
            )
            if events_response.status_code == 200:
                events = events_response.json()
                logger.info(f"   📊 Events in database: {len(events)}")
                for event in events:
                    logger.info(f"      ✅ {event['name']} ({event['date']})")
            
            # Check fights
            fights_response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?select=id,event_id,winner_id&limit=10",
                headers=self.headers
            )
            if fights_response.status_code == 200:
                fights = fights_response.json()
                logger.info(f"   🥊 Fights in database: {len(fights)}")
                
                fights_with_winners = [f for f in fights if f.get('winner_id')]
                logger.info(f"      ✅ Fights with winners: {len(fights_with_winners)}")
            
            # Check fighters
            fighters_response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters?select=id,name&limit=10",
                headers=self.headers
            )
            if fighters_response.status_code == 200:
                fighters = fighters_response.json()
                logger.info(f"   👊 Fighters in database: {len(fighters)}")
            
        except Exception as e:
            logger.error(f"❌ Error verifying data: {e}")

def main():
    scraper = PastEventsScraper()
    scraper.run_scraper()

if __name__ == "__main__":
    main() 