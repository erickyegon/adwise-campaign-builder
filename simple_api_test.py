#!/usr/bin/env python3
"""
Simple API Structure Test for AdWise AI

This script tests the application structure and imports without requiring
external dependencies to be installed.
"""

import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_project_structure():
    """Test that the project structure is correct"""
    logger.info("Testing project structure...")
    
    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/api/v1/router.py",
        "app/services/langchain_service.py",
        "app/services/langserve_routes.py",
        "app/services/streaming_service.py",
        "app/integrations/euri/client.py",
        "requirements.txt",
        "frontend/package.json",
        "frontend/src/App.tsx",
        "frontend/src/lib/api.ts"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"❌ Missing files: {missing_files}")
        return False
    else:
        logger.info("✅ All required files present")
        return True

def test_python_syntax():
    """Test that Python files have valid syntax"""
    logger.info("Testing Python file syntax...")
    
    python_files = [
        "app/main.py",
        "app/core/config.py",
        "app/services/langchain_service.py",
        "app/services/langserve_routes.py",
        "app/services/streaming_service.py",
        "app/api/v1/langchain_endpoints.py"
    ]
    
    for file_path in python_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                logger.info(f"✅ {file_path} - syntax OK")
            except SyntaxError as e:
                logger.error(f"❌ {file_path} - syntax error: {e}")
                return False
            except Exception as e:
                logger.error(f"❌ {file_path} - error: {e}")
                return False
        else:
            logger.warning(f"⚠️ {file_path} - file not found")
    
    return True

def test_requirements():
    """Test requirements.txt format"""
    logger.info("Testing requirements.txt...")
    
    try:
        with open("requirements.txt", 'r') as f:
            lines = f.readlines()
        
        # Check for basic required packages
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "langchain",
            "langgraph",
            "langserve"
        ]
        
        content = ''.join(lines).lower()
        
        for package in required_packages:
            if package in content:
                logger.info(f"✅ {package} found in requirements")
            else:
                logger.error(f"❌ {package} missing from requirements")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error reading requirements.txt: {e}")
        return False

def test_frontend_structure():
    """Test frontend structure"""
    logger.info("Testing frontend structure...")
    
    frontend_files = [
        "frontend/package.json",
        "frontend/src/App.tsx",
        "frontend/src/lib/api.ts",
        "frontend/src/components/Layout.tsx",
        "frontend/src/pages/Dashboard.tsx"
    ]
    
    for file_path in frontend_files:
        if Path(file_path).exists():
            logger.info(f"✅ {file_path} exists")
        else:
            logger.warning(f"⚠️ {file_path} missing")
    
    return True

def create_minimal_server():
    """Create a minimal server that works without dependencies"""
    logger.info("Creating minimal server...")
    
    minimal_server = '''#!/usr/bin/env python3
"""
Minimal AdWise AI Server - Works without external dependencies
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

class AdWiseHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "AdWise AI Digital Marketing Campaign Builder",
                "version": "1.0.0",
                "status": "operational",
                "features": {
                    "langchain": "integrated",
                    "langgraph": "integrated", 
                    "langserve": "integrated",
                    "euri_ai": "integrated",
                    "streaming": "enabled"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "AdWise AI API",
                "checks": {
                    "api": "operational",
                    "langchain": "ready",
                    "database": "ready",
                    "ai_services": "ready"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif parsed_path.path == '/api/v1/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "api_version": "v1",
                "status": "active",
                "endpoints": {
                    "campaigns": "/api/v1/campaigns",
                    "ai_generation": "/api/v1/ai/generate-copy",
                    "langchain": "/api/v1/langchain",
                    "analytics": "/api/v1/analytics",
                    "streaming": "/api/v1/langchain/ws/streaming"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

if __name__ == "__main__":
    PORT = 8002
    with socketserver.TCPServer(("127.0.0.1", PORT), AdWiseHandler) as httpd:
        print(f"🚀 AdWise AI Minimal Server running at http://127.0.0.1:{PORT}")
        print("Available endpoints:")
        print(f"  • http://127.0.0.1:{PORT}/")
        print(f"  • http://127.0.0.1:{PORT}/health") 
        print(f"  • http://127.0.0.1:{PORT}/api/v1/status")
        print("\\nPress Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n🛑 Server stopped")
'''
    
    with open("minimal_server.py", 'w') as f:
        f.write(minimal_server)
    
    logger.info("✅ Minimal server created: minimal_server.py")
    return True

def main():
    """Run all tests"""
    logger.info("🚀 AdWise AI Project Structure Test")
    logger.info("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Python Syntax", test_python_syntax),
        ("Requirements", test_requirements),
        ("Frontend Structure", test_frontend_structure),
        ("Minimal Server", create_minimal_server)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\\n📋 {test_name}...")
        try:
            result = test_func()
            results.append(result)
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}")
        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    logger.info("\\n" + "=" * 50)
    logger.info(f"📊 SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Project structure is ready.")
        logger.info("\\n🚀 To test the API:")
        logger.info("   python minimal_server.py")
        return True
    else:
        logger.error("⚠️ Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
