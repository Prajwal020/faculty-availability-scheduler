from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import require_student, require_faculty
from app.models.user import User
from app.schemas.student import StudentResponse, StudentUpdate
from app.schemas.faculty import FacultyResponse, FacultyUpdate, FacultyPublicProfile
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users & Profiles"])


# Student Profile Endpoints
@router.get(
    "/students/me",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current student's detailed profile",
)
def get_my_student_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentResponse:
    service = UserService(db)
    return service.get_student_profile(current_user.id)


@router.put(
    "/students/me",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current student's profile",
)
def update_my_student_profile(
    data: StudentUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentResponse:
    service = UserService(db)
    return service.update_student_profile(current_user.id, data)


# Faculty Profile Endpoints
@router.get(
    "/faculty/me",
    response_model=FacultyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current faculty's detailed profile",
)
def get_my_faculty_profile(
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
) -> FacultyResponse:
    service = UserService(db)
    return service.get_faculty_profile(current_user.id)


@router.put(
    "/faculty/me",
    response_model=FacultyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current faculty's profile",
)
def update_my_faculty_profile(
    data: FacultyUpdate,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
) -> FacultyResponse:
    service = UserService(db)
    return service.update_faculty_profile(current_user.id, data)


# Public / Discovery Faculty Endpoints
@router.get(
    "/faculty",
    response_model=List[FacultyPublicProfile],
    status_code=status.HTTP_200_OK,
    summary="Search & list active faculty members",
)
def list_faculty(
    name: Optional[str] = Query(None, description="Search by faculty full name"),
    department_id: Optional[UUID] = Query(None, description="Filter by department ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[FacultyPublicProfile]:
    service = UserService(db)
    return service.list_faculty(name=name, department_id=department_id, skip=skip, limit=limit)


@router.get(
    "/faculty/{faculty_id}",
    response_model=FacultyPublicProfile,
    status_code=status.HTTP_200_OK,
    summary="Get public profile of a faculty member",
)
def get_faculty_public_profile(
    faculty_id: UUID,
    db: Session = Depends(get_db),
) -> FacultyPublicProfile:
    service = UserService(db)
    return service.get_faculty_public_profile(faculty_id)
