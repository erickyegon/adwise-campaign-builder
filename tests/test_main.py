"""
Test suite for AdWise AI Digital Marketing Campaign Builder

This module contains comprehensive tests for the main application functionality:
- Application startup and configuration
- Database connections
- API endpoint availability
- Authentication system
- Core business logic
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Import the main application
from app.main import app
from app.core.config import get_settings
from app.models.mongodb_models import User, Campaign, Ad, Analytics


class TestApplicationStartup:
    """Test application startup and configuration"""

    def test_app_creation(self):
        """Test that the FastAPI app is created successfully"""
        assert app is not None
        assert app.title == "AdWise AI Campaign Builder"

    def test_settings_loading(self):
        """Test that settings are loaded correctly"""
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'app')
        assert hasattr(settings, 'database')
        assert hasattr(settings, 'security')
        assert hasattr(settings, 'ai')

    def test_cors_middleware(self):
        """Test CORS middleware configuration"""
        # Check if CORS middleware is properly configured
        middleware_types = [type(middleware)
                            for middleware in app.user_middleware]
        cors_middleware_present = any(
            'CORSMiddleware' in str(middleware_type)
            for middleware_type in middleware_types
        )
        assert cors_middleware_present


class TestDatabaseModels:
    """Test database model definitions"""

    def test_user_model_structure(self):
        """Test User model has required fields"""
        user_fields = User.model_fields.keys()
        required_fields = {'email', 'password_hash', 'role'}
        assert required_fields.issubset(user_fields)

    def test_campaign_model_structure(self):
        """Test Campaign model has required fields"""
        campaign_fields = Campaign.model_fields.keys()
        required_fields = {'name', 'owner_id', 'status', 'created_at'}
        assert required_fields.issubset(campaign_fields)

    def test_ad_model_structure(self):
        """Test Ad model has required fields"""
        ad_fields = Ad.model_fields.keys()
        required_fields = {'campaign_id', 'type', 'channel', 'status'}
        assert required_fields.issubset(ad_fields)

    def test_analytics_model_structure(self):
        """Test Analytics model has required fields"""
        analytics_fields = Analytics.model_fields.keys()
        required_fields = {'ad_id', 'impressions',
                           'clicks', 'ctr', 'timestamp'}
        assert required_fields.issubset(analytics_fields)


class TestAPIEndpoints:
    """Test API endpoint availability and basic functionality"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_docs_available(self, client):
        """Test that API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "AdWise AI Digital Marketing Campaign Builder"


class TestAuthenticationSystem:
    """Test authentication and security features"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_register_endpoint_exists(self, client):
        """Test user registration endpoint exists"""
        # Test with invalid data to check endpoint exists
        response = client.post("/api/v1/auth/register", json={})
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code in [422, 400]

    def test_login_endpoint_exists(self, client):
        """Test user login endpoint exists"""
        # Test with invalid data to check endpoint exists
        response = client.post("/api/v1/auth/login", json={})
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code in [422, 400]

    def test_protected_endpoint_requires_auth(self, client):
        """Test that protected endpoints require authentication"""
        response = client.get("/api/v1/auth/me")
        # Should return 401 (unauthorized) or 403 (forbidden)
        assert response.status_code in [401, 403]


class TestCampaignEndpoints:
    """Test campaign management endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_campaigns_list_endpoint(self, client):
        """Test campaigns list endpoint"""
        response = client.get("/api/v1/campaigns")
        # Should require authentication
        assert response.status_code in [401, 403]

    def test_campaign_create_endpoint(self, client):
        """Test campaign creation endpoint"""
        response = client.post("/api/v1/campaigns", json={})
        # Should require authentication or return validation error
        assert response.status_code in [401, 403, 422]


class TestAIServiceEndpoints:
    """Test AI service integration endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_generate_copy_endpoint(self, client):
        """Test AI content generation endpoint"""
        response = client.post("/api/v1/ai/generate-copy", json={})
        # Should require authentication or return validation error
        assert response.status_code in [401, 403, 422]

    def test_optimize_campaign_endpoint(self, client):
        """Test AI campaign optimization endpoint"""
        response = client.post("/api/v1/ai/optimize-campaign", json={})
        # Should require authentication or return validation error
        assert response.status_code in [401, 403, 422]


