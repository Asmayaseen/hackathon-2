"""
Database connection and session management.

Task: 1.3, T014
Spec: specs/database/schema.md, specs/1-phase2-advanced-features/data-model.md
"""
from sqlmodel import create_engine, Session, SQLModel
import os

# Get database URL from environment
# Use SQLite for testing, PostgreSQL for production
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "test":
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")

# Create database engine with connection pooling
# SQLite doesn't support pool_size/max_overflow
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Log SQL queries (set to False in production)
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Max 10 connections
        max_overflow=20  # Allow 20 overflow connections
    )


def create_db_and_tables():
    """Create all database tables (T014, T-CHAT-001)."""
    # Import all models to register them with SQLModel metadata
    from models import (
        User, Task, TaskHistory, UserPreferences, Tag, Notification,
        Conversation, Message  # Phase III: ChatKit models
    )
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency function to get database session.
    Use with FastAPI Depends.
    """
    with Session(engine) as session:
        yield session
