-- Clean SQL Fix for Event-Fight Distribution
-- This script properly distributes fights across events

-- Step 1: First, let's see the current state
SELECT 
    e.name as event_name,
    COUNT(f.id) as fight_count
FROM events e
LEFT JOIN fights f ON e.id = f.event_id
WHERE e.name LIKE '%UFC 300%' OR e.name LIKE '%UFC 299%' OR e.name LIKE '%UFC 298%'
GROUP BY e.id, e.name
ORDER BY e.name;

-- Step 2: Get the total number of fights
SELECT COUNT(*) as total_fights FROM fights;

-- Step 3: Get the event IDs for our main events
SELECT id, name FROM events 
WHERE name LIKE '%UFC 300%' OR name LIKE '%UFC 299%' OR name LIKE '%UFC 298%'
ORDER BY name;

-- Step 4: Reset all fights to UFC 300 first (as a starting point)
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 300%' LIMIT 1);

-- Step 5: Distribute fights evenly across the 3 main events
-- This approach takes fights in order and assigns them to different events

-- For UFC 299 (assign every 3rd fight starting from fight #2)
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 299%' LIMIT 1)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / 3
    OFFSET (SELECT COUNT(*) FROM fights) / 3
);

-- For UFC 298 (assign every 3rd fight starting from fight #3)
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name LIKE '%UFC 298%' LIMIT 1)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / 3
    OFFSET 2 * (SELECT COUNT(*) FROM fights) / 3
);

-- Step 6: Verify the new distribution
SELECT 
    e.name as event_name,
    COUNT(f.id) as fight_count
FROM events e
LEFT JOIN fights f ON e.id = f.event_id
WHERE e.name LIKE '%UFC 300%' OR e.name LIKE '%UFC 299%' OR e.name LIKE '%UFC 298%'
GROUP BY e.id, e.name
ORDER BY e.name; 