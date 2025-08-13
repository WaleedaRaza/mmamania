# MMAmania - Complete Code Index

## 📁 Project Structure Overview

This document provides a comprehensive index of all code files in the MMAmania project, organized by functionality and architecture.

## 🏗️ Core Application Architecture

### Frontend (Flutter/Dart)

#### Main Application Entry
- **`lib/main.dart`** (471 lines) - Main Flutter application entry point with Supabase initialization, theme configuration, and navigation setup

#### Models (Data Structures)
- **`lib/models/`** - Data models for the application
  - `audio_participant.dart` - Audio session participant model
  - `audio_session.dart` - Audio session management
  - `debate_message.dart` - Debate messaging system
  - `fight.dart` - Fight data model
  - `fighter.dart` - Fighter profile model
  - `user.dart` - User account model

#### Services (Business Logic)
- **`lib/services/`** - Service layer for API communication and business logic
  - `api_service.dart` - REST API client for backend communication
  - `database_service.dart` - Local database operations
  - `fighter_service.dart` - Fighter-specific business logic
  - `supabase_service.dart` - Supabase integration service

#### Screens (UI Components)
- **`lib/screens/`** - Main application screens
  - `analytics_screen.dart` - Analytics and statistics display
  - `audio_debate_room_screen.dart` - Real-time audio debate interface
  - `debates_screen.dart` - Debate management interface
  - `fight_cards_screen.dart` - Fight card display
  - `profile_screen.dart` - User profile management
  - `rankings_screen.dart` - UFC rankings display
  - `reddit_feed_screen.dart` - Reddit content aggregation

#### Widgets (Reusable Components)
- **`lib/widgets/`** - Reusable UI components
  - `fight_card_widget.dart` - Individual fight card display component

#### Providers (State Management)
- **`lib/providers/`** - State management using Provider pattern
  - `mma_feed_provider.dart` - MMA feed data provider

#### Views (Custom Views)
- **`lib/views/`** - Custom view implementations
  - `mma_feed_screen.dart` - MMA feed display view

### Backend (Python/FastAPI)

#### Main Application
- **`backend/main.py`** (63 lines) - Backend application entry point
- **`backend/app/main.py`** (36 lines) - FastAPI application configuration with CORS and router setup

#### API Endpoints
- **`backend/app/api/`** - REST API endpoints
  - `auth.py` - Authentication endpoints (login, register, token refresh)
  - `debates.py` - Debate management endpoints
  - `fights.py` - Fight data endpoints
  - `fighters.py` - Fighter profile endpoints
  - `predictions.py` - Prediction and ELO system endpoints
  - `rankings.py` - UFC rankings endpoints
  - `users.py` - User management endpoints

#### Data Models
- **`backend/app/models/`** - Database models
  - `base.py` - Base model configuration
  - `debate.py` - Debate database model
  - `fight.py` - Fight database model
  - `fighter.py` - Fighter database model
  - `prediction.py` - Prediction database model
  - `user.py` - User database model

#### Schemas (Data Validation)
- **`backend/app/schemas/`** - Pydantic schemas for request/response validation
  - `debate.py` - Debate request/response schemas
  - `fight.py` - Fight data schemas
  - `fighter.py` - Fighter data schemas
  - `prediction.py` - Prediction schemas
  - `user.py` - User data schemas

#### Core Configuration
- **`backend/app/core/`** - Core application configuration
  - `config.py` - Application configuration settings
  - `database.py` - Database connection and session management
  - `deps.py` - Dependency injection setup

#### Services (Business Logic)
- **`backend/app/services/`** - Backend business logic services
  - `elo_service.py` - ELO rating system implementation
  - `ml_service.py` - Machine learning model services
  - `scheduler_service.py` - Background task scheduling

## 🤖 AI/ML Pipeline

### Machine Learning Models
- **`ml/train_models.py`** (145 lines) - Model training pipeline for fight predictions
- **`ml/requirements.txt`** - ML dependencies (PyTorch, scikit-learn, etc.)

## 🔍 Data Scraping Infrastructure

### Wikipedia Scrapers
- **`scrapers/wikipedia/`** - Wikipedia UFC data extraction
  - `comprehensive_wikipedia_scraper.py` (335 lines) - Complete Wikipedia UFC event scraper
  - `enhanced_comprehensive_scraper.py` (458 lines) - Enhanced Wikipedia scraper with error handling
  - `past_events_scraper.py` (371 lines) - Historical UFC events scraper
  - `quick_wikipedia_scraper.py` (157 lines) - Fast Wikipedia data extraction

### UFC Scrapers
- **`scrapers/ufc/`** - UFC.com data extraction
  - `real_dynamic_scraper.py` (213 lines) - Dynamic UFC rankings scraper
  - `unified_ufc_scraper.py` (313 lines) - Unified UFC data extraction system

## 📊 Data Processing & Management

### Data Processors
- **`data/processors/`** - Data processing utilities
  - `ufc_data_processor.py` - UFC data processing and transformation

