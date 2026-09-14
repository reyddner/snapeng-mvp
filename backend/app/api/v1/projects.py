"""
Endpoints para CRUD de Projetos
Arquivo: backend/app/api/v1/projects.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.template import EngineeringTemplate
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Lista projetos do usuário autenticado

    Args:
        skip: Número de registros para pular
        limit: Limite de registros
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Lista de projetos
    """
    projects = (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Obtém um projeto específico

    Args:
        project_id: ID do projeto
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Projeto encontrado

    Raises:
        HTTPException: Se projeto não encontrado ou sem permissão
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este projeto",
        )

    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Cria um novo projeto

    Args:
        project_data: Dados do projeto
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Projeto criado

    Raises:
        HTTPException: Se template não encontrado
    """
    # Verificar se template existe
    template = (
        db.query(EngineeringTemplate)
        .filter(EngineeringTemplate.id == project_data.template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado",
        )

    db_project = Project(
        name=project_data.name,
        description=project_data.description,
        project_data=project_data.project_data,
        owner_id=current_user.id,
        template_id=project_data.template_id,
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza um projeto

    Args:
        project_id: ID do projeto
        project_data: Dados atualizados
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Projeto atualizado

    Raises:
        HTTPException: Se projeto não encontrado ou sem permissão
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar este projeto",
        )

    # Atualizar campos
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    if "status" in update_data:
        from datetime import datetime, timezone

        if project.status and str(project.status.value if hasattr(project.status, "value") else project.status) == "completed":
            if project.completed_at is None:
                project.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            project.completed_at = None

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Deleta um projeto

    Args:
        project_id: ID do projeto
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Raises:
        HTTPException: Se projeto não encontrado ou sem permissão
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar este projeto",
        )

    db.delete(project)
    db.commit()

    return None

