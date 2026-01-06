"""
Unit tests for AI agent (agent.py).

Tests the run_agent function with mocked OpenAI client and MCP tools.
Ensures proper conversation handling, tool calling, and error handling.

Test Coverage:
- Agent with no tool calls (simple responses)
- Agent with MCP tool calls
- User ID injection into tool arguments
- Conversation history handling
- Error handling and exception propagation
- Multiple tool calls in sequence
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import List, Dict
import json

from agent import run_agent, AGENT_INSTRUCTIONS, MODEL_NAME


@pytest.mark.unit
@pytest.mark.agent
class TestRunAgent:
    """Test suite for run_agent function."""

    @pytest.mark.asyncio
    async def test_run_agent_simple_response_no_tools(self, mock_openai_client, mock_mcp_tools):
        """
        Test agent returns simple response without calling tools.

        Scenario: User asks a general question
        Expected: Agent responds without tool execution
        """
        # Arrange
        conversation_history = []
        user_message = "Hello, how are you?"
        user_id = "test_user_123"

        # Configure mock to return simple response (no tools)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello! I'm doing well. How can I help you today?"
        mock_response.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Act
        assistant_response, tool_calls = await run_agent(
            conversation_history,
            user_message,
            user_id
        )

        # Assert
        assert assistant_response == "Hello! I'm doing well. How can I help you today?"
        assert tool_calls == []
        assert mock_openai_client.chat.completions.create.call_count == 1

        # Verify conversation history was passed correctly
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == AGENT_INSTRUCTIONS
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == user_message


    @pytest.mark.asyncio
    async def test_run_agent_with_conversation_history(self, mock_openai_client, mock_mcp_tools):
        """
        Test agent includes conversation history in API call.

        Scenario: Multi-turn conversation
        Expected: Full conversation history is sent to OpenAI
        """
        # Arrange
        conversation_history = [
            {"role": "user", "content": "What's my name?"},
            {"role": "assistant", "content": "I don't have access to your name yet."}
        ]
        user_message = "My name is Alice"
        user_id = "test_user_123"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Nice to meet you, Alice!"
        mock_response.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Act
        assistant_response, tool_calls = await run_agent(
            conversation_history,
            user_message,
            user_id
        )

        # Assert
        assert assistant_response == "Nice to meet you, Alice!"

        # Verify conversation history was included
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 4  # system + 2 history + 1 new message
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "What's my name?"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "I don't have access to your name yet."
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "My name is Alice"


    @pytest.mark.asyncio
    async def test_run_agent_with_tool_call(self, mock_openai_client, mock_mcp_tools):
        """
        Test agent calls MCP tools correctly.

        Scenario: User requests task creation
        Expected: Agent calls add_task tool and returns formatted response
        """
        # Arrange
        conversation_history = []
        user_message = "Add a task to buy groceries"
        user_id = "test_user_123"

        # Mock tool definition
        from mcp.types import Tool, TextContent
        mock_tool = Tool(
            name="add_task",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        )
        mock_mcp_tools["list_tools"].return_value = [mock_tool]

        # Mock first response with tool call
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "add_task"
        mock_tool_call.function.arguments = json.dumps({"title": "Buy groceries"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = ""
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]

        # Mock tool execution result
        mock_mcp_tools["call_tool"].return_value = [
            TextContent(type="text", text="✅ Task created: 'Buy groceries' (ID: 1)")
        ]

        # Mock final response after tool execution
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "I've created the task 'Buy groceries' for you!"
        mock_response_2.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.side_effect = [
            mock_response_1,
            mock_response_2
        ]

        # Act
        assistant_response, tool_calls = await run_agent(
            conversation_history,
            user_message,
            user_id
        )

        # Assert
        assert assistant_response == "I've created the task 'Buy groceries' for you!"
        assert len(tool_calls) == 1
        assert tool_calls[0]["tool"] == "add_task"
        assert tool_calls[0]["args"]["title"] == "Buy groceries"
        assert tool_calls[0]["args"]["user_id"] == user_id  # Verify user_id injection

        # Verify tool was called with user_id injected
        mock_mcp_tools["call_tool"].assert_called_once_with(
            "add_task",
            {"title": "Buy groceries", "user_id": user_id}
        )

        # Verify two API calls (initial + after tool execution)
        assert mock_openai_client.chat.completions.create.call_count == 2


    @pytest.mark.asyncio
    async def test_run_agent_multiple_tool_calls(self, mock_openai_client, mock_mcp_tools):
        """
        Test agent handles multiple tool calls in one turn.

        Scenario: User requests multiple actions
        Expected: Agent executes all tools and returns combined response
        """
        # Arrange
        conversation_history = []
        user_message = "Create a task to buy milk and show me all my tasks"
        user_id = "test_user_123"

        # Mock tool definitions
        from mcp.types import Tool, TextContent
        mock_tools = [
            Tool(name="add_task", description="Create task", inputSchema={"type": "object", "properties": {}}),
            Tool(name="list_tasks", description="List tasks", inputSchema={"type": "object", "properties": {}})
        ]
        mock_mcp_tools["list_tools"].return_value = mock_tools

        # Mock tool calls
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.id = "call_1"
        mock_tool_call_1.function.name = "add_task"
        mock_tool_call_1.function.arguments = json.dumps({"title": "Buy milk"})

        mock_tool_call_2 = MagicMock()
        mock_tool_call_2.id = "call_2"
        mock_tool_call_2.function.name = "list_tasks"
        mock_tool_call_2.function.arguments = json.dumps({})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = ""
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call_1, mock_tool_call_2]

        # Mock tool results
        mock_mcp_tools["call_tool"].side_effect = [
            [TextContent(type="text", text="✅ Task created: 'Buy milk'")],
            [TextContent(type="text", text="📋 Found 3 tasks: ...")]
        ]

        # Mock final response
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "I've created the task and here are all your tasks!"
        mock_response_2.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.side_effect = [
            mock_response_1,
            mock_response_2
        ]

        # Act
        assistant_response, tool_calls = await run_agent(
            conversation_history,
            user_message,
            user_id
        )

        # Assert
        assert assistant_response == "I've created the task and here are all your tasks!"
        assert len(tool_calls) == 2
        assert tool_calls[0]["tool"] == "add_task"
        assert tool_calls[1]["tool"] == "list_tasks"

        # Verify both tools were called
        assert mock_mcp_tools["call_tool"].call_count == 2


    @pytest.mark.asyncio
    async def test_run_agent_user_id_injection(self, mock_openai_client, mock_mcp_tools):
        """
        Test user_id is correctly injected into all tool calls.

        Scenario: AI calls tool without user_id in arguments
        Expected: user_id is automatically injected before tool execution
        """
        # Arrange
        conversation_history = []
        user_message = "List my tasks"
        user_id = "specific_user_999"

        from mcp.types import Tool, TextContent
        mock_tool = Tool(
            name="list_tasks",
            description="List tasks",
            inputSchema={"type": "object", "properties": {}}
        )
        mock_mcp_tools["list_tools"].return_value = [mock_tool]

        # Mock tool call without user_id
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "list_tasks"
        mock_tool_call.function.arguments = json.dumps({"status": "all"})  # No user_id

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = ""
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]

        mock_mcp_tools["call_tool"].return_value = [
            TextContent(type="text", text="📋 Found 5 tasks")
        ]

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "You have 5 tasks"
        mock_response_2.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.side_effect = [
            mock_response_1,
            mock_response_2
        ]

        # Act
        assistant_response, tool_calls = await run_agent(
            conversation_history,
            user_message,
            user_id
        )

        # Assert - Verify user_id was injected
        mock_mcp_tools["call_tool"].assert_called_once_with(
            "list_tasks",
            {"status": "all", "user_id": "specific_user_999"}
        )


    @pytest.mark.asyncio
    async def test_run_agent_openai_error_propagation(self, mock_openai_client, mock_mcp_tools):
        """
        Test errors from OpenAI API are properly propagated.

        Scenario: OpenAI API returns error
        Expected: Exception is raised with error details
        """
        # Arrange
        conversation_history = []
        user_message = "Hello"
        user_id = "test_user_123"

        # Mock OpenAI error
        mock_openai_client.chat.completions.create.side_effect = Exception("OpenAI API Error: Rate limit exceeded")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await run_agent(conversation_history, user_message, user_id)

        assert "OpenAI API Error" in str(exc_info.value)


    @pytest.mark.asyncio
    async def test_run_agent_tool_execution_error_handling(self, mock_openai_client, mock_mcp_tools):
        """
        Test errors during tool execution are handled gracefully.

        Scenario: MCP tool throws exception
        Expected: Exception is propagated (will be caught by chat endpoint)
        """
        # Arrange
        conversation_history = []
        user_message = "Add a task"
        user_id = "test_user_123"

        from mcp.types import Tool
        mock_tool = Tool(
            name="add_task",
            description="Create task",
            inputSchema={"type": "object", "properties": {}}
        )
        mock_mcp_tools["list_tools"].return_value = [mock_tool]

        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "add_task"
        mock_tool_call.function.arguments = json.dumps({"title": "Test"})

        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = ""
        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]

        # Mock tool execution failure
        mock_mcp_tools["call_tool"].side_effect = Exception("Database connection failed")

        mock_openai_client.chat.completions.create.return_value = mock_response_1

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await run_agent(conversation_history, user_message, user_id)

        assert "Database connection failed" in str(exc_info.value)


    @pytest.mark.asyncio
    async def test_run_agent_model_selection(self, mock_openai_client, mock_mcp_tools):
        """
        Test correct model is used based on environment configuration.

        Scenario: Verify MODEL_NAME is passed to OpenAI API
        Expected: Model name matches configuration
        """
        # Arrange
        conversation_history = []
        user_message = "Hello"
        user_id = "test_user_123"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hi!"
        mock_response.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Act
        await run_agent(conversation_history, user_message, user_id)

        # Assert
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["model"] == MODEL_NAME


    @pytest.mark.asyncio
    async def test_run_agent_empty_conversation_history(self, mock_openai_client, mock_mcp_tools):
        """
        Test agent works correctly with empty conversation history.

        Scenario: First message in conversation
        Expected: Only system prompt and user message are sent
        """
        # Arrange
        conversation_history = []
        user_message = "First message"
        user_id = "test_user_123"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello! This is the first message."
        mock_response.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Act
        assistant_response, tool_calls = await run_agent(
            conversation_history,
            user_message,
            user_id
        )

        # Assert
        assert assistant_response == "Hello! This is the first message."

        # Verify only system + user message
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 2  # system + user
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


    @pytest.mark.asyncio
    async def test_run_agent_tool_choice_auto(self, mock_openai_client, mock_mcp_tools):
        """
        Test agent uses 'auto' tool_choice setting.

        Scenario: Verify OpenAI is configured to auto-select tools
        Expected: tool_choice="auto" in API call
        """
        # Arrange
        conversation_history = []
        user_message = "Test"
        user_id = "test_user_123"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.tool_calls = None

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Act
        await run_agent(conversation_history, user_message, user_id)

        # Assert
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args[1]["tool_choice"] == "auto"
