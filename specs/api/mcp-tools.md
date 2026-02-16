# MCP Tools Specification

**Spec ID**: API-MCP-001
**Created**: 2026-01-10
**Updated**: 2026-02-10
**Status**: Implemented (Phase III - V)
**Server Name**: `evolution-todo-mcp`
**SDK**: Official MCP Python SDK (`mcp>=1.0.0`)

---

## 1. MCP Overview

### 1.1 What is MCP

The **Model Context Protocol (MCP)** is an open protocol that standardizes how applications provide context and tools to Large Language Models. MCP defines a client-server architecture where:

- **MCP Hosts** are applications (IDEs, chat interfaces) that initiate connections
- **MCP Clients** maintain 1:1 connections with MCP servers
- **MCP Servers** expose **tools**, **resources**, and **prompts** to clients

In this project, the MCP server exposes **tools** — model-controlled functions that perform actions and return results. Tools are the primary integration point between the LLM agent and the task management domain.

### 1.2 Protocol Primitives Used

| MCP Primitive | Used | Description |
|---|---|---|
| **Tools** | Yes | 11 tools for task CRUD, search, analytics, and scheduling |
| Resources | No | Not implemented — data access is via tools |
| Prompts | No | Not implemented — system prompts are managed in `agent.py` |
| Sampling | No | Not implemented — LLM calls managed externally via OpenAI SDK |

### 1.3 Server Initialization

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

mcp_server = Server("evolution-todo-mcp")
```

**Source**: `phase-4/backend/mcp_server.py:7-33`

---

## 2. Architecture

### 2.1 System Topology

```
┌──────────────────┐
│   ChatKit UI /   │
│   Chat Endpoint  │
└────────┬─────────┘
         │  HTTP POST /api/{user_id}/chat
         v
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                          │
│                                                              │
│  ┌─────────────────────┐     ┌────────────────────────────┐  │
│  │  routes/chat.py     │────>│  agent.py                  │  │
│  │  routes/chatkit.py  │     │  (OpenAI Agents SDK)       │  │
│  └─────────────────────┘     │                            │  │
│                              │  1. Intent classification   │  │
│                              │  2. LLM call with tools    │  │
│                              │  3. Tool dispatch           │  │
│                              └──────────┬─────────────────┘  │
│                                         │                    │
│                                         │ call_tool(name,    │
│                                         │          arguments)│
│                                         v                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  mcp_server.py  (MCP Server: "evolution-todo-mcp")  │    │
│  │                                                      │    │
│  │  @mcp_server.list_tools()  -> Sequence[Tool]         │    │
│  │  @mcp_server.call_tool()   -> Sequence[TextContent]  │    │
│  │                                                      │    │
│  │  11 Tools:                                           │    │
│  │  ├── add_task          (DB direct)                   │    │
│  │  ├── list_tasks        (DB direct)                   │    │
│  │  ├── complete_task     (DB direct)                   │    │
│  │  ├── delete_task       (REST API)                    │    │
│  │  ├── update_task       (DB direct)                   │    │
│  │  ├── search_tasks      (REST API)                    │    │
│  │  ├── set_priority      (DB direct)                   │    │
│  │  ├── add_tags          (DB direct)                   │    │
│  │  ├── schedule_reminder (REST API)                    │    │
│  │  ├── get_recurring_tasks (REST API)                  │    │
│  │  └── analytics_summary (REST API)                    │    │
│  └────────┬────────────────────────────┬────────────────┘    │
│           │                            │                     │
│           v                            v                     │
│  ┌────────────────┐          ┌──────────────────┐            │
│  │  Neon Postgres │          │  Dapr Pub/Sub    │            │
│  │  (SQLModel)    │          │  (Kafka events)  │            │
│  └────────────────┘          └──────────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Transport Mode

The MCP server runs **in-process** within the FastAPI backend. The agent (`agent.py`) imports `call_tool` directly as a Python function — there is no over-the-wire MCP transport (no stdio, SSE, or HTTP transport). The MCP SDK is used for its type system (`Tool`, `TextContent`) and the decorator-based registration pattern (`@mcp_server.list_tools()`, `@mcp_server.call_tool()`).

### 2.3 Data Access Patterns

Tools use two data access strategies:

