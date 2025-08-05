#!/usr/bin/env python3
"""
Targeted UFC Scraper
Focuses on specific UFC events with known fight data and uses robust parsing
"""

import os
import re
import csv
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TargetedUFCScraper:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Target specific UFC events that we know have fight data
        self.target_events = [
            "UFC_300",
            "UFC_299", 
            "UFC_298",
            "UFC_297",
            "UFC_296",
            "UFC_295",
            "UFC_294",
            "UFC_293",
            "UFC_292",
            "UFC_291",
            "UFC_290",
            "UFC_289",
            "UFC_288",
            "UFC_287",
            "UFC_286",
            "UFC_285",
            "UFC_284",
            "UFC_283",
            "UFC_282",
            "UFC_281",
            "UFC_280",
            "UFC_279",
            "UFC_278",
            "UFC_277",
            "UFC_276",
            "UFC_275",
            "UFC_274",
            "UFC_273",
            "UFC_272",
            "UFC_271",
            "UFC_270",
            "UFC_269",
            "UFC_268",
            "UFC_267",
            "UFC_266",
            "UFC_265",
            "UFC_264",
            "UFC_263",
            "UFC_262",
            "UFC_261",
            "UFC_260",
            "UFC_259",
            "UFC_258",
            "UFC_257",
            "UFC_256",
            "UFC_255",
            "UFC_254",
            "UFC_253",
            "UFC_252",
            "UFC_251",
            "UFC_250"
        ]
    
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
                date_row = infobox.find('th', string=re.compile(r'Date', re.I))
                if date_row and date_row.find_next_sibling('td'):
                    date_text = date_row.find_next_sibling('td').get_text(strip=True)
                    date = self.parse_date(date_text)
            
            # Extract venue from infobox
            venue = None
            if infobox:
                venue_row = infobox.find('th', string=re.compile(r'Venue', re.I))
                if venue_row and venue_row.find_next_sibling('td'):
                    venue = venue_row.find_next_sibling('td').get_text(strip=True)
            
            # Extract location from infobox
            location = None
            if infobox:
                location_row = infobox.find('th', string=re.compile(r'Location', re.I))
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
            
            # Extract fight tables with multiple strategies
            fights = []
            
            # Strategy 1: Look for tables with fight data
            tables = soup.find_all('table', {'class': 'wikitable'})
            for table in tables:
                table_fights = self.parse_fight_table_robust(table)
                if table_fights:
                    fights.extend(table_fights)
            
            # Strategy 2: Look for specific fight sections
            if not fights:
                fights = self.extract_fights_from_sections(soup)
            
            # Strategy 3: Look for fight lists
            if not fights:
                fights = self.extract_fights_from_lists(soup)
            
            return {
                'event': event_info,
                'fights': fights
            }
            
        except Exception as e:
            logger.error(f"Error extracting fight card from {event_url}: {e}")
            return {'event': {'title': 'Unknown Event', 'url': event_url}, 'fights': []}
    
    def parse_fight_table_robust(self, table: BeautifulSoup) -> List[Dict]:
        """Robust parsing of fight tables"""
        fights = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:  # Need at least header + 1 data row
            return fights
        
        # Analyze headers to understand structure
        headers = rows[0].find_all(['th', 'td'])
        header_texts = [h.get_text(strip=True).lower() for h in headers]
        
        # Check if this looks like a fight table
        fight_indicators = ['fighter', 'weight', 'method', 'round', 'time', 'result', 'winner', 'loser', 'bout']
        if not any(indicator in ' '.join(header_texts) for indicator in fight_indicators):
            return fights
        
        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:  # Need at least 2 cells for a fight
                fight = self.parse_fight_row_robust(cells, header_texts)
                if fight:
                    fights.append(fight)
        
        return fights
    
    def parse_fight_row_robust(self, cells: List[BeautifulSoup], headers: List[str]) -> Optional[Dict]:
        """Robust parsing of individual fight rows"""
        try:
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Find fighter columns
            fighter1 = None
            fighter2 = None
            weight_class = None
            method = None
            round_num = None
            time = None
            winner = None
            
            # Analyze based on header structure
            for i, header in enumerate(headers):
                if i < len(cell_texts):
                    cell_text = cell_texts[i]
                    
                    if 'fighter' in header or 'bout' in header:
                        if not fighter1:
                            fighter1 = self.clean_fighter_name(cell_text)
                        elif not fighter2:
                            fighter2 = self.clean_fighter_name(cell_text)
                    
                    elif 'weight' in header:
                        weight_class = cell_text
                    
                    elif 'method' in header or 'result' in header:
                        method = cell_text
                    
                    elif 'round' in header:
                        round_num = cell_text
                    
                    elif 'time' in header:
                        time = cell_text
            
            # If we didn't find fighters by headers, try first two columns
            if not fighter1 and len(cell_texts) >= 2:
                fighter1 = self.clean_fighter_name(cell_texts[0])
                fighter2 = self.clean_fighter_name(cell_texts[1])
            
            # Look for weight class in any cell
            if not weight_class:
                for text in cell_texts:
                    if any(wc in text.lower() for wc in ['weight', 'flyweight', 'bantamweight', 'featherweight', 'lightweight', 'welterweight', 'middleweight', 'light heavyweight', 'heavyweight']):
                        weight_class = text.strip()
                        break
            
            # Look for method in any cell
            if not method:
                for text in cell_texts:
                    if any(m in text.lower() for m in ['ko', 'tko', 'submission', 'decision', 'draw', 'no contest']):
                        method = text.strip()
                        break
            
            # Look for round and time
            if not round_num:
                for text in cell_texts:
                    if re.search(r'round\s*(\d+)', text.lower()):
                        round_match = re.search(r'round\s*(\d+)', text.lower())
                        round_num = round_match.group(1) if round_match else None
            
            if not time:
                for text in cell_texts:
                    if re.search(r'(\d+):(\d+)', text):
                        time_match = re.search(r'(\d+):(\d+)', text)
                        time = f"{time_match.group(1)}:{time_match.group(2)}" if time_match else None
            
            # Determine winner
            if method and fighter1 and fighter2:
                winner = self._determine_winner_robust(cell_texts, fighter1, fighter2, method)
            
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
    
    def _determine_winner_robust(self, cell_texts: List[str], fighter1: str, fighter2: str, method: str) -> Optional[str]:
        """Robust winner determination"""
        # Look for "def." or "defeated" patterns
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
        
        # Check method for winner clues
        if method:
            if 'draw' in method.lower() or 'no contest' in method.lower():
                return 'Draw'
            elif fighter1 and fighter1.lower() in method.lower():
                return fighter1
            elif fighter2 and fighter2.lower() in method.lower():
                return fighter2
        
        return None
    
    def extract_fights_from_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract fights from section headers"""
        fights = []
        
        # Look for sections with fight data
        sections = soup.find_all(['h2', 'h3', 'h4'])
        for section in sections:
            section_text = section.get_text(strip=True).lower()
            if any(keyword in section_text for keyword in ['main card', 'preliminary', 'fight', 'bout']):
                # Look for fight data in this section
                next_elem = section.find_next_sibling()
                if next_elem:
                    # Try to find tables or lists in this section
                    tables = next_elem.find_all('table')
                    for table in tables:
                        table_fights = self.parse_fight_table_robust(table)
                        fights.extend(table_fights)
        
        return fights
    
    def extract_fights_from_lists(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract fights from list elements"""
        fights = []
        
        # Look for lists that might contain fight data
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            items = list_elem.find_all('li')
            for item in items:
                item_text = item.get_text(strip=True)
                # Check if this looks like a fight description
                if any(keyword in item_text.lower() for keyword in ['def.', 'defeated', 'ko', 'tko', 'submission', 'decision']):
                    fight = self.parse_fight_from_text(item_text)
                    if fight:
                        fights.append(fight)
        
        return fights
    
    def parse_fight_from_text(self, text: str) -> Optional[Dict]:
        """Parse fight from text description"""
        try:
            # Look for fighter names and result
            # This is a simplified parser for text-based fight descriptions
            if 'def.' in text.lower() or 'defeated' in text.lower():
                # Extract fighter names and result
                parts = text.split('def.')
                if len(parts) >= 2:
                    winner = parts[0].strip()
                    loser_part = parts[1].strip()
                    
                    # Extract loser name (before any result details)
                    loser = loser_part.split()[0] if loser_part else None
                    
                    # Extract method
                    method = None
                    if any(m in text.lower() for m in ['ko', 'tko', 'submission', 'decision']):
                        for m in ['ko', 'tko', 'submission', 'decision']:
                            if m in text.lower():
                                method = m.upper()
                                break
                    
                    if winner and loser:
                        return {
                            'fighter1': winner,
                            'fighter2': loser,
                            'winner': winner,
                            'loser': loser,
                            'method': method,
                            'weight_class': 'Unknown'
                        }
            
        except Exception as e:
            logger.error(f"Error parsing fight from text: {e}")
        
        return None
    
    def clean_fighter_name(self, name: str) -> str:
        """Clean fighter name"""
        if not name:
            return None
        
        # Remove salary information (e.g., "$350,000 (no win bonus)")
        name = re.sub(r'\$[\d,]+.*?\)', '', name)
        name = re.sub(r'\$[\d,]+.*?$', '', name)
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^\s*def\.?\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*def\.?\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^\s*defeated\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*defeated\s*$', '', name, flags=re.IGNORECASE)
        
        # Remove vs. and similar separators
        name = re.sub(r'\s+vs\.?\s+.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+def\.?\s+.*$', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace and clean up
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove any remaining artifacts
        name = re.sub(r'^\s*[:\$].*$', '', name)  # Remove lines starting with : or $
        name = re.sub(r'^\s*\d+.*$', '', name)     # Remove lines starting with numbers
        
        return name if name and len(name) > 1 else None
    
    def scrape_targeted_events(self) -> List[Dict]:
        """Scrape targeted UFC events"""
        logger.info(f"Starting targeted UFC events scraping ({len(self.target_events)} events)")
        
        results = []
        successful_count = 0
        
        for i, event_name in enumerate(self.target_events):
            event_url = f"{self.base_url}/wiki/{event_name}"
            logger.info(f"Scraping {event_name} ({i+1}/{len(self.target_events)})")
            
            try:
                fight_card = self.extract_fight_card(event_url)
                if fight_card and fight_card.get('fights'):
                    results.append(fight_card)
                    successful_count += 1
                    logger.info(f"✅ Successfully scraped {len(fight_card['fights'])} fights from {event_name}")
                else:
                    logger.warning(f"⚠️  No fight data found for {event_name}")
                
                # Be respectful to Wikipedia
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error scraping {event_name}: {e}")
        
        logger.info(f"Scraping complete! Successfully scraped {successful_count}/{len(self.target_events)} events")
        return results
    
    def save_results(self, results: List[Dict], output_dir: str = "data/exports"):
        """Save results to JSON and CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = os.path.join(output_dir, f"targeted_ufc_events_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(results)} events to {json_file}")
        
        # Save as CSV
        csv_file = os.path.join(output_dir, f"targeted_ufc_fights_{timestamp}.csv")
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
    """Main function to run the targeted scraper"""
    scraper = TargetedUFCScraper()
    
    logger.info("Starting Targeted UFC Event Scraper")
    
    # Scrape targeted events
    results = scraper.scrape_targeted_events()
    
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