#!/usr/bin/env python3
"""
Comprehensive UFC Events Scraper
Scrapes all UFC events from Wikipedia and extracts detailed fight information
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
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveUFCEventsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://en.wikipedia.org"
        
    def scrape_all_events(self) -> List[Dict]:
        """Scrape all UFC events from Wikipedia"""
        logger.info("🚀 Starting comprehensive UFC events scraping...")
        
        try:
            # Get the main events page
            url = f"{self.base_url}/wiki/List_of_UFC_events"
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []
            
            # Scrape scheduled events
            scheduled_events = self.scrape_scheduled_events(soup)
            events.extend(scheduled_events)
            
            # Scrape past events
            past_events = self.scrape_past_events(soup)
            events.extend(past_events)
            
            logger.info(f"📊 Total events found: {len(events)}")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping events: {e}")
            return []
    
    def scrape_scheduled_events(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape scheduled events table"""
        logger.info("📅 Scraping scheduled events...")
        
        events = []
        
        try:
            # Find the scheduled events table
            scheduled_section = soup.find('h2', {'id': 'Scheduled_events'})
            if not scheduled_section:
                logger.warning("⚠️ Scheduled events section not found")
                return events
            
            table = scheduled_section.find_next('table')
            if not table:
                logger.warning("⚠️ Scheduled events table not found")
                return events
            
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    event = self.parse_event_row(cells, 'scheduled')
                    if event:
                        events.append(event)
            
            logger.info(f"✅ Found {len(events)} scheduled events")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping scheduled events: {e}")
            return []
    
    def scrape_past_events(self, soup: BeautifulSoup) -> List[Dict]:
        """Scrape past events table"""
        logger.info("📚 Scraping past events...")
        
        events = []
        
        try:
            # Find the past events table
            past_section = soup.find('h2', {'id': 'Past_events'})
            if not past_section:
                logger.warning("⚠️ Past events section not found")
                return events
            
            table = past_section.find_next('table')
            if not table:
                logger.warning("⚠️ Past events table not found")
                return events
            
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    event = self.parse_event_row(cells, 'completed')
                    if event:
                        events.append(event)
            
            logger.info(f"✅ Found {len(events)} past events")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error scraping past events: {e}")
            return []
    
    def parse_event_row(self, cells: List, status: str) -> Optional[Dict]:
        """Parse event data from table row"""
        try:
            # Extract event name and link
            event_cell = cells[0]
            event_link = event_cell.find('a')
            event_name = event_link.get_text().strip() if event_link else event_cell.get_text().strip()
            event_url = urljoin(self.base_url, event_link['href']) if event_link else None
            
            # Extract date
            date_cell = cells[1]
            date_text = date_cell.get_text().strip()
            event_date = self.parse_date(date_text)
            
            # Extract venue
            venue_cell = cells[2]
            venue_link = venue_cell.find('a')
            venue = venue_link.get_text().strip() if venue_link else venue_cell.get_text().strip()
            
            # Extract location
            location_cell = cells[3]
            location_link = location_cell.find('a')
            location = location_link.get_text().strip() if location_link else location_cell.get_text().strip()
            
            # Determine event type
            event_type = self.determine_event_type(event_name)
            
            return {
                'name': event_name,
                'date': event_date,
                'venue': venue,
                'location': location,
                'status': status,
                'event_type': event_type,
                'url': event_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing event row: {e}")
            return None
    
    def determine_event_type(self, event_name: str) -> str:
        """Determine the type of UFC event"""
        event_name_lower = event_name.lower()
        
        if 'ufc' in event_name_lower and any(char.isdigit() for char in event_name):
            return 'numbered'
        elif 'fight night' in event_name_lower:
            return 'fight_night'
        elif 'ultimate fighter' in event_name_lower:
            return 'tuf_finale'
        elif 'ufc on abc' in event_name_lower:
            return 'abc'
        elif 'ufc on espn' in event_name_lower:
            return 'espn'
        elif 'ufc on fox' in event_name_lower:
            return 'fox'
        elif 'ufc on fx' in event_name_lower:
            return 'fx'
        elif 'ufc on fuel' in event_name_lower:
            return 'fuel'
        elif 'ufc live' in event_name_lower:
            return 'live'
        else:
            return 'other'
    
    def parse_date(self, date_text: str) -> Optional[str]:
        """Parse date from various formats"""
        try:
            # Remove extra whitespace and normalize
            date_text = re.sub(r'\s+', ' ', date_text.strip())
            
            # Common date patterns
            patterns = [
                r'(\w+\s+\d{1,2},\s+\d{4})',  # "Nov 22, 2025"
                r'(\d{1,2}\s+\w+\s+\d{4})',   # "22 Nov 2025"
                r'(\w+\s+\d{4})',              # "Nov 2025"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    return match.group(1)
            
            return date_text
        except Exception as e:
            logger.error(f"Error parsing date '{date_text}': {e}")
            return date_text
    
    def get_event_fights(self, event_url: str) -> List[Dict]:
        """Get detailed fight information from individual event page"""
        logger.info(f"🥊 Getting fights for event: {event_url}")
        
        try:
            response = self.session.get(event_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            fights = []
            
            # Look for fight card tables
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains fight data by looking for "def." or "vs."
                table_text = table.get_text().lower()
                if 'def.' in table_text or 'vs.' in table_text or 'weight class' in table_text:
                    table_fights = self.parse_fight_table(table)
                    fights.extend(table_fights)
            
            logger.info(f"✅ Found {len(fights)} fights for event")
            return fights
            
        except Exception as e:
            logger.error(f"❌ Error getting fights for event: {e}")
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
    
    def scrape_events_with_fights(self) -> List[Dict]:
        """Scrape events and their fights"""
        logger.info("🎯 Starting comprehensive event and fight scraping...")
        
        # First get all events
        events = self.scrape_all_events()
        
        events_with_fights = []
        
        for event in events:
            if event.get('url'):
                logger.info(f"🔍 Scraping fights for: {event['name']}")
                
                # Get fights for this event
                fights = self.get_event_fights(event['url'])
                
                # Add fights to event
                event['fights'] = fights
                events_with_fights.append(event)
                
                # Small delay to be respectful
                time.sleep(1)
        
        logger.info(f"✅ Completed scraping {len(events_with_fights)} events with fights")
        return events_with_fights
    
    def save_results(self, events: List[Dict], output_dir: str = "data/exports"):
        """Save results to JSON and CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save events as JSON
        events_file = os.path.join(output_dir, f"ufc_events_with_fights_{timestamp}.json")
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(events)} events to {events_file}")
        
        # Save events as CSV
        events_csv = os.path.join(output_dir, f"ufc_events_with_fights_{timestamp}.csv")
        with open(events_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'name', 'date', 'venue', 'location', 'status', 'event_type', 'url', 'fight_count', 'scraped_at'
            ])
            
            for event in events:
                fight_count = len(event.get('fights', []))
                writer.writerow([
                    event.get('name', ''),
                    event.get('date', ''),
                    event.get('venue', ''),
                    event.get('location', ''),
                    event.get('status', ''),
                    event.get('event_type', ''),
                    event.get('url', ''),
                    fight_count,
                    event.get('scraped_at', '')
                ])
        
        logger.info(f"Saved events to {events_csv}")
        
        return events_file, events_csv

def main():
    """Main function to run the scraper"""
    scraper = ComprehensiveUFCEventsScraper()
    
    logger.info("Starting Comprehensive UFC Events Scraper")
    
    # Scrape all events with their fights
    events_with_fights = scraper.scrape_events_with_fights()
    
    if events_with_fights:
        # Save results
        events_file, events_csv = scraper.save_results(events_with_fights)
        
        # Print summary
        scheduled_count = len([e for e in events_with_fights if e['status'] == 'scheduled'])
        completed_count = len([e for e in events_with_fights if e['status'] == 'completed'])
        total_fights = sum(len(e.get('fights', [])) for e in events_with_fights)
        
        logger.info(f"Scraping complete!")
        logger.info(f"  Total events: {len(events_with_fights)}")
        logger.info(f"  Scheduled events: {scheduled_count}")
        logger.info(f"  Completed events: {completed_count}")
        logger.info(f"  Total fights: {total_fights}")
        logger.info(f"  Results saved to: {events_file} and {events_csv}")
    else:
        logger.warning("No events were successfully scraped")

if __name__ == "__main__":
    main() 