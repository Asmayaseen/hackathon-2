"""
Tool Validation and Sanitization for Evolution Todo Chatbot.

Purpose: Defensive validation before tool execution to prevent errors.
Fixes:
- Null values being sent to tools
- Invalid recurrence_pattern values ("none" instead of omitting)
- Missing description fields
- Invalid priority values

Task: DEBUG-CHATBOT-002
"""
from typing import Dict, Any, Optional
from datetime import datetime
import re


class ToolValidator:
    """
    Validates and sanitizes tool arguments before execution.

    Ensures:
    - No null values are sent
    - All required fields are present
    - Values match expected formats
    - Auto-generates missing fields when possible
    """

    VALID_PRIORITIES = ["low", "medium", "high", "none"]
    VALID_RECURRENCE = ["daily", "weekly", "monthly"]

    @classmethod
    def validate_add_task(cls, args: Dict[str, Any], user_message: str = "") -> Dict[str, Any]:
        """
        Validate and sanitize add_task arguments.

        Fixes:
        1. Ensure description is never null (auto-generate from title)
        2. Remove recurrence_pattern if value is "none" (should be omitted)
        3. Validate recurrence_pattern is only "daily", "weekly", or "monthly"
        4. Ensure due_date is in ISO format
        5. Validate priority is valid enum

        Args:
            args: Tool arguments dict
            user_message: Original user message (for context)

        Returns:
            Sanitized arguments dict
        """
        sanitized = args.copy()

        # CRITICAL FIX 1: Description must NEVER be null
        if "description" not in sanitized or sanitized["description"] is None or sanitized["description"] == "":
            # Auto-generate description from title
            sanitized["description"] = cls._generate_description(
                sanitized.get("title", ""),
                user_message
            )

        # CRITICAL FIX 2: recurrence_pattern handling
        if "recurrence_pattern" in sanitized:
            recurrence = sanitized["recurrence_pattern"]

            # If value is "none", remove it entirely (one-time task)
            if recurrence in ["none", None, "", "null"]:
                del sanitized["recurrence_pattern"]

            # Validate it's a valid recurrence value
            elif recurrence not in cls.VALID_RECURRENCE:
                # Invalid value - remove it
                print(f"⚠️ Invalid recurrence_pattern '{recurrence}' removed. Valid: {cls.VALID_RECURRENCE}")
                del sanitized["recurrence_pattern"]

        # CRITICAL FIX 3: Priority validation
        if "priority" in sanitized:
            priority = sanitized["priority"]
            if priority not in cls.VALID_PRIORITIES:
                # Default to "none"
                print(f"⚠️ Invalid priority '{priority}' changed to 'none'")
                sanitized["priority"] = "none"
        else:
            # Set default priority
            sanitized["priority"] = "none"

        # CRITICAL FIX 4: due_date validation
        if "due_date" in sanitized and sanitized["due_date"]:
            sanitized["due_date"] = cls._validate_iso_date(sanitized["due_date"])

        # CRITICAL FIX 5: Tags validation (ensure it's a list)
        if "tags" in sanitized:
            if not isinstance(sanitized["tags"], list):
                sanitized["tags"] = []
            # Remove empty strings
            sanitized["tags"] = [tag for tag in sanitized["tags"] if tag and tag.strip()]

        # CRITICAL FIX 6: Remove null values
        sanitized = {k: v for k, v in sanitized.items() if v is not None}

        return sanitized

    @classmethod
    def validate_update_task(cls, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize update_task arguments.

        Fixes:
        1. Ensure task_id is present
        2. Remove null/empty update fields (no point updating with null)
        3. Validate updated values (priority, due_date, etc.)

        Args:
            args: Tool arguments dict

        Returns:
            Sanitized arguments dict
        """
        sanitized = args.copy()

        # CRITICAL FIX 1: task_id is required
        if "task_id" not in sanitized or sanitized["task_id"] is None:
            raise ValueError("task_id is required for update_task")

        # CRITICAL FIX 2: Remove null/empty update fields
        # We only want to update fields that have actual values
        fields_to_check = ["title", "description", "priority", "due_date", "tags"]
        for field in fields_to_check:
            if field in sanitized:
                value = sanitized[field]
                # Remove if null, empty string, or empty list
                if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                    del sanitized[field]

        # CRITICAL FIX 3: Priority validation
        if "priority" in sanitized:
            priority = sanitized["priority"]
            if priority not in cls.VALID_PRIORITIES:
                print(f"⚠️ Invalid priority '{priority}' changed to 'none'")
                sanitized["priority"] = "none"

        # CRITICAL FIX 4: due_date validation
        if "due_date" in sanitized and sanitized["due_date"]:
            sanitized["due_date"] = cls._validate_iso_date(sanitized["due_date"])

        # CRITICAL FIX 5: Tags validation
        if "tags" in sanitized:
            if not isinstance(sanitized["tags"], list):
                sanitized["tags"] = []
            sanitized["tags"] = [tag for tag in sanitized["tags"] if tag and tag.strip()]

        return sanitized

    @staticmethod
    def _generate_description(title: str, user_message: str = "") -> str:
        """
        Auto-generate description when missing.

        Strategy:
        1. Use title as description (works for simple tasks)
        2. Extract from user message if available
        3. Provide generic description

        Args:
            title: Task title
            user_message: Original user message

        Returns:
            Generated description
        """
        # Strategy 1: Use title (most common case)
        if title and len(title.strip()) > 0:
            return f"Task: {title.strip()}"

        # Strategy 2: Extract from user message
        if user_message and len(user_message.strip()) > 0:
            # Clean up message (remove command keywords)
            clean_msg = user_message.lower()
            remove_keywords = ["add", "create", "new", "task", "remind me to", "remember to"]
            for keyword in remove_keywords:
                clean_msg = clean_msg.replace(keyword, "")
            clean_msg = clean_msg.strip()

            if len(clean_msg) > 0:
                return clean_msg.capitalize()

        # Strategy 3: Generic fallback
        return "Task to be completed"

    @staticmethod
    def _validate_iso_date(date_value: str) -> Optional[str]:
        """
        Validate and normalize ISO 8601 date string.

        Args:
            date_value: Date string to validate

        Returns:
            Validated ISO date string or None if invalid
        """
        if not date_value or date_value in ["null", "none", ""]:
            return None

        try:
            # Try parsing as ISO format
            if isinstance(date_value, str):
                # Handle common formats
                if "T" in date_value:
                    # Already ISO format
                    datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                    return date_value
                else:
                    # Date only, add time
                    dt = datetime.fromisoformat(date_value)
                    return dt.isoformat()
            return date_value
        except Exception as e:
            print(f"⚠️ Invalid date format '{date_value}': {e}")
            return None

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language (English, Urdu, or Hindi).

        Returns: "english", "urdu", "hindi"
        """
        # Urdu Unicode ranges: U+0600 to U+06FF (Arabic script)
        urdu_pattern = re.compile(r'[\u0600-\u06FF]')

        # Hindi Unicode ranges: U+0900 to U+097F (Devanagari script)
        hindi_pattern = re.compile(r'[\u0900-\u097F]')

        if hindi_pattern.search(text):
            return "hindi"
        elif urdu_pattern.search(text):
            return "urdu"
        else:
            return "english"

    @classmethod
    def validate_language(cls, user_message: str) -> tuple[bool, Optional[str]]:
        """
        Validate that user message is in supported language (English or Urdu only).

        Args:
            user_message: User's message

        Returns:
            Tuple of (is_valid, error_message)
        """
        language = cls.detect_language(user_message)

        if language == "hindi":
            return False, "Sorry, Hindi is not supported. Please use English or Urdu (اردو)."

        return True, None


# Convenience functions
def validate_add_task(args: Dict[str, Any], user_message: str = "") -> Dict[str, Any]:
    """
    Validate add_task arguments.

    Usage:
        safe_args = validate_add_task(tool_args, user_message)
        result = await call_tool("add_task", safe_args)
    """
    return ToolValidator.validate_add_task(args, user_message)


def validate_update_task(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate update_task arguments.

    Usage:
        safe_args = validate_update_task(tool_args)
        result = await call_tool("update_task", safe_args)
    """
    return ToolValidator.validate_update_task(args)


def validate_language(user_message: str) -> tuple[bool, Optional[str]]:
    """
    Check if language is supported.

    Usage:
        is_valid, error = validate_language(user_message)
        if not is_valid:
            return error
    """
    return ToolValidator.validate_language(user_message)
