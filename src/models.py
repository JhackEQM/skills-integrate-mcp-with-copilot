"""
SQLAlchemy ORM models for Mergington High School activities management.

These models define the database schema for activities and student registrations.
"""

from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# Association table for the many-to-many relationship between students and activities
student_activity_association = Table(
    'student_activity',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id', ondelete='CASCADE')),
    Column('activity_id', Integer, ForeignKey('activities.id', ondelete='CASCADE'))
)


class Activity(Base):
    """
    Represents an extracurricular activity offered at the school.
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String(1000), nullable=False)
    schedule = Column(String(255), nullable=False)
    max_participants = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to students
    participants = relationship(
        "Student",
        secondary=student_activity_association,
        back_populates="activities"
    )

    def __repr__(self):
        return f"<Activity(id={self.id}, name={self.name}, max_participants={self.max_participants})>"

    @property
    def participant_count(self):
        """Get the current number of participants."""
        return len(self.participants)

    @property
    def available_slots(self):
        """Get the number of available slots."""
        return self.max_participants - self.participant_count

    @property
    def is_full(self):
        """Check if the activity is at maximum capacity."""
        return self.participant_count >= self.max_participants


class Student(Base):
    """
    Represents a student who can sign up for activities.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to activities
    activities = relationship(
        "Activity",
        secondary=student_activity_association,
        back_populates="participants"
    )

    def __repr__(self):
        return f"<Student(id={self.id}, email={self.email})>"
