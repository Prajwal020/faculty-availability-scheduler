from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import require_faculty, require_faculty_or_admin
from app.models.user import User
from app.schemas.availability import (
    RegularAvailabilityCreate,
    RegularAvailabilityUpdate,
    RegularAvailabilityResponse,
    TemporaryAvailabilityCreate,
    TemporaryAvailabilityResponse,
    BlockedSlotCreate,
    BlockedSlotUpdate,
    BlockedSlotResponse,
    FacultyAvailabilityResponse,
)
from app.schemas.common import MessageResponse
from app.services.availability_service import AvailabilityService

router = APIRouter(prefix="/availability", tags=["Faculty Availability Engine"])


# 1. Regular Weekly Availability Endpoints
@router.post(
    "/regular",
    response_model=RegularAvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Define recurring weekly availability (Faculty only)",
)
def create_regular_availability(
    data: RegularAvailabilityCreate,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
) -> RegularAvailabilityResponse:
    service = AvailabilityService(db)
    return service.create_regular_availability(current_user, data)


@router.get(
    "/regular",
    response_model=List[RegularAvailabilityResponse],
    status_code=status.HTTP_200_OK,
    summary="List recurring availability windows (Faculty / Admin)",
)
def list_regular_availability(
    faculty_id: Optional[UUID] = Query(None, description="Target faculty ID (Admin only)"),
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> List[RegularAvailabilityResponse]:
    service = AvailabilityService(db)
    return service.list_regular_availability(current_user, faculty_id)


@router.put(
    "/regular/{id}",
    response_model=RegularAvailabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a recurring availability window (Faculty only)",
)
def update_regular_availability(
    id: UUID,
    data: RegularAvailabilityUpdate,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
) -> RegularAvailabilityResponse:
    service = AvailabilityService(db)
    return service.update_regular_availability(current_user, id, data)


@router.delete(
    "/regular/{id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a recurring availability window (Faculty only)",
)
def delete_regular_availability(
    id: UUID,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = AvailabilityService(db)
    service.delete_regular_availability(current_user, id)
    return MessageResponse(message="Regular availability window deleted successfully.")


# 2. Temporary Availability Endpoints
@router.post(
    "/temporary",
    response_model=TemporaryAvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Publish one-time temporary availability (Faculty only)",
)
def create_temporary_availability(
    data: TemporaryAvailabilityCreate,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
) -> TemporaryAvailabilityResponse:
    service = AvailabilityService(db)
    return service.create_temporary_availability(current_user, data)


@router.get(
    "/temporary",
    response_model=List[TemporaryAvailabilityResponse],
    status_code=status.HTTP_200_OK,
    summary="List temporary availability entries (Faculty / Admin)",
)
def list_temporary_availability(
    faculty_id: Optional[UUID] = Query(None, description="Target faculty ID (Admin only)"),
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> List[TemporaryAvailabilityResponse]:
    service = AvailabilityService(db)
    return service.list_temporary_availability(current_user, faculty_id)


@router.delete(
    "/temporary/{id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a temporary availability entry (Faculty only)",
)
def delete_temporary_availability(
    id: UUID,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = AvailabilityService(db)
    service.delete_temporary_availability(current_user, id)
    return MessageResponse(message="Temporary availability record deleted successfully.")


# 3. Blocked Slots Endpoints
@router.post(
    "/blocked",
    response_model=BlockedSlotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a temporary unavailable block period (Faculty / Admin)",
)
def create_blocked_slot(
    data: BlockedSlotCreate,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> BlockedSlotResponse:
    service = AvailabilityService(db)
    return service.create_blocked_slot(current_user, data)


@router.get(
    "/blocked",
    response_model=List[BlockedSlotResponse],
    status_code=status.HTTP_200_OK,
    summary="List blocked slots (Faculty / Admin)",
)
def list_blocked_slots(
    faculty_id: Optional[UUID] = Query(None, description="Target faculty ID (Admin only)"),
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> List[BlockedSlotResponse]:
    service = AvailabilityService(db)
    return service.list_blocked_slots(current_user, faculty_id)


@router.delete(
    "/blocked/{id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a blocked slot (Faculty / Admin)",
)
def delete_blocked_slot(
    id: UUID,
    current_user: User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = AvailabilityService(db)
    service.delete_blocked_slot(current_user, id)
    return MessageResponse(message="Blocked slot deleted successfully.")


# 4. Master Dynamic Availability Calculation (Student / Public Query)
@router.get(
    "/{faculty_id}",
    response_model=FacultyAvailabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate dynamic bookable availability slots for a faculty member on a given date",
)
def get_faculty_availability(
    faculty_id: UUID,
    date: date = Query(..., description="Target calendar date (YYYY-MM-DD)"),
    duration: int = Query(30, ge=15, le=120, description="Slot duration in minutes"),
    min_notice: int = Query(0, ge=0, description="Minimum advance lead notice in minutes"),
    db: Session = Depends(get_db),
) -> FacultyAvailabilityResponse:
    service = AvailabilityService(db)
    return service.get_faculty_availability(
        faculty_id=faculty_id,
        target_date=date,
        duration_minutes=duration,
        min_lead_notice_minutes=min_notice,
    )
