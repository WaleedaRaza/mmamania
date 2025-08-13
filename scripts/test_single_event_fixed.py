#!/usr/bin/env python3
"""
Test Single Event Fixed
Test the fixed scraper with global fight order
"""

import os
import sys
import requests
import logging
import time
import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

class FixedWikipediaScraper:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.supabase_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
        }

    def test_single_event_fixed(self):
        """Test scraping a single event with fixed global fight order"""
        logger.info("🧪 Testing single event with fixed global fight order...")
        
        # Test with UFC 317: Topuria vs. Oliveira (the one with multiple card sections)
        event_url = "https://en.wikipedia.org/wiki/UFC_317"
        event_name = "UFC 317: Topuria vs. Oliveira"
        
        logger.info(f"🔍 Testing event: {event_name}")
        logger.info(f"🔗 URL: {event_url}")
        
        try:
            # Get the event page
            response = requests.get(event_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("✅ Successfully loaded event page")
            
            # Find all tables
            tables = soup.find_all('table')
            all_fights = []
            global_fight_order = 1  # Maintain global fight order across all tables
            
            logger.info(f"📊 Found {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                logger.info(f"🔍 Checking table #{table_idx + 1}")
                
                # Check if this is a fight table
                if self._is_fight_table(table):
                    logger.info(f"✅ Found fight table #{table_idx + 1}")
                    
                    # Parse fights with global fight order
                    table_fights = self._parse_fight_table_fixed(table, global_fight_order)
                    all_fights.extend(table_fights)
                    logger.info(f"📊 Table #{table_idx + 1}: {len(table_fights)} fights (global order {global_fight_order}-{global_fight_order + len(table_fights) - 1})")
                    
                    # Update global fight order for next table
                    global_fight_order += len(table_fights)
            
            logger.info(f"🎯 TOTAL: Found {len(all_fights)} fights with global ordering:")
            
            for i, fight in enumerate(all_fights):
                main_text = " (MAIN EVENT)" if fight['is_main_event'] else ""
                co_main_text = " (CO-MAIN)" if fight['is_co_main_event'] else ""
                event_text = main_text + co_main_text
                logger.info(f"   {fight['fight_order']}. {fight['winner_name']} def. {fight['loser_name']} - {fight['weight_class']}{event_text}")
            
            return all_fights
            
        except Exception as e:
            logger.error(f"❌ Error testing single event: {e}")
            return []

    def _is_fight_table(self, table):
        """Check if table contains fight data"""
        try:
            # Look for weight class column header
            headers = table.find_all('th')
            for header in headers:
                if 'weight' in header.get_text().lower() or 'class' in header.get_text().lower():
                    return True
            
            # Look for "def." pattern in table content
            table_text = table.get_text()
            if 'def.' in table_text:
                return True
                
            return False
        except:
            return False

    def _parse_fight_table_fixed(self, table, global_fight_order):
        """Parse fight table with global fight order"""
        fights = []
        rows = table.find_all('tr')
        
        if len(rows) < 2:
            return fights
        
        fight_order = global_fight_order  # Use the global fight order
        
        # Process each row in table order
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = row.find_all(['td', 'th'])
            
            # Skip section headers (colspan=8)
            if len(cells) == 1 and cells[0].get('colspan') == '8':
                continue
                
            # Need exactly 8 columns for fight data
            if len(cells) == 8:
                try:
                    fight_data = self._parse_fight_row_fixed(cells, fight_order)
                    if fight_data:
                        fights.append(fight_data)
                        fight_order += 1  # Only increment if a valid fight was created
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing fight row {row_idx}: {e}")
                    continue
        
        return fights

    def _parse_fight_row_fixed(self, cells, fight_order):
        """Parse a single fight row with global fight order"""
        try:
            # Column 0: Weight Class
            weight_class = cells[0].get_text(strip=True)
            
            # Column 1: Winner
            winner_name = self._clean_fighter_name(cells[1].get_text(strip=True))
            
            # Column 2: "def." (skip this)
            # Column 3: Loser  
            loser_name = self._clean_fighter_name(cells[3].get_text(strip=True))
            
            # Column 4: Method
            method = cells[4].get_text(strip=True)
            
            # Column 5: Round
            round_text = cells[5].get_text(strip=True)
            round_num = int(round_text) if round_text.isdigit() else None
            
            # Column 6: Time
            time = cells[6].get_text(strip=True)
            
            # Column 7: Notes (skip this)
            
            # Skip fights with empty fighter names
            if not winner_name or not loser_name or winner_name.strip() == '' or loser_name.strip() == '':
                logger.warning(f"⚠️ Skipping fight with empty names: '{winner_name}' vs '{loser_name}'")
                return None
            
            # Simple logic: first fight = main event, second fight = co-main
            is_main_event = fight_order == 1
            is_co_main_event = fight_order == 2
            
            # Clean up method text
            method = self._clean_method_text(method)
            
            return {
                'weight_class': weight_class,
                'winner_name': winner_name,
                'loser_name': loser_name,
                'method': method,
                'round': round_num,
                'time': time,
                'fight_order': fight_order,
                'is_main_event': is_main_event,
                'is_co_main_event': is_co_main_event
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing fight row: {e}")
            return None

    def _clean_fighter_name(self, name):
        """Clean fighter name by removing extra whitespace and special characters"""
        try:
            # Remove extra whitespace
            name = re.sub(r'\s+', ' ', name.strip())
            
            # Remove common prefixes/suffixes
            name = re.sub(r'^\s*\([^)]*\)\s*', '', name)  # Remove (c) or other prefixes
            name = re.sub(r'\s*\([^)]*\)\s*$', '', name)  # Remove suffixes
            
            # Remove HTML entities
            name = name.replace('&nbsp;', ' ')
            
            return name.strip()
        except:
            return name.strip()

    def _clean_method_text(self, method):
        """Clean method text"""
        try:
            # Remove extra whitespace
            method = re.sub(r'\s+', ' ', method.strip())
            
            # Remove HTML entities
            method = method.replace('&nbsp;', ' ')
            
            return method.strip()
        except:
            return method.strip()

def main():
    scraper = FixedWikipediaScraper()
    fights = scraper.test_single_event_fixed()
    
    if fights:
        print(f"\n✅ Successfully parsed {len(fights)} fights with global ordering!")
        print("📊 Expected order vs Actual order:")
        print("Expected: Ilia Topuria (1), Alexandre Pantoja (2), Joshua Van (3), etc.")
        print("Actual:")
        for fight in fights:
            main_text = " (MAIN EVENT)" if fight['is_main_event'] else ""
            co_main_text = " (CO-MAIN)" if fight['is_co_main_event'] else ""
            event_text = main_text + co_main_text
            print(f"   {fight['fight_order']}. {fight['winner_name']} def. {fight['loser_name']} - {fight['weight_class']}{event_text}")
    else:
        print("❌ Failed to parse fights")

if __name__ == "__main__":
    main() 