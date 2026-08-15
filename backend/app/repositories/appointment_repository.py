from datetime import date, time, datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_
from app.models.appointment import Appointment, AppointmentStatus
from app.models.student import Student
from app.models.faculty import Faculty


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        return appointment

    def get_by_id(self, id: UUID, for_update: bool = False) -> Optional[Appointment]:
        query = (
            self.db.query(Appointment)
            .options(
                joinedload(Appointment.student).joinedload(Student.user),
                joinedload(Appointment.faculty).joinedload(Faculty.user),
                joinedload(Appointment.faculty).joinedload(Faculty.department),
            )
            .filter(Appointment.id == id)
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def list_appointments(
        self,
        student_id: Optional[UUID] = None,
        faculty_id: Optional[UUID] = None,
        date_filter: Optional[date] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status: Optional[AppointmentStatus] = None,
    ) -> List[Appointment]:
        query = (
            self.db.query(Appointment)
            .options(
                joinedload(Appointment.student).joinedload(Student.user),
                joinedload(Appointment.faculty).joinedload(Faculty.user),
                joinedload(Appointment.faculty).joinedload(Faculty.department),
            )
        )

        if student_id:
            query = query.filter(Appointment.student_id == student_id)
        if faculty_id:
            query = query.filter(Appointment.faculty_id == faculty_id)
        if date_filter:
            query = query.filter(Appointment.date == date_filter)
        if from_date:
            query = query.filter(Appointment.date >= from_date)
        if to_date:
            query = query.filter(Appointment.date <= to_date)
        if status:
            query = query.filter(Appointment.status == status)

        return query.order_by(Appointment.date.asc(), Appointment.start_time.asc()).all()

    def get_active_appointments_for_faculty_on_date(
        self, faculty_id: UUID, target_date: date
    ) -> List[Appointment]:
        """
        Active appointments (REQUESTED, ACCEPTED, RESCHEDULE_PROPOSED) act as reservations.
        """
        return (
            self.db.query(Appointment)
            .filter(
                Appointment.faculty_id == faculty_id,
                Appointment.date == target_date,
                Appointment.status.in_([
                    AppointmentStatus.REQUESTED,
                    AppointmentStatus.ACCEPTED,
                    AppointmentStatus.RESCHEDULE_PROPOSED,
                ]),
            )
            .order_by(Appointment.start_time.asc())
            .all()
        )

    def check_conflicting_appointment(
        self,
        faculty_id: UUID,
        target_date: date,
        start_time: time,
        end_time: time,
        exclude_id: Optional[UUID] = None,
        for_update: bool = False,
    ) -> Optional[Appointment]:
        """
        Check for any active appointment conflicting with proposed window [start_time, end_time).
        Overlap condition: start_time < existing.end_time AND end_time > existing.start_time.
        """
        query = self.db.query(Appointment).filter(
            Appointment.faculty_id == faculty_id,
            Appointment.date == target_date,
            Appointment.status.in_([
                AppointmentStatus.REQUESTED,
                AppointmentStatus.ACCEPTED,
                AppointmentStatus.RESCHEDULE_PROPOSED,
            ]),
            Appointment.start_time < end_time,
            Appointment.end_time > start_time,
        )
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)
        if for_update:
            query = query.with_for_update()
        return query.first()

    def update(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.flush()
        return appointment
