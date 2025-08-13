from dotenv import load_dotenv
import os
import requests
load_dotenv('.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

headers = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

# Test fight creation without the problematic fields
test_fight = {
    'event_id': 1,
    'weight_class': 'Flyweight',
    'status': 'completed',
    'result': {
        'method': 'Submission (face crank)',
        'round': '2',
        'time': '1:06'
    },
    'fighter1_name': 'Tatsuro Taira',
    'fighter2_name': 'Park Hyun-sung'
}

print(f'Testing simple fight creation...')

# First, let's check if we have any events
response = requests.get(f'{SUPABASE_URL}/rest/v1/events', headers=headers)
print(f'Events response: {response.status_code}')
if response.status_code == 200:
    events = response.json()
    print(f'Found {len(events)} events')
    if events:
        event_id = events[0]['id']
        test_fight['event_id'] = event_id
        print(f'Using event ID: {event_id}')
        
        # Try to create the fight
        response = requests.post(f'{SUPABASE_URL}/rest/v1/fights', headers=headers, json=test_fight)
        print(f'Fight creation response: {response.status_code}')
        print(f'Response text: {response.text}')
