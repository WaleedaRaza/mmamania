-- =====================================================
-- CREATE CLEAN SCHEMAS IN PUBLIC SCHEMA
-- This will create tables directly in public schema
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

-- =====================================================
-- STEP 2: CREATE CLEAN TABLES IN PUBLIC SCHEMA
-- =====================================================

-- Create events table (Database 1: Wikipedia scraper)
CREATE TABLE public.events (
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

-- Create fights table with embedded fighter names (Database 1: Wikipedia scraper)
CREATE TABLE public.fights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES public.events(id) ON DELETE CASCADE,
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

-- Create fighters table (Database 2: UFC scraper - only ranked fighters)
CREATE TABLE public.fighters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL UNIQUE,
    record VARCHAR, -- "W-L-D" format from UFC.com
    weight_class VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create rankings table (Database 2: UFC scraper)
CREATE TABLE public.rankings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fighter_id UUID REFERENCES public.fighters(id) ON DELETE CASCADE,
    weight_class VARCHAR NOT NULL,
    rank_position INTEGER NOT NULL,
    rank_type VARCHAR NOT NULL CHECK (rank_type IN ('champion', 'contender')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- STEP 3: CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- Events indexes
CREATE INDEX idx_events_date ON public.events(date);
CREATE INDEX idx_events_name ON public.events(name);

-- Fights indexes
CREATE INDEX idx_fights_event_id ON public.fights(event_id);
CREATE INDEX idx_fights_fighter1_name ON public.fights(fighter1_name);
CREATE INDEX idx_fights_fighter2_name ON public.fights(fighter2_name);
CREATE INDEX idx_fights_weight_class ON public.fights(weight_class);

-- Fighters indexes
CREATE INDEX idx_fighters_name ON public.fighters(name);
CREATE INDEX idx_fighters_weight_class ON public.fighters(weight_class);

-- Rankings indexes
CREATE INDEX idx_rankings_fighter_id ON public.rankings(fighter_id);
CREATE INDEX idx_rankings_weight_class ON public.rankings(weight_class);
CREATE INDEX idx_rankings_position ON public.rankings(rank_position);

-- =====================================================
-- STEP 4: VERIFICATION
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

-- Check foreign key relationships
SELECT 'FOREIGN KEY RELATIONSHIPS:' as status;
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- =====================================================
-- STEP 5: READY FOR SCRAPERS
-- =====================================================

SELECT 'CLEAN SCHEMAS CREATED SUCCESSFULLY!' as status;
SELECT 'Database 1: events + fights (Wikipedia scraper)' as db1;
SELECT 'Database 2: fighters + rankings (UFC scraper)' as db2;
SELECT 'Ready for enhanced scrapers to populate clean data.' as next_step; 