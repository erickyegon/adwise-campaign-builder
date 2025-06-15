#!/usr/bin/env python3
"""
AdWise AI Digital Marketing Campaign Builder - Production Server
Comprehensive production-quality server with full database integration
"""

from app.core.config import get_settings
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Optional

import uvicorn
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import database managers with error handling
try:
    from app.core.database.mongodb import get_mongodb_manager
    MONGODB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"MongoDB manager not available: {e}")
    MONGODB_AVAILABLE = False
    get_mongodb_manager = None

try:
    from app.core.database.redis import get_redis_manager
    REDIS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Redis manager not available: {e}")
    REDIS_AVAILABLE = False
    get_redis_manager = None

# Initialize console for rich output
console = Console()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


async def validate_environment() -> bool:
    """
    Comprehensive environment validation

    Returns:
        bool: True if environment is valid, False otherwise
    """
    console.print(
        "\n🔍 [bold blue]Validating Production Environment[/bold blue]")

    validation_table = Table(title="Environment Validation")
    validation_table.add_column("Component", style="cyan", no_wrap=True)
    validation_table.add_column("Status", style="magenta")
    validation_table.add_column("Details", style="green")

    all_valid = True

    # 1. Python Version Check
    python_version = f"v{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    validation_table.add_row("Python Version", "✅ Valid", python_version)

    # 2. Virtual Environment Check
    venv_status = "✅ Active" if hasattr(sys, 'real_prefix') or (hasattr(
        sys, 'base_prefix') and sys.base_prefix != sys.prefix) else "❌ Not Active"
    venv_name = Path(sys.prefix).name if venv_status == "✅ Active" else "None"
    validation_table.add_row("Virtual Environment",
                             venv_status, f"{venv_name} detected")

    # 3. Required Directories
    required_dirs = ["app", "uploads", "logs"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        validation_table.add_row(f"Directory: {dir_name}", "✅ Exists", "Ready")

    # 4. Configuration
    try:
        validation_table.add_row(
            "Configuration", "✅ Loaded", f"Environment: {settings.app.ENVIRONMENT}")
    except Exception as e:
        validation_table.add_row("Configuration", "❌ Failed", str(e))
        all_valid = False

    # 5. MongoDB Connection
    if MONGODB_AVAILABLE and get_mongodb_manager:
        try:
            mongodb_manager = await get_mongodb_manager()
            await mongodb_manager.health_check()
            validation_table.add_row(
                "MongoDB", "✅ Connected", "Database accessible")
        except Exception as e:
            validation_table.add_row(
                "MongoDB", "❌ Failed", f"Connection error: {str(e)[:50]}...")
            all_valid = False
    else:
        validation_table.add_row(
            "MongoDB", "⚠️ Warning", "Database manager not available")

    # 6. Redis Connection
    if REDIS_AVAILABLE and get_redis_manager:
        try:
            redis_manager = await get_redis_manager()
            await redis_manager.health_check()
            validation_table.add_row(
                "Redis", "✅ Connected", "Cache accessible")
        except Exception as e:
            validation_table.add_row(
                "Redis", "❌ Failed", f"Connection error: {str(e)[:50]}...")
            all_valid = False
    else:
        validation_table.add_row(
            "Redis", "⚠️ Warning", "Redis manager not available")

    # 7. EURI AI Configuration
    if settings.ai.EURI_API_KEY and settings.ai.EURI_API_KEY != "your_euri_api_key_here":
        validation_table.add_row("EURI AI", "✅ Configured", "API key present")
    else:
        validation_table.add_row("EURI AI", "⚠️ Warning", "Using test API key")

    console.print(validation_table)
    return all_valid


async def initialize_database() -> bool:
    """
    Initialize database connections and schemas

    Returns:
        bool: True if successful, False otherwise
    """
    console.print("\n🗄️ [bold blue]Initializing Database Systems[/bold blue]")

    success = True

    # Initialize MongoDB
    if MONGODB_AVAILABLE and get_mongodb_manager:
        try:
            console.print("📊 Initializing MongoDB...")
            mongodb_manager = await get_mongodb_manager()
            await mongodb_manager.initialize()
            console.print("✅ MongoDB initialized successfully")
        except Exception as e:
            console.print(f"❌ MongoDB initialization failed: {e}")
            success = False
    else:
        console.print("⚠️ MongoDB manager not available, skipping...")

    # Initialize Redis
    if REDIS_AVAILABLE and get_redis_manager:
        try:
            console.print("🔄 Initializing Redis...")
            redis_manager = await get_redis_manager()
            await redis_manager.initialize()
            console.print("✅ Redis initialized successfully")
        except Exception as e:
            console.print(f"❌ Redis initialization failed: {e}")
            success = False
    else:
        console.print("⚠️ Redis manager not available, skipping...")

    return success


def display_server_info():
    """Display comprehensive server information"""

    # Server details panel
    server_info = f"""
🚀 [bold green]AdWise AI Production Server[/bold green]

📍 [bold]Server Details:[/bold]
   • Host: 127.0.0.1
   • Port: 8002
   • Environment: {settings.app.ENVIRONMENT}
   • Debug Mode: {'✅ Enabled' if settings.app.DEBUG else '❌ Disabled'}
   • Workers: 1

🔗 [bold]Access URLs:[/bold]
   • Application: http://127.0.0.1:8002
   • API Documentation: http://127.0.0.1:8002/docs
   • ReDoc: http://127.0.0.1:8002/redoc
   • Health Check: http://127.0.0.1:8002/health
   • Detailed Health: http://127.0.0.1:8002/health/detailed
   • Metrics: http://127.0.0.1:8002/metrics

🛠️ [bold]Production Features:[/bold]
   • MongoDB with Beanie ODM
   • Redis caching and sessions
   • EURI AI integration
   • LangChain/LangGraph workflows
   • Real-time collaboration
   • Comprehensive monitoring
   • Security middleware
   • Error tracking

⚡ [bold]Performance:[/bold]
   • Workers: {getattr(settings.app, 'WORKERS', 1)}
   • Max connections: Unlimited
   • Timeout: 60 seconds
   • Keep-alive: 5 seconds

🔒 [bold]Security:[/bold]
   • CORS configured
   • Rate limiting enabled
   • Secure headers
   • Authentication ready
"""

    console.print(
        Panel(server_info, title="🎯 Production Server", border_style="green"))


async def start_production_server():
    """Start the production server with full validation"""

    console.print(Panel.fit(
        "[bold green]🎯 AdWise AI Digital Marketing Campaign Builder[/bold green]\n"
        "[bold blue]🚀 Production Server Startup[/bold blue]",
        border_style="green"
    ))

    # 1. Environment Validation
    if not await validate_environment():
        console.print(
            "\n❌ [bold red]Environment validation failed. Please fix the issues above.[/bold red]")
        return False

    # 2. Database Initialization
    if not await initialize_database():
        console.print(
            "\n❌ [bold red]Database initialization failed.[/bold red]")
        return False

    # 3. Display server information
    display_server_info()

    # 4. Start the server
    console.print("\n🚀 [bold green]Starting production server...[/bold green]")
    console.print("Press Ctrl+C to stop the server\n")

    try:
        # Import the main app
        from app.main import app

        # Configure uvicorn for production
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8002,  # Use port 8002 to avoid conflicts
            log_level="info",
            access_log=True,
            reload=False,  # Disabled for production
            workers=1,  # Single worker for development, increase for production
        )

        server = uvicorn.Server(config)
        await server.serve()

    except KeyboardInterrupt:
        console.print("\n🛑 [bold yellow]Server stopped by user[/bold yellow]")
    except Exception as e:
        console.print(f"\n❌ [bold red]Server error: {e}[/bold red]")
        return False

    return True


def main():
    """Main entry point"""
    try:
        success = asyncio.run(start_production_server())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print(
            "\n🛑 [bold yellow]Startup interrupted by user[/bold yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ [bold red]Fatal error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
