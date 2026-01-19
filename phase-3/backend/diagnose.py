#!/usr/bin/env python3
"""
Quick diagnostic script to check backend status and dependencies.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("🐍 Python Version:")
    print(f"   {sys.version}")
    if sys.version_info < (3, 10):
        print("   ⚠️  Python 3.10+ recommended")
    else:
        print("   ✅ Version OK")
    print()

def check_dependencies():
    """Check if critical dependencies are installed."""
    print("📦 Checking Dependencies:")

    deps = {
        "fastapi": "FastAPI web framework",
        "sqlmodel": "Database ORM",
        "openai": "OpenAI SDK (for Agents)",
        "httpx": "Async HTTP client (fixed!)",
        "uvicorn": "ASGI server",
        "psycopg2": "PostgreSQL driver",
        "pyjwt": "JWT authentication"
    }

    missing = []

    for dep, description in deps.items():
        try:
            __import__(dep)
            print(f"   ✅ {dep:15s} - {description}")
        except ImportError:
            print(f"   ❌ {dep:15s} - {description} (MISSING)")
            missing.append(dep)

    # Check optional dependencies
    print("\n📦 Optional Dependencies:")
    optional = {
        "mcp": "Anthropic MCP SDK (for tools)",
        "chatkit": "OpenAI ChatKit (for frontend)"
    }

    for dep, description in optional.items():
        try:
            __import__(dep)
            print(f"   ✅ {dep:15s} - {description}")
        except ImportError:
            print(f"   ⚠️  {dep:15s} - {description} (optional, install if needed)")

    print()
    return missing

def check_env_file():
    """Check .env file."""
    print("🔐 Environment Configuration:")

    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("   ❌ .env file NOT found!")
        print("   Create .env with:")
        print("      - DATABASE_URL")
        print("      - JWT_SECRET")
        print("      - GROQ_API_KEY or OPENAI_API_KEY")
        print()
        return False

    print(f"   ✅ .env file exists")

    # Load and check variables
    try:
        from dotenv import load_dotenv
        load_dotenv()

        required_vars = ["DATABASE_URL", "JWT_SECRET"]
        optional_vars = ["GROQ_API_KEY", "OPENAI_API_KEY", "CORS_ORIGINS"]

        print("\n   Required variables:")
        for var in required_vars:
            value = os.getenv(var)
            if value:
                masked = value[:10] + "..." if len(value) > 10 else value
                print(f"      ✅ {var}: {masked}")
            else:
                print(f"      ❌ {var}: NOT SET")

        print("\n   Optional variables:")
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                masked = value[:20] + "..." if len(value) > 20 else value
                print(f"      ✅ {var}: {masked}")
            else:
                print(f"      ⚠️  {var}: not set")

    except ImportError:
        print("   ⚠️  python-dotenv not installed, cannot check .env variables")

    print()
    return True

def check_new_fixes():
    """Check if new fix files are present."""
    print("🛠️  Chatbot Fixes:")

    fix_files = {
        "intent_classifier.py": "Intent classification module",
        "tool_validation.py": "Defensive validation module",
        "CHATBOT_FIXES_SUMMARY.md": "Fix documentation",
        "CHATKIT_MCP_INTEGRATION.md": "Integration guide"
    }

    for file, description in fix_files.items():
        path = Path(__file__).parent / file
        if path.exists():
            print(f"   ✅ {file:30s} - {description}")
        else:
            print(f"   ⚠️  {file:30s} - {description} (not found)")

    print()

def check_server_running():
    """Check if server is running."""
    print("🚀 Server Status:")

    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()

        if result == 0:
            print("   ✅ Server is RUNNING on port 8000")
            print("   URL: http://localhost:8000")
            print("   Docs: http://localhost:8000/docs")
            return True
        else:
            print("   ❌ Server is NOT running on port 8000")
            print("   Start with: ./start_backend.sh")
            print("   Or: uvicorn main:app --reload --port 8000")
            return False
    except Exception as e:
        print(f"   ❌ Error checking server: {e}")
        return False

    print()

def check_database_connection():
    """Check database connectivity."""
    print("\n🗄️  Database Connection:")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("   ❌ DATABASE_URL not configured in .env")
            return False

        # Try to connect
        try:
            from sqlmodel import create_engine
            engine = create_engine(db_url, echo=False)
            with engine.connect() as conn:
                print("   ✅ Database connection successful")
                return True
        except Exception as e:
            print(f"   ❌ Database connection FAILED: {e}")
            return False

    except ImportError:
        print("   ⚠️  Cannot check database (missing dependencies)")
        return False

    print()

def main():
    """Run all diagnostics."""
    print("=" * 60)
    print("Backend Diagnostic Report")
    print("=" * 60)
    print()

    # Check Python version
    check_python_version()

    # Check dependencies
    missing = check_dependencies()

    # Check environment
    env_ok = check_env_file()

    # Check new fixes
    check_new_fixes()

    # Check if server is running
    server_running = check_server_running()

    # Check database
    db_ok = check_database_connection()

    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    if missing:
        print("❌ Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\nInstall with: pip install -e .")
        print()

    if not env_ok:
        print("❌ Environment not configured")
        print("   Create .env file with required variables")
        print()

    if not server_running:
        print("❌ Server not running")
        print("   Start with: ./start_backend.sh")
        print("   Or: uvicorn main:app --reload --port 8000")
        print()
    else:
        print("✅ Server is running!")
        print()

    if not db_ok:
        print("⚠️  Database connection issues")
        print("   Check DATABASE_URL in .env")
        print()

    if not missing and env_ok and server_running and db_ok:
        print("✅ Everything looks good!")
        print()
        print("Backend is ready to handle requests from frontend.")
        print("Frontend should connect to: http://localhost:8000")
    else:
        print("⚠️  Some issues detected. Fix them and restart.")
        print()
        print("Quick fix:")
        print("1. Install dependencies: pip install -e .")
        print("2. Check .env file has required variables")
        print("3. Start server: ./start_backend.sh")

if __name__ == "__main__":
    main()
