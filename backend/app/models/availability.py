import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID


class RegularAvailability(Base):
    """
    Recurring weekly availability window defined by a faculty member.
    day_of_week: 0 = Monday, 1 = Tuesday, ..., 6 = Sunday.
    """
    __tablename__ = "regular_availability"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    faculty_id = Column(GUID(), ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration_minutes = Column(Integer, nullable=False, default=30)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    faculty = relationship("Faculty", back_populates="regular_availabilities")


class TemporaryAvailability(Base):
    """
    One-time temporary availability published by a faculty member for a specific calendar date.
    """
    __tablename__ = "temporary_availability"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    faculty_id = Column(GUID(), ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    faculty = relationship("Faculty", back_populates="temporary_availabilities")


class BlockedSlot(Base):
    """
    One-time temporary blocked period / unavailability window.
    """
    __tablename__ = "blocked_slots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    faculty_id = Column(GUID(), ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False, index=True)
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    faculty = relationship("Faculty", back_populates="blocked_slots")
