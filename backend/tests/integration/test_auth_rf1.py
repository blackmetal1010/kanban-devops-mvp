def test_register_ok(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "rad@example.com",
            "username": "rad",
            "password": "Rad12345",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "rad@example.com"
    assert body["username"] == "rad"
    assert body["is_active"] is True


def test_register_duplicate_email_returns_409(client):
    payload = {
        "email": "rad@example.com",
        "username": "rad",
        "password": "Rad12345",
    }
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post(
        "/api/auth/register",
        json={
            "email": "rad@example.com",
            "username": "rad2",
            "password": "Rad12345",
        },
    )
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already registered"


def test_login_ok_returns_token(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "rad@example.com",
            "username": "rad",
            "password": "Rad12345",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "rad@example.com", "password": "Rad12345"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 86400


def test_login_bad_password_returns_401(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "rad@example.com",
            "username": "rad",
            "password": "Rad12345",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "rad@example.com", "password": "Wrong12345"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_me_without_token_returns_401(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token_returns_user(client):
    register = client.post(
        "/api/auth/register",
        json={
            "email": "rad@example.com",
            "username": "rad",
            "password": "Rad12345",
        },
    )
    assert register.status_code == 201

    login = client.post(
        "/api/auth/login",
        json={"email": "rad@example.com", "password": "Rad12345"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "rad@example.com"
