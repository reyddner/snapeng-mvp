from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.template import EngineeringTemplate, TemplateCategory


def create_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    session.add(
        EngineeringTemplate(
            name="Template de teste",
            description="Template para o fluxo público",
            category=TemplateCategory.CIVIL_INFRA,
            structure={
                "sections": [
                    {
                        "title": "Objeto",
                        "content": "Obra em {{localizacao}} com {{extensao}} km.",
                    }
                ],
                "calculations": [],
                "normas": [],
            },
            variables=[
                {"name": "localizacao", "type": "text", "required": True},
                {"name": "extensao", "type": "number", "required": True, "min": 0},
            ],
        )
    )
    session.commit()
    app.dependency_overrides[get_db] = lambda: session
    return TestClient(app), session


def teardown_client(session):
    app.dependency_overrides.clear()
    session.close()


def test_questionnaire_preview_and_docx_without_authentication():
    client, session = create_test_client()
    try:
        questionnaire = client.get("/api/v1/templates/1/questionnaire")
        missing_field = client.post(
            "/api/v1/templates/1/preview",
            json={"project_data": {"localizacao": "Goiania"}},
        )
        document = client.post(
            "/api/v1/templates/1/generate",
            json={
                "project_name": "Teste Memorial",
                "project_data": {"localizacao": "Goiania", "extensao": 2},
            },
        )

        assert questionnaire.status_code == 200
        assert len(questionnaire.json()["questions"]) == 2
        assert missing_field.status_code == 200
        assert missing_field.json()["valid"] is False
        assert document.status_code == 200
        assert document.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert document.content[:2] == b"PK"
    finally:
        teardown_client(session)
