#!/usr/bin/env python3
"""
Simple System Test for AdWise AI - No Database Dependencies
Tests core functionality without requiring database connections
"""

import sys
import os
import traceback
from pathlib import Path

def test_python_environment():
    """Test Python environment and virtual environment"""
    print("🐍 Testing Python Environment:")
    print("-" * 40)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if we're in virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Virtual environment: {venv_path}")
        if 'adwise_env' in venv_path:
            print("✅ Running in adwise_env virtual environment")
            return True
        else:
            print("⚠️ Running in different virtual environment")
            return False
    else:
        print("❌ Not running in virtual environment")
        return False

def test_core_imports():
    """Test core package imports without database connections"""
    print("\n🔧 Testing Core Imports:")
    print("-" * 40)
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("uvicorn", "Uvicorn"),
        ("langchain", "LangChain"),
        ("langchain_core", "LangChain Core"),
        ("langchain_community", "LangChain Community"),
        ("langgraph", "LangGraph"),
        ("langserve", "LangServe"),
        ("euriai", "EURI AI"),
        ("beanie", "Beanie ODM"),
        ("motor", "Motor (MongoDB)"),
        ("redis", "Redis"),
        ("pymongo", "PyMongo"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
    ]
    
    results = []
    for module_name, display_name in imports_to_test:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'Available')
            print(f"✅ {display_name}: {version}")
            results.append((display_name, True, version))
        except ImportError as e:
            print(f"❌ {display_name}: Import failed - {e}")
            results.append((display_name, False, str(e)))
        except Exception as e:
            print(f"⚠️ {display_name}: Warning - {e}")
            results.append((display_name, True, f"Warning: {e}"))
    
    return results

def test_configuration_loading():
    """Test configuration loading without database connections"""
    print("\n⚙️ Testing Configuration Loading:")
    print("-" * 40)
    
    try:
        # Test basic pydantic settings
        from pydantic import BaseModel, Field
        from pydantic_settings import BaseSettings
        
        class TestSettings(BaseSettings):
            test_value: str = Field(default="test")
            
        settings = TestSettings()
        print("✅ Pydantic settings loading works")
        
        # Test environment variable loading
        os.environ['TEST_VALUE'] = 'environment_test'
        settings = TestSettings()
        if settings.test_value == 'environment_test':
            print("✅ Environment variable loading works")
        else:
            print("⚠️ Environment variable loading issue")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        traceback.print_exc()
        return False

def test_langchain_basic():
    """Test basic LangChain functionality"""
    print("\n🔗 Testing LangChain Basic Functionality:")
    print("-" * 40)
    
    try:
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Test prompt template
        prompt = PromptTemplate.from_template("Hello {name}!")
        formatted = prompt.format(name="World")
        print(f"✅ Prompt template works: {formatted}")
        
        # Test output parser
        parser = StrOutputParser()
        print("✅ Output parser created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain basic test failed: {e}")
        traceback.print_exc()
        return False

def test_fastapi_basic():
    """Test basic FastAPI functionality without starting server"""
    print("\n🚀 Testing FastAPI Basic Functionality:")
    print("-" * 40)
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Create a simple test app
        test_app = FastAPI(title="Test App")
        
        @test_app.get("/test")
        def test_endpoint():
            return {"message": "test successful"}
        
        # Test with TestClient
        client = TestClient(test_app)
        response = client.get("/test")
        
        if response.status_code == 200 and response.json()["message"] == "test successful":
            print("✅ FastAPI basic functionality works")
            return True
        else:
            print(f"❌ FastAPI test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FastAPI basic test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test project file structure"""
    print("\n📁 Testing Project File Structure:")
    print("-" * 40)
    
    required_files = [
        "app/main.py",
        "app/api/v1/router.py",
        "app/services/langchain_service.py",
        "app/services/langserve_routes.py",
        "app/services/streaming_service.py",
        "requirements.txt",
        ".env",
        "tests/test_main.py",
        "tests/test_langchain_integration.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ All required files present")
        return True
    else:
        print(f"⚠️ Missing {len(missing_files)} files")
        return False

def main():
    """Main test function"""
    print("🎯 AdWise AI Simple System Test")
    print("=" * 60)
    print("Testing core functionality without database dependencies")
    print("=" * 60)
    
    # Run tests
    env_ok = test_python_environment()
    import_results = test_core_imports()
    config_ok = test_configuration_loading()
    langchain_ok = test_langchain_basic()
    fastapi_ok = test_fastapi_basic()
    files_ok = test_file_structure()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 60)
    
    import_success = sum(1 for _, success, _ in import_results if success)
    import_total = len(import_results)
    print(f"📦 Imports: {import_success}/{import_total} successful")
    print(f"🐍 Environment: {'✅ Correct' if env_ok else '❌ Issue'}")
    print(f"⚙️ Configuration: {'✅ Working' if config_ok else '❌ Issue'}")
    print(f"🔗 LangChain: {'✅ Working' if langchain_ok else '❌ Issue'}")
    print(f"🚀 FastAPI: {'✅ Working' if fastapi_ok else '❌ Issue'}")
    print(f"📁 File Structure: {'✅ Complete' if files_ok else '⚠️ Issues'}")
    
    # Overall status
    core_tests_passed = config_ok and langchain_ok and fastapi_ok
    overall_success = (
        import_success >= import_total * 0.8 and  # 80% of imports working
        env_ok and
        core_tests_passed
    )
    
    print("\n🎉 Overall Status:")
    if overall_success:
        print("✅ Core system is working correctly!")
        print("🔧 Ready for database setup and full testing")
        print("📝 Next steps:")
        print("   1. Set up MongoDB and Redis services")
        print("   2. Run full application tests")
        print("   3. Test API endpoints")
    else:
        print("❌ Some core issues detected. Please check the results above.")
        print("🔧 Fix core issues before proceeding with database setup")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
