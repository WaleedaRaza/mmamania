#!/usr/bin/env python3
import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def normalize_name(name: str) -> str:
    name = name or ''
    name = name.replace('\xa0', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    # Normalize different dash types
    name = name.replace('–', '-').replace('—', '-')
    return name


def short_key(name: str) -> str:
    name = normalize_name(name)
    # Prefer the prefix up to the first colon for numbered events like "UFC 317: ..."
    if ':' in name:
        return name.split(':', 1)[0].strip().lower()
    return name.lower()


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


def build_event_link_map():
    logger.info('🔎 Loading List of UFC events...')
    list_page = requests.get(f"{BASE_WIKI}/wiki/List_of_UFC_events", headers=WIKI_HEADERS)
    list_page.raise_for_status()
    soup = BeautifulSoup(list_page.content, 'html.parser')
    mapping = {}
    rows = soup.find_all('table')
    for table in rows:
        for a in table.select('a[href^="/wiki/"]'):
            txt = normalize_name(a.get_text(strip=True))
            href = a.get('href')
            if not href:
                continue
            if 'UFC' in txt and ('/wiki/UFC_' in href or '/wiki/UFC' in href):
                mapping[txt] = href
    logger.info(f"📚 Built wiki link map: {len(mapping)} names")
    # Build short key index as well
    short_index = {}
    for full, href in mapping.items():
        short_index.setdefault(short_key(full), href)
    return mapping, short_index


def find_href_for_event(name: str, mapping, short_index):
    name_n = normalize_name(name)
    if name_n in mapping:
        return mapping[name_n]
    sk = short_key(name_n)
    if sk in short_index:
        return short_index[sk]
    # Fallback: try to extract "UFC <number>" token
    m = re.search(r'UFC\s+\d+', name_n, flags=re.I)
    if m:
        token = m.group(0).lower()
        for full, href in mapping.items():
            if full.lower().startswith(token):
                return href
    # Fallback: exact link title search ignoring diacritics/dashes variants handled by normalize
    return None


def fetch_and_parse_date(href: str):
    url = BASE_WIKI + href
    page = requests.get(url, headers=WIKI_HEADERS)
    page.raise_for_status()
    psoup = BeautifulSoup(page.content, 'html.parser')
    infobox = psoup.find('table', class_='infobox')
    if not infobox:
        return None
    for row in infobox.find_all('tr'):
        cells = row.find_all(['th', 'td'])
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True).lower()
            if 'date' in label:
                return parse_date(cells[1].get_text(strip=True))
    return None


def patch_event_date(event_id: str, dt: datetime):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/events?id=eq.{event_id}",
        headers=HEADERS,
        json={'date': dt.isoformat()}
    )
    return r.status_code in (200, 204)


def main():
    # Load DB events
    logger.info('🔍 Loading events from Supabase...')
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=id,name,date", headers=HEADERS)
    resp.raise_for_status()
    events = resp.json()
    logger.info(f"📊 Total events: {len(events)}")

    # Build wiki mapping
    mapping, short_index = build_event_link_map()

    updated = 0
    skipped = 0

    def work(ev):
        name = ev['name']
        ev_id = ev['id']
        href = find_href_for_event(name, mapping, short_index)
        if not href:
            logger.warning(f"No wiki href match for: {name}")
            return False
        dt = fetch_and_parse_date(href)
        if not dt:
            logger.warning(f"No date parsed for: {name}")
            return False
        ok = patch_event_date(ev_id, dt)
        if ok:
            logger.info(f"✅ {name} -> {dt.date()}")
        else:
            logger.error(f"❌ PATCH failed for {name}")
        return ok

    # Concurrency
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = [ex.submit(work, ev) for ev in events]
        for fut in as_completed(futures):
            try:
                if fut.result():
                    updated += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Thread error: {e}")
                skipped += 1

    logger.info(f"🎉 Date backfill complete. Updated: {updated}, Skipped: {skipped}")


if __name__ == '__main__':
    main()