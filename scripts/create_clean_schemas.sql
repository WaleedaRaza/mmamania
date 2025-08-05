-- =====================================================
-- CLEAN SCHEMA CREATION SCRIPT
-- Creates new schemas without touching existing data
-- =====================================================

-- =====================================================
-- DATABASE 1: EVENTS & FIGHTS (Wikipedia Scraper)
-- =====================================================

-- Create new schema for events and fights
CREATE SCHEMA IF NOT EXISTS events_fights;

-- Create events table in new schema
CREATE TABLE IF NOT EXISTS events_fights.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    date TIMESTAMPTZ,
    location VARCHAR,
    venue VARCHAR,
    broadcast_info VARCHAR,
    status VARCHAR DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create fights table in new schema with embedded fighter names
CREATE TABLE IF NOT EXISTS events_fights.fights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events_fights.events(id) ON DELETE CASCADE,
    weight_class VARCHAR,
    status VARCHAR DEFAULT 'completed',
    date TIMESTAMPTZ,
    result JSONB, -- Keep existing JSONB structure for fight results
    odds JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- NEW: Embedded fighter data (just names, no records)
    fighter1_name VARCHAR,
    fighter2_name VARCHAR
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_fights_events_date ON events_fights.events(date);
CREATE INDEX IF NOT EXISTS idx_events_fights_fights_event_id ON events_fights.fights(event_id);
CREATE INDEX IF NOT EXISTS idx_events_fights_fights_fighter1_name ON events_fights.fights(fighter1_name);
CREATE INDEX IF NOT EXISTS idx_events_fights_fights_fighter2_name ON events_fights.fights(fighter2_name);

-- =====================================================
-- DATABASE 2: RANKINGS & FIGHTER RECORDS (UFC Scraper)
-- =====================================================

-- Create new schema for rankings and fighters
CREATE SCHEMA IF NOT EXISTS rankings_fighters;

-- Create fighters table in new schema (only ranked fighters)
CREATE TABLE IF NOT EXISTS rankings_fighters.fighters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL UNIQUE,
    record VARCHAR, -- "W-L-D" format from UFC.com
    weight_class VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create rankings table in new schema
