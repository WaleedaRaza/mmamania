#!/usr/bin/env python3
"""
Focused UFC Scraper
Follows the exact requirements: get past events links, scrape fight card tables, populate with proper schema
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

class FocusedUFCScraper:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_past_events_links(self) -> List[Dict]:
        """Step 1: Get all past events links from the main UFC events page"""
        logger.info("Step 1: Getting past events links from Wikipedia...")
        
        list_url = f"{self.base_url}/wiki/List_of_UFC_events"
        
        try:
            response = self.session.get(list_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            past_events = []
            
            # Find all tables and look for the one with the most UFC links
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            # Find the table with the most UFC event links
            best_table = None
            max_ufc_links = 0
            
            for i, table in enumerate(tables):
                links = table.find_all('a')
                ufc_links = [link for link in links if 'ufc' in link.get_text().lower()]
                if len(ufc_links) > max_ufc_links:
                    max_ufc_links = len(ufc_links)
                    best_table = table
                    logger.info(f"Table {i+1} has {len(ufc_links)} UFC links")
            
            if best_table and max_ufc_links > 100:  # Should have many UFC links
                logger.info(f"Using table with {max_ufc_links} UFC links")
                rows = best_table.find_all('tr')
                logger.info(f"Table has {len(rows)} rows")
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Look for event link in the Event column (usually column 1)
                        event_cell = cells[1]  # Event column
                        event_link = event_cell.find('a')
                        
                        if event_link and event_link.get('href'):
                            event_name = event_link.get_text(strip=True)
                            event_url = f"{self.base_url}{event_link['href']}"
                            
                            # Get date from the Date column (usually column 2)
                            date_cell = cells[2] if len(cells) > 2 else None
                            date_text = date_cell.get_text(strip=True) if date_cell else None
                            
                            # Only include if it's a UFC event (not just a link to UFC)
                            if 'ufc' in event_name.lower() and not event_name.lower().startswith('ufc apex'):
                                past_events.append({
                                    'name': event_name,
                                    'url': event_url,
                                    'date': date_text
                                })
                                
                                logger.info(f"Found event: {event_name}")
            else:
                logger.warning("No suitable table with UFC events found")
            
            logger.info(f"Found {len(past_events)} past events")
            return past_events
            
        except Exception as e:
            logger.error(f"Error getting past events: {e}")
            return []
    
    def scrape_fight_card_table(self, event_url: str, event_name: str) -> Dict:
        """Step 2: Scrape the fight card table from an event page"""
        logger.info(f"Scraping fight card from: {event_name}")
        
        try:
            response = self.session.get(event_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables on the page (not just wikitable)
            tables = soup.find_all('table')
            
            fights = []
            
            for table in tables:
                # Check if this table contains fight data
                if self._is_fight_card_table(table):
                    table_fights = self._parse_fight_card_table(table)
                    fights.extend(table_fights)
            
            return {
                'event_name': event_name,
                'event_url': event_url,
                'fights': fights
            }
            
        except Exception as e:
            logger.error(f"Error scraping fight card from {event_name}: {e}")
            return {'event_name': event_name, 'event_url': event_url, 'fights': []}
    
    def _is_fight_card_table(self, table: BeautifulSoup) -> bool:
        """Check if a table is a fight card table"""
        headers = table.find_all('th')
        header_text = ' '.join([h.get_text(strip=True) for h in headers]).lower()
        
        # Look for fight card indicators
        fight_indicators = ['weight class', 'fighter', 'def.', 'method', 'round', 'time']
        has_indicators = any(indicator in header_text for indicator in fight_indicators)
        
        # Also check if the table has fight data in the rows
        rows = table.find_all('tr')
        if len(rows) > 2:  # Need at least header + data rows
            # Check if any row contains "def." pattern
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                if any('def.' in text.lower() for text in cell_texts):
                    return True
        
        return has_indicators
    
    def _parse_fight_card_table(self, table: BeautifulSoup) -> List[Dict]:
        """Parse the fight card table to extract fight data"""
        fights = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:  # Need at least header + 1 data row
            return fights
        
        # Get headers to understand structure
        headers = rows[0].find_all(['th', 'td'])
        header_texts = [h.get_text(strip=True).lower() for h in headers]
        
        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:  # Need at least 3 cells for a fight
                fight = self._parse_fight_row(cells, header_texts)
                if fight:
                    fights.append(fight)
        
        return fights
    
    def _parse_fight_row(self, cells: List[BeautifulSoup], headers: List[str]) -> Optional[Dict]:
        """Parse individual fight row"""
        try:
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Find the key data based on header structure
            weight_class = None
            fighter1 = None
            fighter2 = None
            method = None
            round_num = None
            time = None
            
            for i, header in enumerate(headers):
                if i < len(cell_texts):
                    cell_text = cell_texts[i]
                    
                    if 'weight' in header:
                        weight_class = cell_text
                    elif 'fighter' in header or 'name' in header:
                        if not fighter1:
                            fighter1 = self._extract_fighter_name(cell_text)
                        elif not fighter2:
                            fighter2 = self._extract_fighter_name(cell_text)
                    elif 'method' in header:
                        method = cell_text
                    elif 'round' in header:
                        round_num = cell_text
                    elif 'time' in header:
                        time = cell_text
            
            # If we didn't find fighters by headers, try to parse from the structure
            if not fighter1 and not fighter2:
                # Look for "def." pattern in the cells
                for cell_text in cell_texts:
                    if 'def.' in cell_text.lower():
                        fighters = self._parse_fighters_from_def_pattern(cell_text)
                        if fighters:
                            fighter1, fighter2 = fighters
                            break
            
            # Determine winner and loser
            winner = None
            loser = None
            if fighter1 and fighter2:
                # Look for winner in the method or any cell
                for cell_text in cell_texts:
                    if fighter1.lower() in cell_text.lower() and 'def.' in cell_text.lower():
                        winner = fighter1
                        loser = fighter2
                        break
                    elif fighter2.lower() in cell_text.lower() and 'def.' in cell_text.lower():
                        winner = fighter2
                        loser = fighter1
                        break
            
            if fighter1 and fighter2:
                return {
                    'weight_class': weight_class,
                    'fighter1': fighter1,
                    'fighter2': fighter2,
                    'winner': winner,
                    'loser': loser,
                    'method': method,
                    'round': round_num,
                    'time': time
                }
            
        except Exception as e:
            logger.error(f"Error parsing fight row: {e}")
        
        return None
    
    def _extract_fighter_name(self, text: str) -> str:
        """Extract clean fighter name from text"""
        if not text:
            return None
        
        # Remove common artifacts
        text = re.sub(r'\$[\d,]+.*?\)', '', text)  # Remove salary info
        text = re.sub(r'\$[\d,]+.*?$', '', text)   # Remove salary info
        text = re.sub(r'def\.', '', text, flags=re.IGNORECASE)  # Remove "def."
        text = re.sub(r'\s+', ' ', text).strip()   # Clean whitespace
        
        return text if text else None
    
    def _parse_fighters_from_def_pattern(self, text: str) -> Optional[tuple]:
        """Parse fighters from "Fighter1 def. Fighter2" pattern"""
        if 'def.' in text.lower():
            parts = text.split('def.')
            if len(parts) >= 2:
                fighter1 = self._extract_fighter_name(parts[0])
                fighter2 = self._extract_fighter_name(parts[1])
                if fighter1 and fighter2:
                    return (fighter1, fighter2)
        return None
    
    def scrape_all_past_events(self, max_events: int = 20) -> List[Dict]:
        """Main scraping function"""
        logger.info("Starting focused UFC scraping...")
        
        # Step 1: Get past events links
        past_events = self.get_past_events_links()
        logger.info(f"Found {len(past_events)} past events")
        
        # Step 2: Scrape fight cards from each event
        results = []
        for i, event in enumerate(past_events[:max_events]):
            logger.info(f"Scraping {event['name']} ({i+1}/{min(len(past_events), max_events)})")
            
            fight_card = self.scrape_fight_card_table(event['url'], event['name'])
            if fight_card['fights']:
                results.append(fight_card)
                logger.info(f"✅ Found {len(fight_card['fights'])} fights in {event['name']}")
            else:
                logger.warning(f"⚠️  No fights found in {event['name']}")
            
            # Be respectful to Wikipedia
            time.sleep(1)
        
        logger.info(f"Scraping complete! Found {len(results)} events with fight data")
        return results
    
    def save_results(self, results: List[Dict], output_dir: str = "data/exports"):
        """Save results to JSON and CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = os.path.join(output_dir, f"focused_ufc_events_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(results)} events to {json_file}")
        
        # Save as CSV
        csv_file = os.path.join(output_dir, f"focused_ufc_fights_{timestamp}.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'event_name', 'event_url', 'weight_class', 'fighter1', 'fighter2', 
                'winner', 'loser', 'method', 'round', 'time'
            ])
            
            for event in results:
                for fight in event.get('fights', []):
                    writer.writerow([
                        event.get('event_name', ''),
                        event.get('event_url', ''),
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
    """Main function to run the focused scraper"""
    scraper = FocusedUFCScraper()
    
    logger.info("Starting Focused UFC Event Scraper")
    
    # Scrape past events
    results = scraper.scrape_all_past_events(max_events=5)
    
    if results:
        # Save results
        json_file, csv_file = scraper.save_results(results)
        
        # Print summary
        total_fights = sum(len(event.get('fights', [])) for event in results)
        logger.info(f"🎉 Scraping complete! Found {len(results)} events with {total_fights} total fights")
        logger.info(f"📁 Results saved to: {json_file} and {csv_file}")
        
        # Print event summary
        for event in results[:5]:  # Show first 5 events
            logger.info(f"📅 {event.get('event_name', 'Unknown')}: {len(event.get('fights', []))} fights")
    else:
        logger.warning("No events were successfully scraped")

if __name__ == "__main__":
    main() 