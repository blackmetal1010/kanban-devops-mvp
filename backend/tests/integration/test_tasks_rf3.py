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


def _create_project(client, headers: dict[str, str], name: str = "Proyecto Tareas") -> int:
    response = client.post(
        "/api/projects",
        json={"name": name, "description": "desc"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_task_authenticated_returns_201(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)

    response = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Tarea 1", "description": "Primera tarea"},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Tarea 1"
    assert body["status"] == "TODO"
    assert body["project_id"] == project_id


def test_status_transition_flow_and_invalid_transition(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)

    created = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Tarea estado", "description": "x"},
        headers=headers,
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    to_in_progress = client.put(
        f"/api/projects/{project_id}/tasks/{task_id}",
        json={"status": "IN_PROGRESS"},
        headers=headers,
    )
    assert to_in_progress.status_code == 200
    assert to_in_progress.json()["status"] == "IN_PROGRESS"

    to_done = client.put(
        f"/api/projects/{project_id}/tasks/{task_id}",
        json={"status": "DONE"},
        headers=headers,
    )
    assert to_done.status_code == 200
    assert to_done.json()["status"] == "DONE"

    invalid = client.put(
        f"/api/projects/{project_id}/tasks/{task_id}",
        json={"status": "TODO"},
        headers=headers,
    )
    assert invalid.status_code == 400


def test_list_tasks_returns_200(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)

    create1 = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Tarea A", "description": "x"},
        headers=headers,
    )
    assert create1.status_code == 201

    create2 = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Tarea B", "description": "y"},
        headers=headers,
    )
    assert create2.status_code == 201

    listed = client.get(f"/api/projects/{project_id}/tasks", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 2


def test_access_other_user_project_tasks_returns_404(client):
    headers_owner = _auth_headers(client, "owner@example.com", "owner")
    headers_other = _auth_headers(client, "other@example.com", "other")

    project_id = _create_project(client, headers_owner, name="Privado")

    response = client.get(f"/api/projects/{project_id}/tasks", headers=headers_other)
    assert response.status_code == 404


def test_soft_delete_task_hidden_from_list(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)

    created = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Eliminar", "description": "x"},
        headers=headers,
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    deleted = client.delete(f"/api/projects/{project_id}/tasks/{task_id}", headers=headers)
    assert deleted.status_code == 200

    listed = client.get(f"/api/projects/{project_id}/tasks", headers=headers)
    assert listed.status_code == 200
    titles = [item["title"] for item in listed.json()]
    assert "Eliminar" not in titles
