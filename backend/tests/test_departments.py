def test_list_departments(client, sample_department):
    response = client.get("/api/v1/departments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["code"] == sample_department.code


def test_get_department_by_id(client, sample_department):
    response = client.get(f"/api/v1/departments/{sample_department.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_department.name


def test_get_department_not_found(client):
    import uuid
    response = client.get(f"/api/v1/departments/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEPARTMENT_NOT_FOUND"


def test_create_department_duplicate_code(client, admin_auth_headers, sample_department):
    response = client.post(
        "/api/v1/departments",
        json={"code": sample_department.code, "name": "Another Department"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DEPARTMENT_CODE_EXISTS"


def test_create_department_duplicate_name(client, admin_auth_headers, sample_department):
    response = client.post(
        "/api/v1/departments",
        json={"code": "DIFF", "name": sample_department.name},
        headers=admin_auth_headers,
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DEPARTMENT_NAME_EXISTS"


def test_update_department_success(client, admin_auth_headers, sample_department):
    response = client.put(
        f"/api/v1/departments/{sample_department.id}",
        json={"name": "Computer Science & Engineering Updated", "building": "New Building B"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Computer Science & Engineering Updated"
    assert data["building"] == "New Building B"
