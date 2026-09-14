"""Rascunhos publicos temporarios de empreendimentos."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from app.core.database import Base


class MemorialDraft(Base):
    __tablename__ = "memorial_drafts"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(String(64), unique=True, nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<MemorialDraft {self.draft_id}>"
