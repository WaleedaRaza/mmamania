#!/usr/bin/env python3
"""
Enhanced UFC Fighter Profile Scraper
Comprehensive scraping of individual fighter profiles with detailed stats and fight history
"""

import time
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFighterScraper:
    """Enhanced scraper for detailed UFC fighter profiles"""
    
    def __init__(self):
        self.base_url = "https://www.ufc.com"
        self.driver = None
        self.wait_timeout = 10
        
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("✅ Selenium WebDriver initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize WebDriver: {e}")
                self.driver = None
                
    def _close_driver(self):
        """Close the Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("✅ WebDriver closed successfully")
            except Exception as e:
                logger.error(f"❌ Error closing WebDriver: {e}")
    
    def scrape_fighter_profile(self, fighter_url: str) -> Optional[Dict]:
        """Scrape comprehensive fighter profile data"""
        try:
            self._init_driver()
            if not self.driver:
                return None
            
            # Construct full URL
            full_url = f"{self.base_url}{fighter_url}" if fighter_url.startswith('/') else fighter_url
            logger.info(f"🔍 Scraping fighter profile: {full_url}")
            
            # Navigate to fighter page
            self.driver.get(full_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract all fighter data
            fighter_data = {
                'id': fighter_url.split('/')[-1] if '/' in fighter_url else fighter_url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract basic info
            basic_info = self._extract_basic_info()
            fighter_data.update(basic_info)
            
            # Extract personal info
            personal_info = self._extract_personal_info()
            fighter_data.update(personal_info)
            
            # Extract fight statistics
            fight_stats = self._extract_fight_stats()
            fighter_data['stats'] = fight_stats
            
            # Extract fight history
            fight_history = self._extract_fight_history()
            fighter_data['fight_history'] = fight_history
            
            # Extract training info
            training_info = self._extract_training_info()
            fighter_data.update(training_info)
            
            logger.info(f"✅ Successfully scraped profile for {fighter_data.get('name', 'Unknown')}")
            return fighter_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping fighter profile {fighter_url}: {e}")
            return None
    
    def _extract_basic_info(self) -> Dict:
        """Extract basic fighter information"""
        basic_info = {
            'name': 'Unknown Fighter',
            'division': 'Unknown Division',
            'record': {'wins': 0, 'losses': 0, 'draws': 0},
            'image_url': None,
            'status': 'Active'
        }
        
        try:
            # Extract name
            name_selectors = [
                ".hero-content h1",
                ".hero-content .hero-content__title",
                "h1",
                ".fighter-name",
                ".hero-content__title"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name and name != "Skip to main content" and len(name) > 2:
                        basic_info['name'] = name
                        break
                except:
                    continue
            
            # Extract division/weight class
            division_selectors = [
                ".hero-content .hero-content__division",
                ".hero-content .hero-content__weight-class",
                ".fighter-division",
                ".weight-class",
                ".hero-content__division"
            ]
            
            for selector in division_selectors:
                try:
                    div_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    division = div_elem.text.strip()
                    if division and division != "Skip to main content":
                        basic_info['division'] = division
                        break
                except:
                    continue
            
            # Extract record
            record_selectors = [
                ".hero-content .hero-content__record",
                ".fighter-record",
                ".record",
                ".hero-content__record"
            ]
            
            for selector in record_selectors:
                try:
                    record_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    record_text = record_elem.text.strip()
                    
                    # Parse record like "25-1-0" or "25-1"
                    parts = record_text.split('-')
                    if len(parts) >= 2:
                        wins = int(parts[0]) if parts[0].isdigit() else 0
                        losses = int(parts[1]) if parts[1].isdigit() else 0
                        draws = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                        basic_info['record'] = {'wins': wins, 'losses': losses, 'draws': draws}
                        break
                except:
                    continue
            
            # Extract image URL
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, ".hero-content img, .fighter-image img")
                basic_info['image_url'] = img_elem.get_attribute('src')
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Error extracting basic info: {e}")
        
        return basic_info
    
    def _extract_personal_info(self) -> Dict:
        """Extract fighter's personal information"""
        personal_info = {
            'age': None,
            'height': None,
            'weight': None,
            'reach': None,
            'leg_reach': None,
            'place_of_birth': None,
            'nationality': None
        }
        
        try:
            # Look for personal info sections
            info_sections = self.driver.find_elements(By.CSS_SELECTOR, 
                ".personal-info, .fighter-info, .bio, .hero-content__bio, .fighter-details")
            
            for section in info_sections:
                section_text = section.text.lower()
                
                # Extract age
                age_match = re.search(r'age[:\s]*(\d+)', section_text)
                if age_match:
                    personal_info['age'] = int(age_match.group(1))
                
                # Extract height (convert to inches)
                height_match = re.search(r'height[:\s]*(\d+)\'(\d+)"', section_text)
                if height_match:
                    feet = int(height_match.group(1))
                    inches = int(height_match.group(2))
                    personal_info['height'] = feet * 12 + inches
                
                # Extract weight
                weight_match = re.search(r'weight[:\s]*(\d+)\s*lbs?', section_text)
                if weight_match:
                    personal_info['weight'] = int(weight_match.group(1))
                
                # Extract reach
                reach_match = re.search(r'reach[:\s]*(\d+)"', section_text)
                if reach_match:
                    personal_info['reach'] = int(reach_match.group(1))
                
                # Extract leg reach
                leg_reach_match = re.search(r'leg\s*reach[:\s]*(\d+)"', section_text)
                if leg_reach_match:
                    personal_info['leg_reach'] = int(leg_reach_match.group(1))
                
                # Extract birthplace
                birth_match = re.search(r'born[:\s]*([^,\n]+)', section_text)
                if birth_match:
                    personal_info['place_of_birth'] = birth_match.group(1).strip()
                
                # Extract nationality
                nationality_match = re.search(r'nationality[:\s]*([^,\n]+)', section_text)
                if nationality_match:
                    personal_info['nationality'] = nationality_match.group(1).strip()
                    
        except Exception as e:
            logger.warning(f"Error extracting personal info: {e}")
        
        return personal_info
    
    def _extract_fight_stats(self) -> Dict:
        """Extract detailed fighter statistics"""
        stats = {
            'fight_win_streak': 0,
            'wins_by_knockout': 0,
            'wins_by_submission': 0,
            'wins_by_decision': 0,
            'striking_accuracy': 0.0,
            'sig_strikes_landed': 0,
            'sig_strikes_attempted': 0,
            'takedown_accuracy': 0.0,
            'takedowns_landed': 0,
            'takedowns_attempted': 0,
            'sig_strikes_landed_per_min': 0.0,
            'sig_strikes_absorbed_per_min': 0.0,
            'takedown_avg_per_15_min': 0.0,
            'submission_avg_per_15_min': 0.0,
            'sig_strikes_defense': 0.0,
            'takedown_defense': 0.0,
            'knockdown_avg': 0.0,
            'average_fight_time': '0:00'
        }
        
        try:
            # Look for stats in various sections
            stats_sections = self.driver.find_elements(By.CSS_SELECTOR, 
                ".stats-section, .fighter-stats, .statistics, .hero-content__stats")
            
            for section in stats_sections:
                section_text = section.text.lower()
                
                # Extract various stats using regex patterns
                patterns = {
                    'fight_win_streak': r'(\d+)\s*(?:fight\s*)?win\s*streak',
                    'wins_by_knockout': r'(\d+)\s*(?:wins?\s*)?by\s*(?:t)?ko',
                    'wins_by_submission': r'(\d+)\s*(?:wins?\s*)?by\s*submission',
                    'wins_by_decision': r'(\d+)\s*(?:wins?\s*)?by\s*decision',
                    'striking_accuracy': r'striking\s*accuracy[:\s]*(\d+(?:\.\d+)?)',
                    'takedown_accuracy': r'takedown\s*accuracy[:\s]*(\d+(?:\.\d+)?)',
                    'sig_strikes_landed_per_min': r'(\d+(?:\.\d+)?)\s*strikes?\s*per\s*min',
                    'sig_strikes_absorbed_per_min': r'(\d+(?:\.\d+)?)\s*absorbed\s*per\s*min',
                    'takedown_avg_per_15_min': r'(\d+(?:\.\d+)?)\s*takedowns?\s*per\s*15',
                    'submission_avg_per_15_min': r'(\d+(?:\.\d+)?)\s*submissions?\s*per\s*15',
                    'sig_strikes_defense': r'striking\s*defense[:\s]*(\d+(?:\.\d+)?)',
                    'takedown_defense': r'takedown\s*defense[:\s]*(\d+(?:\.\d+)?)',
                    'knockdown_avg': r'(\d+(?:\.\d+)?)\s*knockdowns?\s*per\s*15',
                    'average_fight_time': r'average\s*fight\s*time[:\s]*(\d+:\d+)'
                }
                
                for stat_name, pattern in patterns.items():
                    match = re.search(pattern, section_text)
                    if match:
                        try:
                            if stat_name in ['striking_accuracy', 'takedown_accuracy', 'sig_strikes_defense', 'takedown_defense']:
                                stats[stat_name] = float(match.group(1))
                            elif stat_name in ['fight_win_streak', 'wins_by_knockout', 'wins_by_submission', 'wins_by_decision']:
                                stats[stat_name] = int(match.group(1))
                            elif stat_name in ['sig_strikes_landed_per_min', 'sig_strikes_absorbed_per_min', 'takedown_avg_per_15_min', 'submission_avg_per_15_min', 'knockdown_avg']:
                                stats[stat_name] = float(match.group(1))
                            elif stat_name == 'average_fight_time':
                                stats[stat_name] = match.group(1)
                        except:
                            continue
                            
        except Exception as e:
            logger.warning(f"Error extracting fight stats: {e}")
        
        return stats
    
    def _extract_training_info(self) -> Dict:
        """Extract fighter's training information"""
        training_info = {
            'training_at': None,
            'fighting_style': None,
            'octagon_debut': None
        }
        
        try:
            # Look for training info sections
            info_sections = self.driver.find_elements(By.CSS_SELECTOR, 
                ".training-info, .fighter-info, .bio, .hero-content__bio")
            
            for section in info_sections:
                section_text = section.text.lower()
                
                # Extract training camp
                training_match = re.search(r'training[:\s]*([^,\n]+)', section_text)
                if training_match:
                    training_info['training_at'] = training_match.group(1).strip()
                
                # Extract fighting style
                style_match = re.search(r'style[:\s]*([^,\n]+)', section_text)
                if style_match:
                    training_info['fighting_style'] = style_match.group(1).strip()
                
                # Extract octagon debut
                debut_match = re.search(r'debut[:\s]*([^,\n]+)', section_text)
                if debut_match:
                    training_info['octagon_debut'] = debut_match.group(1).strip()
                    
        except Exception as e:
            logger.warning(f"Error extracting training info: {e}")
        
        return training_info
    
    def _extract_fight_history(self) -> List[Dict]:
        """Extract fighter's fight history"""
        fight_history = []
        
        try:
            # Look for fight history section
            history_sections = self.driver.find_elements(By.CSS_SELECTOR, 
                ".fight-history, .results, .last-fights, .fighter-results")
            
            for section in history_sections:
                fight_items = section.find_elements(By.CSS_SELECTOR, 
                    ".fight-item, .result-item, .fight, .result")
                
                for item in fight_items[:10]:  # Limit to last 10 fights
                    try:
                        fight_data = self._parse_fight_history_item(item)
                        if fight_data:
                            fight_history.append(fight_data)
                    except Exception as e:
                        logger.warning(f"Error parsing fight history item: {e}")
                        continue
                        
        except Exception as e:
            logger.warning(f"Error extracting fight history: {e}")
        
        return fight_history
    
    def _parse_fight_history_item(self, item) -> Optional[Dict]:
        """Parse individual fight history item"""
        try:
            fight_data = {
                'opponent': 'Unknown',
                'result': 'Unknown',
                'method': 'Unknown',
                'round': None,
                'time': 'Unknown',
                'date': 'Unknown',
                'event': 'Unknown'
            }
            
            item_text = item.text.lower()
            
            # Extract opponent name
            opponent_selectors = [".opponent", ".fighter-name", ".name", ".vs"]
            for selector in opponent_selectors:
                try:
                    opp_elem = item.find_element(By.CSS_SELECTOR, selector)
                    fight_data['opponent'] = opp_elem.text.strip()
                    break
                except:
                    continue
            
            # Extract result
            if 'win' in item_text:
                fight_data['result'] = 'Win'
            elif 'loss' in item_text:
                fight_data['result'] = 'Loss'
            elif 'draw' in item_text:
                fight_data['result'] = 'Draw'
            elif 'nc' in item_text or 'no contest' in item_text:
                fight_data['result'] = 'No Contest'
            
            # Extract method
            methods = ['ko', 'tko', 'submission', 'decision', 'unanimous', 'split', 'majority']
            for method in methods:
                if method in item_text:
                    fight_data['method'] = method.title()
                    break
            
            # Extract round
            round_match = re.search(r'round\s*(\d+)', item_text)
            if round_match:
                fight_data['round'] = int(round_match.group(1))
            
            # Extract time
            time_match = re.search(r'(\d+:\d+)', item_text)
            if time_match:
                fight_data['time'] = time_match.group(1)
            
            # Extract date
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', item_text)
            if date_match:
                fight_data['date'] = date_match.group(1)
            
            # Extract event
            event_selectors = [".event", ".card", ".show", ".fight-card"]
            for selector in event_selectors:
                try:
                    event_elem = item.find_element(By.CSS_SELECTOR, selector)
                    fight_data['event'] = event_elem.text.strip()
                    break
                except:
                    continue
            
            return fight_data
            
        except Exception as e:
            logger.warning(f"Error parsing fight history item: {e}")
            return None
    
    def scrape_multiple_fighters(self, fighter_urls: List[str], limit: int = 50) -> List[Dict]:
        """Scrape multiple fighter profiles with rate limiting"""
        logger.info(f"🚀 Starting batch scraping of {min(len(fighter_urls), limit)} fighters...")
        
        fighters = []
        processed_count = 0
        
        for fighter_url in fighter_urls[:limit]:
            try:
                logger.info(f"📊 Progress: {processed_count + 1}/{min(len(fighter_urls), limit)}")
                
                fighter_data = self.scrape_fighter_profile(fighter_url)
                if fighter_data:
                    fighters.append(fighter_data)
                    logger.info(f"✅ Scraped: {fighter_data.get('name', 'Unknown')}")
                else:
                    logger.warning(f"❌ Failed to scrape: {fighter_url}")
                
                processed_count += 1
                
                # Rate limiting - be respectful to the server
                if processed_count < min(len(fighter_urls), limit):
                    time.sleep(3)  # 3 second delay between requests
                
            except Exception as e:
                logger.error(f"❌ Error processing {fighter_url}: {e}")
                continue
        
        self._close_driver()
        logger.info(f"🎉 Batch scraping complete! Successfully scraped {len(fighters)} fighters")
        return fighters

