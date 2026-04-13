from fastapi.testclient import TestClient


BASE_AUTH = "/api/auth"
BASE_PROJECTS = "/api/projects"


def _register_and_login(client: TestClient, email: str, username: str, password: str = "Pass1234") -> str:
    register = client.post(
        f"{BASE_AUTH}/register",
        json={"email": email, "username": username, "password": password},
    )
    assert register.status_code == 201

    login = client.post(
        f"{BASE_AUTH}/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_project(client: TestClient, token: str, name: str = "Proyecto Stats") -> int:
    response = client.post(
        BASE_PROJECTS,
        json={"name": name, "description": "stats"},
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_task(client: TestClient, token: str, project_id: int, title: str) -> int:
    response = client.post(
        f"{BASE_PROJECTS}/{project_id}/tasks",
        json={"title": title, "description": "desc"},
        headers=_headers(token),
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_project_stats_owner_can_view_counts(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_stats@example.com", "owner_stats")
    project_id = _create_project(client, owner_token)

    todo_task = _create_task(client, owner_token, project_id, "Task TODO")
    in_progress_task = _create_task(client, owner_token, project_id, "Task IN_PROGRESS")
    done_task = _create_task(client, owner_token, project_id, "Task DONE")

    to_in_progress = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{in_progress_task}",
        json={"status": "IN_PROGRESS"},
        headers=_headers(owner_token),
    )
    assert to_in_progress.status_code == 200

    done_step_1 = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{done_task}",
        json={"status": "IN_PROGRESS"},
        headers=_headers(owner_token),
    )
    assert done_step_1.status_code == 200

    done_step_2 = client.put(
        f"{BASE_PROJECTS}/{project_id}/tasks/{done_task}",
        json={"status": "DONE"},
        headers=_headers(owner_token),
    )
    assert done_step_2.status_code == 200

    stats = client.get(
        f"{BASE_PROJECTS}/{project_id}/stats",
        headers=_headers(owner_token),
    )

    assert stats.status_code == 200
    body = stats.json()
    assert body["project_id"] == project_id
    assert body["total"] == 3
    assert body["todo"] == 1
    assert body["in_progress"] == 1
    assert body["done"] == 1
    assert body["pct_complete"] == 33.33

    # keep variables referenced to avoid accidental refactor deletion of task creation
    assert todo_task > 0


def test_project_stats_member_can_view(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_stats_member@example.com", "owner_stats_member")
    member_token = _register_and_login(client, "member_stats@example.com", "member_stats")

    member_me = client.get(f"{BASE_AUTH}/me", headers=_headers(member_token))
    member_id = member_me.json()["id"]

    project_id = _create_project(client, owner_token)

    add_member = client.post(
        f"{BASE_PROJECTS}/{project_id}/members",
        json={"user_id": member_id, "role": "MEMBER"},
        headers=_headers(owner_token),
    )
    assert add_member.status_code == 200

    _create_task(client, owner_token, project_id, "Task member stats")

    stats = client.get(
        f"{BASE_PROJECTS}/{project_id}/stats",
        headers=_headers(member_token),
    )

    assert stats.status_code == 200
    assert stats.json()["total"] == 1


def test_project_stats_non_member_gets_404(client: TestClient) -> None:
    owner_token = _register_and_login(client, "owner_stats_404@example.com", "owner_stats_404")
    other_token = _register_and_login(client, "other_stats_404@example.com", "other_stats_404")

    project_id = _create_project(client, owner_token)

    stats = client.get(
        f"{BASE_PROJECTS}/{project_id}/stats",
        headers=_headers(other_token),
    )

    assert stats.status_code == 404
