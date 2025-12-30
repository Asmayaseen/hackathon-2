"""
Unit tests for TodoManager business logic.
Tests CRUD operations, filtering, and edge cases.
"""

import pytest
from datetime import datetime
from src.core.todo_manager import TodoManager
from src.core.todo_item import TodoItem
from pydantic import ValidationError


class TestTodoManagerInitialization:
    """Test TodoManager initialization."""

    def test_manager_starts_empty(self) -> None:
        """Test that new manager has no todos."""
        manager = TodoManager()
        todos = manager.list_todos()
        assert len(todos) == 0

    def test_manager_next_id_starts_at_1(self) -> None:
        """Test that first todo gets ID 1."""
        manager = TodoManager()
        todo = manager.add_todo("First task")
        assert todo.id == 1


class TestTodoManagerAdd:
    """Test adding todos."""

    def test_add_todo_with_title_only(self) -> None:
        """Test adding todo with only title."""
        manager = TodoManager()
        todo = manager.add_todo("Test task")

        assert todo.id == 1
        assert todo.title == "Test task"
        assert todo.description == ""
        assert todo.status == "pending"

    def test_add_todo_with_description(self) -> None:
        """Test adding todo with title and description."""
        manager = TodoManager()
        todo = manager.add_todo("Test task", "Test description")

        assert todo.title == "Test task"
        assert todo.description == "Test description"

    def test_add_multiple_todos_increments_id(self) -> None:
        """Test that IDs increment correctly."""
        manager = TodoManager()
        todo1 = manager.add_todo("Task 1")
        todo2 = manager.add_todo("Task 2")
        todo3 = manager.add_todo("Task 3")

        assert todo1.id == 1
        assert todo2.id == 2
        assert todo3.id == 3

    def test_add_todo_returns_todo_item(self) -> None:
        """Test that add_todo returns TodoItem instance."""
        manager = TodoManager()
        todo = manager.add_todo("Test")
        assert isinstance(todo, TodoItem)

    def test_add_todo_with_invalid_title_raises_error(self) -> None:
        """Test that invalid title raises ValidationError."""
        manager = TodoManager()
        with pytest.raises(ValidationError):
            manager.add_todo("")  # Empty title

    def test_add_todo_stores_in_collection(self) -> None:
        """Test that added todo is stored and retrievable."""
        manager = TodoManager()
        todo = manager.add_todo("Test task")

        retrieved = manager.get_todo(todo.id)
        assert retrieved is not None
        assert retrieved.title == "Test task"


class TestTodoManagerGet:
    """Test retrieving individual todos."""

    def test_get_existing_todo(self) -> None:
        """Test getting an existing todo by ID."""
        manager = TodoManager()
        added = manager.add_todo("Test task")

        retrieved = manager.get_todo(added.id)
        assert retrieved is not None
        assert retrieved.id == added.id
        assert retrieved.title == added.title

    def test_get_nonexistent_todo_returns_none(self) -> None:
        """Test that getting non-existent todo returns None."""
        manager = TodoManager()
        result = manager.get_todo(999)
        assert result is None

    def test_get_todo_from_empty_manager(self) -> None:
        """Test getting todo when manager is empty."""
        manager = TodoManager()
        result = manager.get_todo(1)
        assert result is None


class TestTodoManagerList:
    """Test listing todos with filters."""

    def test_list_empty_manager(self) -> None:
        """Test listing todos when manager is empty."""
        manager = TodoManager()
        todos = manager.list_todos()
        assert todos == []

    def test_list_all_todos(self) -> None:
        """Test listing all todos without filter."""
        manager = TodoManager()
        manager.add_todo("Task 1")
        manager.add_todo("Task 2")
        manager.add_todo("Task 3")

        todos = manager.list_todos()
        assert len(todos) == 3

    def test_list_todos_sorted_by_created_at(self) -> None:
        """Test that todos are sorted by creation time."""
        manager = TodoManager()
        todo1 = manager.add_todo("First")
        todo2 = manager.add_todo("Second")
        todo3 = manager.add_todo("Third")

        todos = manager.list_todos()
        assert todos[0].id == todo1.id
        assert todos[1].id == todo2.id
        assert todos[2].id == todo3.id

    def test_list_todos_filter_by_pending(self) -> None:
        """Test filtering todos by pending status."""
        manager = TodoManager()
        manager.add_todo("Task 1")
        manager.add_todo("Task 2")
        manager.update_todo(2, status="completed")

        pending = manager.list_todos(status="pending")
        assert len(pending) == 1
        assert pending[0].status == "pending"

    def test_list_todos_filter_by_completed(self) -> None:
        """Test filtering todos by completed status."""
        manager = TodoManager()
        manager.add_todo("Task 1")
        manager.add_todo("Task 2")
        manager.complete_todo(1)

        completed = manager.list_todos(status="completed")
        assert len(completed) == 1
        assert completed[0].status == "completed"

    def test_list_todos_filter_by_in_progress(self) -> None:
        """Test filtering todos by in_progress status."""
        manager = TodoManager()
        manager.add_todo("Task 1")
        manager.add_todo("Task 2")
        manager.update_todo(1, status="in_progress")

        in_progress = manager.list_todos(status="in_progress")
        assert len(in_progress) == 1
        assert in_progress[0].status == "in_progress"

    def test_list_todos_filter_returns_empty_if_none_match(self) -> None:
        """Test that filter returns empty list if no matches."""
        manager = TodoManager()
        manager.add_todo("Task 1")

        completed = manager.list_todos(status="completed")
        assert completed == []


