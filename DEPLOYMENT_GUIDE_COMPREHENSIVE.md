# AdWise AI Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the AdWise AI Digital Marketing Campaign Builder in various environments, from local development to production.

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher (for frontend)
- **MongoDB**: 5.0 or higher
- **Redis**: 6.0 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for production)
- **Storage**: Minimum 20GB available space

### Required Services
- **EURI AI API Key**: For AI content generation
- **MongoDB Database**: For data storage
- **Redis Instance**: For caching and sessions
- **SMTP Server**: For email notifications (optional)

## Quick Start (Development)

### 1. Clone Repository
```bash
git clone https://github.com/erickyegon/adwise-campaign-builder.git
cd adwise-campaign-builder
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```bash
# Minimum required for development
EURI_API_KEY="your_euri_api_key"
MONGODB_URL="mongodb://localhost:27017"
REDIS_URL="redis://localhost:6379"
SECRET_KEY="your-secret-key-change-this"
```

### 3. Install Dependencies
```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies (optional)
cd frontend
npm install
cd ..
```

### 4. Start Services
```bash
# Start MongoDB (if not running)
sudo systemctl start mongod

# Start Redis (if not running)
sudo systemctl start redis

# Start the application
python app/main.py
```

### 5. Verify Installation
```bash
# Check API health
curl http://127.0.0.1:8002/health

# Access API documentation
open http://127.0.0.1:8002/docs
```

## Production Deployment

### Option 1: Docker Deployment (Recommended)

#### 1. Build Docker Images
```bash
# Build backend image
docker build -t adwise-api:latest .

# Build frontend image (if using)
cd frontend
docker build -t adwise-frontend:latest .
cd ..
```

#### 2. Docker Compose Deployment
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f adwise-api
```

#### 3. Environment Configuration
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  adwise-api:
    image: adwise-api:latest
    ports:
      - "8002:8002"
    environment:
      - ENVIRONMENT=production
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - EURI_API_KEY=${EURI_API_KEY}
    depends_on:
      - mongodb
      - redis
    restart: unless-stopped

  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

  redis:
    image: redis:6.0-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - adwise-api
    restart: unless-stopped

volumes:
  mongodb_data:
  redis_data:
```

### Option 2: Manual Server Deployment

#### 1. Server Setup (Ubuntu 20.04+)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install mongodb-org -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y
```

#### 2. Application Setup
```bash
# Create application user
sudo useradd -m -s /bin/bash adwise
sudo su - adwise

# Clone repository
git clone https://github.com/erickyegon/adwise-campaign-builder.git
cd adwise-campaign-builder

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Configure production settings
```

#### 3. Systemd Service Setup
Create `/etc/systemd/system/adwise-api.service`:
```ini
[Unit]
Description=AdWise AI Campaign Builder API
After=network.target mongodb.service redis.service

[Service]
Type=exec
User=adwise
Group=adwise
WorkingDirectory=/home/adwise/adwise-campaign-builder
Environment=PATH=/home/adwise/adwise-campaign-builder/venv/bin
ExecStart=/home/adwise/adwise-campaign-builder/venv/bin/python app/main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 4. Nginx Configuration
Create `/etc/nginx/sites-available/adwise`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Documentation
    location /docs {
        proxy_pass http://127.0.0.1:8002/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /home/adwise/adwise-campaign-builder/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend (if serving from same domain)
    location / {
        root /var/www/adwise-frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

#### 5. Start Services
```bash
# Enable and start services
sudo systemctl enable mongodb redis nginx adwise-api
sudo systemctl start mongodb redis nginx adwise-api

# Check status
sudo systemctl status adwise-api
```

### Option 3: Cloud Deployment

#### AWS Deployment
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Deploy using AWS ECS or EC2
# (Detailed AWS deployment scripts available in /scripts/aws/)
```

#### Google Cloud Deployment
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Deploy to Google Cloud Run
gcloud run deploy adwise-api \
  --image gcr.io/PROJECT_ID/adwise-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Deployment
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Deploy to Azure Container Instances
az container create \
  --resource-group adwise-rg \
  --name adwise-api \
  --image adwise-api:latest \
  --ports 8002
