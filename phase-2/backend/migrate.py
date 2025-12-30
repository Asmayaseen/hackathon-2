"""
Database Migration Script - Drop and recreate tables.

WARNING: This will delete all existing data!
"""
from dotenv import load_dotenv
load_dotenv()

from sqlmodel import SQLModel, create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, echo=True)

def reset_database():
    """Drop all tables and recreate them."""
    print("Dropping existing tables...")

    with engine.connect() as conn:
        # Drop tables if they exist
        conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()

    print("Creating new tables...")

    # Import models to register them with SQLModel
    from models import User, Task

    # Create all tables
    SQLModel.metadata.create_all(engine)

    print("Migration complete!")

if __name__ == "__main__":
    confirm = input("This will DELETE ALL DATA. Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Aborted.")