def main():
    """Test the enhanced fighter scraper"""
    print("🥊 Enhanced UFC Fighter Profile Scraper")
    print("=" * 50)
    
    scraper = EnhancedFighterScraper()
    
    # Test with a few fighter URLs
    test_fighters = [
        "/fighter/islam-makhachev",
        "/fighter/alexander-volkanovski", 
        "/fighter/charles-oliveira"
    ]
    
    try:
        print("🧪 Testing fighter profile scraping...")
        print()
        
        for fighter_url in test_fighters:
            print(f"🔍 Testing: {fighter_url}")
            fighter_data = scraper.scrape_fighter_profile(fighter_url)
            
            if fighter_data:
                print(f"✅ Success: {fighter_data.get('name', 'Unknown')}")
                print(f"   • Division: {fighter_data.get('division', 'Unknown')}")
                print(f"   • Record: {fighter_data.get('record', {})}")
                print(f"   • Age: {fighter_data.get('age', 'Unknown')}")
                print(f"   • Height: {fighter_data.get('height', 'Unknown')}")
                print(f"   • Stats Available: {len(fighter_data.get('stats', {}))} metrics")
                print(f"   • Fight History: {len(fighter_data.get('fight_history', []))} fights")
            else:
                print(f"❌ Failed to scrape {fighter_url}")
            
            print()
            time.sleep(2)
        
        print("🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper._close_driver()

if __name__ == "__main__":
    main()
