from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.faculty import MeetingMode
from app.schemas.department import DepartmentResponse


class FacultyBase(BaseModel):
    employee_id_number: str = Field(..., min_length=2, max_length=50, examples=["FAC-1002"])
    title: str = Field(..., min_length=2, max_length=100, examples=["Associate Professor"])
    office_location: str = Field(..., min_length=2, max_length=100, examples=["Block B, Room 402"])
    bio: Optional[str] = Field(None, max_length=2000, examples=["Research in Distributed Systems and Cloud Computing."])
    meeting_mode: MeetingMode = Field(default=MeetingMode.IN_PERSON)


class FacultyCreate(FacultyBase):
    department_id: UUID


class FacultyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    office_location: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=2000)
    meeting_mode: Optional[MeetingMode] = None
    department_id: Optional[UUID] = None


class FacultyResponse(FacultyBase):
    id: UUID
    user_id: UUID
    department_id: UUID
    department: Optional[DepartmentResponse] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FacultyPublicProfile(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    email: str
    title: str
    office_location: str
    bio: Optional[str] = None
    meeting_mode: MeetingMode
    department_id: UUID
    department_name: str
    department_code: str

    model_config = ConfigDict(from_attributes=True)
