"""
SNAPENG - Backend FastAPI
Arquivo: backend/app/main.py
"""

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import uvicorn
from pathlib import Path
from app.core.database import engine, Base, get_db
from app.core.dependencies import resolve_user_from_request
from app.config import settings

# Registrar todos os modelos antes de qualquer criação automática de tabelas.
from app.models.document import Document  # noqa: F401
from app.models.draft import MemorialDraft  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.template import EngineeringTemplate  # noqa: F401
from app.models.user import User  # noqa: F401

# Caminho absoluto para templates (relativo ao diretório raiz do projeto)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# O desenvolvimento local pode iniciar com SQLite vazio. Em produção, o schema
# deve ser criado exclusivamente pelo Alembic antes de iniciar a aplicação.
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="SNAPENG API",
    description="API para geração de memoriais descritivos de engenharia",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
)

# CORS
_cors_origins = ["*"] if settings.DEBUG else settings.allowed_origins_list
_cors_credentials = _cors_origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts_list,
    )


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    script_sources = ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
    style_sources = ["'self'", "'unsafe-inline'"]
    if settings.DEBUG:
        script_sources.append("https://cdn.tailwindcss.com")
        style_sources.append("https://cdn.tailwindcss.com")
    csp = (
        "default-src 'self'; "
        f"script-src {' '.join(script_sources)}; "
        f"style-src {' '.join(style_sources)}; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


# Templates Jinja2
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Montar arquivos estáticos
try:
    STATIC_DIR = BASE_DIR / "frontend" / "static"
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
except RuntimeError:
    # Se o diretório não existir ainda, não montar
    pass

from app.api.v1 import (
    ai,
    auth,
    demos,
    documents,
    drafts,
    ingestion,
    memorials,
    projects,
    questionnaires,
    templates as templates_api,
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(
    templates_api.router, prefix="/api/v1/templates", tags=["Templates"]
)
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projetos"])
app.include_router(
    documents.router, prefix="/api/v1/documents", tags=["Documentos"]
)
app.include_router(drafts.router, prefix="/api/v1/drafts", tags=["Rascunhos"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["IA Assistant"])
app.include_router(
    memorials.router,
    prefix="/api/v1/memorials",
    tags=["Memoriais"],
)
app.include_router(demos.router, prefix="/api/v1/demos", tags=["Projetos-modelo"])
app.include_router(
    questionnaires.router,
    prefix="/api/v1/questionnaires",
    tags=["Questionarios"],
)
app.include_router(
    ingestion.router,
    prefix="/api/v1/ingestion",
    tags=["Ingestão"],
)

# ROTAS DO FRONTEND (HTMX)


def _page(request: Request, name: str, **context):
    """Render Jinja no formato atual do Starlette (request primeiro)."""
    return templates.TemplateResponse(
        request,
        name,
        {"config": {"DEBUG": settings.DEBUG}, **context},
    )


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page pública"""
    return _page(
        request,
        "index.html",
        title="SNAPENG - Memoriais de Engenharia",
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard do usuário (requer sessão autenticada)."""
    user = resolve_user_from_request(request, db)
    if user is None:
        return RedirectResponse(url="/login?next=/dashboard", status_code=302)
    try:
        return _page(
            request,
            "dashboard.html",
            user={
                "name": user.full_name or user.email,
                "email": user.email,
            },
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        from fastapi.responses import JSONResponse
        import logging

        logging.error("Erro ao carregar dashboard: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Erro ao carregar dashboard",
                "message": (
                    "Ocorreu um erro interno. Tente novamente mais tarde."
                    if not settings.DEBUG
                    else str(e)
                ),
            },
        )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Página de registro"""
    return _page(request, "register.html")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return _page(request, "login.html")


@app.get("/templates/select", response_class=HTMLResponse)
async def select_template(request: Request):
    """Página de seleção de template"""
    return _page(request, "select_template.html")


@app.get("/memorials/new", response_class=HTMLResponse)
async def new_enterprise(request: Request):
    """Entrada publica para empreendimentos com uma ou varias disciplinas."""
    return _page(request, "new_enterprise.html")


@app.get("/exemplos", response_class=HTMLResponse)
@app.get("/demos", response_class=HTMLResponse)
async def demos_gallery(request: Request):
    """Galeria publica de projetos-modelo para demonstracao e validacao."""
    return _page(request, "demos.html")


@app.get("/memorials/draft/{draft_id}", response_class=HTMLResponse)
async def draft_editor(request: Request, draft_id: str):
    """Preenchimento publico das disciplinas de um rascunho."""
    return _page(
        request,
        "draft_editor.html",
        editor_mode="draft",
        draft_id=draft_id,
        project_id=0,
    )


@app.get("/memorial/new/{template_id}", response_class=HTMLResponse)
async def new_memorial(request: Request, template_id: int):
    """Página de criação de novo memorial"""
    return _page(request, "new_memorial.html", template_id=template_id)


@app.get("/editor/{project_id}", response_class=HTMLResponse)
async def editor(request: Request, project_id: int, db: Session = Depends(get_db)):
    """Editor autenticado: plano multidisciplinar completo ou editor legado."""
    from app.models.project import Project

    user = resolve_user_from_request(request, db)
    if user is None:
        return RedirectResponse(
            url=f"/login?next=/editor/{project_id}",
            status_code=302,
        )

    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None or (
        project.owner_id != user.id and not user.is_superuser
    ):
        return RedirectResponse(url="/dashboard", status_code=302)

    data = project.project_data or {}
    if data.get("kind") == "memorial_plan":
        return _page(
            request,
            "draft_editor.html",
            editor_mode="project",
            draft_id="",
            project_id=project_id,
        )
    return _page(request, "editor.html", project_id=project_id)


# Health check
@app.get("/health")
async def health_check():
    """Verifica processo e conectividade básica com o banco."""
    from fastapi.responses import JSONResponse
    from sqlalchemy import text

    from app.core.database import SessionLocal

    checks = {"api": "ok", "database": "unknown"}
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            checks["database"] = "ok"
        finally:
            db.close()
    except Exception:
        checks["database"] = "error"

    healthy = checks["database"] == "ok"
    payload = {
        "status": "healthy" if healthy else "degraded",
        "version": settings.APP_VERSION,
        "checks": checks,
    }
    return JSONResponse(status_code=200 if healthy else 503, content=payload)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload em desenvolvimento
    )

