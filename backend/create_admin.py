#!/usr/bin/env python3
"""
Create initial admin user for the RAG system
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, create_tables
from app.models.user import User
from app.auth.auth import get_password_hash


def create_admin_user(email: str, password: str) -> bool:
    """Create an admin user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return False
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"Email: {email}")
        print(f"User ID: {admin_user.id}")
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main function"""
    print("RAG System - Admin User Creation")
    print("=" * 40)
    
    # Ensure tables exist
    try:
        create_tables()
        print("Database tables initialized")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        sys.exit(1)
    
    # Get admin credentials
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
    
    if not email or not password:
        print("Email and password are required!")
        sys.exit(1)
    
    # Validate email format
    if "@" not in email:
        print("Invalid email format!")
        sys.exit(1)
    
    # Create admin user
    success = create_admin_user(email, password)
    if success:
        print("\n✅ Admin user created successfully!")
        print("You can now login to the system with these credentials.")
    else:
        print("\n❌ Failed to create admin user!")
        sys.exit(1)


if __name__ == "__main__":
    main()