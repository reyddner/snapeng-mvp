"""
Schemas Pydantic para EngineeringTemplate
Arquivo: backend/app/schemas/template.py
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.template import TemplateCategory
from app.schemas.multidisciplinary import ProfessionalProfile


class TemplateOption(BaseModel):
    value: str
    label: str


class TemplateQuestion(BaseModel):
    name: str
    type: str = "text"
    label: Optional[str] = None
    description: Optional[str] = None
    placeholder: Optional[str] = None
    unit: Optional[str] = None
    required: bool = False
    default: Any = None
    options: Optional[List[TemplateOption]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    group: Optional[str] = None
    depends_on: Optional[Dict[str, Any]] = None


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: TemplateCategory
    subcategory: Optional[str] = None


class TemplateCreate(TemplateBase):
    structure: Dict[str, Any]  # Estrutura JSON do template
    variables: Optional[List[TemplateQuestion]] = None
    is_public: int = 1


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TemplateCategory] = None
    subcategory: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    variables: Optional[List[TemplateQuestion]] = None
    is_public: Optional[int] = None


class TemplateResponse(TemplateBase):
    id: int
    structure: Dict[str, Any]
    variables: Optional[List[Dict[str, Any]]] = None
    author_id: Optional[int] = None
    is_public: int
    downloads: int
    rating: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplatePreviewRequest(BaseModel):
    project_data: Dict[str, Any]


class MemorialGenerationRequest(TemplatePreviewRequest):
    project_name: str
    description: Optional[str] = None
    professional: Optional[ProfessionalProfile] = None


class TemplatePreviewResponse(BaseModel):
    template_id: int
    template_name: str
    valid: bool
    errors: Dict[str, str]
    content: Dict[str, Any]

