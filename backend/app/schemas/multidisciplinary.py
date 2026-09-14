"""Contratos publicos para empreendimentos multidisciplinares."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemorialGenerationMode(str, Enum):
    INDIVIDUAL = "individual"
    COMBINED = "combined"
    BOTH = "both"


class ProfessionalProfile(BaseModel):
    full_name: str = Field(min_length=2)
    professional_title: str = "Engenheiro(a)"
    crea_number: Optional[str] = None
    crea_state: Optional[str] = None
    art_number: Optional[str] = None
    rrt_number: Optional[str] = None
    company_name: Optional[str] = None
    company_document: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    signature_date: Optional[str] = None
    signature_label: str = "Responsavel tecnico"


class EnterpriseData(BaseModel):
    name: str = Field(min_length=2)
    description: Optional[str] = None
    shared_data: Dict[str, Any] = Field(default_factory=dict)


class DisciplineSelection(BaseModel):
    discipline: str
    template_id: Optional[int] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class MemorialPlanRequest(BaseModel):
    enterprise: EnterpriseData
    disciplines: List[DisciplineSelection] = Field(min_length=1)
    mode: MemorialGenerationMode = MemorialGenerationMode.BOTH
    professional: Optional[ProfessionalProfile] = None


class MemorialPlanResponse(BaseModel):
    enterprise: EnterpriseData
    mode: MemorialGenerationMode
    disciplines: List[Dict[str, Any]]
    professional: Optional[ProfessionalProfile] = None
    signature_notice: str


class MemorialBundleRequest(MemorialPlanRequest):
    """Dados completos para gerar os memoriais selecionados."""
