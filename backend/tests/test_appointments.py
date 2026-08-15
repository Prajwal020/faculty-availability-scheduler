from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
import pytest

from app.models.user import User, UserRole, UserStatus
from app.models.faculty import Faculty, MeetingMode
from app.models.student import Student
from app.models.appointment import Appointment, AppointmentStatus
from app.core.security import hash_password, create_access_token


def test_student_book_appointment_success(
    client, student_auth_headers, faculty_auth_headers, faculty_user, student_user
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-24"  # Monday

    # 1. Setup Faculty regular availability on Monday (09:00 - 12:00)
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

    # 2. Student checks availability before booking -> 6 slots
    res_avail_before = client.get(f"/api/v1/availability/{faculty_id}?date={target_date}&duration=30")
    assert res_avail_before.status_code == 200
    assert len(res_avail_before.json()["slots"]) == 6

    # 3. Student books 09:00 - 09:30
    res_book = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "09:00:00",
            "end_time": "09:30:00",
            "reason": "Discussing thesis topic",
        },
        headers=student_auth_headers,
    )
    assert res_book.status_code == 201
    appt_data = res_book.json()
    assert appt_data["status"] == "REQUESTED"
    assert appt_data["start_time"] == "09:00:00"
    assert appt_data["end_time"] == "09:30:00"
    assert appt_data["reason"] == "Discussing thesis topic"
    assert appt_data["student"]["full_name"] == student_user.full_name
    assert appt_data["faculty"]["full_name"] == faculty_user.full_name

    # 4. Availability Engine Integration: 09:00-09:30 is now reserved -> 5 slots left
    res_avail_after = client.get(f"/api/v1/availability/{faculty_id}?date={target_date}&duration=30")
    assert res_avail_after.status_code == 200
    slots_after = res_avail_after.json()["slots"]
    assert len(slots_after) == 5
    assert not any(s["start_time"] == "09:00" for s in slots_after)


def test_booking_validation_failures(
    client, student_auth_headers, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-24"

    # Setup availability
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

    # 1. Outside faculty hours (03:00 - 03:30)
    res_outside = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "03:00:00",
            "end_time": "03:30:00",
            "reason": "Late night request",
        },
        headers=student_auth_headers,
    )
    assert res_outside.status_code == 409
    assert res_outside.json()["error"]["code"] == "SLOT_UNAVAILABLE"

    # 2. Unaligned slot (09:15 - 09:45)
    res_unaligned = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "09:15:00",
            "end_time": "09:45:00",
            "reason": "Unaligned request",
        },
        headers=student_auth_headers,
    )
    assert res_unaligned.status_code == 409
    assert res_unaligned.json()["error"]["code"] == "SLOT_UNAVAILABLE"

    # 3. Past appointment date (2020-01-01)
    res_past = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": "2020-01-01",
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "Past date request",
        },
        headers=student_auth_headers,
    )
    assert res_past.status_code == 400
    assert res_past.json()["error"]["code"] == "PAST_APPOINTMENT"


def test_double_booking_prevention(
    client, db_session, student_auth_headers, faculty_auth_headers, faculty_user, sample_department
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-31"  # Monday

    # Setup availability
    client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )

    # Student 1 books 09:30 - 10:00 -> SUCCESS
    res_s1 = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "09:30:00",
            "end_time": "10:00:00",
            "reason": "Student 1 meeting",
        },
        headers=student_auth_headers,
    )
    assert res_s1.status_code == 201

    # Create Student 2
    s2_user = User(
        email="student2@test.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Student Two",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(s2_user)
    db_session.flush()
    s2 = Student(user_id=s2_user.id, student_id_number="STU-002", major="CS")
    db_session.add(s2)
    db_session.commit()

    token_s2 = create_access_token({"sub": str(s2_user.id), "role": s2_user.role.value, "email": s2_user.email})
    headers_s2 = {"Authorization": f"Bearer {token_s2}"}

    # Student 2 tries to book the SAME slot (09:30 - 10:00) -> CONFLICT
    res_s2 = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "09:30:00",
            "end_time": "10:00:00",
            "reason": "Student 2 meeting",
        },
        headers=headers_s2,
    )
    assert res_s2.status_code == 409
    assert res_s2.json()["error"]["code"] == "SLOT_UNAVAILABLE"


def test_appointment_lifecycle_accept_reject_cancel(
    client, student_auth_headers, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-31"

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

    # 1. Book appointment 10:00 - 10:30
    res_book = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "Project review",
        },
        headers=student_auth_headers,
    )
    assert res_book.status_code == 201
    appt_id = res_book.json()["id"]

    # 2. Faculty accepts appointment
    res_accept = client.put(
        f"/api/v1/appointments/{appt_id}/accept",
        json={"faculty_notes": "Please bring lab notebook."},
        headers=faculty_auth_headers,
    )
    assert res_accept.status_code == 200
    assert res_accept.json()["status"] == "ACCEPTED"
    assert res_accept.json()["faculty_notes"] == "Please bring lab notebook."

    # 3. Student cancels accepted appointment -> slot released
    res_cancel = client.put(
        f"/api/v1/appointments/{appt_id}/cancel",
        json={"reason": "Schedule conflict with exam"},
        headers=student_auth_headers,
    )
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"
    assert res_cancel.json()["cancellation_reason"] == "Schedule conflict with exam"

    # 4. Verify slot 10:00 - 10:30 is once again bookable!
    res_avail = client.get(f"/api/v1/availability/{faculty_id}?date={target_date}&duration=30")
    assert res_avail.status_code == 200
    slots = res_avail.json()["slots"]
    assert any(s["start_time"] == "10:00" and s["end_time"] == "10:30" for s in slots)


