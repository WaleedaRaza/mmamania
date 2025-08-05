-- =====================================================
-- DESTROY AND REBUILD SCHEMAS SCRIPT
-- WARNING: This will DESTROY existing data
-- =====================================================

-- =====================================================
-- STEP 1: DESTROY EXISTING SCHEMAS
-- =====================================================

-- Drop existing tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS public.fights CASCADE;
DROP TABLE IF EXISTS public.rankings CASCADE;
DROP TABLE IF EXISTS public.fighters CASCADE;
DROP TABLE IF EXISTS public.events CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;

-- Drop any existing schemas
DROP SCHEMA IF EXISTS events_fights CASCADE;
DROP SCHEMA IF EXISTS rankings_fighters CASCADE;

-- =====================================================
-- STEP 2: CREATE CLEAN SCHEMAS
-- =====================================================

-- Create new schema for events and fights
CREATE SCHEMA events_fights;

-- Create events table in new schema
CREATE TABLE events_fights.events (
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
CREATE TABLE events_fights.fights (
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
CREATE INDEX idx_events_fights_events_date ON events_fights.events(date);
CREATE INDEX idx_events_fights_fights_event_id ON events_fights.fights(event_id);
CREATE INDEX idx_events_fights_fights_fighter1_name ON events_fights.fights(fighter1_name);
CREATE INDEX idx_events_fights_fights_fighter2_name ON events_fights.fights(fighter2_name);

-- Create new schema for rankings and fighters
CREATE SCHEMA rankings_fighters;

-- Create fighters table in new schema (only ranked fighters)
CREATE TABLE rankings_fighters.fighters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL UNIQUE,
    record VARCHAR, -- "W-L-D" format from UFC.com
    weight_class VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create rankings table in new schema
CREATE TABLE rankings_fighters.rankings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fighter_id UUID REFERENCES rankings_fighters.fighters(id) ON DELETE CASCADE,
    weight_class VARCHAR NOT NULL,
    rank_position INTEGER NOT NULL,
    rank_type VARCHAR NOT NULL CHECK (rank_type IN ('champion', 'contender')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_rankings_fighters_fighters_name ON rankings_fighters.fighters(name);
CREATE INDEX idx_rankings_fighters_fighters_weight_class ON rankings_fighters.fighters(weight_class);
CREATE INDEX idx_rankings_fighters_rankings_fighter_id ON rankings_fighters.rankings(fighter_id);
CREATE INDEX idx_rankings_fighters_rankings_weight_class ON rankings_fighters.rankings(weight_class);
CREATE INDEX idx_rankings_fighters_rankings_position ON rankings_fighters.rankings(rank_position);

-- =====================================================
-- STEP 3: MOVE TABLES TO PUBLIC SCHEMA
-- =====================================================

-- Move events table to public schema
ALTER TABLE events_fights.events SET SCHEMA public;

-- Move fights table to public schema
ALTER TABLE events_fights.fights SET SCHEMA public;

-- Move fighters table to public schema
ALTER TABLE rankings_fighters.fighters SET SCHEMA public;

-- Move rankings table to public schema
ALTER TABLE rankings_fighters.rankings SET SCHEMA public;

-- =====================================================
-- STEP 4: DROP EMPTY SCHEMAS
-- =====================================================

DROP SCHEMA events_fights;
DROP SCHEMA rankings_fighters;

-- =====================================================
-- STEP 5: VERIFICATION
-- =====================================================

-- Check that tables exist in public schema
SELECT 'TABLES CREATED IN PUBLIC SCHEMA:' as status;
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('events', 'fights', 'fighters', 'rankings')
ORDER BY table_name;

-- Check table structures
SELECT 'TABLE STRUCTURES:' as status;
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('events', 'fights', 'fighters', 'rankings')
ORDER BY table_name, ordinal_position;

-- Check that tables are empty (ready for new data)
SELECT 'CURRENT RECORD COUNTS (SHOULD BE 0):' as status;
SELECT 'events' as table_name, COUNT(*) as record_count FROM public.events
UNION ALL
SELECT 'fights' as table_name, COUNT(*) as record_count FROM public.fights
UNION ALL
SELECT 'fighters' as table_name, COUNT(*) as record_count FROM public.fighters
UNION ALL
SELECT 'rankings' as table_name, COUNT(*) as record_count FROM public.rankings;

-- =====================================================
-- STEP 6: READY FOR SCRAPERS
-- =====================================================

SELECT 'SCHEMAS DESTROYED AND REBUILT SUCCESSFULLY!' as status;
SELECT 'Ready for enhanced scrapers to populate clean data.' as next_step; 