#!/usr/bin/env python3
"""
Firestore Service Layer
Handles all Firebase/Firestore operations for UFC data
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import logging
import os
from typing import Dict, List, Optional, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self, project_id: str = "mmamania-5a974"):
        """Initialize Firestore service"""
        self.project_id = project_id
        self.db = None
        self.authenticated = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Try to initialize with service account key first
            if os.path.exists("firebase-service-account.json"):
                cred = credentials.Certificate("firebase-service-account.json")
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase initialized with service account")
                self.authenticated = True
            else:
                # Try to use default credentials (for production)
                firebase_admin.initialize_app()
                logger.info("✅ Firebase initialized with default credentials")
                self.authenticated = True
        except ValueError:
            # App already initialized
            logger.info("✅ Firebase already initialized")
            self.authenticated = True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            logger.error("🔧 SETUP REQUIRED:")
            logger.error("   1. Create a Firebase project at https://console.firebase.google.com")
            logger.error("   2. Download service account key from Project Settings > Service Accounts")
            logger.error("   3. Save as 'firebase-service-account.json' in project root")
            logger.error("   4. Or set up Google Cloud credentials with: gcloud auth application-default login")
            self.authenticated = False
            return
        
        if self.authenticated:
            try:
                self.db = firestore.client()
                logger.info(f"✅ Firestore client initialized for project: {self.project_id}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Firestore client: {e}")
                self.authenticated = False
    
    def upload_rankings(self, rankings_data: List[Dict]) -> bool:
        """Upload UFC rankings to Firestore"""
        if not self.authenticated:
            logger.error("❌ Not authenticated with Firebase")
            return False
            
        try:
            logger.info(f"🔄 Uploading {len(rankings_data)} rankings to Firestore...")
            
            # Group rankings by division
            divisions = {}
            for ranking in rankings_data:
                division = ranking.get('division', 'Unknown')
                if division not in divisions:
                    divisions[division] = []
                divisions[division].append(ranking)
            
            # Upload each division
            for division, rankings in divisions.items():
                division_ref = self.db.collection('ufc_data').document('rankings').collection(division)
                
                # Clear existing rankings for this division
                existing_docs = division_ref.stream()
                for doc in existing_docs:
                    doc.reference.delete()
                
                # Upload new rankings
                batch = self.db.batch()
                for ranking in rankings:
                    fighter_id = self._generate_fighter_id(ranking['name'])
                    doc_ref = division_ref.document(fighter_id)
                    
                    data = {
                        'rank': int(ranking['rank']),
                        'name': ranking['name'],
                        'division': ranking['division'],
                        'record': ranking.get('record', ''),
                        'url': ranking.get('url', ''),
                        'last_updated': datetime.now(),
                        'scraped_at': datetime.fromisoformat(ranking.get('scraped_at', datetime.now().isoformat()))
                    }
                    
                    batch.set(doc_ref, data)
                
                batch.commit()
                logger.info(f"✅ Uploaded {len(rankings)} rankings for {division}")
            
            # Update metadata
            self._update_rankings_metadata(len(rankings_data))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uploading rankings: {e}")
            return False
    
    def upload_fighters(self, fighters_data: List[Dict]) -> bool:
        """Upload fighter profiles to Firestore"""
        if not self.authenticated:
            logger.error("❌ Not authenticated with Firebase")
            return False
            
        try:
            logger.info(f"🔄 Uploading {len(fighters_data)} fighters to Firestore...")
            
            fighters_ref = self.db.collection('ufc_data').document('fighters').collection('fighters')
            
            # Clear existing fighters
            existing_docs = fighters_ref.stream()
            for doc in existing_docs:
                doc.reference.delete()
            
            # Upload new fighters
            batch = self.db.batch()
            for fighter in fighters_data:
                fighter_id = self._generate_fighter_id(fighter['name'])
                doc_ref = fighters_ref.document(fighter_id)
                
                data = {
                    'name': fighter['name'],
                    'record': fighter.get('record', ''),
                    'division': fighter.get('division', ''),
                    'url': fighter.get('url', ''),
                    'height': fighter.get('height', ''),
                    'weight': fighter.get('weight', ''),
                    'reach': fighter.get('reach', ''),
                    'stance': fighter.get('stance', ''),
                    'dob': fighter.get('dob', ''),
                    'hometown': fighter.get('hometown', ''),
                    'team': fighter.get('team', ''),
                    'last_updated': datetime.now(),
                    'scraped_at': datetime.fromisoformat(fighter.get('scraped_at', datetime.now().isoformat()))
                }
                
                batch.set(doc_ref, data)
            
            batch.commit()
            logger.info(f"✅ Uploaded {len(fighters_data)} fighters")
            
            # Update metadata
            self._update_fighters_metadata(len(fighters_data))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uploading fighters: {e}")
            return False
    
    def upload_events(self, events_data: List[Dict]) -> bool:
        """Upload UFC events to Firestore"""
        if not self.authenticated:
            logger.error("❌ Not authenticated with Firebase")
            return False
            
        try:
            logger.info(f"🔄 Uploading {len(events_data)} events to Firestore...")
            
            events_ref = self.db.collection('ufc_data').document('events').collection('events')
            
            # Clear existing events
            existing_docs = events_ref.stream()
            for doc in existing_docs:
                doc.reference.delete()
            
            # Upload new events
            batch = self.db.batch()
            total_fights = 0
            
            for event in events_data:
                event_id = self._generate_event_id(event['event']['title'])
                doc_ref = events_ref.document(event_id)
                
                fights = event.get('fights', [])
                total_fights += len(fights)
                
                data = {
                    'title': event['event']['title'],
                    'date': event['event']['date'],
                    'venue': event['event']['venue'],
                    'url': event['event']['url'],
                    'fights': fights,
                    'total_fights': len(fights),
                    'last_updated': datetime.now(),
                    'scraped_at': datetime.fromisoformat(event.get('scraped_at', datetime.now().isoformat()))
                }
                
                batch.set(doc_ref, data)
            
            batch.commit()
            logger.info(f"✅ Uploaded {len(events_data)} events with {total_fights} fights")
            
            # Update metadata
            self._update_events_metadata(len(events_data), total_fights)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uploading events: {e}")
            return False
    
    def update_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Update global metadata"""
        if not self.authenticated:
            logger.error("❌ Not authenticated with Firebase")
            return False
            
        try:
            metadata_ref = self.db.collection('ufc_data').document('metadata')
            
            data = {
                'last_sync': datetime.now(),
                'total_fighters': metadata.get('total_fighters', 0),
                'total_events': metadata.get('total_events', 0),
                'total_fights': metadata.get('total_fights', 0),
                'data_sources': metadata.get('data_sources', ['UFC.com', 'Wikipedia']),
                'last_updated': datetime.now()
            }
            
            metadata_ref.set(data)
            logger.info("✅ Metadata updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating metadata: {e}")
            return False
    
    def _generate_fighter_id(self, name: str) -> str:
        """Generate a unique fighter ID from name"""
        return name.lower().replace(' ', '-').replace('.', '').replace("'", '')
    
    def _generate_event_id(self, title: str) -> str:
        """Generate a unique event ID from title"""
        return title.lower().replace(' ', '-').replace('.', '').replace("'", '')
    
    def _update_rankings_metadata(self, total_fighters: int):
        """Update rankings metadata"""
        if not self.authenticated:
            return
            
        try:
            metadata_ref = self.db.collection('ufc_data').document('rankings').collection('metadata').document('stats')
            metadata_ref.set({
                'total_fighters': total_fighters,
                'last_update': datetime.now(),
                'source': 'UFC.com'
            })
        except Exception as e:
            logger.error(f"❌ Error updating rankings metadata: {e}")
    
    def _update_fighters_metadata(self, total_fighters: int):
        """Update fighters metadata"""
        if not self.authenticated:
            return
            
        try:
            metadata_ref = self.db.collection('ufc_data').document('fighters').collection('metadata').document('stats')
            metadata_ref.set({
                'total_fighters': total_fighters,
                'last_update': datetime.now(),
                'source': 'UFC.com'
            })
        except Exception as e:
            logger.error(f"❌ Error updating fighters metadata: {e}")
    
    def _update_events_metadata(self, total_events: int, total_fights: int):
        """Update events metadata"""
        if not self.authenticated:
            return
            
        try:
            metadata_ref = self.db.collection('ufc_data').document('events').collection('metadata').document('stats')
            metadata_ref.set({
                'total_events': total_events,
                'total_fights': total_fights,
                'last_update': datetime.now(),
                'source': 'Wikipedia'
            })
        except Exception as e:
            logger.error(f"❌ Error updating events metadata: {e}")
    
    def get_data_counts(self) -> Dict[str, int]:
        """Get current data counts from Firestore"""
        if not self.authenticated:
            return {'rankings': 0, 'fighters': 0, 'events': 0}
            
        try:
            counts = {}
            
            # Get rankings count
            rankings_ref = self.db.collection('ufc_data').document('rankings')
            rankings_docs = rankings_ref.collections()
            total_rankings = 0
            for collection in rankings_docs:
                if collection.id != 'metadata':
                    total_rankings += len(list(collection.stream()))
            counts['rankings'] = total_rankings
            
            # Get fighters count
            fighters_ref = self.db.collection('ufc_data').document('fighters').collection('fighters')
            counts['fighters'] = len(list(fighters_ref.stream()))
            
            # Get events count
            events_ref = self.db.collection('ufc_data').document('events').collection('events')
            counts['events'] = len(list(events_ref.stream()))
            
            return counts
            
        except Exception as e:
            logger.error(f"❌ Error getting data counts: {e}")
            return {'rankings': 0, 'fighters': 0, 'events': 0}
    
    def test_connection(self) -> bool:
        """Test Firestore connection"""
        if not self.authenticated:
            logger.error("❌ Not authenticated with Firebase")
            return False
            
        try:
            # Try to read from a test document
            test_ref = self.db.collection('test').document('connection')
            test_ref.get()
            logger.info("✅ Firestore connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Firestore connection test failed: {e}")
            return False

if __name__ == "__main__":
    # Test the Firestore service
    service = FirestoreService()
    if service.test_connection():
        print("✅ Firestore service is working!")
    else:
        print("❌ Firestore service failed to connect")
        print("\n🔧 SETUP INSTRUCTIONS:")
        print("1. Go to https://console.firebase.google.com")
        print("2. Create a new project or select existing project")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Save the JSON file as 'firebase-service-account.json' in project root")
        print("6. Or run: gcloud auth application-default login") 