class TestTodoManagerUpdate:
    """Test updating todos."""

    def test_update_title(self) -> None:
        """Test updating todo title."""
        manager = TodoManager()
        todo = manager.add_todo("Original Title")

        updated = manager.update_todo(todo.id, title="New Title")
        assert updated is not None
        assert updated.title == "New Title"

    def test_update_description(self) -> None:
        """Test updating todo description."""
        manager = TodoManager()
        todo = manager.add_todo("Task")

        updated = manager.update_todo(todo.id, description="New description")
        assert updated is not None
        assert updated.description == "New description"

    def test_update_status(self) -> None:
        """Test updating todo status."""
        manager = TodoManager()
        todo = manager.add_todo("Task")

        updated = manager.update_todo(todo.id, status="in_progress")
        assert updated is not None
        assert updated.status == "in_progress"

    def test_update_multiple_fields(self) -> None:
        """Test updating multiple fields at once."""
        manager = TodoManager()
        todo = manager.add_todo("Task")

        updated = manager.update_todo(
            todo.id,
            title="New Title",
            description="New Description",
            status="completed"
        )

        assert updated is not None
        assert updated.title == "New Title"
        assert updated.description == "New Description"
        assert updated.status == "completed"

    def test_update_sets_updated_at(self) -> None:
        """Test that update changes updated_at timestamp."""
        manager = TodoManager()
        todo = manager.add_todo("Task")
        original_updated_at = todo.updated_at

        updated = manager.update_todo(todo.id, title="New Title")
        assert updated is not None
        assert updated.updated_at >= original_updated_at

    def test_update_nonexistent_todo_returns_none(self) -> None:
        """Test that updating non-existent todo returns None."""
        manager = TodoManager()
        result = manager.update_todo(999, title="New Title")
        assert result is None

    def test_update_persists_in_manager(self) -> None:
        """Test that updates persist in manager."""
        manager = TodoManager()
        todo = manager.add_todo("Original")

        manager.update_todo(todo.id, title="Updated")
        retrieved = manager.get_todo(todo.id)

        assert retrieved is not None
        assert retrieved.title == "Updated"


class TestTodoManagerComplete:
    """Test marking todos as completed."""

    def test_complete_todo(self) -> None:
        """Test completing a todo."""
        manager = TodoManager()
        todo = manager.add_todo("Task")

        completed, _ = manager.complete_todo(todo.id)
        assert completed is not None
        assert completed.status == "completed"

    def test_complete_nonexistent_todo_returns_none(self) -> None:
        """Test completing non-existent todo returns None."""
        manager = TodoManager()
        result = manager.complete_todo(999)
        assert result == (None, None)

    def test_complete_already_completed_todo(self) -> None:
        """Test completing already completed todo (idempotent)."""
        manager = TodoManager()
        todo = manager.add_todo("Task")

        manager.complete_todo(todo.id)
        completed_again, _ = manager.complete_todo(todo.id)

        assert completed_again is not None
        assert completed_again.status == "completed"

    def test_complete_updates_timestamp(self) -> None:
        """Test that completing updates updated_at."""
        manager = TodoManager()
        todo = manager.add_todo("Task")
        original_time = todo.updated_at

        completed, _ = manager.complete_todo(todo.id)
        assert completed is not None
        assert completed.updated_at >= original_time


class TestTodoManagerDelete:
    """Test deleting todos."""

    def test_delete_existing_todo(self) -> None:
        """Test deleting an existing todo."""
        manager = TodoManager()
        todo = manager.add_todo("Task")

        result = manager.delete_todo(todo.id)
        assert result is True

    def test_delete_removes_from_collection(self) -> None:
        """Test that deleted todo is no longer retrievable."""
        manager = TodoManager()
        todo = manager.add_todo("Task")

        manager.delete_todo(todo.id)
        retrieved = manager.get_todo(todo.id)

        assert retrieved is None

    def test_delete_nonexistent_todo_returns_false(self) -> None:
        """Test deleting non-existent todo returns False."""
        manager = TodoManager()
        result = manager.delete_todo(999)
        assert result is False

    def test_delete_reduces_list_size(self) -> None:
        """Test that deleting reduces todo count."""
        manager = TodoManager()
        manager.add_todo("Task 1")
        manager.add_todo("Task 2")

        manager.delete_todo(1)
        todos = manager.list_todos()

        assert len(todos) == 1


class TestTodoManagerEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_add_update_delete_sequence(self) -> None:
        """Test full lifecycle of a todo."""
        manager = TodoManager()

        # Add
        todo = manager.add_todo("Task", "Description")
        assert todo.id == 1

        # Update
        updated = manager.update_todo(1, status="in_progress")
        assert updated is not None
        assert updated.status == "in_progress"

        # Complete
        completed, _ = manager.complete_todo(1)
        assert completed is not None
        assert completed.status == "completed"

        # Delete
        deleted = manager.delete_todo(1)
        assert deleted is True

        # Verify gone
        assert manager.get_todo(1) is None

    def test_multiple_managers_independent(self) -> None:
        """Test that multiple managers are independent."""
        manager1 = TodoManager()
        manager2 = TodoManager()

        manager1.add_todo("Task 1")
        manager2.add_todo("Task 2")

        assert len(manager1.list_todos()) == 1
        assert len(manager2.list_todos()) == 1
        assert manager1.list_todos()[0].title == "Task 1"
        assert manager2.list_todos()[0].title == "Task 2"

    def test_id_continues_after_deletion(self) -> None:
        """Test that IDs continue incrementing after deletion."""
        manager = TodoManager()

        todo1 = manager.add_todo("Task 1")
        manager.delete_todo(todo1.id)
        todo2 = manager.add_todo("Task 2")

        assert todo2.id == 2  # ID continues from 1, not reused
