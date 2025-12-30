"""
Unit tests for TodoItem Pydantic model.
Tests data validation, field constraints, and model behavior.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.core.todo_item import TodoItem


class TestTodoItemCreation:
    """Test TodoItem instantiation and validation."""

    def test_create_valid_todo(self) -> None:
        """Test creating a valid TodoItem with all fields."""
        todo = TodoItem(
            id=1,
            title="Test Task",
            description="Test description",
            status="pending"
        )
        assert todo.id == 1
        assert todo.title == "Test Task"
        assert todo.description == "Test description"
        assert todo.status == "pending"
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)

    def test_create_todo_minimal_fields(self) -> None:
        """Test creating TodoItem with only required fields."""
        todo = TodoItem(id=1, title="Minimal Task")
        assert todo.id == 1
        assert todo.title == "Minimal Task"
        assert todo.description == ""  # Default value
        assert todo.status == "pending"  # Default value

    def test_create_todo_with_whitespace_title(self) -> None:
        """Test that whitespace in title is stripped."""
        todo = TodoItem(id=1, title="  Spaced Title  ")
        assert todo.title == "Spaced Title"

    def test_default_status_is_pending(self) -> None:
        """Test that default status is 'pending'."""
        todo = TodoItem(id=1, title="Test")
        assert todo.status == "pending"

    def test_timestamps_auto_generated(self) -> None:
        """Test that created_at and updated_at are auto-generated."""
        todo = TodoItem(id=1, title="Test")
        assert todo.created_at is not None
        assert todo.updated_at is not None
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)


class TestTodoItemValidation:
    """Test TodoItem field validation and constraints."""

    def test_id_must_be_positive(self) -> None:
        """Test that ID must be greater than 0."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(id=0, title="Test")
        assert "greater than 0" in str(exc_info.value)

    def test_id_cannot_be_negative(self) -> None:
        """Test that ID cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(id=-1, title="Test")
        assert "greater than 0" in str(exc_info.value)

    def test_title_cannot_be_empty(self) -> None:
        """Test that title cannot be empty string."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(id=1, title="")
        assert "at least 1 character" in str(exc_info.value).lower()

    def test_title_cannot_be_whitespace_only(self) -> None:
        """Test that title cannot be only whitespace."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(id=1, title="   ")
        assert "empty" in str(exc_info.value).lower()

    def test_title_max_length_200(self) -> None:
        """Test that title cannot exceed 200 characters."""
        long_title = "x" * 201
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(id=1, title=long_title)
        assert "200" in str(exc_info.value)

    def test_title_exactly_200_chars_valid(self) -> None:
        """Test that title with exactly 200 characters is valid."""
        title_200 = "x" * 200
        todo = TodoItem(id=1, title=title_200)
        assert len(todo.title) == 200

    def test_description_max_length_1000(self) -> None:
        """Test that description cannot exceed 1000 characters."""
        long_desc = "x" * 1001
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(id=1, title="Test", description=long_desc)
        assert "1000" in str(exc_info.value)

    def test_description_exactly_1000_chars_valid(self) -> None:
        """Test that description with exactly 1000 characters is valid."""
        desc_1000 = "x" * 1000
        todo = TodoItem(id=1, title="Test", description=desc_1000)
        assert len(todo.description) == 1000

    def test_status_must_be_valid_literal(self) -> None:
        """Test that status must be one of the allowed values."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(id=1, title="Test", status="invalid_status")  # type: ignore
        assert "Input should be" in str(exc_info.value)

    def test_valid_status_values(self) -> None:
        """Test all valid status values."""
        for status in ["pending", "in_progress", "completed"]:
            todo = TodoItem(id=1, title="Test", status=status)  # type: ignore
            assert todo.status == status


class TestTodoItemModelCopy:
    """Test TodoItem model_copy for updates."""

    def test_model_copy_update_title(self) -> None:
        """Test updating title via model_copy."""
        original = TodoItem(id=1, title="Original Title")
        updated = original.model_copy(update={"title": "New Title"})

        assert updated.title == "New Title"
        assert updated.id == original.id
        assert original.title == "Original Title"  # Original unchanged

    def test_model_copy_update_status(self) -> None:
        """Test updating status via model_copy."""
        original = TodoItem(id=1, title="Test", status="pending")
        updated = original.model_copy(update={"status": "completed"})

        assert updated.status == "completed"
        assert original.status == "pending"

    def test_model_copy_update_description(self) -> None:
        """Test updating description via model_copy."""
        original = TodoItem(id=1, title="Test")
        updated = original.model_copy(update={"description": "New description"})

        assert updated.description == "New description"
        assert original.description == ""

    def test_model_copy_update_timestamp(self) -> None:
        """Test updating updated_at timestamp."""
        original = TodoItem(id=1, title="Test")
        new_time = datetime(2025, 12, 31, 23, 59, 59)
        updated = original.model_copy(update={"updated_at": new_time})

        assert updated.updated_at == new_time
        assert original.updated_at != new_time


class TestTodoItemEdgeCases:
    """Test edge cases and special scenarios."""

    def test_unicode_title(self) -> None:
        """Test that Unicode characters in title work correctly."""
        todo = TodoItem(id=1, title="Test 🚀 Unicode ✨ کام")
        assert "🚀" in todo.title
        assert "✨" in todo.title
        assert "کام" in todo.title

    def test_unicode_description(self) -> None:
        """Test that Unicode characters in description work correctly."""
        todo = TodoItem(
            id=1,
            title="Test",
            description="Description with اردو and 中文"
        )
        assert "اردو" in todo.description
        assert "中文" in todo.description

    def test_special_chars_in_title(self) -> None:
        """Test special characters in title."""
        special_title = "Test: \"Task\" with <special> & 'chars' $100"
        todo = TodoItem(id=1, title=special_title)
        assert todo.title == special_title

    def test_newlines_in_description(self) -> None:
        """Test multiline description."""
        multiline = "Line 1\nLine 2\nLine 3"
        todo = TodoItem(id=1, title="Test", description=multiline)
        assert "\n" in todo.description
        assert todo.description.count("\n") == 2
