#!/bin/bash

# Database-Only Supabase Setup Script for MMAMania
# This script helps set up the database without authentication

echo "🚀 Setting up MMAMania Database (No Auth Required)"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ No .env file found!"
    echo "Please create a .env file with your Supabase credentials:"
    echo ""
    echo "SUPABASE_URL=https://your-project-id.supabase.co"
    echo "SUPABASE_SERVICE_KEY=your_service_role_key_here"
    echo "SUPABASE_ANON_KEY=your_anon_key_here"
    echo ""
    echo "You can get these from your Supabase project dashboard → Settings → API"
    exit 1
fi

# Load environment variables
source .env

# Check if required variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "❌ Missing required environment variables!"
    echo "Please check your .env file"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "📡 Connecting to: $SUPABASE_URL"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migration
echo "🗄️ Running database migration..."
python database_only_migration.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Database setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update lib/main.dart with your Supabase URL and anon key"
    echo "2. Run: flutter run"
    echo "3. Navigate to the 'Test' tab to verify connection"
    echo ""
    echo "Your database is ready for Clerk.dev authentication later!"
else
    echo "❌ Database setup failed!"
    echo "Please check the error messages above"
    exit 1
fi 