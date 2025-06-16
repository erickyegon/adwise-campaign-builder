#!/usr/bin/env python3
"""
AdWise AI Main Application Server - Port 8007
Professional Enterprise-Grade Digital Marketing Platform

This script starts the comprehensive AdWise AI application on port 8007
with all enterprise features enabled including:
- Complete API suite with 50+ endpoints
- EURI AI integration with advanced content generation
- LangChain/LangGraph/LangServe workflows
- Real-time collaboration features
- MongoDB integration with Beanie ODM
- Redis caching for optimal performance
- JWT authentication and authorization
- Comprehensive analytics and reporting
- Export services (PDF, CSV, Excel)
- WebSocket real-time features
"""

import asyncio
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def display_startup_banner():
    """Display professional startup banner"""
    
    banner_text = Text()
    banner_text.append("🎯 AdWise AI Digital Marketing Campaign Builder\n", style="bold blue")
    banner_text.append("Enterprise-Grade Professional Implementation\n\n", style="bold green")
    banner_text.append("🌐 Main Application: ", style="white")
    banner_text.append("http://127.0.0.1:8007", style="bold cyan underline")
    banner_text.append("\n📚 API Documentation: ", style="white")
    banner_text.append("http://127.0.0.1:8007/docs", style="bold cyan underline")
    banner_text.append("\n💚 Health Check: ", style="white")
    banner_text.append("http://127.0.0.1:8007/health", style="bold cyan underline")
    banner_text.append("\n🤖 AI Services: ", style="white")
    banner_text.append("http://127.0.0.1:8007/api/v1/", style="bold cyan underline")
    
    panel = Panel(
        banner_text,
        title="🚀 STARTING COMPREHENSIVE APPLICATION",
        title_align="center",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()

def display_features():
    """Display key features"""
    features = [
        "✅ Complete Campaign Management Lifecycle",
        "✅ Advanced AI Content Generation (EURI AI)",
        "✅ LangChain/LangGraph/LangServe Integration",
        "✅ Real-time Collaboration & WebSockets",
        "✅ MongoDB with Beanie ODM",
        "✅ Redis Caching & Performance Optimization",
        "✅ JWT Authentication & Authorization",
        "✅ Comprehensive Analytics & Reporting",
        "✅ Export Services (PDF/CSV/Excel)",
        "✅ Enterprise Security & OWASP Compliance",
        "✅ 50+ Professional API Endpoints",
        "✅ Interactive Swagger Documentation"
    ]
    
    console.print("[bold green]🎯 ENTERPRISE FEATURES ENABLED:[/bold green]")
    for feature in features:
        console.print(f"  {feature}")
    console.print()

async def main():
    """Main application runner"""
    try:
        # Display startup information
        display_startup_banner()
        display_features()
        
        console.print("[bold yellow]🔧 Initializing application components...[/bold yellow]")
        
        # Import the main application
        try:
            from app.main import app
            console.print("✅ Main application imported successfully")
        except ImportError as e:
            console.print(f"⚠️ Using fallback app (some features may be limited): {e}")
            from app_no_db import app
        
        console.print("[bold green]🚀 Starting server on port 8007...[/bold green]")
        console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")
        
        # Configure and start the server
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8007,
            log_level="info",
            access_log=True,
            reload=False,
            workers=1,
            timeout_keep_alive=5,
            timeout_graceful_shutdown=30,
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]🛑 Graceful shutdown initiated...[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Server error: {e}[/bold red]")
        raise
    finally:
        console.print("[bold green]✅ Server shutdown complete[/bold green]")

if __name__ == "__main__":
    asyncio.run(main())
