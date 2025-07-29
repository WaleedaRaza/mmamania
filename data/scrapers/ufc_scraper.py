#!/usr/bin/env python3
"""
UFC Data Scraper
Scrapes fighter and fight data from various UFC sources
"""

import requests
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UFCScraper:
    """Scraper for UFC fighter and fight data"""
    
    def __init__(self):
        """Initialize the UFC scraper"""
        self.base_url = "https://www.ufc.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
    def _init_driver(self):
        """Initialize Selenium WebDriver for deep scraping"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Selenium WebDriver initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize WebDriver: {e}")
                self.driver = None
                
    def _close_driver(self):
        """Close the Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def scrape_rankings(self) -> List[Dict]:
        """Scrape current UFC rankings from the official rankings page"""
        logger.info("Scraping UFC rankings from official page...")
        
        try:
            url = f"{self.base_url}/rankings"
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = []
            champions_set = set()  # Track champions to prevent duplicates
            
            ranking_sections = soup.find_all('div', class_='view-grouping')
            for section in ranking_sections:
                header = section.find('div', class_='view-grouping-header')
                if not header:
                    continue
                    
                # Fix division name parsing - remove "Top Rank" corruption
                division = header.get_text(strip=True).replace('Top Rank', '').strip()
                logger.info(f"Processing division: {division}")
                
                table = section.find('table')
                if not table:
                    continue
                    
                # Add champion if present in caption
                caption = table.find('caption')
                if caption:
                    champ_info = caption.find('div', class_='rankings--athlete--champion')
                    if champ_info:
                        champ_name_tag = champ_info.find('h5')
                        champ_name = champ_name_tag.get_text(strip=True) if champ_name_tag else None
                        champ_link = champ_name_tag.find('a') if champ_name_tag else None
                        champ_url = champ_link.get('href', '') if champ_link else ''
                        
                        if champ_name:
                            champions_set.add(champ_name)  # Track champion
                            # Get real record from fighter profile
                            champ_record = self.get_fighter_record(champ_url)
                            
                            rankings.append({
                                'id': f"{division.lower().replace(' ', '-').replace('&', 'and')}-champion",
                                'division': division,
                                'rank': 0,
                                'fighter_name': champ_name,
                                'record': champ_record,
                                'wins': champ_record['wins'],
                                'losses': champ_record['losses'],
                                'draws': champ_record['draws'],
                                'fighter_url': champ_url,
                                'rank_change': '',
                                'is_champion': True,
                                'scraped_at': datetime.now().isoformat()
                            })
                            
                tbody = table.find('tbody')
                if not tbody:
                    continue
                    
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        try:
                            rank_cell = cells[0]
                            rank_text = rank_cell.get_text(strip=True)
                            name_cell = cells[1]
                            fighter_link = name_cell.find('a')
                            if not fighter_link:
                                continue
                                
                            fighter_name = fighter_link.get_text(strip=True)
                            fighter_url = fighter_link.get('href', '')
                            
                            if not rank_text or not fighter_name or rank_text == 'NR':
                                continue
                                
                            # Skip if fighter is already champion (prevent duplicates)
                            if fighter_name in champions_set:
                                continue
                                
                            rank = int(rank_text)
                            rank_change = ""
                            if len(cells) >= 3:
                                change_cell = cells[2]
                                change_text = change_cell.get_text(strip=True)
                                if change_text and change_text != "NR":
                                    rank_change = change_text
                                    
                            # Get real record from fighter profile
                            fighter_record = self.get_fighter_record(fighter_url)
                            
                            rankings.append({
                                'id': f"{division.lower().replace(' ', '-').replace('&', 'and')}-{rank}",
                                'division': division,
                                'rank': rank,
                                'fighter_name': fighter_name,
                                'record': fighter_record,
                                'wins': fighter_record['wins'],
                                'losses': fighter_record['losses'],
                                'draws': fighter_record['draws'],
                                'fighter_url': fighter_url,
                                'rank_change': rank_change,
                                'is_champion': False,
                                'scraped_at': datetime.now().isoformat()
                            })
                            
                        except Exception as e:
                            logger.warning(f"Error parsing row: {e}")
                            continue
                            
            logger.info(f"Scraped {len(rankings)} rankings")
            return rankings
            
        except Exception as e:
            logger.error(f"Error scraping rankings: {e}")
            return []
    
    def get_upcoming_events(self) -> List[Dict]:
        """Scrape upcoming UFC events"""
        logger.info("Scraping upcoming UFC events...")
        
        events = []
        try:
            url = f"{self.base_url}/events"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find upcoming events
            event_cards = soup.find_all('div', {'class': 'c-card-event'})
            
            for card in event_cards:
                try:
                    event_data = self._parse_event_card(card)
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    logger.error(f"Error parsing event card: {e}")
                    
        except Exception as e:
            logger.error(f"Error scraping upcoming events: {e}")
            
        return events
    
    def _parse_event_card(self, card) -> Optional[Dict]:
        """Parse individual event card"""
        try:
            # Event title
            title_elem = card.find('h3', {'class': 'c-card-event__title'})
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Event"
            
            # Event date
            date_elem = card.find('time')
            date_str = date_elem.get_text(strip=True) if date_elem else None
            
            # Event URL
            link_elem = card.find('a')
            event_url = link_elem['href'] if link_elem else None
            
            # Location
            location_elem = card.find('div', {'class': 'c-card-event__location'})
            location = location_elem.get_text(strip=True) if location_elem else "TBD"
            
            return {
                'title': title,
                'date': date_str,
                'location': location,
                'event_url': event_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing event card: {e}")
            return None
    
    def get_event_fights(self, event_url: str) -> List[Dict]:
        """Scrape fights for a specific event"""
        logger.info(f"Scraping fights for event: {event_url}")
        
        fights = []
        try:
            url = f"{self.base_url}{event_url}"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find fight cards
            fight_cards = soup.find_all('div', {'class': 'c-listing-fight'})
            
            for card in fight_cards:
                try:
                    fight_data = self._parse_fight_card(card)
                    if fight_data:
                        fights.append(fight_data)
                except Exception as e:
                    logger.error(f"Error parsing fight card: {e}")
                    
        except Exception as e:
            logger.error(f"Error scraping event fights: {e}")
            
        return fights
    
    def _parse_fight_card(self, card) -> Optional[Dict]:
        """Parse individual fight card"""
        try:
            # Fight type (Main Card, Prelims, etc.)
            fight_type_elem = card.find('div', {'class': 'c-listing-fight__class-text'})
            fight_type = fight_type_elem.get_text(strip=True) if fight_type_elem else "Unknown"
            
            # Weight class
            weight_elem = card.find('div', {'class': 'c-listing-fight__class-text'})
            weight_class = weight_elem.get_text(strip=True) if weight_elem else "Unknown"
            
            # Fighters
            fighter_elems = card.find_all('div', {'class': 'c-listing-fight__corner-name'})
            fighter1 = fighter_elems[0].get_text(strip=True) if len(fighter_elems) > 0 else "TBD"
            fighter2 = fighter_elems[1].get_text(strip=True) if len(fighter_elems) > 1 else "TBD"
            
            # Records
            record_elems = card.find_all('div', {'class': 'c-listing-fight__corner-record'})
            record1 = record_elems[0].get_text(strip=True) if len(record_elems) > 0 else "N/A"
            record2 = record_elems[1].get_text(strip=True) if len(record_elems) > 1 else "N/A"
            
            return {
                'fight_type': fight_type,
                'weight_class': weight_class,
                'fighter1': {
                    'name': fighter1,
                    'record': record1
                },
                'fighter2': {
                    'name': fighter2,
                    'record': record2
                },
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing fight card: {e}")
            return None
    
    def get_fighter_stats(self, fighter_url: str) -> Optional[Dict]:
        """Scrape detailed fighter statistics"""
        logger.info(f"Scraping fighter stats: {fighter_url}")
        
        try:
            url = f"{self.base_url}{fighter_url}"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Fighter name
            name_elem = soup.find('h1', {'class': 'hero-content__title'})
            name = name_elem.get_text(strip=True) if name_elem else "Unknown"
            
            # Record
            record_elem = soup.find('div', {'class': 'hero-content__record'})
            record = record_elem.get_text(strip=True) if record_elem else "N/A"
            
            # Stats
            stats = {}
            stat_elems = soup.find_all('div', {'class': 'c-overlap__stats-group'})
            
            for stat_group in stat_elems:
                try:
                    stat_title = stat_group.find('div', {'class': 'c-overlap__stats-text'})
                    stat_value = stat_group.find('div', {'class': 'c-overlap__stats-value'})
                    
                    if stat_title and stat_value:
                        title = stat_title.get_text(strip=True)
                        value = stat_value.get_text(strip=True)
                        stats[title] = value
                except Exception as e:
                    logger.error(f"Error parsing stat group: {e}")
            
            return {
                'name': name,
                'record': record,
                'stats': stats,
                'fighter_url': fighter_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping fighter stats: {e}")
            return None
    
    def get_past_events(self, limit: int = 10) -> List[Dict]:
        """Scrape past UFC events"""
        logger.info(f"Scraping past {limit} UFC events...")
        
        events = []
        try:
            url = f"{self.base_url}/events"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find past events (they might be in a different section)
            past_event_cards = soup.find_all('div', {'class': 'c-card-event--past'})
            
            for i, card in enumerate(past_event_cards[:limit]):
                try:
                    event_data = self._parse_past_event_card(card)
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    logger.error(f"Error parsing past event card: {e}")
                    
        except Exception as e:
            logger.error(f"Error scraping past events: {e}")
            
        return events
    
    def _parse_past_event_card(self, card) -> Optional[Dict]:
        """Parse past event card with results"""
        try:
            # Event title
            title_elem = card.find('h3', {'class': 'c-card-event__title'})
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Event"
            
            # Event date
            date_elem = card.find('time')
            date_str = date_elem.get_text(strip=True) if date_elem else None
            
            # Event URL
            link_elem = card.find('a')
            event_url = link_elem['href'] if link_elem else None
            
            # Location
            location_elem = card.find('div', {'class': 'c-card-event__location'})
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            return {
                'title': title,
                'date': date_str,
                'location': location,
                'event_url': event_url,
                'type': 'past',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing past event card: {e}")
            return None
    
    def get_fight_results(self, event_url: str) -> List[Dict]:
        """Scrape fight results for a past event"""
        logger.info(f"Scraping fight results for event: {event_url}")
        
        results = []
        try:
            url = f"{self.base_url}{event_url}"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find completed fights
            fight_cards = soup.find_all('div', {'class': 'c-listing-fight--featured'})
            
            for card in fight_cards:
                try:
                    result_data = self._parse_fight_result(card)
                    if result_data:
                        results.append(result_data)
                except Exception as e:
                    logger.error(f"Error parsing fight result: {e}")
                    
        except Exception as e:
            logger.error(f"Error scraping fight results: {e}")
            
        return results
    
    def _parse_fight_result(self, card) -> Optional[Dict]:
        """Parse individual fight result"""
        try:
            # Weight class
            weight_elem = card.find('div', {'class': 'c-listing-fight__class-text'})
            weight_class = weight_elem.get_text(strip=True) if weight_elem else "Unknown"
            
            # Fighters
            fighter_elems = card.find_all('div', {'class': 'c-listing-fight__corner-name'})
            fighter1 = fighter_elems[0].get_text(strip=True) if len(fighter_elems) > 0 else "Unknown"
            fighter2 = fighter_elems[1].get_text(strip=True) if len(fighter_elems) > 1 else "Unknown"
            
            # Winner (look for winner indicator)
            winner_elem = card.find('div', {'class': 'c-listing-fight__corner--winner'})
            winner = None
            if winner_elem:
                winner_name = winner_elem.find('div', {'class': 'c-listing-fight__corner-name'})
                winner = winner_name.get_text(strip=True) if winner_name else None
            
            # Method and round
            method_elem = card.find('div', {'class': 'c-listing-fight__result-text'})
            method = method_elem.get_text(strip=True) if method_elem else "Unknown"
            
            return {
                'weight_class': weight_class,
                'fighter1': fighter1,
                'fighter2': fighter2,
                'winner': winner,
                'method': method,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing fight result: {e}")
            return None
    
    def scrape_all_data(self) -> Dict:
        """Scrape all UFC data including rankings and fighter profiles"""
        logger.info("Starting comprehensive UFC data scraping...")
        
        all_data = {
            'rankings': [],
            'fighters': [],
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # 1. Scrape rankings first
            logger.info("Step 1: Scraping UFC rankings...")
            rankings = self.scrape_rankings()
            all_data['rankings'] = rankings
            logger.info(f"✅ Scraped {len(rankings)} rankings")
            
            # 2. Scrape detailed fighter profiles for top fighters
            logger.info("Step 2: Scraping detailed fighter profiles...")
            fighters = []
            
            # Get unique fighter URLs from rankings
            fighter_urls = set()
            for ranking in rankings:
                if ranking.get('fighter_url'):
                    fighter_urls.add(ranking['fighter_url'])
            
            logger.info(f"Found {len(fighter_urls)} unique fighters to profile")
            
            # Scrape detailed profiles for each fighter
            for i, fighter_url in enumerate(fighter_urls, 1):
                try:
                    logger.info(f"Scraping fighter profile {i}/{len(fighter_urls)}: {fighter_url}")
                    
                    # Get detailed fighter profile
                    fighter_profile = self.get_deep_fighter_profile(fighter_url)
                    
                    if fighter_profile and fighter_profile.get('name'):
                        # Merge ranking data with profile data
                        ranking_data = next((r for r in rankings if r.get('fighter_url') == fighter_url), {})
                        
                        fighter_data = {
                            'id': fighter_profile.get('id', ''),
                            'name': fighter_profile.get('name', ''),
                            'division': fighter_profile.get('division', ranking_data.get('division', '')),
                            'record': fighter_profile.get('record', {'wins': 0, 'losses': 0, 'draws': 0}),
                            'image_url': None,  # UFC doesn't provide direct image URLs
                            'status': 'Active',
                            'place_of_birth': fighter_profile.get('personal_info', {}).get('place_of_birth'),
                            'training_at': fighter_profile.get('personal_info', {}).get('training_at'),
                            'fighting_style': fighter_profile.get('personal_info', {}).get('fighting_style'),
                            'age': fighter_profile.get('personal_info', {}).get('age'),
                            'height': fighter_profile.get('personal_info', {}).get('height'),
                            'weight': fighter_profile.get('personal_info', {}).get('weight'),
                            'octagon_debut': fighter_profile.get('personal_info', {}).get('octagon_debut'),
                            'reach': fighter_profile.get('personal_info', {}).get('reach'),
                            'leg_reach': fighter_profile.get('personal_info', {}).get('leg_reach'),
                            'stats': fighter_profile.get('stats', {}),
                            'fight_history': fighter_profile.get('fight_history', []),
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        fighters.append(fighter_data)
                        logger.info(f"✅ Scraped profile for {fighter_data['name']}")
                    else:
                        logger.warning(f"❌ Failed to get profile for {fighter_url}")
                        
                except Exception as e:
                    logger.error(f"❌ Error scraping fighter profile {fighter_url}: {e}")
                    continue
                
                # Be respectful to the server
                time.sleep(2)
            
            all_data['fighters'] = fighters
            logger.info(f"✅ Scraped {len(fighters)} detailed fighter profiles")
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive scraping: {e}")
        finally:
            # Clean up WebDriver
            self._close_driver()
        
        logger.info(f"🎉 Comprehensive scraping complete! Total: {len(all_data['rankings'])} rankings, {len(all_data['fighters'])} fighters")
        return all_data
    
    def get_deep_fighter_profile(self, fighter_url: str) -> Dict:
        """Get comprehensive fighter profile data using Selenium"""
        if not fighter_url:
            return {}
            
        self._init_driver()
        if not self.driver:
            logger.error("WebDriver not available for deep scraping")
            return {}
            
        try:
            full_url = f"{self.base_url}{fighter_url}" if fighter_url.startswith('/') else fighter_url
            logger.info(f"Scraping fighter profile: {full_url}")
            
            self.driver.get(full_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hero-content"))
            )
            
            # Extract all fighter data
            fighter_data = {
                'id': fighter_url.split('/')[-1] if '/' in fighter_url else fighter_url,
                'name': self._extract_fighter_name(),
                'record': self._extract_fighter_record(),
                'division': self._extract_fighter_division(),
                'stats': self._extract_detailed_stats(),
                'fight_history': self._extract_fight_history(),
                'personal_info': self._extract_personal_info(),
                'scraped_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully scraped profile for {fighter_data['name']}")
            return fighter_data
            
        except Exception as e:
            logger.error(f"Error scraping fighter profile {fighter_url}: {e}")
            return {}
        finally:
            time.sleep(1)  # Be respectful to the server
    
    def _extract_fighter_name(self) -> str:
        """Extract fighter name from profile page"""
        try:
            name_elem = self.driver.find_element(By.CSS_SELECTOR, ".hero-content h1")
            return name_elem.text.strip()
        except:
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, ".hero-content .hero-content__title")
                return name_elem.text.strip()
            except:
                return "Unknown Fighter"
    
    def _extract_fighter_record(self) -> Dict:
        """Extract fighter record from profile page"""
        try:
            record_elem = self.driver.find_element(By.CSS_SELECTOR, ".hero-content .hero-content__record")
            record_text = record_elem.text.strip()
            
            # Parse record like "25-1-0" or "25-1"
            parts = record_text.split('-')
            if len(parts) >= 2:
                wins = int(parts[0]) if parts[0].isdigit() else 0
                losses = int(parts[1]) if parts[1].isdigit() else 0
                draws = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                return {'wins': wins, 'losses': losses, 'draws': draws}
        except:
            pass
        
        return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def _extract_fighter_division(self) -> str:
        """Extract fighter division from profile page"""
        try:
            # Try multiple selectors for division
            selectors = [
                ".hero-content .hero-content__division",
                ".hero-content .hero-content__weight-class",
                ".hero-content .hero-content__category",
                ".hero-content [data-weight-class]"
            ]
            
            for selector in selectors:
                try:
                    div_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    division = div_elem.text.strip()
                    if division:
                        return division
                except:
                    continue
                    
            # Try to find division in the page content
            page_text = self.driver.page_source
            divisions = ['Heavyweight', 'Light Heavyweight', 'Middleweight', 'Welterweight', 
                        'Lightweight', 'Featherweight', 'Bantamweight', 'Flyweight', 
                        'Women\'s Bantamweight', 'Women\'s Flyweight', 'Women\'s Strawweight',
                        'Women\'s Featherweight']
            
            for division in divisions:
                if division.lower() in page_text.lower():
                    return division
                    
        except:
            pass
        
        return "Unknown Division"
    
    def _extract_detailed_stats(self) -> Dict:
        """Extract detailed fighter statistics"""
        stats = {
            'fight_win_streak': 0,
            'wins_by_knockout': 0,
            'wins_by_submission': 0,
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
            stats_sections = self.driver.find_elements(By.CSS_SELECTOR, ".stats-section, .fighter-stats, .statistics")
            
            for section in stats_sections:
                section_text = section.text.lower()
                
                # Extract win streak
                if 'win streak' in section_text or 'streak' in section_text:
                    streak_match = re.search(r'(\d+)\s*(?:fight\s*)?win\s*streak', section_text)
                    if streak_match:
                        stats['fight_win_streak'] = int(streak_match.group(1))
                
                # Extract KO wins
                ko_match = re.search(r'(\d+)\s*(?:wins?\s*)?by\s*(?:t)?ko', section_text)
                if ko_match:
                    stats['wins_by_knockout'] = int(ko_match.group(1))
                
                # Extract submission wins
                sub_match = re.search(r'(\d+)\s*(?:wins?\s*)?by\s*submission', section_text)
                if sub_match:
                    stats['wins_by_submission'] = int(sub_match.group(1))
                
                # Extract striking accuracy
                acc_match = re.search(r'striking\s*accuracy[:\s]*(\d+(?:\.\d+)?)', section_text)
                if acc_match:
                    stats['striking_accuracy'] = float(acc_match.group(1))
                
                # Extract significant strikes
                sig_match = re.search(r'significant\s*strikes[:\s]*(\d+)/(\d+)', section_text)
                if sig_match:
                    stats['sig_strikes_landed'] = int(sig_match.group(1))
                    stats['sig_strikes_attempted'] = int(sig_match.group(2))
                
                # Extract takedown accuracy
                td_acc_match = re.search(r'takedown\s*accuracy[:\s]*(\d+(?:\.\d+)?)', section_text)
                if td_acc_match:
                    stats['takedown_accuracy'] = float(td_acc_match.group(1))
                
                # Extract takedowns
                td_match = re.search(r'takedowns[:\s]*(\d+)/(\d+)', section_text)
                if td_match:
                    stats['takedowns_landed'] = int(td_match.group(1))
                    stats['takedowns_attempted'] = int(td_match.group(2))
                
                # Extract strikes per minute
                spm_match = re.search(r'(\d+(?:\.\d+)?)\s*strikes?\s*per\s*min', section_text)
                if spm_match:
                    stats['sig_strikes_landed_per_min'] = float(spm_match.group(1))
                
                # Extract strikes absorbed per minute
                sapm_match = re.search(r'(\d+(?:\.\d+)?)\s*absorbed\s*per\s*min', section_text)
                if sapm_match:
                    stats['sig_strikes_absorbed_per_min'] = float(sapm_match.group(1))
                
                # Extract takedown average
                td_avg_match = re.search(r'(\d+(?:\.\d+)?)\s*takedowns?\s*per\s*15', section_text)
                if td_avg_match:
                    stats['takedown_avg_per_15_min'] = float(td_avg_match.group(1))
                
                # Extract submission average
                sub_avg_match = re.search(r'(\d+(?:\.\d+)?)\s*submissions?\s*per\s*15', section_text)
                if sub_avg_match:
                    stats['submission_avg_per_15_min'] = float(sub_avg_match.group(1))
                
                # Extract striking defense
                def_match = re.search(r'striking\s*defense[:\s]*(\d+(?:\.\d+)?)', section_text)
                if def_match:
                    stats['sig_strikes_defense'] = float(def_match.group(1))
                
                # Extract takedown defense
                td_def_match = re.search(r'takedown\s*defense[:\s]*(\d+(?:\.\d+)?)', section_text)
                if td_def_match:
                    stats['takedown_defense'] = float(td_def_match.group(1))
                
                # Extract knockdown average
                kd_match = re.search(r'(\d+(?:\.\d+)?)\s*knockdowns?\s*per\s*15', section_text)
                if kd_match:
                    stats['knockdown_avg'] = float(kd_match.group(1))
                
                # Extract average fight time
                time_match = re.search(r'average\s*fight\s*time[:\s]*(\d+:\d+)', section_text)
                if time_match:
                    stats['average_fight_time'] = time_match.group(1)
                    
        except Exception as e:
            logger.warning(f"Error extracting detailed stats: {e}")
        
        return stats
    
    def _extract_fight_history(self) -> List[Dict]:
        """Extract fighter's fight history"""
        fight_history = []
        
        try:
            # Look for fight history section
            history_sections = self.driver.find_elements(By.CSS_SELECTOR, ".fight-history, .results, .last-fights")
            
            for section in history_sections:
                fight_items = section.find_elements(By.CSS_SELECTOR, ".fight-item, .result-item, .fight")
                
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
    
    def _parse_fight_history_item(self, item) -> Dict:
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
            opponent_selectors = [".opponent", ".fighter-name", ".name"]
            for selector in opponent_selectors:
                try:
                    opp_elem = item.find_element(By.CSS_SELECTOR, selector)
                    fight_data['opponent'] = opp_elem.text.strip()
                    break
                except:
                    continue
            
            # Extract result (Win/Loss/Draw)
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
            event_selectors = [".event", ".card", ".show"]
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
            return {}
    
    def _extract_personal_info(self) -> Dict:
        """Extract fighter's personal information"""
        personal_info = {
            'age': None,
            'height': None,
            'weight': None,
            'reach': None,
            'leg_reach': None,
            'place_of_birth': None,
            'training_at': None,
            'fighting_style': None,
            'octagon_debut': None
        }
        
        try:
            # Look for personal info sections
            info_sections = self.driver.find_elements(By.CSS_SELECTOR, ".personal-info, .fighter-info, .bio")
            
            for section in info_sections:
                section_text = section.text.lower()
                
                # Extract age
                age_match = re.search(r'age[:\s]*(\d+)', section_text)
                if age_match:
                    personal_info['age'] = int(age_match.group(1))
                
                # Extract height
                height_match = re.search(r'height[:\s]*(\d+)\'(\d+)"', section_text)
                if height_match:
                    feet = int(height_match.group(1))
                    inches = int(height_match.group(2))
                    personal_info['height'] = feet * 12 + inches  # Convert to inches
                
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
                
                # Extract place of birth
                birth_match = re.search(r'born[:\s]*([^,\n]+)', section_text)
                if birth_match:
                    personal_info['place_of_birth'] = birth_match.group(1).strip()
                
                # Extract training location
                training_match = re.search(r'training[:\s]*([^,\n]+)', section_text)
                if training_match:
                    personal_info['training_at'] = training_match.group(1).strip()
                
                # Extract fighting style
                style_match = re.search(r'style[:\s]*([^,\n]+)', section_text)
                if style_match:
                    personal_info['fighting_style'] = style_match.group(1).strip()
                
                # Extract octagon debut
                debut_match = re.search(r'debut[:\s]*([^,\n]+)', section_text)
                if debut_match:
                    personal_info['octagon_debut'] = debut_match.group(1).strip()
                    
        except Exception as e:
            logger.warning(f"Error extracting personal info: {e}")
        
        return personal_info
    
    def get_fighter_record(self, fighter_url: str) -> Dict:
        """Scrape fighter record from individual profile page"""
        try:
            if not fighter_url:
                return {'wins': 0, 'losses': 0, 'draws': 0}
                
            full_url = f"{self.base_url}{fighter_url}"
            response = self.session.get(full_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use the correct selector found from debugging
            record_elem = soup.select_one('p.hero-profile__division-body')
            
            if record_elem:
                record_text = record_elem.text.strip()
                # Parse record like "27-1-0 (W-L-D)" or "25-3"
                if '(' in record_text:
                    # Extract just the numbers before the parentheses
                    record_part = record_text.split('(')[0].strip()
                else:
                    record_part = record_text
                
                parts = record_part.split('-')
                if len(parts) >= 2:
                    wins = int(parts[0]) if parts[0].isdigit() else 0
                    losses = int(parts[1]) if parts[1].isdigit() else 0
                    draws = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                    return {'wins': wins, 'losses': losses, 'draws': draws}
            
            logger.warning(f"No record found for {fighter_url}")
            return {'wins': 0, 'losses': 0, 'draws': 0}
            
        except Exception as e:
            logger.error(f"Error scraping record for {fighter_url}: {e}")
            return {'wins': 0, 'losses': 0, 'draws': 0}

def main():
    """Main function to test the scraper"""
    scraper = UFCScraper()
    
    # Test individual functions
    print("Testing UFC Scraper...")
    
    # Get comprehensive data
    all_data = scraper.scrape_all_data()
    print(f"Comprehensive scrape completed: {len(all_data)} data points")
    
    # Save to JSON file
    with open('ufc_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print("Data saved to ufc_data.json")

if __name__ == "__main__":
    main() 