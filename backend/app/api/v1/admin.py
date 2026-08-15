from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserProfileResponse, UserStatusUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["Admin Governance"])


@router.get(
    "/users",
    response_model=List[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users with profiles (Admin only)",
)
def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> List[UserProfileResponse]:
    service = UserService(db)
    return service.list_all_users(skip=skip, limit=limit)


@router.post(
    "/users/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user with any role (Admin only)",
)
def create_user_by_admin(
    data: UserCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    return service.create_user_by_admin(data)


@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user status (ACTIVE, SUSPENDED, DEACTIVATED) (Admin only)",
)
def update_user_status(
    user_id: UUID,
    data: UserStatusUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    return service.update_user_status(user_id, data.status)