def test_faculty_rejection_releases_slot(
    client, student_auth_headers, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-31"

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

    # 1. Book appointment 11:00 - 11:30
    res_book = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "11:00:00",
            "end_time": "11:30:00",
            "reason": "Consultation",
        },
        headers=student_auth_headers,
    )
    assert res_book.status_code == 201
    appt_id = res_book.json()["id"]

    # 2. Faculty rejects request
    res_reject = client.put(
        f"/api/v1/appointments/{appt_id}/reject",
        json={"reason": "Attending urgent conference call."},
        headers=faculty_auth_headers,
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["status"] == "REJECTED"
    assert res_reject.json()["cancellation_reason"] == "Attending urgent conference call."

    # 3. Slot 11:00 - 11:30 is released and available again
    res_avail = client.get(f"/api/v1/availability/{faculty_id}?date={target_date}&duration=30")
    assert res_avail.status_code == 200
    slots = res_avail.json()["slots"]
    assert any(s["start_time"] == "11:00" and s["end_time"] == "11:30" for s in slots)


def test_invalid_state_transitions_rejected(
    client, student_auth_headers, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-31"

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

    # Book and reject
    res_book = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "10:30:00",
            "end_time": "11:00:00",
            "reason": "Consultation",
        },
        headers=student_auth_headers,
    )
    assert res_book.status_code == 201
    appt_id = res_book.json()["id"]
    client.put(f"/api/v1/appointments/{appt_id}/reject", headers=faculty_auth_headers)

    # 1. Attempt to accept a REJECTED appointment -> 409 Conflict
    res_invalid_accept = client.put(f"/api/v1/appointments/{appt_id}/accept", headers=faculty_auth_headers)
    assert res_invalid_accept.status_code == 409
    assert res_invalid_accept.json()["error"]["code"] == "INVALID_APPOINTMENT_STATE"

    # 2. Attempt to cancel a REJECTED appointment -> 409 Conflict
    res_invalid_cancel = client.put(f"/api/v1/appointments/{appt_id}/cancel", headers=student_auth_headers)
    assert res_invalid_cancel.status_code == 409
    assert res_invalid_cancel.json()["error"]["code"] == "INVALID_APPOINTMENT_STATE"

    # 3. Attempt to complete a REJECTED appointment -> 409 Conflict
    res_invalid_complete = client.put(f"/api/v1/appointments/{appt_id}/complete", headers=faculty_auth_headers)
    assert res_invalid_complete.status_code == 409
    assert res_invalid_complete.json()["error"]["code"] == "INVALID_APPOINTMENT_STATE"


def test_completion_validation_and_terminal_rules(
    client, student_auth_headers, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-31"

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

    # Book and accept
    res_book = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "10:00:00",
            "end_time": "10:30:00",
            "reason": "Research review",
        },
        headers=student_auth_headers,
    )
    appt_id = res_book.json()["id"]
    client.put(f"/api/v1/appointments/{appt_id}/accept", headers=faculty_auth_headers)

    # Attempt to complete a future appointment before it finishes -> 400 Bad Request
    res_early = client.put(f"/api/v1/appointments/{appt_id}/complete", headers=faculty_auth_headers)
    assert res_early.status_code == 400
    assert res_early.json()["error"]["code"] == "APPOINTMENT_NOT_YET_FINISHED"


def test_security_and_idor_isolation(
    client, db_session, sample_department, student_auth_headers, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id
    target_date = "2026-08-31"

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

    # Book an appointment for Student 1
    res_book = client.post(
        "/api/v1/appointments",
        json={
            "faculty_id": str(faculty_id),
            "date": target_date,
            "start_time": "11:30:00",
            "end_time": "12:00:00",
            "reason": "Thesis",
        },
        headers=student_auth_headers,
    )
    assert res_book.status_code == 201
    appt_id = res_book.json()["id"]

    # Create Student 2
    s2_user = User(
        email="s2_idor@test.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Student 2 IDOR",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(s2_user)
    db_session.flush()
    s2 = Student(user_id=s2_user.id, student_id_number="STU-IDOR", major="CS")
    db_session.add(s2)
    db_session.commit()

    token_s2 = create_access_token({"sub": str(s2_user.id), "role": s2_user.role.value, "email": s2_user.email})
    headers_s2 = {"Authorization": f"Bearer {token_s2}"}

    # Student 2 attempts to view Student 1's appointment -> 403 Forbidden
    res_idor_view = client.get(f"/api/v1/appointments/{appt_id}", headers=headers_s2)
    assert res_idor_view.status_code == 403
    assert res_idor_view.json()["error"]["code"] == "FORBIDDEN_RESOURCE"

    # Student 2 attempts to cancel Student 1's appointment -> 403 Forbidden
    res_idor_cancel = client.put(f"/api/v1/appointments/{appt_id}/cancel", headers=headers_s2)
    assert res_idor_cancel.status_code == 403
    assert res_idor_cancel.json()["error"]["code"] == "UNAUTHORIZED_APPOINTMENT_ACTION"

    # Student 1 attempts to accept an appointment -> 403 Forbidden (student cannot accept)
    res_student_accept = client.put(f"/api/v1/appointments/{appt_id}/accept", headers=student_auth_headers)
    assert res_student_accept.status_code == 403


def test_list_my_appointments(client, student_auth_headers, faculty_auth_headers):
    # Student lists own appointments
    res_student_list = client.get("/api/v1/appointments/me", headers=student_auth_headers)
    assert res_student_list.status_code == 200
    assert isinstance(res_student_list.json(), list)

    # Faculty lists own appointments
    res_faculty_list = client.get("/api/v1/appointments/me", headers=faculty_auth_headers)
    assert res_faculty_list.status_code == 200
    assert isinstance(res_faculty_list.json(), list)
