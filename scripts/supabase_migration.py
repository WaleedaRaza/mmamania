#!/usr/bin/env python3
"""
Supabase Migration Script for FightHub
This script helps migrate existing MMA data to Supabase
"""

import json
import csv
import os
import sys
from datetime import datetime
from supabase import create_client, Client
from typing import Dict, List, Any

# Configuration
SUPABASE_URL = "YOUR_SUPABASE_URL"  # Replace with your Supabase URL
SUPABASE_KEY = "YOUR_SUPABASE_SERVICE_KEY"  # Replace with your service key

class SupabaseMigrator:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def create_tables(self):
        """Create the necessary tables in Supabase"""
        print("Creating tables...")
        
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
        
        # Create user_profiles table
        user_profiles_table = """
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id),
            username VARCHAR UNIQUE,
            email VARCHAR,
            avatar_url VARCHAR,
            bio TEXT,
            favorite_fighters JSONB,
            stats JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create predictions table
        predictions_table = """
        CREATE TABLE IF NOT EXISTS predictions (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id),
            fight_id UUID REFERENCES fights(id),
            predicted_winner UUID REFERENCES fighters(id),
            prediction_method VARCHAR,
            confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100),
            prediction_details JSONB,
            is_correct BOOLEAN,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create debates table
        debates_table = """
        CREATE TABLE IF NOT EXISTS debates (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            title VARCHAR NOT NULL,
            description TEXT,
            author_id UUID REFERENCES auth.users(id),
            category VARCHAR,
            status VARCHAR DEFAULT 'active',
            participants_count INTEGER DEFAULT 0,
            max_participants INTEGER DEFAULT 20,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create hot_takes table
        hot_takes_table = """
        CREATE TABLE IF NOT EXISTS hot_takes (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            content TEXT NOT NULL,
            author_id UUID REFERENCES auth.users(id),
            likes_count INTEGER DEFAULT 0,
            dislikes_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        tables = [
            ("fighters", fighters_table),
            ("events", events_table),
            ("fights", fights_table),
            ("rankings", rankings_table),
            ("user_profiles", user_profiles_table),
            ("predictions", predictions_table),
            ("debates", debates_table),
            ("hot_takes", hot_takes_table),
        ]
        
        for table_name, table_sql in tables:
            try:
                self.supabase.rpc('exec_sql', {'sql': table_sql}).execute()
                print(f"✅ Created table: {table_name}")
            except Exception as e:
                print(f"❌ Error creating {table_name}: {e}")
    
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
        
        for fighter in fighters_data:
            try:
                # Transform fighter data
                fighter_record = fighter.get('record', {})
                personal_info = fighter.get('personal_info', {})
                
                fighter_data = {
                    'name': fighter.get('name', ''),
                    'weight_class': fighter.get('division', '').replace(' Division', ''),
                    'record': {
                        'wins': fighter_record.get('wins', 0),
                        'losses': fighter_record.get('losses', 0),
                        'draws': fighter_record.get('draws', 0),
                    },
                    'reach': float(personal_info.get('reach', 0)) if personal_info.get('reach') else None,
                    'height': float(personal_info.get('height', 0)) if personal_info.get('height') else None,
                    'stance': personal_info.get('fighting_style', ''),
                    'style': personal_info.get('fighting_style', ''),
                    'stats': personal_info,
                    'is_active': personal_info.get('status', 'Active') == 'Active',
                }
                
                # Insert fighter
                result = self.supabase.table('fighters').insert(fighter_data).execute()
                print(f"✅ Migrated fighter: {fighter_data['name']}")
                
            except Exception as e:
                print(f"❌ Error migrating fighter {fighter.get('name', 'Unknown')}: {e}")
    
    def migrate_rankings(self):
        """Migrate rankings data from CSV files"""
        print("Migrating rankings...")
        
        rankings_file = "data/processed/rankings.csv"
        if not os.path.exists(rankings_file):
            print(f"❌ Rankings file not found: {rankings_file}")
            return
        
        with open(rankings_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Find fighter by name
                    fighter_result = self.supabase.table('fighters').select('id').eq('name', row['name']).execute()
                    
                    if fighter_result.data:
                        fighter_id = fighter_result.data[0]['id']
                        
                        ranking_data = {
                            'fighter_id': fighter_id,
                            'weight_class': row.get('division', '').replace(' Division', ''),
                            'rank_position': int(row.get('rank', 0)),
                            'rank_type': 'ufc',
                        }
                        
                        self.supabase.table('rankings').insert(ranking_data).execute()
                        print(f"✅ Migrated ranking: {row['name']} - {row.get('division', '')}")
                    
                except Exception as e:
                    print(f"❌ Error migrating ranking for {row.get('name', 'Unknown')}: {e}")
    
    def create_functions(self):
        """Create database functions for analytics"""
        print("Creating functions...")
        
        # Leaderboard function
        leaderboard_function = """
        CREATE OR REPLACE FUNCTION get_leaderboard(limit_count INTEGER DEFAULT 20)
        RETURNS TABLE (
            user_id UUID,
            username VARCHAR,
            total_predictions INTEGER,
            correct_predictions INTEGER,
            win_rate DECIMAL,
            current_streak INTEGER
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                up.user_id,
                up.username,
                COUNT(p.id) as total_predictions,
                COUNT(CASE WHEN p.is_correct = true THEN 1 END) as correct_predictions,
                CASE 
                    WHEN COUNT(p.id) > 0 
                    THEN ROUND((COUNT(CASE WHEN p.is_correct = true THEN 1 END)::DECIMAL / COUNT(p.id)::DECIMAL) * 100, 2)
                    ELSE 0 
                END as win_rate,
                0 as current_streak
            FROM user_profiles up
            LEFT JOIN predictions p ON up.user_id = p.user_id
            GROUP BY up.user_id, up.username
            HAVING COUNT(p.id) > 0
            ORDER BY win_rate DESC, total_predictions DESC
            LIMIT limit_count;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Fighter stats function
        fighter_stats_function = """
        CREATE OR REPLACE FUNCTION get_fighter_stats(fighter_id UUID)
        RETURNS JSON AS $$
        DECLARE
            result JSON;
        BEGIN
            SELECT json_build_object(
                'total_fights', COUNT(f.id),
                'wins', COUNT(CASE WHEN f.result->>'winner_id' = fighter_id::TEXT THEN 1 END),
                'losses', COUNT(CASE WHEN f.result->>'loser_id' = fighter_id::TEXT THEN 1 END),
                'win_rate', CASE 
                    WHEN COUNT(f.id) > 0 
                    THEN ROUND((COUNT(CASE WHEN f.result->>'winner_id' = fighter_id::TEXT THEN 1 END)::DECIMAL / COUNT(f.id)::DECIMAL) * 100, 2)
                    ELSE 0 
                END
            ) INTO result
            FROM fights f
            WHERE (f.fighter1_id = fighter_id OR f.fighter2_id = fighter_id)
            AND f.result IS NOT NULL;
            
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        # Prediction stats function
        prediction_stats_function = """
        CREATE OR REPLACE FUNCTION get_prediction_stats(user_id UUID)
        RETURNS JSON AS $$
        DECLARE
            result JSON;
        BEGIN
            SELECT json_build_object(
                'total_predictions', COUNT(p.id),
                'correct_predictions', COUNT(CASE WHEN p.is_correct = true THEN 1 END),
                'win_rate', CASE 
                    WHEN COUNT(p.id) > 0 
                    THEN ROUND((COUNT(CASE WHEN p.is_correct = true THEN 1 END)::DECIMAL / COUNT(p.id)::DECIMAL) * 100, 2)
                    ELSE 0 
                END,
                'current_streak', 0,
                'best_streak', 0
            ) INTO result
            FROM predictions p
            WHERE p.user_id = user_id;
            
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        functions = [
            ("get_leaderboard", leaderboard_function),
            ("get_fighter_stats", fighter_stats_function),
            ("get_prediction_stats", prediction_stats_function),
        ]
        
        for func_name, func_sql in functions:
            try:
                self.supabase.rpc('exec_sql', {'sql': func_sql}).execute()
                print(f"✅ Created function: {func_name}")
            except Exception as e:
                print(f"❌ Error creating function {func_name}: {e}")
    
    def run_migration(self):
        """Run the complete migration"""
        print("🚀 Starting Supabase migration...")
        
        try:
            self.create_tables()
            self.migrate_fighters()
            self.migrate_rankings()
            self.create_functions()
            
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            sys.exit(1)

def main():
    if not SUPABASE_URL or SUPABASE_URL == "YOUR_SUPABASE_URL":
        print("❌ Please set your Supabase URL in the script")
        sys.exit(1)
    
    if not SUPABASE_KEY or SUPABASE_KEY == "YOUR_SUPABASE_SERVICE_KEY":
        print("❌ Please set your Supabase service key in the script")
        sys.exit(1)
    
    migrator = SupabaseMigrator()
    migrator.run_migration()

if __name__ == "__main__":
    main() 