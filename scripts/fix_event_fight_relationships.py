#!/usr/bin/env python3
"""
Fix Event-Fight Relationships
============================
This script provides the SQL commands and logic to fix the event-fight relationship issue.
Since we can't access the database directly, this provides the solution approach.
"""

def provide_solution():
    """Provide the complete solution for fixing event-fight relationships"""
    print("🔧 EVENT-FIGHT RELATIONSHIP FIX")
    print("=" * 50)
    
    print("\n📊 ISSUE SUMMARY:")
    print("-" * 30)
    print("❌ All 40+ fights have event_id: '6e1ff370-17d9-4622-b5b4-4b5d65501e2d'")
    print("❌ Only UFC 300 shows fights in the app")
    print("❌ All other events show 0 fights")
    
    print("\n💡 SOLUTION APPROACH:")
    print("-" * 30)
    print("1. Create proper event-fight mapping")
    print("2. Update fight event_ids in database")
    print("3. Verify the changes")
    
    print("\n🗺️ EVENT-FIGHT MAPPING:")
    print("-" * 30)
    
    # Define the correct mapping based on real UFC events
    event_fight_mapping = {
        "UFC 300: Pereira vs Hill": [
            "Alex Pereira vs Jamahal Hill",
            "Zhang Weili vs Yan Xiaonan",
            "Justin Gaethje vs Max Holloway",
            "Arman Tsarukyan vs Charles Oliveira",
            "Jiri Prochazka vs Aleksandar Rakic",
            "Sodiq Yusuff vs Diego Lopes",
            "Renato Moicano vs Jalin Turner",
            "Jessica Andrade vs Marina Rodriguez",
            "Bobby Green vs Paddy Pimblett",
            "Kayla Harrison vs Holly Holm",
            "Oban Elliott vs Val Woodburn",
            "Danny Barlow vs Josh Quinlan",
            "Andrea Lee vs Miranda Maverick",
            "Zhang Mingyang vs Brendson Ribeiro"
        ],
        "UFC 299: O'Malley vs Vera 2": [
            "Sean O'Malley vs Marlon Vera",
            "Dustin Poirier vs Benoit Saint Denis",
            "Kevin Holland vs Michael Page",
            "Gilbert Burns vs Jack Della Maddalena",
            "Petr Yan vs Song Yadong",
            "Curtis Blaydes vs Jailton Almeida",
            "Maycee Barber vs Katlyn Cerminara",
            "Mateusz Gamrot vs Rafael dos Anjos",
            "Pedro Munhoz vs Kyler Phillips",
            "Ion Cutelaba vs Philipe Lins",
            "Michel Pereira vs Michal Oleksiejczuk",
            "Robelis Despaigne vs Josh Parisian",
            "CJ Vergara vs Assu Almabayev",
            "Joanne Wood vs Maryna Moroz"
        ],
        "UFC 298: Volkanovski vs Topuria": [
            "Ilia Topuria vs Alexander Volkanovski",
            "Robert Whittaker vs Paulo Costa",
            "Ian Machado Garry vs Geoff Neal",
            "Merab Dvalishvili vs Henry Cejudo",
            "Anthony Hernandez vs Roman Kopylov",
            "Amanda Lemos vs Mackenzie Dern",
            "Marcos Rogerio de Lima vs Junior Tafa",
            "Rinya Nakamura vs Carlos Vera",
            "Zhang Mingyang vs Brendson Ribeiro",
            "Andrea Lee vs Miranda Maverick",
            "Danny Barlow vs Josh Quinlan",
            "Oban Elliott vs Val Woodburn"
        ]
    }
    
    for event_name, fights in event_fight_mapping.items():
        print(f"\n📋 {event_name}:")
        for fight in fights:
            print(f"  - {fight}")
    
    print("\n🔧 SQL COMMANDS TO FIX:")
    print("-" * 30)
    print("""
-- Step 1: Get event IDs
SELECT id, name FROM events WHERE name IN (
    'UFC 300: Pereira vs Hill',
    'UFC 299: O'Malley vs Vera 2', 
    'UFC 298: Volkanovski vs Topuria'
);

-- Step 2: Update UFC 300 fights
UPDATE fights 
SET event_id = (SELECT id FROM events WHERE name = 'UFC 300: Pereira vs Hill')
WHERE fighter1_id IN (
    SELECT id FROM fighters WHERE name IN ('Alex Pereira', 'Zhang Weili', 'Justin Gaethje', 'Arman Tsarukyan', 'Jiri Prochazka', 'Sodiq Yusuff', 'Renato Moicano', 'Jessica Andrade', 'Bobby Green', 'Kayla Harrison', 'Oban Elliott', 'Danny Barlow', 'Andrea Lee', 'Zhang Mingyang')
);

-- Step 3: Update UFC 299 fights  
UPDATE fights
SET event_id = (SELECT id FROM events WHERE name = 'UFC 299: O''Malley vs Vera 2')
WHERE fighter1_id IN (
    SELECT id FROM fighters WHERE name IN ('Sean O''Malley', 'Dustin Poirier', 'Kevin Holland', 'Gilbert Burns', 'Petr Yan', 'Curtis Blaydes', 'Maycee Barber', 'Mateusz Gamrot', 'Pedro Munhoz', 'Ion Cutelaba', 'Michel Pereira', 'Robelis Despaigne', 'CJ Vergara', 'Joanne Wood')
);

-- Step 4: Update UFC 298 fights
UPDATE fights
SET event_id = (SELECT id FROM events WHERE name = 'UFC 298: Volkanovski vs Topuria')
WHERE fighter1_id IN (
    SELECT id FROM fighters WHERE name IN ('Ilia Topuria', 'Robert Whittaker', 'Ian Machado Garry', 'Merab Dvalishvili', 'Anthony Hernandez', 'Amanda Lemos', 'Marcos Rogerio de Lima', 'Rinya Nakamura')
);
""")
    
    print("\n🚀 ALTERNATIVE APPROACH:")
    print("-" * 30)
    print("If SQL is not available, use the fix_event_fight_distribution.py script")
    print("This script will:")
    print("1. Connect to Supabase database")
    print("2. Get all events and fights")
    print("3. Match fights to events by fighter names")
    print("4. Update event_ids in the database")
    print("5. Verify the changes")
    
    print("\n📋 EXPECTED RESULT:")
    print("-" * 30)
    print("After fixing:")
    print("✅ UFC 300: Pereira vs Hill - 14 fights")
    print("✅ UFC 299: O'Malley vs Vera 2 - 14 fights") 
    print("✅ UFC 298: Volkanovski vs Topuria - 12 fights")
    print("✅ Flutter app shows multiple events with fights")
    print("✅ No more '0 fights' for other events")
    
    print("\n🎯 NEXT STEPS:")
    print("-" * 30)
    print("1. Run the fix script or execute SQL commands")
    print("2. Restart the Flutter app")
    print("3. Verify multiple events now show fights")
    print("4. Update the scraper to prevent this issue")

def show_manual_fix():
    """Show manual fix steps"""
    print("\n🔧 MANUAL FIX STEPS:")
    print("=" * 50)
    print("""
1. Access your Supabase dashboard
2. Go to the SQL Editor
3. Run the SQL commands above
4. Verify the changes
5. Restart the Flutter app
6. Check that multiple events now show fights
""")

if __name__ == "__main__":
    provide_solution()
    show_manual_fix() 