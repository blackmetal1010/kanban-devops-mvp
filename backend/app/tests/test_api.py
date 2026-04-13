import pytest


class TestHealth:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestAuth:
    def test_login_success(self, client, admin_user):
        response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "adminpass"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, admin_user):
        response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "wrongpass"},
        )
        assert response.status_code == 401

    def test_login_unknown_user(self, client):
        response = client.post(
            "/api/auth/token",
            data={"username": "nobody", "password": "pass"},
        )
        assert response.status_code == 401

    def test_get_me(self, client, admin_token):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["username"] == "admin"

    def test_get_me_no_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_register(self, client):
        response = client.post(
            "/api/auth/register",
            params={"username": "newuser", "email": "new@example.com", "password": "newpass123"},
        )
        assert response.status_code == 201
        assert response.json()["username"] == "newuser"

    def test_register_duplicate_username(self, client, admin_user):
        response = client.post(
            "/api/auth/register",
            params={"username": "admin", "email": "other@example.com", "password": "pass"},
        )
        assert response.status_code == 400


class TestProjects:
    def test_create_project(self, client, admin_token):
        response = client.post(
            "/api/projects/",
            json={"name": "Test Project", "description": "A test"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Project"

    def test_list_projects(self, client, admin_token):
        client.post(
            "/api/projects/",
            json={"name": "Project A"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        response = client.get(
            "/api/projects/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_project(self, client, admin_token):
        create_resp = client.post(
            "/api/projects/",
            json={"name": "Project B"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        pid = create_resp.json()["id"]
        response = client.get(
            f"/api/projects/{pid}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == pid

    def test_update_project(self, client, admin_token):
        create_resp = client.post(
            "/api/projects/",
            json={"name": "Old Name"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        pid = create_resp.json()["id"]
        response = client.put(
            f"/api/projects/{pid}",
            json={"name": "New Name"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    def test_delete_project(self, client, admin_token):
        create_resp = client.post(
            "/api/projects/",
            json={"name": "To Delete"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        pid = create_resp.json()["id"]
        response = client.delete(
            f"/api/projects/{pid}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

    def test_project_not_found(self, client, admin_token):
        response = client.get(
            "/api/projects/99999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_member_cannot_access_others_project(self, client, admin_token, member_token):
        create_resp = client.post(
            "/api/projects/",
            json={"name": "Admin Project"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        pid = create_resp.json()["id"]
        response = client.get(
            f"/api/projects/{pid}",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 403


class TestTasks:
    def _create_project(self, client, token):
        return client.post(
            "/api/projects/",
            json={"name": "Task Project"},
            headers={"Authorization": f"Bearer {token}"},
        ).json()

    def test_create_task(self, client, admin_token):
        project = self._create_project(client, admin_token)
        response = client.post(
            "/api/tasks/",
            json={"title": "My Task", "project_id": project["id"]},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        assert response.json()["title"] == "My Task"
        assert response.json()["status"] == "todo"

    def test_list_tasks_by_project(self, client, admin_token):
        project = self._create_project(client, admin_token)
        client.post(
            "/api/tasks/",
            json={"title": "Task 1", "project_id": project["id"]},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        response = client.get(
            f"/api/tasks/?project_id={project['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_update_task_status(self, client, admin_token):
        project = self._create_project(client, admin_token)
        task = client.post(
            "/api/tasks/",
            json={"title": "Status Task", "project_id": project["id"]},
            headers={"Authorization": f"Bearer {admin_token}"},
        ).json()
        response = client.put(
            f"/api/tasks/{task['id']}",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_delete_task(self, client, admin_token):
        project = self._create_project(client, admin_token)
        task = client.post(
            "/api/tasks/",
            json={"title": "Delete Me", "project_id": project["id"]},
            headers={"Authorization": f"Bearer {admin_token}"},
        ).json()
        response = client.delete(
            f"/api/tasks/{task['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

    def test_task_not_found(self, client, admin_token):
        response = client.get(
            "/api/tasks/99999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
