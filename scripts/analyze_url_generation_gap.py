#!/usr/bin/env python3
"""
Analyze URL Generation Gap
Analyze why certain events weren't found and compare URL generation vs actual links
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_url_generation_gap():
    """Analyze the gap between URL generation and actual Wikipedia links"""
    url = "https://en.wikipedia.org/wiki/List_of_UFC_events"
    
    try:
        logger.info(f"🔍 Loading main UFC events page: {url}")
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        logger.info("✅ Successfully loaded main UFC events page")
        
        # Find all tables
        all_tables = soup.find_all('table')
        
        # Find the table with the most UFC references (this is the Past events table)
        best_table = None
        max_ufc_links = 0
        
        for table_idx, table in enumerate(all_tables):
            table_text = table.get_text()
            ufc_count = table_text.count('UFC')
            
            if ufc_count > max_ufc_links:
                max_ufc_links = ufc_count
                best_table = table
        
        if not best_table:
            logger.error("❌ Could not find Past events table")
            return
        
        logger.info(f"✅ Found Past events table with {max_ufc_links} UFC references")
        
        # Analyze the table to find actual links vs generated URLs
        rows = best_table.find_all('tr')
        
        # Sample of events that failed in our test
        failed_events = [
            "UFC 318: Holloway vs. Poirier 3",
            "UFC 317: Topuria vs. Oliveira", 
            "UFC 316: Dvalishvili vs. O'Malley 2",
            "UFC 315: Muhammad vs. Della Maddalena",
            "UFC 314: Volkanovski vs. Lopes",
            "UFC 313: Pereira vs. Ankalaev",
            "UFC 312: du Plessis vs. Strickland 2",
            "UFC 311: Makhachev vs. Moicano",
            "UFC 310: Pantoja vs. Asakura",
            "UFC 309: Jones vs. Miocic",
            "UFC 308: Topuria vs. Holloway",
            "UFC 307: Pereira vs. Rountree Jr.",
            "UFC 306: O'Malley vs. Dvalishvili",
            "UFC 305: du Plessis vs. Adesanya",
            "UFC 303: Pereira vs. Procházka 2"
        ]
        
        logger.info("🔍 Analyzing actual links vs generated URLs...")
        
        actual_links = []
        generated_urls = []
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 6:
                try:
                    event_name = cells[1].get_text(strip=True)
                    
                    # Skip header row
                    if event_name == 'Event':
                        continue
                    
                    # Find actual links in the event cell
                    event_cell = cells[1]
                    links = event_cell.find_all('a')
                    
                    if links:
                        for link in links:
                            href = link.get('href')
                            if href and 'wiki' in href:
                                actual_link = f"https://en.wikipedia.org{href}"
                                actual_links.append({
                                    'event_name': event_name,
                                    'actual_url': actual_link,
                                    'link_text': link.get_text(strip=True)
                                })
                                logger.info(f"🔗 Found actual link: {event_name} -> {actual_link}")
                    
                    # Generate URL using our current logic
                    generated_url = generate_url_from_name(event_name)
                    generated_urls.append({
                        'event_name': event_name,
                        'generated_url': generated_url
                    })
                    
                    # Check if this is one of our failed events
                    if event_name in failed_events:
                        logger.info(f"❌ FAILED EVENT ANALYSIS: {event_name}")
                        logger.info(f"   Generated URL: {generated_url}")
                        
                        # Check if there's an actual link for this event
                        actual_link_found = None
                        for actual in actual_links:
                            if actual['event_name'] == event_name:
                                actual_link_found = actual['actual_url']
                                break
                        
                        if actual_link_found:
                            logger.info(f"   Actual link exists: {actual_link_found}")
                            logger.info(f"   GAP: We should use actual link instead of generating URL!")
                        else:
                            logger.info(f"   No actual link found in table")
                            logger.info(f"   GAP: Event might not have a Wikipedia page")
                    
                except Exception as e:
                    continue
        
        # Summary
        logger.info(f"\n📊 ANALYSIS SUMMARY")
        logger.info("=" * 50)
        logger.info(f"🔗 Actual links found: {len(actual_links)}")
        logger.info(f"🔧 Generated URLs: {len(generated_urls)}")
        
        # Check how many events have actual links
        events_with_links = len([a for a in actual_links])
        total_events = len(generated_urls)
        
        logger.info(f"📊 Events with actual Wikipedia links: {events_with_links}/{total_events}")
        logger.info(f"📊 Events without Wikipedia pages: {total_events - events_with_links}")
        
        # Show sample of actual links
        logger.info(f"\n🔗 Sample of actual links found:")
        for i, link in enumerate(actual_links[:10], 1):
            logger.info(f"  {i}. {link['event_name']} -> {link['actual_url']}")
        
        return actual_links, generated_urls
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return [], []

def generate_url_from_name(event_name):
    """Generate URL using our current logic"""
    url_name = event_name.replace(' ', '_')
    
    # Handle special cases for UFC event names
    if 'UFC on ESPN:' in url_name:
        url_name = url_name.replace('UFC_on_ESPN:', 'UFC_on_ESPN:_')
    elif 'UFC on ABC:' in url_name:
        url_name = url_name.replace('UFC_on_ABC:', 'UFC_on_ABC:_')
    elif 'UFC on Fox:' in url_name:
        url_name = url_name.replace('UFC_on_Fox:', 'UFC_on_Fox:_')
    elif 'UFC on FX:' in url_name:
        url_name = url_name.replace('UFC_on_FX:', 'UFC_on_FX:_')
    elif 'UFC on Fuel TV:' in url_name:
        url_name = url_name.replace('UFC_on_Fuel_TV:', 'UFC_on_Fuel_TV:_')
    
    return f"https://en.wikipedia.org/wiki/{url_name}"

if __name__ == "__main__":
    analyze_url_generation_gap() 