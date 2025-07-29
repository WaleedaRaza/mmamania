import scrapy
from ufc_scraper.items import FighterRanking
from datetime import datetime
import re

class RankingsSpider(scrapy.Spider):
    name = "rankings"
    allowed_domains = ["ufc.com"]
    start_urls = ["https://www.ufc.com/rankings"]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 3,
        'CONCURRENT_REQUESTS': 8,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        """Parse the UFC rankings page"""
        self.logger.info(f"Parsing rankings page: {response.url}")
        
        # Find all ranking sections
        ranking_sections = response.css('.view-grouping')
        champions_set = set()  # Track champions to prevent duplicates
        
        for section in ranking_sections:
            # Extract division name
            header = section.css('.view-grouping-header::text').get()
            if not header:
                continue
                
            # Clean division name - remove "Top Rank" corruption
            division = header.strip().replace('Top Rank', '').strip()
            self.logger.info(f"Processing division: {division}")
            
            # Find the rankings table
            table = section.css('table').get()
            if not table:
                continue
                
            # Process champion (if present in caption)
            champion = section.css('.rankings--athlete--champion h5 a')
            if champion:
                champ_name = champion.css('::text').get().strip()
                champ_url = champion.attrib.get('href', '')
                
                if champ_name:
                    champions_set.add(champ_name)
                    
                    # Create champion ranking item
                    yield FighterRanking(
                        id=f"{division.lower().replace(' ', '-').replace('&', 'and')}-champion",
                        division=division,
                        rank=0,
                        fighter_name=champ_name,
                        record={'wins': 0, 'losses': 0, 'draws': 0},  # Will be filled by fighter spider
                        wins=0,
                        losses=0,
                        draws=0,
                        fighter_url=champ_url,
                        rank_change='',
                        is_champion=True,
                        scraped_at=datetime.utcnow().isoformat()
                    )
            
            # Process ranked fighters
            rows = section.css('tbody tr')
            for row in rows:
                cells = row.css('td')
                if len(cells) < 2:
                    continue
                    
                try:
                    # Extract rank
                    rank_text = cells[0].css('::text').get().strip()
                    if not rank_text or rank_text == 'NR':
                        continue
                    
                    rank = int(rank_text)
                    
                    # Extract fighter info
                    fighter_link = cells[1].css('a')
                    if not fighter_link:
                        continue
                        
                    fighter_name = fighter_link.css('::text').get().strip()
                    fighter_url = fighter_link.attrib.get('href', '')
                    
                    if not fighter_name or fighter_name in champions_set:
                        continue
                    
                    # Extract rank change
                    rank_change = ""
                    if len(cells) >= 3:
                        change_text = cells[2].css('::text').get().strip()
                        if change_text and change_text != "NR":
                            rank_change = change_text
                    
                    # Create ranking item
                    yield FighterRanking(
                        id=f"{division.lower().replace(' ', '-').replace('&', 'and')}-{rank}",
                        division=division,
                        rank=rank,
                        fighter_name=fighter_name,
                        record={'wins': 0, 'losses': 0, 'draws': 0},  # Will be filled by fighter spider
                        wins=0,
                        losses=0,
                        draws=0,
                        fighter_url=fighter_url,
                        rank_change=rank_change,
                        is_champion=False,
                        scraped_at=datetime.utcnow().isoformat()
                    )
                    
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Error parsing row: {e}")
                    continue
        
        self.logger.info("Rankings parsing completed") 