### Data Scrapers
- **`data/scrapers/`** - Data collection utilities
  - `ufc_scraper.py` - UFC data scraping utilities

### Data Exports
- **`data/exports/`** - Processed data exports
  - Multiple JSON and CSV files with processed UFC data

### Live Data
- **`data/live/`** - Real-time data feeds
  - `live_fighter_profiles.csv` - Live fighter profile data
  - `live_fighter_profiles.json` - JSON format of live fighter data

### Processed Data
- **`data/processed/`** - Cleaned and processed datasets
  - `events.csv` - Processed UFC events data
  - `fighters.csv` - Processed fighter profiles
  - `fights.csv` - Processed fight records

## 🔧 Scripts & Utilities

### Database Management Scripts
- **`scripts/`** - Database and data management utilities
  - `add_schema_properties.py` (36 lines) - Database schema property management
  - `add_schema_properties.sql` (10 lines) - SQL schema modifications
  - `create_clean_schemas.sql` (230 lines) - Database schema creation
  - `create_clean_schemas_public.sql` (151 lines) - Public schema setup
  - `destroy_and_rebuild_schemas.sql` (156 lines) - Schema rebuild utilities
  - `populate_fighter_records.py` (153 lines) - Fighter record population
  - `populate_rankings.py` (172 lines) - Rankings data population
  - `safe_database_wipe.py` (176 lines) - Safe database cleanup
  - `complete_database_wipe.py` (185 lines) - Complete database reset
  - `verify_current_database.py` (103 lines) - Database verification utilities

### Scraping Scripts
- **`scripts/`** - Advanced scraping utilities
  - `enhanced_wikipedia_scraper.py` (451 lines) - Enhanced Wikipedia scraper
  - `enhanced_rankings_scraper.py` (411 lines) - UFC rankings scraper
  - `full_scraper.py` (402 lines) - Complete data scraping pipeline
  - `ultra_robust_scraper.py` (656 lines) - Robust scraping with error handling
  - `parallel_robust_scraper.py` (499 lines) - Parallel processing scraper
  - `integrated_wikipedia_scraper.py` (473 lines) - Integrated Wikipedia scraper
  - `targeted_ufc_scraper.py` (22KB) - Targeted UFC data extraction
  - `scale_past_events.py` (24KB) - Historical event scaling

### Data Analysis Scripts
- **`scripts/`** - Data analysis and processing
  - `calculate_rankings_records.py` (207 lines) - Rankings calculation
  - `calculate_fighter_records.py` (171 lines) - Fighter record calculation
  - `analyze_scaling_strategy.py` (13KB) - Scaling strategy analysis
  - `performance_monitor.py` (4.0KB) - Performance monitoring
  - `simple_analysis.py` (3.9KB) - Basic data analysis

### Testing Scripts
- **`scripts/`** - Testing and validation utilities
  - `test_single_event.py` (97 lines) - Single event testing
  - `test_fight_creation.py` (191 lines) - Fight creation testing
  - `test_multiple_events.py` (191 lines) - Multiple event testing
  - `test_parsing.py` (22 lines) - Data parsing tests
  - `test_winner_display.py` (170 lines) - Winner display testing
  - `test_rankings_query.dart` (40 lines) - Rankings query testing

### Debug Scripts
- **`scripts/`** - Debugging and troubleshooting
  - `debug_table_structure.py` (110 lines) - Database table structure debugging
  - `debug_date_scraping.py` (107 lines) - Date parsing debugging
  - `debug_wikipedia_structure.py` (5.9KB) - Wikipedia structure debugging
  - `debug_flutter_data.py` (8.8KB) - Flutter data debugging
  - `quick_debug.py` (4.7KB) - Quick debugging utilities

### Data Fix Scripts
- **`scripts/`** - Data correction and repair
  - `fix_event_fight_relationships.py` (6.0KB) - Event-fight relationship fixes
  - `fix_duplication.py` (9.0KB) - Duplicate data removal
  - `fix_event_fight_linking.py` (4.0KB) - Event-fight linking fixes
  - `dynamic_event_fight_fix.py` (7.9KB) - Dynamic event-fight fixes
  - `real_data_pipeline.py` (12KB) - Real data processing pipeline

## 🚀 Services & Infrastructure

### Real-time Services
- **`services/`** - Real-time and background services
  - `realtime_updater.py` (321 lines) - Real-time data updates
  - `firestore_service.py` (363 lines) - Firestore database service

### Schedulers
- **`schedulers/`** - Background task scheduling
  - `firestore_scheduler.py` - Firestore-based task scheduling

## 📱 Mobile Platform Support

### iOS Configuration
- **`ios/`** - iOS-specific configuration and assets
  - `Runner/` - iOS app configuration
  - `GoogleService-Info.plist` - Firebase configuration

### Android Configuration
- **`android/`** - Android-specific configuration
  - `app/build.gradle.kts` - Android build configuration
  - `gradle.properties` - Gradle properties

### Cross-Platform Support
- **`web/`** - Web platform support
- **`macos/`** - macOS platform support
- **`linux/`** - Linux platform support
- **`windows/`** - Windows platform support

