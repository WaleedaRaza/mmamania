# UFC Data Pipeline


## Overview
This is a unified UFC data pipeline that dynamically scrapes real-time rankings and champions from UFC.com and populates a Supabase database for the Flutter app.

## Architecture

### Files
- **`scrapers/ufc/unified_ufc_scraper.py`** - Dynamic UFC scraper that reads real champions and rankings
- **`scripts/unified_production_pipeline.py`** - Production pipeline that scrapes and uploads data
- **`scripts/clear_database.py`** - Utility to clear database (for testing)
- **`scripts/debug_database.py`** - Utility to debug database contents

### How it works
1. **Dynamic Scraping**: The unified scraper reads UFC.com and dynamically detects champions and rankings
2. **Real-time Data**: No hardcoded champions - everything is scraped live from UFC.com
3. **Database Population**: Rankings are uploaded to Supabase with proper structure
4. **Flutter Integration**: The Flutter app displays champions and rankings in correct order

## Usage

### Run the pipeline
```bash
python3 scripts/unified_production_pipeline.py
```

### Clear database (for testing)
```bash
python3 scripts/clear_database.py
```

### Debug database contents
```bash
python3 scripts/debug_database.py
```

## Data Structure

### Rankings Table
- `fighter_id` - Reference to fighter
- `weight_class` - Division name
- `rank_position` - 0 for champion, 1+ for contenders
- `rank_type` - 'ufc'

### Champions
- Champions are stored with `rank_position: 0`
- Displayed as "C" in the Flutter app
- Automatically detected from UFC.com

### Contenders
- Contenders are stored with `rank_position: 1, 2, 3, ...`
- Displayed as "#1, #2, #3, ..." in the Flutter app
- Ordered correctly in the database

## Flutter App Integration

The Flutter app uses:
- `RankingItem` model to handle both fighter data and ranking info
- Proper ordering (champions first, then contenders)
- Correct display of champions vs contenders

## Key Features

✅ **Dynamic Champion Detection** - No hardcoded data  
✅ **Real-time Rankings** - Always current from UFC.com  
✅ **Clean Architecture** - One scraper, one pipeline  
✅ **Proper Ordering** - Champions at top, contenders below  
✅ **Error Handling** - Robust error handling and logging  
✅ **Database Integration** - Seamless Supabase integration  

## Troubleshooting

If champions aren't showing correctly:
1. Check if UFC.com structure has changed
2. Run the debug script to see database contents
3. Clear and re-run the pipeline

The unified system ensures that your Flutter app always shows the most current UFC rankings and champions! 