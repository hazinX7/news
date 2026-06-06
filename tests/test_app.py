import os
import uuid

from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://lentadnya:lentadnya@localhost:5432/lentadnya")
os.environ["SESSION_SECRET"] = "test-secret"

from app.main import app  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models import User  # noqa: E402


def test_smoke_flow():
    test_email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    test_name = f"User{uuid.uuid4().hex[:8]}"
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200

        r = client.post(
            "/auth/register",
            data={"name": test_name, "email": test_email, "password": "secret12"},
            follow_redirects=False,
        )
        assert r.status_code == 303

        r = client.get("/")
        assert "Свежие новости" in r.text


def test_admin_login_page_available():
    with TestClient(app) as client:
        r = client.get("/auth/login")
        assert r.status_code == 200
        assert "Вход" in r.text


def test_register_rejects_existing_email():
    name = f"User{uuid.uuid4().hex[:8]}"
    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    with TestClient(app) as client:
        r = client.post("/auth/register", data={"name": name, "email": email, "password": "secret12"})
        assert r.status_code == 200

        r = client.post(
            "/auth/register",
            data={"name": f"Other{uuid.uuid4().hex[:8]}", "email": email, "password": "secret12"},
        )
        assert "Пользователь с таким email уже существует в системе" in r.text


def test_register_rejects_existing_username():
    name = f"User{uuid.uuid4().hex[:8]}"
    with TestClient(app) as client:
        r = client.post(
            "/auth/register",
            data={"name": name, "email": f"user-{uuid.uuid4().hex[:8]}@example.com", "password": "secret12"},
        )
        assert r.status_code == 200

        r = client.post(
            "/auth/register",
            data={"name": name, "email": f"user-{uuid.uuid4().hex[:8]}@example.com", "password": "secret12"},
        )
        assert "Пользователь с таким username уже существует в системе" in r.text


def test_register_rejects_cyrillic_name_and_email():
    with TestClient(app) as client:
        r = client.post(
            "/auth/register",
            data={"name": "Тест", "email": f"user-{uuid.uuid4().hex[:8]}@example.com", "password": "secret12"},
        )
        assert "Имя пользователя не должно содержать русские символы" in r.text

        r = client.post(
            "/auth/register",
            data={"name": f"User{uuid.uuid4().hex[:8]}", "email": "тест@example.com", "password": "secret12"},
        )
        assert "E-mail не должен содержать русские символы" in r.text


def test_editor_permissions():
    editor_email = f"editor-{uuid.uuid4().hex[:8]}@example.com"
    editor_name = f"Editor{uuid.uuid4().hex[:8]}"
    with TestClient(app) as client:
        client.post(
            "/auth/register",
            data={"name": editor_name, "email": editor_email, "password": "secret12"},
            follow_redirects=False,
        )

        db = SessionLocal()
        try:
            editor = db.query(User).filter(User.email == editor_email).first()
            editor.role = "editor"
            db.commit()
        finally:
            db.close()

        r = client.get("/admin")
        assert r.status_code == 200
        assert "Панель контента" in r.text

        r = client.post("/admin/users/1/delete", follow_redirects=False)
        assert r.status_code == 403
