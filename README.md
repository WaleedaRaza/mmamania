<<<<<<< HEAD
# FightHub - MMA Prediction & Community Platform

A Flutter app for MMA fans to track fighters, make predictions, and engage in live debates.

## 🚀 Quick Start

### Prerequisites
- Flutter SDK (3.0.0 or higher)
- Dart SDK
- Supabase account
- Python 3.8+ (for data migration)

### 1. Setup Supabase

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Get your project URL and anon key from Settings > API
3. Update the configuration in `lib/main.dart`:
   ```dart
   await Supabase.initialize(
     url: 'YOUR_SUPABASE_URL',
     anonKey: 'YOUR_SUPABASE_ANON_KEY',
   );
   ```

### 2. Migrate Data to Supabase

1. Install Python dependencies:
   ```bash
   pip install supabase
   ```

2. Update the Supabase credentials in `scripts/supabase_migration.py`:
   ```python
   SUPABASE_URL = "YOUR_SUPABASE_URL"
   SUPABASE_KEY = "YOUR_SUPABASE_SERVICE_KEY"
   ```

3. Run the migration script:
   ```bash
   python scripts/supabase_migration.py
   ```

### 3. Install Flutter Dependencies

```bash
flutter pub get
```

### 4. Run the App

```bash
flutter run
```

## 📱 Features

### Current Features
- ✅ **Authentication** - Sign up/sign in with Supabase Auth
- ✅ **Fighter Rankings** - View UFC rankings by weight class
- ✅ **Fight Cards** - Browse upcoming and past events
- ✅ **User Profiles** - View stats and settings
- ✅ **Live Debates** - Create and join MMA discussions
- ✅ **Analytics** - Track prediction performance
- ✅ **Modern UI** - Beautiful, responsive design

### Planned Features
- 🔄 **Real-time Updates** - Live fight results and rankings
- 🔄 **Prediction System** - Make and track fight predictions
- 🔄 **Leaderboards** - Compare prediction accuracy
- 🔄 **Push Notifications** - Fight reminders and results
- 🔄 **Social Features** - Follow fighters and users
- 🔄 **Advanced Analytics** - Detailed performance metrics
=======
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
>>>>>>> 638a726d2771376ba71e0338bcda2ffc8c49bccd

## 🏗️ Architecture

### Frontend (Flutter)
<<<<<<< HEAD
- **State Management**: Provider + Riverpod
- **Navigation**: Go Router
- **UI Components**: Custom widgets with Material Design
- **Charts**: FL Chart for analytics
- **Storage**: Hive for local caching

### Backend (Supabase)
- **Database**: PostgreSQL with real-time subscriptions
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage for images
- **Functions**: PostgreSQL functions for analytics

### Data Pipeline
- **Scrapers**: Python scripts for UFC data
- **Processing**: CSV/JSON data processing
- **Migration**: Automated Supabase migration

## 📊 Data Structure

### Core Tables
- `fighters` - UFC fighter profiles and stats
- `fights` - Individual fight records
- `events` - UFC event information
- `rankings` - Current UFC rankings
- `user_profiles` - User account information
- `predictions` - User fight predictions
- `debates` - Live debate rooms
- `hot_takes` - User hot takes and opinions

### Key Features
- **Real-time subscriptions** for live updates
- **Row Level Security** for data protection
- **Automated analytics** via PostgreSQL functions
- **Scalable architecture** for future growth
=======
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
>>>>>>> 638a726d2771376ba71e0338bcda2ffc8c49bccd

## 🔧 Development

### Project Structure
```
<<<<<<< HEAD
lib/
├── main.dart              # App entry point
├── models/               # Data models
├── screens/              # UI screens
├── services/             # API and business logic
├── widgets/              # Reusable components
└── providers/            # State management

assets/
├── data/                # JSON data files
└── images/              # App images

scripts/
└── supabase_migration.py # Data migration script

data/
├── processed/           # Processed CSV data
└── live/               # Live data exports
```

### Key Dependencies
- `supabase_flutter` - Backend integration
- `provider` + `riverpod` - State management
- `fl_chart` - Analytics charts
- `hive` - Local storage
- `go_router` - Navigation

## 🚀 Deployment

### iOS
```bash
flutter build ios
```

### Android
```bash
flutter build apk
```

### Web
```bash
flutter build web
```

## 🔄 Data Updates

### Automated Scraping
The app includes Python scrapers for:
- UFC fighter profiles
- Current rankings
- Fight results
- Event information

### Manual Updates
1. Run scrapers: `python scrapers/ufc/quick_fighter_profile_scraper.py`
2. Process data: `python scripts/process_data.py`
3. Migrate to Supabase: `python scripts/supabase_migration.py`
=======
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
>>>>>>> 638a726d2771376ba71e0338bcda2ffc8c49bccd

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
<<<<<<< HEAD
4. Add tests if applicable
=======
4. Test thoroughly
>>>>>>> 638a726d2771376ba71e0338bcda2ffc8c49bccd
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

<<<<<<< HEAD
## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Include logs and error messages

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Basic app structure
- ✅ Supabase integration
- ✅ Authentication
- ✅ Core screens

### Phase 2 (Next)
- 🔄 Real-time fight updates
- 🔄 Prediction system
- 🔄 Push notifications
- 🔄 Enhanced analytics

### Phase 3 (Future)
- 🔄 Social features
- 🔄 Advanced ML predictions
- 🔄 Live streaming integration
- 🔄 Mobile app stores

---

**Built with ❤️ for the MMA community**
=======
## 🙏 Acknowledgments

- UFC for providing public data
- Flutter team for the amazing framework
- Scrapy community for web scraping tools

## 📞 Support

For questions or support, please open an issue on GitHub.

---

**MMAmania** - The ultimate UFC fan platform! 🥊 
>>>>>>> 638a726d2771376ba71e0338bcda2ffc8c49bccd
