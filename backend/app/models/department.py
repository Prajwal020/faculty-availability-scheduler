import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import GUID


class Department(Base):
    __tablename__ = "departments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(150), unique=True, index=True, nullable=False)
    building = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    faculty_members = relationship("Faculty", back_populates="department")
