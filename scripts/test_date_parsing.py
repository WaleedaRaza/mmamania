#!/usr/bin/env python3
"""
Test Date Parsing
Test the date parsing with the actual format from Wikipedia
"""

from datetime import datetime

def test_date_parsing():
    """Test date parsing with actual Wikipedia formats"""
    
    # Test dates from Wikipedia
    test_dates = [
        "Aug 2, 2025",
        "Jul 26, 2025", 
        "Jul 19, 2025",
        "Jul 12, 2025",
        "Jun 28, 2025",
        "2024-04-13",
        "March 9, 2024",
        "February 17, 2024"
    ]
    
    print("🧪 TESTING DATE PARSING")
    print("=" * 40)
    
    for date_str in test_dates:
        parsed = parse_date(date_str)
        print(f"'{date_str}' -> {parsed}")

def parse_date(date_str: str):
    """Parse date string into ISO format"""
    if not date_str:
        return None
    
    # Try different date formats
    date_formats = [
        '%Y-%m-%d',
        '%B %d, %Y',
        '%B %d %Y',
        '%b %d, %Y',  # Aug 2, 2025
        '%b %d %Y',
        '%m/%d/%Y',
        '%m-%d-%Y'
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.isoformat()
        except ValueError:
            continue
    
    return None

if __name__ == "__main__":
    test_date_parsing() 