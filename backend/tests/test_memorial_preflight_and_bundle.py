"""Testes de preflight e geração pública de memoriais."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.template import EngineeringTemplate, TemplateCategory


def _client_with_template():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(
        EngineeringTemplate(
            name="Memorial CB Base Teste",
            description="Template ready para corpo de bombeiros",
            category=TemplateCategory.EDIFICACOES,
            subcategory="corpo_bombeiros",
            is_public=1,
            structure={
                "sections": [
                    {
                        "title": "Identificacao",
                        "content": (
                            "Obra em {{localizacao}} ocupacao {{ocupacao_bombeiros}} "
                            "area {{area_total_bombeiros}} altura {{altura_edificacao}} "
                            "pop {{populacao_bombeiros}} risco {{risco_incendio}} "
                            "saidas {{saidas_emergencia}} hidrantes {{sistema_hidrantes}} "
                            "sistemas {{sistemas_protecao}}."
                        ),
                    }
                ],
                "calculations": [],
                "normas": ["NBR 9077"],
                "variables": [
                    {"name": "localizacao", "type": "text", "required": True},
                    {"name": "ocupacao_bombeiros", "type": "text", "required": True},
                    {"name": "area_total_bombeiros", "type": "number", "required": True},
                    {"name": "altura_edificacao", "type": "number", "required": True},
                    {"name": "populacao_bombeiros", "type": "number", "required": True},
                    {"name": "risco_incendio", "type": "text", "required": True},
                    {"name": "saidas_emergencia", "type": "textarea", "required": True},
                    {"name": "sistema_hidrantes", "type": "select", "required": True, "options": [{"value": "nao_aplicavel", "label": "Nao aplicavel"}, {"value": "sim", "label": "Aplicavel"}]},
                    {"name": "sistemas_protecao", "type": "textarea", "required": True},
                ],
            },
            variables=[
                {"name": "localizacao", "type": "text", "required": True},
                {"name": "ocupacao_bombeiros", "type": "text", "required": True},
                {"name": "area_total_bombeiros", "type": "number", "required": True},
                {"name": "altura_edificacao", "type": "number", "required": True},
                {"name": "populacao_bombeiros", "type": "number", "required": True},
                {"name": "risco_incendio", "type": "text", "required": True},
                {"name": "saidas_emergencia", "type": "textarea", "required": True},
                {"name": "sistema_hidrantes", "type": "select", "required": True, "options": [{"value": "nao_aplicavel", "label": "Nao aplicavel"}, {"value": "sim", "label": "Aplicavel"}]},
                {"name": "sistemas_protecao", "type": "textarea", "required": True},
            ],
        )
    )
    session.commit()
    app.dependency_overrides[get_db] = lambda: session
    return TestClient(app), session


def _complete_payload(template_id: int):
    return {
        "enterprise": {
            "name": "Clinica Centro",
            "shared_data": {
                "localizacao": "Rua A, Goiania",
                "municipio": "Goiania",
                "uf": "GO",
            },
        },
        "mode": "both",
        "professional": {"full_name": "Eng. Teste", "crea_number": "123"},
        "disciplines": [
            {
                "discipline": "corpo_bombeiros",
                "template_id": template_id,
                "data": {
                    "ocupacao_bombeiros": "Clinica",
                    "area_total_bombeiros": 499,
                    "altura_edificacao": 3.5,
                    "populacao_bombeiros": 40,
                    "risco_incendio": "Baixo",
                    "saidas_emergencia": "2 saidas com 1,20 m",
                    "sistema_hidrantes": "nao_aplicavel",
                    "sistemas_protecao": "Extintores e iluminacao de emergencia",
                    "localizacao": "Rua A, Goiania",
                    "municipio": "Goiania",
                    "uf": "GO",
                },
            }
        ],
    }


def test_preflight_blocks_incomplete_and_allows_complete():
    client, session = _client_with_template()
    try:
        incomplete = client.post(
            "/api/v1/memorials/preflight",
            json={
                "enterprise": {"name": "Obra", "shared_data": {}},
                "disciplines": [{"discipline": "corpo_bombeiros", "template_id": 1, "data": {}}],
                "mode": "individual",
            },
        )
        assert incomplete.status_code == 200
        body = incomplete.json()
        assert body["can_generate"] is False
        assert body["blocking"]

        complete = client.post("/api/v1/memorials/preflight", json=_complete_payload(1))
        assert complete.status_code == 200
        assert complete.json()["can_generate"] is True
        assert complete.json()["summary"]["disciplines_ready"] == 1
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_generate_bundle_returns_zip_when_valid():
    client, session = _client_with_template()
    try:
        failed = client.post(
            "/api/v1/memorials/generate-bundle",
            json={
                "enterprise": {"name": "Obra", "shared_data": {"municipio": "Goiania"}},
                "disciplines": [{"discipline": "corpo_bombeiros", "template_id": 1, "data": {}}],
                "mode": "individual",
                "professional": {"full_name": "Eng. Teste"},
            },
        )
        assert failed.status_code == 422
        detail = failed.json()["detail"]
        assert "blocking" in detail
        assert detail["message"]

        ok = client.post("/api/v1/memorials/generate-bundle", json=_complete_payload(1))
        assert ok.status_code == 200
        assert ok.headers["content-type"].startswith("application/zip")
        assert ok.content[:2] == b"PK"
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_draft_status_and_ttl_refresh_on_patch():
    client, session = _client_with_template()
    try:
        created = client.post(
            "/api/v1/drafts",
            json={
                "enterprise": {"name": "Obra Status", "shared_data": {}},
                "disciplines": [{"discipline": "corpo_bombeiros"}],
                "mode": "individual",
                "professional": {"full_name": "Eng. Teste"},
                "ttl_days": 7,
            },
        )
        assert created.status_code == 201
        assert created.json()["status"] == "novo"
        draft_id = created.json()["draft_id"]
        expires_before = created.json()["expires_at"]

        updated = client.patch(
            f"/api/v1/drafts/{draft_id}",
            json={
                "enterprise": {"name": "Obra Status", "shared_data": {"uf": "GO"}},
                "status": "em_preenchimento",
            },
        )
        assert updated.status_code == 200
        assert updated.json()["status"] == "em_preenchimento"
        assert updated.json()["payload"]["status"] == "em_preenchimento"
        assert updated.json()["expires_at"] >= expires_before
    finally:
        app.dependency_overrides.clear()
        session.close()
