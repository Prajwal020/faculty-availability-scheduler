from datetime import date, time, datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.availability import RegularAvailability, TemporaryAvailability, BlockedSlot


class AvailabilityRepository:
    def __init__(self, db: Session):
        self.db = db

    # 1. Regular Availability
    def get_regular_by_id(self, id: UUID) -> Optional[RegularAvailability]:
        return self.db.query(RegularAvailability).filter(RegularAvailability.id == id).first()

    def list_regular_by_faculty(
        self, faculty_id: UUID, is_active: Optional[bool] = None
    ) -> List[RegularAvailability]:
        query = self.db.query(RegularAvailability).filter(RegularAvailability.faculty_id == faculty_id)
        if is_active is not None:
            query = query.filter(RegularAvailability.is_active == is_active)
        return query.order_by(RegularAvailability.day_of_week.asc(), RegularAvailability.start_time.asc()).all()

    def get_regular_by_faculty_and_day(
        self, faculty_id: UUID, day_of_week: int, is_active: bool = True
    ) -> List[RegularAvailability]:
        return (
            self.db.query(RegularAvailability)
            .filter(
                RegularAvailability.faculty_id == faculty_id,
                RegularAvailability.day_of_week == day_of_week,
                RegularAvailability.is_active == is_active,
            )
            .order_by(RegularAvailability.start_time.asc())
            .all()
        )

    def check_regular_overlap(
        self,
        faculty_id: UUID,
        day_of_week: int,
        start_time: time,
        end_time: time,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        """
        Check if proposed recurring window overlaps with any existing active window on that day.
        Overlap: max(start) < min(end) <=> existing.start < new.end AND existing.end > new.start.
        """
        query = self.db.query(RegularAvailability).filter(
            RegularAvailability.faculty_id == faculty_id,
            RegularAvailability.day_of_week == day_of_week,
            RegularAvailability.is_active == True,
            RegularAvailability.start_time < end_time,
            RegularAvailability.end_time > start_time,
        )
        if exclude_id:
            query = query.filter(RegularAvailability.id != exclude_id)
        return query.first() is not None

    def create_regular(self, reg: RegularAvailability) -> RegularAvailability:
        self.db.add(reg)
        self.db.flush()
        return reg

    def update_regular(self, reg: RegularAvailability) -> RegularAvailability:
        self.db.add(reg)
        self.db.flush()
        return reg

    def delete_regular(self, reg: RegularAvailability) -> None:
        self.db.delete(reg)
        self.db.flush()

    # 2. Temporary Availability
    def get_temporary_by_id(self, id: UUID) -> Optional[TemporaryAvailability]:
        return self.db.query(TemporaryAvailability).filter(TemporaryAvailability.id == id).first()

    def list_temporary_by_faculty(
        self, faculty_id: UUID, start_date: Optional[datetime] = None
    ) -> List[TemporaryAvailability]:
        query = self.db.query(TemporaryAvailability).filter(TemporaryAvailability.faculty_id == faculty_id)
        if start_date:
            query = query.filter(TemporaryAvailability.date >= start_date)
        return query.order_by(TemporaryAvailability.date.asc(), TemporaryAvailability.start_time.asc()).all()

    def get_temporary_by_faculty_and_date(
        self, faculty_id: UUID, target_date_start: datetime, target_date_end: datetime
    ) -> List[TemporaryAvailability]:
        return (
            self.db.query(TemporaryAvailability)
            .filter(
                TemporaryAvailability.faculty_id == faculty_id,
                TemporaryAvailability.date >= target_date_start,
                TemporaryAvailability.date < target_date_end,
            )
            .order_by(TemporaryAvailability.start_time.asc())
            .all()
        )

    def check_temporary_overlap(
        self,
        faculty_id: UUID,
        target_date_start: datetime,
        target_date_end: datetime,
        start_time: time,
        end_time: time,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        query = self.db.query(TemporaryAvailability).filter(
            TemporaryAvailability.faculty_id == faculty_id,
            TemporaryAvailability.date >= target_date_start,
            TemporaryAvailability.date < target_date_end,
            TemporaryAvailability.start_time < end_time,
            TemporaryAvailability.end_time > start_time,
        )
        if exclude_id:
            query = query.filter(TemporaryAvailability.id != exclude_id)
        return query.first() is not None

    def create_temporary(self, temp: TemporaryAvailability) -> TemporaryAvailability:
        self.db.add(temp)
        self.db.flush()
        return temp

    def delete_temporary(self, temp: TemporaryAvailability) -> None:
        self.db.delete(temp)
        self.db.flush()

    # 3. Blocked Slots
    def get_blocked_by_id(self, id: UUID) -> Optional[BlockedSlot]:
        return self.db.query(BlockedSlot).filter(BlockedSlot.id == id).first()

    def list_blocked_by_faculty(
        self, faculty_id: UUID, start_datetime: Optional[datetime] = None
    ) -> List[BlockedSlot]:
        query = self.db.query(BlockedSlot).filter(BlockedSlot.faculty_id == faculty_id)
        if start_datetime:
            query = query.filter(BlockedSlot.end_datetime >= start_datetime)
        return query.order_by(BlockedSlot.start_datetime.asc()).all()

    def get_blocked_for_date_range(
        self, faculty_id: UUID, start_dt: datetime, end_dt: datetime
    ) -> List[BlockedSlot]:
        return (
            self.db.query(BlockedSlot)
            .filter(
                BlockedSlot.faculty_id == faculty_id,
                BlockedSlot.start_datetime < end_dt,
                BlockedSlot.end_datetime > start_dt,
            )
            .order_by(BlockedSlot.start_datetime.asc())
            .all()
        )

    def check_blocked_overlap(
        self,
        faculty_id: UUID,
        start_dt: datetime,
        end_dt: datetime,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        query = self.db.query(BlockedSlot).filter(
            BlockedSlot.faculty_id == faculty_id,
            BlockedSlot.start_datetime < end_dt,
            BlockedSlot.end_datetime > start_dt,
        )
        if exclude_id:
            query = query.filter(BlockedSlot.id != exclude_id)
        return query.first() is not None

    def create_blocked(self, block: BlockedSlot) -> BlockedSlot:
        self.db.add(block)
        self.db.flush()
        return block

    def delete_blocked(self, block: BlockedSlot) -> None:
        self.db.delete(block)
        self.db.flush()
