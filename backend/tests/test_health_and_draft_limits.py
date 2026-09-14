from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.schemas.draft import MAX_DRAFT_PAYLOAD_BYTES


def test_health_reports_database_ok():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["checks"]["api"] == "ok"
    assert body["checks"]["database"] == "ok"


def test_draft_rejects_oversized_payload():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    app.dependency_overrides[get_db] = lambda: session

    try:
        client = TestClient(app)
        oversized_text = "x" * (MAX_DRAFT_PAYLOAD_BYTES + 1000)
        created = client.post(
            "/api/v1/drafts",
            json={
                "enterprise": {
                    "name": "Obra Grande",
                    "shared_data": {"notas": oversized_text},
                },
                "disciplines": [{"discipline": "eletrica"}],
                "mode": "individual",
                "ttl_days": 7,
            },
        )
        assert created.status_code == 422
    finally:
        app.dependency_overrides.clear()
        session.close()
