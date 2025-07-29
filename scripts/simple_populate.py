#!/usr/bin/env python3
"""
Simple script to populate database with real UFC data
"""

import json
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def populate_rankings():
    """Populate rankings from the scraped data"""
    try:
        # Load the scraped data
        with open('ufc_processed_data.json', 'r') as f:
            data = json.load(f)
        
        print(f"📊 Loaded {len(data.get('rankings', []))} rankings from scraped data")
        
        # Import database components
        from app.core.database import SessionLocal, engine
        from app.models.ranking import Ranking
        from app.models.base import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Get database session
        db = SessionLocal()
        
        # Clear existing rankings
        db.query(Ranking).delete()
        
        # Insert new rankings
        rankings_data = data.get('rankings', [])
        for ranking_data in rankings_data:
            ranking = Ranking(
                division=ranking_data['division'],
                rank=ranking_data['rank'],
                fighter_name=ranking_data['fighter_name'],
                record_string=ranking_data.get('record_string', ''),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(ranking)
        
        # Commit changes
        db.commit()
        
        print(f"✅ Successfully inserted {len(rankings_data)} rankings")
        
        # Show sample data
        sample_rankings = db.query(Ranking).limit(5).all()
        print("📋 Sample rankings:")
        for ranking in sample_rankings:
            print(f"   {ranking.rank}. {ranking.fighter_name} ({ranking.division})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🏆 Simple UFC Database Population")
    print("=" * 40)
    
    success = populate_rankings()
    
    if success:
        print("\n🎉 Database populated successfully!")
        print("You can now use the Flutter app to view live UFC rankings!")
    else:
        print("\n❌ Failed to populate database")
        sys.exit(1) 