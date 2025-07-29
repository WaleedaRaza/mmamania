#!/usr/bin/env python3
"""
Comprehensive UFC Data Scraper V2
Multi-source scraper for complete UFC fighter data
"""

import time
import logging
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Set
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveUFCScraperV2:
    """Comprehensive UFC scraper targeting multiple sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        self.wait_timeout = 15
        
        # Data storage
        self.fighters = {}
        self.rankings = {}
        self.events = []
        self.fight_history = {}
        
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
    
    def scrape_all_data(self) -> Dict:
        """Scrape all UFC data from multiple sources"""
        logger.info("🚀 Starting comprehensive UFC data scraping from multiple sources...")
        
        all_data = {
            'fighters': {},
            'rankings': {},
            'events': [],
            'fight_history': {},
            'scraped_at': datetime.now().isoformat(),
            'sources': []
        }
        
        try:
            # Source 1: UFCStats.com - Complete fighter database
            logger.info("📊 Source 1: Scraping UFCStats.com...")
            ufcstats_data = self.scrape_ufcstats()
            all_data['fighters'].update(ufcstats_data.get('fighters', {}))
            all_data['fight_history'].update(ufcstats_data.get('fight_history', {}))
            all_data['sources'].append('ufcstats.com')
            
            # Source 2: UFC.com Rankings
            logger.info("🏆 Source 2: Scraping UFC.com rankings...")
            ufc_rankings = self.scrape_ufc_rankings()
            all_data['rankings'].update(ufc_rankings)
            all_data['sources'].append('ufc.com/rankings')
            
            # Source 3: UFC.com Events
            logger.info("📅 Source 3: Scraping UFC.com events...")
            ufc_events = self.scrape_ufc_events()
            all_data['events'].extend(ufc_events)
            all_data['sources'].append('ufc.com/events')
            
            # Source 4: ESPN MMA Rankings
            logger.info("�� Source 4: Scraping ESPN MMA rankings...")
            espn_rankings = self.scrape_espn_rankings()
            all_data['rankings'].update(espn_rankings)
            all_data['sources'].append('espn.com/mma')
            
            # Source 5: UFC.com Athlete Profiles (detailed)
            logger.info("👤 Source 5: Scraping detailed UFC athlete profiles...")
            detailed_profiles = self.scrape_ufc_athlete_profiles()
            all_data['fighters'].update(detailed_profiles)
            all_data['sources'].append('ufc.com/athletes')
            
            # Source 6: StatLeaders.ufc.com
            logger.info("📈 Source 6: Scraping UFC StatLeaders...")
            statleaders_data = self.scrape_statileaders()
            all_data['fighters'].update(statleaders_data)
            all_data['sources'].append('statleaders.ufc.com')
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive scraping: {e}")
        
        logger.info(f"🎉 Comprehensive scraping complete!")
        logger.info(f"   • Fighters: {len(all_data['fighters'])}")
        logger.info(f"   • Rankings: {len(all_data['rankings'])} divisions")
        logger.info(f"   • Events: {len(all_data['events'])}")
        logger.info(f"   • Fight History: {len(all_data['fight_history'])} fighters")
        
        return all_data
    
    def scrape_ufcstats(self) -> Dict:
        """Scrape complete fighter data from UFCStats.com"""
        logger.info("🔍 Scraping UFCStats.com...")
        
        data = {'fighters': {}, 'fight_history': {}}
        
        try:
            # UFCStats has a comprehensive fighter database
            base_url = "http://ufcstats.com/statistics/fighters"
            
            # Get the main fighters page
            response = self.session.get(base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the fighters table
            fighters_table = soup.find('table', class_='b-statistics__table')
            if not fighters_table:
                logger.error("No fighters table found")
                return data
            
            # Get all fighter rows
            rows = fighters_table.find_all('tr', class_='b-statistics__table-row')
            logger.info(f"Found {len(rows)} fighter rows")
            
            # Process each row
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) < 11:  # Need at least 11 cells for complete data
                        continue
                    
                    # Extract name components
                    first_name = cells[0].get_text(strip=True)
                    last_name = cells[1].get_text(strip=True)
                    nickname = cells[2].get_text(strip=True)
                    
                    # Skip if no first or last name
                    if not first_name or not last_name:
                        continue
                    
                    # Combine into full name
                    full_name = f"{first_name} {last_name}".strip()
                    if nickname:
                        full_name = f"{full_name} \"{nickname}\""
                    
                    # Extract other data
                    height = cells[3].get_text(strip=True)
                    weight = cells[4].get_text(strip=True)
                    reach = cells[5].get_text(strip=True)
                    stance = cells[6].get_text(strip=True)
                    wins = cells[7].get_text(strip=True)
                    losses = cells[8].get_text(strip=True)
                    draws = cells[9].get_text(strip=True)
                    
                    # Get fighter URL from first name link
                    first_name_link = cells[0].find('a')
                    if not first_name_link:
                        continue
                    
                    fighter_url = first_name_link.get('href', '')
                    if not fighter_url:
                        continue
                    
                    logger.info(f"Scraping fighter {i+1}/{len(rows)}: {full_name}")
                    
                    # Create basic fighter data
                    fighter_data = {
                        'name': full_name,
                        'first_name': first_name,
                        'last_name': last_name,
                        'nickname': nickname,
                        'height': height,
                        'weight': weight,
                        'reach': reach,
                        'stance': stance,
                        'record': {
                            'wins': int(wins) if wins.isdigit() else 0,
                            'losses': int(losses) if losses.isdigit() else 0,
                            'draws': int(draws) if draws.isdigit() else 0
                        },
                        'source': 'ufcstats.com',
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Scrape detailed fighter profile
                    detailed_data = self.scrape_ufcstats_fighter(fighter_url)
                    if detailed_data:
                        # Merge detailed data
                        fighter_data.update(detailed_data)
                        
                        # Extract fight history
                        if 'fight_history' in detailed_data:
                            data['fight_history'][full_name] = detailed_data['fight_history']
                    
                    data['fighters'][full_name] = fighter_data
                    
                    # Limit for testing
                    if i >= 49:  # First 50 fighters
                        break
                    
                    time.sleep(1)  # Be respectful
                    
                except Exception as e:
                    logger.warning(f"Error processing fighter row {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping UFCStats: {e}")
        
        return data
    
    def scrape_ufcstats_fighter(self, fighter_url: str) -> Optional[Dict]:
        """Scrape individual fighter data from UFCStats"""
        try:
            if fighter_url.startswith('http'):
                full_url = fighter_url
            else:
                full_url = f"http://ufcstats.com{fighter_url}"
            response = self.session.get(full_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            fighter_data = {
                'source': 'ufcstats.com',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract basic info
            name_elem = soup.find('span', class_='b-content__title-highlight')
            if name_elem:
                fighter_data['name'] = name_elem.get_text(strip=True)
            
            # Extract record
            record_elem = soup.find('span', class_='b-content__title-record')
            if record_elem:
                record_text = record_elem.get_text(strip=True)
                record_match = re.search(r'(\d+)-(\d+)-(\d+)', record_text)
                if record_match:
                    fighter_data['record'] = {
                        'wins': int(record_match.group(1)),
                        'losses': int(record_match.group(2)),
                        'draws': int(record_match.group(3))
                    }
            
            # Extract detailed stats
            stats_table = soup.find('div', class_='b-list__info-box')
            if stats_table:
                stats = {}
                rows = stats_table.find_all('li', class_='b-list__box-list-item')
                for row in rows:
                    text = row.get_text(strip=True)
                    if 'Height:' in text:
                        stats['height'] = text.split('Height:')[1].strip()
                    elif 'Weight:' in text:
                        stats['weight'] = text.split('Weight:')[1].strip()
                    elif 'Reach:' in text:
                        stats['reach'] = text.split('Reach:')[1].strip()
                    elif 'STANCE:' in text:
                        stats['stance'] = text.split('STANCE:')[1].strip()
                    elif 'DOB:' in text:
                        stats['dob'] = text.split('DOB:')[1].strip()
                
                fighter_data['stats'] = stats
            
            # Extract fight history
            fight_history = []
            fights_table = soup.find('tbody', class_='b-fight-details__table-body')
            if fights_table:
                fight_rows = fights_table.find_all('tr', class_='b-fight-details__table-row')
                for row in fight_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 7:
                        fight = {
                            'opponent': cells[1].get_text(strip=True),
                            'result': cells[2].get_text(strip=True),
                            'method': cells[3].get_text(strip=True),
                            'round': cells[4].get_text(strip=True),
                            'time': cells[5].get_text(strip=True),
                            'event': cells[6].get_text(strip=True),
                            'date': cells[7].get_text(strip=True) if len(cells) > 7 else ''
                        }
                        fight_history.append(fight)
                
                fighter_data['fight_history'] = fight_history
            
            return fighter_data
            
        except Exception as e:
            logger.error(f"Error scraping UFCStats fighter {fighter_url}: {e}")
            return None
    
    def scrape_ufc_rankings(self) -> Dict:
        """Scrape UFC.com rankings"""
        logger.info("🔍 Scraping UFC.com rankings...")
        
        self._init_driver()
        if not self.driver:
            return {}
        
        rankings = {}
        
        try:
            url = "https://www.ufc.com/rankings"
            self.driver.get(url)
            
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract rankings by division
            rankings_sections = self.driver.find_elements(By.CSS_SELECTOR, '[class*="rankings"]')
            
            for section in rankings_sections:
                try:
                    # Extract division name
                    division_elem = section.find_element(By.CSS_SELECTOR, 'h3, h4, h5')
                    division = division_elem.text.strip()
                    
                    # Extract fighters
                    fighters = []
                    fighter_elements = section.find_elements(By.CSS_SELECTOR, 'a[href*="/athlete/"]')
                    
                    for i, fighter_elem in enumerate(fighter_elements):
                        try:
                            name = fighter_elem.text.strip()
                            url = fighter_elem.get_attribute('href')
                            
                            if name and url:
                                fighters.append({
                                    'name': name,
                                    'url': url,
                                    'rank': i + 1 if i > 0 else 0  # 0 for champion
                                })
                        except Exception as e:
                            continue
                    
                    if fighters:
                        rankings[division] = fighters
                        
                except Exception as e:
                    logger.warning(f"Error extracting division rankings: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping UFC rankings: {e}")
        
        return rankings
    
    def scrape_ufc_events(self) -> List[Dict]:
        """Scrape UFC.com events"""
        logger.info("🔍 Scraping UFC.com events...")
        
        self._init_driver()
        if not self.driver:
            return []
        
        events = []
        
        try:
            url = "https://www.ufc.com/events"
            self.driver.get(url)
            
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract event cards
            event_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="event"]')
            
            for event_elem in event_elements[:10]:  # Limit to 10 events
                try:
                    # Extract event info
                    title_elem = event_elem.find_element(By.CSS_SELECTOR, 'h3, h4, h5')
                    title = title_elem.text.strip()
                    
                    # Extract date
                    date_elem = event_elem.find_element(By.CSS_SELECTOR, '[class*="date"]')
                    date = date_elem.text.strip()
                    
                    # Extract location
                    location_elem = event_elem.find_element(By.CSS_SELECTOR, '[class*="location"]')
                    location = location_elem.text.strip()
                    
                    events.append({
                        'title': title,
                        'date': date,
                        'location': location,
                        'source': 'ufc.com'
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping UFC events: {e}")
        
        return events
    
    def scrape_espn_rankings(self) -> Dict:
        """Scrape ESPN MMA rankings"""
        logger.info("🔍 Scraping ESPN MMA rankings...")
        
        rankings = {}
        
        try:
            # ESPN P4P rankings
            p4p_url = "https://www.espn.com/mma/story/_/id/24067525/espn-mma-pound-pound-rankings"
            response = self.session.get(p4p_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract P4P rankings
            p4p_fighters = []
            ranking_elements = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(r'\d+\.'))
            
            for elem in ranking_elements[:15]:  # Top 15
                text = elem.get_text(strip=True)
                match = re.search(r'(\d+)\.\s*(.+)', text)
                if match:
                    rank = int(match.group(1))
                    name = match.group(2).strip()
                    p4p_fighters.append({
                        'rank': rank,
                        'name': name,
                        'division': 'Pound for Pound'
                    })
            
            if p4p_fighters:
                rankings['ESPN_P4P'] = p4p_fighters
            
        except Exception as e:
            logger.error(f"Error scraping ESPN rankings: {e}")
        
        return rankings
    
    def scrape_ufc_athlete_profiles(self) -> Dict:
        """Scrape detailed UFC athlete profiles"""
        logger.info("🔍 Scraping detailed UFC athlete profiles...")
        
        self._init_driver()
        if not self.driver:
            return {}
        
        profiles = {}
        
        # Sample fighter URLs to scrape
        sample_fighters = [
            "/athlete/islam-makhachev",
            "/athlete/alexander-volkanovski", 
            "/athlete/charles-oliveira",
            "/athlete/justin-gaethje",
            "/athlete/dustin-poirier"
        ]
        
        for fighter_url in sample_fighters:
            try:
                logger.info(f"Scraping profile: {fighter_url}")
                
                full_url = f"https://www.ufc.com{fighter_url}"
                self.driver.get(full_url)
                
                WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Extract fighter data
                fighter_data = self._extract_ufc_profile_data()
                if fighter_data:
                    fighter_id = fighter_url.split('/')[-1]
                    profiles[fighter_id] = fighter_data
                
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                logger.warning(f"Error scraping fighter profile {fighter_url}: {e}")
                continue
        
        return profiles
    
    def _extract_ufc_profile_data(self) -> Optional[Dict]:
        """Extract data from UFC athlete profile page"""
        try:
            data = {
                'source': 'ufc.com',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract name
            name_elem = self.driver.find_element(By.TAG_NAME, "h1")
            if name_elem:
                data['name'] = name_elem.text.strip()
            
            # Extract record
            page_source = self.driver.page_source
            record_match = re.search(r'(\d+)-(\d+)-(\d+)', page_source)
            if record_match:
                data['record'] = {
                    'wins': int(record_match.group(1)),
                    'losses': int(record_match.group(2)),
                    'draws': int(record_match.group(3))
                }
            
            # Extract division
            division_elem = self.driver.find_element(By.CSS_SELECTOR, '[class*="division"]')
            if division_elem:
                data['division'] = division_elem.text.strip()
            
            # Extract stats
            stats = {}
            stats_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="stat"]')
            for elem in stats_elements:
                text = elem.text.strip()
                if 'FIGHT WIN STREAK' in text:
                    streak_match = re.search(r'(\d+)', text)
                    if streak_match:
                        stats['fight_win_streak'] = int(streak_match.group(1))
                elif 'WINS BY KO' in text:
                    ko_match = re.search(r'(\d+)', text)
                    if ko_match:
                        stats['wins_by_ko'] = int(ko_match.group(1))
                elif 'WINS BY SUBMISSION' in text:
                    sub_match = re.search(r'(\d+)', text)
                    if sub_match:
                        stats['wins_by_submission'] = int(sub_match.group(1))
            
            if stats:
                data['stats'] = stats
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting UFC profile data: {e}")
            return None
    
    def scrape_statileaders(self) -> Dict:
        """Scrape UFC StatLeaders data"""
        logger.info("🔍 Scraping UFC StatLeaders...")
        
        self._init_driver()
        if not self.driver:
            return {}
        
        statleaders_data = {}
        
        try:
            url = "https://statleaders.ufc.com/"
            self.driver.get(url)
            
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract leaderboards
            leaderboard_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="leaderboard"]')
            
            for leaderboard in leaderboard_elements[:5]:  # First 5 leaderboards
                try:
                    # Extract category
                    category_elem = leaderboard.find_element(By.CSS_SELECTOR, 'h3, h4, h5')
                    category = category_elem.text.strip()
                    
                    # Extract top performers
                    performers = []
                    performer_elements = leaderboard.find_elements(By.CSS_SELECTOR, '[class*="performer"]')
                    
                    for i, performer_elem in enumerate(performer_elements[:10]):
                        try:
                            name = performer_elem.text.strip()
                            if name:
                                performers.append({
                                    'rank': i + 1,
                                    'name': name,
                                    'category': category
                                })
                        except Exception as e:
                            continue
                    
                    if performers:
                        statleaders_data[category] = performers
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping StatLeaders: {e}")
        
        return statleaders_data
    
    def save_data(self, data: Dict, output_dir: str = "assets/data"):
        """Save scraped data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save comprehensive data
        comprehensive_file = f"{output_dir}/ufc_comprehensive_v2.json"
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
            'total_fighters': len(data.get('fighters', {})),
            'total_rankings_divisions': len(data.get('rankings', {})),
            'total_events': len(data.get('events', [])),
            'total_fight_history': len(data.get('fight_history', {})),
            'sources_used': data.get('sources', []),
            'scraped_at': data.get('scraped_at'),
        }
        
        summary_file = f"{output_dir}/scraping_summary_v2.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"📊 Summary saved to: {summary_file}")
        
        return comprehensive_file, flutter_file, summary_file

