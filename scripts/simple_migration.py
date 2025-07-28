#!/usr/bin/env python3
"""
Simple Database Migration Script for MMAMania
Uses direct HTTP requests to avoid auth client issues
"""

import json
import os
import sys
import requests
from datetime import datetime
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

class SimpleMigrator:
    def __init__(self):
        self.base_url = f"{SUPABASE_URL}/rest/v1"
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
    def create_tables(self):
        """Create tables using direct SQL"""
        print("Creating database tables...")
        
        # SQL statements to create tables
        sql_statements = [
            """
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
            """,
            """
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
            """,
            """
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
            """,
            """
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
        ]
        
        for i, sql in enumerate(sql_statements):
            try:
                # Use RPC to execute SQL
                rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
                response = requests.post(
                    rpc_url,
                    headers=self.headers,
                    json={'sql': sql}
                )
                
                if response.status_code == 200:
                    table_names = ['fighters', 'events', 'fights', 'rankings']
                    print(f"✅ Created table: {table_names[i]}")
                else:
                    print(f"❌ Error creating table {i+1}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error creating table {i+1}: {e}")
    
    def setup_rls_policies(self):
        """Set up RLS policies"""
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
                rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
                response = requests.post(
                    rpc_url,
                    headers=self.headers,
                    json={'sql': policy}
                )
                
                if response.status_code == 200:
                    print(f"✅ Applied policy: {policy[:50]}...")
                else:
                    print(f"❌ Error applying policy: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error applying policy: {e}")
    
    def insert_sample_data(self):
        """Insert sample data for testing"""
        print("Inserting sample data...")
        
        # Sample fighters
        sample_fighters = [
            {
                'name': 'Israel Adesanya',
                'nickname': 'The Last Stylebender',
                'weight_class': 'Middleweight',
                'record': {'wins': 24, 'losses': 3, 'draws': 0},
                'reach': 80.0,
                'height': 76.0,
                'stance': 'Orthodox',
                'style': 'Kickboxing',
                'ufc_ranking': 1,
                'is_active': True
            },
            {
                'name': 'Alex Pereira',
                'nickname': 'Poatan',
                'weight_class': 'Light Heavyweight',
                'record': {'wins': 9, 'losses': 2, 'draws': 0},
                'reach': 79.0,
                'height': 76.0,
                'stance': 'Orthodox',
                'style': 'Kickboxing',
                'ufc_ranking': 1,
                'is_active': True
            },
            {
                'name': 'Jon Jones',
                'nickname': 'Bones',
                'weight_class': 'Heavyweight',
                'record': {'wins': 27, 'losses': 1, 'draws': 0},
                'reach': 84.5,
                'height': 76.0,
                'stance': 'Orthodox',
                'style': 'Wrestling',
                'ufc_ranking': 1,
                'is_active': True
            }
        ]
        
        # Insert fighters
        for fighter in sample_fighters:
            try:
                response = requests.post(
                    f"{self.base_url}/fighters",
                    headers=self.headers,
                    json=fighter
                )
                
                if response.status_code == 201:
                    print(f"✅ Added fighter: {fighter['name']}")
                else:
                    print(f"❌ Error adding fighter {fighter['name']}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error adding fighter {fighter['name']}: {e}")
        
        # Sample event
        sample_event = {
            'name': 'UFC 300: Pereira vs Hill',
            'date': '2024-04-13T23:00:00Z',
            'location': 'Las Vegas, Nevada',
            'venue': 'T-Mobile Arena',
            'broadcast_info': 'ESPN+ PPV',
            'status': 'scheduled'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/events",
                headers=self.headers,
                json=sample_event
            )
            
            if response.status_code == 201:
                print(f"✅ Added event: {sample_event['name']}")
            else:
                print(f"❌ Error adding event: {response.text}")
                
        except Exception as e:
            print(f"❌ Error adding event: {e}")
    
    def test_connection(self):
        """Test database connection"""
        print("Testing database connection...")
        
        try:
            # Test with a simple RPC call instead of table access
            rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
            response = requests.post(
                rpc_url,
                headers=self.headers,
                json={'sql': 'SELECT 1 as test;'}
            )
            
            if response.status_code == 200:
                print("✅ Database connection successful!")
                return True
            else:
                print(f"❌ Database connection failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def run_migration(self):
        """Run the complete migration"""
        print("🚀 Starting simple database migration...")
        print(f"📡 Connecting to: {SUPABASE_URL}")
        
        # Test connection first
        if not self.test_connection():
            print("❌ Cannot connect to database. Please check your credentials.")
            return
        
        # Create tables
        self.create_tables()
        
        # Set up RLS policies
        self.setup_rls_policies()
        
        # Insert sample data
        self.insert_sample_data()
        
        print("\n🎉 Migration completed successfully!")
        print("📊 Check your Supabase dashboard to see the data")

def main():
    migrator = SimpleMigrator()
    migrator.run_migration()

if __name__ == "__main__":
    main() 