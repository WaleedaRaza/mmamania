#!/bin/bash

# FightHub Quick Start Script
# This script sets up and runs the FightHub platform locally

set -e

echo "🥊 Welcome to FightHub - MMA Prediction & Community Platform"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+"
        exit 1
    fi
    
    # Check Flutter
    if ! command -v flutter &> /dev/null; then
        print_warning "Flutter is not installed. Please install Flutter SDK 3.0+"
        print_warning "Visit: https://flutter.dev/docs/get-started/install"
    fi
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL is not installed. Please install PostgreSQL 13+"
        print_warning "You can use Docker or install locally"
    fi
    
    # Check Redis
    if ! command -v redis-server &> /dev/null; then
        print_warning "Redis is not installed. Please install Redis 6+"
        print_warning "You can use Docker or install locally"
    fi
    
    print_success "Requirements check completed"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# App settings
APP_NAME=FightHub API
APP_VERSION=1.0.0
DEBUG=true

# Database
DATABASE_URL=postgresql://fighthub_user:password@localhost/fighthub
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Settings
ML_MODEL_PATH=../ml/models/
PREDICTION_THRESHOLD=0.6

# CORS
ALLOWED_ORIGINS=["http://localhost:8080", "http://localhost:3000"]
EOF
        print_success "Created .env file"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup ML pipeline
setup_ml() {
    print_status "Setting up ML pipeline..."
    
    cd ml
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment for ML..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing ML dependencies..."
    pip install -r requirements.txt
    
    # Create models directory
    mkdir -p models
    mkdir -p data
    
    cd ..
    print_success "ML pipeline setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Get Flutter dependencies
    if command -v flutter &> /dev/null; then
        print_status "Getting Flutter dependencies..."
        flutter pub get
    else
        print_warning "Flutter not found. Skipping frontend setup."
    fi
    
    cd ..
    print_success "Frontend setup completed"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start Redis (if available)
    if command -v redis-server &> /dev/null; then
        print_status "Starting Redis..."
        redis-server --daemonize yes
        print_success "Redis started"
    else
        print_warning "Redis not found. Please start Redis manually or use Docker."
    fi
    
    # Start PostgreSQL (if available)
    if command -v pg_ctl &> /dev/null; then
        print_status "Starting PostgreSQL..."
        # This assumes PostgreSQL is installed and configured
        print_warning "Please ensure PostgreSQL is running and database 'fighthub' exists"
    else
        print_warning "PostgreSQL not found. Please start PostgreSQL manually or use Docker."
    fi
}

# Start backend server
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    source venv/bin/activate
    
    # Start the server in background
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    cd ..
    print_success "Backend server started on http://localhost:8000"
    print_success "API documentation available at http://localhost:8000/docs"
}

# Start frontend (if Flutter is available)
start_frontend() {
    if command -v flutter &> /dev/null; then
        print_status "Starting Flutter frontend..."
        
        cd frontend
        
        # Start Flutter web server
        flutter run -d web-server --web-port 8080 &
        FRONTEND_PID=$!
        
        cd ..
        print_success "Frontend started on http://localhost:8080"
    else
        print_warning "Flutter not available. Frontend not started."
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    # Set up cleanup on script exit
    trap cleanup EXIT
    
    print_status "Starting FightHub setup..."
    
    # Check requirements
    check_requirements
    
    # Setup components
    setup_backend
    setup_ml
    setup_frontend
    
    # Start services
    start_services
    
    # Start applications
    start_backend
    start_frontend
    
    print_success "FightHub is starting up!"
    echo ""
    echo "🌐 Frontend: http://localhost:8080"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for user to stop
    wait
}

# Run main function
main "$@" 