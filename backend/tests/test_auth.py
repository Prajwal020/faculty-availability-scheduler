from datetime import timedelta
from app.core.security import create_access_token
from app.models.user import UserStatus


def test_register_student_success(client):
    response = client.post(
        "/api/v1/auth/register/student",
        json={
            "email": "new.student@test.edu",
            "password": "Password123!",
            "full_name": "New Student",
            "student_id_number": "STU-NEW-001",
            "major": "Computer Science",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "new.student@test.edu"
    assert data["user"]["role"] == "STUDENT"
    assert data["user"]["student_profile"]["student_id_number"] == "STU-NEW-001"


def test_register_student_duplicate_email(client, student_user):
    response = client.post(
        "/api/v1/auth/register/student",
        json={
            "email": student_user.email,
            "password": "Password123!",
            "full_name": "Another Student",
            "student_id_number": "STU-DIFF-001",
            "major": "Data Science",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


def test_register_student_duplicate_id_number(client, student_user):
    response = client.post(
        "/api/v1/auth/register/student",
        json={
            "email": "unique.student@test.edu",
            "password": "Password123!",
            "full_name": "Unique Student",
            "student_id_number": student_user.student_profile.student_id_number,
            "major": "Data Science",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STUDENT_ID_EXISTS"


def test_register_faculty_success(client, sample_department):
    response = client.post(
        "/api/v1/auth/register/faculty",
        json={
            "email": "new.faculty@test.edu",
            "password": "Password123!",
            "full_name": "Dr. New Faculty",
            "employee_id_number": "FAC-NEW-001",
            "department_id": str(sample_department.id),
            "title": "Assistant Professor",
            "office_location": "Block C, 102",
            "bio": "Bio content",
            "meeting_mode": "IN_PERSON",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "FACULTY"
    assert data["user"]["faculty_profile"]["employee_id_number"] == "FAC-NEW-001"


def test_register_faculty_invalid_department(client):
    import uuid
    response = client.post(
        "/api/v1/auth/register/faculty",
        json={
            "email": "faculty.invalid@test.edu",
            "password": "Password123!",
            "full_name": "Dr. Invalid",
            "employee_id_number": "FAC-INV-001",
            "department_id": str(uuid.uuid4()),
            "title": "Professor",
            "office_location": "Block A",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"


def test_login_success(client, student_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": student_user.email,
            "password": "StudentPass123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == student_user.email


def test_login_invalid_password(client, student_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": student_user.email,
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_inactive_user(client, student_user, db_session):
    student_user.status = UserStatus.SUSPENDED
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": student_user.email,
            "password": "StudentPass123!",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "ACCOUNT_INACTIVE"


def test_get_me_authenticated(client, student_auth_headers, student_user):
    response = client.get("/api/v1/auth/me", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == student_user.email
    assert data["role"] == "STUDENT"
    assert data["student_profile"]["student_id_number"] == "STU-TEST-001"


def test_get_me_unauthenticated(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NOT_AUTHENTICATED"


def test_get_me_expired_token(client, student_user):
    expired_token = create_access_token(
        data={"sub": str(student_user.id), "role": student_user.role.value, "email": student_user.email},
        expires_delta=timedelta(minutes=-10),
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_TOKEN"
