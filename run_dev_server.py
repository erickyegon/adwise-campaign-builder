#!/usr/bin/env python3
"""
AdWise AI Development Server Runner

This script provides a comprehensive development server setup with:
- Hot reload for development
- Proper logging configuration
- Environment validation
- Database connectivity checks
- Service health monitoring
- Development-specific middleware
- Debug mode configuration
- Performance monitoring

Usage:
    python run_dev_server.py [--host HOST] [--port PORT] [--reload] [--debug]

Features:
- Automatic dependency validation
- Database connection testing
- Redis connectivity verification
- EURI AI service validation
- Comprehensive error handling
- Development-specific CORS settings
- Hot reload with file watching
- Structured logging
"""

from app.core.config import get_settings
import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import uvicorn
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# Optional imports for validation
try:
    from app.core.database.mongodb import get_database_manager
except ImportError:
    get_database_manager = None

try:
    from app.core.redis import get_redis_manager
except ImportError:
    get_redis_manager = None

console = Console()
logger = logging.getLogger(__name__)


def setup_development_logging():
    """Setup rich logging for development"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


async def validate_environment():
    """Validate development environment and dependencies"""
    console.print(
        "\n🔍 [bold blue]Validating Development Environment[/bold blue]")

    validation_table = Table(title="Environment Validation")
    validation_table.add_column("Component", style="cyan")
    validation_table.add_column("Status", style="green")
    validation_table.add_column("Details", style="yellow")

    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        validation_table.add_row(
            "Python Version", "✅ Valid", f"v{python_version}")
    else:
        validation_table.add_row(
            "Python Version", "❌ Invalid", f"v{python_version} (requires 3.10+)")
        return False

    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        validation_table.add_row(
            "Virtual Environment", "✅ Active", "adwise_env detected")
    else:
        validation_table.add_row(
            "Virtual Environment", "⚠️ Warning", "No virtual environment detected")

    # Check required directories
    required_dirs = ["app", "uploads", "logs"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            validation_table.add_row(
                f"Directory: {dir_name}", "✅ Exists", "Ready")
        else:
            Path(dir_name).mkdir(exist_ok=True)
            validation_table.add_row(
                f"Directory: {dir_name}", "✅ Created", "Auto-created")

    # Check configuration
    try:
        settings = get_settings()
        validation_table.add_row(
            "Configuration", "✅ Loaded", f"Environment: {settings.app.ENVIRONMENT}")
    except Exception as e:
        validation_table.add_row("Configuration", "❌ Failed", str(e))
        return False

    # Check database connectivity
    if get_database_manager:
        try:
            db_manager = await get_database_manager()
            if await db_manager.health_check():
                validation_table.add_row(
                    "MongoDB", "✅ Connected", "Database accessible")
            else:
                validation_table.add_row(
                    "MongoDB", "⚠️ Warning", "Connection issues")
        except Exception as e:
            validation_table.add_row(
                "MongoDB", "❌ Failed", f"Error: {str(e)[:50]}...")
    else:
        validation_table.add_row(
            "MongoDB", "⚠️ Warning", "Database manager not available")

    # Check Redis connectivity
    if get_redis_manager:
        try:
            redis_manager = await get_redis_manager()
            if await redis_manager.health_check():
                validation_table.add_row(
                    "Redis", "✅ Connected", "Cache accessible")
            else:
                validation_table.add_row(
                    "Redis", "⚠️ Warning", "Connection issues")
        except Exception as e:
            validation_table.add_row(
                "Redis", "❌ Failed", f"Error: {str(e)[:50]}...")
    else:
        validation_table.add_row(
            "Redis", "⚠️ Warning", "Redis manager not available")

    # Check EURI AI configuration
    try:
        if settings.ai.EURI_API_KEY and settings.ai.EURI_API_KEY != "test-key":
            validation_table.add_row(
                "EURI AI", "✅ Configured", "API key present")
        else:
            validation_table.add_row(
                "EURI AI", "⚠️ Warning", "Using test API key")
    except Exception as e:
        validation_table.add_row("EURI AI", "❌ Failed", str(e))

    console.print(validation_table)
    return True


def display_server_info(host: str, port: int, debug: bool, reload: bool):
    """Display comprehensive server information"""
    settings = get_settings()

    # Server info panel
    server_info = f"""
