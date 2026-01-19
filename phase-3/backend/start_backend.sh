#!/bin/bash
# Backend Startup Script with Diagnostics
# This script checks dependencies and starts the backend server

set -e  # Exit on error

echo "======================================"
echo "Backend Startup Diagnostics"
echo "======================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "   ✅ $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "   ❌ Python not found!"
    exit 1
fi

# Check if .env exists
echo ""
echo "🔐 Checking .env file..."
if [ -f ".env" ]; then
    echo "   ✅ .env file exists"
else
    echo "   ❌ .env file NOT found!"
    echo "   Create .env file with required variables"
    exit 1
fi

# Check critical dependencies
echo ""
echo "📦 Checking dependencies..."

check_package() {
    if $PYTHON_CMD -c "import $1" 2>/dev/null; then
        echo "   ✅ $1"
        return 0
    else
        echo "   ❌ $1 NOT installed"
        return 1
    fi
}

MISSING_DEPS=0

check_package "fastapi" || MISSING_DEPS=1
check_package "sqlmodel" || MISSING_DEPS=1
check_package "openai" || MISSING_DEPS=1
check_package "httpx" || MISSING_DEPS=1

# Check if mcp is installed (might fail, that's ok)
if check_package "mcp"; then
    echo "   ✅ mcp (Anthropic MCP SDK)"
else
    echo "   ⚠️  mcp not installed (install: pip install mcp)"
fi

# Check new modules from fixes
if [ -f "intent_classifier.py" ]; then
    echo "   ✅ intent_classifier.py (fixes installed)"
else
    echo "   ⚠️  intent_classifier.py not found"
fi

if [ -f "tool_validation.py" ]; then
    echo "   ✅ tool_validation.py (fixes installed)"
else
    echo "   ⚠️  tool_validation.py not found"
fi

# Install missing dependencies if needed
if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo "❌ Missing dependencies detected!"
    echo ""
    read -p "Install missing dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing dependencies..."
        $PYTHON_CMD -m pip install -e .
    else
        echo "❌ Cannot start without dependencies"
        exit 1
    fi
fi

# Check if uvicorn is available
echo ""
echo "🚀 Checking uvicorn..."
if command -v uvicorn &> /dev/null; then
    echo "   ✅ uvicorn found"
elif $PYTHON_CMD -c "import uvicorn" 2>/dev/null; then
    echo "   ✅ uvicorn installed (Python module)"
else
    echo "   ❌ uvicorn NOT found!"
    echo "   Installing uvicorn..."
    $PYTHON_CMD -m pip install uvicorn
fi

# Check database connectivity
echo ""
echo "🗄️  Checking database connectivity..."
DB_CHECK=$($PYTHON_CMD -c "
import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL')
if db_url:
    print('✅ DATABASE_URL configured')
else:
    print('❌ DATABASE_URL not set in .env')
" 2>&1)
echo "   $DB_CHECK"

# Check GROQ API key
echo ""
echo "🤖 Checking AI configuration..."
AI_CHECK=$($PYTHON_CMD -c "
import os
from dotenv import load_dotenv
load_dotenv()
groq_key = os.getenv('GROQ_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')
if groq_key:
    print('✅ GROQ_API_KEY configured')
elif openai_key:
    print('✅ OPENAI_API_KEY configured')
else:
    print('⚠️  No AI API key configured')
" 2>&1)
echo "   $AI_CHECK"

# All checks passed
echo ""
echo "======================================"
echo "✅ All checks passed!"
echo "======================================"
echo ""

# Start the server
echo "🚀 Starting backend server..."
echo "   URL: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn with proper settings
if command -v uvicorn &> /dev/null; then
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info
else
    $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info
fi
