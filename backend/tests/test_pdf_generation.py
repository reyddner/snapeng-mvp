"""Testes da geracao de PDF."""

from app.services.document_generator import DocumentGenerator


def test_generate_pdf_returns_pdf_bytes():
    content = {
        "sections": [
            {
                "title": "Objeto",
                "content": "Memorial descritivo de instalacoes eletricas.",
                "subsections": [
                    {"title": "Escopo", "content": "Projeto completo da obra."}
                ],
            }
        ],
        "calculations": {
            "demanda": {"value": 12.5, "unit": "kW", "formula": "P * fp"}
        },
        "normas": ["NBR 5410", "NBR 5419"],
    }
    metadata = {
        "title": "MEMORIAL TESTE",
        "obra": "Obra Demo",
        "local": "Goiania/GO",
        "responsavel": "Eng. Teste",
        "crea": "12345/D-GO",
        "professional": {"full_name": "Eng. Teste", "company_name": "SNAPENG"},
    }
    pdf = DocumentGenerator().generate_pdf(content, metadata)
    data = pdf.getvalue()
    assert data.startswith(b"%PDF")
    assert len(data) > 500
