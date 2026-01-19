#!/usr/bin/env python3
"""
Reset user password directly in database.
Usage: python reset_user_password.py
"""
import os
import hashlib
from sqlmodel import Session, select, create_engine
from models import User
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_password():
    """Reset password for asmayaseen9960@gmail.com"""

    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env")
        return

    print(f"📍 Connecting to database...")
    engine = create_engine(DATABASE_URL, echo=False)

    with Session(engine) as session:
        # Find user
        user = session.exec(
            select(User).where(User.email == "asmayaseen9960@gmail.com")
        ).first()

        if not user:
            print("❌ User not found: asmayaseen9960@gmail.com")
            return

        print(f"✅ User found: {user.name} ({user.email})")
        print(f"   User ID: {user.id}")
        print()

        # Set new password
        new_password = "Evolution@123"
        user.password_hash = hash_password(new_password)

        session.add(user)
        session.commit()

        print("✅ Password reset successfully!")
        print()
        print("📝 New Login Credentials:")
        print("   Email: asmayaseen9960@gmail.com")
        print(f"   Password: {new_password}")
        print()
        print("🔐 Password hash:", user.password_hash[:50] + "...")
        print()
        print("Now try logging in at: http://localhost:3000/login")

if __name__ == "__main__":
    reset_password()
