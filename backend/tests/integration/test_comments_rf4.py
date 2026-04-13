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


def _create_project(client, headers: dict[str, str], name: str = "Proyecto Comentarios") -> int:
    response = client.post(
        "/api/projects",
        json={"name": name, "description": "desc"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_task(client, headers: dict[str, str], project_id: int, title: str = "Tarea base") -> int:
    response = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": title, "description": "desc"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_comment_authenticated_returns_201(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)
    task_id = _create_task(client, headers, project_id)

    response = client.post(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        json={"text": "Primer comentario"},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["text"] == "Primer comentario"
    assert body["author_id"] > 0


def test_list_comments_returns_200(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)
    task_id = _create_task(client, headers, project_id)

    c1 = client.post(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        json={"text": "Comentario 1"},
        headers=headers,
    )
    assert c1.status_code == 201

    c2 = client.post(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        json={"text": "Comentario 2"},
        headers=headers,
    )
    assert c2.status_code == 201

    listed = client.get(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        headers=headers,
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 2


def test_edit_own_comment_returns_200(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)
    task_id = _create_task(client, headers, project_id)

    created = client.post(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        json={"text": "Texto inicial"},
        headers=headers,
    )
    assert created.status_code == 201
    comment_id = created.json()["id"]

    updated = client.put(
        f"/api/projects/{project_id}/tasks/{task_id}/comments/{comment_id}",
        json={"text": "Texto editado"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["text"] == "Texto editado"


def test_edit_comment_from_user_without_project_access_returns_404(client):
    headers_owner = _auth_headers(client, "owner@example.com", "owner")
    headers_other = _auth_headers(client, "other@example.com", "other")

    project_id = _create_project(client, headers_owner)
    task_id = _create_task(client, headers_owner, project_id)

    created = client.post(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        json={"text": "Comentario owner"},
        headers=headers_owner,
    )
    assert created.status_code == 201
    comment_id = created.json()["id"]

    forbidden = client.put(
        f"/api/projects/{project_id}/tasks/{task_id}/comments/{comment_id}",
        json={"text": "Intento editar"},
        headers=headers_other,
    )
    assert forbidden.status_code == 404


def test_soft_delete_comment_hidden_from_list(client):
    headers = _auth_headers(client, "owner@example.com", "owner")
    project_id = _create_project(client, headers)
    task_id = _create_task(client, headers, project_id)

    created = client.post(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        json={"text": "Se borrara"},
        headers=headers,
    )
    assert created.status_code == 201
    comment_id = created.json()["id"]

    deleted = client.delete(
        f"/api/projects/{project_id}/tasks/{task_id}/comments/{comment_id}",
        headers=headers,
    )
    assert deleted.status_code == 200

    listed = client.get(
        f"/api/projects/{project_id}/tasks/{task_id}/comments",
        headers=headers,
    )
    assert listed.status_code == 200
    texts = [item["text"] for item in listed.json()]
    assert "Se borrara" not in texts
