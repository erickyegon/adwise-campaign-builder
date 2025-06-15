# 🧪 AdWise AI Digital Marketing Campaign Builder - Comprehensive Testing Guide

## 📋 **Table of Contents**
1. [Testing Overview](#testing-overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [API Testing](#api-testing)
6. [End-to-End Testing](#end-to-end-testing)
7. [Performance Testing](#performance-testing)
8. [Security Testing](#security-testing)
9. [AI Integration Testing](#ai-integration-testing)
10. [Continuous Integration](#continuous-integration)

---

## 🎯 **Testing Overview**

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **API Tests**: Endpoint functionality testing
- **E2E Tests**: Complete user workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability assessment
- **AI Tests**: EURI AI integration testing

### Test Coverage Goals
- **Unit Tests**: >90% code coverage
- **Integration Tests**: All service interactions
- **API Tests**: All endpoints and error cases
- **E2E Tests**: Critical user journeys
- **Performance Tests**: Expected load scenarios

---

## 🛠️ **Test Environment Setup**

### 1. Install Testing Dependencies
```bash
# Activate virtual environment
adwise_env\Scripts\activate  # Windows
source adwise_env/bin/activate  # Linux/Mac

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx pytest-mock faker

# Install additional testing tools
pip install locust selenium webdriver-manager
```

### 2. Test Configuration
```bash
# Create test environment file
cp .env.development .env.test

# Configure test-specific settings
# - Use test databases
# - Mock external services
# - Enable debug logging
# - Disable rate limiting
```

### 3. Test Database Setup
```bash
# Start test databases
docker-compose -f docker-compose.test.yml up -d

# Initialize test data
python scripts/setup_test_data.py
```

---

## 🔬 **Unit Testing**

### Running Unit Tests
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_campaign_service.py -v

# Run specific test
pytest tests/unit/test_campaign_service.py::test_create_campaign -v
```

### Unit Test Examples

#### Campaign Service Tests
```python
# tests/unit/test_campaign_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.campaign_service import CampaignService
from app.models.campaign import Campaign

@pytest.fixture
def campaign_service():
    return CampaignService()

@pytest.mark.asyncio
async def test_create_campaign(campaign_service):
    """Test campaign creation"""
    campaign_data = {
        "title": "Test Campaign",
        "description": "Test Description",
        "target_audience": "Young Adults",
        "budget": 1000.0
    }
    
    with patch('app.services.campaign_service.Campaign.save') as mock_save:
        mock_save.return_value = Campaign(**campaign_data)
        
        result = await campaign_service.create_campaign(campaign_data)
        
        assert result.title == "Test Campaign"
        assert result.budget == 1000.0
        mock_save.assert_called_once()

@pytest.mark.asyncio
async def test_create_campaign_validation_error(campaign_service):
    """Test campaign creation with invalid data"""
    invalid_data = {
        "title": "",  # Empty title should fail
        "budget": -100  # Negative budget should fail
    }
    
    with pytest.raises(ValueError):
        await campaign_service.create_campaign(invalid_data)
```

#### AI Service Tests
```python
# tests/unit/test_ai_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai_service import AIService

@pytest.fixture
def ai_service():
    return AIService()

@pytest.mark.asyncio
async def test_generate_ad_content(ai_service):
    """Test AI content generation"""
    prompt = "Create an ad for eco-friendly products"
    
    with patch('app.integrations.euri.euri_client.EuriaiClient.generate') as mock_generate:
        mock_generate.return_value = {
            "content": "Go green with our eco-friendly products!",
            "tone": "enthusiastic",
            "length": 45
        }
        
        result = await ai_service.generate_ad_content(prompt)
        
        assert "eco-friendly" in result["content"]
        assert result["tone"] == "enthusiastic"
        mock_generate.assert_called_once()
```

---

## 🔗 **Integration Testing**

### Running Integration Tests
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run database integration tests
pytest tests/integration/test_database_integration.py -v

# Run AI integration tests
pytest tests/integration/test_ai_integration.py -v
```

### Integration Test Examples

#### Database Integration Tests
```python
# tests/integration/test_database_integration.py
import pytest
from app.core.database.mongodb import get_database_manager
from app.models.campaign import Campaign

@pytest.mark.asyncio
async def test_campaign_crud_operations():
    """Test complete CRUD operations for campaigns"""
    db_manager = await get_database_manager()
    
    # Create
    campaign_data = {
        "title": "Integration Test Campaign",
        "description": "Test Description",
        "user_id": "test_user_123",
        "status": "draft"
    }
    
    campaign = Campaign(**campaign_data)
    await campaign.save()
    
    assert campaign.id is not None
    
    # Read
    retrieved = await Campaign.get(campaign.id)
    assert retrieved.title == "Integration Test Campaign"
    
    # Update
    retrieved.status = "active"
    await retrieved.save()
    
    updated = await Campaign.get(campaign.id)
    assert updated.status == "active"
    
    # Delete
    await updated.delete()
    
    deleted = await Campaign.get(campaign.id)
    assert deleted is None
```

#### AI Integration Tests
```python
# tests/integration/test_ai_integration.py
import pytest
from app.integrations.euri.euri_client import get_euri_client

@pytest.mark.asyncio
async def test_euri_ai_health_check():
    """Test EURI AI service health"""
    client = await get_euri_client()
    
    health_status = await client.health_check()
    assert health_status is not None
    
@pytest.mark.asyncio
async def test_euri_ai_content_generation():
    """Test actual AI content generation"""
    client = await get_euri_client()
    
    prompt = "Generate a marketing slogan for a coffee shop"
    response = await client.generate_content(prompt)
    
    assert response is not None
    assert len(response.get("content", "")) > 0
```

---

## 🌐 **API Testing**

### Running API Tests
```bash
# Run all API tests
pytest tests/api/ -v

# Run specific endpoint tests
pytest tests/api/test_campaign_endpoints.py -v

# Run with test client
pytest tests/api/ --tb=short
```

### API Test Examples

#### Campaign API Tests
```python
# tests/api/test_campaign_endpoints.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_campaign_endpoint():
    """Test campaign creation endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        campaign_data = {
            "title": "API Test Campaign",
            "description": "Test Description",
            "target_audience": "Tech Enthusiasts",
            "budget": 2000.0
        }
        
        response = await client.post("/api/v1/campaigns", json=campaign_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Test Campaign"
        assert data["budget"] == 2000.0

@pytest.mark.asyncio
async def test_get_campaigns_endpoint():
    """Test campaigns listing endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/campaigns")
        
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert isinstance(data["campaigns"], list)

@pytest.mark.asyncio
async def test_campaign_not_found():
    """Test campaign not found error"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/campaigns/nonexistent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
```

#### Health Check Tests
```python
# tests/api/test_health_endpoints.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    """Test basic health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AdWise AI Campaign Builder"

@pytest.mark.asyncio
async def test_detailed_health_check():
    """Test detailed health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "features" in data
```

---

## 🎭 **End-to-End Testing**

### E2E Test Setup
```bash
# Install Selenium and WebDriver
pip install selenium webdriver-manager

# Download browser drivers automatically
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### E2E Test Examples

#### User Journey Tests
```python
# tests/e2e/test_user_journey.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for CI
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    yield driver
    driver.quit()

def test_campaign_creation_flow(driver):
    """Test complete campaign creation user journey"""
    # Navigate to application
    driver.get("http://localhost:8000")
    
    # Wait for page to load
    wait = WebDriverWait(driver, 10)
    
    # Click create campaign button
    create_button = wait.until(
        EC.element_to_be_clickable((By.ID, "create-campaign-btn"))
    )
    create_button.click()
    
    # Fill campaign form
    title_input = driver.find_element(By.ID, "campaign-title")
    title_input.send_keys("E2E Test Campaign")
    
    description_input = driver.find_element(By.ID, "campaign-description")
    description_input.send_keys("This is an end-to-end test campaign")
    
    # Submit form
    submit_button = driver.find_element(By.ID, "submit-campaign")
    submit_button.click()
    
    # Verify campaign was created
    success_message = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
    )
    assert "Campaign created successfully" in success_message.text
```

---

## ⚡ **Performance Testing**

### Load Testing with Locust
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class AdWiseUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup user session"""
        self.client.headers.update({
            "Content-Type": "application/json"
        })
    
    @task(3)
    def view_campaigns(self):
        """Test campaigns listing performance"""
        self.client.get("/api/v1/campaigns")
    
    @task(2)
    def view_campaign_details(self):
        """Test campaign details performance"""
        self.client.get("/api/v1/campaigns/test-campaign-id")
    
    @task(1)
    def create_campaign(self):
        """Test campaign creation performance"""
        campaign_data = {
            "title": f"Load Test Campaign {self.user_id}",
            "description": "Performance test campaign",
            "budget": 1000.0
        }
        self.client.post("/api/v1/campaigns", json=campaign_data)
    
    @task(1)
    def health_check(self):
        """Test health endpoint performance"""
        self.client.get("/health")
```

### Running Performance Tests
```bash
# Install Locust
pip install locust

# Run load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Run headless load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 5m --headless
```

---

## 🔒 **Security Testing**

### Security Test Examples
```python
# tests/security/test_security.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_sql_injection_protection():
    """Test SQL injection protection"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        malicious_input = "'; DROP TABLE campaigns; --"
        
        response = await client.get(f"/api/v1/campaigns?search={malicious_input}")
        
        # Should not return 500 error or expose database errors
        assert response.status_code in [200, 400, 422]

@pytest.mark.asyncio
async def test_xss_protection():
    """Test XSS protection"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        xss_payload = "<script>alert('xss')</script>"
        
        campaign_data = {
            "title": xss_payload,
            "description": "Test campaign"
        }
        
        response = await client.post("/api/v1/campaigns", json=campaign_data)
        
        # Should sanitize or reject malicious input
        if response.status_code == 201:
            data = response.json()
            assert "<script>" not in data["title"]

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test API rate limiting"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make multiple rapid requests
        responses = []
        for _ in range(150):  # Exceed rate limit
            response = await client.get("/api/v1/campaigns")
            responses.append(response.status_code)
        
        # Should eventually return 429 (Too Many Requests)
        assert 429 in responses
```

---

## 🤖 **AI Integration Testing**

### AI Service Tests
```python
# tests/ai/test_ai_integration.py
import pytest
from app.services.ai_service import AIService
from app.integrations.euri.euri_client import get_euri_client

@pytest.mark.asyncio
async def test_ai_content_generation_quality():
    """Test AI content generation quality"""
    ai_service = AIService()
    
    prompt = "Create a professional marketing email for a luxury watch brand"
    
    result = await ai_service.generate_content(prompt)
    
    # Quality checks
    assert len(result["content"]) > 100  # Sufficient length
    assert "luxury" in result["content"].lower()  # Relevant content
    assert result["tone"] in ["professional", "elegant", "sophisticated"]
    
@pytest.mark.asyncio
async def test_ai_response_time():
    """Test AI service response time"""
    import time
    
    ai_service = AIService()
    
    start_time = time.time()
    await ai_service.generate_content("Quick test prompt")
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 30  # Should respond within 30 seconds

@pytest.mark.asyncio
async def test_ai_error_handling():
    """Test AI service error handling"""
    ai_service = AIService()
    
    # Test with invalid/empty prompt
    with pytest.raises(ValueError):
        await ai_service.generate_content("")
    
    # Test with extremely long prompt
    long_prompt = "test " * 10000
    result = await ai_service.generate_content(long_prompt)
    
    # Should handle gracefully or truncate
    assert result is not None
```

---

## 🔄 **Continuous Integration**

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:5.0
        ports:
          - 27017:27017
      
      redis:
        image: redis:6.0
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements.test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=app --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Run API tests
      run: |
        pytest tests/api/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Test Commands Summary
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/api/          # API tests
pytest tests/e2e/          # End-to-end tests

# Run performance tests
locust -f tests/performance/locustfile.py

# Run security tests
pytest tests/security/

# Generate test report
pytest --html=report.html --self-contained-html
```

---

## 📊 **Test Reporting**

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Generate terminal coverage report
pytest --cov=app --cov-report=term-missing

# Generate XML coverage report (for CI)
pytest --cov=app --cov-report=xml
```

### Test Metrics
- **Code Coverage**: Target >90%
- **Test Execution Time**: <5 minutes for full suite
- **API Response Time**: <200ms for 95th percentile
- **Load Test**: Handle 100 concurrent users
- **Security**: Zero critical vulnerabilities

---

**🎯 AdWise AI Campaign Builder - Professional Testing Implementation**
*Comprehensive testing strategy for production-ready AI-powered marketing campaigns*