| Strategy | Tools | Mechanism |
|---|---|---|
| **Direct DB** | `add_task`, `list_tasks`, `complete_task`, `update_task`, `set_priority`, `add_tags` | SQLModel `Session(engine)` |
| **REST API** | `delete_task`, `search_tasks`, `schedule_reminder`, `get_recurring_tasks`, `analytics_summary` | `httpx.AsyncClient` to `API_BASE_URL` |

**Source**: `phase-4/backend/mcp_server.py:29-30`

---

## 3. Tool Registration Format

### 3.1 MCP `list_tools` Handler

Tools are registered via the `@mcp_server.list_tools()` decorator. The handler returns a `Sequence[Tool]` where each `Tool` has:

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Unique tool identifier (snake_case) |
| `description` | `str` | Natural language description for the LLM |
| `inputSchema` | `dict` | JSON Schema object defining accepted parameters |

```python
@mcp_server.list_tools()
async def list_tools() -> Sequence[Tool]:
    return [
        Tool(
            name="add_task",
            description="Create a new task. IMPORTANT: ...",
            inputSchema={
                "type": "object",
                "properties": { ... },
                "required": ["user_id", "title", "description", "due_date"]
            }
        ),
        # ... 10 more tools
    ]
```

### 3.2 MCP `call_tool` Handler

Tool execution is registered via `@mcp_server.call_tool()`. The handler receives `(name: str, arguments: dict)` and returns `Sequence[TextContent]`.

```python
@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    user_id = arguments.get("user_id")
    # ... dispatch by name, return TextContent results
```

### 3.3 Agent-Side Tool Schema (OpenAI Function Calling Format)

The agent (`agent.py`) exposes a **subset of 5 tools** to the LLM using OpenAI function calling format. The LLM sees these schemas and decides which tools to invoke:

```python
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": { ... },
                "required": ["title"]
            }
        }
    },
    # list_tasks, complete_task, delete_task, update_task
]
```

The agent injects `user_id` into arguments before calling `call_tool()`:

```python
args["user_id"] = user_id  # Injected, not from LLM
result = await call_tool(tool_name, args)
```

**Source**: `phase-4/backend/agent.py:53-131`, `phase-4/backend/agent.py:186-198`

---

## 4. Tool Catalog (11 Tools)

### 4.1 `add_task`

**Purpose**: Create a new task for the authenticated user.
**Task Ref**: T-CHAT-004
**Data Access**: Direct DB (SQLModel)
**Events**: Publishes `CREATED` to Dapr pub/sub (Phase V)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id":            { "type": "string",  "description": "User ID (required)" },
    "title":              { "type": "string",  "description": "Task title (required, 1-200 characters)" },
    "description":        { "type": "string",  "description": "Task description (required - use title if not provided by user)" },
    "due_date":           { "type": "string",  "format": "date-time", "description": "When task is due (required, ISO 8601)" },
    "priority":           { "type": "string",  "enum": ["low","medium","high","none"], "default": "none" },
    "tags":               { "type": "array",   "items": {"type": "string"} },
    "recurrence_pattern": { "type": "string",  "enum": ["daily","weekly","monthly"], "description": "OMIT for one-time tasks" }
  },
  "required": ["user_id", "title", "description", "due_date"]
}
```

#### Output

```
TextContent: "✅ Task created: '{title}' (ID: {id})\n📅 Due: {due_date}\n⚡ Priority: {priority}\n🏷️ Tags: {tags}\n🔁 Recurring: {pattern}"
```

#### Example Invocation

```python
await call_tool("add_task", {
    "user_id": "user-123",
    "title": "Buy groceries",
    "description": "Task: Buy groceries",
    "due_date": "2026-02-15T14:00:00",
    "priority": "high",
    "tags": ["shopping"]
})
# => [TextContent(text="✅ Task created: 'Buy groceries' (ID: 5)\n📅 Due: 2026-02-15 14:00:00\n⚡ Priority: high\n🏷️ Tags: shopping")]
```

---

### 4.2 `list_tasks`

**Purpose**: Retrieve user's tasks with optional filtering and sorting.
**Task Ref**: T-CHAT-005
**Data Access**: Direct DB (SQLModel)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id":  { "type": "string" },
    "status":   { "type": "string", "enum": ["all","pending","completed"], "default": "all" },
    "priority": { "type": "string", "enum": ["low","medium","high","none"] },
    "tags":     { "type": "string", "description": "Comma-separated tag filter" },
    "sort_by":  { "type": "string", "enum": ["created","due_date","priority","title"], "default": "created" },
    "search":   { "type": "string", "description": "Search in titles and descriptions" }
  },
  "required": ["user_id"]
}
```

