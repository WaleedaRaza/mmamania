import scrapy
import json
import re
from datetime import datetime
from urllib.parse import urljoin
import time

class FighterProfilesSpider(scrapy.Spider):
    name = 'fighter_profiles'
    allowed_domains = ['ufc.com']
    
    def __init__(self, fighter_urls=None, *args, **kwargs):
        super(FighterProfilesSpider, self).__init__(*args, **kwargs)
        self.fighter_urls = fighter_urls or []
        self.start_urls = [f"https://www.ufc.com{url}" for url in self.fighter_urls]
    
    def parse(self, response):
        """Parse fighter profile page and extract detailed information"""
        
        # Extract fighter slug from URL
        fighter_slug = response.url.split('/athlete/')[-1].split('#')[0]
        
        # Extract basic fighter info
        fighter_name = response.css('h1::text').get()
        nickname = response.css('.hero-athlete__nickname::text').get()
        
        # Extract record
        record_text = response.css('.hero-athlete__record::text').get()
        record = self.parse_record(record_text)
        
        # Extract division
        division = response.css('.hero-athlete__division::text').get()
        
        # Extract personal info
        personal_info = self.extract_personal_info(response)
        
        # Extract fight statistics
        stats = self.extract_fight_stats(response)
        
        # Extract complete fight history
        fight_history = self.extract_fight_history(response)
        
        # Create fighter profile
        fighter_profile = {
            'id': fighter_slug,
            'name': fighter_name,
            'nickname': nickname,
            'record': record,
            'wins': record['wins'],
            'losses': record['losses'],
            'draws': record['draws'],
            'division': division,
            'personal_info': personal_info,
            'stats': stats,
            'fight_history': fight_history,
            'fighter_url': f"/athlete/{fighter_slug}",
            'scraped_at': datetime.now().isoformat()
        }
        
        yield {
            'fighter_profile': fighter_profile
        }
    
    def parse_record(self, record_text):
        """Parse fighter record from text like '30-5-0 (W-L-D)'"""
        if not record_text:
            return {'wins': 0, 'losses': 0, 'draws': 0}
        
        # Extract numbers from record text
        match = re.search(r'(\d+)-(\d+)-(\d+)', record_text)
        if match:
            return {
                'wins': int(match.group(1)),
                'losses': int(match.group(2)),
                'draws': int(match.group(3))
            }
        return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def extract_personal_info(self, response):
        """Extract personal information from the Info section"""
        personal_info = {}
        
        # Extract info from the Info tab
        info_items = response.css('.athlete-info__item')
        for item in info_items:
            label = item.css('.athlete-info__label::text').get()
            value = item.css('.athlete-info__value::text').get()
            
            if label and value:
                label = label.strip().lower().replace(' ', '_')
                personal_info[label] = value.strip()
        
        return personal_info
    
    def extract_fight_stats(self, response):
        """Extract fight statistics"""
        stats = {}
        
        # Extract key stats
        stats_selectors = {
            'striking_accuracy': '.stats-section .stat-item:nth-child(1) .stat-value::text',
            'takedown_accuracy': '.stats-section .stat-item:nth-child(2) .stat-value::text',
            'sig_strikes_landed_per_min': '.stats-section .stat-item:nth-child(3) .stat-value::text',
            'sig_strikes_absorbed_per_min': '.stats-section .stat-item:nth-child(4) .stat-value::text',
            'takedown_avg_per_15_min': '.stats-section .stat-item:nth-child(5) .stat-value::text',
            'submission_avg_per_15_min': '.stats-section .stat-item:nth-child(6) .stat-value::text',
            'sig_strikes_defense': '.stats-section .stat-item:nth-child(7) .stat-value::text',
            'takedown_defense': '.stats-section .stat-item:nth-child(8) .stat-value::text',
            'knockdown_avg': '.stats-section .stat-item:nth-child(9) .stat-value::text',
            'average_fight_time': '.stats-section .stat-item:nth-child(10) .stat-value::text'
        }
        
        for stat_name, selector in stats_selectors.items():
            value = response.css(selector).get()
            if value:
                stats[stat_name] = value.strip()
        
        return stats
    
    def extract_fight_history(self, response):
        """Extract complete fight history from the athlete record section"""
        fight_history = []
        
        # Find all fight entries in the athlete record section
        fight_entries = response.css('.athlete-record__fight')
        
        for entry in fight_entries:
            fight = {}
            
            # Extract fight result (Win/Loss/Draw)
            result_element = entry.css('.athlete-record__result')
            if result_element:
                result_text = result_element.css('::text').get()
                if 'Win' in result_text:
                    fight['result'] = 'Win'
                elif 'Loss' in result_text:
                    fight['result'] = 'Loss'
                else:
                    fight['result'] = 'Draw'
            
            # Extract opponent name
            opponent = entry.css('.athlete-record__opponent::text').get()
            if opponent:
                fight['opponent'] = opponent.strip()
            
            # Extract fight details
            fight_details = entry.css('.athlete-record__details')
            if fight_details:
                # Extract event name
                event = fight_details.css('.athlete-record__event::text').get()
                if event:
                    fight['event'] = event.strip()
                
                # Extract date
                date = fight_details.css('.athlete-record__date::text').get()
                if date:
                    fight['date'] = date.strip()
                
                # Extract round
                round_text = fight_details.css('.athlete-record__round::text').get()
                if round_text:
                    fight['round'] = round_text.strip()
                
                # Extract time
                time_text = fight_details.css('.athlete-record__time::text').get()
                if time_text:
                    fight['time'] = time_text.strip()
                
                # Extract method
                method = fight_details.css('.athlete-record__method::text').get()
                if method:
                    fight['method'] = method.strip()
            
            if fight:  # Only add if we have at least some data
                fight_history.append(fight)
        
        return fight_history 