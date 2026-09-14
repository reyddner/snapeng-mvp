"""Claim + edicao autenticada do memorial_plan."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.template import EngineeringTemplate, TemplateCategory


def _client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    template = EngineeringTemplate(
        name="Template MVP",
        description="mvp",
        category=TemplateCategory.ELETRICA,
        subcategory="eletrica",
        is_public=1,
        structure={"sections": [{"title": "A", "content": "{{localizacao}}"}], "variables": []},
        variables=[{"name": "localizacao", "type": "text", "required": False}],
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    app.dependency_overrides[get_db] = lambda: session
    return TestClient(app), session, template.id


def test_claim_then_edit_and_open_full_editor():
    client, session, template_id = _client()
    try:
        email = "mvp.edit@example.com"
        password = "senha1234"
        assert (
            client.post(
                "/api/v1/auth/register",
                json={"email": email, "password": password, "full_name": "MVP"},
            ).status_code
            == 201
        )
        login = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        created = client.post(
            "/api/v1/drafts",
            json={
                "enterprise": {
                    "name": "Obra MVP",
                    "shared_data": {"municipio": "Goiania"},
                },
                "disciplines": [
                    {
                        "discipline": "eletrica",
                        "template_id": template_id,
                        "data": {"tensao": "127"},
                    }
                ],
                "mode": "individual",
                "professional": {"full_name": "Eng MVP"},
                "status": "em_preenchimento",
            },
        )
        draft_id = created.json()["draft_id"]
        claimed = client.post(f"/api/v1/drafts/{draft_id}/claim", headers=headers)
        assert claimed.status_code == 200
        project_id = claimed.json()["id"]

        updated = client.put(
            f"/api/v1/projects/{project_id}",
            headers=headers,
            json={
                "name": "Obra MVP Atualizada",
                "project_data": {
                    "kind": "memorial_plan",
                    "source_draft_id": draft_id,
                    "enterprise": {
                        "name": "Obra MVP Atualizada",
                        "shared_data": {"municipio": "Anapolis"},
                    },
                    "disciplines": [
                        {
                            "discipline": "eletrica",
                            "template_id": template_id,
                            "data": {"tensao": "220"},
                        }
                    ],
                    "mode": "both",
                    "professional": {"full_name": "Eng MVP"},
                    "source_documents": [],
                    "draft_status": "em_preenchimento",
                },
                "status": "in_progress",
            },
        )
        assert updated.status_code == 200
        body = updated.json()
        assert body["name"] == "Obra MVP Atualizada"
        assert body["project_data"]["kind"] == "memorial_plan"
        assert body["project_data"]["disciplines"][0]["data"]["tensao"] == "220"
        assert body["project_data"]["enterprise"]["shared_data"]["municipio"] == "Anapolis"

        page = client.get(f"/editor/{project_id}")
        assert page.status_code == 200
        assert 'editorMode: \'project\'' in page.text or 'editorMode: "project"' in page.text or "editor_mode" in page.text or "Conta · edição completa" in page.text or "isProjectMode" in page.text
    finally:
        app.dependency_overrides.clear()
        session.close()
