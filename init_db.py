#!/usr/bin/env python3
"""
Database initialization script.

This script initializes the database by:
1. Creating the database if it doesn't exist (for MySQL)
2. Running all pending migrations
3. Optionally loading sample data

Usage:
    python init_db.py              # Run migrations
    python init_db.py --seed       # Run migrations and load sample data
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import engine, init_db
from models import Activity, Student, Base
from sqlalchemy.orm import Session


def run_migrations():
    """Run Alembic migrations."""
    print("Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running migrations:\n{result.stderr}")
        return False
    
    print("✓ Migrations completed successfully")
    return True


def load_sample_data():
    """Load sample data into the database."""
    print("\nLoading sample data...")
    
    db = Session(bind=engine)
    
    try:
        # Check if data already exists
        existing_activities = db.query(Activity).count()
        if existing_activities > 0:
            print("✓ Sample data already exists, skipping...")
            return True
        
        # Create sample activities
        activities = [
            Activity(
                name="Debate Club",
                description="Develop public speaking and argumentation skills",
                schedule="Tuesdays 4-5 PM",
                max_participants=20
            ),
            Activity(
                name="Robotics Team",
                description="Build and program robots for competitions",
                schedule="Thursdays 4-6 PM",
                max_participants=15
            ),
            Activity(
                name="Science Club",
                description="Explore science through experiments and projects",
                schedule="Wednesdays 4-5 PM",
                max_participants=25
            ),
            Activity(
                name="Chess Club",
                description="Play chess and improve strategic thinking",
                schedule="Mondays 4-5 PM",
                max_participants=30
            ),
            Activity(
                name="Art Society",
                description="Create and showcase various art forms",
                schedule="Fridays 4-5 PM",
                max_participants=20
            ),
        ]
        
        # Create sample students
        students = [
            Student(email="alice@school.edu", name="Alice Johnson"),
            Student(email="bob@school.edu", name="Bob Smith"),
            Student(email="charlie@school.edu", name="Charlie Davis"),
            Student(email="diana@school.edu", name="Diana Wilson"),
            Student(email="eva@school.edu", name="Eva Martinez"),
        ]
        
        # Add all objects to session
        db.add_all(activities)
        db.add_all(students)
        db.flush()  # Flush to get IDs without committing
        
        # Add some signups
        if len(students) >= 2 and len(activities) >= 2:
            students[0].activities.append(activities[0])
            students[0].activities.append(activities[2])
            students[1].activities.append(activities[1])
            students[2].activities.append(activities[0])
            students[2].activities.append(activities[1])
        
        db.commit()
        print(f"✓ Loaded {len(activities)} activities and {len(students)} students")
        return True
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Initialize the database."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument("--seed", action="store_true", help="Load sample data")
    args = parser.parse_args()
    
    print("=" * 50)
    print("Database Initialization")
    print("=" * 50)
    
    # Get database URL
    db_url = os.getenv(
        "DATABASE_URL",
        "mysql+mysqlconnector://root:password@localhost:3306/mergington_school"
    )
    print(f"\nDatabase URL: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Load sample data if requested
    if args.seed:
        if not load_sample_data():
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ Database initialization completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