#### Output

```
TextContent: "📋 Found {n} task(s):\n\n⬜ [1] Buy groceries ⚡high 📅2026-02-15 🏷️shopping\n✅ [2] Call mom"
```

#### Example Invocation

```python
await call_tool("list_tasks", {
    "user_id": "user-123",
    "status": "pending",
    "sort_by": "due_date"
})
```

---

### 4.3 `complete_task`

**Purpose**: Toggle task completion status (complete/uncomplete).
**Task Ref**: T-CHAT-006
**Data Access**: Direct DB (SQLModel)
**Events**: Publishes `COMPLETED` or `UPDATED` to Dapr pub/sub (Phase V)
**Side Effects**: For recurring tasks, auto-creates next occurrence (Phase V, T5-500)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "task_id": { "type": "integer", "description": "Task ID to complete" }
  },
  "required": ["user_id", "task_id"]
}
```

#### Output

```
TextContent: "✅ Task '{title}' marked as completed"
TextContent: "✅ Task '{title}' marked as completed\n🔁 Next occurrence created: ID {next_id} (Due: {date})"
```

#### Example Invocation

```python
await call_tool("complete_task", {"user_id": "user-123", "task_id": 5})
```

---

### 4.4 `delete_task`

**Purpose**: Permanently remove a task.
**Task Ref**: T-CHAT-007
**Data Access**: REST API (`DELETE /api/{user_id}/tasks/{task_id}`)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "task_id": { "type": "integer", "description": "Task ID to delete" }
  },
  "required": ["user_id", "task_id"]
}
```

#### Output

```
TextContent: "🗑️ Task {task_id} deleted successfully"
```

#### Example Invocation

```python
await call_tool("delete_task", {"user_id": "user-123", "task_id": 3})
```

---

### 4.5 `update_task`

**Purpose**: Modify task fields (title, description, priority, due date, tags).
**Task Ref**: T-CHAT-008
**Data Access**: Direct DB (SQLModel)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id":     { "type": "string" },
    "task_id":     { "type": "integer", "description": "Task ID to update" },
    "title":       { "type": "string" },
    "description": { "type": "string" },
    "priority":    { "type": "string", "enum": ["low","medium","high","none"] },
    "due_date":    { "type": "string", "format": "date-time" },
    "tags":        { "type": "array", "items": {"type": "string"} }
  },
  "required": ["user_id", "task_id"]
}
```

#### Output

```
TextContent: "✏️ Task '{title}' updated successfully"
```

#### Example Invocation

```python
await call_tool("update_task", {
    "user_id": "user-123",
    "task_id": 1,
    "title": "Buy groceries and fruits",
    "priority": "medium"
})
```

---

### 4.6 `search_tasks`

**Purpose**: Full-text search across task titles and descriptions.
**Task Ref**: T-CHAT-009
**Data Access**: REST API (`GET /api/{user_id}/tasks/search?q=...`)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id":  { "type": "string" },
    "query":    { "type": "string", "description": "Search query" },
    "priority": { "type": "string", "enum": ["low","medium","high","none"] },
    "tags":     { "type": "string", "description": "Comma-separated tag filter" }
  },
  "required": ["user_id", "query"]
}
```

#### Output

```
TextContent: "🔍 Found {n} task(s) matching '{query}':\n\n⬜ [1] Buy groceries\n✅ [2] Grocery list"
```

#### Example Invocation

```python
await call_tool("search_tasks", {"user_id": "user-123", "query": "groceries"})
```

---

### 4.7 `set_priority`

**Purpose**: Change the priority level of a specific task.
**Task Ref**: T-CHAT-009
**Data Access**: Direct DB (SQLModel)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id":  { "type": "string" },
    "task_id":  { "type": "integer" },
    "priority": { "type": "string", "enum": ["low","medium","high","none"] }
  },
  "required": ["user_id", "task_id", "priority"]
}
```

#### Output

```
TextContent: "⚡ Task '{title}' priority set to {priority}"
```

#### Example Invocation

```python
await call_tool("set_priority", {"user_id": "user-123", "task_id": 1, "priority": "high"})
```

---

### 4.8 `add_tags`

**Purpose**: Append tags to a task (merges with existing, deduplicates).
**Task Ref**: T-CHAT-009
**Data Access**: Direct DB (SQLModel)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "task_id": { "type": "integer" },
    "tags":    { "type": "array", "items": {"type": "string"}, "description": "Tags to add" }
  },
  "required": ["user_id", "task_id", "tags"]
}
```

