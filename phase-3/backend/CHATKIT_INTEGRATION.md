# ChatKit Backend Integration Guide

**Evolution Todo - Phase III AI Chatbot**

This document explains how to integrate the ChatKit Python backend server with your frontend application.

---

## Architecture Overview

```
┌─────────────────────┐
│  ChatKit Frontend   │ (Next.js + @openai/chatkit)
│  (User Interface)   │
└──────────┬──────────┘
           │ HTTPS + JWT
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  (Authentication)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ChatKitServer      │ (chatkit_server.py)
│  (Request Context)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  OpenAI Agent SDK   │ (agent.py)
│  (AI Processing)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MCP Tools          │ (mcp_server.py)
│  (Task Operations)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Neon PostgreSQL    │
│  (State Storage)    │
└─────────────────────┘
```

**Key Principles:**
- **Stateless Architecture**: All conversation state in database
- **User Isolation**: RequestContext ensures user data separation
- **MCP Integration**: 11 task management tools accessible via natural language
- **JWT Authentication**: Secure user authentication on all requests

---

## Backend Components

### 1. ChatKitServer (`chatkit_server.py`)

**Purpose**: Extends OpenAI's `ChatKitServer[RequestContext]` to process chat messages.

**Key Methods:**
- `respond()`: Process user messages, call AI agent, stream responses
- `get_threads()`: List all conversations for a user
- `get_thread_messages()`: Get message history for a conversation
- `delete_thread()`: Delete conversation and all messages

**User Isolation:**
```python
@dataclass
class TodoRequestContext(RequestContext):
    user_id: str  # Authenticated user ID from JWT
    user_name: Optional[str] = None
    user_email: Optional[str] = None
```

### 2. Store Contract (`chatkit_store.py`)

**Purpose**: Database persistence layer for conversations and messages.

**Operations:**
- `create_conversation(user_id)`: Create new conversation thread
- `add_message(conversation_id, user_id, role, content)`: Store message
- `get_messages(conversation_id, user_id)`: Retrieve message history
- `get_conversation_history(conversation_id, user_id)`: Get OpenAI-format history

**Stateless Design:**
- No in-memory state on server
- All data persisted to PostgreSQL
- Server restart does NOT lose conversations
- Horizontal scaling enabled (K8s-ready)

### 3. API Endpoints (`main.py`)

**ChatKit Session Endpoint:**
```http
POST /api/chatkit/session
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "user_id": "user_abc123"
}
```

**Response:**
```json
{
  "client_secret": "random_secure_token",
  "server_url": "http://localhost:8000/api/chatkit"
}
```

**Other Endpoints:**
- `POST /api/chatkit/respond`: Process chat message
- `GET /api/chatkit/threads`: List all threads
- `GET /api/chatkit/threads/{thread_id}/messages`: Get thread messages
- `DELETE /api/chatkit/threads/{thread_id}`: Delete thread

---

## Frontend Integration

### Step 1: Install ChatKit Dependencies

```bash
npm install @openai/chatkit
```

### Step 2: Create ChatKit Session Hook

**File: `hooks/useChatKitSession.ts`**

```typescript
import { useState, useEffect } from 'react';
import { useChatKit } from '@openai/chatkit';

export function useChatKitSession(userId: string, jwtToken: string) {
  const [session, setSession] = useState<{
    clientSecret: string;
    serverUrl: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function createSession() {
      try {
        const response = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${jwtToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ user_id: userId })
        });

        if (!response.ok) {
          throw new Error('Failed to create ChatKit session');
        }

        const data = await response.json();
        setSession(data);
      } catch (err) {
        setError(err.message);
      }
    }

    if (userId && jwtToken) {
      createSession();
    }
  }, [userId, jwtToken]);

  return { session, error };
}
```

### Step 3: Initialize ChatKit in Your Component

**File: `components/ChatWidget.tsx`**

```typescript
'use client';

import { useChatKit } from '@openai/chatkit';
import { useChatKitSession } from '@/hooks/useChatKitSession';

export default function ChatWidget({
  userId,
  jwtToken
}: {
  userId: string;
  jwtToken: string;
}) {
  // 1. Create ChatKit session
  const { session, error } = useChatKitSession(userId, jwtToken);

  // 2. Initialize ChatKit
  const chatkit = useChatKit({
    clientSecret: session?.clientSecret,
    serverUrl: session?.serverUrl,
    // Custom fetch interceptor to add JWT auth
    fetch: async (url, options) => {
      return fetch(url, {
        ...options,
        headers: {
          ...options?.headers,
          'Authorization': `Bearer ${jwtToken}`
        }
      });
    }
  });

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!session) {
    return <div>Loading ChatKit session...</div>;
  }

  return (
    <div className="chatkit-container">
      <chatkit.ChatInterface
        onMessageSend={(message) => {
          console.log('Message sent:', message);
        }}
        placeholder="Ask me to manage your tasks..."
      />
    </div>
  );
}
```

### Step 4: Add ChatKit to Your App

**File: `app/chat/page.tsx`**

```typescript
import { auth } from '@/lib/auth'; // Your auth library
import ChatWidget from '@/components/ChatWidget';

export default async function ChatPage() {
  const session = await auth();

  if (!session) {
    return <div>Please login to access chat</div>;
  }

  return (
    <div>
      <h1>Evolution Todo Chatbot</h1>
      <ChatWidget
        userId={session.user.id}
        jwtToken={session.accessToken}
      />
    </div>
  );
}
```

---

## Environment Variables

**Backend (`.env`):**

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# JWT Authentication
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256

