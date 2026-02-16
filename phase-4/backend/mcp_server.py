"""
MCP Server for Evolution Todo - Exposes task operations as AI tools.

Task: T-CHAT-003 to T-CHAT-009, T5-302
Spec: specs/phase-3-chatbot/spec.md (FR-CHAT-4), specs/features/phase-v-integration.md
"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Sequence
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
import httpx
import os
import asyncio
import logging
from models import Task
from db import engine

# Phase 5: Event Publishing (T5-302)
try:
    from events import publish_task_event, EventType
    EVENTS_ENABLED = True
except ImportError:
    EVENTS_ENABLED = False
    logging.warning("Events module not available in MCP server")

logger = logging.getLogger(__name__)

# API Base URL for REST API calls
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize MCP Server
mcp_server = Server("evolution-todo-mcp")


@mcp_server.list_tools()
async def list_tools() -> Sequence[Tool]:
    """Return list of available tools for AI agent (11 total)."""
    return [
        # Tool 1: add_task (T-CHAT-004)
        # FIXES: Strict schema validation, description auto-generated, recurrence_pattern strict
        Tool(
            name="add_task",
            description=(
                "Create a new task. IMPORTANT: "
                "1. description is REQUIRED (will be auto-generated if missing) "
                "2. due_date is REQUIRED in ISO format "
                "3. recurrence_pattern: ONLY use for recurring tasks ('daily'|'weekly'|'monthly'). "
                "   For one-time tasks, DO NOT include this field. "
                "4. NEVER send null values"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID (required)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required, 1-200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (required - use title if not provided by user)"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When task is due (required, ISO 8601: YYYY-MM-DDTHH:MM:SS)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "none"],
                        "default": "none",
                        "description": "Task priority level"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task tags for categorization (optional)"
                    },
                    "recurrence_pattern": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "description": (
                            "Recurring pattern ONLY for repeating tasks. "
                            "OMIT this field entirely for one-time tasks. "
                            "Valid: 'daily', 'weekly', 'monthly'"
                        )
                    }
                },
                "required": ["user_id", "title", "description", "due_date"]
            }
        ),

        # Tool 2: list_tasks (T-CHAT-005)
        Tool(
            name="list_tasks",
            description="List all tasks with optional filtering by status, priority, tags, and sorting",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "default": "all",
                        "description": "Filter by completion status"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "none"],
                        "description": "Filter by priority level"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Filter by tags (comma-separated)"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["created", "due_date", "priority", "title"],
                        "default": "created",
                        "description": "Sort tasks by field"
                    },
                    "search": {
                        "type": "string",
                        "description": "Search in task titles and descriptions"
                    }
                },
                "required": ["user_id"]
            }
        ),

        # Tool 3: complete_task (T-CHAT-006)
        Tool(
            name="complete_task",
            description="Mark a task as completed or toggle its completion status",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "task_id": {"type": "integer", "description": "Task ID to complete"}
                },
                "required": ["user_id", "task_id"]
            }
        ),

        # Tool 4: delete_task (T-CHAT-007)
        Tool(
            name="delete_task",
            description="Delete a task permanently",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "task_id": {"type": "integer", "description": "Task ID to delete"}
                },
                "required": ["user_id", "task_id"]
            }
        ),

        # Tool 5: update_task (T-CHAT-008)
        Tool(
            name="update_task",
            description="Update task details (title, description, priority, due date, tags)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "task_id": {"type": "integer", "description": "Task ID to update"},
                    "title": {"type": "string", "description": "New task title"},
                    "description": {"type": "string", "description": "New task description"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "none"],
                        "description": "New priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "New due date (ISO 8601 format)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags list"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),

        # Tool 6: search_tasks (T-CHAT-009 - Bonus)
        Tool(
            name="search_tasks",
            description="Search tasks using full-text search across titles and descriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "query": {"type": "string", "description": "Search query"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "none"],
                        "description": "Filter results by priority"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Filter results by tags (comma-separated)"
                    }
                },
                "required": ["user_id", "query"]
            }
        ),

        # Tool 7: set_priority (T-CHAT-009 - Bonus)
        Tool(
            name="set_priority",
            description="Change the priority level of a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "task_id": {"type": "integer", "description": "Task ID"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "none"],
                        "description": "New priority level"
                    }
                },
                "required": ["user_id", "task_id", "priority"]
            }
        ),

        # Tool 8: add_tags (T-CHAT-009 - Bonus)
        Tool(
            name="add_tags",
            description="Add tags to a task (appends to existing tags)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "task_id": {"type": "integer", "description": "Task ID"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags to add"
                    }
                },
                "required": ["user_id", "task_id", "tags"]
            }
        ),

        # Tool 9: schedule_reminder (T-CHAT-009 - Bonus)
        Tool(
            name="schedule_reminder",
            description="Schedule a reminder notification for a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "task_id": {"type": "integer", "description": "Task ID"},
                    "reminder_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When to send reminder (ISO 8601 format)"
                    }
                },
                "required": ["user_id", "task_id", "reminder_time"]
            }
        ),

        # Tool 10: get_recurring_tasks (T-CHAT-009 - Bonus)
        Tool(
            name="get_recurring_tasks",
            description="Get all recurring tasks, optionally filtered by pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "pattern": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "description": "Filter by recurrence pattern"
                    }
                },
                "required": ["user_id"]
            }
        ),

        # Tool 11: analytics_summary (T-CHAT-009 - Bonus)
        Tool(
            name="analytics_summary",
            description="Get task statistics and analytics summary",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"}
                },
                "required": ["user_id"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Execute tool and return result."""
    user_id = arguments.get("user_id")

    try:
        # Tool 1: add_task (T-CHAT-004)
        # FIXED: Proper handling of recurrence_pattern and description
        if name == "add_task":
            with Session(engine) as session:
                # Build task arguments safely
                task_data = {
                    "user_id": user_id,
                    "title": arguments["title"],
                    "description": arguments.get("description", arguments["title"]),  # Fallback to title
                    "priority": arguments.get("priority", "none"),
                    "tags": arguments.get("tags", [])
                }

                # Add due_date if provided
                if arguments.get("due_date"):
                    task_data["due_date"] = arguments["due_date"]

                # CRITICAL FIX: Only add recurrence_pattern if it's a valid value
                recurrence = arguments.get("recurrence_pattern")
                if recurrence and recurrence in ["daily", "weekly", "monthly"]:
                    task_data["recurrence_pattern"] = recurrence
                    task_data["is_recurring"] = True
                # Don't set recurrence_pattern if it's None, "none", or empty

                task = Task(**task_data)
                session.add(task)
                session.commit()
                session.refresh(task)

                # Phase 5: Publish task created event (T5-302)
                if EVENTS_ENABLED:
                    try:
                        asyncio.create_task(publish_task_event(EventType.CREATED, task, user_id))
                        logger.info(f"MCP: Published CREATED event for task {task.id}")
                    except Exception as e:
                        logger.warning(f"MCP: Event publish failed (non-blocking): {e}")

                # Build response message
                message = f"✅ Task created: '{task.title}' (ID: {task.id})"
                if task.due_date:
                    message += f"\n📅 Due: {task.due_date}"
                if task.priority and task.priority != 'none':
                    message += f"\n⚡ Priority: {task.priority}"
                if task.tags:
                    message += f"\n🏷️ Tags: {', '.join(task.tags)}"
                if task.recurrence_pattern:
                    message += f"\n🔁 Recurring: {task.recurrence_pattern}"

                return [TextContent(type="text", text=message)]

        # Tool 2: list_tasks (T-CHAT-005)
        elif name == "list_tasks":
            with Session(engine) as session:
                query = select(Task).where(Task.user_id == user_id)

                # Apply filters
                if arguments.get("status") == "pending":
                    query = query.where(Task.completed == False)
                elif arguments.get("status") == "completed":
                    query = query.where(Task.completed == True)
                if arguments.get("priority"):
                    query = query.where(Task.priority == arguments["priority"])
                if arguments.get("search"):
                    search = f"%{arguments['search']}%"
                    query = query.where(Task.title.like(search))

                # Execute query
                tasks = session.exec(query).all()

                if not tasks:
                    return [TextContent(type="text", text="📋 No tasks found")]

                message = f"📋 Found {len(tasks)} task(s):\n\n"
                for task in tasks:
                    status = "✅" if task.completed else "⬜"
                    message += f"{status} [{task.id}] {task.title}"
                    if task.priority and task.priority != 'none':
                        message += f" ⚡{task.priority}"
                    if task.due_date:
                        message += f" 📅{str(task.due_date)[:10]}"
                    if task.tags:
                        message += f" 🏷️{','.join(task.tags)}"
                    message += "\n"

                return [TextContent(type="text", text=message)]

        # Tool 3: complete_task (T-CHAT-006, T5-302, T5-500)
        elif name == "complete_task":
            task_id = arguments["task_id"]
            with Session(engine) as session:
                task = session.get(Task, task_id)
                if not task or task.user_id != user_id:
                    return [TextContent(type="text", text=f"❌ Task {task_id} not found")]

                task.completed = not task.completed
                task.updated_at = datetime.now(timezone.utc)
                session.add(task)
                session.commit()
                session.refresh(task)

                # Phase 5: Publish completed event (T5-302)
                if EVENTS_ENABLED:
                    try:
                        event_type = EventType.COMPLETED if task.completed else EventType.UPDATED
                        asyncio.create_task(publish_task_event(event_type, task, user_id))
                    except Exception as e:
                        logger.warning(f"MCP: Event publish failed: {e}")

                status = "completed" if task.completed else "uncompleted"
                message = f"✅ Task '{task.title}' marked as {status}"

                # Phase 5: Auto-create next occurrence for recurring tasks (T5-500)
                if task.completed and task.is_recurring and task.recurrence_pattern:
                    next_task = _create_next_occurrence(task, user_id)
                    if next_task:
                        session.add(next_task)
                        session.commit()
                        session.refresh(next_task)
                        message += f"\n🔁 Next occurrence created: ID {next_task.id}"
                        if next_task.due_date:
                            message += f" (Due: {str(next_task.due_date)[:10]})"

                        # Publish created event for new occurrence
                        if EVENTS_ENABLED:
                            try:
                                asyncio.create_task(publish_task_event(EventType.CREATED, next_task, user_id))
                            except Exception as e:
                                logger.warning(f"MCP: Event publish for recurrence failed: {e}")

                return [TextContent(type="text", text=message)]

        # Tool 4: delete_task (T-CHAT-007)
        elif name == "delete_task":
            task_id = arguments["task_id"]
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{API_BASE}/api/{user_id}/tasks/{task_id}",
                    timeout=10.0
                )
                response.raise_for_status()

                return [TextContent(
                    type="text",
                    text=f"🗑️ Task {task_id} deleted successfully"
                )]

        # Tool 5: update_task (T-CHAT-008)
        elif name == "update_task":
            task_id = arguments["task_id"]
            with Session(engine) as session:
                # Find task
                task = session.get(Task, task_id)
                if not task or task.user_id != user_id:
                    return [TextContent(type="text", text=f"❌ Task {task_id} not found")]

                # Update fields if provided
                if arguments.get("title"):
                    task.title = arguments["title"]
                if arguments.get("description") is not None:
                    task.description = arguments["description"]
                if arguments.get("priority"):
                    task.priority = arguments["priority"]
                if arguments.get("due_date"):
                    task.due_date = arguments["due_date"]
                if arguments.get("tags"):
                    task.tags = arguments["tags"]

                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)

                return [TextContent(
                    type="text",
                    text=f"✏️ Task '{task.title}' updated successfully"
                )]

        # Tool 6: search_tasks (T-CHAT-009 - Bonus)
        elif name == "search_tasks":
            async with httpx.AsyncClient() as client:
                params = {"q": arguments["query"]}
                if arguments.get("priority"):
                    params["priority"] = arguments["priority"]
                if arguments.get("tags"):
                    params["tags"] = arguments["tags"]

                response = await client.get(
                    f"{API_BASE}/api/{user_id}/tasks/search",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                tasks = response.json()

                if not tasks:
                    return [TextContent(type="text", text=f"🔍 No tasks found matching '{arguments['query']}'"

)]

                message = f"🔍 Found {len(tasks)} task(s) matching '{arguments['query']}':\n\n"
                for task in tasks:
                    status = "✅" if task['completed'] else "⬜"
                    message += f"{status} [{task['id']}] {task['title']}\n"

                return [TextContent(type="text", text=message)]

        # Tool 7: set_priority (T-CHAT-009 - Bonus)
        elif name == "set_priority":
            task_id = arguments["task_id"]
            priority = arguments["priority"]

            with Session(engine) as session:
                # Find task
                task = session.get(Task, task_id)
                if not task or task.user_id != user_id:
                    return [TextContent(type="text", text=f"❌ Task {task_id} not found")]

                task.priority = priority
                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)

                return [TextContent(
                    type="text",
                    text=f"⚡ Task '{task.title}' priority set to {priority}"
                )]

        # Tool 8: add_tags (T-CHAT-009 - Bonus)
        elif name == "add_tags":
            task_id = arguments["task_id"]
            new_tags = arguments["tags"]

            with Session(engine) as session:
                # Find task
                task = session.get(Task, task_id)
                if not task or task.user_id != user_id:
                    return [TextContent(type="text", text=f"❌ Task {task_id} not found")]

                # Merge tags
                current_tags = task.tags or []
                merged_tags = list(set(current_tags + new_tags))
                task.tags = merged_tags
                task.updated_at = datetime.utcnow()
                session.add(task)
                session.commit()
                session.refresh(task)

                return [TextContent(
                    type="text",
                    text=f"🏷️ Tags added to '{task.title}': {', '.join(new_tags)}"
                )]

        # Tool 9: schedule_reminder (T-CHAT-009 - Bonus)
        elif name == "schedule_reminder":
            task_id = arguments["task_id"]
            reminder_time = arguments["reminder_time"]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE}/api/{user_id}/notifications",
                    json={
                        "task_id": task_id,
                        "scheduled_time": reminder_time,
                        "notification_type": "reminder"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()

                return [TextContent(
                    type="text",
                    text=f"🔔 Reminder scheduled for {reminder_time}"
                )]

        # Tool 10: get_recurring_tasks (T-CHAT-009 - Bonus)
        elif name == "get_recurring_tasks":
            async with httpx.AsyncClient() as client:
                params = {}
                if arguments.get("pattern"):
                    params["pattern"] = arguments["pattern"]

                response = await client.get(
                    f"{API_BASE}/api/{user_id}/tasks/recurrence",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                tasks = response.json()

                if not tasks:
                    return [TextContent(type="text", text="🔁 No recurring tasks found")]

                message = f"🔁 Found {len(tasks)} recurring task(s):\n\n"
                for task in tasks:
                    pattern = task.get('recurrence_pattern', 'unknown')
                    message += f"🔁 [{task['id']}] {task['title']} - {pattern}\n"

                return [TextContent(type="text", text=message)]

        # Tool 11: analytics_summary (T-CHAT-009 - Bonus)
        elif name == "analytics_summary":
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{API_BASE}/api/{user_id}/stats",
                    timeout=10.0
                )
                response.raise_for_status()
                stats = response.json()

                message = "📊 Task Analytics Summary:\n\n"
                message += f"📋 Total tasks: {stats.get('total_tasks', 0)}\n"
                message += f"✅ Completed: {stats.get('completed_tasks', 0)}\n"
                message += f"⬜ Pending: {stats.get('pending_tasks', 0)}\n"
                message += f"📈 Completion rate: {stats.get('completion_rate', 0)}%\n"

                if stats.get('priority_breakdown'):
                    message += "\n⚡ Priority breakdown:\n"
                    for priority, count in stats['priority_breakdown'].items():
                        message += f"  {priority}: {count}\n"

                if stats.get('overdue_tasks'):
                    message += f"\n⚠️ Overdue tasks: {stats['overdue_tasks']}\n"

                return [TextContent(type="text", text=message)]

        # Unknown tool
        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]

    except httpx.HTTPStatusError as e:
        return [TextContent(
            type="text",
            text=f"❌ API Error ({e.response.status_code}): {e.response.text}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]


def _create_next_occurrence(task: Task, user_id: str):
    """
    Create next occurrence for a recurring task (MCP helper).

    Task: T5-500
    Spec: specs/phase-5/spec.md (US-P5-01)
    """
    if not task.recurrence_pattern:
        return None

    base_date = task.due_date or datetime.now(timezone.utc)

    if task.recurrence_pattern == "daily":
        next_due = base_date + timedelta(days=1)
    elif task.recurrence_pattern == "weekly":
        next_due = base_date + timedelta(weeks=1)
    elif task.recurrence_pattern == "monthly":
        next_due = base_date + timedelta(days=30)
    else:
        return None

    return Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        completed=False,
        due_date=next_due,
        priority=task.priority,
        tags=task.tags or [],
        recurrence_pattern=task.recurrence_pattern,
        is_recurring=True,
        parent_recurring_id=task.id,
        reminder_offset=task.reminder_offset,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