CREATE TABLE IF NOT EXISTS rankings_fighters.rankings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fighter_id UUID REFERENCES rankings_fighters.fighters(id) ON DELETE CASCADE,
    weight_class VARCHAR NOT NULL,
    rank_position INTEGER NOT NULL,
    rank_type VARCHAR NOT NULL CHECK (rank_type IN ('champion', 'contender')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_rankings_fighters_fighters_name ON rankings_fighters.fighters(name);
CREATE INDEX IF NOT EXISTS idx_rankings_fighters_fighters_weight_class ON rankings_fighters.fighters(weight_class);
CREATE INDEX IF NOT EXISTS idx_rankings_fighters_rankings_fighter_id ON rankings_fighters.rankings(fighter_id);
CREATE INDEX IF NOT EXISTS idx_rankings_fighters_rankings_weight_class ON rankings_fighters.rankings(weight_class);
CREATE INDEX IF NOT EXISTS idx_rankings_fighters_rankings_position ON rankings_fighters.rankings(rank_position);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if schemas were created
SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('events_fights', 'rankings_fighters');

-- Check if tables were created
SELECT 
    table_schema,
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_schema IN ('events_fights', 'rankings_fighters')
ORDER BY table_schema, table_name, ordinal_position;

-- =====================================================
-- MIGRATION HELPER FUNCTIONS
-- =====================================================

-- Function to migrate events data
CREATE OR REPLACE FUNCTION migrate_events_to_new_schema()
RETURNS INTEGER AS $$
DECLARE
    migrated_count INTEGER;
BEGIN
    INSERT INTO events_fights.events (id, name, date, location, venue, broadcast_info, status, created_at, updated_at)
    SELECT id, name, date, location, venue, broadcast_info, status, created_at, updated_at
    FROM public.events
    ON CONFLICT (id) DO NOTHING;
    
    GET DIAGNOSTICS migrated_count = ROW_COUNT;
    RETURN migrated_count;
END;
$$ LANGUAGE plpgsql;

-- Function to migrate fights data (without fighter IDs)
CREATE OR REPLACE FUNCTION migrate_fights_to_new_schema()
RETURNS INTEGER AS $$
DECLARE
    migrated_count INTEGER;
BEGIN
    INSERT INTO events_fights.fights (id, event_id, weight_class, status, date, result, odds, created_at, updated_at, fighter1_name, fighter2_name)
    SELECT 
        f.id,
        f.event_id,
        f.weight_class,
        f.status,
        f.date,
        f.result,
        f.odds,
        f.created_at,
        f.updated_at,
        f1.name as fighter1_name,
        f2.name as fighter2_name
    FROM public.fights f
    LEFT JOIN public.fighters f1 ON f.fighter1_id = f1.id
    LEFT JOIN public.fighters f2 ON f.fighter2_id = f2.id
    ON CONFLICT (id) DO NOTHING;
    
    GET DIAGNOSTICS migrated_count = ROW_COUNT;
    RETURN migrated_count;
END;
$$ LANGUAGE plpgsql;

-- Function to migrate ranked fighters only
CREATE OR REPLACE FUNCTION migrate_ranked_fighters_to_new_schema()
RETURNS INTEGER AS $$
DECLARE
    migrated_count INTEGER;
BEGIN
    INSERT INTO rankings_fighters.fighters (id, name, record, weight_class, created_at, updated_at)
    SELECT DISTINCT
        f.id,
        f.name,
        f.record,
        f.weight_class,
        f.created_at,
        f.updated_at
    FROM public.fighters f
    INNER JOIN public.rankings r ON f.id = r.fighter_id
    ON CONFLICT (name) DO NOTHING;
    
    GET DIAGNOSTICS migrated_count = ROW_COUNT;
    RETURN migrated_count;
END;
$$ LANGUAGE plpgsql;

-- Function to migrate rankings
CREATE OR REPLACE FUNCTION migrate_rankings_to_new_schema()
RETURNS INTEGER AS $$
DECLARE
    migrated_count INTEGER;
BEGIN
    INSERT INTO rankings_fighters.rankings (id, fighter_id, weight_class, rank_position, rank_type, created_at, updated_at)
    SELECT 
        r.id,
        r.fighter_id,
        r.weight_class,
        r.rank_position,
        r.rank_type,
        r.created_at,
        r.updated_at
    FROM public.rankings r
    INNER JOIN rankings_fighters.fighters nf ON r.fighter_id = nf.id
    ON CONFLICT (id) DO NOTHING;
    
    GET DIAGNOSTICS migrated_count = ROW_COUNT;
    RETURN migrated_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- CLEANUP FUNCTIONS (USE WITH CAUTION)
-- =====================================================

-- Function to backup and drop old tables (USE WITH CAUTION)
CREATE OR REPLACE FUNCTION backup_and_cleanup_old_tables()
RETURNS VOID AS $$
BEGIN
    -- Create backup tables
    CREATE TABLE IF NOT EXISTS backup_events AS SELECT * FROM public.events;
    CREATE TABLE IF NOT EXISTS backup_fights AS SELECT * FROM public.fights;
    CREATE TABLE IF NOT EXISTS backup_fighters AS SELECT * FROM public.fighters;
    CREATE TABLE IF NOT EXISTS backup_rankings AS SELECT * FROM public.rankings;
    
    -- Rename old tables to backup
    ALTER TABLE public.events RENAME TO old_events;
    ALTER TABLE public.fights RENAME TO old_fights;
    ALTER TABLE public.fighters RENAME TO old_fighters;
    ALTER TABLE public.rankings RENAME TO old_rankings;
    
    -- Rename new tables to main names
    ALTER TABLE events_fights.events RENAME TO events;
    ALTER TABLE events_fights.fights RENAME TO fights;
    ALTER TABLE rankings_fighters.fighters RENAME TO fighters;
    ALTER TABLE rankings_fighters.rankings RENAME TO rankings;
    
    -- Move tables to public schema
    ALTER TABLE events SET SCHEMA public;
    ALTER TABLE fights SET SCHEMA public;
    ALTER TABLE fighters SET SCHEMA public;
    ALTER TABLE rankings SET SCHEMA public;
    
    RAISE NOTICE 'Old tables backed up and new tables activated. Old tables are: old_events, old_fights, old_fighters, old_rankings';
END;
$$ LANGUAGE plpgsql; 