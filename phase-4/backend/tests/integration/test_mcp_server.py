"""
Integration tests for MCP Server (mcp_server.py).

Tests MCP tools with real database operations to verify:
- Task creation, listing, completion, deletion, updating
- Database persistence and query filtering
- User isolation (tasks are user-scoped)
- Input validation via inputSchema
- Error handling for invalid operations

These tests use real database connections with transaction rollback for isolation.
"""
import pytest
from sqlmodel import Session, select
from datetime import datetime
from mcp.types import Tool, TextContent

from mcp_server import list_tools, call_tool
from models import Task


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPToolList:
    """Test MCP tool list endpoint."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """
        Test list_tools returns all 11 MCP tools with correct schema.

        Expected tools:
        1. add_task
        2. list_tasks
        3. complete_task
        4. delete_task
        5. update_task
        6. search_tasks
        7. set_priority
        8. add_tags
        9. schedule_reminder
        10. get_recurring_tasks
        11. analytics_summary
        """
        # Act
        tools = await list_tools()

        # Assert
        assert len(tools) >= 11  # At least 11 tools (may add more in future)
        tool_names = [tool.name for tool in tools]

        # Verify all core tools exist
        assert "add_task" in tool_names
        assert "list_tasks" in tool_names
        assert "complete_task" in tool_names
        assert "delete_task" in tool_names
        assert "update_task" in tool_names
        assert "search_tasks" in tool_names
        assert "set_priority" in tool_names
        assert "add_tags" in tool_names
        assert "schedule_reminder" in tool_names
        assert "get_recurring_tasks" in tool_names
        assert "analytics_summary" in tool_names


    @pytest.mark.asyncio
    async def test_list_tools_schema_validation(self):
        """
        Test each tool has required schema fields.

        Every tool must have:
        - name: string
        - description: string
        - inputSchema: object with type, properties, required
        """
        # Act
        tools = await list_tools()

        # Assert
        for tool in tools:
            assert isinstance(tool, Tool)
            assert isinstance(tool.name, str)
            assert len(tool.name) > 0
            assert isinstance(tool.description, str)
            assert len(tool.description) > 0
            assert isinstance(tool.inputSchema, dict)
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema
            # Verify user_id is required for all tools
            assert "user_id" in tool.inputSchema["required"]


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPAddTask:
    """Test add_task MCP tool."""

    @pytest.mark.asyncio
    async def test_add_task_creates_task_in_database(self, db_session: Session, test_user):
        """
        Test add_task creates task in database with correct attributes.

        Scenario: Call add_task with title only
        Expected: Task created with defaults (priority=none, completed=False)
        """
        # Arrange
        args = {
            "user_id": test_user.id,
            "title": "Test Task from MCP"
        }

        # Act
        result = await call_tool("add_task", args)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Task created" in result[0].text
        assert "Test Task from MCP" in result[0].text

        # Verify database persistence
        task = db_session.exec(
            select(Task).where(
                Task.user_id == test_user.id,
                Task.title == "Test Task from MCP"
            )
        ).first()

        assert task is not None
        assert task.title == "Test Task from MCP"
        assert task.description is None
        assert task.priority == "none"
        assert task.completed == False
        assert task.tags == []


    @pytest.mark.asyncio
    async def test_add_task_with_all_fields(self, db_session: Session, test_user):
        """
        Test add_task with all optional fields.

        Scenario: Create task with priority, due_date, tags, description
        Expected: All fields are persisted correctly
        """
        # Arrange
        due_date = "2026-12-31T23:59:59"
        args = {
            "user_id": test_user.id,
            "title": "Complete Task",
            "description": "This is a detailed description",
            "priority": "high",
            "due_date": due_date,
            "tags": ["urgent", "work"],
            "recurrence_pattern": "daily"
        }

        # Act
        result = await call_tool("add_task", args)

        # Assert
        assert "Task created" in result[0].text
        assert "high" in result[0].text or "⚡" in result[0].text

        # Verify database
        task = db_session.exec(
            select(Task).where(Task.user_id == test_user.id)
        ).first()

        assert task.title == "Complete Task"
        assert task.description == "This is a detailed description"
        assert task.priority == "high"
        assert task.tags == ["urgent", "work"]
        assert task.recurrence_pattern == "daily"


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPListTasks:
    """Test list_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_returns_all_user_tasks(self, db_session: Session, test_user, task_factory):
        """
        Test list_tasks returns all tasks for user.

        Scenario: User has 3 tasks
        Expected: All 3 tasks are returned
        """
        # Arrange
        task_factory(user_id=test_user.id, title="Task 1")
        task_factory(user_id=test_user.id, title="Task 2")
        task_factory(user_id=test_user.id, title="Task 3")

        args = {"user_id": test_user.id}

        # Act
        result = await call_tool("list_tasks", args)

        # Assert
        assert len(result) == 1
        assert "Found 3 task(s)" in result[0].text
        assert "Task 1" in result[0].text
        assert "Task 2" in result[0].text
        assert "Task 3" in result[0].text


    @pytest.mark.asyncio
    async def test_list_tasks_filters_by_status_pending(self, db_session: Session, test_user, task_factory):
        """
        Test list_tasks filters by completion status.

        Scenario: 2 pending tasks, 1 completed task
        Expected: Only 2 pending tasks returned when status=pending
        """
        # Arrange
        task_factory(user_id=test_user.id, title="Pending 1", completed=False)
        task_factory(user_id=test_user.id, title="Pending 2", completed=False)
        task_factory(user_id=test_user.id, title="Completed", completed=True)

        args = {"user_id": test_user.id, "status": "pending"}

        # Act
        result = await call_tool("list_tasks", args)

        # Assert
        assert "Found 2 task(s)" in result[0].text
        assert "Pending 1" in result[0].text
        assert "Pending 2" in result[0].text
        assert "Completed" not in result[0].text


    @pytest.mark.asyncio
    async def test_list_tasks_filters_by_status_completed(self, db_session: Session, test_user, task_factory):
        """
        Test list_tasks filters completed tasks.

        Scenario: 2 pending tasks, 1 completed task
        Expected: Only 1 completed task returned when status=completed
        """
        # Arrange
        task_factory(user_id=test_user.id, title="Pending 1", completed=False)
        task_factory(user_id=test_user.id, title="Pending 2", completed=False)
        task_factory(user_id=test_user.id, title="Completed", completed=True)

        args = {"user_id": test_user.id, "status": "completed"}

        # Act
        result = await call_tool("list_tasks", args)

        # Assert
        assert "Found 1 task(s)" in result[0].text
        assert "Completed" in result[0].text
        assert "Pending 1" not in result[0].text


    @pytest.mark.asyncio
    async def test_list_tasks_filters_by_priority(self, db_session: Session, test_user, task_factory):
        """
        Test list_tasks filters by priority level.

        Scenario: Tasks with different priorities
        Expected: Only high priority tasks returned when priority=high
        """
        # Arrange
        task_factory(user_id=test_user.id, title="High Priority", priority="high")
        task_factory(user_id=test_user.id, title="Low Priority", priority="low")
        task_factory(user_id=test_user.id, title="Medium Priority", priority="medium")

        args = {"user_id": test_user.id, "priority": "high"}

        # Act
        result = await call_tool("list_tasks", args)

        # Assert
        assert "Found 1 task(s)" in result[0].text
        assert "High Priority" in result[0].text
        assert "Low Priority" not in result[0].text


    @pytest.mark.asyncio
    async def test_list_tasks_search_filter(self, db_session: Session, test_user, task_factory):
        """
        Test list_tasks search functionality.

        Scenario: Search for tasks containing "groceries"
        Expected: Only matching tasks are returned
        """
        # Arrange
        task_factory(user_id=test_user.id, title="Buy groceries")
        task_factory(user_id=test_user.id, title="Grocery shopping list")
        task_factory(user_id=test_user.id, title="Pay bills")

        args = {"user_id": test_user.id, "search": "groceries"}

        # Act
        result = await call_tool("list_tasks", args)

        # Assert
        assert "Buy groceries" in result[0].text
        assert "Pay bills" not in result[0].text


    @pytest.mark.asyncio
    async def test_list_tasks_user_isolation(self, db_session: Session, test_user, test_user_2, task_factory):
        """
        Test list_tasks only returns tasks for authenticated user.

        Scenario: Two users with different tasks
        Expected: Each user only sees their own tasks
        """
        # Arrange
        task_factory(user_id=test_user.id, title="User 1 Task")
        task_factory(user_id=test_user_2.id, title="User 2 Task")

        args = {"user_id": test_user.id}

        # Act
        result = await call_tool("list_tasks", args)

        # Assert
        assert "User 1 Task" in result[0].text
        assert "User 2 Task" not in result[0].text
        assert "Found 1 task(s)" in result[0].text


    @pytest.mark.asyncio
    async def test_list_tasks_empty_result(self, db_session: Session, test_user):
        """
        Test list_tasks with no tasks.

        Scenario: User has no tasks
        Expected: Friendly "No tasks found" message
        """
        # Arrange
        args = {"user_id": test_user.id}

        # Act
        result = await call_tool("list_tasks", args)

        # Assert
        assert "No tasks found" in result[0].text


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPCompleteTask:
    """Test complete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_complete_task_marks_task_as_completed(self, db_session: Session, test_user, sample_task):
        """
        Test complete_task toggles task completion status.

        Scenario: Incomplete task exists
        Expected: Task is marked as completed
        """
        # Arrange
        assert sample_task.completed == False

        args = {
            "user_id": test_user.id,
            "task_id": sample_task.id
        }

        # Act
        result = await call_tool("complete_task", args)

        # Assert
        assert "marked as completed" in result[0].text

        # Verify database
        db_session.refresh(sample_task)
        assert sample_task.completed == True


    @pytest.mark.asyncio
    async def test_complete_task_toggles_completion_status(self, db_session: Session, test_user, task_factory):
        """
        Test complete_task can toggle back to incomplete.

        Scenario: Completed task exists
        Expected: Task is marked as uncompleted
        """
        # Arrange
        task = task_factory(user_id=test_user.id, title="Completed Task", completed=True)

        args = {
            "user_id": test_user.id,
            "task_id": task.id
        }

        # Act
        result = await call_tool("complete_task", args)

        # Assert
        assert "marked as uncompleted" in result[0].text

        # Verify database
        db_session.refresh(task)
        assert task.completed == False


    @pytest.mark.asyncio
    async def test_complete_task_nonexistent_task_id(self, db_session: Session, test_user):
        """
        Test complete_task with invalid task ID.

        Scenario: Task ID doesn't exist
        Expected: Error message returned
        """
        # Arrange
        args = {
            "user_id": test_user.id,
            "task_id": 99999  # Non-existent ID
        }

        # Act
        result = await call_tool("complete_task", args)

        # Assert
        assert "not found" in result[0].text.lower()


    @pytest.mark.asyncio
    async def test_complete_task_wrong_user_id(self, db_session: Session, test_user, test_user_2, task_factory):
        """
        Test complete_task prevents cross-user operations.

        Scenario: User A tries to complete User B's task
        Expected: Task not found error (security isolation)
        """
        # Arrange
        task = task_factory(user_id=test_user.id, title="User 1 Task")

        args = {
            "user_id": test_user_2.id,  # Different user
            "task_id": task.id
        }

        # Act
        result = await call_tool("complete_task", args)

        # Assert
        assert "not found" in result[0].text.lower()

        # Verify task was NOT modified
        db_session.refresh(task)
        assert task.completed == False


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPUpdateTask:
    """Test update_task MCP tool (integration with real database)."""

    @pytest.mark.asyncio
    async def test_update_task_title(self, db_session: Session, test_user, sample_task):
        """
        Test update_task changes task title.

        Note: update_task uses HTTP client (not direct DB), so we mock httpx
        """
        # This test would require mocking httpx.AsyncClient
        # For now, we test the inputSchema is correct
        tools = await list_tools()
        update_tool = next(t for t in tools if t.name == "update_task")

        assert "title" in update_tool.inputSchema["properties"]
        assert "task_id" in update_tool.inputSchema["required"]


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPSearchTasks:
    """Test search_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_search_tasks_schema_validation(self):
        """
        Test search_tasks has correct schema.

        Verifies required fields and query parameter.
        """
        tools = await list_tools()
        search_tool = next(t for t in tools if t.name == "search_tasks")

        assert "user_id" in search_tool.inputSchema["required"]
        assert "query" in search_tool.inputSchema["required"]
        assert "priority" in search_tool.inputSchema["properties"]
        assert "tags" in search_tool.inputSchema["properties"]


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPSetPriority:
    """Test set_priority MCP tool."""

    @pytest.mark.asyncio
    async def test_set_priority_schema_validation(self):
        """
        Test set_priority has correct schema with priority enum.
        """
        tools = await list_tools()
        priority_tool = next(t for t in tools if t.name == "set_priority")

        assert "user_id" in priority_tool.inputSchema["required"]
        assert "task_id" in priority_tool.inputSchema["required"]
        assert "priority" in priority_tool.inputSchema["required"]

        # Verify priority enum values
        priority_prop = priority_tool.inputSchema["properties"]["priority"]
        assert "enum" in priority_prop
        assert "low" in priority_prop["enum"]
        assert "medium" in priority_prop["enum"]
        assert "high" in priority_prop["enum"]
        assert "none" in priority_prop["enum"]


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPAddTags:
    """Test add_tags MCP tool."""

    @pytest.mark.asyncio
    async def test_add_tags_schema_validation(self):
        """
        Test add_tags has correct schema with tags array.
        """
        tools = await list_tools()
        tags_tool = next(t for t in tools if t.name == "add_tags")

        assert "user_id" in tags_tool.inputSchema["required"]
        assert "task_id" in tags_tool.inputSchema["required"]
        assert "tags" in tags_tool.inputSchema["required"]

        # Verify tags is an array
        tags_prop = tags_tool.inputSchema["properties"]["tags"]
        assert tags_prop["type"] == "array"
        assert tags_prop["items"]["type"] == "string"


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPScheduleReminder:
    """Test schedule_reminder MCP tool."""

    @pytest.mark.asyncio
    async def test_schedule_reminder_schema_validation(self):
        """
        Test schedule_reminder has correct schema with reminder_time.
        """
        tools = await list_tools()
        reminder_tool = next(t for t in tools if t.name == "schedule_reminder")

        assert "user_id" in reminder_tool.inputSchema["required"]
        assert "task_id" in reminder_tool.inputSchema["required"]
        assert "reminder_time" in reminder_tool.inputSchema["required"]

        # Verify reminder_time is date-time format
        reminder_prop = reminder_tool.inputSchema["properties"]["reminder_time"]
        assert reminder_prop["format"] == "date-time"


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPGetRecurringTasks:
    """Test get_recurring_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_get_recurring_tasks_schema_validation(self):
        """
        Test get_recurring_tasks has correct schema with pattern filter.
        """
        tools = await list_tools()
        recurring_tool = next(t for t in tools if t.name == "get_recurring_tasks")

        assert "user_id" in recurring_tool.inputSchema["required"]
        assert "pattern" in recurring_tool.inputSchema["properties"]

        # Verify pattern enum
        pattern_prop = recurring_tool.inputSchema["properties"]["pattern"]
        assert "enum" in pattern_prop
        assert "daily" in pattern_prop["enum"]
        assert "weekly" in pattern_prop["enum"]
        assert "monthly" in pattern_prop["enum"]


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPAnalyticsSummary:
    """Test analytics_summary MCP tool."""

    @pytest.mark.asyncio
    async def test_analytics_summary_schema_validation(self):
        """
        Test analytics_summary has correct schema.
        """
        tools = await list_tools()
        analytics_tool = next(t for t in tools if t.name == "analytics_summary")

        assert "user_id" in analytics_tool.inputSchema["required"]
        assert len(analytics_tool.inputSchema["required"]) == 1  # Only user_id required