def main():
    """Run comprehensive UFC scraper V2"""
    print("🥊 Comprehensive UFC Data Scraper V2")
    print("=" * 60)
    print("This will scrape from multiple sources:")
    print("  • UFCStats.com - Complete fighter database")
    print("  • UFC.com - Rankings, events, athlete profiles")
    print("  • ESPN.com - Additional rankings")
    print("  • StatLeaders.ufc.com - Advanced statistics")
    print("=" * 60)
    
    scraper = ComprehensiveUFCScraperV2()
    
    try:
        # Run comprehensive scraping
        print("🚀 Starting comprehensive scraping...")
        print("This may take several minutes...")
        print()
        
        start_time = datetime.now()
        
        # Scrape all data
        data = scraper.scrape_all_data()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("✅ Scraping completed!")
        print(f"⏱️  Duration: {duration}")
        print()
        
        # Display results
        print("📊 Results Summary:")
        print(f"   • Total Fighters: {len(data.get('fighters', {}))}")
        print(f"   • Rankings Divisions: {len(data.get('rankings', {}))}")
        print(f"   • Events: {len(data.get('events', []))}")
        print(f"   • Fight History: {len(data.get('fight_history', {}))}")
        print(f"   • Sources Used: {', '.join(data.get('sources', []))}")
        print()
        
        # Save data
        print("💾 Saving data...")
        comprehensive_file, flutter_file, summary_file = scraper.save_data(data)
        
        print()
        print("🎉 Comprehensive scraper V2 completed successfully!")
        print(f"📁 Data files saved:")
        print(f"   • Comprehensive: {comprehensive_file}")
        print(f"   • Flutter App: {flutter_file}")
        print(f"   • Summary: {summary_file}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper._close_driver()

if __name__ == "__main__":
    main()
