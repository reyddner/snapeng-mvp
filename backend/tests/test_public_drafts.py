from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


def test_public_draft_lifecycle():
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
        created = client.post(
            "/api/v1/drafts",
            json={
                "enterprise": {"name": "Residencia Silva", "shared_data": {}},
                "disciplines": [{"discipline": "eletrica"}],
                "mode": "individual",
                "professional": {"full_name": "Ana Silva", "crea_number": "12345"},
                "ttl_days": 7,
            },
        )
        assert created.status_code == 201
        draft_id = created.json()["draft_id"]

        updated = client.patch(
            f"/api/v1/drafts/{draft_id}",
            json={"enterprise": {"name": "Residencia Silva Atualizada", "shared_data": {}}},
        )
        assert updated.status_code == 200
        assert updated.json()["payload"]["enterprise"]["name"] == "Residencia Silva Atualizada"

        fetched = client.get(f"/api/v1/drafts/{draft_id}")
        assert fetched.status_code == 200
        assert fetched.json()["draft_id"] == draft_id

        deleted = client.delete(f"/api/v1/drafts/{draft_id}")
        assert deleted.status_code == 204
        assert client.get(f"/api/v1/drafts/{draft_id}").status_code == 404
    finally:
        app.dependency_overrides.clear()
        session.close()
