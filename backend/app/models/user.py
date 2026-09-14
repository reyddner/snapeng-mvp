"""
Model User - SQLAlchemy
Arquivo: backend/app/models/user.py
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    crea = Column(String(50))  # CREA do engenheiro
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    plan = Column(String(50), default="free")  # free, professional, enterprise

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relacionamentos
    templates = relationship("EngineeringTemplate", back_populates="author")
    projects = relationship("Project", back_populates="owner")

    def __repr__(self):
        return f"<User {self.email}>"

