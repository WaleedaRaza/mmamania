#!/usr/bin/env python3
"""
Comprehensive Wikipedia UFC Event Scraper
Extracts detailed fight cards from UFC event pages on Wikipedia
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import re
from datetime import datetime
import time
import logging
from typing import Dict, List, Optional, Tuple
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WikipediaUFCEventScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://en.wikipedia.org"
        
    def get_event_info(self, event_url: str) -> Dict:
        """Extract event information from Wikipedia page"""
        try:
            response = self.session.get(event_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract event title
            title = soup.find('h1', {'id': 'firstHeading'})
            event_title = title.get_text().strip() if title else "Unknown Event"
            
            # Extract event date from infobox
            event_date = None
            infobox = soup.find('table', {'class': 'infobox'})
            if infobox:
                date_row = infobox.find('th', string=lambda text: text and 'Date' in text)
                if date_row and date_row.find_next_sibling('td'):
                    date_text = date_row.find_next_sibling('td').get_text().strip()
                    event_date = self.parse_date(date_text)
            
            # Extract venue from infobox
            venue = None
            if infobox:
                venue_row = infobox.find('th', string=lambda text: text and 'Venue' in text)
                if venue_row and venue_row.find_next_sibling('td'):
                    venue = venue_row.find_next_sibling('td').get_text().strip()
            
            return {
                'title': event_title,
                'date': event_date,
                'venue': venue,
                'url': event_url
            }
            
        except Exception as e:
            logger.error(f"Error getting event info from {event_url}: {e}")
            return {}
    
    def parse_date(self, date_text: str) -> Optional[str]:
        """Parse date from various formats"""
        try:
            # Remove extra whitespace and normalize
            date_text = re.sub(r'\s+', ' ', date_text.strip())
            
            # Common date patterns
            patterns = [
                r'(\w+\s+\d{1,2},\s+\d{4})',  # "June 28, 2025"
                r'(\d{1,2}\s+\w+\s+\d{4})',   # "28 June 2025"
                r'(\w+\s+\d{4})',              # "June 2025"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    return match.group(1)
            
            return date_text
        except Exception as e:
            logger.error(f"Error parsing date '{date_text}': {e}")
            return date_text
    
    def extract_fight_card(self, event_url: str) -> Dict:
        """Extract complete fight card from Wikipedia page"""
        try:
            response = self.session.get(event_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get event info
            event_info = self.get_event_info(event_url)
            
            # Find the fight card table
            fight_card = self.extract_fight_table(soup)
            
            return {
                'event': event_info,
                'fights': fight_card,
                'scraped_at': datetime.now().isoformat(),
                'source_url': event_url
            }
            
        except Exception as e:
            logger.error(f"Error extracting fight card from {event_url}: {e}")
            return {}
    
    def extract_fight_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract fights from the fight card table"""
        fights = []
        
        try:
            # Look for tables with fight data
            # The fight card table has specific structure with "def." text
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains fight data
                if table.find('td', string=lambda text: text and 'def.' in text):
                    fights.extend(self.parse_fight_table(table))
                    break  # Found the fight card table
            
            return fights
            
        except Exception as e:
            logger.error(f"Error extracting fight table: {e}")
            return []
    
    def parse_fight_table(self, table: BeautifulSoup) -> List[Dict]:
        """Parse individual fights from the table"""
        fights = []
        
        try:
            rows = table.find_all('tr')
            current_card = None
            
            for row in rows:
                # Check for card headers (Main card, Preliminary card, etc.)
                header_cell = row.find('th', {'colspan': '8'})
                if header_cell:
                    current_card = header_cell.get_text().strip()
                    continue
                
                # Check for fight rows (should have multiple td elements)
                cells = row.find_all('td')
                if len(cells) >= 6:  # Fight rows have multiple columns
                    fight = self.parse_fight_row(cells, current_card)
                    if fight:
                        fights.append(fight)
            
            return fights
            
        except Exception as e:
            logger.error(f"Error parsing fight table: {e}")
            return []
    
    def parse_fight_row(self, cells: List[BeautifulSoup], card_type: str) -> Optional[Dict]:
        """Parse a single fight row"""
        try:
            if len(cells) < 6:
                return None
            
            # Extract fight data based on the structure we found
            # Format: Weight Class | Fighter 1 | def. | Fighter 2 | Method | Round | Time
            weight_class = cells[0].get_text().strip() if cells[0] else ""
            fighter1 = cells[1].get_text().strip() if cells[1] else ""
            result = cells[2].get_text().strip() if cells[2] else ""
            fighter2 = cells[3].get_text().strip() if cells[3] else ""
            method = cells[4].get_text().strip() if cells[4] else ""
            round_num = cells[5].get_text().strip() if cells[5] else ""
            time = cells[6].get_text().strip() if len(cells) > 6 and cells[6] else ""
            
            # Determine winner and loser
            winner = None
            loser = None
            
            if result == "def.":
                winner = fighter1
                loser = fighter2
            elif result == "vs.":
                # Scheduled fight
                winner = None
                loser = None
            else:
                # Check if there's a different result format
                winner = fighter1 if "def." in result else None
                loser = fighter2
            
            # Clean up fighter names (remove links)
            winner = self.clean_fighter_name(winner) if winner else None
            loser = self.clean_fighter_name(loser) if loser else None
            
            return {
                'weight_class': weight_class,
                'fighter1': fighter1,
                'fighter2': fighter2,
                'winner': winner,
                'loser': loser,
                'method': method,
                'round': round_num,
                'time': time,
                'card_type': card_type,
                'result_type': 'completed' if winner else 'scheduled'
            }
            
        except Exception as e:
            logger.error(f"Error parsing fight row: {e}")
            return None
    
    def clean_fighter_name(self, name: str) -> str:
        """Clean fighter name by removing HTML tags and extra whitespace"""
        if not name:
            return ""
        
        # Remove HTML tags
        soup = BeautifulSoup(name, 'html.parser')
        clean_name = soup.get_text().strip()
        
        # Remove extra whitespace
        clean_name = re.sub(r'\s+', ' ', clean_name)
        
        return clean_name
    
    def scrape_known_events(self) -> List[Dict]:
        """Scrape a list of known UFC events"""
        known_events = [
            "UFC_317",
            "UFC_316", 
            "UFC_315",
            "UFC_314",
            "UFC_313",
            "UFC_312",
            "UFC_311",
            "UFC_310",
            "UFC_309",
            "UFC_308"
        ]
        
        results = []
        
        for event in known_events:
            event_url = f"{self.base_url}/wiki/{event}"
            logger.info(f"Scraping {event} from {event_url}")
            
            try:
                fight_card = self.extract_fight_card(event_url)
                if fight_card and fight_card.get('fights'):
                    results.append(fight_card)
                    logger.info(f"Successfully scraped {len(fight_card['fights'])} fights from {event}")
                else:
                    logger.warning(f"No fight data found for {event}")
                
                # Be respectful to Wikipedia
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping {event}: {e}")
        
        return results
    
    def save_results(self, results: List[Dict], output_dir: str = "data/exports"):
        """Save results to JSON and CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = os.path.join(output_dir, f"wikipedia_ufc_events_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(results)} events to {json_file}")
        
        # Save as CSV
        csv_file = os.path.join(output_dir, f"wikipedia_ufc_fights_{timestamp}.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'event_title', 'event_date', 'event_venue', 'event_url',
                'weight_class', 'fighter1', 'fighter2', 'winner', 'loser',
                'method', 'round', 'time', 'card_type', 'result_type'
            ])
            
            for event in results:
                event_info = event.get('event', {})
                for fight in event.get('fights', []):
                    writer.writerow([
                        event_info.get('title', ''),
                        event_info.get('date', ''),
                        event_info.get('venue', ''),
                        event_info.get('url', ''),
                        fight.get('weight_class', ''),
                        fight.get('fighter1', ''),
                        fight.get('fighter2', ''),
                        fight.get('winner', ''),
                        fight.get('loser', ''),
                        fight.get('method', ''),
                        fight.get('round', ''),
                        fight.get('time', ''),
                        fight.get('card_type', ''),
                        fight.get('result_type', '')
                    ])
        
        logger.info(f"Saved fight data to {csv_file}")
        
        return json_file, csv_file

def main():
    """Main function to run the scraper"""
    scraper = WikipediaUFCEventScraper()
    
    logger.info("Starting Wikipedia UFC Event Scraper")
    
    # Scrape known events
    results = scraper.scrape_known_events()
    
    if results:
        # Save results
        json_file, csv_file = scraper.save_results(results)
        
        # Print summary
        total_fights = sum(len(event.get('fights', [])) for event in results)
        logger.info(f"Scraping complete! Found {len(results)} events with {total_fights} total fights")
        logger.info(f"Results saved to: {json_file} and {csv_file}")
    else:
        logger.warning("No events were successfully scraped")

if __name__ == "__main__":
    main() 