"""Testes dos projetos-modelo publicos (galeria + geracao)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_catalog import DEMO_PROJECTS, list_demos

client = TestClient(app)

EXPECTED_SLUGS = {
    "residencia-alto-padrao-alphaville-go",
    "galpao-logistico-aparecida-go",
}


def test_list_demos_catalog():
    demos = list_demos()
    assert {item["slug"] for item in demos} == EXPECTED_SLUGS
    for item in demos:
        assert item["discipline_count"] >= 9
        assert item["area_m2"] > 0
        assert "Plantas CAD" in item["scope_note"] or "CAD/DWG" in item["scope_note"]


def test_demos_cover_all_platform_disciplines():
    covered = set()
    for demo in DEMO_PROJECTS:
        covered.update(demo["disciplines_data"].keys())
    # Todas as disciplinas do questionario devem aparecer em ao menos um modelo.
    from app.services.questionnaire_catalog import CATALOG

    assert covered == set(CATALOG.keys())


def test_api_list_and_detail_demos():
    listing = client.get("/api/v1/demos")
    assert listing.status_code == 200, listing.text
    demos = listing.json()["demos"]
    assert {item["slug"] for item in demos} == EXPECTED_SLUGS

    for slug in EXPECTED_SLUGS:
        detail = client.get(f"/api/v1/demos/{slug}")
        assert detail.status_code == 200, detail.text
        body = detail.json()
        assert body["demo"]["slug"] == slug
        assert body["payload_preview"]["disciplines"]
        assert all(item["template_id"] for item in body["payload_preview"]["disciplines"])


def test_open_demo_creates_draft():
    response = client.post("/api/v1/demos/residencia-alto-padrao-alphaville-go/open-draft")
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["draft_id"]
    draft = client.get(f"/api/v1/drafts/{data['draft_id']}")
    assert draft.status_code == 200
    payload = draft.json()["payload"]
    assert payload["enterprise"]["name"]
    assert len(payload["disciplines"]) >= 9


def test_generate_demo_bundles_for_both_projects():
    for slug in sorted(EXPECTED_SLUGS):
        response = client.post(f"/api/v1/demos/{slug}/generate-bundle")
        assert response.status_code == 200, f"{slug}: {response.text[:800]}"
        assert response.headers.get("content-type", "").startswith("application/")
        assert response.content[:2] == b"PK"  # ZIP magic


def test_exemplos_page_renders():
    response = client.get("/exemplos")
    assert response.status_code == 200
    assert b"Projetos-modelo" in response.content or b"projetos-modelo" in response.content.lower()
