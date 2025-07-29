#!/usr/bin/env python3
"""
Enhanced UFC Events Data Migration Script
Migrates comprehensive event and fight data to Supabase with proper status tracking
"""

import os
import sys
import json
import csv
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import requests
from supabase import create_client, Client

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"

class EnhancedEventsMigrator:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def migrate_events_data(self, events_file: str):
        """Migrate events data to Supabase"""
        logger.info(f"🚀 Starting enhanced events migration from {events_file}")
        
        try:
            # Load events data
            with open(events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            logger.info(f"📊 Loaded {len(events_data)} events from file")
            
            # Process and migrate events
            migrated_events = []
            for event in events_data:
                try:
                    event_id = self.migrate_event(event)
                    if event_id:
                        migrated_events.append(event_id)
                        logger.info(f"✅ Migrated event: {event['name']}")
                except Exception as e:
                    logger.error(f"❌ Error migrating event {event.get('name', 'Unknown')}: {e}")
            
            logger.info(f"🎉 Successfully migrated {len(migrated_events)} events")
            return migrated_events
            
        except Exception as e:
            logger.error(f"❌ Error in events migration: {e}")
            return []
    
    def migrate_event(self, event_data: Dict) -> Optional[str]:
        """Migrate a single event to Supabase"""
        try:
            # Prepare event data for Supabase
            event_payload = {
                'title': event_data['name'],
                'date': self.parse_event_date(event_data['date']),
                'venue': event_data['venue'],
                'location': event_data['location'],
                'status': event_data['status'],
                'type': event_data['event_type'],
                'source_url': event_data.get('url'),
                'scraped_at': event_data.get('scraped_at', datetime.now().isoformat())
            }
            
            # Insert event into Supabase
            response = self.supabase.table('events').insert(event_payload).execute()
            
            if response.data:
                event_id = response.data[0]['id']
                logger.info(f"✅ Created event with ID: {event_id}")
                return event_id
            else:
                logger.warning(f"⚠️ No event created for: {event_data['name']}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error migrating event: {e}")
            return None
    
    def parse_event_date(self, date_str: str) -> Optional[str]:
        """Parse event date string to ISO format"""
        try:
            if not date_str:
                return None
            
            # Handle various date formats
            date_formats = [
                '%b %d, %Y',  # "Nov 22, 2025"
                '%d %b %Y',   # "22 Nov 2025"
                '%B %d, %Y',  # "November 22, 2025"
                '%Y-%m-%d',   # "2025-11-22"
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.isoformat()
                except ValueError:
                    continue
            
            # If no format matches, return as is
            return date_str
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            return date_str
    
    def migrate_fights_for_event(self, event_id: str, fights_data: List[Dict]):
        """Migrate fights for a specific event"""
        logger.info(f"🥊 Migrating fights for event {event_id}")
        
        migrated_fights = []
        
        for fight in fights_data:
            try:
                fight_id = self.migrate_fight(event_id, fight)
                if fight_id:
                    migrated_fights.append(fight_id)
                    logger.info(f"✅ Migrated fight: {fight.get('fighter1', '')} vs {fight.get('fighter2', '')}")
            except Exception as e:
                logger.error(f"❌ Error migrating fight: {e}")
        
        logger.info(f"🎉 Successfully migrated {len(migrated_fights)} fights for event {event_id}")
        return migrated_fights
    
    def migrate_fight(self, event_id: str, fight_data: Dict) -> Optional[str]:
        """Migrate a single fight to Supabase"""
        try:
            # Get or create fighters
            fighter1_id = self.get_or_create_fighter(fight_data['fighter1'])
            fighter2_id = self.get_or_create_fighter(fight_data['fighter2'])
            
            if not fighter1_id or not fighter2_id:
                logger.warning(f"⚠️ Could not create fighters for fight: {fight_data}")
                return None
            
            # Determine winner and loser
            winner_id = None
            if fight_data.get('winner'):
                winner_id = self.get_or_create_fighter(fight_data['winner'])
            
            # Prepare fight data for Supabase
            fight_payload = {
                'event_id': event_id,
                'fighter1_id': fighter1_id,
                'fighter2_id': fighter2_id,
                'weight_class': fight_data.get('weight_class', ''),
                'status': 'completed' if winner_id else 'scheduled',
                'winner_id': winner_id,
                'method': fight_data.get('method', ''),
                'round': fight_data.get('round', ''),
                'time': fight_data.get('time', ''),
                'card_type': fight_data.get('card_type', ''),
                'is_main_event': fight_data.get('card_type', '').lower() == 'main card',
                'is_title_fight': 'title' in fight_data.get('weight_class', '').lower(),
                'date': datetime.now().isoformat()  # Will be updated from event date
            }
            
            # Insert fight into Supabase
            response = self.supabase.table('fights').insert(fight_payload).execute()
            
            if response.data:
                fight_id = response.data[0]['id']
                logger.info(f"✅ Created fight with ID: {fight_id}")
                return fight_id
            else:
                logger.warning(f"⚠️ No fight created")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error migrating fight: {e}")
            return None
    
    def get_or_create_fighter(self, fighter_name: str) -> Optional[str]:
        """Get existing fighter or create new one"""
        if not fighter_name:
            return None
        
        try:
            # Clean fighter name
            clean_name = self.clean_fighter_name(fighter_name)
            
            # Check if fighter already exists
            response = self.supabase.table('fighters').select('id').eq('name', clean_name).execute()
            
            if response.data:
                return response.data[0]['id']
            
            # Create new fighter
            fighter_payload = {
                'name': clean_name,
                'record': '0-0-0',  # Default record
                'weight_class': '',  # Will be updated from fights
                'status': 'active',
                'scraped_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('fighters').insert(fighter_payload).execute()
            
            if response.data:
                fighter_id = response.data[0]['id']
                logger.info(f"✅ Created fighter: {clean_name} (ID: {fighter_id})")
                return fighter_id
            else:
                logger.warning(f"⚠️ Could not create fighter: {clean_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error with fighter {fighter_name}: {e}")
            return None
    
    def clean_fighter_name(self, name: str) -> str:
        """Clean fighter name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        clean_name = ' '.join(name.split())
        
        # Remove common suffixes
        suffixes = [' (c)', ' (ic)', ' (nc)']
        for suffix in suffixes:
            clean_name = clean_name.replace(suffix, '')
        
        return clean_name.strip()
    
    def update_fight_statuses(self):
        """Update fight statuses based on event dates"""
        logger.info("🔄 Updating fight statuses based on event dates...")
        
        try:
            # Get all events with their dates
            response = self.supabase.table('events').select('id, date, status').execute()
            events = response.data
            
            current_date = datetime.now()
            
            for event in events:
                event_date = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                
                # If event date has passed and status is still 'scheduled', update to 'completed'
                if event_date < current_date and event['status'] == 'scheduled':
                    try:
                        # Update event status
                        self.supabase.table('events').update({'status': 'completed'}).eq('id', event['id']).execute()
                        
                        # Update all fights for this event to completed (if not already)
                        self.supabase.table('fights').update({'status': 'completed'}).eq('event_id', event['id']).eq('status', 'scheduled').execute()
                        
                        logger.info(f"✅ Updated event {event['id']} status to completed")
                    except Exception as e:
                        logger.error(f"❌ Error updating event {event['id']}: {e}")
            
            logger.info("🎉 Fight status update complete")
            
        except Exception as e:
            logger.error(f"❌ Error updating fight statuses: {e}")
    
    def create_prediction_tables(self):
        """Create prediction and user stats tables if they don't exist"""
        logger.info("📊 Setting up prediction tables...")
        
        # Note: In a real implementation, you would use Supabase's SQL editor
        # to create these tables. Here we just log the structure.
        
        prediction_table_sql = """
        CREATE TABLE IF NOT EXISTS predictions (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id),
            fight_id UUID REFERENCES fights(id),
            predicted_winner_id UUID REFERENCES fighters(id),
            predicted_method TEXT,
            predicted_round INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            result TEXT DEFAULT 'pending',
            elo_change INTEGER DEFAULT 0,
            actual_winner_id UUID REFERENCES fighters(id),
            actual_method TEXT,
            actual_round INTEGER,
            accuracy_score DECIMAL(5,2)
        );
        """
        
        user_stats_table_sql = """
        CREATE TABLE IF NOT EXISTS user_stats (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) UNIQUE,
            elo_rating INTEGER DEFAULT 1200,
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            accuracy DECIMAL(5,2) DEFAULT 0.0,
            current_streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0,
            last_prediction_date TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        logger.info("📋 Prediction tables structure defined")
        logger.info("💡 Run these SQL commands in your Supabase SQL editor:")
        logger.info(prediction_table_sql)
        logger.info(user_stats_table_sql)

def main():
    """Main function to run the migration"""
    migrator = EnhancedEventsMigrator()
    
    # Check for events file
    events_file = "data/exports/ufc_events_latest.json"
    
    if not os.path.exists(events_file):
        logger.error(f"❌ Events file not found: {events_file}")
        logger.info("💡 Please run the comprehensive scraper first:")
        logger.info("   python scripts/comprehensive_ufc_events_scraper.py")
        return
    
    # Migrate events
    migrated_events = migrator.migrate_events_data(events_file)
    
    if migrated_events:
        # Update fight statuses
        migrator.update_fight_statuses()
        
        # Create prediction tables
        migrator.create_prediction_tables()
        
        logger.info("🎉 Enhanced migration complete!")
        logger.info(f"  Migrated {len(migrated_events)} events")
        logger.info("  Updated fight statuses")
        logger.info("  Prepared prediction system")
    else:
        logger.warning("⚠️ No events were migrated")

if __name__ == "__main__":
    main() 