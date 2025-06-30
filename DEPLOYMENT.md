# 🚀 FightHub Deployment Guide

This guide covers deploying the complete FightHub MMA prediction and community platform.

## 📋 Prerequisites

- Python 3.9+
- Flutter SDK 3.0+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)
- Node.js 18+ (for web frontend)

## 🏗️ Architecture Overview

```
FightHub Platform
├── Backend (FastAPI) - Port 8000
├── Frontend (Flutter) - Port 8080
├── Database (PostgreSQL) - Port 5432
├── Cache (Redis) - Port 6379
└── ML Pipeline (Python) - Background jobs
```

## 🔧 Backend Deployment

### 1. Environment Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup

```sql
-- Create PostgreSQL database
CREATE DATABASE fighthub;
CREATE USER fighthub_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fighthub TO fighthub_user;
```

### 3. Environment Configuration

Create `.env` file in `backend/`:

```env
# App settings
APP_NAME=FightHub API
APP_VERSION=1.0.0
DEBUG=false

# Database
DATABASE_URL=postgresql://fighthub_user:your_secure_password@localhost/fighthub
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs (optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# ML Settings
ML_MODEL_PATH=ml/models/
PREDICTION_THRESHOLD=0.6

# CORS
ALLOWED_ORIGINS=["http://localhost:8080", "https://yourdomain.com"]
```

### 4. Database Migration

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Start Backend Server

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

For production:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📱 Flutter Frontend Deployment

### 1. Environment Setup

```bash
cd frontend
flutter pub get
```

### 2. Configuration

Update `lib/services/api_service.dart`:
```dart
static const String baseUrl = 'https://your-api-domain.com';  // Production URL
```

### 3. Build for Production

#### Android APK
```bash
flutter build apk --release
```

#### Android App Bundle (Google Play)
```bash
flutter build appbundle --release
```

#### iOS
```bash
flutter build ios --release
```

#### Web
```bash
flutter build web --release
```

### 4. Deploy Web Version

```bash
# Build web version
flutter build web --release

# Deploy to any static hosting (Netlify, Vercel, etc.)
# Copy build/web/ contents to your hosting provider
```

## 🤖 ML Pipeline Deployment

### 1. Setup ML Environment

```bash
cd ml
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Data Collection

```bash
# Run UFC data scraper
python data/scrapers/ufc_scraper.py

# This will create:
# - data/upcoming_events.json
# - data/rankings.json
```

### 3. Train Models

```bash
# Train prediction models
python train_models.py

# This will create:
# - models/logistic_regression_best.joblib
# - models/feature_names.joblib
# - mlflow.db (experiment tracking)
```

### 4. Setup Scheduled Jobs

Create a cron job for data updates:

```bash
# Add to crontab
0 6 * * * cd /path/to/fighthub/ml && python data/scrapers/ufc_scraper.py
0 7 * * * cd /path/to/fighthub/ml && python train_models.py
```

## 🐳 Docker Deployment (Optional)

### 1. Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://fighthub_user:password@db:5432/fighthub
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=fighthub
      - POSTGRES_USER=fighthub_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 3. Deploy with Docker

```bash
docker-compose up -d
```

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. EC2 Setup
```bash
# Launch EC2 instance
# Install dependencies
sudo apt update
sudo apt install python3-pip postgresql redis-server nginx

# Setup PostgreSQL
sudo -u postgres createdb fighthub
sudo -u postgres createuser fighthub_user
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fighthub TO fighthub_user;"
```

#### 2. Nginx Configuration
```nginx
# /etc/nginx/sites-available/fighthub
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. Systemd Service
```ini
# /etc/systemd/system/fighthub.service
[Unit]
Description=FightHub API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/fighthub/backend
Environment=PATH=/home/ubuntu/fighthub/backend/venv/bin
ExecStart=/home/ubuntu/fighthub/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Railway Deployment

#### 1. Backend
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy backend
cd backend
railway login
railway init
railway up
```

#### 2. Frontend
```bash
cd frontend
railway init
railway up
```

### Vercel Deployment

#### 1. Backend
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd backend
vercel
```

#### 2. Frontend Web
```bash
cd frontend
flutter build web
vercel build/web
```

## 🔒 Security Configuration

### 1. SSL/TLS Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 2. Environment Security

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use environment variables for sensitive data
export SECRET_KEY="your-generated-secret"
export DATABASE_URL="postgresql://..."
```

### 3. Database Security

```sql
-- Create read-only user for analytics
CREATE USER fighthub_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE fighthub TO fighthub_readonly;
GRANT USAGE ON SCHEMA public TO fighthub_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO fighthub_readonly;
```

## 📊 Monitoring & Logging

### 1. Application Logs

```bash
# Backend logs
journalctl -u fighthub.service -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. Database Monitoring

```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. Performance Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop

# Monitor system resources
htop
iotop
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy FightHub

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      - name: Test Frontend
        run: |
          cd frontend
          flutter test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Production
        run: |
          # Your deployment script
          ./deploy.sh
```

## 📈 Scaling Considerations

### 1. Database Scaling

```sql
-- Add read replicas
-- Configure connection pooling with PgBouncer
-- Implement database sharding for large datasets
```

### 2. Application Scaling

```bash
# Use load balancer (HAProxy, Nginx)
# Implement horizontal scaling with multiple instances
# Use Redis for session storage and caching
```

### 3. ML Pipeline Scaling

```bash
# Use Kubernetes for ML job orchestration
# Implement model versioning with MLflow
# Use cloud ML services (AWS SageMaker, Google AI Platform)
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check PostgreSQL service status
   - Verify connection string
   - Check firewall settings

2. **CORS Errors**
   - Update ALLOWED_ORIGINS in backend config
   - Check frontend API URL configuration

3. **ML Model Loading Errors**
   - Verify model files exist
   - Check file permissions
   - Ensure correct Python environment

4. **Flutter Build Errors**
   - Update Flutter SDK
   - Clear build cache: `flutter clean`
   - Check dependency versions

### Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test individual components
4. Review security settings

## 📚 Additional Resources

- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Flutter Deployment Guide](https://flutter.dev/docs/deployment)
- [PostgreSQL Administration](https://www.postgresql.org/docs/current/admin.html)
- [Redis Documentation](https://redis.io/documentation) 