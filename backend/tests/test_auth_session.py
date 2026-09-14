"""Testes de autenticacao JWT e refresh."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register_and_login(email: str = "auth.session@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "senha123",
            "full_name": "Usuario Teste",
            "crea": "CREA-GO 1",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "senha123"},
    )
    assert response.status_code == 200
    return response.json()


def test_login_returns_tokens_and_me_works():
    tokens = _register_and_login("auth.me@example.com")
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "auth.me@example.com"


def test_refresh_token_issues_new_access_token():
    tokens = _register_and_login("auth.refresh@example.com")
    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    data = refreshed.json()
    assert data["access_token"]
    assert data["refresh_token"]
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me.status_code == 200
