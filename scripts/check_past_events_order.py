#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
}

def main():
    # Fetch past events ordered by date desc
    r = requests.get(f"{SUPABASE_URL}/rest/v1/events?order=date.desc&select=id,name,date,location", headers=headers)
    r.raise_for_status()
    events = r.json()
    print(f"Total events: {len(events)}")
    print("Top 30 by date.desc:")
    for e in events[:30]:
        print(f"- {e.get('date')} | {e.get('name')} | {e.get('id')}")
    # Check for null or empty dates
    nulls = [e for e in events if not e.get('date')]
    if nulls:
        print(f"\nEvents with NULL date: {len(nulls)}")
        for e in nulls[:20]:
            print(f"NULL | {e.get('name')} | {e.get('id')}")

if __name__ == '__main__':
    main()