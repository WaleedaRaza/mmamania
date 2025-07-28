#!/bin/bash

# MMAMania Data Pipeline Runner
echo "🚀 Starting MMAMania Data Pipeline..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your Supabase credentials:"
    echo "SUPABASE_URL=your_supabase_url"
    echo "SUPABASE_SERVICE_KEY=your_service_key"
    exit 1
fi

# Load environment variables
source .env

# Check if required variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "❌ Error: Missing Supabase environment variables!"
    echo "Please check your .env file"
    exit 1
fi

echo "✅ Environment variables loaded"

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Run the data pipeline
echo "🔄 Running data pipeline..."
python3 data_pipeline.py

if [ $? -eq 0 ]; then
    echo "✅ Data pipeline completed successfully!"
    echo "🎉 Your Supabase database is now populated with live UFC data!"
    echo ""
    echo "Next steps:"
    echo "1. Run 'flutter run' to test the app"
    echo "2. Navigate to Rankings and Fight Cards screens"
    echo "3. You should see real data from Supabase!"
else
    echo "❌ Data pipeline failed!"
    exit 1
fi 