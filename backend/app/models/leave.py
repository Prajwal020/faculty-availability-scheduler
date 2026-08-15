import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID


class LeaveType(str, enum.Enum):
    FULL_DAY = "FULL_DAY"
    HALF_DAY_MORNING = "HALF_DAY_MORNING"
    HALF_DAY_AFTERNOON = "HALF_DAY_AFTERNOON"
    MULTI_DAY = "MULTI_DAY"


class LeaveStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"


class LeaveRecord(Base):
    """
    Leave record declared by a faculty member.
    """
    __tablename__ = "leave_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    faculty_id = Column(GUID(), ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    leave_type = Column(
        Enum(LeaveType, name="leave_type_enum", native_enum=False),
        nullable=False,
        default=LeaveType.FULL_DAY,
    )
    reason = Column(String(255), nullable=False)
    status = Column(
        Enum(LeaveStatus, name="leave_status_enum", native_enum=False),
        nullable=False,
        default=LeaveStatus.APPROVED,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    faculty = relationship("Faculty", back_populates="leave_records")
