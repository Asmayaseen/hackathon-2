#!/usr/bin/env python3
"""
Password Reset Script for Evolution Todo
Usage: python reset_password.py <email> <new_password>
"""
import sys
import hashlib
import os
from sqlmodel import Session, create_engine, select
from models import User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def hash_password(password: str) -> str:
    """Hash password using SHA256 (same as auth.py)."""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_user_password(email: str, new_password: str):
    """Reset password for a user by email."""

    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env")
        sys.exit(1)

    # Create engine and session
    engine = create_engine(database_url, echo=False)

    with Session(engine) as session:
        # Find user by email
        user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if not user:
            print(f"❌ ERROR: User with email '{email}' not found")
            sys.exit(1)

        # Hash new password
        new_hash = hash_password(new_password)

        # Update password
        user.password_hash = new_hash
        session.add(user)
        session.commit()

        print(f"✅ SUCCESS: Password reset for user: {user.email}")
        print(f"   Name: {user.name}")
        print(f"   User ID: {user.id}")
        print(f"   New password: {new_password}")
        print(f"\n🔐 You can now login with:")
        print(f"   Email: {user.email}")
        print(f"   Password: {new_password}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        print("\nExample:")
        print("  python reset_password.py asmayaseen9960@gmail.com MyNewPassword123")
        sys.exit(1)

    email = sys.argv[1]
    new_password = sys.argv[2]

    if len(new_password) < 8:
        print("❌ ERROR: Password must be at least 8 characters")
        sys.exit(1)

    print(f"🔄 Resetting password for: {email}")
    reset_user_password(email, new_password)
