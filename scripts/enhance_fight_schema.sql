-- Enhance Fight Schema to Support Winners, Losers, and Fight Order
-- This script adds new columns to the fights table to properly track fight results

-- Add new columns to the fights table
ALTER TABLE fights 
ADD COLUMN IF NOT EXISTS winner_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS loser_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS fight_order INTEGER,
ADD COLUMN IF NOT EXISTS is_main_event BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_co_main_event BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS weight_class VARCHAR(100),
ADD COLUMN IF NOT EXISTS method VARCHAR(255),
ADD COLUMN IF NOT EXISTS round INTEGER,
ADD COLUMN IF NOT EXISTS time VARCHAR(50),
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_fights_winner_name ON fights(winner_name);
CREATE INDEX IF NOT EXISTS idx_fights_loser_name ON fights(loser_name);
CREATE INDEX IF NOT EXISTS idx_fights_order ON fights(fight_order);
CREATE INDEX IF NOT EXISTS idx_fights_main_event ON fights(is_main_event);
CREATE INDEX IF NOT EXISTS idx_fights_weight_class ON fights(weight_class);

-- Add a constraint to ensure fight_order is positive
ALTER TABLE fights 
ADD CONSTRAINT IF NOT EXISTS check_fight_order_positive 
CHECK (fight_order > 0);

-- Add a constraint to ensure only one main event per event
ALTER TABLE fights 
ADD CONSTRAINT IF NOT EXISTS unique_main_event_per_event 
UNIQUE (event_id, is_main_event) 
WHERE is_main_event = TRUE;

-- Add a constraint to ensure only one co-main event per event
ALTER TABLE fights 
ADD CONSTRAINT IF NOT EXISTS unique_co_main_event_per_event 
UNIQUE (event_id, is_co_main_event) 
WHERE is_co_main_event = TRUE;

-- Create a view for easier querying of fight results
CREATE OR REPLACE VIEW fight_results AS
SELECT 
    f.id,
    f.event_id,
    e.title as event_title,
    e.date as event_date,
    f.winner_name,
    f.loser_name,
    f.fight_order,
    f.is_main_event,
    f.is_co_main_event,
    f.weight_class,
    f.method,
    f.round,
    f.time,
    f.notes,
    f.created_at,
    f.updated_at
FROM fights f
JOIN events e ON f.event_id = e.id
ORDER BY e.date DESC, f.fight_order ASC;

-- Create a function to automatically set fight order based on position in event
CREATE OR REPLACE FUNCTION set_fight_order()
RETURNS TRIGGER AS $$
BEGIN
    -- If fight_order is not set, set it based on the number of fights in the event
    IF NEW.fight_order IS NULL THEN
        SELECT COALESCE(MAX(fight_order), 0) + 1 
        INTO NEW.fight_order 
        FROM fights 
        WHERE event_id = NEW.event_id;
    END IF;
    
    -- Set main event flag based on fight order
    IF NEW.fight_order = 1 THEN
        NEW.is_main_event = TRUE;
    ELSIF NEW.fight_order = 2 THEN
        NEW.is_co_main_event = TRUE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically set fight order
DROP TRIGGER IF EXISTS trigger_set_fight_order ON fights;
CREATE TRIGGER trigger_set_fight_order
    BEFORE INSERT ON fights
    FOR EACH ROW
    EXECUTE FUNCTION set_fight_order();

-- Add comments to document the new columns
COMMENT ON COLUMN fights.winner_name IS 'Name of the fighter who won the fight';
COMMENT ON COLUMN fights.loser_name IS 'Name of the fighter who lost the fight';
COMMENT ON COLUMN fights.fight_order IS 'Order of the fight on the card (1 = main event)';
COMMENT ON COLUMN fights.is_main_event IS 'Whether this fight is the main event';
COMMENT ON COLUMN fights.is_co_main_event IS 'Whether this fight is the co-main event';
COMMENT ON COLUMN fights.weight_class IS 'Weight class of the fight';
COMMENT ON COLUMN fights.method IS 'Method of victory (KO, Submission, Decision, etc.)';
COMMENT ON COLUMN fights.round IS 'Round in which the fight ended';
COMMENT ON COLUMN fights.time IS 'Time in the round when the fight ended';
COMMENT ON COLUMN fights.notes IS 'Additional notes about the fight';

-- Create a function to get fight card for an event
CREATE OR REPLACE FUNCTION get_fight_card(event_id_param INTEGER)
RETURNS TABLE (
    fight_id INTEGER,
    winner_name VARCHAR(255),
    loser_name VARCHAR(255),
    fight_order INTEGER,
    is_main_event BOOLEAN,
    is_co_main_event BOOLEAN,
    weight_class VARCHAR(100),
    method VARCHAR(255),
    round INTEGER,
    time VARCHAR(50)
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
        f.weight_class,
        f.method,
        f.round,
        f.time
    FROM fights f
    WHERE f.event_id = event_id_param
    ORDER BY f.fight_order ASC;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get event summary with fight count
CREATE OR REPLACE FUNCTION get_event_summary()
RETURNS TABLE (
    event_id INTEGER,
    event_title VARCHAR(255),
    event_date DATE,
    total_fights INTEGER,
    main_event_winner VARCHAR(255),
    main_event_loser VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.title,
        e.date,
        COUNT(f.id)::INTEGER as total_fights,
        f_me.winner_name as main_event_winner,
        f_me.loser_name as main_event_loser
    FROM events e
    LEFT JOIN fights f ON e.id = f.event_id
    LEFT JOIN fights f_me ON e.id = f_me.event_id AND f_me.is_main_event = TRUE
    GROUP BY e.id, e.title, e.date, f_me.winner_name, f_me.loser_name
    ORDER BY e.date DESC;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT SELECT ON fight_results TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_fight_card(INTEGER) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_event_summary() TO anon, authenticated;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE '✅ Fight schema enhanced successfully!';
    RAISE NOTICE 'New columns added: winner_name, loser_name, fight_order, is_main_event, is_co_main_event, weight_class, method, round, time, notes';
    RAISE NOTICE 'New views created: fight_results';
    RAISE NOTICE 'New functions created: get_fight_card(), get_event_summary()';
END $$; 