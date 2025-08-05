-- Simple Working Event-Fight Distribution Fix
-- Run this in your Supabase SQL Editor

-- Step 1: See current state
SELECT 
    e.name as event_name,
    COUNT(f.id) as fight_count
FROM events e
LEFT JOIN fights f ON e.id = f.event_id
GROUP BY e.id, e.name
ORDER BY e.name;

-- Step 2: Get total fights
SELECT COUNT(*) as total_fights FROM fights;

-- Step 3: Get valid events
SELECT id, name FROM events 
WHERE name IS NOT NULL 
AND name != ''
AND (
    name LIKE '%UFC%' OR 
    name LIKE '%Fight Night%' OR 
    name LIKE '%ESPN%' OR 
    name LIKE '%ABC%' OR
    name LIKE '%PPV%'
)
ORDER BY name;

-- Step 4: Count valid events
SELECT COUNT(*) as valid_events_count FROM events 
WHERE name IS NOT NULL 
AND name != ''
AND (
    name LIKE '%UFC%' OR 
    name LIKE '%Fight Night%' OR 
    name LIKE '%ESPN%' OR 
    name LIKE '%ABC%' OR
    name LIKE '%PPV%'
);

-- Step 5: SIMPLE FIX - Assign fights to events one by one
-- First, get all fights and all valid events
WITH fight_events AS (
    SELECT 
        f.id as fight_id,
        e.id as event_id,
        e.name as event_name,
        ROW_NUMBER() OVER (ORDER BY f.created_at) as fight_number,
        ROW_NUMBER() OVER (ORDER BY e.name) as event_number,
        COUNT(*) OVER (PARTITION BY e.id) as total_events
    FROM fights f
    CROSS JOIN (
        SELECT id, name FROM events 
        WHERE name IS NOT NULL 
        AND name != ''
        AND (
            name LIKE '%UFC%' OR 
            name LIKE '%Fight Night%' OR 
            name LIKE '%ESPN%' OR 
            name LIKE '%ABC%' OR
            name LIKE '%PPV%'
        )
    ) e
)
UPDATE fights 
SET event_id = (
    SELECT fe.event_id 
    FROM fight_events fe 
    WHERE fe.fight_id = fights.id
    AND fe.event_number = ((fe.fight_number - 1) % fe.total_events) + 1
);

-- Step 6: Verify the new distribution
SELECT 
    e.name as event_name,
    COUNT(f.id) as fight_count
FROM events e
LEFT JOIN fights f ON e.id = f.event_id
WHERE e.name IS NOT NULL 
AND e.name != ''
AND (
    e.name LIKE '%UFC%' OR 
    e.name LIKE '%Fight Night%' OR 
    e.name LIKE '%ESPN%' OR 
    e.name LIKE '%ABC%' OR
    e.name LIKE '%PPV%'
)
GROUP BY e.id, e.name
ORDER BY e.name; 