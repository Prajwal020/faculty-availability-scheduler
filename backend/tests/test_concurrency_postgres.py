import os
import threading
from datetime import date, time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.user import User, UserRole, UserStatus
from app.models.department import Department
from app.models.faculty import Faculty, MeetingMode
from app.models.student import Student
from app.models.appointment import Appointment, AppointmentStatus
from app.models.availability import RegularAvailability
from app.core.security import hash_password
from app.schemas.appointment import AppointmentCreate
from app.services.appointment_service import AppointmentService
from app.core.exceptions import ConflictException

POSTGRES_TEST_URL = os.getenv(
    "TEST_POSTGRESQL_URL",
    os.getenv("DATABASE_URL") if os.getenv("DATABASE_URL", "").startswith("postgresql") else None,
)

# Check if PostgreSQL server is reachable
POSTGRES_AVAILABLE = False
if POSTGRES_TEST_URL:
    try:
        engine = create_engine(POSTGRES_TEST_URL, connect_args={"connect_timeout": 2})
        with engine.connect() as conn:
            POSTGRES_AVAILABLE = True
    except Exception:
        POSTGRES_AVAILABLE = False


@pytest.mark.skipif(
    not POSTGRES_AVAILABLE,
    reason="PostgreSQL server is not configured or running in environment (TEST_POSTGRESQL_URL required)",
)
def test_postgres_concurrent_booking_race_condition():
    """
    Dedicated PostgreSQL Integration Test:
    Executes true concurrent transactions against PostgreSQL.
    Verifies that FOR UPDATE row locking on Faculty record serializes transactions,
    guaranteeing exactly 1 successful booking and 1 409 Conflict.
    """
    engine = create_engine(POSTGRES_TEST_URL, pool_size=10)

    # This is a dedicated disposable PostgreSQL test database.
    # Reset the schema so every test run starts clean.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    target_date = date(2026, 10, 5)  # Monday

    # 1. Setup Department & Faculty
    dept = Department(code="CS-PG", name="Computer Science Postgres", building="PG Hall")
    db.add(dept)
    db.flush()

    fac_user = User(
        email="fac_pg@institution.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Dr. Postgres Faculty",
        role=UserRole.FACULTY,
        status=UserStatus.ACTIVE,
    )
    db.add(fac_user)
    db.flush()

    fac = Faculty(
        user_id=fac_user.id,
        department_id=dept.id,
        employee_id_number="FAC-PG-01",
        title="Professor",
        office_location="PG Hall 101",
        meeting_mode=MeetingMode.HYBRID,
    )
    db.add(fac)
    db.flush()

    # Regular availability on Monday (09:00 - 12:00)
    db.add(RegularAvailability(
        faculty_id=fac.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(12, 0),
        slot_duration_minutes=30,
        is_active=True,
    ))

    # 2. Setup Students
    u1 = User(
        email="s1_pg@institution.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Postgres Student 1",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    u2 = User(
        email="s2_pg@institution.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Postgres Student 2",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add_all([u1, u2])
    db.flush()

    s1 = Student(user_id=u1.id, student_id_number="STU-PG-01", major="CS")
    s2 = Student(user_id=u2.id, student_id_number="STU-PG-02", major="CS")
    db.add_all([s1, s2])
    db.commit()

    fac_id = fac.id
    u1_id = u1.id
    u2_id = u2.id
    db.close()

    # 3. Concurrent Booking with Barrier
    barrier = threading.Barrier(2)
    results = []
    errors = []

    def book_pg_slot(user_id: str, reason: str):
        thread_db = TestingSessionLocal()
        try:
            current_user = thread_db.query(User).filter(User.id == user_id).first()
            service = AppointmentService(thread_db)
            data = AppointmentCreate(
                faculty_id=fac_id,
                date=target_date,
                start_time=time(9, 0),
                end_time=time(9, 30),
                reason=reason,
            )
            barrier.wait(timeout=5.0)
            resp = service.book_appointment(current_user, data)
            results.append({"status": "SUCCESS", "resp": resp})
        except ConflictException as ce:
            errors.append({"status": "CONFLICT", "code": ce.code, "message": ce.message})
        except Exception as ex:
            errors.append({"status": "ERROR", "exception": str(ex)})
        finally:
            thread_db.close()

    t1 = threading.Thread(target=book_pg_slot, args=(u1_id, "Postgres Thread 1"))
    t2 = threading.Thread(target=book_pg_slot, args=(u2_id, "Postgres Thread 2"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # 4. Assert invariants
    assert len(results) == 1, f"Expected 1 success, got {len(results)}. Errors: {errors}"
    assert len(errors) == 1, f"Expected 1 conflict error, got {len(errors)}"
    assert errors[0]["code"] == "SLOT_UNAVAILABLE"

    # Verify PostgreSQL database contains exactly one active appointment
    verify_db = TestingSessionLocal()
    active_appts = verify_db.query(Appointment).filter(
        Appointment.faculty_id == fac_id,
        Appointment.date == target_date,
        Appointment.start_time == time(9, 0),
        Appointment.end_time == time(9, 30),
        Appointment.status.in_([AppointmentStatus.REQUESTED, AppointmentStatus.ACCEPTED]),
    ).all()
    assert len(active_appts) == 1
    verify_db.close()
