from datetime import datetime, date, time, timedelta
from typing import List, Optional
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.time_utils import get_current_time
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ForbiddenException,
    BadRequestException,
)
from app.models.user import User, UserRole, UserStatus
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.appointment import Appointment, AppointmentStatus
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentFilter,
    StudentSummary,
    FacultySummary,
)
from app.services.availability_service import AvailabilityService


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AppointmentRepository(db)
        self.user_repo = UserRepository(db)
        self.avail_service = AvailabilityService(db)
        self.tz = ZoneInfo(settings.TIMEZONE)

    def _build_response(self, appt: Appointment) -> AppointmentResponse:
        student_summary = None
        if appt.student and appt.student.user:
            student_summary = StudentSummary(
                id=appt.student.id,
                user_id=appt.student.user.id,
                full_name=appt.student.user.full_name,
                email=appt.student.user.email,
                student_id_number=appt.student.student_id_number,
                major=appt.student.major,
            )

        faculty_summary = None
        if appt.faculty and appt.faculty.user:
            dept_name = appt.faculty.department.name if appt.faculty.department else None
            faculty_summary = FacultySummary(
                id=appt.faculty.id,
                user_id=appt.faculty.user.id,
                full_name=appt.faculty.user.full_name,
                email=appt.faculty.user.email,
                employee_id_number=appt.faculty.employee_id_number,
                title=appt.faculty.title,
                office_location=appt.faculty.office_location,
                department_name=dept_name,
            )

        return AppointmentResponse(
            id=appt.id,
            student_id=appt.student_id,
            faculty_id=appt.faculty_id,
            student=student_summary,
            faculty=faculty_summary,
            date=appt.date,
            start_time=appt.start_time,
            end_time=appt.end_time,
            duration_minutes=appt.duration_minutes,
            status=appt.status,
            reason=appt.reason,
            faculty_notes=appt.faculty_notes,
            cancellation_reason=appt.cancellation_reason,
            created_at=appt.created_at,
            updated_at=appt.updated_at,
        )

    def book_appointment(self, current_user: User, data: AppointmentCreate) -> AppointmentResponse:
        """
        Concurrency-safe atomic appointment booking:
        1. Authenticates student and validates timing/duration.
        2. Locks the target Faculty row (FOR UPDATE) to serialize booking requests for this faculty member.
        3. Recalculates available slots on server (zero client trust).
        4. Checks for conflicting active appointments.
        5. Inserts REQUESTED appointment within atomic transaction.
        6. Rolls back cleanly on any failure or constraint violation.
        """
        # 1. Authenticate and verify Student role
        if current_user.role != UserRole.STUDENT:
            raise ForbiddenException(
                code="INSUFFICIENT_PERMISSIONS",
                message="Only authenticated students can book appointments.",
            )

        student = self.user_repo.get_student_by_user_id(current_user.id)
        if not student:
            raise NotFoundException(
                code="STUDENT_PROFILE_NOT_FOUND",
                message="Student profile not found for authenticated user.",
            )

        now = get_current_time(settings.TIMEZONE)

        # 2. Validate timing and duration
        start_dt = datetime.combine(data.date, data.start_time, tzinfo=self.tz)
        if start_dt <= now:
            raise BadRequestException(
                code="PAST_APPOINTMENT",
                message="Cannot book an appointment in the past.",
            )

        duration_sec = (datetime.combine(data.date, data.end_time) - datetime.combine(data.date, data.start_time)).total_seconds()
        duration_minutes = int(duration_sec / 60)
        if duration_minutes <= 0 or duration_minutes > 120:
            raise BadRequestException(
                code="INVALID_APPOINTMENT_DURATION",
                message="Appointment duration must be between 15 and 120 minutes.",
            )

        try:
            # 3. Acquire row lock on target Faculty to serialize concurrent booking requests for this faculty member
            faculty_query = self.db.query(Faculty).filter(Faculty.id == data.faculty_id)
            # Only apply with_for_update on backends supporting it
            if self.db.bind and self.db.bind.dialect.name != "sqlite":
                faculty_query = faculty_query.with_for_update()
            
            faculty = faculty_query.first()
            if not faculty or faculty.user.status != UserStatus.ACTIVE:
                raise NotFoundException(
                    code="FACULTY_NOT_FOUND",
                    message="Target faculty member not found or inactive.",
                )

            # 4. Server-side Availability Recalculation (Zero client trust)
            avail_resp = self.avail_service.get_faculty_availability(
                faculty_id=data.faculty_id,
                target_date=data.date,
                duration_minutes=duration_minutes,
            )

            req_start_str = f"{data.start_time.hour:02d}:{data.start_time.minute:02d}"
            req_end_str = f"{data.end_time.hour:02d}:{data.end_time.minute:02d}"

            matching_slot = None
            for slot in avail_resp.slots:
                if slot.start_time == req_start_str and slot.end_time == req_end_str:
                    matching_slot = slot
                    break

            if not matching_slot:
                raise ConflictException(
                    code="SLOT_UNAVAILABLE",
                    message="The requested appointment slot is not available in the faculty member's schedule.",
                )

            # 5. Overlap Check for active appointments (Tier 1 reservations)
            conflict = self.repo.check_conflicting_appointment(
                faculty_id=data.faculty_id,
                target_date=data.date,
                start_time=data.start_time,
                end_time=data.end_time,
                for_update=True,
            )
            if conflict:
                raise ConflictException(
                    code="SLOT_UNAVAILABLE",
                    message="The selected appointment slot has just been reserved by another student.",
                )

            # 6. Create REQUESTED appointment
            appt = Appointment(
                student_id=student.id,
                faculty_id=data.faculty_id,
                date=data.date,
                start_time=data.start_time,
                end_time=data.end_time,
                duration_minutes=duration_minutes,
                status=AppointmentStatus.REQUESTED,
                reason=data.reason.strip(),
            )
            created = self.repo.create(appt)
            self.db.commit()

            # Re-fetch eager-loaded appointment for clean response
            loaded_appt = self.repo.get_by_id(created.id)
            return self._build_response(loaded_appt)

        except (ConflictException, NotFoundException, ForbiddenException, BadRequestException):
            self.db.rollback()
            raise
        except IntegrityError:
            self.db.rollback()
            raise ConflictException(
                code="SLOT_UNAVAILABLE",
                message="The selected appointment slot is no longer available.",
            )
        except Exception:
            self.db.rollback()
            raise

    def accept_appointment(
        self, current_user: User, appointment_id: UUID, notes: Optional[str] = None
    ) -> AppointmentResponse:
        appt = self.repo.get_by_id(appointment_id, for_update=True)
        if not appt:
            raise NotFoundException(
                code="APPOINTMENT_NOT_FOUND",
                message="Appointment record not found.",
            )

        # Authorization: Faculty owner or Admin
        if current_user.role != UserRole.ADMIN:
            if current_user.role != UserRole.FACULTY or appt.faculty.user_id != current_user.id:
                raise ForbiddenException(
                    code="UNAUTHORIZED_APPOINTMENT_ACTION",
                    message="You can only accept appointments assigned to your faculty profile.",
                )

        # State transition validation
        if appt.status not in (AppointmentStatus.REQUESTED, AppointmentStatus.RESCHEDULE_PROPOSED):
            raise ConflictException(
                code="INVALID_APPOINTMENT_STATE",
                message=f"Cannot accept appointment in {appt.status.value} status.",
            )

        appt.status = AppointmentStatus.ACCEPTED
        if notes:
            appt.faculty_notes = notes.strip()

        self.repo.update(appt)
        self.db.commit()
        return self._build_response(appt)

    def reject_appointment(
        self, current_user: User, appointment_id: UUID, reason: Optional[str] = None
    ) -> AppointmentResponse:
        appt = self.repo.get_by_id(appointment_id, for_update=True)
        if not appt:
            raise NotFoundException(
                code="APPOINTMENT_NOT_FOUND",
                message="Appointment record not found.",
            )

        # Authorization: Faculty owner or Admin
        if current_user.role != UserRole.ADMIN:
            if current_user.role != UserRole.FACULTY or appt.faculty.user_id != current_user.id:
                raise ForbiddenException(
                    code="UNAUTHORIZED_APPOINTMENT_ACTION",
                    message="You can only reject appointments assigned to your faculty profile.",
                )

        # State transition validation
        if appt.status not in (AppointmentStatus.REQUESTED, AppointmentStatus.RESCHEDULE_PROPOSED):
            raise ConflictException(
                code="INVALID_APPOINTMENT_STATE",
                message=f"Cannot reject appointment in {appt.status.value} status.",
            )

        appt.status = AppointmentStatus.REJECTED
        if reason:
            appt.cancellation_reason = reason.strip()

        self.repo.update(appt)
        self.db.commit()
        return self._build_response(appt)

    def cancel_appointment(
        self, current_user: User, appointment_id: UUID, reason: Optional[str] = None
    ) -> AppointmentResponse:
        appt = self.repo.get_by_id(appointment_id, for_update=True)
        if not appt:
            raise NotFoundException(
                code="APPOINTMENT_NOT_FOUND",
                message="Appointment record not found.",
            )

        # Authorization: Student owner, Faculty owner, or Admin
        is_student_owner = current_user.role == UserRole.STUDENT and appt.student.user_id == current_user.id
        is_faculty_owner = current_user.role == UserRole.FACULTY and appt.faculty.user_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not (is_student_owner or is_faculty_owner or is_admin):
            raise ForbiddenException(
                code="UNAUTHORIZED_APPOINTMENT_ACTION",
                message="You do not have permission to cancel this appointment.",
            )

        # State transition validation (terminal states cannot be cancelled)
        if appt.status in (AppointmentStatus.REJECTED, AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED):
            raise ConflictException(
                code="INVALID_APPOINTMENT_STATE",
                message=f"Cannot cancel an appointment already in {appt.status.value} status.",
            )

        appt.status = AppointmentStatus.CANCELLED
        if reason:
            appt.cancellation_reason = reason.strip()

        self.repo.update(appt)
        self.db.commit()
        return self._build_response(appt)

    def complete_appointment(self, current_user: User, appointment_id: UUID) -> AppointmentResponse:
        appt = self.repo.get_by_id(appointment_id, for_update=True)
        if not appt:
            raise NotFoundException(
                code="APPOINTMENT_NOT_FOUND",
                message="Appointment record not found.",
            )

        # Authorization: Faculty owner or Admin
        if current_user.role != UserRole.ADMIN:
            if current_user.role != UserRole.FACULTY or appt.faculty.user_id != current_user.id:
                raise ForbiddenException(
                    code="UNAUTHORIZED_APPOINTMENT_ACTION",
                    message="You can only complete appointments assigned to your faculty profile.",
                )

        if appt.status != AppointmentStatus.ACCEPTED:
            raise ConflictException(
                code="INVALID_APPOINTMENT_STATE",
                message="Only ACCEPTED appointments can be marked as COMPLETED.",
            )

        # Validate that appointment end time has passed
        now = get_current_time(settings.TIMEZONE)
        appt_end_dt = datetime.combine(appt.date, appt.end_time, tzinfo=self.tz)
        if now < appt_end_dt:
            raise BadRequestException(
                code="APPOINTMENT_NOT_YET_FINISHED",
                message="Appointment cannot be marked as completed before its scheduled end time.",
            )

        appt.status = AppointmentStatus.COMPLETED
        self.repo.update(appt)
        self.db.commit()
        return self._build_response(appt)

    def get_appointment(self, current_user: User, appointment_id: UUID) -> AppointmentResponse:
        appt = self.repo.get_by_id(appointment_id)
        if not appt:
            raise NotFoundException(
                code="APPOINTMENT_NOT_FOUND",
                message="Appointment record not found.",
            )

        # IDOR Authorization check
        is_student_owner = current_user.role == UserRole.STUDENT and appt.student.user_id == current_user.id
        is_faculty_owner = current_user.role == UserRole.FACULTY and appt.faculty.user_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not (is_student_owner or is_faculty_owner or is_admin):
            raise ForbiddenException(
                code="FORBIDDEN_RESOURCE",
                message="You do not have permission to access this appointment.",
            )

        return self._build_response(appt)

    def list_user_appointments(
        self, current_user: User, filters: AppointmentFilter
    ) -> List[AppointmentResponse]:
        student_id = None
        faculty_id = None

        if current_user.role == UserRole.STUDENT:
            student = self.user_repo.get_student_by_user_id(current_user.id)
            if not student:
                return []
            student_id = student.id
        elif current_user.role == UserRole.FACULTY:
            faculty = self.user_repo.get_faculty_by_user_id(current_user.id)
            if not faculty:
                return []
            faculty_id = faculty.id

        items = self.repo.list_appointments(
            student_id=student_id,
            faculty_id=faculty_id,
            date_filter=filters.date,
            from_date=filters.from_date,
            to_date=filters.to_date,
            status=filters.status,
        )
        return [self._build_response(item) for item in items]
