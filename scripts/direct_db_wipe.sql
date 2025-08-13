-- Direct Database Wipe for Events and Fights Tables
-- This script directly deletes all data from events and fights tables

-- First, delete all fights (due to foreign key constraints)
DELETE FROM fights;

-- Then delete all events
DELETE FROM events;

-- Verify the tables are empty
SELECT 'fights' as table_name, COUNT(*) as row_count FROM fights
UNION ALL
SELECT 'events' as table_name, COUNT(*) as row_count FROM events;

-- Reset the auto-increment sequences if they exist
-- Note: This is optional but helps keep the database clean
-- ALTER SEQUENCE IF EXISTS fights_id_seq RESTART WITH 1;
-- ALTER SEQUENCE IF EXISTS events_id_seq RESTART WITH 1; 