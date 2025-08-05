#!/usr/bin/env python3
"""
Enhanced Comprehensive Wikipedia UFC Scraper
Systematically extracts all UFC events from Wikipedia and scrapes their fight cards
"""

import os
import re
import csv
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedWikipediaUFCEventScraper:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Track processed events to avoid duplicates
        self.processed_events = set()
        
        # Event patterns to identify UFC events
        self.ufc_patterns = [
            r'UFC_\d+',  # UFC_123
            r'UFC_on_\w+',  # UFC_on_ESPN
            r'UFC_Fight_Night',  # UFC Fight Night
            r'UFC_\d+\.\d+',  # UFC_37.5
        ]
    
    def extract_all_ufc_events_from_list(self) -> List[str]:
        """Extract all UFC event URLs from the main UFC events list page"""
        logger.info("Extracting all UFC events from Wikipedia list...")
        
        list_url = f"{self.base_url}/wiki/List_of_UFC_events"
        
        try:
            response = self.session.get(list_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links that match UFC patterns
            ufc_links = set()
            
            # Look for links in various sections
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # Check if it's a UFC event link
                if self._is_ufc_event_link(href, text):
                    event_name = href.replace('/wiki/', '')
                    ufc_links.add(event_name)
            
            logger.info(f"Found {len(ufc_links)} potential UFC events")
            return list(ufc_links)
            
        except Exception as e:
            logger.error(f"Error extracting UFC events from list: {e}")
            return []
    
    def _is_ufc_event_link(self, href: str, text: str) -> bool:
        """Check if a link is a UFC event link"""
        if not href.startswith('/wiki/'):
            return False
        
        # Check for UFC patterns in href
        for pattern in self.ufc_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return True
        
        # Check for UFC patterns in text
        for pattern in self.ufc_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for specific UFC event patterns
        ufc_text_patterns = [
            r'UFC \d+',
            r'UFC on \w+',
            r'UFC Fight Night',
            r'UFC \d+\.\d+'
        ]
        
        for pattern in ufc_text_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_event_info(self, event_url: str) -> Dict:
        """Extract basic event information from event page"""
        try:
            response = self.session.get(event_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1', {'id': 'firstHeading'})
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Event"
            
            # Extract date from infobox
            date = None
            infobox = soup.find('table', {'class': 'infobox'})
            if infobox:
                date_row = infobox.find('th', text=re.compile(r'Date', re.I))
                if date_row and date_row.find_next_sibling('td'):
                    date_text = date_row.find_next_sibling('td').get_text(strip=True)
                    date = self.parse_date(date_text)
            
            # Extract venue from infobox
            venue = None
            if infobox:
                venue_row = infobox.find('th', text=re.compile(r'Venue', re.I))
                if venue_row and venue_row.find_next_sibling('td'):
                    venue = venue_row.find_next_sibling('td').get_text(strip=True)
            
            # Extract location from infobox
            location = None
            if infobox:
                location_row = infobox.find('th', text=re.compile(r'Location', re.I))
                if location_row and location_row.find_next_sibling('td'):
                    location = location_row.find_next_sibling('td').get_text(strip=True)
            
            return {
                'title': title,
                'date': date,
                'venue': venue,
                'location': location,
                'url': event_url
            }
            
        except Exception as e:
            logger.error(f"Error getting event info from {event_url}: {e}")
            return {'title': 'Unknown Event', 'date': None, 'venue': None, 'location': None, 'url': event_url}
    
    def parse_date(self, date_text: str) -> Optional[str]:
        """Parse date from various formats"""
        if not date_text:
            return None
        
        # Common date patterns
        patterns = [
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    if pattern == patterns[0]:  # Month name format
                        month_map = {
                            'january': '01', 'february': '02', 'march': '03', 'april': '04',
                            'may': '05', 'june': '06', 'july': '07', 'august': '08',
                            'september': '09', 'october': '10', 'november': '11', 'december': '12'
                        }
                        day, month, year = match.groups()
                        month_num = month_map.get(month.lower(), '01')
                        return f"{year}-{month_num.zfill(2)}-{day.zfill(2)}"
                    else:  # Numeric format
                        if pattern == patterns[1]:  # MM/DD/YYYY
                            month, day, year = match.groups()
                        else:  # YYYY-MM-DD
                            year, month, day = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    
    def extract_fight_card(self, event_url: str) -> Dict:
        """Extract complete fight card from event page"""
        try:
            response = self.session.get(event_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get event info
            event_info = self.get_event_info(event_url)
            
            # Extract fight tables
            fights = self.extract_fight_table(soup)
            
            return {
                'event': event_info,
                'fights': fights
            }
            
        except Exception as e:
            logger.error(f"Error extracting fight card from {event_url}: {e}")
            return {'event': {'title': 'Unknown Event', 'url': event_url}, 'fights': []}
    
    def extract_fight_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract fight tables from the page"""
        fights = []
        
        # Look for fight tables
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        for table in tables:
            # Check if this table contains fight data
            if self._is_fight_table(table):
                table_fights = self.parse_fight_table(table)
                fights.extend(table_fights)
        
        return fights
    
    def _is_fight_table(self, table: BeautifulSoup) -> bool:
        """Check if a table contains fight data"""
        headers = table.find_all('th')
        header_text = ' '.join([h.get_text(strip=True) for h in headers]).lower()
        
        # Look for fight-related keywords
        fight_keywords = ['fighter', 'weight', 'method', 'round', 'time', 'result', 'winner', 'loser']
        return any(keyword in header_text for keyword in fight_keywords)
    
    def parse_fight_table(self, table: BeautifulSoup) -> List[Dict]:
        """Parse individual fight table"""
        fights = []
        rows = table.find_all('tr')
        
        # Skip header row
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:  # Minimum cells for a fight
                fight = self.parse_fight_row(cells)
                if fight:
                    fights.append(fight)
        
        return fights
    
    def parse_fight_row(self, cells: List[BeautifulSoup]) -> Optional[Dict]:
        """Parse individual fight row"""
        try:
            # Extract data from cells
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Look for fighter names (usually first two columns)
            fighter1 = self.clean_fighter_name(cell_texts[0]) if len(cell_texts) > 0 else None
            fighter2 = self.clean_fighter_name(cell_texts[1]) if len(cell_texts) > 1 else None
            
            # Look for weight class
            weight_class = None
            for text in cell_texts:
                if any(wc in text.lower() for wc in ['weight', 'flyweight', 'bantamweight', 'featherweight', 'lightweight', 'welterweight', 'middleweight', 'light heavyweight', 'heavyweight']):
                    weight_class = text.strip()
                    break
            
            # Look for result/method
            method = None
            round_num = None
            time = None
            winner = None
            
            for text in cell_texts:
                # Check for method
                if any(m in text.lower() for m in ['ko', 'tko', 'submission', 'decision', 'draw', 'no contest']):
                    method = text.strip()
                
                # Check for round
                if re.search(r'round\s*(\d+)', text.lower()):
                    round_match = re.search(r'round\s*(\d+)', text.lower())
                    round_num = round_match.group(1) if round_match else None
                
                # Check for time
                if re.search(r'(\d+):(\d+)', text):
                    time_match = re.search(r'(\d+):(\d+)', text)
                    time = f"{time_match.group(1)}:{time_match.group(2)}" if time_match else None
            
            # Determine winner based on method and fighter names
            if method and fighter1 and fighter2:
                if 'def.' in method.lower() or 'defeated' in method.lower():
                    # Look for winner in the method text
                    for fighter in [fighter1, fighter2]:
                        if fighter and fighter.lower() in method.lower():
                            winner = fighter
                            break
                elif 'draw' in method.lower() or 'no contest' in method.lower():
                    winner = 'Draw'
                else:
                    # Try to determine winner from context
                    winner = self._determine_winner_from_context(cell_texts, fighter1, fighter2)
            
            if fighter1 and fighter2:
                return {
                    'fighter1': fighter1,
                    'fighter2': fighter2,
                    'weight_class': weight_class,
                    'method': method,
                    'round': round_num,
                    'time': time,
                    'winner': winner,
                    'loser': fighter2 if winner == fighter1 else fighter1 if winner == fighter2 else None
                }
            
        except Exception as e:
            logger.error(f"Error parsing fight row: {e}")
        
        return None
    
    def _determine_winner_from_context(self, cell_texts: List[str], fighter1: str, fighter2: str) -> Optional[str]:
        """Try to determine winner from context"""
        # Look for indicators like "def." or "defeated"
        for text in cell_texts:
            if 'def.' in text.lower() or 'defeated' in text.lower():
                if fighter1 and fighter1.lower() in text.lower():
                    return fighter1
                elif fighter2 and fighter2.lower() in text.lower():
                    return fighter2
        
        # Look for result indicators
        for text in cell_texts:
            if any(indicator in text.lower() for indicator in ['win', 'victory', 'defeats']):
                if fighter1 and fighter1.lower() in text.lower():
                    return fighter1
                elif fighter2 and fighter2.lower() in text.lower():
                    return fighter2
        
        return None
    
    def clean_fighter_name(self, name: str) -> str:
        """Clean fighter name"""
        if not name:
            return None
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^\s*def\.?\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*def\.?\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^\s*defeated\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*defeated\s*$', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name if name else None
    
    def scrape_all_ufc_events(self, max_events: int = 50) -> List[Dict]:
        """Scrape all available UFC events"""
        logger.info(f"Starting comprehensive UFC events scraping (max: {max_events})")
        
        # Get all UFC event URLs
        event_urls = self.extract_all_ufc_events_from_list()
        logger.info(f"Found {len(event_urls)} UFC events to process")
        
        results = []
        processed_count = 0
        
        for event_name in event_urls[:max_events]:
            if event_name in self.processed_events:
                continue
            
            event_url = f"{self.base_url}/wiki/{event_name}"
            logger.info(f"Scraping {event_name} ({processed_count + 1}/{min(len(event_urls), max_events)})")
            
            try:
                fight_card = self.extract_fight_card(event_url)
                if fight_card and fight_card.get('fights'):
                    results.append(fight_card)
                    self.processed_events.add(event_name)
                    logger.info(f"✅ Successfully scraped {len(fight_card['fights'])} fights from {event_name}")
                else:
                    logger.warning(f"⚠️  No fight data found for {event_name}")
                
                processed_count += 1
                
                # Be respectful to Wikipedia
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error scraping {event_name}: {e}")
        
        logger.info(f"Scraping complete! Processed {processed_count} events, found {len(results)} with fight data")
        return results
    
    def save_results(self, results: List[Dict], output_dir: str = "data/exports"):
        """Save results to JSON and CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = os.path.join(output_dir, f"enhanced_wikipedia_ufc_events_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(results)} events to {json_file}")
        
        # Save as CSV
        csv_file = os.path.join(output_dir, f"enhanced_wikipedia_ufc_fights_{timestamp}.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'event_title', 'event_date', 'event_venue', 'event_location', 'event_url',
                'weight_class', 'fighter1', 'fighter2', 'winner', 'loser',
                'method', 'round', 'time'
            ])
            
            for event in results:
                event_info = event.get('event', {})
                for fight in event.get('fights', []):
                    writer.writerow([
                        event_info.get('title', ''),
                        event_info.get('date', ''),
                        event_info.get('venue', ''),
                        event_info.get('location', ''),
                        event_info.get('url', ''),
                        fight.get('weight_class', ''),
                        fight.get('fighter1', ''),
                        fight.get('fighter2', ''),
                        fight.get('winner', ''),
                        fight.get('loser', ''),
                        fight.get('method', ''),
                        fight.get('round', ''),
                        fight.get('time', '')
                    ])
        
        logger.info(f"Saved fight data to {csv_file}")
        
        return json_file, csv_file

def main():
    """Main function to run the enhanced scraper"""
    scraper = EnhancedWikipediaUFCEventScraper()
    
    logger.info("Starting Enhanced Wikipedia UFC Event Scraper")
    
    # Scrape all available events (limit to 50 for testing)
    results = scraper.scrape_all_ufc_events(max_events=50)
    
    if results:
        # Save results
        json_file, csv_file = scraper.save_results(results)
        
        # Print summary
        total_fights = sum(len(event.get('fights', [])) for event in results)
        logger.info(f"🎉 Scraping complete! Found {len(results)} events with {total_fights} total fights")
        logger.info(f"📁 Results saved to: {json_file} and {csv_file}")
        
        # Print event summary
        for event in results[:5]:  # Show first 5 events
            event_info = event.get('event', {})
            fights = event.get('fights', [])
            logger.info(f"📅 {event_info.get('title', 'Unknown')}: {len(fights)} fights")
    else:
        logger.warning("No events were successfully scraped")

if __name__ == "__main__":
    main() 