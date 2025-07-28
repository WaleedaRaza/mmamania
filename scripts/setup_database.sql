-- MMAMania Database Setup SQL
-- Run this in your Supabase SQL Editor

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

-- Create fights table
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

-- Create rankings table
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

-- Insert sample data
INSERT INTO fighters (name, nickname, weight_class, record, reach, height, stance, style, ufc_ranking, is_active) VALUES
('Israel Adesanya', 'The Last Stylebender', 'Middleweight', '{"wins": 24, "losses": 3, "draws": 0}', 80.0, 76.0, 'Orthodox', 'Kickboxing', 1, true),
('Alex Pereira', 'Poatan', 'Light Heavyweight', '{"wins": 9, "losses": 2, "draws": 0}', 79.0, 76.0, 'Orthodox', 'Kickboxing', 1, true),
('Jon Jones', 'Bones', 'Heavyweight', '{"wins": 27, "losses": 1, "draws": 0}', 84.5, 76.0, 'Orthodox', 'Wrestling', 1, true),
('Kamaru Usman', 'The Nigerian Nightmare', 'Welterweight', '{"wins": 20, "losses": 4, "draws": 0}', 78.0, 72.0, 'Orthodox', 'Wrestling', 2, true),
('Charles Oliveira', 'Do Bronx', 'Lightweight', '{"wins": 34, "losses": 9, "draws": 0}', 74.0, 70.0, 'Orthodox', 'Brazilian Jiu-Jitsu', 1, true);

-- Insert sample event
INSERT INTO events (name, date, location, venue, broadcast_info, status) VALUES
('UFC 300: Pereira vs Hill', '2024-04-13T23:00:00Z', 'Las Vegas, Nevada', 'T-Mobile Arena', 'ESPN+ PPV', 'scheduled');

-- Insert sample rankings
INSERT INTO rankings (fighter_id, weight_class, rank_position, rank_type) 
SELECT id, weight_class, ufc_ranking, 'ufc' FROM fighters WHERE ufc_ranking IS NOT NULL; 