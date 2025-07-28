-- Fix MMAMania Database Schema
-- Run this in your Supabase SQL Editor

-- Drop existing tables if they exist
DROP TABLE IF EXISTS rankings CASCADE;
DROP TABLE IF EXISTS fights CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS fighters CASCADE;

-- Create fighters table
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

-- Create events table
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

-- Create fights table with proper foreign keys
CREATE TABLE IF NOT EXISTS fights (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    fighter1_id UUID REFERENCES fighters(id) ON DELETE CASCADE,
    fighter2_id UUID REFERENCES fighters(id) ON DELETE CASCADE,
    weight_class VARCHAR,
    status VARCHAR DEFAULT 'scheduled',
    date TIMESTAMP WITH TIME ZONE,
    result JSONB,
    odds JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create rankings table with proper foreign key
CREATE TABLE IF NOT EXISTS rankings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    fighter_id UUID REFERENCES fighters(id) ON DELETE CASCADE,
    weight_class VARCHAR NOT NULL,
    rank_position INTEGER NOT NULL,
    rank_type VARCHAR DEFAULT 'ufc',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(weight_class, rank_position, rank_type)
);

-- Enable RLS on all tables
ALTER TABLE fighters ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE fights ENABLE ROW LEVEL SECURITY;
ALTER TABLE rankings ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Public read access" ON fighters FOR SELECT USING (true);
CREATE POLICY "Public read access" ON events FOR SELECT USING (true);
CREATE POLICY "Public read access" ON fights FOR SELECT USING (true);
CREATE POLICY "Public read access" ON rankings FOR SELECT USING (true);

-- Create policies for public write access (for testing)
CREATE POLICY "Public write access" ON fighters FOR INSERT WITH CHECK (true);
CREATE POLICY "Public write access" ON events FOR INSERT WITH CHECK (true);
CREATE POLICY "Public write access" ON fights FOR INSERT WITH CHECK (true);
CREATE POLICY "Public write access" ON rankings FOR INSERT WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_fighters_name ON fighters(name);
CREATE INDEX IF NOT EXISTS idx_fighters_weight_class ON fighters(weight_class);
CREATE INDEX IF NOT EXISTS idx_rankings_weight_class ON rankings(weight_class);
CREATE INDEX IF NOT EXISTS idx_rankings_fighter_id ON rankings(fighter_id);
CREATE INDEX IF NOT EXISTS idx_fights_event_id ON fights(event_id);
CREATE INDEX IF NOT EXISTS idx_fights_fighter1_id ON fights(fighter1_id);
CREATE INDEX IF NOT EXISTS idx_fights_fighter2_id ON fights(fighter2_id); 