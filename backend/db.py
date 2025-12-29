"""
Database connection and session management.

Task: 1.3
Spec: specs/database/schema.md
"""
from sqlmodel import create_engine, Session, SQLModel
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (set to False in production)
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Max 10 connections
    max_overflow=20  # Allow 20 overflow connections
)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency function to get database session.
    Use with FastAPI Depends.
    """
    with Session(engine) as session:
        yield session
