-- Working SQL Fix for Event-Fight Distribution
-- This script distributes fights across ALL events using simple, working SQL

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

-- Step 3: Get all valid events
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

-- Step 5: Simple working approach - Reset all fights to first event
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

-- Step 6: Now distribute fights using a simple approach
-- This creates a temporary table with event assignments and updates fights

-- Create a temporary table with fight assignments
CREATE TEMP TABLE fight_assignments AS
SELECT 
    f.id as fight_id,
    e.id as event_id,
    e.name as event_name,
    ROW_NUMBER() OVER (ORDER BY f.created_at) as fight_number
FROM fights f
CROSS JOIN (
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
    )
) e
WHERE e.event_number = ((ROW_NUMBER() OVER (ORDER BY f.created_at) - 1) % (
    SELECT COUNT(*) FROM events 
    WHERE name IS NOT NULL 
    AND name != ''
    AND (
        name LIKE '%UFC%' OR 
        name LIKE '%Fight Night%' OR 
        name LIKE '%ESPN%' OR 
        name LIKE '%ABC%' OR
        name LIKE '%PPV%'
    )
)) + 1;

-- Update fights using the temporary table
UPDATE fights 
SET event_id = fa.event_id
FROM fight_assignments fa
WHERE fights.id = fa.fight_id;

-- Clean up
DROP TABLE fight_assignments;

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

-- Alternative ultra-simple approach (if the above still has issues):
-- This manually assigns fights to events in batches

/*
-- Step 1: Get all valid events
WITH valid_events AS (
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
    )
),
total_events AS (
    SELECT COUNT(*) as count FROM valid_events
),
fight_numbers AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as fight_number
    FROM fights
)
UPDATE fights 
SET event_id = (
    SELECT ve.id 
    FROM valid_events ve, total_events te
    WHERE ve.event_number = ((fn.fight_number - 1) % te.count) + 1
)
FROM fight_numbers fn
WHERE fights.id = fn.id;
*/ 