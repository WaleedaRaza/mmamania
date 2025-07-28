#!/usr/bin/env python3
"""
Database-Only Supabase Migration Script for MMAMania
This script creates database tables without authentication dependencies
"""

import json
import csv
import os
import sys
from datetime import datetime
from supabase import create_client, Client
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing environment variables")
    print("Please create a .env file with:")
    print("SUPABASE_URL=https://your-project-id.supabase.co")
    print("SUPABASE_SERVICE_KEY=your_service_role_key_here")
    sys.exit(1)

class DatabaseOnlyMigrator:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def create_tables(self):
        """Create the necessary database tables (no auth tables)"""
        print("Creating database tables...")
        
        # Create fighters table
        fighters_table = """
        CREATE TABLE IF NOT EXISTS fighters (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name VARCHAR NOT NULL,
            nickname VARCHAR,
            weight_class VARCHAR,
            record JSONB,
            reach DECIMAL,
            height DECIMAL,
            stance VARCHAR,
            style VARCHAR,
            stats JSONB,
            ufc_ranking INTEGER,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create events table
        events_table = """
        CREATE TABLE IF NOT EXISTS events (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name VARCHAR NOT NULL,
            date TIMESTAMP WITH TIME ZONE,
            location VARCHAR,
            venue VARCHAR,
            broadcast_info VARCHAR,
            status VARCHAR DEFAULT 'scheduled',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create fights table
        fights_table = """
        CREATE TABLE IF NOT EXISTS fights (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            event_id UUID REFERENCES events(id),
            fighter1_id UUID REFERENCES fighters(id),
            fighter2_id UUID REFERENCES fighters(id),
            weight_class VARCHAR,
            status VARCHAR DEFAULT 'scheduled',
            date TIMESTAMP WITH TIME ZONE,
            result JSONB,
            odds JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create rankings table
        rankings_table = """
        CREATE TABLE IF NOT EXISTS rankings (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            fighter_id UUID REFERENCES fighters(id),
            weight_class VARCHAR NOT NULL,
            rank_position INTEGER NOT NULL,
            rank_type VARCHAR DEFAULT 'ufc',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(weight_class, rank_position, rank_type)
        );
        """
        
        tables = [
            ("fighters", fighters_table),
            ("events", events_table),
            ("fights", fights_table),
            ("rankings", rankings_table),
        ]
        
        for table_name, table_sql in tables:
            try:
                self.supabase.rpc('exec_sql', {'sql': table_sql}).execute()
                print(f"✅ Created table: {table_name}")
            except Exception as e:
                print(f"❌ Error creating {table_name}: {e}")
    
    def setup_rls_policies(self):
        """Set up Row Level Security policies for public access"""
        print("Setting up RLS policies...")
        
        policies = [
            "ALTER TABLE fighters ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE events ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE fights ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE rankings ENABLE ROW LEVEL SECURITY;",
            
            "CREATE POLICY IF NOT EXISTS \"Public read access\" ON fighters FOR SELECT USING (true);",
            "CREATE POLICY IF NOT EXISTS \"Public read access\" ON events FOR SELECT USING (true);",
            "CREATE POLICY IF NOT EXISTS \"Public read access\" ON fights FOR SELECT USING (true);",
            "CREATE POLICY IF NOT EXISTS \"Public read access\" ON rankings FOR SELECT USING (true);",
            
            "CREATE POLICY IF NOT EXISTS \"Public write access\" ON fighters FOR INSERT WITH CHECK (true);",
            "CREATE POLICY IF NOT EXISTS \"Public write access\" ON events FOR INSERT WITH CHECK (true);",
            "CREATE POLICY IF NOT EXISTS \"Public write access\" ON fights FOR INSERT WITH CHECK (true);",
            "CREATE POLICY IF NOT EXISTS \"Public write access\" ON rankings FOR INSERT WITH CHECK (true);",
        ]
        
        for policy in policies:
            try:
                self.supabase.rpc('exec_sql', {'sql': policy}).execute()
                print(f"✅ Applied policy: {policy[:50]}...")
            except Exception as e:
                print(f"❌ Error applying policy: {e}")
    
    def migrate_fighters(self):
        """Migrate fighters data from JSON files"""
        print("Migrating fighters...")
        
        # Load fighter data from JSON files
        fighter_files = [
            "assets/data/ufc_fighter_data_real.json",
            "assets/data/ufc_fighter_data.json",
        ]
        
        fighters_data = []
        for file_path in fighter_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        fighters_data.extend(data)
                    else:
                        fighters_data.append(data)
        
        migrated_count = 0
        for fighter in fighters_data:
            try:
                # Transform fighter data
                fighter_record = fighter.get('record', {})
                personal_info = fighter.get('personal_info', {})
                
                fighter_data = {
                    'name': fighter.get('name', ''),
                    'weight_class': fighter.get('division', '').replace(' Division', ''),
                    'nickname': fighter.get('nickname', ''),
                    'record': {
                        'wins': fighter_record.get('wins', 0),
                        'losses': fighter_record.get('losses', 0),
                        'draws': fighter_record.get('draws', 0),
                    },
                    'reach': personal_info.get('reach'),
                    'height': personal_info.get('height'),
                    'stance': personal_info.get('stance', ''),
                    'style': fighter.get('style', ''),
                    'stats': fighter.get('stats', {}),
                    'ufc_ranking': fighter.get('ufc_ranking'),
                    'is_active': True,
                }
                
                # Insert fighter
                self.supabase.table('fighters').upsert(fighter_data).execute()
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Error migrating fighter {fighter.get('name', 'Unknown')}: {e}")
        
        print(f"✅ Migrated {migrated_count} fighters")
    
    def migrate_rankings(self):
        """Migrate rankings data"""
        print("Migrating rankings...")
        
        # Get all fighters
        fighters_response = self.supabase.table('fighters').select('id, name, weight_class, ufc_ranking').execute()
        fighters = fighters_response.data
        
        migrated_count = 0
        for fighter in fighters:
            if fighter.get('ufc_ranking') and fighter.get('weight_class'):
                try:
                    ranking_data = {
                        'fighter_id': fighter['id'],
                        'weight_class': fighter['weight_class'],
                        'rank_position': fighter['ufc_ranking'],
                        'rank_type': 'ufc',
                    }
                    
                    self.supabase.table('rankings').upsert(ranking_data).execute()
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"❌ Error migrating ranking for {fighter.get('name', 'Unknown')}: {e}")
        
        print(f"✅ Migrated {migrated_count} rankings")
    
    def create_sample_data(self):
        """Create sample events and fights for testing"""
        print("Creating sample events and fights...")
        
        # Create sample event
        event_data = {
            'name': 'UFC 300: Pereira vs Hill',
            'date': '2024-04-13T23:00:00Z',
            'location': 'Las Vegas, Nevada',
            'venue': 'T-Mobile Arena',
            'broadcast_info': 'ESPN+ PPV',
            'status': 'scheduled',
        }
        
        try:
            event_response = self.supabase.table('events').insert(event_data).execute()
            event_id = event_response.data[0]['id']
            print(f"✅ Created sample event: {event_data['name']}")
            
            # Get some fighters for sample fights
            fighters_response = self.supabase.table('fighters').select('id, name').limit(10).execute()
            fighters = fighters_response.data
            
            if len(fighters) >= 2:
                # Create sample fight
                fight_data = {
                    'event_id': event_id,
                    'fighter1_id': fighters[0]['id'],
                    'fighter2_id': fighters[1]['id'],
                    'weight_class': 'Light Heavyweight',
                    'status': 'scheduled',
                    'date': '2024-04-13T23:00:00Z',
                    'odds': {'fighter1': 1.5, 'fighter2': 2.5},
                }
                
                self.supabase.table('fights').insert(fight_data).execute()
                print(f"✅ Created sample fight: {fighters[0]['name']} vs {fighters[1]['name']}")
                
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
    
    def run_migration(self):
        """Run the complete migration"""
        print("🚀 Starting database-only migration...")
        print(f"📡 Connecting to: {SUPABASE_URL}")
        
        try:
            # Test connection
            self.supabase.table('fighters').select('count').execute()
            print("✅ Database connection successful")
            
            # Create tables
            self.create_tables()
            
            # Set up RLS policies
            self.setup_rls_policies()
            
            # Migrate data
            self.migrate_fighters()
            self.migrate_rankings()
            
            # Create sample data
            self.create_sample_data()
            
            print("\n🎉 Migration completed successfully!")
            print("📊 Check your Supabase dashboard to see the data")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("Please check your environment variables and try again")

def main():
    migrator = DatabaseOnlyMigrator()
    migrator.run_migration()

if __name__ == "__main__":
    main() 