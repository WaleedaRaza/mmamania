#!/usr/bin/env python3
"""
Script to populate the backend database with real UFC data
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import SessionLocal, engine
from app.models.ranking import Ranking
from app.services.ufc_scraper_service import UFCScraperService

def populate_database():
    """Populate the database with real UFC data"""
    print("🚀 Starting database population with real UFC data...")
    
    try:
        # Create database tables
        from app.models import ranking
        ranking.Base.metadata.create_all(bind=engine)
        
        # Initialize scraper service
        scraper_service = UFCScraperService()
        
        # Get database session
        db = SessionLocal()
        
        print("📊 Updating rankings from live UFC data...")
        success = scraper_service.update_rankings(db)
        
        if success:
            print("✅ Rankings updated successfully!")
            
            # Get count of rankings
            rankings_count = db.query(Ranking).count()
            divisions_count = db.query(Ranking.division).distinct().count()
            
            print(f"📈 Database Statistics:")
            print(f"   - Total Rankings: {rankings_count}")
            print(f"   - Divisions: {divisions_count}")
            
            # Show sample divisions
            divisions = db.query(Ranking.division).distinct().limit(5).all()
            print(f"   - Sample Divisions: {[div[0] for div in divisions]}")
            
        else:
            print("❌ Failed to update rankings")
            return False
            
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        return False

def check_database_status():
    """Check the current status of the database"""
    try:
        db = SessionLocal()
        
        rankings_count = db.query(Ranking).count()
        divisions_count = db.query(Ranking.division).distinct().count()
        
        print(f"📊 Current Database Status:")
        print(f"   - Total Rankings: {rankings_count}")
        print(f"   - Divisions: {divisions_count}")
        
        if rankings_count > 0:
            # Show last update time
            last_update = db.query(Ranking.updated_at).order_by(Ranking.updated_at.desc()).first()
            if last_update and last_update[0]:
                print(f"   - Last Updated: {last_update[0]}")
            
            # Show sample rankings
            sample_rankings = db.query(Ranking).limit(3).all()
            print(f"   - Sample Rankings:")
            for ranking in sample_rankings:
                print(f"     {ranking.rank}. {ranking.fighter_name} ({ranking.division})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error checking database status: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🏆 UFC Database Population Script")
    print("=" * 60)
    
    # Check if backend is running
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend is not responding properly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Backend is not running. Please start the backend first:")
        print("   cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print()
    
    # Populate database
    success = populate_database()
    
    if success:
        print()
        print("✅ Database population completed successfully!")
        print()
        check_database_status()
        print()
        print("🎉 You can now use the Flutter app to view live UFC rankings!")
    else:
        print()
        print("❌ Database population failed!")
        sys.exit(1) 