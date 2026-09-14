"""Testes de cookies HttpOnly, dashboard e CSP."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.rate_limit import auth_login_limiter, auth_register_limiter
from app.main import app

client = TestClient(app)


def _clear_auth_rate_limits():
    auth_login_limiter._memory._hits.clear()
    auth_register_limiter._memory._hits.clear()


def _login(email: str | None = None):
    _clear_auth_rate_limits()
    email = email or f"user-{uuid4().hex[:10]}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "senha123",
            "full_name": "Cookie User",
            "crea": "CREA-1",
        },
    )
    assert register.status_code in (201, 400)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "senha123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    return response


def test_dashboard_redirects_when_anonymous():
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers.get("location", "")


def test_dashboard_allows_cookie_session():
    _login("dashboard.cookie@example.com")
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 200
    assert "Meus Projetos" in response.text


def test_me_works_with_cookie_only():
    _login("me.cookie@example.com")
    # Sem Authorization header: apenas cookie da sessao do TestClient
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "me.cookie@example.com"


def test_refresh_from_cookie_without_body_token():
    _login("refresh.cookie@example.com")
    refreshed = client.post("/api/v1/auth/refresh", json={})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


def test_logout_clears_cookies():
    _login("logout.cookie@example.com")
    logged_out = client.post("/api/v1/auth/logout")
    assert logged_out.status_code == 204
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 401


def test_editor_redirects_when_anonymous():
    response = client.get("/editor/1", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers.get("location", "")


def test_editor_missing_project_goes_to_dashboard():
    _login("editor.cookie@example.com")
    response = client.get("/editor/999999", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers.get("location", "")


def test_csp_header_present():
    response = client.get("/health")
    assert "Content-Security-Policy" in response.headers
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers.get("X-Frame-Options") == "DENY"
