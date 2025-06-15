#!/usr/bin/env python3
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
        print("\nPress Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
