from datetime import datetime, date, time, timedelta
from typing import List, Optional
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time_utils import get_current_time, get_current_date
from app.core.exceptions import ConflictException, NotFoundException, ForbiddenException, BadRequestException
from app.models.user import User, UserRole, UserStatus
from app.models.faculty import Faculty
from app.models.availability import RegularAvailability, TemporaryAvailability, BlockedSlot
from app.models.leave import LeaveRecord, LeaveType, LeaveStatus
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.leave_repository import LeaveRepository
from app.repositories.user_repository import UserRepository
from app.repositories.appointment_repository import AppointmentRepository
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
    TimeIntervalSchema,
    BookableSlotSchema,
)
from app.services.scheduling_engine import SchedulingEngine, TimeInterval


class AvailabilityService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AvailabilityRepository(db)
        self.leave_repo = LeaveRepository(db)
        self.user_repo = UserRepository(db)
        self.appt_repo = AppointmentRepository(db)
        self.tz = ZoneInfo(settings.TIMEZONE)

    def _get_faculty_for_user(self, current_user: User) -> Faculty:
        if current_user.role == UserRole.FACULTY:
            faculty = self.user_repo.get_faculty_by_user_id(current_user.id)
            if not faculty:
                raise NotFoundException(
                    code="FACULTY_PROFILE_NOT_FOUND",
                    message="Faculty profile not found for the authenticated user.",
                )
            return faculty
        raise ForbiddenException(
            code="INSUFFICIENT_PERMISSIONS",
            message="Operation requires FACULTY role.",
        )

    # 1. Regular Weekly Availability CRUD
    def create_regular_availability(
        self, current_user: User, data: RegularAvailabilityCreate
    ) -> RegularAvailabilityResponse:
        faculty = self._get_faculty_for_user(current_user)

        # Overlap check
        if self.repo.check_regular_overlap(
            faculty_id=faculty.id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
        ):
            raise ConflictException(
                code="REGULAR_AVAILABILITY_OVERLAP",
                message=f"Recurring availability for day {data.day_of_week} ({data.start_time} - {data.end_time}) overlaps with an existing window.",
            )

        reg = RegularAvailability(
            faculty_id=faculty.id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            slot_duration_minutes=data.slot_duration_minutes,
            is_active=data.is_active,
        )
        created = self.repo.create_regular(reg)
        self.db.commit()
        self.db.refresh(created)
        return RegularAvailabilityResponse.model_validate(created)

    def list_regular_availability(
        self, current_user: User, faculty_id: Optional[UUID] = None
    ) -> List[RegularAvailabilityResponse]:
        if faculty_id and current_user.role == UserRole.ADMIN:
            target_faculty_id = faculty_id
        else:
            faculty = self._get_faculty_for_user(current_user)
            target_faculty_id = faculty.id

        items = self.repo.list_regular_by_faculty(target_faculty_id)
        return [RegularAvailabilityResponse.model_validate(item) for item in items]

    def update_regular_availability(
        self, current_user: User, id: UUID, data: RegularAvailabilityUpdate
    ) -> RegularAvailabilityResponse:
        faculty = self._get_faculty_for_user(current_user)
        reg = self.repo.get_regular_by_id(id)
        if not reg or reg.faculty_id != faculty.id:
            raise NotFoundException(
                code="REGULAR_AVAILABILITY_NOT_FOUND",
                message="Regular availability window not found.",
            )

        new_start = data.start_time or reg.start_time
        new_end = data.end_time or reg.end_time

        if new_end <= new_start:
            raise BadRequestException(
                code="INVALID_TIME_RANGE",
                message="end_time must be strictly after start_time.",
            )

        # Overlap check
        if self.repo.check_regular_overlap(
            faculty_id=faculty.id,
            day_of_week=reg.day_of_week,
            start_time=new_start,
            end_time=new_end,
            exclude_id=reg.id,
        ):
            raise ConflictException(
                code="REGULAR_AVAILABILITY_OVERLAP",
                message="Updated time window overlaps with an existing regular availability window.",
            )

        if data.start_time:
            reg.start_time = data.start_time
        if data.end_time:
            reg.end_time = data.end_time
        if data.slot_duration_minutes:
            reg.slot_duration_minutes = data.slot_duration_minutes
        if data.is_active is not None:
            reg.is_active = data.is_active

        updated = self.repo.update_regular(reg)
        self.db.commit()
        self.db.refresh(updated)
        return RegularAvailabilityResponse.model_validate(updated)

    def delete_regular_availability(self, current_user: User, id: UUID) -> None:
        faculty = self._get_faculty_for_user(current_user)
        reg = self.repo.get_regular_by_id(id)
        if not reg or reg.faculty_id != faculty.id:
            raise NotFoundException(
                code="REGULAR_AVAILABILITY_NOT_FOUND",
                message="Regular availability window not found.",
            )
        self.repo.delete_regular(reg)
        self.db.commit()

    # 2. Temporary Availability CRUD
    def create_temporary_availability(
        self, current_user: User, data: TemporaryAvailabilityCreate
    ) -> TemporaryAvailabilityResponse:
        faculty = self._get_faculty_for_user(current_user)
        now = get_current_time(settings.TIMEZONE)

        # Reject past date
        if data.date < now.date():
            raise BadRequestException(
                code="INVALID_DATE",
                message="Cannot publish temporary availability for a past date.",
            )

        # If date is today, reject if end_time is already in the past
        if data.date == now.date():
            end_dt = datetime.combine(data.date, data.end_time, tzinfo=self.tz)
            if end_dt <= now:
                raise BadRequestException(
                    code="AVAILABILITY_EXPIRED",
                    message="Cannot publish temporary availability that has already ended.",
                )

        target_date_start = datetime(data.date.year, data.date.month, data.date.day, 0, 0, 0, tzinfo=self.tz)
        target_date_end = target_date_start + timedelta(days=1)

        # Check if faculty has full-day leave on this date
        leave_records = self.leave_repo.get_active_leave_for_date_range(
            faculty_id=faculty.id,
            start_dt=target_date_start,
            end_dt=target_date_end,
        )
        for leave in leave_records:
            if leave.leave_type in (LeaveType.FULL_DAY, LeaveType.MULTI_DAY):
                raise ConflictException(
                    code="CANNOT_ADD_TEMP_AVAIL_DURING_LEAVE",
                    message="Cannot publish temporary availability on a date with approved full-day leave.",
                )

        # Check overlap with existing temporary availability
        if self.repo.check_temporary_overlap(
            faculty_id=faculty.id,
            target_date_start=target_date_start,
            target_date_end=target_date_end,
            start_time=data.start_time,
            end_time=data.end_time,
        ):
            raise ConflictException(
                code="TEMPORARY_AVAILABILITY_OVERLAP",
                message="Temporary availability overlaps with an existing temporary availability window on this date.",
            )

        temp = TemporaryAvailability(
            faculty_id=faculty.id,
            date=target_date_start,
            start_time=data.start_time,
            end_time=data.end_time,
            reason=data.reason.strip() if data.reason else None,
        )
        created = self.repo.create_temporary(temp)
        self.db.commit()
        self.db.refresh(created)
        return TemporaryAvailabilityResponse(
            id=created.id,
            faculty_id=created.faculty_id,
            date=data.date,
            start_time=created.start_time,
            end_time=created.end_time,
            reason=created.reason,
            created_at=created.created_at,
        )

    def list_temporary_availability(
        self, current_user: User, faculty_id: Optional[UUID] = None
    ) -> List[TemporaryAvailabilityResponse]:
        if faculty_id and current_user.role == UserRole.ADMIN:
            target_faculty_id = faculty_id
        else:
            faculty = self._get_faculty_for_user(current_user)
            target_faculty_id = faculty.id

        items = self.repo.list_temporary_by_faculty(target_faculty_id)
        return [
            TemporaryAvailabilityResponse(
                id=item.id,
                faculty_id=item.faculty_id,
                date=item.date.astimezone(self.tz).date(),
                start_time=item.start_time,
                end_time=item.end_time,
                reason=item.reason,
                created_at=item.created_at,
            )
            for item in items
        ]

    def delete_temporary_availability(self, current_user: User, id: UUID) -> None:
        faculty = self._get_faculty_for_user(current_user)
        temp = self.repo.get_temporary_by_id(id)
        if not temp or temp.faculty_id != faculty.id:
            raise NotFoundException(
                code="TEMPORARY_AVAILABILITY_NOT_FOUND",
                message="Temporary availability record not found.",
            )
        self.repo.delete_temporary(temp)
        self.db.commit()

    # 3. Blocked Slots CRUD
    def create_blocked_slot(
        self, current_user: User, data: BlockedSlotCreate
    ) -> BlockedSlotResponse:
        faculty = self._get_faculty_for_user(current_user)

        start_dt = data.start_datetime.astimezone(self.tz)
        end_dt = data.end_datetime.astimezone(self.tz)

        # Check overlap
        if self.repo.check_blocked_overlap(
            faculty_id=faculty.id,
            start_dt=start_dt,
            end_dt=end_dt,
        ):
            raise ConflictException(
                code="BLOCKED_SLOT_OVERLAP",
                message="The requested blocked slot overlaps with an existing blocked slot.",
            )

        block = BlockedSlot(
            faculty_id=faculty.id,
            start_datetime=start_dt,
            end_datetime=end_dt,
            reason=data.reason.strip(),
        )
        created = self.repo.create_blocked(block)
        self.db.commit()
        self.db.refresh(created)
        return BlockedSlotResponse.model_validate(created)

    def list_blocked_slots(
        self, current_user: User, faculty_id: Optional[UUID] = None
    ) -> List[BlockedSlotResponse]:
        if faculty_id and current_user.role == UserRole.ADMIN:
            target_faculty_id = faculty_id
        else:
            faculty = self._get_faculty_for_user(current_user)
            target_faculty_id = faculty.id

        items = self.repo.list_blocked_by_faculty(target_faculty_id)
        return [BlockedSlotResponse.model_validate(item) for item in items]

    def delete_blocked_slot(self, current_user: User, id: UUID) -> None:
        faculty = self._get_faculty_for_user(current_user)
        block = self.repo.get_blocked_by_id(id)
        if not block or block.faculty_id != faculty.id:
            raise NotFoundException(
                code="BLOCKED_SLOT_NOT_FOUND",
                message="Blocked slot record not found.",
            )
        self.repo.delete_blocked(block)
        self.db.commit()

    # 4. Master Dynamic Availability Calculation Engine Endpoint
    def get_faculty_availability(
        self,
        faculty_id: UUID,
        target_date: date,
        duration_minutes: int = 30,
        min_lead_notice_minutes: int = 0,
        current_time: Optional[datetime] = None,
    ) -> FacultyAvailabilityResponse:
        r"""
        Calculates dynamic bookable slots for target_date by evaluating:
        Regular Schedule, Temp Availability, Temp Blocks, Leave, and Active Appointments (P & C).
        Formula: A_final = ((R U T) \ B) \ (L U P U C)
        Strictly enforces privacy: Student response does NOT expose leave_reason or internal notes.
        """
        faculty = self.user_repo.get_faculty_by_id(faculty_id)
        if not faculty or faculty.user.status != UserStatus.ACTIVE:
            raise NotFoundException(
                code="FACULTY_NOT_FOUND",
                message="Faculty member not found or account is inactive.",
            )

        now = current_time if current_time is not None else get_current_time(settings.TIMEZONE)
        day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
        target_date_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=self.tz)
        target_date_end = target_date_start + timedelta(days=1)

        # 0. If target_date is in the past, return 0 slots immediately
        if target_date < now.date():
            return FacultyAvailabilityResponse(
                faculty_id=faculty.id,
                date=target_date.isoformat(),
                timezone=settings.TIMEZONE,
                day_of_week=day_of_week,
                is_on_leave=False,
                available_windows=[],
                slots=[],
                total_slots=0,
            )

        # 1. Load active Leave records (Tier 2)
        leave_records = self.leave_repo.get_active_leave_for_date_range(
            faculty_id=faculty.id,
            start_dt=target_date_start,
            end_dt=target_date_end,
        )

        leave_intervals: List[TimeInterval] = []
        is_full_day_leave = False

        for l in leave_records:
            if l.leave_type in (LeaveType.FULL_DAY, LeaveType.MULTI_DAY):
                is_full_day_leave = True
                leave_intervals.append(TimeInterval(0, 1440))
            elif l.leave_type == LeaveType.HALF_DAY_MORNING:
                # Morning: 00:00 to 13:00 (0 to 780 minutes)
                leave_intervals.append(TimeInterval(0, 13 * 60))
            elif l.leave_type == LeaveType.HALF_DAY_AFTERNOON:
                # Afternoon: 13:00 to 24:00 (780 to 1440 minutes)
                leave_intervals.append(TimeInterval(13 * 60, 1440))

        # Short-circuit if full-day leave
        if is_full_day_leave:
            return FacultyAvailabilityResponse(
                faculty_id=faculty.id,
                date=target_date.isoformat(),
                timezone=settings.TIMEZONE,
                day_of_week=day_of_week,
                is_on_leave=True,
                available_windows=[],
                slots=[],
                total_slots=0,
            )

        # 2. Load Regular Weekly Availability (Tier 5)
        reg_records = self.repo.get_regular_by_faculty_and_day(
            faculty_id=faculty.id,
            day_of_week=day_of_week,
            is_active=True,
        )
        regular_intervals = [
            TimeInterval.from_time(r.start_time, r.end_time) for r in reg_records
        ]

        # 3. Load Temporary Availability (Tier 4)
        temp_records = self.repo.get_temporary_by_faculty_and_date(
            faculty_id=faculty.id,
            target_date_start=target_date_start,
            target_date_end=target_date_end,
        )
        temp_intervals = [
            TimeInterval.from_time(t.start_time, t.end_time) for t in temp_records
        ]

        # 4. Load Blocked Slots (Tier 3)
        blocked_records = self.repo.get_blocked_for_date_range(
            faculty_id=faculty.id,
            start_dt=target_date_start,
            end_dt=target_date_end,
        )
        blocked_intervals = []
        for b in blocked_records:
            iv = TimeInterval.from_datetimes_on_date(b.start_datetime, b.end_datetime, target_date, self.tz)
            if iv:
                blocked_intervals.append(iv)

        # 5. Load Active Appointments (Tier 1: P & C)
        active_appts = self.appt_repo.get_active_appointments_for_faculty_on_date(
            faculty_id=faculty.id,
            target_date=target_date,
        )
        booked_intervals = [
            TimeInterval.from_time(a.start_time, a.end_time) for a in active_appts
        ]

        # 6. Compute Final Available Windows via Pure Domain Engine
        final_windows = SchedulingEngine.compute_final_available_windows(
            regular_intervals=regular_intervals,
            temporary_intervals=temp_intervals,
            blocked_intervals=blocked_intervals,
            leave_intervals=leave_intervals,
            booked_intervals=booked_intervals,
        )

        # 7. Generate Discrete Bookable Slots
        slots_data = SchedulingEngine.generate_discrete_slots(
            available_windows=final_windows,
            target_date=target_date,
            duration_minutes=duration_minutes,
            min_lead_notice_minutes=min_lead_notice_minutes,
            current_time=now,
            tz_name=settings.TIMEZONE,
        )

        slots_schemas = [BookableSlotSchema(**s) for s in slots_data]
        windows_schemas = [
            TimeIntervalSchema(start_time=w.start_time_str, end_time=w.end_time_str)
            for w in final_windows
        ]

        return FacultyAvailabilityResponse(
            faculty_id=faculty.id,
            date=target_date.isoformat(),
            timezone=settings.TIMEZONE,
            day_of_week=day_of_week,
            is_on_leave=len(leave_records) > 0,
            available_windows=windows_schemas,
            slots=slots_schemas,
            total_slots=len(slots_schemas),
        )
