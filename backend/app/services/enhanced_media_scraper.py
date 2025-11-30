import asyncio
import aiohttp
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus, urljoin
from ..config.scraper_config import scraper_config, ScraperSource

class EnhancedMediaScraper:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.rate_limit_delay = {
            'youtube': 2,  # seconds between requests
            'twitter': 3,
            'tiktok': 4
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_all_platforms(self, 
                                 event_name: Optional[str] = None,
                                 fighter_names: Optional[List[str]] = None,
                                 max_per_platform: int = 30) -> Dict[str, Any]:
        """Scrape content from all platforms with context-aware search terms"""
        
        # Generate dynamic search terms
        search_terms = self._generate_search_terms(event_name, fighter_names)
        
        try:
            # Run all platform scrapers concurrently
            youtube_task = self._scrape_youtube_comprehensive(search_terms['youtube'], max_per_platform)
            twitter_task = self._scrape_twitter_comprehensive(search_terms['twitter'], max_per_platform)
            tiktok_task = self._scrape_tiktok_comprehensive(search_terms['tiktok'], max_per_platform)
            
            results = await asyncio.gather(
                youtube_task, twitter_task, tiktok_task, 
                return_exceptions=True
            )
            
            youtube_content, twitter_content, tiktok_content = results
            
            # Handle exceptions gracefully
            if isinstance(youtube_content, Exception):
                print(f"YouTube scraping failed: {youtube_content}")
                youtube_content = []
            
            if isinstance(twitter_content, Exception):
                print(f"Twitter scraping failed: {twitter_content}")
                twitter_content = []
                
            if isinstance(tiktok_content, Exception):
                print(f"TikTok scraping failed: {tiktok_content}")
                tiktok_content = []
            
            # Combine and rank content
            all_content = []
            all_content.extend(youtube_content)
            all_content.extend(twitter_content)
            all_content.extend(tiktok_content)
            
            # Apply intelligent ranking
            ranked_content = self._rank_content_by_relevance(all_content, event_name, fighter_names)
            
