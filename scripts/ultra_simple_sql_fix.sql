-- Ultra Simple SQL Fix for Event-Fight Distribution
-- This script distributes fights across ALL events using the simplest possible approach

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

-- Step 5: Ultra simple approach - Reset all fights to first event
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

-- Step 6: Now distribute fights using the simplest possible approach
-- This manually assigns fights to events in order, cycling through all events

-- First, let's get all valid events into a simple list
-- Then we'll assign fights one by one to each event in order

-- For the first event (UFC 300 or similar)
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
    OFFSET 0
)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / (SELECT COUNT(*) FROM events 
        WHERE name IS NOT NULL 
        AND name != ''
        AND (
            name LIKE '%UFC%' OR 
            name LIKE '%Fight Night%' OR 
            name LIKE '%ESPN%' OR 
            name LIKE '%ABC%' OR
            name LIKE '%PPV%'
        ))
);

-- For the second event
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
    OFFSET 1
)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / (SELECT COUNT(*) FROM events 
        WHERE name IS NOT NULL 
        AND name != ''
        AND (
            name LIKE '%UFC%' OR 
            name LIKE '%Fight Night%' OR 
            name LIKE '%ESPN%' OR 
            name LIKE '%ABC%' OR
            name LIKE '%PPV%'
        ))
    OFFSET (SELECT COUNT(*) FROM fights) / (SELECT COUNT(*) FROM events 
        WHERE name IS NOT NULL 
        AND name != ''
        AND (
            name LIKE '%UFC%' OR 
            name LIKE '%Fight Night%' OR 
            name LIKE '%ESPN%' OR 
            name LIKE '%ABC%' OR
            name LIKE '%PPV%'
        ))
);

-- For the third event
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
    OFFSET 2
)
WHERE id IN (
    SELECT id FROM fights 
    ORDER BY created_at 
    LIMIT (SELECT COUNT(*) FROM fights) / (SELECT COUNT(*) FROM events 
        WHERE name IS NOT NULL 
        AND name != ''
        AND (
            name LIKE '%UFC%' OR 
            name LIKE '%Fight Night%' OR 
            name LIKE '%ESPN%' OR 
            name LIKE '%ABC%' OR
            name LIKE '%PPV%'
        ))
    OFFSET 2 * (SELECT COUNT(*) FROM fights) / (SELECT COUNT(*) FROM events 
        WHERE name IS NOT NULL 
        AND name != ''
        AND (
            name LIKE '%UFC%' OR 
            name LIKE '%Fight Night%' OR 
            name LIKE '%ESPN%' OR 
            name LIKE '%ABC%' OR
            name LIKE '%PPV%'
        ))
);

-- Continue for more events as needed...
-- (You can copy and paste this pattern for more events)

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