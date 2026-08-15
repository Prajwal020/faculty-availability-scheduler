from datetime import datetime, time, timedelta
from typing import List, Optional
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException, ForbiddenException
from app.models.user import User, UserRole
from app.models.faculty import Faculty
from app.models.leave import LeaveRecord, LeaveStatus
from app.repositories.leave_repository import LeaveRepository
from app.repositories.user_repository import UserRepository
from app.schemas.leave import LeaveCreate, LeaveUpdate, LeaveResponse


class LeaveService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LeaveRepository(db)
        self.user_repo = UserRepository(db)
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

    def create_leave(self, current_user: User, data: LeaveCreate) -> LeaveResponse:
        faculty = self._get_faculty_for_user(current_user)

        start_dt = datetime.combine(data.start_date, time(0, 0, 0), tzinfo=self.tz)
        end_dt = datetime.combine(data.end_date, time(23, 59, 59), tzinfo=self.tz)

        # Overlap check
        if self.repo.check_leave_overlap(
            faculty_id=faculty.id,
            start_dt=start_dt,
            end_dt=end_dt,
        ):
            raise ConflictException(
                code="LEAVE_OVERLAP_EXISTS",
                message="An approved leave record already covers part or all of the requested date range.",
            )

        leave = LeaveRecord(
            faculty_id=faculty.id,
            start_date=start_dt,
            end_date=end_dt,
            leave_type=data.leave_type,
            reason=data.reason.strip(),
            status=LeaveStatus.APPROVED,
        )
        created = self.repo.create(leave)
        self.db.commit()
        self.db.refresh(created)

        return LeaveResponse(
            id=created.id,
            faculty_id=created.faculty_id,
            start_date=data.start_date,
            end_date=data.end_date,
            leave_type=created.leave_type,
            reason=created.reason,
            status=created.status,
            created_at=created.created_at,
        )

    def list_faculty_leave(
        self, current_user: User, faculty_id: Optional[UUID] = None
    ) -> List[LeaveResponse]:
        if faculty_id and current_user.role == UserRole.ADMIN:
            target_faculty_id = faculty_id
        else:
            faculty = self._get_faculty_for_user(current_user)
            target_faculty_id = faculty.id

        items = self.repo.list_by_faculty(target_faculty_id)
        return [
            LeaveResponse(
                id=item.id,
                faculty_id=item.faculty_id,
                start_date=item.start_date.astimezone(self.tz).date(),
                end_date=item.end_date.astimezone(self.tz).date(),
                leave_type=item.leave_type,
                reason=item.reason,
                status=item.status,
                created_at=item.created_at,
            )
            for item in items
        ]

    def cancel_leave(self, current_user: User, leave_id: UUID) -> LeaveResponse:
        leave = self.repo.get_by_id(leave_id)
        if not leave:
            raise NotFoundException(
                code="LEAVE_NOT_FOUND",
                message="Leave record not found.",
            )

        if current_user.role != UserRole.ADMIN:
            faculty = self._get_faculty_for_user(current_user)
            if leave.faculty_id != faculty.id:
                raise ForbiddenException(
                    code="INSUFFICIENT_PERMISSIONS",
                    message="You can only cancel your own leave records.",
                )

        leave.status = LeaveStatus.CANCELLED
        updated = self.repo.update(leave)
        self.db.commit()
        self.db.refresh(updated)

        return LeaveResponse(
            id=updated.id,
            faculty_id=updated.faculty_id,
            start_date=updated.start_date.astimezone(self.tz).date(),
            end_date=updated.end_date.astimezone(self.tz).date(),
            leave_type=updated.leave_type,
            reason=updated.reason,
            status=updated.status,
            created_at=updated.created_at,
        )
