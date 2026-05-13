import os
import uuid

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SESSION_SECRET"] = "test-secret"

from app.main import app  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models import User  # noqa: E402


def test_smoke_flow():
    test_email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200

        r = client.post(
            "/auth/register",
            data={"name": "Тест", "email": test_email, "password": "secret12"},
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


def test_editor_permissions():
    editor_email = f"editor-{uuid.uuid4().hex[:8]}@example.com"
    with TestClient(app) as client:
        client.post(
            "/auth/register",
            data={"name": "Editor", "email": editor_email, "password": "secret12"},
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
