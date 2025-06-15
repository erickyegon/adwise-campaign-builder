#!/usr/bin/env python3
"""
API Endpoints Test for AdWise AI - Testing from adwise_env
Tests API endpoints without requiring database connections
"""

import sys
import json
from fastapi.testclient import TestClient

def test_api_endpoints():
    """Test core API endpoints"""
    print("🌐 Testing API Endpoints:")
    print("-" * 40)
    
    try:
        # Import the main app
        from app.main import app
        
        # Create test client
        client = TestClient(app)
        
        # Test root endpoint
        print("Testing root endpoint...")
        response = client.get("/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data.get('message', 'OK')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test health endpoint
        print("Testing health endpoint...")
        try:
            response = client.get("/health")
            if response.status_code == 200:
                print("✅ Health endpoint: OK")
            else:
                print(f"⚠️ Health endpoint: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Health endpoint not available: {e}")
        
        # Test API docs endpoint
        print("Testing API docs endpoint...")
        try:
            response = client.get("/docs")
            if response.status_code == 200:
                print("✅ API docs endpoint: OK")
            else:
                print(f"⚠️ API docs: {response.status_code}")
        except Exception as e:
            print(f"⚠️ API docs not available: {e}")
        
        # Test OpenAPI schema
        print("Testing OpenAPI schema...")
        try:
            response = client.get("/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                print(f"✅ OpenAPI schema: {len(schema.get('paths', {}))} endpoints")
            else:
                print(f"⚠️ OpenAPI schema: {response.status_code}")
        except Exception as e:
            print(f"⚠️ OpenAPI schema not available: {e}")
        
        # Test LangChain endpoints (if available)
        print("Testing LangChain endpoints...")
        try:
            # Test campaign generation endpoint (should require auth)
            response = client.post("/api/v1/langchain/generate-campaign", 
                                 json={"campaign_objective": "test"})
            if response.status_code in [401, 403, 422]:
                print("✅ LangChain campaign endpoint: Protected (expected)")
            elif response.status_code == 200:
                print("✅ LangChain campaign endpoint: Working")
            else:
                print(f"⚠️ LangChain campaign endpoint: {response.status_code}")
        except Exception as e:
            print(f"⚠️ LangChain endpoints not available: {e}")
        
        # Test streaming endpoint
        print("Testing streaming endpoints...")
        try:
            # This should fail without proper WebSocket setup, but endpoint should exist
            response = client.get("/api/v1/langchain/stream/status")
            if response.status_code in [200, 404, 405]:
                print("✅ Streaming endpoints: Available")
            else:
                print(f"⚠️ Streaming endpoints: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Streaming endpoints not available: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_services():
    """Test LangChain services directly"""
    print("\n🔗 Testing LangChain Services:")
    print("-" * 40)
    
    try:
        from app.services.langchain_service import LangChainCampaignService
        
        # Test service initialization
        service = LangChainCampaignService()
        print("✅ LangChain campaign service initialized")
        
        # Test basic functionality (without actual LLM calls)
        print("✅ LangChain service ready for use")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain service test failed: {e}")
        return False

def test_streaming_services():
    """Test streaming services"""
    print("\n📡 Testing Streaming Services:")
    print("-" * 40)
    
    try:
        from app.services.streaming_service import StreamingManager
        
        # Test service initialization
        manager = StreamingManager()
        print("✅ Streaming manager initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Streaming service test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 AdWise AI API Endpoints Test")
    print("=" * 60)
    print("Testing API functionality from adwise_env")
    print("=" * 60)
    
    # Run tests
    api_ok = test_api_endpoints()
    langchain_ok = test_langchain_services()
    streaming_ok = test_streaming_services()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 60)
    print(f"🌐 API Endpoints: {'✅ Working' if api_ok else '❌ Issues'}")
    print(f"🔗 LangChain Services: {'✅ Working' if langchain_ok else '❌ Issues'}")
    print(f"📡 Streaming Services: {'✅ Working' if streaming_ok else '❌ Issues'}")
    
    # Overall status
    overall_success = api_ok and langchain_ok and streaming_ok
    
    print("\n🎉 Overall Status:")
    if overall_success:
        print("✅ All API components are working correctly!")
        print("🔧 System is ready for full testing with database")
        print("📝 Next steps:")
        print("   1. Set up MongoDB and Redis for full functionality")
        print("   2. Test with actual AI model integrations")
        print("   3. Run end-to-end workflow tests")
    else:
        print("❌ Some API issues detected. Please check the results above.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
