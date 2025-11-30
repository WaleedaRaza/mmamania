from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ScraperSource:
    name: str
    url: str
    platform: str
    content_type: str  # 'official', 'media', 'analyst', 'podcast', 'journalist'
    priority: int  # 1-5, higher = more important

class ScraperConfig:
    """Comprehensive MMA content scraping configuration"""
    
    # YouTube Search Terms
    YOUTUBE_SEARCH_TERMS = [
        # Event-specific
        "UFC {event}", "UFC {event} Embedded", "UFC {event} Countdown",
        "UFC {event} press conference", "UFC {event} weigh in",
        "UFC {event} ceremonial weigh in", "UFC {event} face off",
        "UFC {event} staredown", "UFC {event} media day",
        "UFC {event} post fight press conference",
        
        # Fighter-specific
        "{fighter} highlights", "{fighter} knockout", "{fighter} submission",
        "{fighter} vs {fighter} full fight highlights", "{fighter} interview",
        "{fighter} media day", "{fighter} post fight", "{fighter} camp vlog",
        "{fighter} breakdown", "{fighter} analysis",
        
        # General MMA
        "mma breakdown", "mma film study", "mma technique", "mma controversy",
        "mma news today", "mma podcast clips", "pfl highlights", 
        "one championship highlights", "bellator highlights",
        "cage warriors highlights", "rizin highlights", "lfa highlights"
    ]
    
    # TikTok Search Terms  
    TIKTOK_SEARCH_TERMS = [
        "#ufc", "#mma", "#ufcfightnight", "#ufc{event}",
        "#staredown", "#faceoff", "#weighin", "#pressconference",
        "#knockout", "#ko", "#submission", "#highlight", "#octagon", "#bjj",
        "{fighter} interview", "{fighter} highlights", "ufc face off",
        "ufc staredown", "ufc media day", "ufc weigh in", "mma knockout",
        "mma compilation", "ufc meme", "mma drama"
    ]
    
    # Twitter Search Terms
    TWITTER_SEARCH_TERMS = [
        "UFC {event} filter:media", "UFC {event} filter:videos",
        "UFC {event} press conference filter:media",
        "UFC {event} weigh in filter:media", "UFC {event} face off filter:videos",
        "UFC {event} staredown filter:videos", "{fighter} min_faves:100 filter:media",
        "{fighter} interview filter:media", "mma news OR ufc news min_faves:100",
        "media day filter:media since:{date}", 
        "post fight press conference filter:media",
        "breaking ufc OR breaking mma"
    ]
    
    # High-Priority YouTube Channels
    YOUTUBE_SOURCES = [
        ScraperSource("UFC Official", "https://www.youtube.com/@UFC", "youtube", "official", 5),
        ScraperSource("ESPN MMA", "https://www.youtube.com/@ESPnmma", "youtube", "media", 5),
        ScraperSource("MMA Fighting", "https://www.youtube.com/@MMAFightingonSBN", "youtube", "media", 4),
        ScraperSource("MMA Junkie", "https://www.youtube.com/@MMAJunkieVideo", "youtube", "media", 4),
        ScraperSource("The MMA Hour", "https://www.youtube.com/@MMAHour", "youtube", "podcast", 4),
        ScraperSource("Morning Kombat", "https://www.youtube.com/@MorningKombat", "youtube", "podcast", 4),
        ScraperSource("MMA Guru", "https://www.youtube.com/@the-mma-guru", "youtube", "analyst", 3),
        ScraperSource("The Weasle", "https://www.youtube.com/channel/UCZD2qRU8J82XGdGdUWYneNQ", "youtube", "analyst", 3),
        ScraperSource("MMA On Point", "https://www.youtube.com/mmaonpoint", "youtube", "analyst", 3),
        ScraperSource("Mixed Molly Whoppery", "https://www.youtube.com/@MollyWhopMMA", "youtube", "analyst", 3),
        ScraperSource("Chael Sonnen", "https://www.youtube.com/@ChaelSonnen", "youtube", "analyst", 3),
        ScraperSource("Lawrence Kenshin", "https://www.youtube.com/@LawrenceKenshin", "youtube", "analyst", 3),
        ScraperSource("BJJ Scout", "https://www.youtube.com/@BJJSCOUT", "youtube", "analyst", 3),
        ScraperSource("MMA Shredded", "https://www.youtube.com/@MMAShredded", "youtube", "analyst", 3),
        # Add all other promotion channels
        ScraperSource("PFL", "https://www.youtube.com/@PFLMMA", "youtube", "official", 3),
        ScraperSource("ONE Championship", "https://www.youtube.com/@ONEChampionship", "youtube", "official", 3),
        ScraperSource("Bellator MMA", "https://www.youtube.com/@BellatorMMA", "youtube", "official", 3),
        ScraperSource("Cage Warriors", "https://www.youtube.com/@CageWarriors", "youtube", "official", 3),
        ScraperSource("KSW", "https://www.youtube.com/@KSW", "youtube", "official", 3),
        ScraperSource("RIZIN FF", "https://www.youtube.com/@RIZINFightingFederation", "youtube", "official", 3),
        ScraperSource("LFA", "https://www.youtube.com/@LFAfighting", "youtube", "official", 3),
        ScraperSource("Invicta FC", "https://www.youtube.com/@InvictaFC", "youtube", "official", 3),
        ScraperSource("BRAVE CF", "https://www.youtube.com/@BraveCFTV", "youtube", "official", 3),
    ]
    
    # High-Signal Twitter Accounts
    TWITTER_SOURCES = [
        ScraperSource("UFC Official", "https://twitter.com/ufc", "twitter", "official", 5),
        ScraperSource("Ariel Helwani", "https://twitter.com/arielhelwani", "twitter", "journalist", 5),
        ScraperSource("Brett Okamoto", "https://twitter.com/bokamotoESPN", "twitter", "journalist", 5),
        ScraperSource("ESPN MMA", "https://twitter.com/espnmma", "twitter", "media", 5),
        ScraperSource("MMA Fighting", "https://twitter.com/MMAFighting", "twitter", "media", 4),
        ScraperSource("MMA Junkie", "https://twitter.com/MMAJunkie", "twitter", "media", 4),
        ScraperSource("Marc Raimondi", "https://twitter.com/marc_raimondi", "twitter", "journalist", 4),
        ScraperSource("Mike Bohn", "https://twitter.com/MikeBohn", "twitter", "journalist", 4),
        ScraperSource("Damon Martin", "https://twitter.com/DamonMartin", "twitter", "journalist", 4),
        ScraperSource("Chael Sonnen", "https://twitter.com/ChaelSonnen", "twitter", "analyst", 3),
        ScraperSource("Dana White", "https://twitter.com/danawhite", "twitter", "official", 5),
        ScraperSource("Shaheen Al-Shatti", "https://twitter.com/shahanshah", "twitter", "journalist", 4),
        ScraperSource("Guilherme Cruz", "https://twitter.com/gcMMA", "twitter", "journalist", 4),
        ScraperSource("John Morgan", "https://twitter.com/MMAjunkieJohn", "twitter", "journalist", 4),
    ]
    
    # TikTok Sources
    TIKTOK_SOURCES = [
        ScraperSource("UFC Official", "https://www.tiktok.com/@ufc", "tiktok", "official", 5),
        ScraperSource("ESPN MMA", "https://www.tiktok.com/@espnmma", "tiktok", "media", 5),
        ScraperSource("MMA Fighting", "https://www.tiktok.com/@mmafighting", "tiktok", "media", 4),
        ScraperSource("Nina-Marie Daniele", "https://www.tiktok.com/@ninamariedaniele", "tiktok", "journalist", 4),
        ScraperSource("The Schmo", "https://www.tiktok.com/@theschmo312", "tiktok", "journalist", 3),
        ScraperSource("Sean O'Malley", "https://www.tiktok.com/@sugasean", "tiktok", "fighter", 3),
        ScraperSource("Israel Adesanya", "https://www.tiktok.com/@stylebender", "tiktok", "fighter", 3),
        ScraperSource("Paddy Pimblett", "https://www.tiktok.com/@theufcbaddy", "tiktok", "fighter", 3),
        ScraperSource("Alexander Volkanovski", "https://www.tiktok.com/@alexvolkanovski", "tiktok", "fighter", 3),
    ]
    
    # Content Classification Keywords
    CONTENT_CATEGORIES = {
        'highlights': ['highlight', 'knockout', 'ko', 'submission', 'finish', 'best moments'],
        'interview': ['interview', 'sits down', 'talks about', 'speaks on', 'media day'],
        'analysis': ['breakdown', 'analysis', 'technique', 'film study', 'preview'],
        'news': ['breaking', 'news', 'announcement', 'confirms', 'reports'],
        'event': ['press conference', 'weigh in', 'face off', 'staredown', 'embedded', 'countdown'],
        'podcast': ['podcast', 'show', 'episode', 'discusses']
    }
    
    # Fighter Name Variations for Better Matching
    FIGHTER_ALIASES = {
        'Jon Jones': ['Jon Jones', 'Jonathan Jones', 'Bones Jones'],
        'Conor McGregor': ['Conor McGregor', 'The Notorious', 'Mystic Mac'],
        'Israel Adesanya': ['Israel Adesanya', 'Izzy', 'The Last Stylebender'],
        'Sean O\'Malley': ['Sean O\'Malley', 'Sugar Sean', 'Suga Show'],
        'Daniel Cormier': ['Daniel Cormier', 'DC', 'Double Champ'],
        'Khabib Nurmagomedov': ['Khabib Nurmagomedov', 'The Eagle', 'Khabib'],
        'Kamaru Usman': ['Kamaru Usman', 'The Nigerian Nightmare'],
        'Alexander Volkanovski': ['Alexander Volkanovski', 'Volk', 'The Great'],
        'Charles Oliveira': ['Charles Oliveira', 'Do Bronx'],
        'Dustin Poirier': ['Dustin Poirier', 'The Diamond'],
        'Justin Gaethje': ['Justin Gaethje', 'The Highlight'],
        'Max Holloway': ['Max Holloway', 'Blessed'],
        'Amanda Nunes': ['Amanda Nunes', 'The Lioness'],
        'Valentina Shevchenko': ['Valentina Shevchenko', 'Bullet'],
        'Rose Namajunas': ['Rose Namajunas', 'Thug Rose'],
    }

# Global instance
scraper_config = ScraperConfig()
