# 🚀 AdWise AI Digital Marketing Campaign Builder - Comprehensive Deployment Guide

## 📋 **Table of Contents**
1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Monitoring & Observability](#monitoring--observability)
8. [Security Configuration](#security-configuration)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## 🔧 **Prerequisites**

### System Requirements
- **Python**: 3.10+ (recommended: 3.11)
- **Node.js**: 18+ (for frontend development)
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+
- **Git**: Latest version

### Required Services
- **MongoDB**: 5.0+ (primary database)
- **Redis**: 6.0+ (caching and sessions)
- **PostgreSQL**: 13+ (optional, for analytics)

### External Services
- **EURI AI API**: Account and API key required
- **Email Service**: SMTP configuration
- **Cloud Storage**: AWS S3, Google Cloud Storage, or MinIO

---

## 🛠️ **Development Environment Setup**

### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone <repository-url>
cd "AdWise AI Digital Marketing Campaign Builder"

# Create Python virtual environment
python -m venv adwise_env

# Activate virtual environment
# Windows:
adwise_env\Scripts\activate
# Linux/Mac:
source adwise_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy development environment template
cp .env.development .env

# Edit environment variables
# Update EURI_API_KEY with your actual API key
# Configure database connections
# Set security keys
```

### 3. Database Setup
```bash
# Start development databases with Docker
docker-compose -f docker-compose.dev.yml up -d postgres mongodb redis

# Wait for services to be ready
docker-compose -f docker-compose.dev.yml ps

# Initialize databases (optional - auto-created on first run)
python -c "from app.core.database.mongodb import init_database; import asyncio; asyncio.run(init_database())"
```

### 4. Start Development Server
```bash
# Using comprehensive development server (recommended)
python run_dev_server.py --debug --reload --port 8000

# Or using uvicorn directly
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug

# Access the application
# Main: http://127.0.0.1:8000
# API Docs: http://127.0.0.1:8000/docs
# Health: http://127.0.0.1:8000/health
```

### 5. Development Tools Access
```bash
# Database administration
# pgAdmin: http://localhost:5050 (admin@adwise.ai / admin_password_2024)
# Mongo Express: http://localhost:8081 (admin / admin_password_2024)
# Redis Commander: http://localhost:8082 (admin / admin_password_2024)

# Monitoring
# Grafana: http://localhost:3000 (admin / admin_password_2024)
# Prometheus: http://localhost:9090

# Email testing
# MailHog: http://localhost:8025

# Object storage
# MinIO Console: http://localhost:9001 (admin / admin_password_2024)
```

---

## 🏭 **Production Deployment**

### 1. Production Environment Setup
```bash
# Create production environment file
cp .env.production.template .env.production

# Configure production settings
# - Set strong SECRET_KEY
# - Configure production database URLs
# - Set EURI_API_KEY
# - Configure email settings
# - Set up SSL certificates
# - Configure monitoring
```

### 2. Production Database Setup
```bash
# PostgreSQL (if using)
createdb adwise_campaigns_prod
psql adwise_campaigns_prod < scripts/init-prod-db.sql

# MongoDB
mongosh --eval "use adwise_campaigns_prod; db.createUser({user: 'adwise_prod', pwd: 'secure_password', roles: ['readWrite']})"

# Redis
redis-cli CONFIG SET requirepass "secure_redis_password"
```

### 3. Application Deployment
```bash
# Install production dependencies
pip install -r requirements.prod.txt

# Run database migrations
python scripts/migrate_database.py

# Start production server
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/adwise/access.log \
  --error-logfile /var/log/adwise/error.log \
  --log-level info \
  --timeout 120 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

### 4. Reverse Proxy Configuration (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout 120s;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐳 **Docker Deployment**

### 1. Build Production Image
```bash
# Build the application image
docker build -t adwise-ai:latest -f Dockerfile.prod .

# Or using docker-compose
docker-compose -f docker-compose.prod.yml build
```

### 2. Production Docker Compose
```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f app
```

### 3. Container Health Checks
```bash
# Check application health
curl http://localhost:8000/health

# Check detailed health
curl http://localhost:8000/health/detailed

# Check metrics
curl http://localhost:8000/metrics
```

---

## ⚙️ **Environment Configuration**

### Development (.env.development)
- Debug mode enabled
- Verbose logging
- Hot reload enabled
- Permissive CORS
- Local database connections
- Mock external services

### Production (.env.production)
- Debug mode disabled
- Structured logging
- Security headers enabled
- Restricted CORS
- Production database connections
- Real external services
- SSL/TLS enabled
- Rate limiting enabled

### Key Configuration Variables
```bash
# Application
APP_NAME="AdWise AI Campaign Builder"
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=your-super-secure-secret-key
ALLOWED_ORIGINS=["https://yourdomain.com"]

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
MONGODB_URL=mongodb://user:pass@host:27017/dbname
REDIS_URL=redis://user:pass@host:6379/0

# AI Integration
EURI_API_KEY=your-euri-api-key
EURI_BASE_URL=https://api.euri.ai/v1

# Email
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your-smtp-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
ENABLE_METRICS=true
```

---

## 🗄️ **Database Setup**

### MongoDB Configuration
```javascript
// Create indexes for optimal performance
db.campaigns.createIndex({ "user_id": 1, "created_at": -1 })
db.campaigns.createIndex({ "status": 1 })
db.campaigns.createIndex({ "tags": 1 })
db.ads.createIndex({ "campaign_id": 1 })
db.analytics.createIndex({ "campaign_id": 1, "date": -1 })
```

### Redis Configuration
```redis
# Memory optimization
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
requirepass your-redis-password
```

### Backup Strategy
```bash
# MongoDB backup
mongodump --uri="mongodb://user:pass@host:27017/adwise_campaigns" --out=/backup/mongodb/$(date +%Y%m%d)

# Redis backup
redis-cli --rdb /backup/redis/dump-$(date +%Y%m%d).rdb

# Automated backup script
0 2 * * * /scripts/backup_databases.sh
```

---

## 📊 **Monitoring & Observability**

### Application Metrics
- Request/response times
- Error rates
- Active connections
- Database performance
- AI API usage
- Memory and CPU usage

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with dependencies
curl http://localhost:8000/health/detailed

# Metrics endpoint
curl http://localhost:8000/metrics
```

### Logging Configuration
```python
# Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/adwise/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}
```

---

## 🔒 **Security Configuration**

### SSL/TLS Setup
```bash
# Generate SSL certificate (Let's Encrypt)
certbot --nginx -d yourdomain.com

# Or use custom certificates
openssl req -x509 -newkey rsa:4096 -keyout private.key -out certificate.crt -days 365
```

### Security Headers
```python
# Implemented in middleware
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'"
}
```

### Rate Limiting
```python
# API rate limits
RATE_LIMITS = {
    'default': '100/minute',
    'auth': '5/minute',
    'ai_generation': '10/minute'
}
```

---

## 🔧 **Troubleshooting**

### Common Issues

#### 1. Server Won't Start
```bash
# Check port availability
netstat -tulpn | grep :8000

# Check logs
tail -f /var/log/adwise/error.log

# Verify dependencies
pip check
```

#### 2. Database Connection Issues
```bash
# Test MongoDB connection
mongosh "mongodb://user:pass@host:27017/dbname"

# Test Redis connection
redis-cli -h host -p 6379 -a password ping

# Check network connectivity
telnet host 27017
```

#### 3. AI API Issues
```bash
# Test EURI AI connection
curl -H "Authorization: Bearer $EURI_API_KEY" https://api.euri.ai/v1/health

# Check API quota
curl -H "Authorization: Bearer $EURI_API_KEY" https://api.euri.ai/v1/usage
```

#### 4. Performance Issues
```bash
# Monitor resource usage
htop
iotop
nethogs

# Check database performance
mongostat
redis-cli info stats

# Profile application
python -m cProfile -o profile.stats app/main.py
```

### Log Analysis
```bash
# Error analysis
grep "ERROR" /var/log/adwise/app.log | tail -20

# Performance analysis
grep "slow" /var/log/adwise/app.log

# User activity
grep "user_id" /var/log/adwise/access.log | wc -l
```

---

## 🔄 **Maintenance**

### Regular Tasks

#### Daily
- Monitor application health
- Check error logs
- Verify backup completion
- Monitor resource usage

#### Weekly
- Update dependencies
- Clean old logs
- Optimize database
- Review security alerts

#### Monthly
- Security updates
- Performance review
- Capacity planning
- Backup testing

### Update Procedure
```bash
# 1. Backup current state
./scripts/backup_full_system.sh

# 2. Update code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Run migrations
python scripts/migrate_database.py

# 5. Restart services
systemctl restart adwise-ai
systemctl restart nginx

# 6. Verify deployment
curl http://localhost:8000/health
```

### Scaling Considerations
- Horizontal scaling with load balancer
- Database sharding for large datasets
- CDN for static assets
- Caching layer optimization
- Microservices architecture migration

---

## 📞 **Support**

For deployment issues or questions:
- Check the troubleshooting section
- Review application logs
- Consult the API documentation
- Contact the development team

---

**🎯 AdWise AI Campaign Builder - Professional Implementation**
*Comprehensive deployment guide for production-ready AI-powered marketing campaigns*
