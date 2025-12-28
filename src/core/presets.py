"""
15 Life Categories - Predefined Task Templates
===============================================
Provides realistic task presets for common life areas.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any


class LifePresets:
    """15 predefined categories with realistic tasks."""

    PRAYER: List[Dict[str, Any]] = [
        {"title": "Fajr Prayer", "description": "Morning prayer before sunrise", "priority": "high", "tags": ["prayer", "fajr"], "recurrence_pattern": "daily"},
        {"title": "Dhuhr Prayer", "description": "Afternoon prayer at noon", "priority": "high", "tags": ["prayer", "dhuhr"], "recurrence_pattern": "daily"},
        {"title": "Asr Prayer", "description": "Late afternoon prayer", "priority": "high", "tags": ["prayer", "asr"], "recurrence_pattern": "daily"},
        {"title": "Maghrib Prayer", "description": "Evening prayer at sunset", "priority": "high", "tags": ["prayer", "maghrib"], "recurrence_pattern": "daily"},
        {"title": "Isha Prayer", "description": "Night prayer", "priority": "high", "tags": ["prayer", "isha"], "recurrence_pattern": "daily"},
    ]

    SCHOOL: List[Dict[str, Any]] = [
        {"title": "Math Homework Ch5", "description": "Complete exercises 1-20", "priority": "high", "tags": ["homework", "math"], "recurrence_pattern": None},
        {"title": "Physics Class", "description": "Attend weekly physics lecture", "priority": "medium", "tags": ["class", "physics"], "recurrence_pattern": "weekly"},
        {"title": "Chemistry Exam Prep", "description": "Study for midterm exam", "priority": "high", "tags": ["exam", "chemistry"], "recurrence_pattern": None},
        {"title": "English Essay", "description": "Write 1000-word essay", "priority": "medium", "tags": ["homework", "english"], "recurrence_pattern": None},
    ]

    RAMZAN: List[Dict[str, Any]] = [
        {"title": "Sehri Reminder", "description": "Pre-dawn meal before fasting", "priority": "high", "tags": ["ramzan", "sehri"], "recurrence_pattern": "daily"},
        {"title": "Iftar Reminder", "description": "Breaking fast at sunset", "priority": "high", "tags": ["ramzan", "iftar"], "recurrence_pattern": "daily"},
        {"title": "Taraweeh Prayer", "description": "Special Ramzan night prayer", "priority": "high", "tags": ["ramzan", "taraweeh"], "recurrence_pattern": "daily"},
        {"title": "Quran Reading - 1 Juz", "description": "Read one para daily", "priority": "high", "tags": ["ramzan", "quran"], "recurrence_pattern": "daily"},
    ]

    FITNESS: List[Dict[str, Any]] = [
        {"title": "Morning Workout", "description": "30-min cardio or strength training", "priority": "high", "tags": ["fitness", "gym"], "recurrence_pattern": "daily"},
        {"title": "Drink 8 Glasses Water", "description": "Stay hydrated throughout the day", "priority": "medium", "tags": ["fitness", "water"], "recurrence_pattern": "daily"},
        {"title": "Yoga Session", "description": "Stretching and flexibility", "priority": "medium", "tags": ["fitness", "yoga"], "recurrence_pattern": "weekly"},
    ]

    CHORES: List[Dict[str, Any]] = [
        {"title": "Weekly Laundry", "description": "Wash, dry, and fold clothes", "priority": "medium", "tags": ["chores", "laundry"], "recurrence_pattern": "weekly"},
        {"title": "Room Cleaning", "description": "Vacuum and organize bedroom", "priority": "low", "tags": ["chores", "cleaning"], "recurrence_pattern": "weekly"},
        {"title": "Kitchen Cleaning", "description": "Wash dishes and clean counters", "priority": "medium", "tags": ["chores", "kitchen"], "recurrence_pattern": "daily"},
    ]

    MEAL_PLANNING: List[Dict[str, Any]] = [
        {"title": "Dinner Preparation", "description": "Cook evening meal", "priority": "medium", "tags": ["meal", "cooking"], "recurrence_pattern": "daily"},
        {"title": "Grocery Shopping", "description": "Buy weekly groceries", "priority": "high", "tags": ["meal", "grocery"], "recurrence_pattern": "weekly"},
        {"title": "Meal Prep Sunday", "description": "Prepare meals for the week", "priority": "high", "tags": ["meal", "prep"], "recurrence_pattern": "weekly"},
    ]

    FREELANCE: List[Dict[str, Any]] = [
        {"title": "Client Meeting - Weekly", "description": "Project status discussion", "priority": "high", "tags": ["freelance", "client"], "recurrence_pattern": "weekly"},
        {"title": "Send Monthly Invoice", "description": "Invoice for completed work", "priority": "high", "tags": ["freelance", "invoice"], "recurrence_pattern": "monthly"},
        {"title": "Update Portfolio", "description": "Add recent projects to portfolio", "priority": "medium", "tags": ["freelance", "portfolio"], "recurrence_pattern": None},
    ]

    JOB_HUNTING: List[Dict[str, Any]] = [
        {"title": "Update Resume", "description": "Add recent experience and skills", "priority": "high", "tags": ["jobhunt", "resume"], "recurrence_pattern": None},
        {"title": "Apply to Jobs - Weekly", "description": "Apply to 5 positions", "priority": "high", "tags": ["jobhunt", "apply"], "recurrence_pattern": "weekly"},
        {"title": "LinkedIn Profile Update", "description": "Optimize for recruiters", "priority": "medium", "tags": ["jobhunt", "linkedin"], "recurrence_pattern": None},
    ]

    CONTENT_CREATION: List[Dict[str, Any]] = [
        {"title": "YouTube Video Edit", "description": "Edit and upload weekly video", "priority": "high", "tags": ["content", "youtube"], "recurrence_pattern": "weekly"},
        {"title": "Blog Post Draft", "description": "Write article for blog", "priority": "medium", "tags": ["content", "blog"], "recurrence_pattern": "weekly"},
        {"title": "Social Media Posts", "description": "Schedule posts for the week", "priority": "medium", "tags": ["content", "social"], "recurrence_pattern": "weekly"},
    ]

    FINANCE: List[Dict[str, Any]] = [
        {"title": "Pay Electricity Bill", "description": "Monthly utility payment", "priority": "high", "tags": ["finance", "bills"], "recurrence_pattern": "monthly"},
        {"title": "Review Monthly Budget", "description": "Analyze expenses vs income", "priority": "medium", "tags": ["finance", "budget"], "recurrence_pattern": "monthly"},
        {"title": "Transfer to Savings", "description": "Move 20% to savings account", "priority": "high", "tags": ["finance", "savings"], "recurrence_pattern": "monthly"},
    ]

    LEARNING: List[Dict[str, Any]] = [
        {"title": "LeetCode Daily", "description": "Solve 1 coding problem", "priority": "high", "tags": ["learning", "coding"], "recurrence_pattern": "daily"},
        {"title": "Read Tech Article", "description": "Read one technical blog post", "priority": "medium", "tags": ["learning", "reading"], "recurrence_pattern": "daily"},
        {"title": "Online Course Module", "description": "Complete one course lesson", "priority": "medium", "tags": ["learning", "course"], "recurrence_pattern": "weekly"},
    ]

    LANGUAGE: List[Dict[str, Any]] = [
        {"title": "Duolingo Practice", "description": "Complete daily lesson", "priority": "high", "tags": ["language", "duolingo"], "recurrence_pattern": "daily"},
        {"title": "Vocabulary - 10 Words", "description": "Learn new vocabulary", "priority": "medium", "tags": ["language", "vocab"], "recurrence_pattern": "daily"},
        {"title": "Speaking Practice", "description": "Practice conversation for 15 mins", "priority": "high", "tags": ["language", "speaking"], "recurrence_pattern": "daily"},
    ]

    FAMILY: List[Dict[str, Any]] = [
        {"title": "Family Dinner Together", "description": "Quality time with family", "priority": "high", "tags": ["family", "dinner"], "recurrence_pattern": "daily"},
        {"title": "Call Parents", "description": "Check in with parents", "priority": "high", "tags": ["family", "parents"], "recurrence_pattern": "weekly"},
        {"title": "Kids Homework Help", "description": "Help children with assignments", "priority": "medium", "tags": ["family", "kids"], "recurrence_pattern": "daily"},
    ]

    SELFCARE: List[Dict[str, Any]] = [
        {"title": "Morning Meditation", "description": "10-minute mindfulness practice", "priority": "high", "tags": ["selfcare", "meditation"], "recurrence_pattern": "daily"},
        {"title": "Gratitude Journaling", "description": "Write 3 things you're grateful for", "priority": "medium", "tags": ["selfcare", "journal"], "recurrence_pattern": "daily"},
        {"title": "Digital Detox Hour", "description": "No phone/laptop for 1 hour", "priority": "medium", "tags": ["selfcare", "detox"], "recurrence_pattern": "daily"},
    ]

    EVENTS: List[Dict[str, Any]] = [
        {"title": "Birthday Planning", "description": "Plan upcoming birthday celebration", "priority": "high", "tags": ["events", "birthday"], "recurrence_pattern": None},
        {"title": "Wedding Anniversary", "description": "Plan special dinner", "priority": "high", "tags": ["events", "anniversary"], "recurrence_pattern": None},
        {"title": "Holiday Preparation", "description": "Prepare for upcoming holiday", "priority": "medium", "tags": ["events", "holiday"], "recurrence_pattern": None},
    ]

    ALL_CATEGORIES: Dict[str, List[Dict[str, Any]]] = {
        "prayer": PRAYER,
        "school": SCHOOL,
        "ramzan": RAMZAN,
        "fitness": FITNESS,
        "chores": CHORES,
        "meal": MEAL_PLANNING,
        "freelance": FREELANCE,
        "jobhunt": JOB_HUNTING,
        "content": CONTENT_CREATION,
        "finance": FINANCE,
        "learning": LEARNING,
        "language": LANGUAGE,
        "family": FAMILY,
        "selfcare": SELFCARE,
        "events": EVENTS,
    }

    CATEGORY_NAMES: Dict[str, str] = {
        "prayer": "Prayer Schedule",
        "school": "School Management",
        "ramzan": "Ramzan Tracker",
        "fitness": "Fitness & Health",
        "chores": "Home Chores",
        "meal": "Meal Planning",
        "freelance": "Freelance Work",
        "jobhunt": "Job Hunting",
        "content": "Content Creation",
        "finance": "Finance",
        "learning": "Learning & Coding",
        "language": "Language Learning",
        "family": "Family & Kids",
        "selfcare": "Self-Care",
        "events": "Events & Occasions",
    }

    @staticmethod
    def get_smart_due_date(hours_offset: int = 1) -> datetime:
        """
        Generate smart due dates based on recurrence pattern.
        Default: 1 hour from now for non-recurring tasks.
        """
        return datetime.now() + timedelta(hours=hours_offset)

    @staticmethod
    def get_category_tasks(category_key: str) -> List[Dict[str, Any]]:
        """Get tasks for a specific category."""
        return LifePresets.ALL_CATEGORIES.get(category_key, [])

    @staticmethod
    def get_all_category_keys() -> List[str]:
        """Get list of all category keys."""
        return list(LifePresets.ALL_CATEGORIES.keys())
