from dotenv import load_dotenv
import os
import requests
load_dotenv('.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

headers = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

# Add the missing schema properties
sql_commands = [
    "ALTER TABLE fights ADD COLUMN IF NOT EXISTS is_main_event BOOLEAN DEFAULT FALSE;",
    "ALTER TABLE fights ADD COLUMN IF NOT EXISTS fight_order INTEGER;",
    "ALTER TABLE fights ADD COLUMN IF NOT EXISTS winner_id INTEGER;"
]

print("Adding schema properties...")

for sql in sql_commands:
    print(f"Executing: {sql}")
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
        headers=headers,
        json={'query': sql}
    )
    print(f"Response: {response.status_code}")
    print(f"Text: {response.text}")
    print()

print("Schema update complete!")
