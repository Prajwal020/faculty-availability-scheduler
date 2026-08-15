from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_student, require_faculty, require_faculty_or_admin
from app.models.user import User
from app.models.appointment import AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentActionRequest,
    AppointmentResponse,
    AppointmentFilter,
)
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments & Booking Engine"])


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an appointment request for a faculty slot (Student only)",
)
def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    service = AppointmentService(db)
    return service.book_appointment(current_user, data)


@router.get(
    "/me",
    response_model=List[AppointmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List authenticated user's appointments with optional filters",
)
def list_my_appointments(
    status: Optional[AppointmentStatus] = Query(None, description="Filter by status (REQUESTED, ACCEPTED, etc.)"),
    date: Optional[date] = Query(None, description="Filter by exact date (YYYY-MM-DD)"),
    from_date: Optional[date] = Query(None, description="Filter from date (inclusive)"),
    to_date: Optional[date] = Query(None, description="Filter to date (inclusive)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AppointmentResponse]:
    service = AppointmentService(db)
    filters = AppointmentFilter(
        status=status,
        date=date,
        from_date=from_date,
        to_date=to_date,
    )
    return service.list_user_appointments(current_user, filters)


@router.get(
    "/{id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get appointment details by ID (Student/Faculty participant or Admin)",
)
def get_appointment_details(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    service = AppointmentService(db)
    return service.get_appointment(current_user, id)


@router.put(
    "/{id}/accept",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept a requested appointment (Faculty owner only)",
)
def accept_appointment(
    id: UUID,
    data: Optional[AppointmentActionRequest] = None,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    service = AppointmentService(db)
    notes = data.faculty_notes if data else None
    return service.accept_appointment(current_user, id, notes=notes)


@router.put(
    "/{id}/reject",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a requested appointment (Faculty owner only)",
)
def reject_appointment(
    id: UUID,
    data: Optional[AppointmentActionRequest] = None,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    service = AppointmentService(db)
    reason = data.reason if data else None
    return service.reject_appointment(current_user, id, reason=reason)


@router.put(
    "/{id}/cancel",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel an active appointment (Student owner, Faculty owner, or Admin)",
)
def cancel_appointment(
    id: UUID,
    data: Optional[AppointmentActionRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    service = AppointmentService(db)
    reason = data.reason if data else None
    return service.cancel_appointment(current_user, id, reason=reason)


@router.put(
    "/{id}/complete",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark an accepted appointment as completed (Faculty owner or Admin)",
)
def complete_appointment(
    id: UUID,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    service = AppointmentService(db)
    return service.complete_appointment(current_user, id)
