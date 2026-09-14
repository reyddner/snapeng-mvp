"""Testes do claim draft publico -> projeto autenticado."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.template import EngineeringTemplate, TemplateCategory


def _session_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    template = EngineeringTemplate(
        name="Template Claim",
        description="Para claim",
        category=TemplateCategory.ELETRICA,
        subcategory="eletrica",
        is_public=1,
        structure={"sections": [{"title": "A", "content": "x {{localizacao}}"}], "variables": []},
        variables=[{"name": "localizacao", "type": "text", "required": False}],
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    app.dependency_overrides[get_db] = lambda: session
    return TestClient(app), session, template.id


def test_claim_draft_requires_auth():
    client, session, template_id = _session_client()
    try:
        created = client.post(
            "/api/v1/drafts",
            json={
                "enterprise": {"name": "Obra Claim", "shared_data": {}},
                "disciplines": [{"discipline": "eletrica", "template_id": template_id}],
                "mode": "individual",
                "professional": {"full_name": "Eng"},
            },
        )
        draft_id = created.json()["draft_id"]
        denied = client.post(f"/api/v1/drafts/{draft_id}/claim")
        assert denied.status_code == 401
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_claim_draft_creates_project_and_is_idempotent():
    client, session, template_id = _session_client()
    try:
        email = "claim.user@example.com"
        password = "senha1234"
        assert client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Claim User"},
        ).status_code == 201
        login = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        created = client.post(
            "/api/v1/drafts",
            json={
                "enterprise": {
                    "name": "Residencia Claim",
                    "description": "Desc",
                    "shared_data": {"municipio": "Goiania"},
                },
                "disciplines": [
                    {
                        "discipline": "eletrica",
                        "template_id": template_id,
                        "data": {"tensao": "220"},
                    }
                ],
                "mode": "both",
                "professional": {"full_name": "Eng Claim"},
                "status": "memorial_gerado",
            },
        )
        assert created.status_code == 201
        draft_id = created.json()["draft_id"]

        claimed = client.post(f"/api/v1/drafts/{draft_id}/claim", headers=headers)
        assert claimed.status_code == 200
        body = claimed.json()
        assert body["name"] == "Residencia Claim"
        assert body["owner_id"] > 0
        assert body["template_id"] == template_id
        assert body["status"] in {"completed", "COMPLETED"}
        assert body["project_data"]["kind"] == "memorial_plan"
        assert body["project_data"]["source_draft_id"] == draft_id
        assert body["project_data"]["disciplines"][0]["data"]["tensao"] == "220"
        project_id = body["id"]

        # Draft removido apos claim
        assert client.get(f"/api/v1/drafts/{draft_id}").status_code == 404

        listed = client.get("/api/v1/projects/", headers=headers)
        assert listed.status_code == 200
        assert any(p["id"] == project_id for p in listed.json())
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_claim_rejects_draft_without_template():
    client, session, _template_id = _session_client()
    try:
        email = "claim.notpl@example.com"
        password = "senha1234"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "X"},
        )
        token = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        created = client.post(
            "/api/v1/drafts",
            json={
                "enterprise": {"name": "Sem template", "shared_data": {}},
                "disciplines": [{"discipline": "eletrica"}],
                "mode": "individual",
                "professional": {"full_name": "Eng"},
            },
        )
        draft_id = created.json()["draft_id"]
        claimed = client.post(f"/api/v1/drafts/{draft_id}/claim", headers=headers)
        assert claimed.status_code == 422
    finally:
        app.dependency_overrides.clear()
        session.close()
