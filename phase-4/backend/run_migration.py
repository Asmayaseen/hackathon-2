"""
Database Migration Script - Run SQL migration files
Task: T004
Spec: specs/1-phase2-advanced-features/data-model.md
"""
from dotenv import load_dotenv
load_dotenv()

from sqlmodel import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, echo=True)

def run_migration_file(filepath: str):
    """Run a SQL migration file."""
    print(f"Running migration: {filepath}")

    with open(filepath, 'r') as f:
        sql_content = f.read()

    with engine.connect() as conn:
        # Execute the migration SQL
        conn.execute(text(sql_content))
        conn.commit()

    print(f"Migration {filepath} complete!")

if __name__ == "__main__":
    migration_file = "migrations/002_phase2_advanced.sql"

    if os.path.exists(migration_file):
        confirm = input(f"Run migration {migration_file}? (yes/no): ")
        if confirm.lower() == 'yes':
            run_migration_file(migration_file)
        else:
            print("Aborted.")
    else:
        print(f"ERROR: Migration file {migration_file} not found!")
