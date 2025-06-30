#!/usr/bin/env python3
"""
Enhanced UFC Data Scraper
Comprehensive scraping with proper champion handling and detailed fighter profiles
"""

import requests
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
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

class EnhancedUFCScraper:
    """Enhanced scraper for UFC data with proper champion handling"""
    
    def __init__(self):
        self.base_url = "https://www.ufc.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
    
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
    
    def scrape_rankings_with_champions(self) -> List[Dict]:
        """Scrape UFC rankings with proper champion identification"""
        logger.info("Scraping UFC rankings with champion detection...")
        
        try:
            url = f"{self.base_url}/rankings"
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = []
            
            # Find all division sections
            division_sections = soup.find_all('div', class_='view-grouping')
            
            for section in division_sections:
                # Extract division name
                header = section.find('div', class_='view-grouping-header')
                if not header:
                    continue
                    
                division = header.get_text(strip=True)
                logger.info(f"Processing division: {division}")
                
                # Find the rankings table
                table = section.find('table')
                if not table:
                    continue
                
                # Look for champion in caption or special section
                champion = self._extract_champion_from_section(section, division)
                if champion:
                    rankings.append(champion)
                
                # Extract ranked fighters
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    for row in rows:
                        ranking = self._extract_ranking_from_row(row, division)
                        if ranking:
                            rankings.append(ranking)
            
            logger.info(f"Scraped {len(rankings)} rankings including champions")
            return rankings
            
        except Exception as e:
            logger.error(f"Error scraping rankings: {e}")
            return []
    
    def _extract_champion_from_section(self, section, division: str) -> Optional[Dict]:
        """Extract champion information from a division section"""
        try:
            # Look for champion in caption
            caption = section.find('caption')
            if caption:
                champ_info = caption.find('div', class_='rankings--athlete--champion')
                if champ_info:
                    champ_name_tag = champ_info.find('h5')
                    if champ_name_tag:
                        champ_name = champ_name_tag.get_text(strip=True)
                        champ_link = champ_name_tag.find('a')
                        champ_url = champ_link.get('href', '') if champ_link else ''
                        
                        # Extract record from champion section
                        record = self._extract_record_from_section(champ_info)
                        
                        return {
                            'id': f"{division.lower().replace(' ', '-')}-champion",
                            'division': division,
                            'rank': 0,
                            'fighter_name': champ_name,
                            'record': record,
                            'fighter_url': champ_url,
                            'fighter_id': champ_url.split('/')[-1] if champ_url else '',
                            'is_champion': True,
                            'rank_change': '',
                            'scraped_at': datetime.now().isoformat()
                        }
            
            # Look for champion in special champion section
            champ_section = section.find('div', class_='rankings--champion')
            if champ_section:
                champ_name_elem = champ_section.find('h5')
                if champ_name_elem:
                    champ_name = champ_name_elem.get_text(strip=True)
                    champ_link = champ_name_elem.find('a')
                    champ_url = champ_link.get('href', '') if champ_link else ''
                    
                    # Extract record from champion section
                    record = self._extract_record_from_section(champ_section)
                    
                    return {
                        'id': f"{division.lower().replace(' ', '-')}-champion",
                        'division': division,
                        'rank': 0,
                        'fighter_name': champ_name,
                        'record': record,
                        'fighter_url': champ_url,
                        'fighter_id': champ_url.split('/')[-1] if champ_url else '',
                        'is_champion': True,
                        'rank_change': '',
                        'scraped_at': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.warning(f"Error extracting champion for {division}: {e}")
        
        return None
    
    def _extract_record_from_section(self, section) -> Dict:
        """Extract fighter record from a section"""
        try:
            section_text = section.get_text()
            
            # Pattern 1: "27-1-0" or "27-1" format
            record_match = re.search(r'(\d+)-(\d+)-(\d+)', section_text)
            if record_match:
                wins = int(record_match.group(1))
                losses = int(record_match.group(2))
                draws = int(record_match.group(3))
                return {'wins': wins, 'losses': losses, 'draws': draws}
            
            # Pattern 2: "27-1" format (no draws)
            record_match = re.search(r'(\d+)-(\d+)(?!\d)', section_text)
            if record_match:
                wins = int(record_match.group(1))
                losses = int(record_match.group(2))
                return {'wins': wins, 'losses': losses, 'draws': 0}
            
        except Exception as e:
            logger.warning(f"Error extracting record from section: {e}")
        
        # Default fallback
        return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def _extract_ranking_from_row(self, row, division: str) -> Optional[Dict]:
        """Extract ranking information from a table row"""
        try:
            cells = row.find_all('td')
            if len(cells) < 2:
                return None
            
            # Extract rank
            rank_cell = cells[0]
            rank_text = rank_cell.get_text(strip=True)
            if not rank_text or rank_text == 'NR':
                return None
            
            rank = int(rank_text)
            
            # Extract fighter name and URL
            name_cell = cells[1]
            fighter_link = name_cell.find('a')
            if not fighter_link:
                return None
            
            fighter_name = fighter_link.get_text(strip=True)
            fighter_url = fighter_link.get('href', '')
            
            # Extract record from the row
            record = self._extract_record_from_row(row)
            
            # Extract rank change
            rank_change = ""
            if len(cells) >= 3:
                change_cell = cells[2]
                change_text = change_cell.get_text(strip=True)
                if change_text and change_text != "NR":
                    rank_change = change_text
            
            return {
                'id': f"{division.lower().replace(' ', '-')}-{rank}",
                'division': division,
                'rank': rank,
                'fighter_name': fighter_name,
                'record': record,
                'fighter_url': fighter_url,
                'fighter_id': fighter_url.split('/')[-1] if fighter_url else '',
                'is_champion': False,
                'rank_change': rank_change,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing ranking row: {e}")
            return None
    
    def _extract_record_from_row(self, row) -> Dict:
        """Extract fighter record from a table row"""
        try:
            # Look for record in various possible locations
            row_text = row.get_text()
            
            # Pattern 1: "27-1-0" or "27-1" format
            record_match = re.search(r'(\d+)-(\d+)-(\d+)', row_text)
            if record_match:
                wins = int(record_match.group(1))
                losses = int(record_match.group(2))
                draws = int(record_match.group(3))
                return {'wins': wins, 'losses': losses, 'draws': draws}
            
            # Pattern 2: "27-1" format (no draws)
            record_match = re.search(r'(\d+)-(\d+)(?!\d)', row_text)
            if record_match:
                wins = int(record_match.group(1))
                losses = int(record_match.group(2))
                return {'wins': wins, 'losses': losses, 'draws': 0}
            
            # Pattern 3: Look for record in specific cells
            cells = row.find_all('td')
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                record_match = re.search(r'(\d+)-(\d+)-(\d+)', cell_text)
                if record_match:
                    wins = int(record_match.group(1))
                    losses = int(record_match.group(2))
                    draws = int(record_match.group(3))
                    return {'wins': wins, 'losses': losses, 'draws': draws}
                
                record_match = re.search(r'(\d+)-(\d+)(?!\d)', cell_text)
                if record_match:
                    wins = int(record_match.group(1))
                    losses = int(record_match.group(2))
                    return {'wins': wins, 'losses': losses, 'draws': 0}
            
        except Exception as e:
            logger.warning(f"Error extracting record from row: {e}")
        
        # Default fallback
        return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def scrape_fighter_profiles(self, fighter_urls: List[str], limit: int = 50) -> List[Dict]:
        """Scrape detailed fighter profiles"""
        logger.info(f"Scraping detailed profiles for {min(len(fighter_urls), limit)} fighters...")
        
        self._init_driver()
        if not self.driver:
            logger.error("WebDriver not available for profile scraping")
            return []
        
        fighters = []
        processed_count = 0
        
        for fighter_url in fighter_urls[:limit]:
            try:
                logger.info(f"Scraping profile {processed_count + 1}/{min(len(fighter_urls), limit)}: {fighter_url}")
                
                profile = self._scrape_single_fighter_profile(fighter_url)
                if profile:
                    fighters.append(profile)
                    logger.info(f"✅ Scraped profile for {profile.get('name', 'Unknown')}")
                else:
                    logger.warning(f"❌ Failed to scrape profile for {fighter_url}")
                
                processed_count += 1
                time.sleep(2)  # Be respectful to the server
                
            except Exception as e:
                logger.error(f"❌ Error scraping profile {fighter_url}: {e}")
                continue
        
        self._close_driver()
        logger.info(f"Completed profile scraping: {len(fighters)} successful profiles")
        return fighters
    
    def _scrape_single_fighter_profile(self, fighter_url: str) -> Optional[Dict]:
        """Scrape a single fighter's detailed profile"""
        try:
            full_url = f"{self.base_url}{fighter_url}" if fighter_url.startswith('/') else fighter_url
            
            self.driver.get(full_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract basic info
            name = self._extract_fighter_name()
            record = self._extract_fighter_record()
            division = self._extract_fighter_division()
            
            # Extract detailed stats
            stats = self._extract_detailed_stats()
            
            # Extract personal info
            personal_info = self._extract_personal_info()
            
            # Extract fight history
            fight_history = self._extract_fight_history()
            
            fighter_id = fighter_url.split('/')[-1] if '/' in fighter_url else fighter_url
            
            return {
                'id': fighter_id,
                'name': name,
                'division': division,
                'record': record,
                'stats': stats,
                'personal_info': personal_info,
                'fight_history': fight_history,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping fighter profile {fighter_url}: {e}")
            return None
    
    def _extract_fighter_name(self) -> str:
        """Extract fighter name from profile page"""
        try:
            name_selectors = [
                ".hero-content h1",
                ".hero-content .hero-content__title",
                "h1",
                ".fighter-name"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name and name != "Skip to main content":
                        return name
                except:
                    continue
            
            return "Unknown Fighter"
        except:
            return "Unknown Fighter"
    
    def _extract_fighter_record(self) -> Dict:
        """Extract fighter record from profile page"""
        try:
            record_selectors = [
                ".hero-content .hero-content__record",
                ".fighter-record",
                ".record"
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
                        return {'wins': wins, 'losses': losses, 'draws': draws}
                except:
                    continue
            
            return {'wins': 0, 'losses': 0, 'draws': 0}
        except:
            return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def _extract_fighter_division(self) -> str:
        """Extract fighter division from profile page"""
        try:
            division_selectors = [
                ".hero-content .hero-content__division",
                ".hero-content .hero-content__weight-class",
                ".fighter-division",
                ".weight-class"
            ]
            
            for selector in division_selectors:
                try:
                    div_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    division = div_elem.text.strip()
                    if division:
                        return division
                except:
                    continue
            
            # Try to find division in page content
            page_text = self.driver.page_source
            divisions = [
                'Heavyweight', 'Light Heavyweight', 'Middleweight', 'Welterweight',
                'Lightweight', 'Featherweight', 'Bantamweight', 'Flyweight',
                "Women's Bantamweight", "Women's Flyweight", "Women's Strawweight",
                "Women's Featherweight", "Men's Pound for Pound", "Women's Pound for Pound"
            ]
            
            for division in divisions:
                if division.lower() in page_text.lower():
                    return division
            
            return "Unknown Division"
        except:
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
                
                # Extract various stats using regex patterns
                patterns = {
                    'fight_win_streak': r'(\d+)\s*(?:fight\s*)?win\s*streak',
                    'wins_by_knockout': r'(\d+)\s*(?:wins?\s*)?by\s*(?:t)?ko',
                    'wins_by_submission': r'(\d+)\s*(?:wins?\s*)?by\s*submission',
                    'striking_accuracy': r'striking\s*accuracy[:\s]*(\d+(?:\.\d+)?)',
                    'takedown_accuracy': r'takedown\s*accuracy[:\s]*(\d+(?:\.\d+)?)',
                    'sig_strikes_landed_per_min': r'(\d+(?:\.\d+)?)\s*strikes?\s*per\s*min',
                    'sig_strikes_absorbed_per_min': r'(\d+(?:\.\d+)?)\s*absorbed\s*per\s*min',
                    'takedown_avg_per_15_min': r'(\d+(?:\.\d+)?)\s*takedowns?\s*per\s*15',
                    'submission_avg_per_15_min': r'(\d+(?:\.\d+)?)\s*submissions?\s*per\s*15',
                    'striking_defense': r'striking\s*defense[:\s]*(\d+(?:\.\d+)?)',
                    'takedown_defense': r'takedown\s*defense[:\s]*(\d+(?:\.\d+)?)',
                    'knockdown_avg': r'(\d+(?:\.\d+)?)\s*knockdowns?\s*per\s*15',
                    'average_fight_time': r'average\s*fight\s*time[:\s]*(\d+:\d+)'
                }
                
                for stat_name, pattern in patterns.items():
                    match = re.search(pattern, section_text)
                    if match:
                        try:
                            if stat_name in ['striking_accuracy', 'takedown_accuracy', 'striking_defense', 'takedown_defense']:
                                stats[stat_name] = float(match.group(1))
                            elif stat_name in ['fight_win_streak', 'wins_by_knockout', 'wins_by_submission']:
                                stats[stat_name] = int(match.group(1))
                            elif stat_name in ['sig_strikes_landed_per_min', 'sig_strikes_absorbed_per_min', 'takedown_avg_per_15_min', 'submission_avg_per_15_min', 'knockdown_avg']:
                                stats[stat_name] = float(match.group(1))
                            elif stat_name == 'average_fight_time':
                                stats[stat_name] = match.group(1)
                        except:
                            continue
                            
        except Exception as e:
            logger.warning(f"Error extracting detailed stats: {e}")
        
        return stats
    
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
                
                # Extract various personal info using regex patterns
                patterns = {
                    'age': r'age[:\s]*(\d+)',
                    'height': r'height[:\s]*(\d+)\'(\d+)"',
                    'weight': r'weight[:\s]*(\d+)\s*lbs?',
                    'reach': r'reach[:\s]*(\d+)"',
                    'leg_reach': r'leg\s*reach[:\s]*(\d+)"',
                    'place_of_birth': r'born[:\s]*([^,\n]+)',
                    'training_at': r'training[:\s]*([^,\n]+)',
                    'fighting_style': r'style[:\s]*([^,\n]+)',
                    'octagon_debut': r'debut[:\s]*([^,\n]+)'
                }
                
                for info_name, pattern in patterns.items():
                    match = re.search(pattern, section_text)
                    if match:
                        try:
                            if info_name == 'height':
                                feet = int(match.group(1))
                                inches = int(match.group(2))
                                personal_info[info_name] = feet * 12 + inches
                            elif info_name in ['age', 'weight', 'reach', 'leg_reach']:
                                personal_info[info_name] = int(match.group(1))
                            else:
                                personal_info[info_name] = match.group(1).strip()
                        except:
                            continue
                            
        except Exception as e:
            logger.warning(f"Error extracting personal info: {e}")
        
        return personal_info
    
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
    
    def scrape_comprehensive_data(self) -> Dict:
        """Scrape comprehensive UFC data with rankings and fighter profiles"""
        logger.info("Starting comprehensive UFC data scraping...")
        
        all_data = {
            'rankings': [],
            'fighters': [],
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # 1. Scrape rankings with champions
            logger.info("Step 1: Scraping rankings with champion detection...")
            rankings = self.scrape_rankings_with_champions()
            all_data['rankings'] = rankings
            logger.info(f"✅ Scraped {len(rankings)} rankings")
            
            # 2. Create basic fighter profiles from rankings
            logger.info("Step 2: Creating basic fighter profiles...")
            fighters = []
            fighter_ids = set()
            
            for ranking in rankings:
                fighter_id = ranking.get('fighter_id', '')
                if fighter_id and fighter_id not in fighter_ids:
                    fighter_ids.add(fighter_id)
                    
                    fighter_profile = {
                        'id': fighter_id,
                        'name': ranking['fighter_name'],
                        'division': ranking['division'],
                        'record': ranking['record'],
                        'image_url': None,
                        'status': 'Active',
                        'place_of_birth': None,
                        'training_at': None,
                        'fighting_style': None,
                        'age': None,
                        'height': None,
                        'weight': None,
                        'octagon_debut': None,
                        'reach': None,
                        'leg_reach': None,
                        'stats': {
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
                        },
                        'fight_history': [],
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    fighters.append(fighter_profile)
            
            all_data['fighters'] = fighters
            logger.info(f"✅ Created {len(fighters)} basic fighter profiles")
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive scraping: {e}")
        
        logger.info(f"🎉 Comprehensive scraping complete! Total: {len(all_data['rankings'])} rankings, {len(all_data['fighters'])} fighters")
        return all_data

def main():
    """Run enhanced UFC scraper"""
    print("🥊 Enhanced UFC Scraper")
    print("=" * 50)
    
    scraper = EnhancedUFCScraper()
    
    try:
        # Run comprehensive scraping
        print("🚀 Starting comprehensive UFC data scraping...")
        print("This will scrape rankings with champions and create fighter profiles.")
        print()
        
        start_time = datetime.now()
        
        # Scrape all data
        data = scraper.scrape_comprehensive_data()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("✅ Scraping completed!")
        print(f"⏱️  Duration: {duration}")
        print()
        
        # Display results
        print("📊 Results Summary:")
        print(f"   • Rankings: {len(data.get('rankings', []))}")
        print(f"   • Fighter Profiles: {len(data.get('fighters', []))}")
        print()
        
        # Show champions
        champions = [r for r in data.get('rankings', []) if r.get('is_champion')]
        if champions:
            print("👑 Champions Found:")
            for champ in champions:
                print(f"   • {champ['fighter_name']} - {champ['division']}")
        print()
        
        # Save data
        raw_file = f"ufc_enhanced_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(raw_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Raw data saved to: {raw_file}")
        
        # Save for Flutter
        processed_file = "assets/data/ufc_data.json"
        os.makedirs(os.path.dirname(processed_file), exist_ok=True)
        with open(processed_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📱 Processed data saved to: {processed_file}")
        
        print()
        print("🎉 Enhanced scraper completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 