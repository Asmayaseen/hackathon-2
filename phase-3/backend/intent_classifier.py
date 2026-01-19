"""
Intent Classifier for Evolution Todo Chatbot.

Purpose: Classify user intent to prevent tool misuse and improve accuracy.
Fixes: Agent calling update_task when intent is ADD_TASK.

Task: DEBUG-CHATBOT-001
"""
from typing import Optional, Literal
import re

# Intent types
IntentType = Literal["ADD_TASK", "UPDATE_TASK", "DELETE_TASK", "LIST_TASKS", "COMPLETE_TASK", "SEARCH", "ANALYTICS", "UNCLEAR"]


class IntentClassifier:
    """
    Classifies user intent before tool execution.

    Prevents common errors:
    - Calling update_task when user wants to add a task
    - Sending null values to tools
    - Incorrect tool selection
    """

    # Keywords for each intent type
    ADD_TASK_KEYWORDS = [
        # English
        "add", "create", "new", "make", "remind", "remember", "schedule", "set",
        "buy", "call", "send", "write", "book", "plan", "organize",
        # Roman Urdu
        "banao", "banana", "yaad", "dilao", "karna", "karwana",
        # Urdu
        "بنانا", "بناؤ", "یاد", "دلانا", "کرنا"
    ]

    UPDATE_TASK_KEYWORDS = [
        # English
        "update", "change", "modify", "edit", "move", "reschedule", "shift", "postpone",
        "rename", "alter", "adjust",
        # Roman Urdu
        "badlo", "badalna", "tabdeel", "edit",
        # Urdu
        "بدلنا", "بدلو", "تبدیل"
    ]

    DELETE_TASK_KEYWORDS = [
        # English
        "delete", "remove", "cancel", "discard", "drop", "clear",
        # Roman Urdu
        "delete", "hatao", "khatam", "mitao",
        # Urdu
        "ڈیلیٹ", "ہٹاؤ", "ختم", "مٹاؤ"
    ]

    LIST_TASK_KEYWORDS = [
        # English
        "list", "show", "display", "view", "see", "get", "what", "fetch", "all",
        # Roman Urdu
        "dikhao", "dekho", "batao", "sab", "saray",
        # Urdu
        "دکھاؤ", "دیکھو", "بتاؤ", "سب", "سارے"
    ]

    COMPLETE_TASK_KEYWORDS = [
        # English
        "complete", "done", "finish", "mark", "tick", "check",
        # Roman Urdu
        "mukammal", "hogaya", "karliya", "khatam",
        # Urdu
        "مکمل", "ہوگیا", "کرلیا", "ختم"
    ]

    SEARCH_KEYWORDS = [
        # English
        "search", "find", "look", "where",
        # Roman Urdu
        "dhundo", "khojo", "talash",
        # Urdu
        "ڈھونڈو", "کھوجو", "تلاش"
    ]

    @classmethod
    def classify(cls, user_message: str, conversation_history: list = None) -> IntentType:
        """
        Classify user intent from message.

        Args:
            user_message: User's input message
            conversation_history: Previous messages for context (optional)

        Returns:
            IntentType: Classified intent
        """
        message_lower = user_message.lower().strip()

        # Priority 1: ADD_TASK (most common, check first)
        # Examples: "add task", "remind me", "buy groceries", "call mom"
        if cls._contains_keywords(message_lower, cls.ADD_TASK_KEYWORDS):
            # Check if it's NOT an update (explicit update keywords override)
            if not cls._contains_keywords(message_lower, ["update", "change", "modify", "edit", "move", "reschedule"]):
                return "ADD_TASK"

        # Priority 2: UPDATE_TASK (explicit update intent)
        # Examples: "update task 5", "change priority", "move to tomorrow"
        if cls._contains_keywords(message_lower, cls.UPDATE_TASK_KEYWORDS):
            # Check for task ID mention (strong indicator of update)
            if cls._has_task_id(message_lower):
                return "UPDATE_TASK"
            # Check for explicit update keywords
            if any(kw in message_lower for kw in ["update", "change", "modify", "edit", "reschedule", "move"]):
                return "UPDATE_TASK"

        # Priority 3: COMPLETE_TASK
        # Examples: "mark task 3 as done", "complete task"
        if cls._contains_keywords(message_lower, cls.COMPLETE_TASK_KEYWORDS):
            return "COMPLETE_TASK"

        # Priority 4: DELETE_TASK
        # Examples: "delete task 5", "remove this task"
        if cls._contains_keywords(message_lower, cls.DELETE_TASK_KEYWORDS):
            return "DELETE_TASK"

        # Priority 5: SEARCH
        # Examples: "search for groceries", "find tasks about meeting"
        if cls._contains_keywords(message_lower, cls.SEARCH_KEYWORDS):
            return "SEARCH"

        # Priority 6: LIST_TASKS
        # Examples: "show my tasks", "list all pending", "what's due today"
        if cls._contains_keywords(message_lower, cls.LIST_TASK_KEYWORDS):
            return "LIST_TASKS"

        # Priority 7: ANALYTICS
        # Examples: "show stats", "how many tasks", "summary"
        if any(kw in message_lower for kw in ["stats", "statistics", "summary", "analytics", "how many", "count"]):
            return "ANALYTICS"

        # Priority 8: Implicit ADD_TASK (action verbs without explicit "add")
        # Examples: "buy groceries", "call mom", "email boss"
        action_verbs = ["buy", "call", "send", "email", "write", "book", "pay", "clean", "fix"]
        if any(verb in message_lower for verb in action_verbs):
            # Make sure it's not asking for a list
            if not cls._contains_keywords(message_lower, ["show", "list", "what", "display"]):
                return "ADD_TASK"

        # Default: UNCLEAR (let AI decide)
        return "UNCLEAR"

    @staticmethod
    def _contains_keywords(text: str, keywords: list) -> bool:
        """Check if text contains any of the keywords."""
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _has_task_id(text: str) -> bool:
        """Check if text mentions a task ID."""
        # Pattern: "task 5", "task #10", "task id 3", "ID: 5"
        patterns = [
            r"task\s+#?\d+",
            r"task\s+id\s+\d+",
            r"id[:\s]+\d+",
            r"#\d+"
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    @classmethod
    def get_confidence_score(cls, user_message: str, intent: IntentType) -> float:
        """
        Get confidence score (0.0 to 1.0) for classified intent.

        Higher score = more confident in classification.
        """
        message_lower = user_message.lower()

        # Strong indicators
        if intent == "ADD_TASK":
            if any(kw in message_lower for kw in ["add task", "create task", "new task", "remind me"]):
                return 0.95
            if any(kw in message_lower for kw in cls.ADD_TASK_KEYWORDS[:10]):  # Top keywords
                return 0.85
            return 0.70

        if intent == "UPDATE_TASK":
            if cls._has_task_id(message_lower) and any(kw in message_lower for kw in ["update", "change", "modify"]):
                return 0.95
            if any(kw in message_lower for kw in cls.UPDATE_TASK_KEYWORDS[:5]):
                return 0.85
            return 0.70

        if intent == "DELETE_TASK":
            if cls._has_task_id(message_lower) and any(kw in message_lower for kw in ["delete", "remove"]):
                return 0.95
            return 0.80

        if intent == "LIST_TASKS":
            if any(kw in message_lower for kw in ["show all", "list all", "show my"]):
                return 0.90
            return 0.75

        # Default: medium confidence
        return 0.60


# Convenience function
def classify_intent(user_message: str, conversation_history: list = None) -> IntentType:
    """
    Classify user intent.

    Usage:
        intent = classify_intent("Add a task to buy groceries")
        # Returns: "ADD_TASK"
    """
    return IntentClassifier.classify(user_message, conversation_history)
