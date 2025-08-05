-- Simple SQL Fix for Event-Fight Distribution
-- This script distributes fights evenly across events without hardcoding fighter names

-- Step 1: Get all events that should have fights
SELECT id, name FROM events 
WHERE name LIKE '%UFC 300%' OR name LIKE '%UFC 299%' OR name LIKE '%UFC 298%'
ORDER BY name;

-- Step 2: Get the current event_id that all fights are assigned to
SELECT event_id, COUNT(*) as fight_count 
FROM fights 
GROUP BY event_id;

-- Step 3: Create a temporary table to map fights to new events
-- This approach distributes fights evenly without hardcoding names

-- First, let's see how many fights we have total
SELECT COUNT(*) as total_fights FROM fights;

-- Step 4: Update fights to distribute them across 3 main events
-- This is a simple approach that takes every 3rd fight and assigns it to different events

-- For UFC 300 (first third of fights)
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 300%' LIMIT 1)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / 3
);

-- For UFC 299 (second third of fights)
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 299%' LIMIT 1)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / 3
    OFFSET (SELECT COUNT(*) FROM fights) / 3
);

-- For UFC 298 (remaining fights)
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 298%' LIMIT 1)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / 3
    OFFSET 2 * (SELECT COUNT(*) FROM fights) / 3
);

-- Step 5: Verify the new distribution
SELECT 
    e.name as event_name,
    COUNT(f.id) as fight_count
FROM events e
LEFT JOIN fights f ON e.id = f.event_id
WHERE e.name LIKE '%UFC 300%' OR e.name LIKE '%UFC 299%' OR e.name LIKE '%UFC 298%'
GROUP BY e.id, e.name
ORDER BY e.name;

-- Alternative approach: Simple random distribution
-- This distributes fights randomly across the 3 main events

/*
-- Reset all fights to the first event
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 300%' LIMIT 1);

-- Then randomly assign to other events
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 299%' LIMIT 1)
WHERE RANDOM() < 0.5;

UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 298%' LIMIT 1)
WHERE event_id = (SELECT id FROM events WHERE name LIKE '%UFC 300%' LIMIT 1)
AND RANDOM() < 0.5;
*/ 