"""
Add conversations and messages tables for Phase III chatbot.

Task: T-CHAT-002
Spec: specs/phase-3-chatbot/spec.md
"""
from dotenv import load_dotenv
load_dotenv()

from sqlmodel import SQLModel, create_engine
import sys
import os

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Conversation, Message

def run_migration():
    """Create conversations and messages tables."""
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL environment variable not set")

    print("🔄 Starting Phase III chat tables migration...")
    print(f"📊 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Create only the new tables (idempotent)
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Conversation.__table__,
            Message.__table__
        ]
    )

    print("✅ Migration complete: conversations + messages tables created")
    print("📋 Tables created:")
    print("   - conversations (id, user_id, created_at, updated_at)")
    print("   - messages (id, conversation_id, user_id, role, content, tool_calls, created_at)")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
