#!/usr/bin/env python3
"""
Comprehensive UFC Data Scraper
Combines rankings scraping with enhanced fighter profile scraping
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import logging

# Import our scrapers
from enhanced_ufc_scraper import EnhancedUFCScraper
from improved_fighter_scraper import ImprovedFighterScraper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveUFCScraper:
    """Comprehensive scraper that combines rankings and fighter profiles"""
    
    def __init__(self):
        self.rankings_scraper = EnhancedUFCScraper()
        self.fighter_scraper = ImprovedFighterScraper()
    
    def scrape_comprehensive_data(self, fighter_profile_limit: int = 30) -> Dict:
        """Scrape comprehensive UFC data with rankings and fighter profiles"""
        logger.info("🚀 Starting comprehensive UFC data scraping...")
        
        all_data = {
            'rankings': [],
            'fighters': [],
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Scrape rankings with champions
            logger.info("📊 Step 1: Scraping rankings with champion detection...")
            rankings = self.rankings_scraper.scrape_rankings_with_champions()
            all_data['rankings'] = rankings
            logger.info(f"✅ Scraped {len(rankings)} rankings")
            
            # Step 2: Extract unique fighter URLs for profile scraping
            fighter_urls = set()
            for ranking in rankings:
                if ranking.get('fighter_url'):
                    fighter_urls.add(ranking['fighter_url'])
            
            logger.info(f"🔍 Found {len(fighter_urls)} unique fighters for profile scraping")
            
            # Step 3: Scrape detailed fighter profiles
            logger.info(f"👤 Step 2: Scraping detailed fighter profiles (limit: {fighter_profile_limit})...")
            fighters = self.fighter_scraper.scrape_multiple_fighters(
                list(fighter_urls), 
                limit=fighter_profile_limit
            )
            all_data['fighters'] = fighters
            logger.info(f"✅ Scraped {len(fighters)} detailed fighter profiles")
            
            # Step 4: Link rankings to fighter profiles
            logger.info("🔗 Step 3: Linking rankings to fighter profiles...")
            self._link_rankings_to_fighters(all_data)
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive scraping: {e}")
        
        logger.info(f"🎉 Comprehensive scraping complete!")
        logger.info(f"   • Rankings: {len(all_data['rankings'])}")
        logger.info(f"   • Fighter Profiles: {len(all_data['fighters'])}")
        
        return all_data
    
    def _link_rankings_to_fighters(self, data: Dict):
        """Link rankings to fighter profiles by ID"""
        fighters_by_id = {fighter['id']: fighter for fighter in data['fighters']}
        
        for ranking in data['rankings']:
            fighter_id = ranking.get('fighter_id', '')
            if fighter_id and fighter_id in fighters_by_id:
                # Update ranking with fighter profile data
                fighter = fighters_by_id[fighter_id]
                ranking['has_detailed_profile'] = True
                ranking['fighter_profile'] = {
                    'age': fighter.get('age'),
                    'height': fighter.get('height'),
                    'weight': fighter.get('weight'),
                    'reach': fighter.get('reach'),
                    'nationality': fighter.get('nationality'),
                    'training_at': fighter.get('training_at'),
                    'fighting_style': fighter.get('fighting_style'),
                    'stats_available': len(fighter.get('stats', {})) > 0
                }
            else:
                ranking['has_detailed_profile'] = False
                ranking['fighter_profile'] = None
    
    def save_data(self, data: Dict, output_dir: str = "assets/data"):
        """Save scraped data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save comprehensive data
        comprehensive_file = f"{output_dir}/ufc_comprehensive_data.json"
        with open(comprehensive_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"💾 Comprehensive data saved to: {comprehensive_file}")
        
        # Save for Flutter app
        flutter_file = f"{output_dir}/ufc_data.json"
        with open(flutter_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"📱 Flutter data saved to: {flutter_file}")
        
        # Save summary
        summary = {
            'total_rankings': len(data.get('rankings', [])),
            'total_fighters': len(data.get('fighters', [])),
            'champions': len([r for r in data.get('rankings', []) if r.get('is_champion')]),
            'fighters_with_profiles': len([r for r in data.get('rankings', []) if r.get('has_detailed_profile')]),
            'scraped_at': data.get('scraped_at'),
            'divisions': list(set([r.get('division') for r in data.get('rankings', [])]))
        }
        
        summary_file = f"{output_dir}/scraping_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"📊 Summary saved to: {summary_file}")
        
        return comprehensive_file, flutter_file, summary_file

def main():
    """Run comprehensive UFC scraper"""
    print("🥊 Comprehensive UFC Data Scraper")
    print("=" * 60)
    print("This will scrape:")
    print("  • UFC rankings with champions")
    print("  • Detailed fighter profiles")
    print("  • Link rankings to fighter data")
    print("=" * 60)
    
    scraper = ComprehensiveUFCScraper()
    
    try:
        # Run comprehensive scraping
        print("🚀 Starting comprehensive scraping...")
        print("This may take several minutes...")
        print()
        
        start_time = datetime.now()
        
        # Scrape all data
        data = scraper.scrape_comprehensive_data(fighter_profile_limit=20)  # Limit to 20 for testing
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("✅ Scraping completed!")
        print(f"⏱️  Duration: {duration}")
        print()
        
        # Display results
        print("📊 Results Summary:")
        print(f"   • Total Rankings: {len(data.get('rankings', []))}")
        print(f"   • Total Fighters: {len(data.get('fighters', []))}")
        print(f"   • Champions: {len([r for r in data.get('rankings', []) if r.get('is_champion')])}")
        print(f"   • Fighters with Profiles: {len([r for r in data.get('rankings', []) if r.get('has_detailed_profile')])}")
        print()
        
        # Show champions
        champions = [r for r in data.get('rankings', []) if r.get('is_champion')]
        if champions:
            print("👑 Champions Found:")
            for champ in champions:
                profile_info = ""
                if champ.get('has_detailed_profile'):
                    profile = champ.get('fighter_profile', {})
                    if profile.get('nationality'):
                        profile_info = f" ({profile['nationality']})"
                print(f"   • {champ['fighter_name']} - {champ['division']}{profile_info}")
        print()
        
        # Show sample fighter data
        if data.get('fighters'):
            print("👤 Sample Fighter Profile:")
            sample_fighter = data['fighters'][0]
            print(f"   • Name: {sample_fighter.get('name', 'Unknown')}")
            print(f"   • Division: {sample_fighter.get('division', 'Unknown')}")
            print(f"   • Record: {sample_fighter.get('record', {})}")
            print(f"   • Age: {sample_fighter.get('age', 'Unknown')}")
            print(f"   • Nationality: {sample_fighter.get('nationality', 'Unknown')}")
            print(f"   • Stats Available: {len(sample_fighter.get('stats', {}))} metrics")
            print()
        
        # Save data
        print("💾 Saving data...")
        comprehensive_file, flutter_file, summary_file = scraper.save_data(data)
        
        print()
        print("🎉 Comprehensive scraper completed successfully!")
        print(f"📁 Data files saved:")
        print(f"   • Comprehensive: {comprehensive_file}")
        print(f"   • Flutter App: {flutter_file}")
        print(f"   • Summary: {summary_file}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 