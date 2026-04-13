from fastapi.testclient import TestClient


BASE_AUTH = "/api/auth"
BASE_PROJECTS = "/api/projects"


def _register_and_login(client: TestClient, email: str, username: str, password: str) -> str:
    register_payload = {
        "email": email,
        "username": username,
        "password": password,
    }
    reg = client.post(f"{BASE_AUTH}/register", json=register_payload)
    assert reg.status_code == 201

    login = client.post(
        f"{BASE_AUTH}/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_project(client: TestClient, owner_token: str, name: str = "Proyecto RF5") -> int:
    res = client.post(
        BASE_PROJECTS,
        json={"name": name, "description": "Permisos avanzados"},
        headers=_auth_header(owner_token),
    )
    assert res.status_code == 201
    return res.json()["id"]


def _add_member(client: TestClient, owner_token: str, project_id: int, user_id: int, role: str) -> None:
    res = client.post(
        f"{BASE_PROJECTS}/{project_id}/members",
        json={"user_id": user_id, "role": role},
        headers=_auth_header(owner_token),
    )
    assert res.status_code == 200


def _create_task(client: TestClient, token: str, project_id: int, title: str = "Tarea RF5") -> int:
    res = client.post(
        f"{BASE_PROJECTS}/{project_id}/tasks",
        json={"title": title, "description": "Desc"},
        headers=_auth_header(token),
    )
    assert res.status_code == 201
    return res.json()["id"]


def test_owner_can_assign_task_to_member(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_rf5@example.com", "Owner RF5", "Pass1234")
    member_token = _register_and_login(client, "member_rf5@example.com", "Member RF5", "Pass1234")

    member_me = client.get(f"{BASE_AUTH}/me", headers=_auth_header(member_token))
    member_id = member_me.json()["id"]

    project_id = _create_project(client, owner_token)
    _add_member(client, owner_token, project_id, member_id, "MEMBER")
    task_id = _create_task(client, owner_token, project_id)

    assign = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{task_id}/assign",
        json={"assigned_to": member_id},
        headers=_auth_header(owner_token),
    )

    assert assign.status_code == 200
    assert assign.json()["assigned_to"] == member_id


def test_member_cannot_assign_task(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_noassign@example.com", "Owner NoAssign", "Pass1234")
    member_token = _register_and_login(client, "member_noassign@example.com", "Member NoAssign", "Pass1234")

    member_me = client.get(f"{BASE_AUTH}/me", headers=_auth_header(member_token))
    member_id = member_me.json()["id"]

    project_id = _create_project(client, owner_token)
    _add_member(client, owner_token, project_id, member_id, "MEMBER")
    task_id = _create_task(client, owner_token, project_id)

    assign = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{task_id}/assign",
        json={"assigned_to": member_id},
        headers=_auth_header(member_token),
    )

    assert assign.status_code == 403


def test_viewer_cannot_create_task(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_viewer@example.com", "Owner Viewer", "Pass1234")
    viewer_token = _register_and_login(client, "viewer_rf5@example.com", "Viewer RF5", "Pass1234")

    viewer_me = client.get(f"{BASE_AUTH}/me", headers=_auth_header(viewer_token))
    viewer_id = viewer_me.json()["id"]

    project_id = _create_project(client, owner_token)
    _add_member(client, owner_token, project_id, viewer_id, "VIEWER")

    create_task = client.post(
        f"{BASE_PROJECTS}/{project_id}/tasks",
        json={"title": "No permitido", "description": "Viewer"},
        headers=_auth_header(viewer_token),
    )

    assert create_task.status_code == 403


def test_assigned_member_can_edit_task(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_edit@example.com", "Owner Edit", "Pass1234")
    member_token = _register_and_login(client, "member_edit@example.com", "Member Edit", "Pass1234")

    member_me = client.get(f"{BASE_AUTH}/me", headers=_auth_header(member_token))
    member_id = member_me.json()["id"]

    project_id = _create_project(client, owner_token)
    _add_member(client, owner_token, project_id, member_id, "MEMBER")
    task_id = _create_task(client, owner_token, project_id)

    assign = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{task_id}/assign",
        json={"assigned_to": member_id},
        headers=_auth_header(owner_token),
    )
    assert assign.status_code == 200

    update = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{task_id}",
        json={"status": "IN_PROGRESS", "description": "Tomada por miembro"},
        headers=_auth_header(member_token),
    )

    assert update.status_code == 200
    assert update.json()["status"] == "IN_PROGRESS"
    assert update.json()["description"] == "Tomada por miembro"


def test_non_assigned_member_cannot_edit_task(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_block@example.com", "Owner Block", "Pass1234")
    member_a_token = _register_and_login(client, "member_a@example.com", "Member A", "Pass1234")
    member_b_token = _register_and_login(client, "member_b@example.com", "Member B", "Pass1234")

    member_a_id = client.get(f"{BASE_AUTH}/me", headers=_auth_header(member_a_token)).json()["id"]
    member_b_id = client.get(f"{BASE_AUTH}/me", headers=_auth_header(member_b_token)).json()["id"]

    project_id = _create_project(client, owner_token)
    _add_member(client, owner_token, project_id, member_a_id, "MEMBER")
    _add_member(client, owner_token, project_id, member_b_id, "MEMBER")
    task_id = _create_task(client, owner_token, project_id)

    assign = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{task_id}/assign",
        json={"assigned_to": member_a_id},
        headers=_auth_header(owner_token),
    )
    assert assign.status_code == 200

    update = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{task_id}",
        json={"description": "Intento sin permiso"},
        headers=_auth_header(member_b_token),
    )

    assert update.status_code == 403