#### Output

```
TextContent: "🏷️ Tags added to '{title}': {new_tags}"
```

#### Example Invocation

```python
await call_tool("add_tags", {"user_id": "user-123", "task_id": 1, "tags": ["urgent", "work"]})
```

---

### 4.9 `schedule_reminder`

**Purpose**: Schedule a reminder notification for a task at a specific time.
**Task Ref**: T-CHAT-009
**Data Access**: REST API (`POST /api/{user_id}/notifications`)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id":       { "type": "string" },
    "task_id":       { "type": "integer" },
    "reminder_time": { "type": "string", "format": "date-time", "description": "When to send reminder (ISO 8601)" }
  },
  "required": ["user_id", "task_id", "reminder_time"]
}
```

#### Output

```
TextContent: "🔔 Reminder scheduled for {reminder_time}"
```

#### Example Invocation

```python
await call_tool("schedule_reminder", {
    "user_id": "user-123",
    "task_id": 1,
    "reminder_time": "2026-02-15T13:30:00Z"
})
```

---

### 4.10 `get_recurring_tasks`

**Purpose**: List recurring tasks, optionally filtered by recurrence pattern.
**Task Ref**: T-CHAT-009
**Data Access**: REST API (`GET /api/{user_id}/tasks/recurrence`)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "pattern": { "type": "string", "enum": ["daily","weekly","monthly"] }
  },
  "required": ["user_id"]
}
```

#### Output

```
TextContent: "🔁 Found {n} recurring task(s):\n\n🔁 [1] Daily standup - daily\n🔁 [2] Weekly review - weekly"
```

#### Example Invocation

```python
await call_tool("get_recurring_tasks", {"user_id": "user-123", "pattern": "weekly"})
```

---

### 4.11 `analytics_summary`

**Purpose**: Get task statistics and analytics overview.
**Task Ref**: T-CHAT-009
**Data Access**: REST API (`GET /api/{user_id}/stats`)

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" }
  },
  "required": ["user_id"]
}
```

#### Output

```
TextContent: "📊 Task Analytics Summary:\n\n📋 Total tasks: 15\n✅ Completed: 8\n⬜ Pending: 7\n📈 Completion rate: 53%\n\n⚡ Priority breakdown:\n  high: 3\n  medium: 5\n  low: 4\n  none: 3\n\n⚠️ Overdue tasks: 2"
```

#### Example Invocation

```python
await call_tool("analytics_summary", {"user_id": "user-123"})
```

---

## 5. Agent Integration

### 5.1 Tool Invocation Flow

```
User message
    │
    v
┌───────────────────────────────┐
│  1. Language validation       │  tool_validation.validate_language()
│     (English/Urdu only)       │
└───────────────┬───────────────┘
                │
                v
┌───────────────────────────────┐
│  2. Intent classification     │  intent_classifier.classify_intent()
│     ADD_TASK | UPDATE_TASK |  │  Multilingual keyword matching
│     DELETE | LIST | COMPLETE  │  (English, Roman Urdu, Urdu)
│     SEARCH | ANALYTICS        │
└───────────────┬───────────────┘
                │
                v
┌───────────────────────────────┐
│  3. LLM call (OpenAI/Groq)   │  client.chat.completions.create(
│     with MCP_TOOLS schemas    │      tools=MCP_TOOLS,
│                               │      tool_choice="auto")
└───────────────┬───────────────┘
                │
                │  LLM returns tool_calls[]
                v
┌───────────────────────────────┐
│  4. Argument validation       │  validate_add_task() / validate_update_task()
│     + user_id injection       │  args["user_id"] = user_id
└───────────────┬───────────────┘
                │
                v
┌───────────────────────────────┐
│  5. MCP call_tool() dispatch  │  from mcp_server import call_tool
│                               │  result = await call_tool(name, args)
└───────────────┬───────────────┘
                │
                │  TextContent[] result
                v
┌───────────────────────────────┐
│  6. Tool result fed back to   │  messages.append({
│     LLM for natural language  │      "role": "tool",
│     response generation       │      "content": result_text})
└───────────────┬───────────────┘
                │
                v
            Final response to user
