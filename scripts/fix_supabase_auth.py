#!/usr/bin/env python3
"""
Fix Supabase Authentication
Test different authentication methods to resolve 401 errors
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test different Supabase authentication methods"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"🔍 Testing Supabase connection...")
    print(f"URL: {supabase_url}")
    print(f"Service Key: {'✅' if service_key else '❌'}")
    print(f"Anon Key: {'✅' if anon_key else '❌'}")
    
    # Test 1: Service Key with Bearer token
    print("\n🧪 Test 1: Service Key with Bearer token")
    headers1 = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    try:
        response = requests.get(f"{supabase_url}/rest/v1/fighters", headers=headers1)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Service Key with Bearer works!")
            return headers1
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Service Key without Bearer
    print("\n🧪 Test 2: Service Key without Bearer")
    headers2 = {
        'apikey': service_key,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    try:
        response = requests.get(f"{supabase_url}/rest/v1/fighters", headers=headers2)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Service Key without Bearer works!")
            return headers2
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Anon Key
    print("\n🧪 Test 3: Anon Key")
    headers3 = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    try:
        response = requests.get(f"{supabase_url}/rest/v1/fighters", headers=headers3)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Anon Key works!")
            return headers3
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def test_insert_fighter(headers):
    """Test inserting a fighter with working headers"""
    if not headers:
        print("❌ No working headers found")
        return False
    
    print("\n🧪 Testing fighter insertion...")
    
    test_fighter = {
        'name': 'Test Fighter',
        'nickname': 'Test',
        'weight_class': 'Middleweight',
        'record': {'wins': 10, 'losses': 2, 'draws': 0},
        'is_active': True
    }
    
    try:
        response = requests.post(
            f"{os.getenv('SUPABASE_URL')}/rest/v1/fighters",
            headers=headers,
            json=test_fighter
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Fighter insertion works!")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function to test and fix Supabase auth"""
    print("🚀 Testing Supabase Authentication...\n")
    
    # Test connection
    working_headers = test_supabase_connection()
    
    if working_headers:
        print(f"\n✅ Found working authentication method!")
        
        # Test insertion
        if test_insert_fighter(working_headers):
            print("\n🎉 Authentication fixed! Ready for production pipeline.")
            
            # Save working headers to file
            with open('working_headers.json', 'w') as f:
                json.dump(working_headers, f, indent=2)
            print("💾 Working headers saved to working_headers.json")
        else:
            print("\n❌ Insertion failed. Check RLS policies.")
    else:
        print("\n❌ No authentication method worked. Check credentials.")

if __name__ == "__main__":
    main() 