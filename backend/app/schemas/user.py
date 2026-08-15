from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.models.user import UserRole, UserStatus
from app.schemas.student import StudentResponse
from app.schemas.faculty import FacultyResponse


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150, examples=["Dr. Alan Turing"])


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, examples=["StrongPassword123!"])
    role: UserRole = Field(default=UserRole.STUDENT)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserResponse):
    student_profile: Optional[StudentResponse] = None
    faculty_profile: Optional[FacultyResponse] = None

    model_config = ConfigDict(from_attributes=True)
