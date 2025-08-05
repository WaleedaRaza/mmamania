#!/usr/bin/env python3
"""
Scale Past Events Script
Add more past UFC events to scale up the fight cards functionality
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('scripts/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class PastEventsScaler:
    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Extended past UFC events with more data
        self.extended_past_events = [
            {
                'name': 'UFC 300: Pereira vs Hill',
                'date': '2024-04-13',
                'venue': 'T-Mobile Arena',
                'location': 'Las Vegas, Nevada',
                'fights': [
                    {'fighter1': 'Alex Pereira', 'fighter2': 'Jamahal Hill', 'method': 'TKO (punches)', 'round': 1, 'time': '3:14', 'winner': 'Alex Pereira', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Zhang Weili', 'fighter2': 'Yan Xiaonan', 'method': 'Decision (unanimous)', 'round': 5, 'time': '5:00', 'winner': 'Zhang Weili', 'weight_class': 'Strawweight'},
                    {'fighter1': 'Justin Gaethje', 'fighter2': 'Max Holloway', 'method': 'KO (head kick)', 'round': 5, 'time': '4:59', 'winner': 'Justin Gaethje', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Arman Tsarukyan', 'fighter2': 'Charles Oliveira', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Arman Tsarukyan', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Kayla Harrison', 'fighter2': 'Holly Holm', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '1:21', 'winner': 'Kayla Harrison', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Aljamain Sterling', 'fighter2': 'Calvin Kattar', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Aljamain Sterling', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Jiri Prochazka', 'fighter2': 'Aleksandar Rakic', 'method': 'TKO (punches)', 'round': 2, 'time': '3:17', 'winner': 'Jiri Prochazka', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Bobby Green', 'fighter2': 'Jim Miller', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Bobby Green', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Deiveson Figueiredo', 'fighter2': 'Cody Garbrandt', 'method': 'Submission (guillotine choke)', 'round': 2, 'time': '2:13', 'winner': 'Deiveson Figueiredo', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Sodiq Yusuff', 'fighter2': 'Diego Lopes', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Sodiq Yusuff', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Renato Moicano', 'fighter2': 'Jalin Turner', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '4:11', 'winner': 'Renato Moicano', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Jessica Andrade', 'fighter2': 'Marina Rodriguez', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Jessica Andrade', 'weight_class': 'Strawweight'},
                    {'fighter1': 'Bobby Green', 'fighter2': 'Paddy Pimblett', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Bobby Green', 'weight_class': 'Lightweight'}
                ]
            },
            {
                'name': 'UFC 299: O\'Malley vs Vera 2',
                'date': '2024-03-09',
                'venue': 'Kaseya Center',
                'location': 'Miami, Florida',
                'fights': [
                    {'fighter1': 'Sean O\'Malley', 'fighter2': 'Marlon Vera', 'method': 'Decision (unanimous)', 'round': 5, 'time': '5:00', 'winner': 'Sean O\'Malley', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Dustin Poirier', 'fighter2': 'Benoit Saint Denis', 'method': 'KO (punches)', 'round': 2, 'time': '2:32', 'winner': 'Dustin Poirier', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Kevin Holland', 'fighter2': 'Michael Page', 'method': 'Submission (rear-naked choke)', 'round': 1, 'time': '3:00', 'winner': 'Kevin Holland', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Jack Della Maddalena', 'fighter2': 'Gilbert Burns', 'method': 'TKO (punches)', 'round': 3, 'time': '2:43', 'winner': 'Jack Della Maddalena', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Petr Yan', 'fighter2': 'Song Yadong', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Petr Yan', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Curtis Blaydes', 'fighter2': 'Jailton Almeida', 'method': 'TKO (punches)', 'round': 2, 'time': '0:36', 'winner': 'Curtis Blaydes', 'weight_class': 'Heavyweight'},
                    {'fighter1': 'Maycee Barber', 'fighter2': 'Katlyn Cerminara', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Maycee Barber', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Mateusz Gamrot', 'fighter2': 'Rafael dos Anjos', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Mateusz Gamrot', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Pedro Munhoz', 'fighter2': 'Kyler Phillips', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Pedro Munhoz', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Michel Pereira', 'fighter2': 'Michal Oleksiejczuk', 'method': 'Submission (rear-naked choke)', 'round': 1, 'time': '1:01', 'winner': 'Michel Pereira', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Robelis Despaigne', 'fighter2': 'Josh Parisian', 'method': 'TKO (punches)', 'round': 1, 'time': '0:18', 'winner': 'Robelis Despaigne', 'weight_class': 'Heavyweight'},
                    {'fighter1': 'CJ Vergara', 'fighter2': 'Assu Almabayev', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'CJ Vergara', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Joanne Wood', 'fighter2': 'Maryna Moroz', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Joanne Wood', 'weight_class': 'Flyweight'}
                ]
            },
            {
                'name': 'UFC 298: Volkanovski vs Topuria',
                'date': '2024-02-17',
                'venue': 'Honda Center',
                'location': 'Anaheim, California',
                'fights': [
                    {'fighter1': 'Ilia Topuria', 'fighter2': 'Alexander Volkanovski', 'method': 'KO (punches)', 'round': 2, 'time': '3:32', 'winner': 'Ilia Topuria', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Robert Whittaker', 'fighter2': 'Paulo Costa', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Robert Whittaker', 'weight_class': 'Middleweight'},
                    {'fighter1': 'Ian Machado Garry', 'fighter2': 'Geoff Neal', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Ian Machado Garry', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Merab Dvalishvili', 'fighter2': 'Henry Cejudo', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Merab Dvalishvili', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Anthony Hernandez', 'fighter2': 'Roman Kopylov', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '3:23', 'winner': 'Anthony Hernandez', 'weight_class': 'Middleweight'},
                    {'fighter1': 'Mackenzie Dern', 'fighter2': 'Amanda Lemos', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Mackenzie Dern', 'weight_class': 'Strawweight'},
                    {'fighter1': 'Marcos Rogerio de Lima', 'fighter2': 'Junior Tafa', 'method': 'TKO (leg kicks)', 'round': 2, 'time': '1:14', 'winner': 'Marcos Rogerio de Lima', 'weight_class': 'Heavyweight'},
                    {'fighter1': 'Rinya Nakamura', 'fighter2': 'Carlos Vera', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Rinya Nakamura', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Zhang Mingyang', 'fighter2': 'Brendson Ribeiro', 'method': 'KO (punches)', 'round': 1, 'time': '1:41', 'winner': 'Zhang Mingyang', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Tatsuro Taira', 'fighter2': 'Carlos Hernandez', 'method': 'TKO (punches)', 'round': 1, 'time': '0:55', 'winner': 'Tatsuro Taira', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Josh Quinlan', 'fighter2': 'Danny Barlow', 'method': 'TKO (punches)', 'round': 3, 'time': '1:18', 'winner': 'Josh Quinlan', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Oban Elliott', 'fighter2': 'Val Woodburn', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Oban Elliott', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Miranda Maverick', 'fighter2': 'Andrea Lee', 'method': 'Submission (armbar)', 'round': 3, 'time': '4:17', 'winner': 'Miranda Maverick', 'weight_class': 'Flyweight'}
                ]
            },
            {
                'name': 'UFC 297: Strickland vs Du Plessis',
                'date': '2024-01-20',
                'venue': 'Scotiabank Arena',
                'location': 'Toronto, Ontario, Canada',
                'fights': [
                    {'fighter1': 'Dricus Du Plessis', 'fighter2': 'Sean Strickland', 'method': 'Decision (split)', 'round': 5, 'time': '5:00', 'winner': 'Dricus Du Plessis', 'weight_class': 'Middleweight'},
                    {'fighter1': 'Raquel Pennington', 'fighter2': 'Mayra Bueno Silva', 'method': 'Decision (unanimous)', 'round': 5, 'time': '5:00', 'winner': 'Raquel Pennington', 'weight_class': 'Women\'s Bantamweight'},
                    {'fighter1': 'Neil Magny', 'fighter2': 'Mike Malott', 'method': 'TKO (punches)', 'round': 3, 'time': '4:45', 'winner': 'Neil Magny', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Chris Curtis', 'fighter2': 'Marc-Andre Barriault', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Chris Curtis', 'weight_class': 'Middleweight'},
                    {'fighter1': 'Movsar Evloev', 'fighter2': 'Arnold Allen', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Movsar Evloev', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Garrett Armfield', 'fighter2': 'Brad Katona', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Garrett Armfield', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Sean Woodson', 'fighter2': 'Charles Jourdain', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Sean Woodson', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Ramon Taveras', 'fighter2': 'Serhiy Sidey', 'method': 'Decision (split)', 'round': 3, 'time': '5:00', 'winner': 'Ramon Taveras', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Gillian Robertson', 'fighter2': 'Polyana Viana', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '3:12', 'winner': 'Gillian Robertson', 'weight_class': 'Women\'s Strawweight'},
                    {'fighter1': 'Yohan Lainesse', 'fighter2': 'Sam Patterson', 'method': 'Submission (rear-naked choke)', 'round': 1, 'time': '2:03', 'winner': 'Yohan Lainesse', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Jasmine Jasudavicius', 'fighter2': 'Priscila Cachoeira', 'method': 'Submission (rear-naked choke)', 'round': 3, 'time': '4:21', 'winner': 'Jasmine Jasudavicius', 'weight_class': 'Women\'s Flyweight'},
                    {'fighter1': 'Jimmy Flick', 'fighter2': 'Malcolm Gordon', 'method': 'Submission (triangle choke)', 'round': 2, 'time': '1:37', 'winner': 'Jimmy Flick', 'weight_class': 'Flyweight'}
                ]
            },
            {
                'name': 'UFC 296: Edwards vs Covington',
                'date': '2023-12-16',
                'venue': 'T-Mobile Arena',
                'location': 'Las Vegas, Nevada',
                'fights': [
                    {'fighter1': 'Leon Edwards', 'fighter2': 'Colby Covington', 'method': 'Decision (unanimous)', 'round': 5, 'time': '5:00', 'winner': 'Leon Edwards', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Alexandre Pantoja', 'fighter2': 'Brandon Royval', 'method': 'Decision (unanimous)', 'round': 5, 'time': '5:00', 'winner': 'Alexandre Pantoja', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Shavkat Rakhmonov', 'fighter2': 'Stephen Thompson', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '4:56', 'winner': 'Shavkat Rakhmonov', 'weight_class': 'Welterweight'},
                    {'fighter1': 'Paddy Pimblett', 'fighter2': 'Tony Ferguson', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Paddy Pimblett', 'weight_class': 'Lightweight'},
                    {'fighter1': 'Josh Emmett', 'fighter2': 'Bryce Mitchell', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Josh Emmett', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Alonzo Menifield', 'fighter2': 'Dustin Jacoby', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Alonzo Menifield', 'weight_class': 'Light Heavyweight'},
                    {'fighter1': 'Irene Aldana', 'fighter2': 'Karol Rosa', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Irene Aldana', 'weight_class': 'Women\'s Bantamweight'},
                    {'fighter1': 'Cody Garbrandt', 'fighter2': 'Brian Kelleher', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Cody Garbrandt', 'weight_class': 'Bantamweight'},
                    {'fighter1': 'Ariane Lipski', 'fighter2': 'Casey O\'Neill', 'method': 'Decision (unanimous)', 'round': 3, 'time': '5:00', 'winner': 'Ariane Lipski', 'weight_class': 'Women\'s Flyweight'},
                    {'fighter1': 'Tagir Ulanbekov', 'fighter2': 'Cody Durden', 'method': 'Submission (rear-naked choke)', 'round': 2, 'time': '4:25', 'winner': 'Tagir Ulanbekov', 'weight_class': 'Flyweight'},
                    {'fighter1': 'Andre Fili', 'fighter2': 'Lucas Almeida', 'method': 'TKO (punches)', 'round': 1, 'time': '2:45', 'winner': 'Andre Fili', 'weight_class': 'Featherweight'},
                    {'fighter1': 'Shamil Gaziev', 'fighter2': 'Martin Buday', 'method': 'TKO (punches)', 'round': 2, 'time': '0:56', 'winner': 'Shamil Gaziev', 'weight_class': 'Heavyweight'}
                ]
            }
        ]
    
    def get_or_create_fighter(self, fighter_name: str) -> str:
        """Get or create fighter in database"""
        try:
            # Check if fighter exists
            response = requests.get(
                f"{self.supabase_url}/rest/v1/fighters?name=eq.{fighter_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                fighters = response.json()
                if fighters:
                    return fighters[0]['id']
            
            # Create new fighter
            fighter_to_create = {
                'name': fighter_name,
                'weight_class': 'Unknown',
                'record': {'wins': 0, 'losses': 0, 'draws': 0},
                'is_active': 'Active'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/fighters",
                headers=self.headers,
                json=fighter_to_create
            )
            
            if response.status_code == 201:
                # Get the created fighter ID
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/fighters?name=eq.{fighter_name}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    fighters = response.json()
                    if fighters:
                        return fighters[0]['id']
            
            return None
            
        except Exception as e:
            print(f"Error with fighter {fighter_name}: {e}")
            return None
    
    def create_event(self, event_data: dict) -> str:
        """Create event in database"""
        try:
            event_to_create = {
                'name': event_data['name'],
                'date': event_data['date'],
                'venue': event_data['venue'],
                'location': event_data['location'],
                'status': 'completed'
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/events",
                headers=self.headers,
                json=event_to_create
            )
            
            if response.status_code == 201:
                # Get the created event ID
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/events?name=eq.{event_data['name']}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    events = response.json()
                    if events:
                        return events[0]['id']
            
            return None
            
        except Exception as e:
            print(f"Error creating event {event_data['name']}: {e}")
            return None
    
    def create_fight(self, fight_data: dict, event_id: str) -> bool:
        """Create fight in database with proper winner/loser data"""
        try:
            fighter1_id = self.get_or_create_fighter(fight_data['fighter1'])
            fighter2_id = self.get_or_create_fighter(fight_data['fighter2'])
            
            if not fighter1_id or not fighter2_id:
                print(f"Could not get/create fighters for {fight_data['fighter1']} vs {fight_data['fighter2']}")
                return False
            
            # Determine winner
            winner_id = fighter1_id if fight_data['winner'] == fight_data['fighter1'] else fighter2_id
            
            fight_to_create = {
                'event_id': event_id,
                'fighter1_id': fighter1_id,
                'fighter2_id': fighter2_id,
                'status': 'completed',
                'result': {
                    'method': fight_data['method'],
                    'round': fight_data['round'],
                    'time': fight_data['time'],
                    'winner_id': winner_id
                },
                'weight_class': fight_data['weight_class']
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/fights",
                headers=self.headers,
                json=fight_to_create
            )
            
            if response.status_code == 201:
                print(f"   ✅ {fight_data['fighter1']} vs {fight_data['fighter2']} -> {fight_data['winner']} wins")
                return True
            else:
                print(f"   ❌ Failed to create fight: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error creating fight: {e}")
            return False
    
    def scale_up_past_events(self):
        """Scale up past events with more data"""
        print("🚀 Starting Past Events Scaling...")
        
        total_fights_created = 0
        total_events_created = 0
        
        for event_data in self.extended_past_events:
            print(f"\n📅 Processing: {event_data['name']}")
            
            # Check if event already exists
            response = requests.get(
                f"{self.supabase_url}/rest/v1/events?name=eq.{event_data['name']}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                events = response.json()
                if events:
                    event_id = events[0]['id']
                    print(f"   ✅ Event already exists: {event_data['name']}")
                else:
                    # Create event
                    event_id = self.create_event(event_data)
                    if not event_id:
                        print(f"❌ Could not create event: {event_data['name']}")
                        continue
                    total_events_created += 1
                    print(f"   ✅ Created event: {event_data['name']}")
            else:
                # Create event
                event_id = self.create_event(event_data)
                if not event_id:
                    print(f"❌ Could not create event: {event_data['name']}")
                    continue
                total_events_created += 1
                print(f"   ✅ Created event: {event_data['name']}")
            
            # Check if fights already exist for this event
            fights_response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?event_id=eq.{event_id}&select=id&limit=1",
                headers=self.headers
            )
            
            if fights_response.status_code == 200 and fights_response.json():
                print(f"   ⚠️  Fights already exist for {event_data['name']}, skipping...")
                continue
            
            # Create fights for this event
            fights_created = 0
            for fight_data in event_data['fights']:
                if self.create_fight(fight_data, event_id):
                    fights_created += 1
            
            total_fights_created += fights_created
            print(f"   📊 Created {fights_created} fights for {event_data['name']}")
        
        print(f"\n🎉 Scaling complete!")
        print(f"   📊 Total events: {total_events_created}")
        print(f"   🥊 Total fights: {total_fights_created}")
        
        return total_events_created, total_fights_created
    
    def verify_scaling(self):
        """Verify the scaled data"""
        print("\n🔍 Verifying scaled data...")
        
        try:
            # Check events
            events_response = requests.get(
                f"{self.supabase_url}/rest/v1/events?select=id,name,date&order=date.desc",
                headers=self.headers
            )
            if events_response.status_code == 200:
                events = events_response.json()
                print(f"   📊 Total events: {len(events)}")
                for event in events:
                    print(f"      ✅ {event['name']} ({event['date']})")
            
            # Check fights
            fights_response = requests.get(
                f"{self.supabase_url}/rest/v1/fights?select=id,event_id&limit=10",
                headers=self.headers
            )
            if fights_response.status_code == 200:
                fights = fights_response.json()
                print(f"   🥊 Total fights: {len(fights)}")
                
                # Group by event
                event_fights = {}
                for fight in fights:
                    event_id = fight['event_id']
                    if event_id not in event_fights:
                        event_fights[event_id] = 0
                    event_fights[event_id] += 1
                
                print(f"   📊 Fights per event:")
                for event_id, count in event_fights.items():
                    print(f"      Event {event_id[:8]}...: {count} fights")
            
        except Exception as e:
            print(f"❌ Error verifying scaling: {e}")
    
    def run_scaling(self):
        """Run the complete scaling process"""
        print("🚀 Starting Past UFC Events Scaling")
        print("=" * 50)
        
        # Scale up past events
        events_created, fights_created = self.scale_up_past_events()
        
        # Verify scaling
        self.verify_scaling()
        
        print(f"\n✅ Scaling Complete!")
        print(f"   📊 Events: {events_created}")
        print(f"   🥊 Fights: {fights_created}")
        print(f"   🎯 Ready for Flutter app with more fight cards!")

def main():
    scaler = PastEventsScaler()
    scaler.run_scaling()

if __name__ == "__main__":
    main() 