# OpenAI / Groq API
GROQ_API_KEY=gsk_xxx  # Or OPENAI_API_KEY
GROQ_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=openai/gpt-oss-20b  # Or gpt-4o-2024-11-20

# ChatKit Server
CHATKIT_SERVER_URL=http://localhost:8000/api/chatkit

# Internal API (for MCP tools)
API_BASE_URL=http://localhost:8000

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

**Frontend (`.env.local`):**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## MCP Tools Available

The chatbot can perform these task operations via natural language:

1. **add_task** - Create new tasks with priority, tags, due dates, recurrence
2. **list_tasks** - List tasks with filtering (status, priority, tags)
3. **complete_task** - Mark tasks as completed
4. **delete_task** - Delete tasks permanently
5. **update_task** - Update task details (title, description, etc.)
6. **search_tasks** - Full-text search across tasks
7. **set_priority** - Change task priority
8. **add_tags** - Add tags to tasks
9. **schedule_reminder** - Schedule reminder notifications
10. **get_recurring_tasks** - List recurring tasks
11. **analytics_summary** - Get task statistics

**Example Conversations:**

```
User: "Add a task to buy groceries tomorrow at 5 PM"
AI: ✅ Task created: 'Buy groceries' due 2026-01-07 at 5 PM

User: "Show me all my high priority tasks"
AI: 📋 Found 3 high priority task(s):
    ⬜ [1] Review PR #42 ⚡high 📅2026-01-07
    ⬜ [5] Client meeting ⚡high 📅2026-01-08
    ✅ [12] Deploy Phase III ⚡high

User: "Mark task 1 as done"
AI: ✅ Task 'Review PR #42' marked as completed

User: "میری تمام فہرست دکھائیں" (Urdu: "Show me all my tasks")
AI: 📋 آپ کے 15 کام:
    ⬜ [1] گروسری خریدنا
    ✅ [2] کلائنٹ کال
    ...
```

---

## Testing the Integration

### 1. Start Backend Server

```bash
cd /mnt/d/hackathon-2/phase-3/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Session Creation

```bash
# Get JWT token (from login endpoint)
export JWT_TOKEN="your_jwt_token_here"

# Create ChatKit session
curl -X POST http://localhost:8000/api/chatkit/session \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_123"}'

# Expected response:
{
  "client_secret": "random_secure_token",
  "server_url": "http://localhost:8000/api/chatkit"
}
```

### 3. Test Chat Request

```bash
curl -X POST http://localhost:8000/api/chatkit/respond \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": null,
    "message": "Add a task to test the chatbot"
  }'
```

### 4. Test Thread Listing

```bash
curl -X GET http://localhost:8000/api/chatkit/threads \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## Database Schema

**Conversations Table:**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
```

**Messages Table:**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    role VARCHAR NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_user ON messages(user_id);
```

---

## Security Considerations

### 1. JWT Authentication
- All ChatKit endpoints require valid JWT token
- Token must contain `user_id` in payload
- Tokens expire and must be refreshed

### 2. User Isolation
- `RequestContext.user_id` enforced on all operations
- Database queries filtered by `user_id`
- Users can ONLY access their own conversations and tasks

### 3. Input Sanitization
- All user messages sanitized before processing
- SQL injection prevented by SQLModel parameterized queries
- XSS prevented by proper HTML encoding in frontend

### 4. Rate Limiting
- Recommended: 10 requests/second per user
- Implement using FastAPI middleware or API gateway

---

## Troubleshooting

### Issue: "ChatKit session creation fails"
**Solution**: Verify JWT token is valid and contains `user_id` in payload.

```python
# Decode JWT to check payload
import jwt
payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
print(payload)  # Should contain 'user_id'
```

### Issue: "Conversation history not loading"
**Solution**: Check database connection and verify Conversation/Message models are created.

```bash
# Check database tables
psql $DATABASE_URL -c "\dt"

# Should show: conversations, messages, tasks, users, etc.
```

### Issue: "AI agent not calling MCP tools"
**Solution**: Verify MCP server is running and tools are registered.

```python
# Test MCP tools
from mcp_server import list_tools
tools = await list_tools()
print(f"Available tools: {[t.name for t in tools]}")
```

### Issue: "Server restart loses conversations"
**Solution**: This should NOT happen. If it does, check:
1. Database connection is persistent (not in-memory SQLite)
2. `create_db_and_tables()` includes Conversation and Message models
3. No in-memory session storage in chatkit_server.py

---

## Performance Optimization

### 1. Database Connection Pooling
Already configured in `db.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections
    pool_size=10,         # Max connections
    max_overflow=20       # Overflow connections
)
```

### 2. Conversation History Caching
For very long conversations (100+ messages), consider:
- Loading only last 50 messages for context
- Summarizing older messages
- Pagination in `get_messages()`

### 3. Async Processing
All endpoints are async (`async def`) for concurrent request handling.

---

## Next Steps

1. **Frontend Implementation**: Build ChatKit UI in Next.js
2. **Voice Input**: Add Whisper API for speech-to-text
3. **Urdu Language**: Test bilingual support
4. **Deployment**: Deploy to Vercel (frontend) and Hugging Face Spaces (backend)
5. **Monitoring**: Add logging, metrics, and error tracking

---

## Support

- **Documentation**: `/specs/phase-3-chatbot/spec.md`
- **Code References**:
  - Backend: `/phase-3/backend/chatkit_server.py`
  - Store: `/phase-3/backend/chatkit_store.py`
  - Endpoints: `/phase-3/backend/main.py`
  - Agent: `/phase-3/backend/agent.py`
  - MCP Tools: `/phase-3/backend/mcp_server.py`

**Status**: ✅ Backend implementation complete and ready for frontend integration.
