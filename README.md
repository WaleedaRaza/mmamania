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

## 🏗️ Architecture

### Frontend (Flutter)
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

## 🔧 Development

### Project Structure
```
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

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
