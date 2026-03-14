"""
OpenAI Agents SDK — Agent + Runner pattern for Evolution Todo.

Phase III core requirement: uses openai-agents library (NOT raw AsyncOpenAI).
Spec: specs/phase-3-chatbot/spec.md (US-CHAT-1, US-CHAT-7)
Task: T-CHAT-010
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from agents import Agent, Runner, function_tool, RunContextWrapper, set_default_openai_client
from openai import AsyncOpenAI

from intent_classifier import classify_intent, IntentClassifier
from tool_validation import validate_add_task, validate_update_task, validate_language

# ── Client configuration ──────────────────────────────────────────────────────
# Priority: GROQ_API_KEY > OPENAI_API_KEY  (Groq is free!)
if os.getenv("GROQ_API_KEY"):
    _openai_client = AsyncOpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
    set_default_openai_client(_openai_client)
    model_name = "llama-3.3-70b-versatile"
    print(f"🔧 Using Groq API with model: {model_name}")
elif os.getenv("OPENAI_API_KEY"):
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    print(f"🔧 Using OpenAI API with model: {model_name}")
else:
    raise ValueError("Either OPENAI_API_KEY or GROQ_API_KEY must be set")


# ── Run context ───────────────────────────────────────────────────────────────
@dataclass
class TaskContext:
    """Shared state passed to every function tool during a single agent run."""
    user_id: str
    tool_calls: List[Dict] = field(default_factory=list)


# ── Function tools (openai-agents @function_tool pattern) ────────────────────

@function_tool
async def add_task(
    wrapper: RunContextWrapper[TaskContext],
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Create a new task.

    Args:
        title: Task title (required)
        description: Task description
        due_date: Due date in ISO format (YYYY-MM-DD)
        priority: Priority level — high, medium, low, or none
    """
    from mcp_server import call_tool

    args: Dict = {"title": title, "user_id": wrapper.context.user_id}
    if description:
        args["description"] = description
    if due_date:
        args["due_date"] = due_date
    if priority:
        args["priority"] = priority

    try:
        args = validate_add_task(args, title)
    except Exception as e:
        return f"❌ Validation error: {e}"

    result = await call_tool("add_task", args)
    wrapper.context.tool_calls.append({"tool": "add_task", "args": args})
    return result[0].text if result else "Task created"


@function_tool
async def list_tasks(
    wrapper: RunContextWrapper[TaskContext],
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
) -> str:
    """List all tasks.

    Args:
        status: Filter by status — all, pending, or completed
        priority: Filter by priority
        sort_by: Sort field
    """
    from mcp_server import call_tool

    args: Dict = {"user_id": wrapper.context.user_id}
    if status:
        args["status"] = status
    if priority:
        args["priority"] = priority
    if sort_by:
        args["sort_by"] = sort_by

    result = await call_tool("list_tasks", args)
    wrapper.context.tool_calls.append({"tool": "list_tasks", "args": args})
    return result[0].text if result else "No tasks found"


@function_tool
async def complete_task(
    wrapper: RunContextWrapper[TaskContext],
    task_id: int,
) -> str:
    """Mark a task as complete.

    Args:
        task_id: Task ID to complete
    """
    from mcp_server import call_tool

    args = {"task_id": task_id, "user_id": wrapper.context.user_id}
    result = await call_tool("complete_task", args)
    wrapper.context.tool_calls.append({"tool": "complete_task", "args": args})
    return result[0].text if result else "Task completed"


@function_tool
async def delete_task(
    wrapper: RunContextWrapper[TaskContext],
    task_id: int,
) -> str:
    """Delete a task.

    Args:
        task_id: Task ID to delete
    """
    from mcp_server import call_tool

    args = {"task_id": task_id, "user_id": wrapper.context.user_id}
    result = await call_tool("delete_task", args)
    wrapper.context.tool_calls.append({"tool": "delete_task", "args": args})
    return result[0].text if result else "Task deleted"


@function_tool
async def update_task(
    wrapper: RunContextWrapper[TaskContext],
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Update task details.

    Args:
        task_id: Task ID to update
        title: New title
        description: New description
        priority: New priority level
    """
    from mcp_server import call_tool

    args: Dict = {"task_id": task_id, "user_id": wrapper.context.user_id}
    if title:
        args["title"] = title
    if description:
        args["description"] = description
    if priority:
        args["priority"] = priority

    try:
        args = validate_update_task(args)
    except Exception as e:
        return f"❌ Validation error: {e}"

    result = await call_tool("update_task", args)
    wrapper.context.tool_calls.append({"tool": "update_task", "args": args})
    return result[0].text if result else "Task updated"


# ── Agent definition (openai-agents Agent class) ──────────────────────────────
AGENT_INSTRUCTIONS = """You are Evolution Todo Assistant. Help users manage tasks.

Available tools:
- add_task: Create new tasks
- list_tasks: Show tasks (no parameters needed for all tasks)
- complete_task: Mark task complete
- delete_task: Delete task
- update_task: Update task details

Always respond in the same language as the user (English or Urdu)."""

todo_agent = Agent(
    name="Evolution Todo Assistant",
    instructions=AGENT_INSTRUCTIONS,
    tools=[add_task, list_tasks, complete_task, delete_task, update_task],
    model=model_name,
)


# ── Public interface (same signature as before for backward compatibility) ─────
async def run_agent(
    conversation_history: List[Dict[str, str]],
    user_message: str,
    user_id: str,
) -> Tuple[str, List[Dict]]:
    """Run the agent using the OpenAI Agents SDK Runner.run() pattern."""

    # Language guard
    is_valid_language, error_message = validate_language(user_message)
    if not is_valid_language:
        return error_message, []

    # Intent classification (informational — agent decides tool calls)
    intent = classify_intent(user_message, conversation_history)
    confidence = IntentClassifier.get_confidence_score(user_message, intent)
    print(f"🧠 Intent: {intent} (confidence: {confidence:.2f})")

    # Build message list for Runner (last 10 turns + new user message)
    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversation_history[-10:]
    ]
    messages.append({"role": "user", "content": user_message})

    # Context shared across all tool calls in this run
    ctx = TaskContext(user_id=user_id)

    try:
        # ✅ Proper Agents SDK pattern: Runner.run()
        result = await Runner.run(todo_agent, messages, context=ctx)
        return result.final_output, ctx.tool_calls

    except Exception as e:
        error_msg = f"❌ Agent error: {e}"
        print(error_msg)
        return error_msg, []
