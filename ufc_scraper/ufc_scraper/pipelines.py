# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import os
from datetime import datetime


class UfcScraperPipeline:
    def process_item(self, item, spider):
        return item

class UFCScraperPipeline:
    def process_item(self, item, spider):
        """Process each scraped item"""
        # Validate item fields explicitly
        for field in item.fields:
            if field not in item or item[field] is None:
                item[field] = 'N/A' if isinstance(item.fields[field], str) else 0
        return item

class UFCMergePipeline:
    """Pipeline to merge rankings and fighters data"""
    
    def __init__(self):
        self.rankings = []
        self.fighters = []
        self.merged_data = {}

    def process_item(self, item, spider):
        """Process items and categorize them"""
        if spider.name == 'rankings':
            self.rankings.append(dict(item))
        elif spider.name == 'fighters':
            self.fighters.append(dict(item))
        return item

    def close_spider(self, spider):
        """Merge data when spider closes"""
        if spider.name in ['rankings', 'fighters']:
            self._merge_data()
            self._save_merged_data()

    def _merge_data(self):
        """Merge rankings and fighters data"""
        print("🔄 Merging rankings and fighters data...")
        
        # Create fighters lookup by URL
        fighters_by_url = {}
        for fighter in self.fighters:
            fighters_by_url[fighter['fighter_url']] = fighter

        # Merge fighter data into rankings
        merged_rankings = []
        for ranking in self.rankings:
            fighter_url = ranking.get('fighter_url', '')
            fighter_data = fighters_by_url.get(fighter_url, {})
            
            # Merge fighter data into ranking
            merged_ranking = ranking.copy()
            merged_ranking.update({
                'fighter_profile': fighter_data,
                'has_detailed_profile': bool(fighter_data),
                'nickname': fighter_data.get('nickname', ''),
                'personal_info': fighter_data.get('personal_info', {}),
                'stats': fighter_data.get('stats', {}),
                'fight_history': fighter_data.get('fight_history', [])
            })
            
            merged_rankings.append(merged_ranking)

        # Create final merged data structure
        self.merged_data = {
            'rankings': merged_rankings,
            'fighters': self.fighters,
            'scraped_at': datetime.now().isoformat(),
            'total_rankings': len(merged_rankings),
            'total_fighters': len(self.fighters),
            'rankings_with_profiles': len([r for r in merged_rankings if r['has_detailed_profile']])
        }

    def _save_merged_data(self):
        """Save merged data to multiple locations"""
        output_files = [
            'ufc_merged_data.json',
            '../assets/data/ufc_data.json'
        ]
        
        for output_file in output_files:
            try:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.merged_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved merged data to: {output_file}")
            except Exception as e:
                print(f"❌ Error saving to {output_file}: {e}")

        # Print summary
        print(f"\n📊 Data Summary:")
        print(f"   Rankings: {self.merged_data['total_rankings']}")
        print(f"   Fighters: {self.merged_data['total_fighters']}")
        print(f"   Rankings with profiles: {self.merged_data['rankings_with_profiles']}")

class UFCDataCleanPipeline:
    """Pipeline to clean and validate UFC data"""
    
    def process_item(self, item, spider):
        """Clean and validate item data"""
        if spider.name == 'rankings':
            return self._clean_ranking(item)
        elif spider.name == 'fighters':
            return self._clean_fighter(item)
        return item

    def _clean_ranking(self, item):
        """Clean ranking data"""
        # Ensure record is properly structured
        if 'record' in item and isinstance(item['record'], dict):
            record = item['record']
            item['wins'] = record.get('wins', 0)
            item['losses'] = record.get('losses', 0)
            item['draws'] = record.get('draws', 0)
        
        # Clean division name
        if 'division' in item:
            item['division'] = item['division'].replace('Top Rank', '').strip()
        
        # Ensure rank is integer
        if 'rank' in item:
            try:
                item['rank'] = int(item['rank'])
            except (ValueError, TypeError):
                item['rank'] = 0
        
        return item

    def _clean_fighter(self, item):
        """Clean fighter data"""
        # Ensure record is properly structured
        if 'record' in item and isinstance(item['record'], dict):
            record = item['record']
            item['wins'] = record.get('wins', 0)
            item['losses'] = record.get('losses', 0)
            item['draws'] = record.get('draws', 0)
        
        # Clean nickname (remove extra quotes)
        if 'nickname' in item and item['nickname']:
            nickname = item['nickname'].strip()
            if nickname.startswith('"') and nickname.endswith('"'):
                item['nickname'] = nickname[1:-1]
        
        return item
