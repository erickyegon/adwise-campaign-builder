#!/usr/bin/env python3
"""
AdWise AI Digital Marketing Campaign Builder - Comprehensive Test Suite
Testing from adwise_env virtual environment
"""

import sys
import traceback
from fastapi.testclient import TestClient

def test_imports():
    """Test all critical imports"""
    print("🔧 Testing imports from adwise_env:")
    print("-" * 40)
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("langchain", "LangChain"),
        ("langchain_core", "LangChain Core"),
        ("langchain_community", "LangChain Community"),
        ("euriai", "EURI AI"),
        ("beanie", "Beanie ODM"),
        ("motor", "Motor (MongoDB)"),
        ("redis", "Redis"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pymongo", "PyMongo"),
    ]
    
    results = []
    for module_name, display_name in imports_to_test:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "Available")
            print(f"✅ {display_name}: {version}")
            results.append((display_name, True, version))
        except ImportError as e:
            print(f"❌ {display_name}: {str(e)}")
            results.append((display_name, False, str(e)))
        except Exception as e:
            print(f"⚠️ {display_name}: {str(e)}")
            results.append((display_name, False, str(e)))
    
    return results

def test_application():
    """Test the FastAPI application"""
    print("\n🎯 Testing AdWise AI Application:")
    print("-" * 40)
    
    try:
        from app.main import app
        client = TestClient(app)
        
        # Test endpoints
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/docs", "API documentation"),
            ("/redoc", "ReDoc documentation"),
            ("/metrics", "Metrics endpoint")
        ]
        
        results = []
        for endpoint, description in endpoints:
            try:
                response = client.get(endpoint)
                status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
                print(f"{status} {description}: {response.status_code}")
                results.append((description, response.status_code == 200, response.status_code))
                
                # Show response for key endpoints
                if endpoint in ["/", "/health"] and response.status_code == 200:
                    print(f"   Response: {response.json()}")
                    
            except Exception as e:
                print(f"❌ FAIL {description}: {str(e)}")
                results.append((description, False, str(e)))
        
        return results
        
    except Exception as e:
        print(f"❌ Failed to import application: {str(e)}")
        traceback.print_exc()
        return [("Application Import", False, str(e))]

def test_environment():
    """Test the Python environment"""
    print("\n🐍 Testing Python Environment:")
    print("-" * 40)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Virtual environment: {sys.prefix}")
    
    # Check if we're in the correct virtual environment
    if "adwise_env" in sys.executable or "adwise_env" in sys.prefix:
        print("✅ Running in adwise_env virtual environment")
        return True
    else:
        print("⚠️ Not running in adwise_env virtual environment")
        return False

def main():
    """Main test function"""
    print("🎯 AdWise AI Comprehensive Testing from adwise_env")
    print("=" * 60)
    
    # Test environment
    env_ok = test_environment()
    
    # Test imports
    import_results = test_imports()
    
    # Test application
    app_results = test_application()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 60)
    
    import_success = sum(1 for _, success, _ in import_results if success)
    import_total = len(import_results)
    print(f"📦 Imports: {import_success}/{import_total} successful")
    
    if app_results:
        app_success = sum(1 for _, success, _ in app_results if success)
        app_total = len(app_results)
        print(f"🌐 Endpoints: {app_success}/{app_total} working")
    
    print(f"🐍 Environment: {'✅ Correct' if env_ok else '⚠️ Check needed'}")
    
    # Overall status
    overall_success = (
        import_success >= import_total * 0.8 and  # 80% of imports working
        (not app_results or sum(1 for _, success, _ in app_results if success) >= len(app_results) * 0.8) and  # 80% of endpoints working
        env_ok
    )
    
    print("\n🎉 Overall Status:")
    if overall_success:
        print("✅ AdWise AI is running successfully from adwise_env!")
        print("🌐 Access the application at: http://127.0.0.1:8001")
        print("📚 API Documentation: http://127.0.0.1:8001/docs")
        print("💚 Health Check: http://127.0.0.1:8001/health")
    else:
        print("❌ Some issues detected. Please check the results above.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
