def test_student_cannot_create_department(client, student_auth_headers):
    response = client.post(
        "/api/v1/departments",
        json={"code": "PHY", "name": "Physics"},
        headers=student_auth_headers,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_faculty_cannot_create_department(client, faculty_auth_headers):
    response = client.post(
        "/api/v1/departments",
        json={"code": "CHEM", "name": "Chemistry"},
        headers=faculty_auth_headers,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_admin_can_create_department(client, admin_auth_headers):
    response = client.post(
        "/api/v1/departments",
        json={"code": "BIO", "name": "Biotechnology"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["code"] == "BIO"


def test_student_cannot_update_faculty_profile(client, student_auth_headers):
    response = client.put(
        "/api/v1/users/faculty/me",
        json={"title": "Hacked Title"},
        headers=student_auth_headers,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_faculty_cannot_update_student_profile(client, faculty_auth_headers):
    response = client.put(
        "/api/v1/users/students/me",
        json={"major": "Hacked Major"},
        headers=faculty_auth_headers,
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_faculty_cannot_access_admin_user_list(client, faculty_auth_headers):
    response = client.get("/api/v1/admin/users", headers=faculty_auth_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_admin_can_access_admin_user_list(client, admin_auth_headers):
    response = client.get("/api/v1/admin/users", headers=admin_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
