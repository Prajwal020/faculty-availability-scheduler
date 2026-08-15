from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.leave import LeaveRecord, LeaveStatus


class LeaveRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: UUID) -> Optional[LeaveRecord]:
        return self.db.query(LeaveRecord).filter(LeaveRecord.id == id).first()

    def list_by_faculty(
        self, faculty_id: UUID, status: Optional[LeaveStatus] = None
    ) -> List[LeaveRecord]:
        query = self.db.query(LeaveRecord).filter(LeaveRecord.faculty_id == faculty_id)
        if status:
            query = query.filter(LeaveRecord.status == status)
        return query.order_by(LeaveRecord.start_date.asc()).all()

    def get_active_leave_for_date_range(
        self, faculty_id: UUID, start_dt: datetime, end_dt: datetime
    ) -> List[LeaveRecord]:
        return (
            self.db.query(LeaveRecord)
            .filter(
                LeaveRecord.faculty_id == faculty_id,
                LeaveRecord.status == LeaveStatus.APPROVED,
                LeaveRecord.start_date < end_dt,
                LeaveRecord.end_date >= start_dt,
            )
            .all()
        )

    def check_leave_overlap(
        self,
        faculty_id: UUID,
        start_dt: datetime,
        end_dt: datetime,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        query = self.db.query(LeaveRecord).filter(
            LeaveRecord.faculty_id == faculty_id,
            LeaveRecord.status == LeaveStatus.APPROVED,
            LeaveRecord.start_date <= end_dt,
            LeaveRecord.end_date >= start_dt,
        )
        if exclude_id:
            query = query.filter(LeaveRecord.id != exclude_id)
        return query.first() is not None

    def create(self, leave: LeaveRecord) -> LeaveRecord:
        self.db.add(leave)
        self.db.flush()
        return leave

    def update(self, leave: LeaveRecord) -> LeaveRecord:
        self.db.add(leave)
        self.db.flush()
        return leave

    def delete(self, leave: LeaveRecord) -> None:
        self.db.delete(leave)
        self.db.flush()
