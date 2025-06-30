import scrapy
from ufc_scraper.items import FighterProfile
from datetime import datetime
import os
import re

class FightersSpider(scrapy.Spider):
    name = "fighters"
    allowed_domains = ["ufc.com"]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'CONCURRENT_REQUESTS': 4,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, input_file=None, *args, **kwargs):
        super(FightersSpider, self).__init__(*args, **kwargs)
        self.input_file = input_file or 'ufc_scraper/input/urls.txt'

    def start_requests(self):
        """Start requests for fighter URLs from input file"""
        fighter_urls = self._load_fighter_urls()
        
        if not fighter_urls:
            self.logger.warning("No fighter URLs found, using test URLs")
            fighter_urls = ["/athlete/islam-makhachev", "/athlete/alexander-volkanovski"]
        
        self.logger.info(f"Starting to scrape {len(fighter_urls)} fighter profiles")
        
        for fighter_url in fighter_urls:
            full_url = f"https://www.ufc.com{fighter_url}"
            yield scrapy.Request(
                url=full_url,
                callback=self.parse,
                meta={'fighter_url': fighter_url}
            )

    def _load_fighter_urls(self):
        """Load fighter URLs from input file"""
        try:
            if os.path.exists(self.input_file):
                with open(self.input_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                self.logger.info(f"Loaded {len(urls)} fighter URLs from {self.input_file}")
                return urls
            else:
                self.logger.warning(f"Input file not found: {self.input_file}")
                return []
        except Exception as e:
            self.logger.error(f"Error loading fighter URLs: {e}")
            return []

    def parse(self, response):
        """Parse individual fighter profile page"""
        fighter_url = response.meta.get('fighter_url', '')
        self.logger.info(f"Parsing fighter profile: {fighter_url}")
        
        try:
            # Extract basic fighter info
            name = self._parse_name(response)
            nickname = self._parse_nickname(response)
            record = self._parse_record(response)
            division = self._parse_division(response)
            
            # Extract detailed information
            stats = self._parse_stats(response)
            personal_info = self._parse_personal_info(response)
            fight_history = self._parse_fight_history(response)
            
            # Create fighter profile item
            yield FighterProfile(
                id=fighter_url.replace('/athlete/', '').replace('/', ''),
                name=name,
                nickname=nickname,
                record=record,
                wins=record.get('wins', 0),
                losses=record.get('losses', 0),
                draws=record.get('draws', 0),
                division=division,
                height=personal_info.get('height', ''),
                weight=personal_info.get('weight', ''),
                reach=personal_info.get('reach', ''),
                stance=personal_info.get('stance', ''),
                dob=personal_info.get('dob', ''),
                hometown=personal_info.get('hometown', ''),
                team=personal_info.get('team', ''),
                stats=stats,
                personal_info=personal_info,
                fight_history=fight_history,
                fighter_url=fighter_url,
                scraped_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing fighter {fighter_url}: {e}")

    def _parse_name(self, response):
        """Parse fighter name"""
        try:
            name = response.css('h1.hero-profile__name::text').get()
            return name.strip() if name else 'Unknown'
        except Exception as e:
            self.logger.warning(f"Error parsing name: {e}")
            return 'Unknown'

    def _parse_nickname(self, response):
        """Parse fighter nickname"""
        try:
            nickname = response.css('.hero-profile__nickname::text').get()
            return nickname.strip() if nickname else ''
        except Exception as e:
            self.logger.warning(f"Error parsing nickname: {e}")
            return ''

    def _parse_record(self, response):
        """Parse fighter record from text"""
        try:
            record_text = response.css('p.hero-profile__division-body::text').get()
            if not record_text:
                return {'wins': 0, 'losses': 0, 'draws': 0}
            
            record_text = record_text.strip()
            # Handle format like "27-1-0 (W-L-D)"
            if '(' in record_text:
                record_part = record_text.split('(')[0].strip()
            else:
                record_part = record_text
            
            parts = record_part.split('-')
            if len(parts) >= 2:
                wins = int(parts[0]) if parts[0].isdigit() else 0
                losses = int(parts[1]) if parts[1].isdigit() else 0
                draws = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                return {'wins': wins, 'losses': losses, 'draws': draws}
            
            return {'wins': 0, 'losses': 0, 'draws': 0}
        except Exception as e:
            self.logger.warning(f"Error parsing record: {e}")
            return {'wins': 0, 'losses': 0, 'draws': 0}

    def _parse_division(self, response):
        """Parse fighter division/weight class"""
        try:
            division = response.css('.hero-profile__division::text').get()
            return division.strip() if division else ''
        except Exception as e:
            self.logger.warning(f"Error parsing division: {e}")
            return ''

    def _parse_stats(self, response):
        """Parse fighter statistics from stats section"""
        stats = {}
        try:
            # Look for stats in the stats section
            stats_section = response.css('#athlete-stats, .stats-section')
            
            if stats_section:
                # Extract various stats using CSS selectors
                stat_mappings = {
                    'SLpM': 'slpm',
                    'Str. Acc': 'str_acc',
                    'SApM': 'sapm',
                    'Str. Def': 'str_def',
                    'TD Avg': 'td_avg',
                    'TD Acc': 'td_acc',
                    'TD Def': 'td_def',
                    'Sub. Avg': 'sub_avg'
                }
                
                for stat_name, stat_key in stat_mappings.items():
                    # Try different selectors for each stat
                    selectors = [
                        f'[data-stat="{stat_name.lower().replace(" ", "-")}"]::text',
                        f'[data-stat="{stat_name.lower()}"]::text'
                    ]
                    
                    for selector in selectors:
                        value = response.css(selector).get()
                        if value:
                            cleaned_value = self._clean_stat_value(value.strip())
                            if cleaned_value:
                                stats[stat_key] = cleaned_value
                                break
            
            return stats
        except Exception as e:
            self.logger.warning(f"Error parsing stats: {e}")
            return {}

    def _clean_stat_value(self, value):
        """Clean and normalize stat values"""
        try:
            if '%' in value:
                return value.replace('%', '')
            elif value.replace('.', '').replace('-', '').isdigit():
                return value
            else:
                return value.strip()
        except:
            return value

    def _parse_personal_info(self, response):
        """Parse personal information from fighter page"""
        personal_info = {}
        try:
            # Look for personal info in various sections
            info_sections = response.css('.hero-profile__info, .fighter-info, .personal-info')
            
            for section in info_sections:
                # Extract table rows
                rows = section.css('tr')
                
                for row in rows:
                    try:
                        key_elem = row.css('th')
                        value_elem = row.css('td')
                        
                        if key_elem and value_elem:
                            key = key_elem.css('::text').get().strip().lower()
                            value = value_elem.css('::text').get().strip()
                            
                            # Normalize key names
                            key_mapping = {
                                'height': 'height',
                                'weight': 'weight',
                                'reach': 'reach',
                                'stance': 'stance',
                                'date of birth': 'dob',
                                'born': 'dob',
                                'hometown': 'hometown',
                                'country': 'hometown',
                                'team': 'team',
                                'gym': 'team'
                            }
                            
                            normalized_key = key_mapping.get(key, key)
                            if normalized_key and value:
                                personal_info[normalized_key] = value
                    except Exception as e:
                        continue
            
            return personal_info
        except Exception as e:
            self.logger.warning(f"Error parsing personal info: {e}")
            return {}

    def _parse_fight_history(self, response):
        """Parse fighter's fight history"""
        fight_history = []
        try:
            # Look for fight history in the athlete record section
            fights = response.css('.athlete-record .c-card-event--athlete-fight')
            
            for fight in fights:
                try:
                    # Extract fight details
                    fighters = fight.css('.c-card-event--athlete-fight__headline::text').get()
                    date = fight.css('.c-card-event--athlete-fight__date::text').get()
                    result = fight.css('.c-card-event--athlete-fight__result::text').get()
                    method = fight.css('.c-card-event--athlete-fight__method::text').get()
                    round_num = fight.css('.c-card-event--athlete-fight__round::text').get()
                    time = fight.css('.c-card-event--athlete-fight__time::text').get()
                    
                    if fighters:
                        fight_data = {
                            'opponent': fighters.strip(),
                            'date': date.strip() if date else '',
                            'result': result.strip() if result else '',
                            'method': method.strip() if method else '',
                            'round': round_num.strip() if round_num else '',
                            'time': time.strip() if time else ''
                        }
                        fight_history.append(fight_data)
                except Exception as e:
                    self.logger.warning(f"Error parsing individual fight: {e}")
                    continue
            
            return fight_history
        except Exception as e:
            self.logger.warning(f"Error parsing fight history: {e}")
            return []
