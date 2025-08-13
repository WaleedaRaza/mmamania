#!/usr/bin/env python3
import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

WIKI_HEADERS = {'User-Agent': 'Mozilla/5.0'}
BASE_WIKI = 'https://en.wikipedia.org'


def parse_date(text: str):
    try:
        if not text:
            return None
        cleaned = re.sub(r'\[[^\]]*\]', '', text).replace('\xa0', ' ')
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        iso = re.search(r'(\d{4}-\d{2}-\d{2})', cleaned)
        if iso:
            return datetime.strptime(iso.group(1), '%Y-%m-%d')
        for fmt in ['%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y', '%Y-%m-%d']:
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None


def main():
    # Get all events with missing or sentinel (<= 1905-01-01) dates
    logger.info('🔍 Loading events to backfill...')
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=id,name,location,venue,date", headers=HEADERS)
    resp.raise_for_status()
    events = resp.json()

    candidates = []
    for e in events:
        d = e.get('date')
        if not d:
            candidates.append(e)
            continue
        try:
            dt = datetime.fromisoformat(d.replace('Z', '+00:00'))
            if dt.year <= 1905:
                candidates.append(e)
        except Exception:
            candidates.append(e)

    logger.info(f"📊 Candidates needing date backfill: {len(candidates)}")

    # Discover wiki links from main list page mapping by name
    list_page = requests.get(f"{BASE_WIKI}/wiki/List_of_UFC_events", headers=WIKI_HEADERS)
    list_page.raise_for_status()
    soup = BeautifulSoup(list_page.content, 'html.parser')

    name_to_href = {}
    for a in soup.select('table a[href^="/wiki/"]'):
        txt = a.get_text(strip=True)
        href = a.get('href')
        if not href:
            continue
        if 'UFC' in txt and '/wiki/UFC_' in href:
            name_to_href[txt] = href

    updated = 0
    for e in candidates:
        name = e.get('name')
        href = name_to_href.get(name)
        if not href:
            logger.warning(f"No wiki href for {name}")
            continue
        url = BASE_WIKI + href
        page = requests.get(url, headers=WIKI_HEADERS)
        page.raise_for_status()
        psoup = BeautifulSoup(page.content, 'html.parser')
        infobox = psoup.find('table', class_='infobox')
        if not infobox:
            continue
        new_date = None
        for row in infobox.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                if 'date' in label:
                    new_date = parse_date(cells[1].get_text(strip=True))
                    break
        if new_date is None:
            logger.warning(f"No date parsed for {name}")
            continue
        # Update in supabase
        patch = requests.patch(
            f"{SUPABASE_URL}/rest/v1/events?id=eq.{e['id']}",
            headers=HEADERS,
            json={'date': new_date.isoformat()}
        )
        if patch.status_code in (204, 200):
            updated += 1
            logger.info(f"✅ Updated {name} -> {new_date.date()}")
        else:
            logger.error(f"❌ Failed updating {name}: {patch.status_code} {patch.text}")

    logger.info(f"🎉 Backfill complete: {updated} events updated")


if __name__ == '__main__':
    main()