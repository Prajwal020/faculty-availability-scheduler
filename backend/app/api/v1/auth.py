from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, RegisterStudentRequest, RegisterFacultyRequest
from app.schemas.user import UserProfileResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/student",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Student account",
)
def register_student(
    data: RegisterStudentRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return service.register_student(data)


@router.post(
    "/register/faculty",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Faculty account",
)
def register_faculty(
    data: RegisterFacultyRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return service.register_faculty(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT token",
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    return service.login(data)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = AuthService(db)
    return service.get_user_profile(current_user.id)
