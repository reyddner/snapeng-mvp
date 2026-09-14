"""
Schemas Pydantic para Project
Arquivo: backend/app/schemas/project.py
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    template_id: int
    project_data: Dict[str, Any]  # Dados preenchidos pelo usuário


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_data: Optional[Dict[str, Any]] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    id: int
    project_data: Dict[str, Any]
    status: ProjectStatus
    owner_id: int
    template_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

