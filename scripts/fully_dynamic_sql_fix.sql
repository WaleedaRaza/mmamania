-- Fully Dynamic SQL Fix for Event-Fight Distribution
-- This script distributes fights across ALL events dynamically

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

-- Step 4: Create a temporary table to help with distribution
-- This approach uses ROW_NUMBER() to distribute fights evenly

-- First, let's see how many valid events we have
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

-- Step 5: Dynamic distribution using ROW_NUMBER()
-- This assigns fights to events in a round-robin fashion

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

-- Step 6: Now distribute fights across all valid events using modulo
-- This is a more sophisticated approach that works for any number of events

-- Create a temporary table with fight assignments
WITH fight_assignments AS (
    SELECT 
        f.id as fight_id,
        e.id as event_id,
        e.name as event_name,
        ROW_NUMBER() OVER (ORDER BY f.created_at) as fight_number,
        COUNT(*) OVER () as total_fights,
        COUNT(*) OVER (PARTITION BY e.id) as events_count
    FROM fights f
    CROSS JOIN events e
    WHERE e.name IS NOT NULL 
    AND e.name != ''
    AND (
        e.name LIKE '%UFC%' OR 
        e.name LIKE '%Fight Night%' OR 
        e.name LIKE '%ESPN%' OR 
        e.name LIKE '%ABC%' OR
        e.name LIKE '%PPV%'
    )
),
valid_events AS (
    SELECT DISTINCT id, name
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
    ORDER BY name
),
event_assignments AS (
    SELECT 
        f.id as fight_id,
        ve.id as event_id,
        ve.name as event_name,
        ROW_NUMBER() OVER (ORDER BY f.created_at) as fight_number,
        (ROW_NUMBER() OVER (ORDER BY f.created_at) - 1) % (SELECT COUNT(*) FROM valid_events) as event_index
    FROM fights f
    CROSS JOIN valid_events ve
    WHERE ve.id = (
        SELECT id FROM valid_events 
        ORDER BY name 
        LIMIT 1 
        OFFSET (ROW_NUMBER() OVER (ORDER BY f.created_at) - 1) % (SELECT COUNT(*) FROM valid_events)
    )
)
UPDATE fights 
SET event_id = ea.event_id
FROM event_assignments ea
WHERE fights.id = ea.fight_id;

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

-- Alternative simpler approach: Round-robin distribution
-- This is easier to understand and implement

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
    WHERE ve.event_number = ((fn.fight_number - 1) % (SELECT COUNT(*) FROM valid_events)) + 1
)
FROM fight_numbers fn
WHERE fights.id = fn.id;
*/ 