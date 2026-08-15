from datetime import datetime, date as date_type
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.leave import LeaveType, LeaveStatus


class LeaveBase(BaseModel):
    start_date: date_type = Field(..., description="Start calendar date of leave")
    end_date: date_type = Field(..., description="End calendar date of leave")
    leave_type: LeaveType = Field(default=LeaveType.FULL_DAY, description="FULL_DAY, HALF_DAY_MORNING, HALF_DAY_AFTERNOON, MULTI_DAY")
    reason: str = Field(..., min_length=2, max_length=255, description="Reason for leave declaration")

    @field_validator("end_date")
    @classmethod
    def validate_end_after_start(cls, v: date_type, info) -> date_type:
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be on or after start_date")
        return v


class LeaveCreate(LeaveBase):
    pass


class LeaveUpdate(BaseModel):
    reason: Optional[str] = Field(None, min_length=2, max_length=255)
    status: Optional[LeaveStatus] = None


class LeaveResponse(LeaveBase):
    id: UUID
    faculty_id: UUID
    status: LeaveStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
