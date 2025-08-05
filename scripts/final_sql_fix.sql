-- Final SQL Fix for Event-Fight Distribution
-- Run this in your Supabase SQL Editor to distribute fights across all events

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

-- Step 5: Reset all fights to the first valid event
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
-- This manually assigns fights to events in order, cycling through all events

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

-- For the fourth event
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
    OFFSET 3
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
    OFFSET 3 * (SELECT COUNT(*) FROM fights) / (SELECT COUNT(*) FROM events 
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

-- For the fifth event
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
    OFFSET 4
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
    OFFSET 4 * (SELECT COUNT(*) FROM fights) / (SELECT COUNT(*) FROM events 
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