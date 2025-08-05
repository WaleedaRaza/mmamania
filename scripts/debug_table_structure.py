#!/usr/bin/env python3
"""
Debug Table Structure
Debug the table structure of the Wikipedia UFC events page
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_table_structure():
    """Debug the table structure of the Wikipedia page"""
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
    
    try:
        logger.info(f"🔍 Loading main UFC events page: {url}")
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        logger.info("✅ Successfully loaded main UFC events page")
        
        # Find all headings
        headings = soup.find_all(['h2', 'h3'])
        logger.info(f"📋 Found {len(headings)} headings")
        
        for i, heading in enumerate(headings):
            heading_text = heading.get_text(strip=True)
            logger.info(f"  Heading {i}: {heading_text}")
        
        # Find the "Past events" section
        past_events_heading = None
        for heading in soup.find_all(['h2', 'h3']):
            if 'Past events' in heading.get_text():
                past_events_heading = heading
                break
        
        if not past_events_heading:
            logger.error("❌ Could not find 'Past events' section")
            return
        
        logger.info("✅ Found 'Past events' section")
        
        # Look for tables in the entire document
        all_tables = soup.find_all('table')
        logger.info(f"📊 Found {len(all_tables)} total tables on page")
        
        # Analyze each table
        for table_idx, table in enumerate(all_tables):
            table_text = table.get_text()
            rows = table.find_all('tr')
            
            logger.info(f"📊 Table {table_idx + 1}: {len(rows)} rows")
            
            # Check if this table contains UFC event data
            if 'UFC' in table_text and ('Date' in table_text or 'Event' in table_text):
                logger.info(f"  ✅ Table {table_idx + 1} appears to contain UFC event data")
                
                # Look at first few rows
                for i, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        logger.info(f"    Row {i}: {cell_texts}")
            else:
                logger.info(f"  ❌ Table {table_idx + 1} does not appear to contain UFC event data")
        
        # Now try to find the correct table more specifically
        logger.info("\n🔍 Looking for the specific Past events table...")
        
        # Find all tables and check which one has the most UFC links
        best_table = None
        max_ufc_links = 0
        
        for table_idx, table in enumerate(all_tables):
            table_text = table.get_text()
            ufc_count = table_text.count('UFC')
            
            if ufc_count > max_ufc_links:
                max_ufc_links = ufc_count
                best_table = table
                logger.info(f"  📊 Table {table_idx + 1} has {ufc_count} UFC references")
        
        if best_table:
            logger.info(f"✅ Best candidate table has {max_ufc_links} UFC references")
            
            # Analyze the best table
            rows = best_table.find_all('tr')
            logger.info(f"📋 Best table has {len(rows)} rows")
            
            # Look at first few rows
            for i, row in enumerate(rows[:5]):
                cells = row.find_all(['td', 'th'])
                if cells:
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    logger.info(f"  Row {i}: {cell_texts}")
        else:
            logger.error("❌ No suitable table found")
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_table_structure() 