```

**Source**: `phase-4/backend/agent.py:145-222`

### 5.2 LLM-Visible vs Full Tool Set

| Scope | Tools | Format | Purpose |
|---|---|---|---|
| **LLM-visible** (agent.py `MCP_TOOLS`) | 5 tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task` | OpenAI function calling | Sent to LLM as tool schemas |
| **Full MCP server** (mcp_server.py) | 11 tools (all above + `search_tasks`, `set_priority`, `add_tags`, `schedule_reminder`, `get_recurring_tasks`, `analytics_summary`) | MCP `Tool` type | Available for direct invocation |

The 6 additional tools in the MCP server are available for direct programmatic use but are not currently exposed to the LLM via the `MCP_TOOLS` list.

### 5.3 Intent-to-Tool Mapping

| User Intent | Classified As | Tool(s) Called |
|---|---|---|
| "Add a task to buy groceries" | `ADD_TASK` | `add_task` |
| "Show me all my tasks" | `LIST_TASKS` | `list_tasks` (status=all) |
| "What's pending?" | `LIST_TASKS` | `list_tasks` (status=pending) |
| "Mark task 3 as complete" | `COMPLETE_TASK` | `complete_task` (task_id=3) |
| "Delete the meeting task" | `DELETE_TASK` | `delete_task` |
| "Change task 1 title to 'Call mom'" | `UPDATE_TASK` | `update_task` (task_id=1, title=...) |
| "Set task 2 to high priority" | `UPDATE_TASK` | `set_priority` (task_id=2, priority=high) |
| "Tag task 1 with 'urgent'" | `UNCLEAR` | `add_tags` (task_id=1, tags=["urgent"]) |
| "Find tasks about meeting" | `SEARCH` | `search_tasks` (query="meeting") |
| "Remind me about task 1 at 2pm" | `ADD_TASK` | `schedule_reminder` |
| "Show my recurring tasks" | `LIST_TASKS` | `get_recurring_tasks` |
| "How am I doing?" | `ANALYTICS` | `analytics_summary` |

---

## 6. Security and Isolation

### 6.1 User Isolation (Tenant Boundary)

Every tool requires `user_id` as a mandatory parameter. Ownership checks are enforced at two levels:

1. **Agent-level**: `user_id` is injected by the agent (`agent.py:187`) from the authenticated session, never supplied by the LLM. The LLM tool schemas in `MCP_TOOLS` omit `user_id` from their `properties` entirely.

2. **Tool-level**: Direct DB tools filter by `user_id` in queries (`Task.user_id == user_id`). Tools that locate tasks by ID verify `task.user_id != user_id` before proceeding, returning "Task not found" on mismatch.

```python
# agent.py — user_id injected, not from LLM
args["user_id"] = user_id

# mcp_server.py — ownership check on every DB tool
task = session.get(Task, task_id)
if not task or task.user_id != user_id:
    return [TextContent(type="text", text=f"❌ Task {task_id} not found")]
```

### 6.2 Input Validation Layer

A `ToolValidator` class (`tool_validation.py`) sanitizes arguments before MCP tool execution:

| Validation | Applies To | Behavior |
|---|---|---|
| Null removal | All tools | `{k: v for k, v in args.items() if v is not None}` |
| Description auto-gen | `add_task` | Generates from title or user message if missing |
| Recurrence sanitization | `add_task` | Removes `"none"`, `null`, `""` values; validates against `["daily","weekly","monthly"]` |
| Priority validation | `add_task`, `update_task` | Rejects invalid values, defaults to `"none"` |
| ISO date validation | `add_task`, `update_task` | Parses and normalizes via `datetime.fromisoformat()` |
| Tags list check | `add_task`, `update_task` | Ensures array type, removes empty strings |

### 6.3 Language Validation

Messages are validated for supported languages (English, Urdu) before reaching the LLM. Hindi and other unsupported languages are rejected with an error response.

### 6.4 No Secret Exposure

- API keys (`GROQ_API_KEY`, `OPENAI_API_KEY`) are sourced from environment variables, never included in tool schemas or responses.
- Database connection strings are managed via `db.py` and `engine`, not exposed to the MCP tool layer.
- `API_BASE_URL` defaults to `http://localhost:8000` and is configurable via environment.

---

## 7. Failure Handling

### 7.1 Error Response Format

