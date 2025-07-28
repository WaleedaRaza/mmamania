#!/usr/bin/env python3
"""
Clear database tables to start fresh
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def clear_database():
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
    }
    
    print("🧹 Clearing database tables...")
    
    # Clear rankings first (due to foreign key constraints)
    print("🗑️ Clearing rankings...")
    response = requests.delete(f"{supabase_url}/rest/v1/rankings", headers=headers)
    if response.status_code == 200:
        print("✅ Rankings cleared")
    else:
        print(f"❌ Error clearing rankings: {response.status_code}")
    
    # Clear fights
    print("🗑️ Clearing fights...")
    response = requests.delete(f"{supabase_url}/rest/v1/fights", headers=headers)
    if response.status_code == 200:
        print("✅ Fights cleared")
    else:
        print(f"❌ Error clearing fights: {response.status_code}")
    
    # Clear fighters
    print("🗑️ Clearing fighters...")
    response = requests.delete(f"{supabase_url}/rest/v1/fighters", headers=headers)
    if response.status_code == 200:
        print("✅ Fighters cleared")
    else:
        print(f"❌ Error clearing fighters: {response.status_code}")
    
    # Clear events
    print("🗑️ Clearing events...")
    response = requests.delete(f"{supabase_url}/rest/v1/events", headers=headers)
    if response.status_code == 200:
        print("✅ Events cleared")
    else:
        print(f"❌ Error clearing events: {response.status_code}")
    
    print("🎉 Database cleared successfully!")

if __name__ == "__main__":
    clear_database() 