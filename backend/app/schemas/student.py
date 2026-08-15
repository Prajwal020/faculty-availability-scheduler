from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    student_id_number: str = Field(..., min_length=2, max_length=50, examples=["STU-2026-001"])
    major: str = Field(..., min_length=2, max_length=100, examples=["Computer Science"])


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    major: Optional[str] = Field(None, min_length=2, max_length=100)


class StudentResponse(StudentBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
