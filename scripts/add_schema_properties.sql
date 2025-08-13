-- Add schema properties for winner identification and fight order
ALTER TABLE fights ADD COLUMN IF NOT EXISTS winner_id INTEGER;
ALTER TABLE fights ADD COLUMN IF NOT EXISTS is_main_event BOOLEAN DEFAULT FALSE;
ALTER TABLE fights ADD COLUMN IF NOT EXISTS fight_order INTEGER;

-- Add comments for clarity
COMMENT ON COLUMN fights.winner_id IS '1 for fighter1 (winner), 2 for fighter2 (winner)';
COMMENT ON COLUMN fights.is_main_event IS 'True if this is the main event fight';
COMMENT ON COLUMN fights.fight_order IS 'Order of the fight on the card (1 = main event)';
