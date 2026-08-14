"""
High School Management System API

A FastAPI application that allows students to view and sign up for extracurricular
activities at Mergington High School with persistent database storage.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
from pathlib import Path

from database import get_db, engine
from models import Activity, Student, Base
from schemas import (
    ActivityResponse, ActivityListResponse, ActivityCreate, ActivityUpdate,
    StudentResponse, StudentCreate
)

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities with persistent storage"
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent, "static")), name="static")


@app.get("/")
def root():
    """Redirect to the static index page."""
    return RedirectResponse(url="/static/index.html")


@app.get("/activities", response_model=dict)
def get_activities(db: Session = Depends(get_db)):
    """
    Get all activities.
    
    Returns a dictionary mapping activity names to their details,
    maintaining compatibility with the frontend structure.
    """
    activities = db.query(Activity).all()
    
    # Convert to dictionary format for frontend compatibility
    result = {}
    for activity in activities:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [student.email for student in activity.participants],
            "id": activity.id
        }
    
    return result


@app.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get details for a specific activity."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@app.post("/activities", response_model=ActivityResponse)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Create a new activity."""
    db_activity = Activity(**activity.dict())
    db.add(db_activity)
    
    try:
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Activity with this name already exists"
        )


@app.put("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity_update: ActivityUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing activity."""
    db_activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    update_data = activity_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_activity, key, value)
    
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity by name."""
    # Find activity by name
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if activity is full
    if activity.is_full:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Get or create student
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        student = Student(email=email)
        db.add(student)
        db.flush()  # Flush to get the student ID

    # Check if student is already signed up
    if student in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up for this activity"
        )

    # Add student to activity
    activity.participants.append(student)
    db.commit()

    return {
        "message": f"Signed up {email} for {activity_name}",
        "activity": activity_name,
        "email": email
    }


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity by name."""
    # Find activity by name
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Find student
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check if student is signed up
    if student not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student from activity
    activity.participants.remove(student)
    db.commit()

    return {
        "message": f"Unregistered {email} from {activity_name}",
        "activity": activity_name,
        "email": email
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Startup event to initialize sample data if database is empty
@app.on_event("startup")
def startup_event():
    """Initialize sample data if database is empty."""
    db = next(get_db())
    try:
        # Check if database already has activities
        if db.query(Activity).count() == 0:
            # Add sample activities
            sample_activities = [
                Activity(
                    name="Chess Club",
                    description="Learn strategies and compete in chess tournaments",
                    schedule="Fridays, 3:30 PM - 5:00 PM",
                    max_participants=12
                ),
                Activity(
                    name="Programming Class",
                    description="Learn programming fundamentals and build software projects",
                    schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                    max_participants=20
                ),
                Activity(
                    name="Gym Class",
                    description="Physical education and sports activities",
                    schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                    max_participants=30
                ),
                Activity(
                    name="Soccer Team",
                    description="Join the school soccer team and compete in matches",
                    schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                    max_participants=22
                ),
                Activity(
                    name="Basketball Team",
                    description="Practice and play basketball with the school team",
                    schedule="Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                    max_participants=15
                ),
                Activity(
                    name="Art Club",
                    description="Explore your creativity through painting and drawing",
                    schedule="Thursdays, 3:30 PM - 5:00 PM",
                    max_participants=15
                ),
                Activity(
                    name="Drama Club",
                    description="Act, direct, and produce plays and performances",
                    schedule="Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                    max_participants=20
                ),
                Activity(
                    name="Math Club",
                    description="Solve challenging problems and participate in math competitions",
                    schedule="Tuesdays, 3:30 PM - 4:30 PM",
                    max_participants=10
                ),
                Activity(
                    name="Debate Team",
                    description="Develop public speaking and argumentation skills",
                    schedule="Fridays, 4:00 PM - 5:30 PM",
                    max_participants=12
                ),
            ]
            
            # Add sample students and their signups
            sample_students_data = {
                "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
                "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
                "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
                "Soccer Team": ["liam@mergington.edu", "noah@mergington.edu"],
                "Basketball Team": ["ava@mergington.edu", "mia@mergington.edu"],
                "Art Club": ["amelia@mergington.edu", "harper@mergington.edu"],
                "Drama Club": ["ella@mergington.edu", "scarlett@mergington.edu"],
                "Math Club": ["james@mergington.edu", "benjamin@mergington.edu"],
                "Debate Team": ["charlotte@mergington.edu", "henry@mergington.edu"],
            }
            
            # Create activities and add students
            for activity in sample_activities:
                db.add(activity)
            db.flush()  # Flush to get activity IDs
            
            # Add participants to activities
            for activity_name, student_emails in sample_students_data.items():
                activity = db.query(Activity).filter(Activity.name == activity_name).first()
                for email in student_emails:
                    student = db.query(Student).filter(Student.email == email).first()
                    if not student:
                        student = Student(email=email)
                        db.add(student)
                        db.flush()
                    activity.participants.append(student)
            
            db.commit()
    finally:
        db.close()
