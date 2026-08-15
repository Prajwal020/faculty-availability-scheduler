import uuid
from datetime import date, time
import pytest

from app.models.user import User, UserRole, UserStatus
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.appointment import Appointment, AppointmentStatus
from app.models.availability import RegularAvailability
from app.models.leave import LeaveRecord, LeaveType, LeaveStatus
from app.core.security import hash_password, create_access_token
from app.schemas.appointment import AppointmentCreate
from app.services.appointment_service import AppointmentService
from app.core.exceptions import ConflictException


def test_double_booking_conflict_prevention(client, student_auth_headers, faculty_auth_headers, faculty_user, db_session):
    """
    Verifies that when a slot is booked by Student 1 (REQUESTED or ACCEPTED),
    any subsequent booking attempt by Student 2 for the exact same or overlapping slot
    is rejected with 409 Conflict (SLOT_UNAVAILABLE).
    """
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-09-07"  # Monday

    # 1. Setup Faculty regular availability for Monday 09:00-12:00
    client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )

    # 2. Student 1 books 09:00 - 09:30 -> SUCCESS
    res_s1 = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "09:00:00",
            "end_time": "09:30:00",
            "reason": "First student booking",
        },
        headers=student_auth_headers,
    )
    assert res_s1.status_code == 201

    # 3. Create Student 2
    uid_suffix = uuid.uuid4().hex[:6]
    s2_user = User(
        email=f"conc_s2_{uid_suffix}@test.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Student Two",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(s2_user)
    db_session.flush()
    s2 = Student(user_id=s2_user.id, student_id_number=f"CONC-{uid_suffix}-2", major="CS")
    db_session.add(s2)
    db_session.commit()

    token_s2 = create_access_token({"sub": str(s2_user.id), "role": s2_user.role.value, "email": s2_user.email})
    headers_s2 = {"Authorization": f"Bearer {token_s2}"}

    # 4. Student 2 tries to book 09:00 - 09:30 -> 409 Conflict
    res_s2 = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "09:00:00",
            "end_time": "09:30:00",
            "reason": "Second student booking attempt",
        },
        headers=headers_s2,
    )
    assert res_s2.status_code == 409
    assert res_s2.json()["error"]["code"] == "SLOT_UNAVAILABLE"

    # 5. Verify database contains exactly 1 active appointment for this slot
    active_appts = db_session.query(Appointment).filter(
        Appointment.faculty_id == faculty_id,
        Appointment.date == date(2026, 9, 7),
        Appointment.start_time == time(9, 0),
        Appointment.end_time == time(9, 30),
        Appointment.status.in_([AppointmentStatus.REQUESTED, AppointmentStatus.ACCEPTED]),
    ).all()
    assert len(active_appts) == 1


def test_stale_availability_rejected(client, student_auth_headers, faculty_auth_headers, faculty_user, db_session):
    """
    Student A and Student B both see slot 10:00-10:30 available.
    Student B books the slot.
    Student A then submits the stale slot request -> 409 Conflict (SLOT_UNAVAILABLE).
    """
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-09-14"  # Monday

    # Setup availability
    client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )

    # Student 1 books 10:00 - 10:30
    res_b1 = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "First booking",
        },
        headers=student_auth_headers,
    )
    assert res_b1.status_code == 201

    # Student 2 tries to book the same slot (stale frontend data)
    uid_suffix = uuid.uuid4().hex[:6]
    s2_user = User(
        email=f"stale_s2_{uid_suffix}@test.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Stale Student",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(s2_user)
    db_session.flush()
    s2 = Student(user_id=s2_user.id, student_id_number=f"STU-STALE-{uid_suffix}", major="CS")
    db_session.add(s2)
    db_session.commit()

    token_s2 = create_access_token({"sub": str(s2_user.id), "role": s2_user.role.value, "email": s2_user.email})
    headers_s2 = {"Authorization": f"Bearer {token_s2}"}

    res_stale = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "Stale booking attempt",
        },
        headers=headers_s2,
    )
    assert res_stale.status_code == 409
    assert res_stale.json()["error"]["code"] == "SLOT_UNAVAILABLE"


def test_transaction_rollback_preserves_session(client, student_auth_headers, faculty_auth_headers, faculty_user):
    """
    Verify that when a booking fails (e.g. invalid duration or conflict),
    the session is cleanly rolled back and subsequent valid bookings succeed.
    """
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-09-14"

    # Setup availability
    client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,
            "start_time": "10:00:00",
            "end_time": "12:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )

    # 1. Attempt invalid booking (end before start) -> 422 Validation Error
    res_bad = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "10:30:00",
            "end_time": "10:00:00",
            "reason": "Bad timing",
        },
        headers=student_auth_headers,
    )
    assert res_bad.status_code == 422
    assert res_bad.json()["error"]["code"] == "VALIDATION_ERROR"

    # 2. Subsequent valid booking for 10:30 - 11:00 succeeds cleanly
    res_valid = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "10:30:00",
            "end_time": "11:00:00",
            "reason": "Valid booking after rollback",
        },
        headers=student_auth_headers,
    )
    assert res_valid.status_code == 201
    assert res_valid.json()["status"] == "REQUESTED"


def test_leave_creation_preserves_existing_appointments(client, db_session, student_auth_headers, faculty_auth_headers, faculty_user):
    """
    Verify Section 18: Leave declaration over an existing appointment preserves appointment history and does not corrupt or delete it.
    """
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-09-21"  # Monday

    # Setup regular availability
    client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )

    # Book an appointment on 2026-09-21 09:00-09:30
    res_book = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "09:00:00",
            "end_time": "09:30:00",
            "reason": "Prior appointment",
        },
        headers=student_auth_headers,
    )
    assert res_book.status_code == 201
    appt_id = res_book.json()["id"]

    # Faculty declares leave on 2026-09-21
    res_leave = client.post(
        "/api/v1/leave",
        json={
            "start_date": target_date,
            "end_date": target_date,
            "leave_type": "FULL_DAY",
            "reason": "Family emergency",
        },
        headers=faculty_auth_headers,
    )
    assert res_leave.status_code == 201

    # Appointment still exists in DB and is NOT deleted
    res_appt = client.get(f"/api/v1/appointments/{appt_id}", headers=student_auth_headers)
    assert res_appt.status_code == 200
    assert res_appt.json()["id"] == appt_id
    assert res_appt.json()["status"] == "REQUESTED"

    # Future slot generation on this date returns 0 slots (leave overrides availability)
    res_avail = client.get(f"/api/v1/availability/{faculty_id}?date={target_date}&duration=30")
    assert res_avail.status_code == 200
    assert res_avail.json()["is_on_leave"] is True
    assert res_avail.json()["total_slots"] == 0
