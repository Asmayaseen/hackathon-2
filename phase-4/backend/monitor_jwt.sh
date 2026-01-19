#!/bin/bash
# Monitor JWT authentication errors in real-time

echo "🔍 Monitoring JWT Authentication Errors..."
echo "📍 Backend logs: /tmp/backend_jwt_debug.log"
echo "---"

tail -f /tmp/backend_jwt_debug.log | grep -E "(JWT|401|✅|❌)" --color=always