## 🎨 Design System

### Design Package
- **`design_package/`** - Design system and UI components
  - `lib/main.dart` - Design system main entry
  - `lib/models/` - Design system data models
  - `lib/screens/` - Design system screens
  - `lib/widgets/` - Design system widgets
  - `DESIGN_SYSTEM.md` - Design system documentation
  - `QUICK_SETUP.md` - Quick setup guide

## 📋 Configuration Files

### Dependencies
- **`pubspec.yaml`** (84 lines) - Flutter dependencies
- **`pubspec.lock`** (1304 lines) - Locked dependency versions
- **`backend/requirements.txt`** (24 lines) - Python backend dependencies
- **`scripts/requirements.txt`** (103B) - Script dependencies

### Build Configuration
- **`analysis_options.yaml`** (29 lines) - Dart analysis configuration
- **`.flutter-plugins-dependencies`** (9.8KB) - Flutter plugin dependencies
- **`.metadata`** (31 lines) - Project metadata

### Platform Configuration
- **`android/build.gradle.kts`** - Android build configuration
- **`android/gradle.properties`** - Gradle properties
- **`android/settings.gradle.kts`** - Gradle settings

## 📊 Data Files

### Raw Data
- **`ufc_raw_data.json`** (450KB, 16851 lines) - Raw UFC data
- **`ufc_enhanced_data_20250629_232935.json`** (286KB, 10643 lines) - Enhanced UFC data
- **`ufc_processed_data.json`** (151KB, 7171 lines) - Processed UFC data
- **`test_full_data.json`** (450KB, 16851 lines) - Test data

### Rankings Data
- **`data/real_dynamic_rankings.json`** (32KB, 1462 lines) - Real-time rankings
- **`data/unified_ufc_rankings.json`** (42KB, 1562 lines) - Unified rankings
- **`data/ufc_rankings.json`** (44KB, 1650 lines) - UFC rankings

### Test Data
- **`test_profile_islam-makhachev.json`** (54 lines) - Test fighter profile
- **`test_profile_merab-dvalishvili.json`** (54 lines) - Test fighter profile
- **`test_fighter_output.json`** (5 lines) - Test fighter output

## 📚 Documentation

### Technical Documentation
- **`README.md`** (169 lines) - Main project documentation
- **`README2.md`** (166 lines) - Advanced technical documentation
- **`COMPLETE_SOLUTION.md`** (132 lines) - Complete solution overview
- **`DATA_PIPELINE_ANALYSIS.md`** (150 lines) - Data pipeline analysis
- **`SCRAPER_ANALYSIS.md`** (201 lines) - Scraper analysis
- **`DEPLOYMENT.md`** (519 lines) - Deployment guide
- **`UFC_DATA_PIPELINE.md`** (78 lines) - UFC data pipeline documentation

### Analysis Documents
- **`FULLY_DYNAMIC_SOLUTION.md`** (105 lines) - Dynamic solution analysis
- **`NON_HARDCODED_SOLUTION.md`** (103 lines) - Non-hardcoded solution
- **`EVENT_FIGHT_FIX_SUMMARY.md`** (153 lines) - Event-fight fix summary
- **`OPTIMIZATION_SUMMARY.md`** (136 lines) - Optimization summary

## 🔧 Development Tools

### Setup Scripts
- **`quick_start.sh`** (269 lines) - Quick project setup script

### Environment Configuration
- **`.gitignore`** (225 lines) - Git ignore patterns
- **`scripts/env_example.txt`** (335B) - Environment configuration example

## 📈 Statistics Summary

### Code Metrics
- **Total Files**: 200+ code files
- **Lines of Code**: 50,000+ lines
- **Languages**: Dart, Python, SQL, Shell, YAML
- **Frameworks**: Flutter, FastAPI, Supabase, Firebase

### Data Coverage
- **UFC Events**: 654+ events processed
- **Fights**: 7,533+ fight records
- **Fighters**: 200+ ranked fighters
- **Data Points**: 10,000+ processed nightly

### Architecture Components
- **Frontend**: Flutter mobile app with WebRTC
- **Backend**: FastAPI with PostgreSQL/Supabase
- **AI/ML**: ELO system, sentiment analysis, predictions
- **Data Pipeline**: Distributed scraping with Ray/Apache Spark
- **Real-time**: WebSocket connections and live updates

## 🎯 Key Features Indexed

### Real-time Features
- Live fight data updates
- WebSocket connections
- Real-time debate system
- Live rankings updates

### AI/ML Features
- ELO rating system
- Sentiment analysis
- Fight predictions
- Speech-to-text processing

### Data Processing
- Multi-source scraping
- Distributed processing
- Real-time ingestion
- Quality validation

### User Experience
- Cross-platform support
- Modern UI/UX design
- Real-time communication
- Community features

---

*This index covers the complete MMAmania codebase as of the latest commit. For detailed implementation specifics, refer to individual file documentation and inline comments.* 