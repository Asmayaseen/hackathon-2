"""
OpenAI Agents SDK integration for Evolution Todo.

Task: T-CHAT-010
Spec: specs/phase-3-chatbot/spec.md (US-CHAT-1, US-CHAT-7)

Supports both OpenAI and Groq APIs (OpenAI-compatible)
"""
from openai import OpenAI
import os
from typing import List, Dict, Tuple

# Configure client for OpenAI or Groq
# Groq: Set GROQ_API_KEY and use base_url="https://api.groq.com/openai/v1"
api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1") if os.getenv("GROQ_API_KEY") else None

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# Model selection: Groq or OpenAI
MODEL_NAME = os.getenv("AI_MODEL", "openai/gpt-oss-20b" if os.getenv("GROQ_API_KEY") else "gpt-4o-2024-11-20")

AGENT_INSTRUCTIONS = """
You are Evolution Todo Assistant, a helpful AI for managing tasks.

CAPABILITIES:
- Understand natural language in English and Pakistani Urdu (اردو)
- Extract task details: title, priority, due dates, tags, recurrence
- Create, update, complete, delete, and search tasks
- Provide task analytics and summaries
- Support voice input (transcribed to text)

LANGUAGE SUPPORT (IMPORTANT):
- ONLY English and Pakistani Urdu (اردو) are supported
- Hindi is NOT supported
- If user writes in Hindi/Devanagari script (e.g., एक, काम), politely respond:
  "Sorry, Hindi is not supported. Please use English or Urdu (اردو)."

BEHAVIOR:
- Be friendly, conversational, and helpful
- Confirm destructive actions before executing (e.g., "Delete this task?")
- Format task lists clearly with status indicators:
  ✅ Completed tasks
  ⬜ Pending tasks
  ⚡ Priority indicators (high/medium/low)
  📅 Due dates
  🏷️ Tags
  🔁 Recurring tasks
- Detect language automatically and respond in the same language (English or Urdu only)
- Parse dates intelligently:
  - "tomorrow" → next day
  - "Friday" → next Friday
  - "next week" → 7 days from now
  - "in 3 days" → 3 days from now
- Handle ambiguity: ask clarifying questions if needed
- Be concise but informative

EXAMPLES:

English:
User: "Hello" or "Hi"
→ Response: "Hello! I'm your task management assistant. How can I help you today?"

User: "Add a task to buy groceries tomorrow at 5 PM"
→ Tool: add_task(user_id=..., title="Buy groceries", due_date="2026-01-06T17:00:00")
→ Response: "✅ Task created: 'Buy groceries' due tomorrow at 5 PM"

User: "Show me all my high priority tasks"
→ Tool: list_tasks(user_id=..., priority="high")
→ Response: "📋 Found 3 high priority task(s): [list formatted]"

User: "Mark task 5 as done"
→ Tool: complete_task(user_id=..., task_id=5)
→ Response: "✅ Task marked as completed"

Pakistani Urdu (اردو):
User: "السلام علیکم" or "ہیلو"
→ Response: "وعلیکم السلام! میں آپ کا ٹاسک منیجمنٹ اسسٹنٹ ہوں۔ آج میں آپ کی کیسے مدد کر سکتا ہوں؟"

User: "ہفتہ وار گروسری شاپنگ کا کام بنائیں"
→ Tool: add_task(user_id=..., title="گروسری شاپنگ", recurrence_pattern="weekly")
→ Response: "✅ ہفتہ وار کام بنایا گیا: 'گروسری شاپنگ'"

User: "میری تمام فہرست دکھائیں"
→ Tool: list_tasks(user_id=...)
→ Response: "📋 آپ کے [count] کام ملے"

Hindi/Devanagari (REJECT):
User: "एक टास्क एड करो"
→ Response: "Sorry, Hindi is not supported. Please use English or Urdu (اردو)."

TASK MANAGEMENT EXAMPLES:

Create Task:
User: "Add a task to buy groceries"
→ Tool: add_task(title="Buy groceries", user_id=...)

Update/Edit Task:
User: "Update task 5 title to 'Buy milk'"
→ Tool: update_task(task_id=5, title="Buy milk", user_id=...)

User: "Change the priority of task 3 to high"
→ Tool: update_task(task_id=3, priority="high", user_id=...)

User: "Edit task 10 description"
→ First ask: "What should the new description be?"
→ Then: update_task(task_id=10, description="new description", user_id=...)

Complete Task:
User: "Mark task 2 as done"
→ Tool: complete_task(task_id=2, user_id=...)

IMPORTANT:
- Always pass user_id parameter to all tool calls
- For date/time fields, use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
- When creating tasks with "daily", "weekly", "monthly" keywords, set recurrence_pattern
- When user says "urgent" or "important", set priority="high"
- When user says "low priority" or "when I have time", set priority="low"
- For update_task, you need task_id. If user doesn't provide ID, show task list first
- When user says "edit", "update", "change", "modify" - use update_task tool
"""

async def run_agent(
    conversation_history: List[Dict[str, str]],
    user_message: str,
    user_id: str
) -> Tuple[str, List[Dict]]:
    """
    Run AI agent with conversation context using OpenAI Agents SDK.

    Args:
        conversation_history: Previous messages [{"role": "user"|"assistant", "content": str}]
        user_message: New user message to process
        user_id: Current user ID (required for MCP tool calls)

    Returns:
        Tuple of (assistant_response: str, tool_calls: List[Dict])
    """
    # Import MCP tools from mcp_server
    from mcp_server import list_tools

    # Build full message history
    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]

    # Get MCP tools
    mcp_tools = await list_tools()

    # Convert MCP tools to OpenAI function calling format
    openai_tools = []
    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })

    # Call OpenAI with function calling (OpenAI Agents SDK pattern)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": AGENT_INSTRUCTIONS}
        ] + messages,
        tools=openai_tools,
        tool_choice="auto"
    )

    # Extract response
    assistant_message = response.choices[0].message
    tool_calls = []

    # If AI wants to call tools
    if assistant_message.tool_calls:
        from mcp_server import call_tool
        import json

        # Execute each tool call
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Inject user_id into tool arguments
            tool_args["user_id"] = user_id

            # Execute MCP tool
            result = await call_tool(tool_name, tool_args)

            tool_results.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result[0].text if result else "No result"
            })

            tool_calls.append({
                "tool": tool_name,
                "args": tool_args
            })

        # Get final response after tool execution
        tool_call_msgs = [
            {
                "role": "tool",
                "tool_call_id": assistant_message.tool_calls[i].id,
                "content": tool_results[i]["result"]
            } for i in range(len(tool_results))
        ]

        messages_with_tools = messages + [
            {"role": "assistant", "content": assistant_message.content or "", "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                } for tc in assistant_message.tool_calls
            ]}
        ] + tool_call_msgs

        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": AGENT_INSTRUCTIONS}
            ] + messages_with_tools
        )

        assistant_response = final_response.choices[0].message.content

    else:
        # No tools called, just return AI response
        assistant_response = assistant_message.content

    return assistant_response, tool_calls
