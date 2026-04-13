import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Must be set BEFORE app modules are imported so Settings picks up SQLite
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-min-32-chars")

from app.main import app  # noqa: E402
import app.database as app_db  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.user import User  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Override the module-level engine to use SQLite
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
app_db.engine = test_engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
app_db.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db_session):
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def regular_user(db_session):
    user = User(
        username="member",
        email="member@example.com",
        hashed_password=get_password_hash("memberpass"),
        role="member",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    response = client.post(
        "/api/auth/token",
        data={"username": "admin", "password": "adminpass"},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def member_token(client, regular_user):
    response = client.post(
        "/api/auth/token",
        data={"username": "member", "password": "memberpass"},
    )
    return response.json()["access_token"]
