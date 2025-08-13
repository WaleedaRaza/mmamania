-- Add new columns to fights table for enhanced fight data
-- This script adds columns for winner/loser names, fight order, and additional fight details

-- Add winner_name column
ALTER TABLE fights ADD COLUMN IF NOT EXISTS winner_name TEXT;

-- Add loser_name column  
ALTER TABLE fights ADD COLUMN IF NOT EXISTS loser_name TEXT;

-- Add fight_order column (integer to track fight sequence)
ALTER TABLE fights ADD COLUMN IF NOT EXISTS fight_order INTEGER;

-- Add is_main_event column (boolean)
ALTER TABLE fights ADD COLUMN IF NOT EXISTS is_main_event BOOLEAN DEFAULT FALSE;

-- Add is_co_main_event column (boolean)
ALTER TABLE fights ADD COLUMN IF NOT EXISTS is_co_main_event BOOLEAN DEFAULT FALSE;

-- Add method column (text for submission, KO, decision, etc.)
ALTER TABLE fights ADD COLUMN IF NOT EXISTS method TEXT;

-- Add round column (integer for which round the fight ended)
ALTER TABLE fights ADD COLUMN IF NOT EXISTS round INTEGER;

-- Add time column (text for time in round, e.g., "2:34")
ALTER TABLE fights ADD COLUMN IF NOT EXISTS "time" TEXT;

-- Add notes column (text for additional fight notes)
ALTER TABLE fights ADD COLUMN IF NOT EXISTS notes TEXT;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_fights_winner_name ON fights(winner_name);
CREATE INDEX IF NOT EXISTS idx_fights_loser_name ON fights(loser_name);
CREATE INDEX IF NOT EXISTS idx_fights_fight_order ON fights(fight_order);
CREATE INDEX IF NOT EXISTS idx_fights_is_main_event ON fights(is_main_event);
CREATE INDEX IF NOT EXISTS idx_fights_is_co_main_event ON fights(is_co_main_event);

-- Add a trigger to automatically set fight_order if not provided
CREATE OR REPLACE FUNCTION set_fight_order()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fight_order IS NULL THEN
        -- Get the next fight order for this event
        SELECT COALESCE(MAX(fight_order), 0) + 1 
        INTO NEW.fight_order 
        FROM fights 
        WHERE event_id = NEW.event_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
DROP TRIGGER IF EXISTS trigger_set_fight_order ON fights;
CREATE TRIGGER trigger_set_fight_order
    BEFORE INSERT ON fights
    FOR EACH ROW
    EXECUTE FUNCTION set_fight_order();

-- Create a view for fight results
CREATE OR REPLACE VIEW fight_results AS
SELECT 
    f.id,
    f.event_id,
    e.name as event_name,
    f.winner_name,
    f.loser_name,
    f.fight_order,
    f.is_main_event,
    f.is_co_main_event,
    f.method,
    f.round,
    f."time",
    f.weight_class,
    f.result,
    f.status,
    f.date,
    f.notes
FROM fights f
JOIN events e ON f.event_id = e.id
ORDER BY f.event_id, f.fight_order;

-- Create a function to get fight card for an event
CREATE OR REPLACE FUNCTION get_fight_card(event_uuid UUID)
RETURNS TABLE (
    fight_id UUID,
    winner_name TEXT,
    loser_name TEXT,
    fight_order INTEGER,
    is_main_event BOOLEAN,
    is_co_main_event BOOLEAN,
    method TEXT,
    round INTEGER,
    "time" TEXT,
    weight_class TEXT,
    result TEXT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.winner_name,
        f.loser_name,
        f.fight_order,
        f.is_main_event,
        f.is_co_main_event,
        f.method,
        f.round,
        f."time",
        f.weight_class,
        f.result,
        f.status
    FROM fights f
    WHERE f.event_id = event_uuid
    ORDER BY f.fight_order;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get event summary
CREATE OR REPLACE FUNCTION get_event_summary(event_uuid UUID)
RETURNS TABLE (
    event_name TEXT,
    event_date DATE,
    total_fights INTEGER,
    main_event_winner TEXT,
    main_event_loser TEXT,
    main_event_method TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.name,
        e.date,
        COUNT(f.id)::INTEGER as total_fights,
        f.winner_name,
        f.loser_name,
        f.method
    FROM events e
    LEFT JOIN fights f ON e.id = f.event_id
    WHERE e.id = event_uuid
    AND f.is_main_event = TRUE
    GROUP BY e.name, e.date, f.winner_name, f.loser_name, f.method;
END;
$$ LANGUAGE plpgsql;

-- Add comments to document the new columns
COMMENT ON COLUMN fights.winner_name IS 'Name of the winning fighter';
COMMENT ON COLUMN fights.loser_name IS 'Name of the losing fighter';
COMMENT ON COLUMN fights.fight_order IS 'Order of the fight in the event (1 = main event)';
COMMENT ON COLUMN fights.is_main_event IS 'Whether this is the main event';
COMMENT ON COLUMN fights.is_co_main_event IS 'Whether this is the co-main event';
COMMENT ON COLUMN fights.method IS 'Method of victory (Submission, KO, Decision, etc.)';
COMMENT ON COLUMN fights.round IS 'Round in which the fight ended';
COMMENT ON COLUMN fights."time" IS 'Time in the round when the fight ended';
COMMENT ON COLUMN fights.notes IS 'Additional notes about the fight';

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'fights' 
AND column_name IN ('winner_name', 'loser_name', 'fight_order', 'is_main_event', 'is_co_main_event', 'method', 'round', '"time"', 'notes')
ORDER BY column_name; 