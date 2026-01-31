"""
OpenAI Agents SDK pattern integration for Evolution Todo.

Task: T-CHAT-010
Spec: specs/phase-3-chatbot/spec.md (US-CHAT-1, US-CHAT-7)

Uses OpenAI SDK with function tools for task management.
"""
from openai import AsyncOpenAI
import os
from typing import List, Dict, Tuple, Optional
import json

# Import validation and intent classification
from intent_classifier import classify_intent, IntentClassifier
from tool_validation import (
    validate_add_task,
    validate_update_task,
    validate_language,
    ToolValidator
)

# Default model name constant (for tests and fallback)
MODEL_NAME = "gpt-4o-mini"

# Configure client for OpenAI or Groq
# Priority: GROQ_API_KEY > OPENAI_API_KEY
if os.getenv("GROQ_API_KEY"):
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1"
    model_name = "llama-3.3-70b-versatile"
    MODEL_NAME = model_name  # Update constant
    print(f"🔧 Using Groq API with model: {model_name}")
elif os.getenv("OPENAI_API_KEY"):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = None
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    MODEL_NAME = model_name  # Update constant
    print(f"🔧 Using OpenAI API with model: {model_name}")
elif os.getenv("ENVIRONMENT") == "test":
    # Test mode - mock client
    api_key = "test-key"
    base_url = None
    model_name = MODEL_NAME
    print(f"🧪 Test mode with mock model: {model_name}")
else:
    raise ValueError("Either OPENAI_API_KEY or GROQ_API_KEY must be set")

# Create OpenAI client
client = AsyncOpenAI(api_key=api_key, base_url=base_url)

# Define MCP tools schema for function calling
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title (required)"},
                    "description": {"type": "string", "description": "Task description"},
                    "due_date": {"type": "string", "description": "Due date in ISO format"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low", "none"], "description": "Priority level"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter by status"},
                    "priority": {"type": "string", "description": "Filter by priority"},
                    "sort_by": {"type": "string", "description": "Sort field"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID to complete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID to delete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task details",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID to update"},
                    "title": {"type": "string", "description": "New title"},
                    "description": {"type": "string", "description": "New description"},
                    "priority": {"type": "string", "description": "New priority"}
                },
                "required": ["task_id"]
            }
        }
    }
]

AGENT_INSTRUCTIONS = """You are Evolution Todo Assistant. Help users manage tasks.

Available tools:
- add_task: Create new tasks
- list_tasks: Show tasks (no parameters needed for all tasks)
- complete_task: Mark task complete
- delete_task: Delete task
- update_task: Update task details

Always respond in the same language as the user (English or Urdu)."""


async def run_agent(
    conversation_history: List[Dict[str, str]],
    user_message: str,
    user_id: str
) -> Tuple[str, List[Dict]]:
    """Run AI agent with conversation context."""
    # Language validation
    is_valid_language, error_message = validate_language(user_message)
    if not is_valid_language:
        return error_message, []

    # Intent classification
    intent = classify_intent(user_message, conversation_history)
    confidence = IntentClassifier.get_confidence_score(user_message, intent)
    print(f"🧠 Intent: {intent} (confidence: {confidence:.2f})")

    # Build messages
    messages = [{"role": "system", "content": AGENT_INSTRUCTIONS}]
    for msg in conversation_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        # Call API with tools (AsyncOpenAI requires await)
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=MCP_TOOLS,
            tool_choice="auto"
        )

        message = response.choices[0].message
        tool_calls = []
        assistant_response = message.content or ""

        # Execute tool calls
        if message.tool_calls:
            from mcp_server import call_tool

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")
                args["user_id"] = user_id

                # Validate and execute
                try:
                    if tool_name == "add_task":
                        args = validate_add_task(args, user_message)
                    elif tool_name == "update_task":
                        args = validate_update_task(args)
                except Exception as e:
                    return f"❌ Validation error: {str(e)}", []

                result = await call_tool(tool_name, args)
                result_text = result[0].text if result else "Done"

                tool_calls.append({"tool": tool_name, "args": args})

                # Get final response after tool
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_text
                })

            # Get final response (async)
            final = await client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            assistant_response = final.choices[0].message.content or ""

        return assistant_response, tool_calls

    except Exception as e:
        error_msg = f"❌ Agent error: {str(e)}"
        print(error_msg)
        return error_msg, []
