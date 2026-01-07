"""
MCP Server for Evolution Todo - Exposes task operations as AI tools.

Task: T-CHAT-003
Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-4)
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Sequence
import httpx
import os

# Initialize MCP Server
mcp_server = Server("evolution-todo-mcp")

# Internal API base URL
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


@mcp_server.list_tools()
async def list_tools() -> Sequence[Tool]:
    """Return list of available tools for AI agent."""
    return [
        Tool(
            name="add_task",
            description="Create a new task with optional priority, due date, tags, and recurrence",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "title": {"type": "string", "description": "Task title (required)"},
                    "description": {"type": "string", "description": "Task description (optional)"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "none"],
                        "default": "none",
                        "description": "Task priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When task is due (ISO 8601 format)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task tags for categorization"
                    },
                    "recurrence_pattern": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "description": "Recurring pattern for repeating tasks"
                    }
                },
                "required": ["user_id", "title"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Execute tool and return result."""
    if name == "add_task":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE}/api/{arguments['user_id']}/tasks",
                    json={
                        "title": arguments["title"],
                        "description": arguments.get("description"),
                        "priority": arguments.get("priority", "none"),
                        "due_date": arguments.get("due_date"),
                        "tags": arguments.get("tags", []),
                        "recurrence_pattern": arguments.get("recurrence_pattern")
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()

                # Format success message
                message = f"✅ Task created: '{result['title']}' (ID: {result['id']})"
                if result.get('due_date'):
                    message += f"\n📅 Due: {result['due_date']}"
                if result.get('priority') and result['priority'] != 'none':
                    message += f"\n⚡ Priority: {result['priority']}"
                if result.get('tags'):
                    message += f"\n🏷️ Tags: {', '.join(result['tags'])}"

                return [TextContent(type="text", text=message)]
        except httpx.HTTPStatusError as e:
            return [TextContent(
                type="text",
                text=f"❌ Error creating task: {e.response.status_code} - {e.response.text}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error creating task: {str(e)}"
            )]

    # Unknown tool
    return [TextContent(
        type="text",
        text=f"❌ Unknown tool: {name}"
    )]
