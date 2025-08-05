-- Simple Dynamic SQL Fix for Event-Fight Distribution
-- This script distributes fights across ALL events without complex window functions

-- Step 1: First, let's see the current state
SELECT 
    e.name as event_name,
    COUNT(f.id) as fight_count
FROM events e
LEFT JOIN fights f ON e.id = f.event_id
GROUP BY e.id, e.name
ORDER BY e.name;

-- Step 2: Get the total number of fights
SELECT COUNT(*) as total_fights FROM fights;

-- Step 3: Get all valid events (not just 3 hardcoded ones)
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

-- Step 4: Count how many valid events we have
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

-- Step 5: Simple approach - Reset all fights to first event, then distribute
-- First, reset all fights to the first valid event
UPDATE fights 
SET event_id = (
    SELECT id FROM events 
    WHERE name IS NOT NULL 
    AND name != ''
    AND (
        name LIKE '%UFC%' OR 
        name LIKE '%Fight Night%' OR 
        name LIKE '%ESPN%' OR 
        name LIKE '%ABC%' OR
        name LIKE '%PPV%'
    )
    ORDER BY name
    LIMIT 1
);

-- Step 6: Now distribute fights using a simple round-robin approach
-- This approach assigns fights to events in order, cycling through all events

-- Get all valid events with their row numbers
WITH valid_events AS (
    SELECT 
        id, 
        name, 
        ROW_NUMBER() OVER (ORDER BY name) as event_number,
        (SELECT COUNT(*) FROM events 
         WHERE name IS NOT NULL 
         AND name != ''
         AND (
             name LIKE '%UFC%' OR 
             name LIKE '%Fight Night%' OR 
             name LIKE '%ESPN%' OR 
             name LIKE '%ABC%' OR
             name LIKE '%PPV%'
         )) as total_events
    FROM events 
    WHERE name IS NOT NULL 
    AND name != ''
    AND (
        name LIKE '%UFC%' OR 
        name LIKE '%Fight Night%' OR 
        name LIKE '%ESPN%' OR 
        name LIKE '%ABC%' OR
        name LIKE '%PPV%'
    )
),
fight_numbers AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (ORDER BY created_at) as fight_number
    FROM fights
)
UPDATE fights 
SET event_id = (
    SELECT ve.id 
    FROM valid_events ve 
    WHERE ve.event_number = ((fn.fight_number - 1) % ve.total_events) + 1
)
FROM fight_numbers fn
WHERE fights.id = fn.id;

-- Step 7: Verify the new distribution
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

-- Alternative even simpler approach (if the above doesn't work):
-- This uses a basic modulo distribution without complex CTEs

/*
-- Step 1: Get all valid events into a temporary table
CREATE TEMP TABLE temp_valid_events AS
SELECT id, name, ROW_NUMBER() OVER (ORDER BY name) as event_number
FROM events 
WHERE name IS NOT NULL 
AND name != ''
AND (
    name LIKE '%UFC%' OR 
    name LIKE '%Fight Night%' OR 
    name LIKE '%ESPN%' OR 
    name LIKE '%ABC%' OR
    name LIKE '%PPV%'
);

-- Step 2: Update fights using simple modulo
UPDATE fights 
SET event_id = (
    SELECT id FROM temp_valid_events 
    WHERE event_number = ((ROW_NUMBER() OVER (ORDER BY fights.created_at) - 1) % (SELECT COUNT(*) FROM temp_valid_events)) + 1
);

-- Step 3: Clean up
DROP TABLE temp_valid_events;
*/ 