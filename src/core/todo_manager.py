# T017-T024: TodoManager business logic service
from typing import Optional
from datetime import datetime
from .todo_item import TodoItem


class TodoManager:
    """
    Manages the in-memory collection of todos.

    Provides CRUD operations with automatic ID assignment and
    validation via Pydantic models.
    """

    def __init__(self) -> None:
        """Initialize empty todo collection."""
        self._todos: dict[int, TodoItem] = {}
        self._next_id: int = 1

    def add_todo(self, title: str, description: str = "") -> TodoItem:
        """
        Create a new todo with auto-assigned ID.

        Args:
            title: Task title (1-200 chars)
            description: Optional task details (max 1000 chars)

        Returns:
            Created TodoItem

        Raises:
            ValidationError: If title is invalid
        """
        todo = TodoItem(
            id=self._next_id,
            title=title,
            description=description
        )
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        """
        Retrieve todo by ID.

        Args:
            todo_id: ID of todo to retrieve

        Returns:
            TodoItem if found, None otherwise
        """
        return self._todos.get(todo_id)

    def list_todos(self, status: Optional[str] = None) -> list[TodoItem]:
        """
        List all todos, optionally filtered by status.

        Args:
            status: Optional filter ("pending", "in_progress", "completed")

        Returns:
            List of TodoItem instances (may be empty), sorted by creation time
        """
        todos = list(self._todos.values())
        if status:
            todos = [t for t in todos if t.status == status]
        return sorted(todos, key=lambda t: t.created_at)

    def update_todo(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[TodoItem]:
        """
        Update todo fields.

        Args:
            todo_id: ID of todo to update
            title: New title (if provided)
            description: New description (if provided)
            status: New status (if provided)

        Returns:
            Updated TodoItem or None if not found

        Raises:
            ValidationError: If updates violate constraints
        """
        todo = self._todos.get(todo_id)
        if not todo:
            return None

        # Build update dictionary
        update_data: dict[str, str | datetime] = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status

        # Always update timestamp
        update_data["updated_at"] = datetime.now()

        # Create updated todo (Pydantic validation)
        updated_todo = todo.model_copy(update=update_data)
        self._todos[todo_id] = updated_todo
        return updated_todo

    def complete_todo(self, todo_id: int) -> Optional[TodoItem]:
        """
        Set todo status to 'completed'.

        Args:
            todo_id: ID of todo to complete

        Returns:
            Updated TodoItem or None if not found
        """
        return self.update_todo(todo_id, status="completed")

    def delete_todo(self, todo_id: int) -> bool:
        """
        Delete todo by ID.

        Args:
            todo_id: ID of todo to delete

        Returns:
            True if deleted, False if not found
        """
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False
