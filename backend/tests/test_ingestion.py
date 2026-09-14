"""Testes do endpoint publico de ingestao de documentos."""

from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_extract_txt_document():
    response = client.post(
        "/api/v1/ingestion/extract",
        files={"file": ("nota.txt", b"Memorial de referencia GO", "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "nota.txt"
    assert data["status"] == "pending_confirmation"
    assert "Memorial de referencia GO" in data["text"]


def test_extract_docx_document():
    buffer = BytesIO()
    document = Document()
    document.add_paragraph("Texto de memorial para revisao humana.")
    document.save(buffer)
    response = client.post(
        "/api/v1/ingestion/extract",
        files={
            "file": (
                "memorial.docx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["extension"] == ".docx"
    assert "revisao humana" in data["text"]


def test_extract_rejects_unsupported_format():
    response = client.post(
        "/api/v1/ingestion/extract",
        files={"file": ("foto.png", b"not-an-image", "image/png")},
    )
    assert response.status_code == 422


def test_extract_returns_field_suggestions():
    content = (
        b"Memorial descritivo\n"
        b"Municipio: Goiania\n"
        b"UF: GO\n"
        b"Localizacao: Rua das Flores, 100\n"
        b"Area construida 250,5 m2\n"
        b"Numero de pavimentos: 3\n"
    )
    response = client.post(
        "/api/v1/ingestion/extract",
        files={"file": ("obra.txt", content, "text/plain")},
    )
    assert response.status_code == 200
    suggestions = {item["field"]: item["value"] for item in response.json()["suggestions"]}
    assert suggestions["uf"] == "GO"
    assert suggestions["municipio"] == "Goiania"
    assert suggestions["area_construida"] == 250.5
    assert suggestions["numero_pavimentos"] == 3
    assert "localizacao" in suggestions


def test_extract_returns_discipline_suggestions():
    content = (
        b"Tipo de edificacao: Residencial multifamiliar\n"
        b"Potencia instalada: 85,5 kW\n"
        b"Tensao de fornecimento: 220/380\n"
        b"Gerador 150 kVA\n"
        b"Altura da edificacao: 18 m\n"
        b"Nivel de protecao: II\n"
        b"Populacao estimada: 120\n"
    )
    response = client.post(
        "/api/v1/ingestion/extract",
        data={"disciplines": "eletrica,spda,hidraulica"},
        files={"file": ("tec.txt", content, "text/plain")},
    )
    assert response.status_code == 200
    payload = response.json()
    by_key = {
        (item.get("discipline"), item["field"]): item["value"]
        for item in payload["suggestions"]
    }
    assert by_key[("eletrica", "potencia_instalada")] == 85.5
    assert by_key[("eletrica", "tensao_fornecimento")] == "220_380"
    assert by_key[("eletrica", "gerador")] == "sim"
    assert by_key[("eletrica", "potencia_gerador")] == 150.0
    assert by_key[("spda", "altura_edificacao")] == 18.0
    assert by_key[("spda", "nivel_protecao")] == "II"
    assert by_key[("hidraulica", "ocupacao_total")] == 120


def test_extract_returns_pluvial_fundacao_bombeiros_suggestions():
    content = (
        b"Area de contribuicao: 450 m2\n"
        b"Intensidade de chuva: 180 mm/h\n"
        b"Tempo de retorno: 25\n"
        b"Tipo de fundacao: Sapata isolada\n"
        b"Sondagem disponivel no terreno\n"
        b"Tensao admissivel do solo: 200 kPa\n"
        b"fck 30 MPa\n"
        b"Altura da edificacao: 12 m\n"
        b"Populacao prevista: 80\n"
        b"Risco de incendio: Medio\n"
        b"Ocupacao: Comercial\n"
    )
    response = client.post(
        "/api/v1/ingestion/extract",
        data={"disciplines": "pluvial,fundacoes,estrutura_concreto,corpo_bombeiros"},
        files={"file": ("mais.txt", content, "text/plain")},
    )
    assert response.status_code == 200
    by_key = {
        (item.get("discipline"), item["field"]): item["value"]
        for item in response.json()["suggestions"]
    }
    assert by_key[("pluvial", "area_contribuicao")] == 450.0
    assert by_key[("pluvial", "intensidade_chuva")] == 180.0
    assert by_key[("pluvial", "tempo_retorno")] == 25
    assert "sapata" in str(by_key[("fundacoes", "tipo_fundacao")]).lower()
    assert by_key[("fundacoes", "sondagem_disponivel")] == "sim"
    assert by_key[("fundacoes", "tensao_admissivel")] == 200.0
    assert by_key[("estrutura_concreto", "fck")] == 30.0
    assert by_key[("corpo_bombeiros", "altura_edificacao")] == 12.0
    assert by_key[("corpo_bombeiros", "populacao_bombeiros")] == 80
