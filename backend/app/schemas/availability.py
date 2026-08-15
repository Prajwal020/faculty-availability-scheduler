from datetime import datetime, time, date as date_type
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


# Regular Availability Schemas
class RegularAvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 1=Tuesday, ..., 6=Sunday")
    start_time: time = Field(..., description="Start time of recurring availability (e.g. 09:00:00)")
    end_time: time = Field(..., description="End time of recurring availability (e.g. 12:00:00)")
    slot_duration_minutes: int = Field(default=30, description="Default slot duration in minutes (e.g. 15, 30, 60)")
    is_active: bool = Field(default=True)

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: time, info) -> time:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be strictly after start_time")
        return v


class RegularAvailabilityCreate(RegularAvailabilityBase):
    pass


class RegularAvailabilityUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class RegularAvailabilityResponse(RegularAvailabilityBase):
    id: UUID
    faculty_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Temporary Availability Schemas
class TemporaryAvailabilityBase(BaseModel):
    date: date_type = Field(..., description="Calendar date of temporary availability")
    start_time: time = Field(..., description="Start time (e.g. 11:15:00)")
    end_time: time = Field(..., description="End time (e.g. 11:45:00)")
    reason: Optional[str] = Field(None, max_length=255, description="Optional note (e.g. Cancelled lecture pop-up)")

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: time, info) -> time:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be strictly after start_time")
        return v


class TemporaryAvailabilityCreate(TemporaryAvailabilityBase):
    pass


class TemporaryAvailabilityResponse(TemporaryAvailabilityBase):
    id: UUID
    faculty_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Blocked Slot Schemas
class BlockedSlotBase(BaseModel):
    start_datetime: datetime = Field(..., description="Start timestamp of blocked period")
    end_datetime: datetime = Field(..., description="End timestamp of blocked period")
    reason: str = Field(..., min_length=2, max_length=255, description="Mandatory reason for blocking (e.g. Dept meeting)")

    @field_validator("end_datetime")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info) -> datetime:
        if "start_datetime" in info.data and v <= info.data["start_datetime"]:
            raise ValueError("end_datetime must be strictly after start_datetime")
        return v


class BlockedSlotCreate(BlockedSlotBase):
    pass


class BlockedSlotUpdate(BaseModel):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    reason: Optional[str] = None


class BlockedSlotResponse(BlockedSlotBase):
    id: UUID
    faculty_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Calculated Availability & Slot Generation Schemas
class TimeIntervalSchema(BaseModel):
    start_time: str = Field(..., examples=["09:00"])
    end_time: str = Field(..., examples=["12:00"])


class BookableSlotSchema(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    start_time: str = Field(..., examples=["09:00"])
    end_time: str = Field(..., examples=["09:30"])
    duration_minutes: int = Field(default=30)
    status: str = Field(default="AVAILABLE")


class FacultyAvailabilityResponse(BaseModel):
    """
    Student/Public availability response.
    Protects faculty privacy by omitting internal leave reasons and personal notes.
    """
    faculty_id: UUID
    date: str = Field(..., examples=["2026-08-15"])
    timezone: str = Field(default="Asia/Kolkata")
    day_of_week: int = Field(..., description="0=Monday, ..., 6=Sunday")
    is_on_leave: bool = False
    available_windows: List[TimeIntervalSchema] = []
    slots: List[BookableSlotSchema] = []
    total_slots: int = 0


class FacultyAvailabilityDetailResponse(FacultyAvailabilityResponse):
    """
    Faculty/Admin detailed availability response including administrative leave reason.
    """
    leave_reason: Optional[str] = None
