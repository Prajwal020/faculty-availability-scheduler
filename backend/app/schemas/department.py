from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20, examples=["CS", "MATH"])
    name: str = Field(..., min_length=2, max_length=150, examples=["Computer Science & Engineering"])
    building: Optional[str] = Field(None, max_length=100, examples=["Science Block A"])


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    building: Optional[str] = Field(None, max_length=100)


class DepartmentResponse(DepartmentBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
