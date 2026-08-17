from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from app.core.config import settings
from app.core.time_utils import get_current_date
from app.models.user import User, UserRole, UserStatus
from app.models.faculty import Faculty, MeetingMode
from app.core.security import hash_password, create_access_token


def test_regular_availability_crud(client, faculty_auth_headers):
    # 1. Create Regular Availability (Monday: 09:00 - 12:00)
    res_create = client.post(
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
    assert res_create.status_code == 201
    data = res_create.json()
    reg_id = data["id"]
    assert data["day_of_week"] == 0
    assert data["start_time"] == "09:00:00"

    # 2. Reject Overlapping Window (Monday: 10:00 - 13:00)
    res_overlap = client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,
            "start_time": "10:00:00",
            "end_time": "13:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )
    assert res_overlap.status_code == 409
    assert res_overlap.json()["error"]["code"] == "REGULAR_AVAILABILITY_OVERLAP"

    # 3. Allow Adjacent Window (Monday: 12:00 - 14:00)
    res_adj = client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,
            "start_time": "12:00:00",
            "end_time": "14:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )
    assert res_adj.status_code == 201

    # 4. List Regular Availability
    res_list = client.get("/api/v1/availability/regular", headers=faculty_auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 2

    # 5. Update Regular Availability
    res_update = client.put(
        f"/api/v1/availability/regular/{reg_id}",
        json={"start_time": "08:30:00"},
        headers=faculty_auth_headers,
    )
    assert res_update.status_code == 200
    assert res_update.json()["start_time"] == "08:30:00"

    # 6. Delete Regular Availability
    res_del = client.delete(f"/api/v1/availability/regular/{reg_id}", headers=faculty_auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True


def test_temporary_availability_crud(client, faculty_auth_headers):
    target_date = "2026-08-20"

    # 1. Create Temporary Availability
    res_create = client.post(
        "/api/v1/availability/temporary",
        json={
            "date": target_date,
            "start_time": "11:15:00",
            "end_time": "12:00:00",
            "reason": "Cancelled lecture pop-up hours",
        },
        headers=faculty_auth_headers,
    )
    assert res_create.status_code == 201
    temp_id = res_create.json()["id"]

    # 2. Reject Overlapping Temporary Availability
    res_overlap = client.post(
        "/api/v1/availability/temporary",
        json={
            "date": target_date,
            "start_time": "11:30:00",
            "end_time": "12:30:00",
        },
        headers=faculty_auth_headers,
    )
    assert res_overlap.status_code == 409
    assert res_overlap.json()["error"]["code"] == "TEMPORARY_AVAILABILITY_OVERLAP"

    # 3. List
    res_list = client.get("/api/v1/availability/temporary", headers=faculty_auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 4. Delete
    res_del = client.delete(f"/api/v1/availability/temporary/{temp_id}", headers=faculty_auth_headers)
    assert res_del.status_code == 200


def test_temporary_availability_standalone_without_regular_hours(
    client, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id
    # Future Thursday (2026-08-20) with no regular schedule
    res_create = client.post(
        "/api/v1/availability/temporary",
        json={
            "date": "2026-08-20",
            "start_time": "14:00:00",
            "end_time": "14:30:00",
            "reason": "Extra office hour",
        },
        headers=faculty_auth_headers,
    )
    assert res_create.status_code == 201

    # Student query returns the standalone slot
    res_query = client.get(f"/api/v1/availability/{faculty_id}?date=2026-08-20&duration=30")
    assert res_query.status_code == 200
    data = res_query.json()
    assert len(data["available_windows"]) == 1
    assert data["available_windows"][0]["start_time"] == "14:00"
    assert data["available_windows"][0]["end_time"] == "14:30"
    assert len(data["slots"]) == 1
    assert data["slots"][0]["start_time"] == "14:00"
    assert data["slots"][0]["end_time"] == "14:30"


def test_blocked_slots_crud(client, faculty_auth_headers):
    # Create Block
    res_create = client.post(
        "/api/v1/availability/blocked",
        json={
            "start_datetime": "2026-08-20T10:00:00+05:30",
            "end_datetime": "2026-08-20T11:00:00+05:30",
            "reason": "Department meeting",
        },
        headers=faculty_auth_headers,
    )
    assert res_create.status_code == 201
    block_id = res_create.json()["id"]

    # Overlap rejection
    res_overlap = client.post(
        "/api/v1/availability/blocked",
        json={
            "start_datetime": "2026-08-20T10:30:00+05:30",
            "end_datetime": "2026-08-20T11:30:00+05:30",
            "reason": "Research call",
        },
        headers=faculty_auth_headers,
    )
    assert res_overlap.status_code == 409
    assert res_overlap.json()["error"]["code"] == "BLOCKED_SLOT_OVERLAP"

    # Delete
    res_del = client.delete(f"/api/v1/availability/blocked/{block_id}", headers=faculty_auth_headers)
    assert res_del.status_code == 200


def test_leave_management_crud(client, faculty_auth_headers):
    # 1. Create Full-Day Leave
    res_create = client.post(
        "/api/v1/leave",
        json={
            "start_date": "2026-08-24",
            "end_date": "2026-08-26",
            "leave_type": "FULL_DAY",
            "reason": "Attending IEEE Conference",
        },
        headers=faculty_auth_headers,
    )
    assert res_create.status_code == 201
    leave_id = res_create.json()["id"]

    # 2. Reject Overlapping Leave
    res_overlap = client.post(
        "/api/v1/leave",
        json={
            "start_date": "2026-08-25",
            "end_date": "2026-08-27",
            "leave_type": "FULL_DAY",
            "reason": "Personal Leave",
        },
        headers=faculty_auth_headers,
    )
    assert res_overlap.status_code == 409
    assert res_overlap.json()["error"]["code"] == "LEAVE_OVERLAP_EXISTS"

    # 3. List
    res_list = client.get("/api/v1/leave", headers=faculty_auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 4. Cancel Leave
    res_cancel = client.delete(f"/api/v1/leave/{leave_id}", headers=faculty_auth_headers)
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELLED"


def test_student_leave_privacy_and_dynamic_availability(
    client, faculty_auth_headers, faculty_user
):
    faculty_id = faculty_user.faculty_profile.id

    # Compute a deterministic future Monday relative to current time
    today = get_current_date()
    days_until_monday = (0 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    target_monday = today + timedelta(days=days_until_monday)
    target_date_str = target_monday.isoformat()

    # 1. Set Regular Availability on Monday (09:00 - 12:00)
    client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 0,  # Monday
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "slot_duration_minutes": 30,
            "is_active": True,
        },
        headers=faculty_auth_headers,
    )

    # 2. Query future Monday
    res_calc = client.get(f"/api/v1/availability/{faculty_id}?date={target_date_str}&duration=30")
    assert res_calc.status_code == 200
    data = res_calc.json()
    assert data["day_of_week"] == 0
    assert data["is_on_leave"] is False
    assert "leave_reason" not in data  # Privacy check: student response must not expose leave_reason
    assert len(data["slots"]) == 6

    # 3. Declare Private Full-Day Leave on that Monday
    client.post(
        "/api/v1/leave",
        json={
            "start_date": target_date_str,
            "end_date": target_date_str,
            "leave_type": "FULL_DAY",
            "reason": "CONFIDENTIAL: Urgent Medical Procedure",
        },
        headers=faculty_auth_headers,
    )

    # 4. Student queries the date -> is_on_leave=True, slots=0, NO leave_reason exposed!
    res_calc2 = client.get(f"/api/v1/availability/{faculty_id}?date={target_date_str}&duration=30")
    assert res_calc2.status_code == 200
    data2 = res_calc2.json()
    assert data2["is_on_leave"] is True
    assert "leave_reason" not in data2  # Privacy check: Private reason must NEVER leak!
    assert len(data2["slots"]) == 0
    assert data2["total_slots"] == 0


def test_past_date_query_returns_zero_slots(client, faculty_user):
    faculty_id = faculty_user.faculty_profile.id
    # Query a past date (2020-01-01)
    res = client.get(f"/api/v1/availability/{faculty_id}?date=2020-01-01&duration=30")
    assert res.status_code == 200
    data = res.json()
    assert data["total_slots"] == 0
    assert len(data["slots"]) == 0


def test_student_cannot_modify_availability(client, student_auth_headers):
    response = client.post(
        "/api/v1/availability/regular",
        json={
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "12:00:00",
        },
        headers=student_auth_headers,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_faculty_isolation_security(client, db_session, sample_department, faculty_auth_headers):
    # Create second faculty member (Faculty B)
    fac_b_user = User(
        email="faculty.b@test.edu",
        password_hash=hash_password("Pass123!"),
        full_name="Dr. Faculty B",
        role=UserRole.FACULTY,
        status=UserStatus.ACTIVE,
    )
    db_session.add(fac_b_user)
    db_session.flush()

    fac_b = Faculty(
        user_id=fac_b_user.id,
        department_id=sample_department.id,
        employee_id_number="FAC-B-001",
        title="Professor",
        office_location="Room 202",
        meeting_mode=MeetingMode.IN_PERSON,
    )
    db_session.add(fac_b)
    db_session.commit()

    token_b = create_access_token({"sub": str(fac_b_user.id), "role": fac_b_user.role.value, "email": fac_b_user.email})
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Faculty B creates regular availability
    res_b = client.post(
        "/api/v1/availability/regular",
        json={"day_of_week": 2, "start_time": "10:00:00", "end_time": "13:00:00"},
        headers=headers_b,
    )
    assert res_b.status_code == 201
    reg_id_b = res_b.json()["id"]

    # Faculty A attempts to delete Faculty B's availability
    res_hack = client.delete(
        f"/api/v1/availability/regular/{reg_id_b}",
        headers=faculty_auth_headers,
    )
    assert res_hack.status_code == 404
    assert res_hack.json()["error"]["code"] == "REGULAR_AVAILABILITY_NOT_FOUND"
