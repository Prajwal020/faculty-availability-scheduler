from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.models.faculty import MeetingMode
from app.schemas.user import UserProfileResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse


class RegisterStudentRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters.")
    full_name: str = Field(..., min_length=2, max_length=150)
    student_id_number: str = Field(..., min_length=2, max_length=50)
    major: str = Field(..., min_length=2, max_length=100)


class RegisterFacultyRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters.")
    full_name: str = Field(..., min_length=2, max_length=150)
    employee_id_number: str = Field(..., min_length=2, max_length=50)
    department_id: UUID
    title: str = Field(..., min_length=2, max_length=100)
    office_location: str = Field(..., min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=2000)
    meeting_mode: MeetingMode = Field(default=MeetingMode.IN_PERSON)
