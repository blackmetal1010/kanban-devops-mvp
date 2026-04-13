def _auth_headers(client, email: str, username: str, password: str = "Rad12345") -> dict[str, str]:
    register = client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_project_authenticated_returns_201(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    response = client.post(
        "/api/projects",
        json={"name": "Proyecto 1", "description": "Descripcion"},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Proyecto 1"
    assert body["owner_id"] > 0
    assert body["is_deleted"] is False


def test_list_projects_only_own_returns_200(client):
    headers_owner = _auth_headers(client, "owner@example.com", "owner")
    headers_other = _auth_headers(client, "other@example.com", "other")

    create_owner = client.post(
        "/api/projects",
        json={"name": "Proyecto Owner", "description": "x"},
        headers=headers_owner,
    )
    assert create_owner.status_code == 201

    create_other = client.post(
        "/api/projects",
        json={"name": "Proyecto Other", "description": "y"},
        headers=headers_other,
    )
    assert create_other.status_code == 201

    list_owner = client.get("/api/projects", headers=headers_owner)
    assert list_owner.status_code == 200
    names_owner = [item["name"] for item in list_owner.json()]
    assert "Proyecto Owner" in names_owner
    assert "Proyecto Other" not in names_owner


def test_access_other_user_project_returns_404(client):
    headers_owner = _auth_headers(client, "owner@example.com", "owner")
    headers_other = _auth_headers(client, "other@example.com", "other")

    created = client.post(
        "/api/projects",
        json={"name": "Privado", "description": "x"},
        headers=headers_owner,
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    response = client.get(f"/api/projects/{project_id}", headers=headers_other)
    assert response.status_code == 404


def test_soft_delete_project_hidden_from_list(client):
    headers = _auth_headers(client, "owner@example.com", "owner")

    created = client.post(
        "/api/projects",
        json={"name": "A borrar", "description": "x"},
        headers=headers,
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    deleted = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert deleted.status_code == 200

    listed = client.get("/api/projects", headers=headers)
    assert listed.status_code == 200
    names = [item["name"] for item in listed.json()]
    assert "A borrar" not in names