All tools return errors as `TextContent` with descriptive messages. Errors never propagate as exceptions to the caller — they are always caught and returned as text.

```python
except httpx.HTTPStatusError as e:
    return [TextContent(type="text", text=f"❌ API Error ({e.response.status_code}): {e.response.text}")]
except Exception as e:
    return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
```

### 7.2 Error Categories

| Error | Trigger | Response |
|---|---|---|
| Task not found | `task_id` invalid or belongs to another user | `"❌ Task {task_id} not found"` |
| Unknown tool | `name` does not match any registered tool | `"❌ Unknown tool: {name}"` |
| HTTP status error | REST API call returns non-2xx | `"❌ API Error ({status}): {body}"` |
| General exception | Any unhandled exception | `"❌ Error: {message}"` |
| Validation error | Pre-execution validation fails in agent | `"❌ Validation error: {message}"` |
| Language not supported | Unsupported language detected | Error message in detected language |

### 7.3 JSON Schema Validation

Missing required fields are rejected by JSON Schema validation before tool execution reaches the `call_tool` handler. The MCP SDK validates `inputSchema` constraints against the provided `arguments` dict.

### 7.4 Event Publishing Failures

Phase V event publishing is **non-blocking** (fire-and-forget). Tool execution succeeds even if event publish fails:

```python
if EVENTS_ENABLED:
    try:
        asyncio.create_task(publish_task_event(EventType.CREATED, task, user_id))
    except Exception as e:
        logger.warning(f"MCP: Event publish failed (non-blocking): {e}")
```

If the `events` module is not importable (e.g., running without Phase V dependencies), `EVENTS_ENABLED` is set to `False` at startup and event publishing is skipped entirely.

### 7.5 REST API Timeouts

Tools using `httpx.AsyncClient` set a 10-second timeout on all outbound HTTP requests:

```python
response = await client.get(url, timeout=10.0)
```

---

## 8. Phase V Event Integration

When `EVENTS_ENABLED=True`, mutation tools publish domain events to Kafka via the Dapr pub/sub HTTP API:

| Tool | Event Type | Dapr Topic | Fire-and-Forget |
|---|---|---|---|
| `add_task` | `CREATED` | `task-events` | Yes |
| `complete_task` | `COMPLETED` / `UPDATED` | `task-events` | Yes |
| `complete_task` (recurring) | `CREATED` (next occurrence) | `task-events` | Yes |

### Event Payload Schema

```json
{
  "event_type": "created",
  "task_id": 5,
  "task_data": {
    "id": 5,
    "title": "Buy groceries",
    "description": "Task: Buy groceries",
    "completed": false,
    "due_date": "2026-02-15T14:00:00",
    "priority": "high",
    "tags": ["shopping"],
    "recurrence_pattern": null,
    "is_recurring": false
  },
  "user_id": "user-123",
  "timestamp": "2026-02-10T12:00:00Z"
}
```

**Source**: `phase-4/backend/events/schemas.py`, `phase-4/backend/events/publisher.py`

---

## 9. Testing

### 9.1 Integration Tests

MCP tools are tested via `@pytest.mark.mcp` markers:

- `TestMCPToolList` — verifies all 11 tools returned, validates each has `name`, `description`, `inputSchema` with `user_id` required
- `TestMCPAddTask` — creates tasks via `call_tool()`, verifies DB persistence
- `TestMCPListTasks` — tests listing and filtering

**Source**: `phase-4/backend/tests/integration/test_mcp_server.py`

### 9.2 Agent Unit Tests

Agent tests mock both the LLM client and MCP tools:

- Simple responses (no tool calls)
- Tool call execution with `user_id` injection
- Multiple tool calls in sequence
- Error handling

**Source**: `phase-4/backend/tests/unit/test_agent.py`

---

## 10. Related Specs

- `specs/features/task-crud.md` — CRUD feature requirements
- `specs/api/rest-endpoints.md` — REST API that MCP tools operate alongside
- `specs/features/chatbot.md` — Chatbot architecture and conversation flow
- `specs/features/phase-v-integration.md` — Event-driven extensions

---

## Revision History

| Date | Change | Author |
|---|---|---|
| 2026-01-10 | Initial draft for Phase III | spec-kit |
| 2026-02-10 | Complete rewrite: official MCP terminology, full input/output schemas for all 11 tools, architecture diagrams, security model, failure handling, agent integration flow, event integration, example invocations | claude-code |
