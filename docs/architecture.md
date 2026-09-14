# Arquitetura do Sistema - SNAPENG

## Visão Geral

O SNAPENG é uma aplicação SaaS full-stack construída com Python, seguindo uma arquitetura em camadas com separação clara de responsabilidades.

## Stack Tecnológica

### Backend
- **Framework**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Database**: PostgreSQL 15+ (com fallback para SQLite em dev)
- **Autenticação**: JWT (python-jose)
- **Validação**: Pydantic 2.5+

### Frontend
- **Templates**: Jinja2
- **Interatividade**: HTMX + Alpine.js
- **Estilização**: Tailwind CSS (via CDN)
- **Editor**: TipTap (planejado para Sprint 3)

### Serviços planejados
- **IA**: Anthropic Claude API (integração em evolução)
- **Storage**: AWS S3 ou Cloudflare R2
- **Email**: Resend
- **Pagamentos**: Stripe (planejado)
- **Cache/Task Queue**: Redis + Celery

## Estrutura de Camadas

```
┌─────────────────────────────────────┐
│         Frontend (HTMX)            │
│    Templates Jinja2 + Alpine.js    │
└──────────────┬────────────────────┘
               │
┌──────────────▼────────────────────┐
│      API Layer (FastAPI)           │
│  /api/v1/auth, templates, etc     │
└──────────────┬────────────────────┘
               │
┌──────────────▼────────────────────┐
│      Service Layer                 │
│  template_engine, document_gen,   │
│  ai_assistant, calculation_engine  │
└──────────────┬────────────────────┘
               │
┌──────────────▼────────────────────┐
│      Data Layer (SQLAlchemy)       │
│  Models: User, Template, Project   │
└──────────────┬────────────────────┘
               │
┌──────────────▼────────────────────┐
│      Database (PostgreSQL)         │
└────────────────────────────────────┘
```

## Fluxo de Dados

### Geração de Memorial

1. **Usuário preenche dados** → Frontend (HTMX)
2. **Dados enviados** → API `/api/v1/projects` (POST)
3. **Projeto criado** → Database (SQLAlchemy)
4. **Usuário solicita geração** → API `/api/v1/documents/generate`
5. **Template renderizado** → `TemplateEngine.render_template()`
6. **Documento gerado** → `DocumentGenerator.generate_docx()`
7. **Arquivo retornado** → Download pelo usuário

O fluxo principal do produto é a criação de memoriais. Integrações secundárias somente devem ser adicionadas depois que autenticação, projetos, templates e geração de documentos estiverem validados.

### Autenticação

1. **Login** → `/api/v1/auth/login`
2. **Validação** → `verify_password()`
3. **Tokens gerados** → `create_access_token()` + `create_refresh_token()`
4. **Token armazenado** → Frontend (localStorage)
5. **Requisições autenticadas** → Header `Authorization: Bearer <token>`
6. **Validação** → `get_current_user()` dependency

## Modelos de Dados

### User
- Informações do usuário
- Plano (free, professional, enterprise)
- Relacionamentos: Templates (author), Projects (owner)

### EngineeringTemplate
- Estrutura JSON do template
- Variáveis e cálculos
- Categoria e subcategoria
- Relacionamentos: User (author), Projects

### Project
- Dados preenchidos pelo usuário (JSON)
- Status (draft, in_progress, completed)
- Relacionamentos: User (owner), Template, Documents

### Document
- Arquivos gerados (DOCX, PDF, HTML)
- Metadados (filename, size, format)
- Relacionamento: Project

## Segurança

### Autenticação
- JWT com expiração curta (30 min access, 7 dias refresh)
- Hash de senha com bcrypt
- Refresh token para renovação

### Autorização
- Middleware de autenticação em rotas protegidas
- Verificação de propriedade (owner_id)
- Superuser para operações administrativas

### Validação
- Pydantic schemas para validação de entrada
- SQLAlchemy ORM previne SQL injection
- Jinja2 auto-escape previne XSS

## Escalabilidade

### Horizontal
- Stateless API (JWT tokens)
- Database connection pooling
- Redis para cache e sessões

### Vertical
- Async/await no FastAPI
- Processamento assíncrono com Celery
- Geração de documentos em background

## Próximas Melhorias

- WebSockets para colaboração em tempo real
- CDN para assets estáticos
- Load balancer para múltiplas instâncias
- Monitoring e logging estruturado (Sentry, DataDog)

