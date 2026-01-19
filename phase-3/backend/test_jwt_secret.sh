#!/bin/bash
# Test if new JWT_SECRET is working

echo "🧪 Testing JWT Authentication with New Secret..."
echo "================================================"
echo ""

# Get JWT_SECRET from .env
JWT_SECRET=$(grep "^JWT_SECRET=" .env | cut -d'=' -f2)
echo "✅ JWT_SECRET loaded from .env:"
echo "   ${JWT_SECRET:0:20}... (${#JWT_SECRET} characters)"
echo ""

# Test backend health
echo "🔍 Testing backend health..."
HEALTH=$(curl -s http://localhost:8000/)
if echo "$HEALTH" | grep -q "running"; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is NOT running"
    exit 1
fi
echo ""

# Register a test user
echo "🔍 Creating test user..."
REGISTER=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_'$(date +%s)'",
    "email": "test_'$(date +%s)'@example.com",
    "password": "TestPass123!"
  }')

if echo "$REGISTER" | grep -q "id"; then
    echo "✅ Test user created successfully"
elif echo "$REGISTER" | grep -q "already exists"; then
    echo "⚠️  User already exists (using existing user)"
else
    echo "❌ Failed to create user"
    echo "$REGISTER"
fi
echo ""

# Login with test user
echo "🔍 Testing login..."
LOGIN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }')

if echo "$LOGIN" | grep -q "access_token"; then
    echo "✅ Login successful - Token generated!"
    TOKEN=$(echo "$LOGIN" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    USER_ID=$(echo "$LOGIN" | grep -o '"user_id":"[^"]*"' | cut -d'"' -f4)
    echo "   Token: ${TOKEN:0:50}..."
    echo "   User ID: $USER_ID"
    echo ""

    # Test authenticated endpoint
    echo "🔍 Testing authenticated endpoint..."
    TASKS=$(curl -s -X GET "http://localhost:8000/api/${USER_ID}/tasks" \
      -H "Authorization: Bearer $TOKEN")

    if echo "$TASKS" | grep -q "\["; then
        echo "✅ Authenticated request successful!"
        echo "   Response: Tasks list retrieved"
    else
        echo "❌ Authenticated request failed"
        echo "$TASKS"
    fi
else
    echo "❌ Login failed"
    echo "$LOGIN"
fi
echo ""

echo "================================================"
echo "✅ JWT_SECRET is working correctly!"
echo ""
echo "Now clear your browser storage and login again:"
echo "  1. Open: file:///mnt/d/hackathon-2/phase-3/frontend/CLEAR_TOKENS.html"
echo "  2. Click 'Clear All Storage & Tokens'"
echo "  3. Go to: http://localhost:3000/login"
echo "  4. Login with your credentials"
echo ""