```

## Database Setup

### MongoDB Configuration
```javascript
// Connect to MongoDB
use adwise_campaigns

// Create indexes for performance
db.campaigns.createIndex({ "user_id": 1, "status": 1 })
db.campaigns.createIndex({ "created_at": -1 })
db.ads.createIndex({ "campaign_id": 1, "status": 1 })
db.users.createIndex({ "email": 1 }, { unique: true })

// Create initial admin user
db.users.insertOne({
  email: "admin@adwise.ai",
  name: "Admin User",
  role: "admin",
  password_hash: "hashed_password",
  created_at: new Date(),
  is_active: true
})
```

### Redis Configuration
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Key settings for production:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## SSL/TLS Setup

### Let's Encrypt (Free SSL)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Custom SSL Certificate
```bash
# Place certificates
sudo mkdir -p /etc/nginx/ssl
sudo cp your-cert.pem /etc/nginx/ssl/cert.pem
sudo cp your-key.pem /etc/nginx/ssl/key.pem
sudo chmod 600 /etc/nginx/ssl/*
```

## Monitoring & Logging

### Application Monitoring
```bash
# Install monitoring tools
pip install prometheus-client sentry-sdk

# Configure Prometheus metrics
# Add to .env:
PROMETHEUS_ENABLED=true
SENTRY_DSN=your_sentry_dsn
```

### Log Management
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/adwise

# Content:
/home/adwise/adwise-campaign-builder/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 adwise adwise
    postrotate
        systemctl reload adwise-api
    endscript
}
```

### Health Checks
```bash
# Create health check script
cat > /home/adwise/health-check.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health)
if [ $response -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is unhealthy (HTTP $response)"
    exit 1
fi
EOF

chmod +x /home/adwise/health-check.sh

# Add to crontab for monitoring
crontab -e
# Add: */5 * * * * /home/adwise/health-check.sh
```

## Backup & Recovery

### Database Backup
```bash
# Create backup script
cat > /home/adwise/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/adwise/backups"
mkdir -p $BACKUP_DIR

# MongoDB backup
mongodump --db adwise_campaigns --out $BACKUP_DIR/mongodb_$DATE

# Compress backup
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/mongodb_$DATE
rm -rf $BACKUP_DIR/mongodb_$DATE

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
EOF

chmod +x /home/adwise/backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /home/adwise/backup.sh
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
sudo journalctl -u adwise-api -f

# Check configuration
python -c "from app.core.config import get_settings; print(get_settings())"

# Test database connection
python -c "import pymongo; client = pymongo.MongoClient('mongodb://localhost:27017'); print(client.server_info())"
```

#### 2. High Memory Usage
```bash
# Monitor memory usage
htop

# Check Python processes
ps aux | grep python

# Optimize MongoDB
# Add to /etc/mongod.conf:
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 1
```

#### 3. Slow API Responses
```bash
# Check database indexes
mongo adwise_campaigns --eval "db.campaigns.getIndexes()"

# Monitor Redis
redis-cli monitor

# Check network latency
ping your-database-host
```

### Performance Optimization

#### 1. Database Optimization
```javascript
// MongoDB performance tuning
db.campaigns.createIndex({ "user_id": 1, "status": 1, "created_at": -1 })
db.ads.createIndex({ "campaign_id": 1, "performance.ctr": -1 })
```

#### 2. Caching Strategy
```python
# Redis caching configuration
CACHE_TTL_SECONDS=3600
ENABLE_QUERY_CACHING=true
ENABLE_RESPONSE_CACHING=true
```

#### 3. Load Balancing
```nginx
upstream adwise_backend {
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}

server {
    location /api/ {
        proxy_pass http://adwise_backend;
    }
}
```

## Security Checklist

- [ ] Change default passwords and secrets
- [ ] Enable SSL/TLS encryption
- [ ] Configure firewall rules
- [ ] Set up regular security updates
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Implement proper authentication
- [ ] Regular security scans
- [ ] Backup encryption
- [ ] Access control reviews

## Support

For deployment assistance:
- **Documentation**: https://docs.adwise.ai
- **GitHub Issues**: https://github.com/erickyegon/adwise-campaign-builder/issues
- **Email Support**: support@adwise.ai
- **Community**: https://discord.gg/adwise-ai
