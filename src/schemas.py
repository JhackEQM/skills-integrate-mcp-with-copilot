"""
Pydantic schemas for API request/response validation.

These schemas define the structure of data sent to and from the API.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class StudentBase(BaseModel):
    """Base student schema with common fields."""
    email: str
    name: Optional[str] = None


class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    pass


class StudentResponse(StudentBase):
    """Schema for student response from API."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allow reading from SQLAlchemy models


class ActivityBase(BaseModel):
    """Base activity schema with common fields."""
    name: str
    description: str
    schedule: str
    max_participants: int


class ActivityCreate(ActivityBase):
    """Schema for creating a new activity."""
    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = None


class ActivityResponse(ActivityBase):
    """Schema for activity response from API."""
    id: int
    created_at: datetime
    updated_at: datetime
    participant_count: int
    available_slots: int
    is_full: bool
    participants: List[StudentResponse] = []

    class Config:
        from_attributes = True  # Allow reading from SQLAlchemy models


class ActivityListResponse(ActivityBase):
    """Schema for activity in list response (without detailed participants)."""
    id: int
    participant_count: int
    available_slots: int
    is_full: bool

    class Config:
        from_attributes = True