🚀 [bold green]AdWise AI Development Server[/bold green]

📍 [bold]Server Details:[/bold]
   • Host: {host}
   • Port: {port}
   • Debug Mode: {'✅ Enabled' if debug else '❌ Disabled'}
   • Hot Reload: {'✅ Enabled' if reload else '❌ Disabled'}
   • Environment: {settings.app.ENVIRONMENT}

🔗 [bold]Access URLs:[/bold]
   • Application: http://{host}:{port}
   • API Documentation: http://{host}:{port}/docs
   • ReDoc: http://{host}:{port}/redoc
   • Health Check: http://{host}:{port}/health
   • Metrics: http://{host}:{port}/metrics

🛠️ [bold]Development Features:[/bold]
   • Interactive API docs with Swagger UI
   • Automatic code reloading on file changes
   • Comprehensive error tracebacks
   • Performance monitoring
   • Request/response logging
   • CORS enabled for local development

⚡ [bold]Performance:[/bold]
   • Workers: 1 (development)
   • Max connections: Unlimited
   • Timeout: 60 seconds
   • Keep-alive: 5 seconds
    """

    console.print(
        Panel(server_info, title="🎯 Development Server", border_style="green"))


def create_uvicorn_config(host: str, port: int, debug: bool, reload: bool) -> dict:
    """Create comprehensive uvicorn configuration for development"""
    settings = get_settings()

    # Comprehensive logging configuration
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "level": "DEBUG" if debug else "INFO",
            "handlers": ["default"],
        },
    }

    config = {
        "app": "app.main:app",
        "host": host,
        "port": port,
        "reload": reload,
        "reload_dirs": ["app", "tests"] if reload else None,
        "reload_includes": ["*.py"] if reload else None,
        "reload_excludes": ["*.pyc", "__pycache__"] if reload else None,
        "log_level": "debug" if debug else "info",
        "log_config": log_config,
        "access_log": True,
        "use_colors": True,
        "loop": "asyncio",
        "http": "httptools",
        "ws": "websockets",
        "ws_ping_interval": 20,
        "ws_ping_timeout": 20,
        "ws_max_size": 16777216,
        "lifespan": "on",
        "interface": "asgi3",
        "timeout_keep_alive": 5,
        "timeout_graceful_shutdown": 30,
        "limit_concurrency": None,
        "limit_max_requests": None,
        "backlog": 2048,
        "forwarded_allow_ips": "*",
        "proxy_headers": True,
        "server_header": True,
        "date_header": True,
    }

    # Development-specific enhancements
    if debug:
        config.update({
            "reload_delay": 0.25,
            "workers": 1,  # Single worker for development
            "factory": False,
            "env_file": ".env.development",
            "ssl_keyfile": None,
            "ssl_certfile": None,
            "ssl_keyfile_password": None,
            "ssl_version": None,
            "ssl_cert_reqs": None,
            "ssl_ca_certs": None,
            "ssl_ciphers": "TLSv1",
        })

        # Enhanced logging for debug mode
        config["log_config"]["loggers"]["app"] = {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        }
        config["log_config"]["loggers"]["sqlalchemy"] = {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        }
        config["log_config"]["loggers"]["beanie"] = {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        }

    # Production-ready settings for non-debug mode
    else:
        config.update({
            "workers": 1,  # Still single worker for development
            "factory": False,
            "env_file": ".env.development",
        })

    return config


async def main():
    """Main development server runner"""
    parser = argparse.ArgumentParser(
        description="AdWise AI Development Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to bind to")
    parser.add_argument("--reload", action="store_true",
                        help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    parser.add_argument("--no-validation", action="store_true",
                        help="Skip environment validation")

    args = parser.parse_args()

    # Setup logging
    setup_development_logging()

    # Display banner
    console.print("\n" + "="*80)
    console.print(
        "🎯 [bold blue]AdWise AI Digital Marketing Campaign Builder[/bold blue]")
    console.print("🚀 [bold green]Development Server Startup[/bold green]")
    console.print("="*80)

    # Validate environment unless skipped
    if not args.no_validation:
        if not await validate_environment():
            console.print(
                "\n❌ [bold red]Environment validation failed![/bold red]")
            console.print(
                "Please fix the issues above before starting the server.")
            sys.exit(1)

    # Display server information
    display_server_info(args.host, args.port, args.debug, args.reload)

    # Create uvicorn configuration
    config = create_uvicorn_config(
        args.host, args.port, args.debug, args.reload)

    # Start server
    console.print(
        "\n🚀 [bold green]Starting development server...[/bold green]")
    console.print("Press Ctrl+C to stop the server\n")

    try:
        # Add startup validation
        console.print(
            "🔍 [bold blue]Validating application startup...[/bold blue]")

        # Test import of main app
        try:
            from app.main import app as test_app
            console.print("✅ Application module imported successfully")
            console.print(
                f"📋 Available routes: {len(test_app.routes)} endpoints")
        except Exception as import_error:
            console.print(
                f"❌ [bold red]Failed to import application: {import_error}[/bold red]")
            raise

        # Start the server
        console.print(
            f"🌐 [bold green]Server starting on http://{args.host}:{args.port}[/bold green]")

        # Create comprehensive uvicorn server configuration
        console.print(
            "⚙️ [bold blue]Creating server configuration...[/bold blue]")

        try:
            server_config = uvicorn.Config(**config)
            console.print("✅ Server configuration created successfully")
        except Exception as config_error:
            console.print(
                f"❌ [bold red]Configuration error: {config_error}[/bold red]")
            raise

        server = uvicorn.Server(server_config)

        # Comprehensive signal handling
        import signal
        import threading

        shutdown_event = threading.Event()

        def signal_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            console.print(
                f"\n🛑 [bold yellow]Received {signal_name} signal - initiating graceful shutdown[/bold yellow]")
            server.should_exit = True
            shutdown_event.set()

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)

        # Pre-startup validation
        console.print(
            "🔍 [bold blue]Performing pre-startup validation...[/bold blue]")

        # Check port availability
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((args.host, args.port))
            console.print(f"✅ Port {args.port} is available")
        except OSError as e:
            console.print(
                f"❌ [bold red]Port {args.port} is not available: {e}[/bold red]")
            raise

        # Start server with comprehensive monitoring
        console.print(
            f"🚀 [bold green]Starting server on {args.host}:{args.port}[/bold green]")
        console.print("📊 [dim]Server will be available at:[/dim]")
        console.print(f"   • Main: http://{args.host}:{args.port}")
        console.print(f"   • Docs: http://{args.host}:{args.port}/docs")
        console.print(f"   • Health: http://{args.host}:{args.port}/health")

        try:
            console.print("🔄 [bold blue]Calling server.serve()...[/bold blue]")
            await server.serve()
            console.print(
                "✅ [bold green]Server.serve() completed[/bold green]")
        except Exception as serve_error:
            console.print(
                f"❌ [bold red]Server error during startup: {serve_error}[/bold red]")
            import traceback
            console.print(f"📋 [dim]Traceback: {traceback.format_exc()}[/dim]")
            raise

    except KeyboardInterrupt:
        console.print(
            "\n\n🛑 [bold yellow]Server stopped by user[/bold yellow]")
    except ImportError as e:
        console.print(f"\n❌ [bold red]Import error: {e}[/bold red]")
        console.print(
            "💡 [yellow]Hint: Check that all dependencies are installed and the app module is correct[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ [bold red]Server error: {e}[/bold red]")
        console.print(f"🔍 [yellow]Error type: {type(e).__name__}[/yellow]")
        import traceback
        console.print(f"📋 [dim]Traceback: {traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Use asyncio.run with proper event loop policy for Windows
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(
                asyncio.WindowsProactorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print(
            "\n🛑 [bold yellow]Development server stopped[/bold yellow]")
    except Exception as e:
        console.print(f"\n❌ [bold red]Fatal error: {e}[/bold red]")
        sys.exit(1)