            return {
                'total_content': len(all_content),
                'youtube_count': len(youtube_content),
                'twitter_count': len(twitter_content),
                'tiktok_count': len(tiktok_content),
                'content': ranked_content[:50],  # Top 50 pieces
                'search_context': {
                    'event_name': event_name,
                    'fighter_names': fighter_names,
                    'search_terms_used': len(search_terms['youtube'] + search_terms['twitter'] + search_terms['tiktok'])
                },
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in comprehensive scraping: {e}")
            return {'content': [], 'error': str(e)}
    
    def _generate_search_terms(self, event_name: Optional[str], fighter_names: Optional[List[str]]) -> Dict[str, List[str]]:
        """Generate dynamic search terms based on context"""
        
        youtube_terms = []
        twitter_terms = []
        tiktok_terms = []
        
        # Add base terms
        youtube_terms.extend(scraper_config.YOUTUBE_SEARCH_TERMS[:10])  # General terms
        twitter_terms.extend(scraper_config.TWITTER_SEARCH_TERMS[:8])
        tiktok_terms.extend(scraper_config.TIKTOK_SEARCH_TERMS[:12])
        
        # Add event-specific terms
        if event_name:
            event_youtube = [term.format(event=event_name) for term in scraper_config.YOUTUBE_SEARCH_TERMS if '{event}' in term]
            event_twitter = [term.format(event=event_name, date=datetime.now().strftime('%Y-%m-%d')) for term in scraper_config.TWITTER_SEARCH_TERMS if '{event}' in term]
            event_tiktok = [term.format(event=event_name.replace(' ', '')) for term in scraper_config.TIKTOK_SEARCH_TERMS if '{event}' in term]
            
            youtube_terms.extend(event_youtube[:8])
            twitter_terms.extend(event_twitter[:6])
            tiktok_terms.extend(event_tiktok[:8])
        
        # Add fighter-specific terms
        if fighter_names:
            for fighter in fighter_names[:3]:  # Limit to top 3 fighters
                # Get fighter aliases for better matching
                aliases = scraper_config.FIGHTER_ALIASES.get(fighter, [fighter])
                main_name = aliases[0]
                
                fighter_youtube = [term.format(fighter=main_name) for term in scraper_config.YOUTUBE_SEARCH_TERMS if '{fighter}' in term]
                fighter_twitter = [term.format(fighter=main_name) for term in scraper_config.TWITTER_SEARCH_TERMS if '{fighter}' in term]
                fighter_tiktok = [term.format(fighter=main_name) for term in scraper_config.TIKTOK_SEARCH_TERMS if '{fighter}' in term]
                
                youtube_terms.extend(fighter_youtube[:5])
                twitter_terms.extend(fighter_twitter[:4])
                tiktok_terms.extend(fighter_tiktok[:5])
        
        return {
            'youtube': list(set(youtube_terms)),  # Remove duplicates
            'twitter': list(set(twitter_terms)),
            'tiktok': list(set(tiktok_terms))
        }
    
    async def _scrape_youtube_comprehensive(self, search_terms: List[str], max_results: int) -> List[Dict]:
        """Enhanced YouTube scraping with channel monitoring"""
        all_videos = []
        
        # 1. Search-based scraping
        for term in search_terms[:10]:  # Limit search terms
            try:
                videos = await self._scrape_youtube_search(term, max_results // len(search_terms))
                all_videos.extend(videos)
                await asyncio.sleep(self.rate_limit_delay['youtube'])
            except Exception as e:
                print(f"Error scraping YouTube search '{term}': {e}")
        
        # 2. High-priority channel monitoring
        priority_channels = [src for src in scraper_config.YOUTUBE_SOURCES if src.priority >= 4]
        for channel_source in priority_channels[:5]:  # Monitor top 5 channels
            try:
                channel_videos = await self._scrape_youtube_channel_recent(channel_source)
                all_videos.extend(channel_videos)
                await asyncio.sleep(self.rate_limit_delay['youtube'])
            except Exception as e:
                print(f"Error scraping YouTube channel {channel_source.name}: {e}")
        
        # Remove duplicates and apply quality filters
        unique_videos = {v['platform_id']: v for v in all_videos if self._is_high_quality_youtube(v)}.values()
        return sorted(list(unique_videos), key=lambda x: x['relevance_score'], reverse=True)[:max_results]
    
    async def _scrape_youtube_search(self, search_term: str, limit: int = 8) -> List[Dict]:
        """Scrape YouTube search results with enhanced parsing"""
        encoded_term = quote_plus(f"{search_term} -live -stream")
        url = f"https://www.youtube.com/results?search_query={encoded_term}&sp=CAISBAgBEAE%253D"
        
        async with self.session.get(url) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find script with video data
            script_pattern = re.compile(r'var ytInitialData = ({.+?});')
            video_data = None
            
            for script in soup.find_all('script'):
                if script.string:
                    match = script_pattern.search(script.string)
                    if match:
                        try:
                            video_data = json.loads(match.group(1))
                            break
                        except json.JSONDecodeError:
                            continue
            
            if not video_data:
                return []
            
            return self._extract_youtube_videos_from_data(video_data, limit)
    
    async def _scrape_youtube_channel_recent(self, channel_source: ScraperSource, limit: int = 5) -> List[Dict]:
        """Scrape recent videos from specific YouTube channel"""
        # Extract channel ID or username from URL
        channel_id = channel_source.url.split('/')[-1]
        
        # Try different URL formats
        urls_to_try = [
            f"https://www.youtube.com/{channel_id}/videos",
            f"https://www.youtube.com/c/{channel_id}/videos",
            f"https://www.youtube.com/channel/{channel_id}/videos"
        ]
        
        for url in urls_to_try:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract recent videos
                        videos = self._extract_channel_videos(soup, channel_source, limit)
                        if videos:
                            return videos
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                continue
        
        return []
    
    def _extract_youtube_videos_from_data(self, video_data: Dict, limit: int) -> List[Dict]:
        """Extract video information from YouTube's data structure"""
        videos = []
        
        try:
            contents = video_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
            
            for section in contents:
                if 'itemSectionRenderer' in section:
                    items = section['itemSectionRenderer']['contents']
                    
                    for item in items:
                        if 'videoRenderer' in item and len(videos) < limit:
                            video_info = self._parse_youtube_video_renderer(item['videoRenderer'])
                            if video_info and self._is_mma_relevant(video_info):
                                videos.append(video_info)
                                
        except Exception as e:
            print(f"Error parsing YouTube data structure: {e}")
        
        return videos
    
    def _extract_channel_videos(self, soup: BeautifulSoup, channel_source: ScraperSource, limit: int) -> List[Dict]:
        """Extract videos from channel page"""
        videos = []
        
        # Look for video containers
        video_containers = soup.find_all('div', {'id': re.compile(r'content.*')})
        
        for container in video_containers[:limit]:
            try:
                # Extract video info from container
                video_info = self._parse_channel_video_container(container, channel_source)
                if video_info and self._is_mma_relevant(video_info):
                    videos.append(video_info)
            except Exception as e:
                print(f"Error parsing channel video container: {e}")
        
        return videos
    
    def _parse_channel_video_container(self, container, channel_source: ScraperSource) -> Optional[Dict]:
        """Parse individual video from channel page"""
        try:
            # Extract video ID from link
            link = container.find('a', href=re.compile(r'/watch\?v='))
            if not link:
                return None
            
            video_id = link['href'].split('v=')[1].split('&')[0]
            
            # Extract title
            title_elem = container.find('a', {'title': True})
            title = title_elem['title'] if title_elem else ''
            
            # Extract thumbnail
            img = container.find('img')
            thumbnail_url = img['src'] if img else ''
            
            # Extract view count and duration
            view_count = 0
            duration_seconds = 0
            
            # Create basic video info
            return {
                'platform': 'youtube',
                'platform_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'title': title,
                'description': title,
                'thumbnail_url': thumbnail_url,
                'author_name': channel_source.name,
                'published_at': datetime.now().isoformat(),  # Approximate
                'view_count': view_count,
                'duration_seconds': duration_seconds,
                'content_type': self._classify_content_type(title),
                'relevance_score': self._calculate_youtube_relevance(title, channel_source.name),
                'source_priority': channel_source.priority
            }
            
        except Exception as e:
            print(f"Error parsing channel video container: {e}")
            return None
    
    def _parse_youtube_video_renderer(self, renderer: Dict) -> Optional[Dict]:
        """Parse individual YouTube video from renderer data"""
        try:
            video_id = renderer.get('videoId', '')
            if not video_id:
                return None
            
            # Extract title
            title_runs = renderer.get('title', {}).get('runs', [])
            title = title_runs[0]['text'] if title_runs else ''
            
            # Extract channel name
            owner_text = renderer.get('ownerText', {}).get('runs', [])
            channel_name = owner_text[0]['text'] if owner_text else ''
            
            # Extract thumbnail
            thumbnail_url = ''
            thumbnails = renderer.get('thumbnail', {}).get('thumbnails', [])
            if thumbnails:
                thumbnail_url = thumbnails[-1].get('url', '')
            
            # Extract view count
            view_count = 0
            view_text = renderer.get('viewCountText', {}).get('simpleText', '')
            if view_text:
                view_count = self._parse_view_count(view_text)
            
            # Extract duration
            duration_seconds = 0
            length_text = renderer.get('lengthText', {}).get('simpleText', '')
            if length_text:
                duration_seconds = self._parse_duration(length_text)
            
            # Extract published time
            published_text = renderer.get('publishedTimeText', {}).get('simpleText', '')
            published_at = self._parse_published_time(published_text)
            
            return {
                'platform': 'youtube',
                'platform_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'title': title,
                'description': title,  # Search doesn't provide full description
                'thumbnail_url': thumbnail_url,
                'author_name': channel_name,
                'published_at': published_at.isoformat(),
                'view_count': view_count,
                'duration_seconds': duration_seconds,
                'content_type': self._classify_content_type(title),
                'relevance_score': self._calculate_youtube_relevance(title, channel_name),
                'source_priority': self._get_source_priority(channel_name, 'youtube')
            }
            
        except Exception as e:
            print(f"Error parsing YouTube video renderer: {e}")
            return None
    
    async def _scrape_twitter_comprehensive(self, search_terms: List[str], max_results: int) -> List[Dict]:
        """Enhanced Twitter scraping using nitter.net"""
        all_tweets = []
        
        # Use nitter.net as Twitter proxy
        for term in search_terms[:8]:  # Limit search terms
            try:
                tweets = await self._scrape_nitter_search(term, max_results // len(search_terms))
                all_tweets.extend(tweets)
                await asyncio.sleep(self.rate_limit_delay['twitter'])
            except Exception as e:
                print(f"Error scraping Twitter search '{term}': {e}")
        
        # Remove duplicates and apply quality filters
        unique_tweets = {t['platform_id']: t for t in all_tweets if self._is_high_quality_twitter(t)}.values()
        return sorted(list(unique_tweets), key=lambda x: x['relevance_score'], reverse=True)[:max_results]
    
    async def _scrape_nitter_search(self, search_term: str, limit: int = 8) -> List[Dict]:
        """Scrape Twitter via nitter.net"""
        encoded_term = quote_plus(search_term)
        url = f"https://nitter.net/search?f=tweets&q={encoded_term}&since=&until=&near="
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return []
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                tweets = []
                tweet_containers = soup.find_all('div', class_='timeline-item')
                
                for container in tweet_containers[:limit]:
                    try:
                        tweet_info = self._extract_tweet_info(container)
                        if tweet_info and self._is_mma_relevant(tweet_info):
                            tweets.append(tweet_info)
                    except Exception as e:
                        print(f"Error parsing tweet: {e}")
                
                return tweets
                
        except Exception as e:
            print(f"Error scraping nitter: {e}")
            return []
    
    def _extract_tweet_info(self, tweet_container) -> Optional[Dict]:
        """Extract tweet information from nitter HTML"""
        try:
            # Get username and handle
            username_elem = tweet_container.find('a', class_='username')
            if not username_elem:
                return None
                
            username = username_elem.text.strip()
            profile_link = username_elem.get('href', '')
            
            # Get tweet text
            tweet_content = tweet_container.find('div', class_='tweet-content')
            if not tweet_content:
                return None
                
            tweet_text = tweet_content.get_text(strip=True)
            
            # Get engagement metrics
            stats = tweet_container.find('div', class_='tweet-stats')
            likes = 0
            retweets = 0
            replies = 0
            
            if stats:
                like_elem = stats.find('span', class_='tweet-stat')
                if like_elem:
                    likes = self._parse_stat_number(like_elem.text)
            
            # Get timestamp
            time_elem = tweet_container.find('span', class_='tweet-date')
            published_at = datetime.now()
            if time_elem:
                published_at = self._parse_tweet_time(time_elem.get('title', ''))
            
            # Get images/media
            media_url = None
            media_container = tweet_container.find('div', class_='attachments')
            if media_container:
                img = media_container.find('img')
                if img:
                    media_url = f"https://nitter.net{img.get('src', '')}"
            
            # Create tweet ID from content hash
            tweet_id = abs(hash(f"{username}{tweet_text[:50]}")) % (10**10)
            
            return {
                'platform': 'twitter',
                'platform_id': str(tweet_id),
                'url': f"https://twitter.com{profile_link}",
                'title': tweet_text[:100] + '...' if len(tweet_text) > 100 else tweet_text,
                'description': tweet_text,
                'thumbnail_url': media_url,
                'author_name': username.replace('@', ''),
                'author_handle': username,
                'published_at': published_at.isoformat(),
                'like_count': likes,
                'share_count': retweets,
                'comment_count': replies,
                'content_type': 'social_post',
                'relevance_score': self._calculate_tweet_relevance(tweet_text, username),
                'source_priority': self._get_source_priority(username, 'twitter')
            }
            
        except Exception as e:
            print(f"Error extracting tweet info: {e}")
            return None
    
    async def _scrape_tiktok_comprehensive(self, search_terms: List[str], max_results: int) -> List[Dict]:
        """Enhanced TikTok scraping"""
        all_videos = []
        
        for term in search_terms[:6]:  # Limit search terms
            try:
                videos = await self._scrape_tiktok_search(term, max_results // len(search_terms))
                all_videos.extend(videos)
                await asyncio.sleep(self.rate_limit_delay['tiktok'])
            except Exception as e:
                print(f"Error scraping TikTok search '{term}': {e}")
        
        # Remove duplicates and apply quality filters
        unique_videos = {v['platform_id']: v for v in all_videos if self._is_high_quality_tiktok(v)}.values()
        return sorted(list(unique_videos), key=lambda x: x['relevance_score'], reverse=True)[:max_results]
    
    async def _scrape_tiktok_search(self, search_term: str, limit: int = 8) -> List[Dict]:
        """Scrape TikTok search results"""
        # For now, return mock data since TikTok scraping is complex
        # In production, you'd implement actual TikTok scraping
        return []
    
    def _classify_content_type(self, title: str) -> str:
        """Classify content based on title keywords"""
        title_lower = title.lower()
        
        for category, keywords in scraper_config.CONTENT_CATEGORIES.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _calculate_youtube_relevance(self, title: str, channel: str) -> int:
        """Calculate relevance score for YouTube content"""
        score = 0
        text = f"{title} {channel}".lower()
        
        # High-value keywords
        if 'ufc' in text: score += 50
        if 'knockout' in text or 'ko' in text: score += 30
        if 'highlights' in text: score += 25
        if 'interview' in text: score += 20
        if 'breakdown' in text or 'analysis' in text: score += 20
        if 'press conference' in text or 'weigh in' in text: score += 25
        
        # Channel authority bonus
        source_priority = self._get_source_priority(channel, 'youtube')
        score += source_priority * 10
        
        return min(score, 100)
    
    def _calculate_tweet_relevance(self, text: str, username: str) -> int:
        """Calculate relevance score for tweet"""
        score = 0
        content = f"{text} {username}".lower()
        
        # High value keywords
        if 'ufc' in content: score += 40
        if 'knockout' in content or 'ko' in content: score += 30
        if 'fight' in content: score += 20
        if 'mma' in content: score += 15
        
        # Verified accounts or official UFC accounts
        if 'ufc' in username.lower(): score += 35
        if 'dana' in username.lower(): score += 25
        
        return min(score, 100)
    
    def _get_source_priority(self, source_name: str, platform: str) -> int:
        """Get priority score for a source"""
        sources = {
            'youtube': scraper_config.YOUTUBE_SOURCES,
            'twitter': scraper_config.TWITTER_SOURCES,
            'tiktok': scraper_config.TIKTOK_SOURCES
        }.get(platform, [])
        
        for source in sources:
            if source.name.lower() in source_name.lower():
                return source.priority
        
        return 1  # Default priority
    
    def _is_mma_relevant(self, content: Dict) -> bool:
        """Check if content is MMA/UFC relevant"""
        text_to_check = f"{content.get('title', '')} {content.get('author_name', '')}".lower()
        
        mma_keywords = [
            'ufc', 'mma', 'mixed martial arts', 'fight', 'fighter', 'knockout', 'ko',
            'submission', 'octagon', 'championship', 'title fight', 'main event',
            'weigh in', 'press conference', 'face off', 'staredown'
        ]
        
        return any(keyword in text_to_check for keyword in mma_keywords)
    
    def _is_high_quality_youtube(self, video: Dict) -> bool:
        """Filter for high-quality YouTube content"""
        # Minimum view threshold
        if video.get('view_count', 0) < 1000:
            return False
        
        # Duration filters (avoid very short or very long videos)
        duration = video.get('duration_seconds', 0)
        if duration > 0 and (duration < 30 or duration > 3600):  # 30s to 1 hour
            return False
        
        # Title quality check
        title = video.get('title', '').lower()
        spam_indicators = ['clickbait', 'reaction', 'live stream', 'compilation']
        if any(indicator in title for indicator in spam_indicators):
            return False
        
        return True
    
    def _is_high_quality_twitter(self, tweet: Dict) -> bool:
        """Filter for high-quality Twitter content"""
        # Minimum engagement threshold
        if tweet.get('like_count', 0) < 10:
            return False
        
        # Content length check
        description = tweet.get('description', '')
        if len(description) < 10:
            return False
        
        return True
    
    def _is_high_quality_tiktok(self, video: Dict) -> bool:
        """Filter for high-quality TikTok content"""
        # For now, accept all TikTok content
        return True
    
    def _rank_content_by_relevance(self, content: List[Dict], event_name: Optional[str], fighter_names: Optional[List[str]]) -> List[Dict]:
        """Intelligent content ranking based on context"""
        
        def calculate_contextual_score(item: Dict) -> float:
            base_score = item.get('relevance_score', 0)
            
            # Boost for event-specific content
            if event_name:
                text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                if event_name.lower() in text:
                    base_score += 30
            
            # Boost for fighter-specific content
            if fighter_names:
                text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                for fighter in fighter_names:
                    if fighter.lower() in text:
                        base_score += 20
                        break
            
            # Platform-specific adjustments
            platform = item.get('platform', '')
            if platform == 'youtube':
                base_score += item.get('view_count', 0) / 10000  # View count bonus
            elif platform == 'twitter':
                base_score += item.get('like_count', 0) / 100   # Like count bonus
            elif platform == 'tiktok':
                base_score += item.get('view_count', 0) / 50000  # View count bonus
            
            # Recency bonus
            published_at = datetime.fromisoformat(item.get('published_at', '').replace('Z', '+00:00'))
            hours_ago = (datetime.now() - published_at.replace(tzinfo=None)).total_seconds() / 3600
            if hours_ago < 24:
                base_score += 20
            elif hours_ago < 72:
                base_score += 10
            
            # Source priority bonus
            base_score += item.get('source_priority', 1) * 5
            
            return base_score
        
        # Calculate contextual scores and sort
        for item in content:
            item['contextual_score'] = calculate_contextual_score(item)
        
        return sorted(content, key=lambda x: x['contextual_score'], reverse=True)
    
    # Helper methods for parsing
    def _parse_view_count(self, view_text: str) -> int:
        """Parse view count from text like '1.2M views'"""
        if not view_text:
            return 0
        
        match = re.search(r'([\d.]+)\s*([KMB]?)', view_text)
        if match:
            number = float(match.group(1))
            unit = match.group(2).upper()
            
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            return int(number * multipliers.get(unit, 1))
        return 0
    
    def _parse_duration(self, duration_text: str) -> int:
        """Parse duration from text like '5:32'"""
        if ':' not in duration_text:
            return 0
        
        parts = duration_text.split(':')
        try:
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except ValueError:
            pass
        return 0
    
    def _parse_published_time(self, published_text: str) -> datetime:
        """Parse published time from relative text"""
        if not published_text:
            return datetime.now()
        
        now = datetime.now()
        text = published_text.lower()
        
        time_patterns = [
            (r'(\d+)\s*hour', lambda x: now - timedelta(hours=int(x))),
            (r'(\d+)\s*day', lambda x: now - timedelta(days=int(x))),
            (r'(\d+)\s*week', lambda x: now - timedelta(weeks=int(x))),
            (r'(\d+)\s*month', lambda x: now - timedelta(days=int(x) * 30)),
        ]
        
        for pattern, calculator in time_patterns:
            match = re.search(pattern, text)
            if match:
                return calculator(match.group(1))
        
        return now
    
    def _parse_stat_number(self, stat_text: str) -> int:
        """Parse engagement numbers like '1.2K' to integers"""
        if not stat_text:
            return 0
        
        match = re.search(r'([\d.]+)\s*([KM]?)', stat_text)
        if match:
            number = float(match.group(1))
            unit = match.group(2).upper()
            
            if unit == 'K':
                return int(number * 1000)
            elif unit == 'M':
                return int(number * 1000000)
            else:
                return int(number)
        return 0
    
    def _parse_tweet_time(self, time_str: str) -> datetime:
        """Parse tweet timestamp"""
        try:
            return datetime.strptime(time_str, '%b %d, %Y · %I:%M %p UTC')
        except:
            return datetime.now()
