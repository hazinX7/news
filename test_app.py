from fastapi.testclient import TestClient

from main import app


def test_smoke_flow():
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200

        r = client.post(
            "/auth/register",
            data={"name": "Тест", "email": "user@example.com", "password": "secret12"},
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
