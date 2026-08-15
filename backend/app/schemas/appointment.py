from datetime import datetime, time, date as date_type
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.appointment import AppointmentStatus


class StudentSummary(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    email: str
    student_id_number: str
    major: str

    model_config = ConfigDict(from_attributes=True)


class FacultySummary(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    email: str
    employee_id_number: str
    title: str
    office_location: str
    department_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    faculty_id: UUID = Field(..., description="Target faculty member ID")
    date: date_type = Field(..., description="Calendar date of appointment (YYYY-MM-DD)")
    start_time: time = Field(..., description="Start time (e.g. 10:00:00)")
    end_time: time = Field(..., description="End time (e.g. 10:30:00)")
    reason: str = Field(..., min_length=2, max_length=255, description="Purpose or agenda of appointment request")

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: time, info) -> time:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be strictly after start_time")
        return v


class AppointmentActionRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=255, description="Optional cancellation / rejection note")
    faculty_notes: Optional[str] = Field(None, max_length=255, description="Optional internal faculty notes")


class AppointmentResponse(BaseModel):
    id: UUID
    student_id: UUID
    faculty_id: UUID
    student: Optional[StudentSummary] = None
    faculty: Optional[FacultySummary] = None
    date: date_type
    start_time: time
    end_time: time
    duration_minutes: int
    status: AppointmentStatus
    reason: str
    faculty_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentFilter(BaseModel):
    status: Optional[AppointmentStatus] = None
    date: Optional[date_type] = None
    from_date: Optional[date_type] = None
    to_date: Optional[date_type] = None
