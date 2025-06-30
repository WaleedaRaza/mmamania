# MMAmania - MMA Fan Platform

A comprehensive MMA (UFC) fan platform built with Flutter and Python, featuring real UFC data, fighter profiles, rankings, and advanced analytics.

## 🥊 Features

### Core Features
- **Real UFC Rankings**: Live rankings across all divisions with real fighter records
- **Fighter Profiles**: Detailed fighter information, stats, and fight history
- **Comprehensive Data**: 200+ fighters with real records, stats, and personal info
- **Division Management**: Organized by UFC weight classes
- **Champion Tracking**: Special handling for division champions

### Technical Features
- **Multi-Source Scraping**: UFC.com, UFCStats.com, ESPN integration
- **Batch Processing**: Efficient data collection with rate limiting
- **Real-time Updates**: "Live enough" system with scheduled scraping
- **Cross-Platform**: iOS, Android, Web support
- **Modern UI**: UFC-themed design with gradients and animations

## 🏗️ Architecture

### Frontend (Flutter)
- **Models**: Fighter, Ranking, Fight, Record, Stats
- **Services**: UFC Data Service, API Service
- **Screens**: Rankings, Fighter Profiles, Stats, Debates
- **Widgets**: Reusable UI components

### Backend (Python)
- **FastAPI**: RESTful API with PostgreSQL/SQLite
- **Scrapy**: Web scraping framework for UFC data
- **Selenium**: Deep scraping for fighter profiles
- **Data Processing**: Cleaning and structuring scraped data

### Data Pipeline
- **Scraping**: Multi-source UFC data collection
- **Processing**: Data cleaning and validation
- **Storage**: JSON files for Flutter assets
- **Updates**: Scheduled scraping every 6-12 hours

## 🚀 Quick Start

### Prerequisites
- Flutter SDK (latest stable)
- Python 3.8+
- iOS Simulator / Android Emulator

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/WaleedaRaza/mmamania.git
   cd mmamania
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r backend/requirements.txt
   pip install scrapy selenium webdriver-manager
   ```

4. **Scrape UFC data**
   ```bash
   python3 scripts/extract_and_run_fighters.py
   ```

5. **Run the app**
   ```bash
   flutter run
   ```

## 📊 Data Sources

### UFC.com
- Official rankings
- Fighter profiles
- Event information

### UFCStats.com
- Detailed fight statistics
- Historical data
- Performance metrics

### ESPN
- Additional fighter information
- News and updates

## 🔧 Development

### Project Structure
```
MMA/
├── lib/                    # Flutter app
│   ├── models/            # Data models
│   ├── screens/           # UI screens
│   ├── services/          # Business logic
│   └── widgets/           # Reusable components
├── backend/               # Python backend
│   ├── app/              # FastAPI application
│   ├── models/           # Database models
│   └── services/         # Business services
├── ufc_scraper/          # Scrapy project
│   ├── spiders/          # Web scrapers
│   └── pipelines/        # Data processing
├── scripts/              # Utility scripts
└── assets/data/          # UFC data files
```

### Key Components

#### UFC Data Service
- Loads and manages UFC data
- Handles fighter-profile linking
- Provides division-based queries

#### Scrapy Pipeline
- Rankings spider: Scrapes UFC rankings
- Fighters spider: Scrapes detailed fighter profiles
- Batch processing: Handles large datasets efficiently

#### Flutter Models
- `Fighter`: Complete fighter information
- `Ranking`: Division rankings with records
- `Record`: Win/loss/draw statistics
- `FighterStats`: Performance metrics

## 📱 Screenshots

### Rankings Screen
- Tabbed interface by division
- Champion cards with special styling
- Rank badges and change indicators
- Navigation to fighter profiles

### Fighter Profile Screen
- Detailed fighter information
- Performance statistics
- Fight history
- Personal information

## 🔄 Data Updates

The app uses a "live enough" approach:
- **Scheduled scraping**: Every 6-12 hours
- **Batch processing**: Efficient handling of 200+ fighters
- **Caching**: Reduces load on UFC servers
- **Manual refresh**: Users can trigger updates

## 🛠️ Customization

### Adding New Data Sources
1. Create new Scrapy spider
2. Add to scraping pipeline
3. Update data models
4. Integrate with Flutter app

### UI Customization
- Modify theme colors in `lib/main.dart`
- Update widget styles in `lib/widgets/`
- Add new screens in `lib/screens/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- UFC for providing public data
- Flutter team for the amazing framework
- Scrapy community for web scraping tools

## 📞 Support

For questions or support, please open an issue on GitHub.

---

**MMAmania** - The ultimate UFC fan platform! 🥊 
