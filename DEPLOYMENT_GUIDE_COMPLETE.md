# 🚀 Complete Deployment Guide - AdWise AI Platform

This guide covers the complete deployment of both the backend API and frontend React application for the AdWise AI Digital Marketing Campaign Builder.

## 📋 Prerequisites

### System Requirements
- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **MongoDB** (local or cloud instance)
- **Redis** (optional, for caching)
- **Git** (for version control)

### Development Tools
- **Code Editor**: VS Code, PyCharm, or similar
- **Terminal**: Command line access
- **Browser**: Modern browser for testing

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   React App     │◄──►│   FastAPI       │◄──►│   MongoDB       │
│   Port 3002     │    │   Port 8002     │    │   Port 27017    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │     Redis       │
                       │   Port 6379     │
                       └─────────────────┘
```

## 🔧 Backend Deployment

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd "AdWise AI Digital Marketing Campaign Builder"

# Create Python virtual environment
python -m venv adwise_env

# Activate virtual environment
# Windows:
adwise_env\Scripts\activate
# macOS/Linux:
source adwise_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:

```env
# Application Settings
ENVIRONMENT=production
DEBUG=false
HOST=127.0.0.1
PORT=8002
LOG_LEVEL=info

# Database Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=adwise_ai
REDIS_URL=redis://localhost:6379

# AI Integration
EURI_API_KEY=your_euri_api_key_here
EURI_API_URL=https://api.euri.ai

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### 3. Database Setup

```bash
# Start MongoDB (if using local instance)
mongod --dbpath /path/to/your/db

# Start Redis (if using local instance)
redis-server
```

### 4. Start Backend Server

```bash
# Using the production server script
python run_production_server.py

# Or using uvicorn directly
uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

### 5. Verify Backend

- **API Health**: http://127.0.0.1:8002/health
- **API Docs**: http://127.0.0.1:8002/docs
- **API Root**: http://127.0.0.1:8002/api/v1/

## 🎨 Frontend Deployment

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
# Install all dependencies
npm install

# Verify installation
npm list --depth=0
```

### 3. Configuration

Create a `.env.local` file in the frontend directory:

```env
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8002
VITE_API_TIMEOUT=10000

# Application Configuration
VITE_APP_NAME=AdWise AI
VITE_APP_VERSION=1.0.0
```

### 4. Fix Tailwind CSS Configuration

Ensure the PostCSS configuration is correct:

```javascript
// postcss.config.js
import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'

export default {
  plugins: [
    tailwindcss,
    autoprefixer,
  ],
}
```

### 5. Start Frontend Development Server

```bash
# Start development server
npm run dev

# The server will start on the next available port (usually 3000, 3001, or 3002)
```

### 6. Verify Frontend

- **Frontend App**: http://localhost:3002 (or displayed port)
- **Dashboard**: Navigate to the dashboard page
- **API Integration**: Check that data loads from backend

## 🔄 Full Stack Integration

### 1. Start Both Services

```bash
# Terminal 1: Backend
cd "AdWise AI Digital Marketing Campaign Builder"
adwise_env\Scripts\activate
python run_production_server.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Verify Integration

1. **Backend Health**: Visit http://127.0.0.1:8002/health
2. **Frontend App**: Visit http://localhost:3002
3. **API Calls**: Check browser network tab for successful API calls
4. **Data Flow**: Verify data loads in frontend from backend

## 🚀 Production Deployment

### Backend Production

```bash
# Set production environment
export ENVIRONMENT=production

# Install production dependencies only
pip install --no-dev -r requirements.txt

# Run with production settings
python run_production_server.py
```

### Frontend Production

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Serve with a production server (e.g., nginx, Apache)
```

## 🐳 Docker Deployment (Optional)

### 1. Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["python", "run_production_server.py"]
```

### 2. Frontend Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 3. Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8002:8002"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  mongo:
    image: mongo:5
    ports:
      - "27017:27017"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
```

## 🔍 Troubleshooting

### Common Backend Issues

1. **Port already in use**:
   ```bash
   # Find process using port 8002
   netstat -ano | findstr :8002
   # Kill the process or use a different port
   ```

2. **MongoDB connection failed**:
   - Verify MongoDB is running
   - Check connection string in .env
   - Ensure database permissions

3. **EURI AI API errors**:
   - Verify API key in .env
   - Check API quota and limits
   - Review error logs

### Common Frontend Issues

1. **Tailwind CSS not working**:
   ```bash
   # Reinstall Tailwind dependencies
   npm uninstall tailwindcss postcss autoprefixer
   npm install tailwindcss@latest postcss@latest autoprefixer@latest
   ```

2. **API calls failing**:
   - Verify backend is running on port 8002
   - Check proxy configuration in vite.config.ts
   - Review browser console for CORS errors

3. **Build errors**:
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

## 📊 Health Monitoring

### Backend Health Checks

- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /health/detailed`
- **Dependencies**: `GET /health/dependencies`
- **Metrics**: `GET /health/metrics`

### Frontend Monitoring

- **Build Status**: Check for TypeScript errors
- **Bundle Size**: Monitor with `npm run analyze`
- **Performance**: Use browser dev tools
- **Error Tracking**: Monitor console errors

## 🔒 Security Considerations

### Backend Security

- Use environment variables for secrets
- Enable HTTPS in production
- Implement rate limiting
- Regular security updates

### Frontend Security

- Sanitize user inputs
- Use HTTPS for API calls
- Implement CSP headers
- Regular dependency updates

## 📚 Additional Resources

- **Backend API Docs**: http://127.0.0.1:8002/docs
- **Frontend README**: ./frontend/README.md
- **Main README**: ./README.md
- **Issues Log**: ./COMPREHENSIVE_ISSUES_LOG.md

---

**🎉 Congratulations! Your AdWise AI platform is now fully deployed and operational!**
