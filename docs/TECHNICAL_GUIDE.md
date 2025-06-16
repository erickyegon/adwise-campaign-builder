# 🔧 AdWise AI Technical Documentation

## 🎯 Overview

This technical guide provides comprehensive information for developers, system administrators, and technical teams responsible for maintaining and extending the AdWise AI platform.

---

## 🏗️ System Architecture

### **Application Stack**

**Frontend Layer**:
- **Framework**: React 18.2+ with TypeScript 5.0+
- **Build Tool**: Vite 5.0+ for fast development and production builds
- **Styling**: Tailwind CSS 3.3+ with custom component library
- **State Management**: React Query 4.0+ with Context API
- **Routing**: React Router 6.0+ with lazy loading

**Backend Layer**:
- **API Framework**: FastAPI 0.104+ with async/await patterns
- **Authentication**: JWT with RS256 signing and refresh tokens
- **Validation**: Pydantic models with comprehensive validation
- **Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Testing**: Pytest with 95%+ coverage

**Data Layer**:
- **Primary Database**: MongoDB 6.0+ with Beanie ODM
- **Analytics Database**: PostgreSQL 15+ with SQLAlchemy
- **Cache Layer**: Redis 7.0+ with intelligent caching strategies
- **Search Engine**: Elasticsearch 8.0+ for full-text search

**AI/ML Integration**:
- **EURI AI**: Primary content generation service
- **LangChain**: Workflow orchestration and chaining
- **LangGraph**: State-based AI workflow management
- **LangServe**: AI service API deployment

---

## 🚀 Development Environment Setup

### **Prerequisites**

```bash
# System Requirements
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+
- PostgreSQL 15+
- Redis 7.0+
- Docker 24.0+ (optional)
```

### **Backend Setup**

```bash
# 1. Create virtual environment
python -m venv adwise_env
source adwise_env/bin/activate  # Linux/Mac
# or
.\adwise_env\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env
# Edit .env with your configuration

# 4. Database setup
python scripts/setup_databases.py

# 5. Run development server
uvicorn app.main:app --host 127.0.0.1 --port 8007 --reload
```

### **Frontend Setup**

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Environment configuration
cp .env.example .env.local
# Edit .env.local with your configuration

# 4. Run development server
npm run dev
```

---

## 🗄️ Database Architecture

### **MongoDB Schema Design**

**Collections Structure**:

```python
# Users Collection
{
  "_id": ObjectId,
  "email": str,
  "username": str,
  "password_hash": str,
  "role": str,  # admin, manager, creator, analyst
  "profile": {
    "first_name": str,
    "last_name": str,
    "avatar_url": str,
    "timezone": str
  },
  "settings": dict,
  "created_at": datetime,
  "updated_at": datetime,
  "last_login": datetime
}

# Campaigns Collection
{
  "_id": ObjectId,
  "name": str,
  "description": str,
  "status": str,  # draft, review, active, paused, completed
  "budget": {
    "total": float,
    "daily": float,
    "spent": float
  },
  "targeting": {
    "demographics": dict,
    "interests": list,
    "locations": list,
    "custom_audiences": list
  },
  "platforms": list,  # facebook, google, linkedin, twitter
  "content": {
    "headlines": list,
    "descriptions": list,
    "images": list,
    "videos": list
  },
  "performance": {
    "impressions": int,
    "clicks": int,
    "conversions": int,
    "spend": float,
    "ctr": float,
    "cpc": float,
    "roas": float
  },
  "schedule": {
    "start_date": datetime,
    "end_date": datetime,
    "timezone": str
  },
  "team": {
    "owner": ObjectId,
    "collaborators": list,
    "approvers": list
  },
  "created_at": datetime,
  "updated_at": datetime
}
```

### **PostgreSQL Analytics Schema**

```sql
-- Campaign Performance Table
CREATE TABLE campaign_performance (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(24) NOT NULL,
    date DATE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    conversions BIGINT DEFAULT 0,
    spend DECIMAL(10,2) DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, date, platform)
);

-- User Activity Table
CREATE TABLE user_activity (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(24) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(24),
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX idx_campaign_performance_date ON campaign_performance(date);
CREATE INDEX idx_campaign_performance_campaign ON campaign_performance(campaign_id);
CREATE INDEX idx_user_activity_user ON user_activity(user_id);
CREATE INDEX idx_user_activity_date ON user_activity(created_at);
```

---

## 🔌 API Documentation

### **Authentication Endpoints**

```python
# POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "secure_password"
}
# Response: {"access_token": "jwt_token", "refresh_token": "refresh_jwt"}