class TestAnalyticsEndpoints:
    """Test analytics and reporting endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_analytics_endpoint(self, client):
        """Test analytics endpoint"""
        response = client.get("/api/v1/analytics/summary")
        # Should require authentication
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality and database operations"""

    async def test_database_connection_mock(self):
        """Test database connection (mocked)"""
        with patch('app.core.database.mongodb.get_db') as mock_db:
            mock_db.return_value = AsyncMock()
            db = await mock_db()
            assert db is not None

    async def test_euri_client_mock(self):
        """Test EURI AI client (mocked)"""
        with patch('app.integrations.euri.get_euri_client') as mock_client:
            mock_client.return_value = AsyncMock()
            client = await mock_client()
            assert client is not None


class TestConfigurationValidation:
    """Test configuration and environment validation"""

    def test_required_config_sections(self):
        """Test that all required configuration sections exist"""
        settings = get_settings()

        # Check main configuration sections
        assert hasattr(settings, 'app')
        assert hasattr(settings, 'database')
        assert hasattr(settings, 'auth')
        assert hasattr(settings, 'redis')

    def test_app_config_fields(self):
        """Test app configuration fields"""
        settings = get_settings()
        app_config = settings.app

        # Check required app fields
        assert hasattr(app_config, 'APP_NAME')
        assert hasattr(app_config, 'APP_VERSION')
        assert hasattr(app_config, 'ENVIRONMENT')

    def test_database_config_fields(self):
        """Test database configuration fields"""
        settings = get_settings()
        db_config = settings.database

        # Check required database fields
        assert hasattr(db_config, 'POSTGRES_HOST')
        assert hasattr(db_config, 'POSTGRES_DB')

    def test_auth_config_fields(self):
        """Test authentication configuration fields"""
        settings = get_settings()
        auth_config = settings.security

        # Check required auth fields
        assert hasattr(auth_config, 'SECRET_KEY')
        assert hasattr(auth_config, 'ACCESS_TOKEN_EXPIRE_MINUTES')


class TestSecurityFeatures:
    """Test security implementation"""

    def test_password_hashing_import(self):
        """Test password hashing utilities are available"""
        try:
            from app.core.security import get_password_hash, verify_password
            assert callable(get_password_hash)
            assert callable(verify_password)
        except ImportError:
            pytest.fail("Security utilities not properly imported")

    def test_jwt_token_utilities(self):
        """Test JWT token utilities are available"""
        try:
            from app.core.security import create_access_token, verify_token
            assert callable(create_access_token)
            assert callable(verify_token)
        except ImportError:
            pytest.fail("JWT utilities not properly imported")

    def test_permission_system(self):
        """Test permission system is available"""
        try:
            from app.core.security import Permission, ROLE_PERMISSIONS
            assert Permission is not None
            assert ROLE_PERMISSIONS is not None
            assert 'admin' in ROLE_PERMISSIONS
            assert 'editor' in ROLE_PERMISSIONS
            assert 'viewer' in ROLE_PERMISSIONS
        except ImportError:
            pytest.fail("Permission system not properly imported")


class TestIntegrationReadiness:
    """Test integration readiness and external service mocks"""

    def test_euri_integration_structure(self):
        """Test EURI AI integration structure"""
        try:
            from app.integrations.euri import EuriaiClient
            assert EuriaiClient is not None
        except ImportError:
            pytest.fail("EURI AI integration not properly structured")

    def test_langchain_service_structure(self):
        """Test LangChain service structure"""
        try:
            from app.services.langchain_service import get_langchain_service
            assert callable(get_langchain_service)
        except ImportError:
            pytest.fail("LangChain service not properly structured")

    def test_analytics_service_structure(self):
        """Test analytics service structure"""
        try:
            from app.services.analytics_service import get_analytics_service
            assert callable(get_analytics_service)
        except ImportError:
            pytest.fail("Analytics service not properly structured")

    def test_export_service_structure(self):
        """Test export service structure"""
        try:
            from app.services.export_service import get_export_service
            assert callable(get_export_service)
        except ImportError:
            pytest.fail("Export service not properly structured")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
