"""Testes de catalogo publico limpo e fluxo de criacao de memorial."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.template import EngineeringTemplate
from app.services.official_templates import (
    SEED_ALLOWLIST,
    is_sensitive_template_name,
    official_names_from_disk,
)
from app.services.template_quality import assess_template


client = TestClient(app)
TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "engineering_templates"


def test_catalog_has_no_sensitive_template_names():
    for path in TEMPLATES_DIR.rglob("*.json"):
        if "_inbox" in path.parts:
            continue
        if path.name not in SEED_ALLOWLIST:
            # Lixo fora da allowlist nao deve existir no disco do produto.
            assert False, f"Arquivo fora da allowlist no disco: {path}"
        data = path.read_text(encoding="utf-8")
        assert "gerado automaticamente" not in data.casefold()
        name = __import__("json").loads(data)["name"]
        assert not is_sensitive_template_name(name), name


def test_public_list_only_ready_templates():
    response = client.get("/api/v1/templates/")
    assert response.status_code == 200
    templates = response.json()
    assert templates, "Catalogo publico vazio — rode load_templates + purge"
    keep = official_names_from_disk(TEMPLATES_DIR)
    for item in templates:
        assert item["name"] in keep
        assert not is_sensitive_template_name(item["name"])
        structure = item.get("structure") or {}
        structure.setdefault("variables", item.get("variables") or [])
        assert assess_template(structure)["ready"] is True


def test_create_memorial_persists_draft():
    listing = client.get("/api/v1/templates/").json()
    arquitetura = next(t for t in listing if t.get("subcategory") == "arquitetura")
    response = client.post(
        "/api/v1/drafts",
        json={
            "enterprise": {
                "name": "Obra Persistencia",
                "description": "",
                "shared_data": {},
            },
            "mode": "both",
            "disciplines": [
                {
                    "discipline": "arquitetura",
                    "template_id": arquitetura["id"],
                    "data": {},
                }
            ],
            "professional": {
                "full_name": "A definir",
                "professional_title": "Engenheiro(a)",
            },
            "ttl_days": 7,
            "status": "novo",
        },
    )
    assert response.status_code == 201, response.text
    draft_id = response.json()["draft_id"]
    fetched = client.get(f"/api/v1/drafts/{draft_id}")
    assert fetched.status_code == 200
    payload = fetched.json()["payload"]
    assert payload["enterprise"]["name"] == "Obra Persistencia"
    assert payload["disciplines"][0]["template_id"] == arquitetura["id"]


def test_enterprise_form_asks_name_first():
    html = (Path(__file__).resolve().parents[2] / "frontend" / "templates" / "new_enterprise.html").read_text(
        encoding="utf-8"
    )
    name_pos = html.find("Nome do empreendimento")
    assert name_pos != -1
    # Localizacao e demais dados do projeto ficam no editor (draft_editor), nao aqui.
    assert "Local da obra" not in html
    assert "Continuar para o preenchimento" in html

    editor = (
        Path(__file__).resolve().parents[2] / "frontend" / "templates" / "draft_editor.html"
    ).read_text(encoding="utf-8")
    assert "Dados do projeto" in editor
    assert "Local da obra" in editor
    assert editor.find("Dados do projeto") < editor.find("Local da obra")


def test_db_public_templates_match_allowlist():
    keep = official_names_from_disk(TEMPLATES_DIR)
    db = SessionLocal()
    try:
        publics = (
            db.query(EngineeringTemplate)
            .filter(EngineeringTemplate.is_public == 1)
            .all()
        )
        for template in publics:
            assert template.name in keep, template.name
            assert not is_sensitive_template_name(template.name)
    finally:
        db.close()
