import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)

class UFCDataProcessor:
    def __init__(self):
        self.processed_data = {}
        
    def process_raw_data(self, raw_data: Dict) -> Dict:
        """Process raw scraped data into structured format for FightHub"""
        logger.info("Processing raw UFC data...")
        
        try:
            # Process rankings
            rankings = self._process_rankings(raw_data.get('rankings', []))
            
            # Process events
            upcoming_events = self._process_events(raw_data.get('upcoming_events', []))
            past_events = self._process_events(raw_data.get('past_events', []))
            
            # Process fights
            upcoming_fights = self._process_fights(raw_data.get('upcoming_fights', []))
            past_results = self._process_fight_results(raw_data.get('past_results', []))
            
            # Create fighters database
            fighters = self._create_fighters_database(rankings, upcoming_fights, past_results)
            
            # Create processed dataset
            processed_data = {
                'rankings': rankings,
                'upcoming_events': upcoming_events,
                'past_events': past_events,
                'upcoming_fights': upcoming_fights,
                'past_results': past_results,
                'fighters': fighters,
                'processed_at': datetime.now().isoformat(),
                'metadata': {
                    'total_rankings': len(rankings),
                    'total_upcoming_events': len(upcoming_events),
                    'total_past_events': len(past_events),
                    'total_upcoming_fights': len(upcoming_fights),
                    'total_past_results': len(past_results),
                    'total_fighters': len(fighters)
                }
            }
            
            self.processed_data = processed_data
            logger.info("UFC data processing completed!")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing UFC data: {e}")
            return {}
    
    def _process_rankings(self, raw_rankings: List[Dict]) -> List[Dict]:
        """Process and clean rankings data"""
        processed_rankings = []
        
        for ranking in raw_rankings:
            try:
                # Clean fighter name
                fighter_name = ranking.get('fighter_name', '').strip()
                if not fighter_name:
                    continue
                
                # Parse record
                record = self._parse_record(ranking.get('record', ''))
                
                # Create processed ranking
                processed_ranking = {
                    'id': self._generate_id(fighter_name),
                    'division': ranking.get('division', '').replace('-', ' ').title(),
                    'rank': ranking.get('rank', 0),
                    'fighter_name': fighter_name,
                    'record': record,
                    'wins': record.get('wins', 0),
                    'losses': record.get('losses', 0),
                    'draws': record.get('draws', 0),
                    'fighter_url': ranking.get('fighter_url'),
                    'scraped_at': ranking.get('scraped_at')
                }
                
                processed_rankings.append(processed_ranking)
                
            except Exception as e:
                logger.error(f"Error processing ranking: {e}")
                continue
        
        return processed_rankings
    
    def _process_events(self, raw_events: List[Dict]) -> List[Dict]:
        """Process and clean events data"""
        processed_events = []
        
        for event in raw_events:
            try:
                # Clean event title
                title = event.get('title', '').strip()
                if not title:
                    continue
                
                # Parse date
                date_str = event.get('date', '')
                parsed_date = self._parse_date(date_str)
                
                # Create processed event
                processed_event = {
                    'id': self._generate_id(title),
                    'title': title,
                    'date': parsed_date,
                    'date_str': date_str,
                    'location': event.get('location', 'TBD').strip(),
                    'event_url': event.get('event_url'),
                    'type': event.get('type', 'upcoming'),
                    'scraped_at': event.get('scraped_at')
                }
                
                processed_events.append(processed_event)
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                continue
        
        return processed_events
    
    def _process_fights(self, raw_fights: List[Dict]) -> List[Dict]:
        """Process and clean fights data"""
        processed_fights = []
        
        for fight in raw_fights:
            try:
                # Extract fighter names
                fighter1_name = fight.get('fighter1', {}).get('name', '').strip()
                fighter2_name = fight.get('fighter2', {}).get('name', '').strip()
                
                if not fighter1_name or not fighter2_name:
                    continue
                
                # Parse records
                record1 = self._parse_record(fight.get('fighter1', {}).get('record', ''))
                record2 = self._parse_record(fight.get('fighter2', {}).get('record', ''))
                
                # Create processed fight
                processed_fight = {
                    'id': self._generate_id(f"{fighter1_name} vs {fighter2_name}"),
                    'fighter1': {
                        'name': fighter1_name,
                        'record': record1,
                        'wins': record1.get('wins', 0),
                        'losses': record1.get('losses', 0),
                        'draws': record1.get('draws', 0)
                    },
                    'fighter2': {
                        'name': fighter2_name,
                        'record': record2,
                        'wins': record2.get('wins', 0),
                        'losses': record2.get('losses', 0),
                        'draws': record2.get('draws', 0)
                    },
                    'weight_class': fight.get('weight_class', 'Unknown').strip(),
                    'fight_type': fight.get('fight_type', 'Unknown').strip(),
                    'scraped_at': fight.get('scraped_at')
                }
                
                processed_fights.append(processed_fight)
                
            except Exception as e:
                logger.error(f"Error processing fight: {e}")
                continue
        
        return processed_fights
    
    def _process_fight_results(self, raw_results: List[Dict]) -> List[Dict]:
        """Process and clean fight results data"""
        processed_results = []
        
        for result in raw_results:
            try:
                # Extract fighter names
                fighter1_name = result.get('fighter1', '').strip()
                fighter2_name = result.get('fighter2', '').strip()
                winner_name = result.get('winner', '').strip()
                
                if not fighter1_name or not fighter2_name:
                    continue
                
                # Determine winner
                winner = None
                if winner_name == fighter1_name:
                    winner = 'fighter1'
                elif winner_name == fighter2_name:
                    winner = 'fighter2'
                
                # Parse method and round
                method_info = self._parse_method(result.get('method', ''))
                
                # Create processed result
                processed_result = {
                    'id': self._generate_id(f"{fighter1_name} vs {fighter2_name}"),
                    'fighter1': fighter1_name,
                    'fighter2': fighter2_name,
                    'winner': winner,
                    'winner_name': winner_name if winner else None,
                    'weight_class': result.get('weight_class', 'Unknown').strip(),
                    'method': method_info.get('method', 'Unknown'),
                    'round': method_info.get('round', None),
                    'time': method_info.get('time', None),
                    'scraped_at': result.get('scraped_at')
                }
                
                processed_results.append(processed_result)
                
            except Exception as e:
                logger.error(f"Error processing fight result: {e}")
                continue
        
        return processed_results
    
    def _create_fighters_database(self, rankings: List[Dict], fights: List[Dict], results: List[Dict]) -> List[Dict]:
        """Create comprehensive fighters database"""
        fighters = {}
        
        # Add fighters from rankings
        for ranking in rankings:
            fighter_name = ranking['fighter_name']
            if fighter_name not in fighters:
                fighters[fighter_name] = {
                    'id': ranking['id'],
                    'name': fighter_name,
                    'record': ranking['record'],
                    'wins': ranking['wins'],
                    'losses': ranking['losses'],
                    'draws': ranking['draws'],
                    'rankings': [],
                    'fights': [],
                    'results': []
                }
            
            # Add ranking info
            fighters[fighter_name]['rankings'].append({
                'division': ranking['division'],
                'rank': ranking['rank'],
                'scraped_at': ranking['scraped_at']
            })
        
        # Add fighters from fights
        for fight in fights:
            for fighter_key in ['fighter1', 'fighter2']:
                fighter_name = fight[fighter_key]['name']
                if fighter_name not in fighters:
                    fighters[fighter_name] = {
                        'id': self._generate_id(fighter_name),
                        'name': fighter_name,
                        'record': fight[fighter_key]['record'],
                        'wins': fight[fighter_key]['wins'],
                        'losses': fight[fighter_key]['losses'],
                        'draws': fight[fighter_key]['draws'],
                        'rankings': [],
                        'fights': [],
                        'results': []
                    }
                
                # Add fight info
                fighters[fighter_name]['fights'].append({
                    'fight_id': fight['id'],
                    'opponent': fight['fighter2']['name'] if fighter_key == 'fighter1' else fight['fighter1']['name'],
                    'weight_class': fight['weight_class'],
                    'fight_type': fight['fight_type'],
                    'scraped_at': fight['scraped_at']
                })
        
        # Add fighters from results
        for result in results:
            for fighter_name in [result['fighter1'], result['fighter2']]:
                if fighter_name not in fighters:
                    fighters[fighter_name] = {
                        'id': self._generate_id(fighter_name),
                        'name': fighter_name,
                        'record': {'wins': 0, 'losses': 0, 'draws': 0},
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'rankings': [],
                        'fights': [],
                        'results': []
                    }
                
                # Add result info
                is_winner = result['winner_name'] == fighter_name
                fighters[fighter_name]['results'].append({
                    'result_id': result['id'],
                    'opponent': result['fighter2'] if result['fighter1'] == fighter_name else result['fighter1'],
                    'result': 'W' if is_winner else 'L',
                    'method': result['method'],
                    'round': result['round'],
                    'weight_class': result['weight_class'],
                    'scraped_at': result['scraped_at']
                })
        
        return list(fighters.values())
    
    def _parse_record(self, record_data):
        """Parse fighter record from various formats"""
        try:
            if isinstance(record_data, dict):
                # New format: {'wins': 0, 'losses': 0, 'draws': 0}
                return {
                    'wins': record_data.get('wins', 0),
                    'losses': record_data.get('losses', 0),
                    'draws': record_data.get('draws', 0)
                }
            elif isinstance(record_data, str):
                # Old format: "27-1-0"
                parts = record_data.split('-')
                return {
                    'wins': int(parts[0]) if len(parts) > 0 else 0,
                    'losses': int(parts[1]) if len(parts) > 1 else 0,
                    'draws': int(parts[2]) if len(parts) > 2 else 0
                }
            else:
                return {'wins': 0, 'losses': 0, 'draws': 0}
        except Exception as e:
            logger.error(f"Error parsing record '{record_data}': {e}")
            return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            if not date_str:
                return None
            
            # Try different date formats
            date_formats = [
                '%B %d, %Y',  # December 15, 2024
                '%b %d, %Y',  # Dec 15, 2024
                '%Y-%m-%d',   # 2024-12-15
                '%m/%d/%Y',   # 12/15/2024
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.isoformat()
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            return None
    
    def _parse_method(self, method_str: str) -> Dict:
        """Parse fight method and round information"""
        try:
            method_info = {
                'method': 'Unknown',
                'round': None,
                'time': None
            }
            
            if not method_str:
                return method_info
            
            # Common methods
            methods = ['KO/TKO', 'Submission', 'Decision', 'DQ', 'No Contest']
            for method in methods:
                if method.lower() in method_str.lower():
                    method_info['method'] = method
                    break
            
            # Extract round number
            round_match = re.search(r'Round (\d+)', method_str, re.IGNORECASE)
            if round_match:
                method_info['round'] = int(round_match.group(1))
            
            # Extract time
            time_match = re.search(r'(\d+):(\d+)', method_str)
            if time_match:
                minutes = int(time_match.group(1))
                seconds = int(time_match.group(2))
                method_info['time'] = f"{minutes:02d}:{seconds:02d}"
            
            return method_info
            
        except Exception as e:
            logger.error(f"Error parsing method '{method_str}': {e}")
            return {'method': 'Unknown', 'round': None, 'time': None}
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID from text"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()[:8]
    
    def save_processed_data(self, filepath: str):
        """Save processed data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.processed_data, f, indent=2)
            logger.info(f"Processed data saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
    
    def get_fighters_by_division(self, division: str) -> List[Dict]:
        """Get all fighters in a specific division"""
        if not self.processed_data:
            return []
        
        return [
            fighter for fighter in self.processed_data.get('fighters', [])
            if any(ranking['division'].lower() == division.lower() 
                   for ranking in fighter.get('rankings', []))
        ]
    
    def get_upcoming_fights_for_fighter(self, fighter_name: str) -> List[Dict]:
        """Get upcoming fights for a specific fighter"""
        if not self.processed_data:
            return []
        
        return [
            fight for fight in self.processed_data.get('upcoming_fights', [])
            if (fight['fighter1']['name'] == fighter_name or 
                fight['fighter2']['name'] == fighter_name)
        ]
    
    def get_fighter_stats(self, fighter_name: str) -> Optional[Dict]:
        """Get comprehensive stats for a fighter"""
        if not self.processed_data:
            return None
        
        for fighter in self.processed_data.get('fighters', []):
            if fighter['name'] == fighter_name:
                return fighter
        
        return None

def main():
    """Test the data processor"""
    processor = UFCDataProcessor()
    
    # Load sample data (you would load your scraped data here)
    try:
        with open('ufc_data.json', 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("No ufc_data.json found. Run the scraper first.")
        return
    
    # Process the data
    processed_data = processor.process_raw_data(raw_data)
    
    # Save processed data
    processor.save_processed_data('processed_ufc_data.json')
    
    # Print some stats
    print(f"Processed {len(processed_data.get('fighters', []))} fighters")
    print(f"Processed {len(processed_data.get('upcoming_fights', []))} upcoming fights")
    print(f"Processed {len(processed_data.get('rankings', []))} rankings")

if __name__ == "__main__":
    main() 