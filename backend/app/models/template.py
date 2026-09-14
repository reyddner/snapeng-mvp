"""
Model EngineeringTemplate - SQLAlchemy
Arquivo: backend/app/models/template.py
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class TemplateCategory(str, enum.Enum):
    CIVIL_INFRA = "civil_infra"
    EDIFICACOES = "edificacoes"
    ESTRUTURAS = "estruturas"
    PONTES = "pontes_viadutos"
    ELETRICA = "eletrica"
    HIDRAULICA = "hidraulica"


class EngineeringTemplate(Base):
    __tablename__ = "engineering_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(
        Enum(
            TemplateCategory,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=False,
    )
    subcategory = Column(String(100))

    # Estrutura do template em JSON
    structure = Column(JSON, nullable=False)
    # Exemplo: {
    #   "sections": [
    #     {
    #       "title": "1. OBJETO",
    #       "content": "Este memorial descreve {{tipo_obra}}...",
    #       "variables": ["tipo_obra", "localizacao"]
    #     }
    #   ],
    #   "calculations": [...],
    #   "normas": ["NBR 15115", "NBR 7207"]
    # }

    # Variáveis do template
    variables = Column(JSON)  # Lista de campos que o usuário preenche

    # Metadados
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_public = Column(Integer, default=1)  # 1=público, 0=privado
    downloads = Column(Integer, default=0)
    rating = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    author = relationship("User", back_populates="templates")
    projects = relationship("Project", back_populates="template")

    def __repr__(self):
        return f"<Template {self.name} ({self.category})>"

