from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import require_faculty_or_admin
from app.models.user import User
from app.schemas.leave import LeaveCreate, LeaveResponse
from app.schemas.common import MessageResponse
from app.services.leave_service import LeaveService

router = APIRouter(prefix="/leave", tags=["Faculty Leave Management"])


@router.post(
    "",
    response_model=LeaveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Declare a leave period (Faculty / Admin)",
)
def create_leave(
    data: LeaveCreate,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> LeaveResponse:
    service = LeaveService(db)
    return service.create_leave(current_user, data)


@router.get(
    "",
    response_model=List[LeaveResponse],
    status_code=status.HTTP_200_OK,
    summary="List leave records (Faculty / Admin)",
)
def list_leave(
    faculty_id: Optional[UUID] = Query(None, description="Target faculty ID (Admin only)"),
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> List[LeaveResponse]:
    service = LeaveService(db)
    return service.list_faculty_leave(current_user, faculty_id)


@router.delete(
    "/{id}",
    response_model=LeaveResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel an existing leave record (Faculty / Admin)",
)
def cancel_leave(
    id: UUID,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> LeaveResponse:
    service = LeaveService(db)
    return service.cancel_leave(current_user, id)
