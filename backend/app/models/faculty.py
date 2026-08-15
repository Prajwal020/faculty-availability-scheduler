import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID


class MeetingMode(str, enum.Enum):
    IN_PERSON = "IN_PERSON"
    VIRTUAL = "VIRTUAL"
    HYBRID = "HYBRID"


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    department_id = Column(GUID(), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    employee_id_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(100), nullable=False)
    office_location = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    meeting_mode = Column(
        Enum(MeetingMode, name="meeting_mode_enum", native_enum=False),
        nullable=False,
        default=MeetingMode.IN_PERSON,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department", back_populates="faculty_members")
    regular_availabilities = relationship("RegularAvailability", back_populates="faculty", cascade="all, delete-orphan")
    temporary_availabilities = relationship("TemporaryAvailability", back_populates="faculty", cascade="all, delete-orphan")
    blocked_slots = relationship("BlockedSlot", back_populates="faculty", cascade="all, delete-orphan")
    leave_records = relationship("LeaveRecord", back_populates="faculty", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="faculty", cascade="all, delete-orphan")
