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

    def add_todo(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        tags: Optional[list[str]] = None,
        due_date: Optional[datetime] = None,
        recurrence_pattern: Optional[str] = None
    ) -> TodoItem:
        """
        Create a new todo with auto-assigned ID.

        Args:
            title: Task title (1-200 chars)
            description: Optional task details (max 1000 chars)
            priority: Task urgency level (high/medium/low, default: medium)
            tags: Category labels (max 10, will be normalized)
            due_date: Optional deadline for the task
            recurrence_pattern: Optional repeat schedule (daily/weekly/monthly, requires due_date)

        Returns:
            Created TodoItem

        Raises:
            ValidationError: If title, priority, tags are invalid, or recurrence without due_date
        """
        # Validate: recurrence requires due_date
        if recurrence_pattern and not due_date:
            raise ValueError("Recurrence pattern requires a due date")

        todo = TodoItem(
            id=self._next_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags if tags is not None else [],
            due_date=due_date,
            recurrence_pattern=recurrence_pattern
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

    def list_todos(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[list[str]] = None
    ) -> list[TodoItem]:
        """
        List all todos, optionally filtered by status, priority, and tags.

        Args:
            status: Optional filter ("pending", "in_progress", "completed")
            priority: Optional filter ("high", "medium", "low")
            tags: Optional filter (AND logic: task must have ALL specified tags)

        Returns:
            List of TodoItem instances (may be empty), sorted by creation time
        """
        todos = list(self._todos.values())

        # Apply status filter
        if status:
            todos = [t for t in todos if t.status == status]

        # T021: Apply priority filter
        if priority:
            todos = [t for t in todos if t.priority == priority]

        # T022: Apply tags filter (AND logic - task must have all specified tags)
        if tags:
            todos = [
                t for t in todos
                if all(tag in t.tags for tag in tags)
            ]

        return sorted(todos, key=lambda t: t.created_at)

    def filter_todos(
        self,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[list[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> list[TodoItem]:
        """
        Advanced filtering with keyword search and date range.

        Args:
            keyword: Search in title and description (case-insensitive)
            status: Optional filter ("pending", "in_progress", "completed")
            priority: Optional filter ("high", "medium", "low")
            tags: Optional filter (AND logic: task must have ALL specified tags)
            date_from: Filter tasks created on or after this date
            date_to: Filter tasks created on or before this date

        Returns:
            List of TodoItem instances matching ALL criteria (AND logic), sorted by creation time
        """
        todos = list(self._todos.values())

        # T042: Keyword search (case-insensitive substring match in title and description)
        if keyword:
            keyword_lower = keyword.lower()
            todos = [
                t for t in todos
                if keyword_lower in t.title.lower() or keyword_lower in t.description.lower()
            ]

        # Apply status filter
        if status:
            todos = [t for t in todos if t.status == status]

        # Apply priority filter
        if priority:
            todos = [t for t in todos if t.priority == priority]

        # Apply tags filter (AND logic - task must have all specified tags)
        if tags:
            todos = [
                t for t in todos
                if all(tag in t.tags for tag in tags)
            ]

        # T043: Date range filtering (filter by created_at)
        if date_from:
            todos = [t for t in todos if t.created_at >= date_from]
        if date_to:
            # Include tasks created on date_to (up to end of day)
            todos = [t for t in todos if t.created_at <= date_to]

        # T044: AND logic combines all filters (already implemented by sequential filtering)
        return sorted(todos, key=lambda t: t.created_at)

    def sort_todos(
        self,
        todos: list[TodoItem],
        sort_by: str = "created_at",
        sort_order: str = "asc"
    ) -> list[TodoItem]:
        """
        Sort todos by specified field and order.

        Args:
            todos: List of todos to sort
            sort_by: Field to sort by (priority/due_date/created_at/title)
            sort_order: Sort order (asc/desc)

        Returns:
            Sorted list of TodoItem instances
        """
        # T063: Priority sorting logic (high=0, medium=1, low=2)
        if sort_by == "priority":
            priority_map = {"high": 0, "medium": 1, "low": 2}
            sorted_todos = sorted(todos, key=lambda t: priority_map[t.priority])

        # T064: Due date sorting logic (null dates last)
        elif sort_by == "due_date":
            # Use datetime.max for null dates to put them last
            from datetime import datetime as dt
            sorted_todos = sorted(
                todos,
                key=lambda t: t.due_date if t.due_date is not None else dt.max
            )

        # T065: Created_at and title sorting logic
        elif sort_by == "created_at":
            sorted_todos = sorted(todos, key=lambda t: t.created_at)

        elif sort_by == "title":
            sorted_todos = sorted(todos, key=lambda t: t.title.lower())

        else:
            # Default to created_at
            sorted_todos = sorted(todos, key=lambda t: t.created_at)

        # Apply sort order (reverse for descending)
        if sort_order == "desc":
            sorted_todos = list(reversed(sorted_todos))

        return sorted_todos

    def check_reminders(self) -> list[TodoItem]:
        """
        Check for tasks due within the next 30 minutes.

        Returns:
            List of TodoItem instances with due dates within 30 minutes
        """
        from datetime import timedelta
        now = datetime.now()
        reminder_window = now + timedelta(minutes=30)

        reminders = []
        for todo in self._todos.values():
            # Only check pending and in_progress tasks
            if todo.status in ["pending", "in_progress"] and todo.due_date:
                # Task is due within 30 minutes
                if now <= todo.due_date <= reminder_window:
                    reminders.append(todo)

        return sorted(reminders, key=lambda t: t.due_date if t.due_date else datetime.max)

    def update_todo(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date: Optional[datetime] = None,
        clear_due_date: bool = False,
        recurrence_pattern: Optional[str] = None,
        clear_recurrence: bool = False
    ) -> Optional[TodoItem]:
        """
        Update todo fields.

        Args:
            todo_id: ID of todo to update
            title: New title (if provided)
            description: New description (if provided)
            status: New status (if provided)
            priority: New priority level (if provided)
            tags: New tags (replaces existing tags if provided)
            due_date: New due date (if provided)
            clear_due_date: If True, clears the due date
            recurrence_pattern: New recurrence pattern (if provided)
            clear_recurrence: If True, clears the recurrence pattern

        Returns:
            Updated TodoItem or None if not found

        Raises:
            ValidationError: If updates violate constraints
        """
        todo = self._todos.get(todo_id)
        if not todo:
            return None

        # Build update dictionary
        update_data: dict[str, str | datetime | list[str] | None] = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        if priority is not None:
            update_data["priority"] = priority
        if tags is not None:
            update_data["tags"] = tags
        if due_date is not None:
            update_data["due_date"] = due_date
        if clear_due_date:
            update_data["due_date"] = None
        if recurrence_pattern is not None:
            update_data["recurrence_pattern"] = recurrence_pattern
        if clear_recurrence:
            update_data["recurrence_pattern"] = None

        # Always update timestamp
        update_data["updated_at"] = datetime.now()

        # Create updated todo (Pydantic validation)
        updated_todo = todo.model_copy(update=update_data)
        self._todos[todo_id] = updated_todo
        return updated_todo

    def complete_todo(self, todo_id: int) -> tuple[Optional[TodoItem], Optional[TodoItem]]:
        """
        Set todo status to 'completed'. For recurring tasks, auto-creates next instance.

        Args:
            todo_id: ID of todo to complete

        Returns:
            Tuple of (completed_todo, new_recurring_instance)
            new_recurring_instance is None if task is not recurring
        """
        # T102: Check for recurrence_pattern
        completed = self.update_todo(todo_id, status="completed")
        if not completed:
            return (None, None)

        # T103-T105: Auto-create next instance if recurring
        if completed.recurrence_pattern and completed.due_date:
            from datetime import timedelta
            from calendar import monthrange

            # T103: Calculate next due_date based on pattern
            next_due: datetime
            if completed.recurrence_pattern == "daily":
                next_due = completed.due_date + timedelta(days=1)
            elif completed.recurrence_pattern == "weekly":
                next_due = completed.due_date + timedelta(weeks=1)
            elif completed.recurrence_pattern == "monthly":
                # Add one month (handle month-end edge cases)
                year = completed.due_date.year
                month = completed.due_date.month + 1
                if month > 12:
                    month = 1
                    year += 1
                # Handle day overflow (e.g., Jan 31 -> Feb 28/29)
                day = min(completed.due_date.day, monthrange(year, month)[1])
                next_due = completed.due_date.replace(year=year, month=month, day=day)
            elif completed.recurrence_pattern == "yearly":
                # Add one year (handle leap year edge case: Feb 29 -> Feb 28)
                year = completed.due_date.year + 1
                month = completed.due_date.month
                # Handle Feb 29 -> Feb 28 for non-leap years
                day = min(completed.due_date.day, monthrange(year, month)[1])
                next_due = completed.due_date.replace(year=year, month=month, day=day)
            else:
                # Shouldn't happen due to Literal type, but handle gracefully
                return (completed, None)

            # T104: Create new instance with inherited fields
            new_instance = TodoItem(
                id=self._next_id,
                title=completed.title,
                description=completed.description,
                priority=completed.priority,
                tags=list(completed.tags),  # Copy list
                due_date=next_due,
                recurrence_pattern=completed.recurrence_pattern,
                recurrence_parent_id=completed.id,  # T105: Link to parent
                status="pending",  # Reset status
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            self._todos[new_instance.id] = new_instance
            self._next_id += 1
            return (completed, new_instance)

        return (completed, None)

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