# POST /api/v1/auth/refresh
{
  "refresh_token": "refresh_jwt_token"
}
# Response: {"access_token": "new_jwt_token"}

# POST /api/v1/auth/logout
# Headers: Authorization: Bearer jwt_token
# Response: {"message": "Successfully logged out"}
```

### **Campaign Management Endpoints**

```python
# GET /api/v1/campaigns
# Query params: status, platform, limit, offset
# Response: {"campaigns": [...], "total": int, "page": int}

# POST /api/v1/campaigns
{
  "name": "Summer Sale Campaign",
  "description": "Q3 promotional campaign",
  "budget": {"total": 10000, "daily": 500},
  "targeting": {...},
  "platforms": ["facebook", "google"],
  "schedule": {"start_date": "2024-07-01", "end_date": "2024-07-31"}
}

# GET /api/v1/campaigns/{campaign_id}
# Response: Complete campaign object with performance data

# PUT /api/v1/campaigns/{campaign_id}
# Request: Partial campaign update object
# Response: Updated campaign object

# DELETE /api/v1/campaigns/{campaign_id}
# Response: {"message": "Campaign deleted successfully"}
```

### **AI Content Generation Endpoints**

```python
# POST /api/v1/ai/generate-content
{
  "content_type": "ad_headline",  # ad_headline, ad_copy, social_post
  "context": {
    "product": "Wireless Headphones",
    "audience": "Tech enthusiasts aged 25-40",
    "tone": "professional",
    "key_points": ["noise cancellation", "long battery life"]
  },
  "options": {
    "count": 5,
    "max_length": 100
  }
}
# Response: {"generated_content": [...], "usage": {...}}

# POST /api/v1/ai/optimize-campaign
{
  "campaign_id": "campaign_id",
  "optimization_goals": ["ctr", "conversions"],
  "constraints": {"budget_increase_limit": 0.2}
}
# Response: {"recommendations": [...], "estimated_impact": {...}}
```

---

## 🔒 Security Implementation

### **Authentication & Authorization**

```python
# JWT Token Configuration
JWT_ALGORITHM = "RS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# Role-Based Access Control
PERMISSIONS = {
    "admin": ["*"],
    "manager": ["campaigns:*", "users:read", "analytics:*"],
    "creator": ["campaigns:read", "campaigns:create", "content:*"],
    "analyst": ["campaigns:read", "analytics:*", "reports:*"]
}

# Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}
```

### **Data Encryption**

```python
# Database Encryption
MONGODB_ENCRYPTION_KEY = os.getenv("MONGODB_ENCRYPTION_KEY")
POSTGRES_SSL_MODE = "require"

# API Key Encryption
from cryptography.fernet import Fernet
cipher_suite = Fernet(ENCRYPTION_KEY)
encrypted_api_key = cipher_suite.encrypt(api_key.encode())
```

---

## 📊 Performance Optimization

### **Database Optimization**

```python
# MongoDB Indexes
db.campaigns.create_index([("status", 1), ("created_at", -1)])
db.campaigns.create_index([("team.owner", 1)])
db.campaigns.create_index([("platforms", 1), ("status", 1)])

# PostgreSQL Query Optimization
EXPLAIN ANALYZE SELECT 
    campaign_id,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(spend) as total_spend
FROM campaign_performance 
WHERE date >= '2024-01-01' 
GROUP BY campaign_id;
```

### **Caching Strategies**

```python
# Redis Caching Implementation
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached_result = redis_client.get(cache_key)
            
            if cached_result:
                return json.loads(cached_result)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=1800)
async def get_campaign_analytics(campaign_id: str):
    # Expensive analytics calculation
    pass
```

---

## 🚀 Deployment & DevOps

### **Docker Configuration**

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8007

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### **Docker Compose**

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8007:8007"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/adwise
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3002:80"
    depends_on:
      - backend

  mongo:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: adwise_analytics
      POSTGRES_USER: adwise
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mongo_data:
  postgres_data:
```

---

## 🔍 Monitoring & Logging

### **Application Monitoring**

```python
# Prometheus Metrics
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

### **Structured Logging**

```python
import structlog

logger = structlog.get_logger()

# Usage in application
logger.info(
    "Campaign created",
    campaign_id=campaign.id,
    user_id=current_user.id,
    campaign_name=campaign.name,
    budget=campaign.budget.total
)
```
