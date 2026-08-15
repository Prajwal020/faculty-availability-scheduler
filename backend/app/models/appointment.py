import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Date, Time, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID


class AppointmentStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    RESCHEDULE_PROPOSED = "RESCHEDULE_PROPOSED"


class Appointment(Base):
    """
    Appointment entity linking a Student and Faculty member for a specific time interval.
    """
    __tablename__ = "appointments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(GUID(), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    faculty_id = Column(GUID(), ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=30)
    status = Column(
        Enum(AppointmentStatus, name="appointment_status_enum", native_enum=False),
        nullable=False,
        default=AppointmentStatus.REQUESTED,
        index=True,
    )
    reason = Column(String(255), nullable=False)
    faculty_notes = Column(String(255), nullable=True)
    cancellation_reason = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    student = relationship("Student", back_populates="appointments")
    faculty = relationship("Faculty", back_populates="appointments")

    # Composite indexes for fast overlap and lifecycle queries
    __table_args__ = (
        Index("ix_appointments_faculty_date_status", "faculty_id", "date", "status"),
        Index("ix_appointments_student_date_status", "student_id", "date", "status"),
    )
