from app.models.user import UserStatus


def test_student_get_and_update_profile(client, student_auth_headers):
    # Get profile
    res_get = client.get("/api/v1/users/students/me", headers=student_auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["student_id_number"] == "STU-TEST-001"

    # Update profile
    res_put = client.put(
        "/api/v1/users/students/me",
        json={"major": "Software Engineering"},
        headers=student_auth_headers,
    )
    assert res_put.status_code == 200
    assert res_put.json()["major"] == "Software Engineering"


def test_faculty_get_and_update_profile(client, faculty_auth_headers):
    # Get profile
    res_get = client.get("/api/v1/users/faculty/me", headers=faculty_auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["employee_id_number"] == "FAC-TEST-001"

    # Update profile
    res_put = client.put(
        "/api/v1/users/faculty/me",
        json={
            "title": "Full Professor",
            "office_location": "Science Block 405",
            "bio": "Updated Bio content",
            "meeting_mode": "HYBRID",
        },
        headers=faculty_auth_headers,
    )
    assert res_put.status_code == 200
    data = res_put.json()
    assert data["title"] == "Full Professor"
    assert data["office_location"] == "Science Block 405"
    assert data["meeting_mode"] == "HYBRID"


def test_list_faculty_public(client, faculty_user, sample_department):
    response = client.get("/api/v1/users/faculty")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["email"] == faculty_user.email
    assert data[0]["department_name"] == sample_department.name

    # Verify foreign key invariants
    assert str(faculty_user.faculty_profile.user_id) == str(faculty_user.id)
    assert str(faculty_user.faculty_profile.department_id) == str(sample_department.id)

    # Filter by name
    res_filtered = client.get("/api/v1/users/faculty?name=Alice")
    assert res_filtered.status_code == 200
    assert len(res_filtered.json()) == 1

    # Filter by non-matching name
    res_empty = client.get("/api/v1/users/faculty?name=NonExistentName")
    assert res_empty.status_code == 200
    assert len(res_empty.json()) == 0


def test_get_faculty_public_profile(client, faculty_user):
    faculty_id = faculty_user.faculty_profile.id
    response = client.get(f"/api/v1/users/faculty/{faculty_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == faculty_user.full_name
    assert data["title"] == faculty_user.faculty_profile.title


def test_faculty_management_retrieval_and_relationships(client, faculty_user, sample_department):
    """
    Regression test ensuring User -> Faculty -> Department relationship
    and availability through the /api/v1/users/faculty endpoint.
    """
    response = client.get("/api/v1/users/faculty")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

    faculty_item = next((item for item in data if item["email"] == faculty_user.email), None)
    assert faculty_item is not None
    assert faculty_item["full_name"] == faculty_user.full_name
    assert faculty_item["user_id"] == str(faculty_user.id)
    assert faculty_item["department_id"] == str(sample_department.id)
    assert faculty_item["department_name"] == sample_department.name
    assert faculty_item["department_code"] == sample_department.code
    assert faculty_item["title"] == faculty_user.faculty_profile.title
    assert faculty_item["office_location"] == faculty_user.faculty_profile.office_location


def test_admin_create_user(client, admin_auth_headers):
    response = client.post(
        "/api/v1/admin/users/create",
        json={
            "email": "another.admin@test.edu",
            "password": "AdminPassword123!",
            "full_name": "Second Admin",
            "role": "ADMIN",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["email"] == "another.admin@test.edu"
    assert response.json()["role"] == "ADMIN"


def test_admin_update_user_status(client, admin_auth_headers, student_user):
    response = client.patch(
        f"/api/v1/admin/users/{student_user.id}/status",
        json={"status": "SUSPENDED"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "SUSPENDED"
