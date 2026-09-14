# Deploy — SNAPENG

Guia mínimo e atualizado para subir o produto com o fluxo público de memoriais.

## Pré-requisitos

- Docker + Docker Compose **ou**
- Python 3.11+ e Node 20+ (apenas se for buildar CSS localmente)
- PostgreSQL 15+ (produção)

## Variáveis obrigatórias em produção

```bash
DEBUG=false
DATABASE_URL=postgresql://snapeng_user:snapeng_pass@postgres:5432/snapeng
SECRET_KEY=<chave-aleatoria-com-32+-caracteres>
ALLOWED_ORIGINS=https://seu-dominio.com
```

Com `DEBUG=false`, valores de `SECRET_KEY` contendo `dev-secret`, `change-this` ou `changeme` são rejeitados.

Copie `.env.example` para `.env` e ajuste.

## Opção A — Docker Compose (recomendado)

Na raiz do projeto:

```bash
docker compose up --build -d
```

Sobe:

- `postgres`
- `redis`
- `api` (migrations via Alembic no entrypoint + Uvicorn na porta 8000)

Healthcheck: `GET /health`

Aplicação: [http://localhost:8000](http://localhost:8000)  
Docs interativas: habilitadas apenas com `DEBUG=true` (desabilitadas em produção)

## Opção B — Local com SQLite (desenvolvimento)

```bash
pip install -r requirements.txt
cd backend
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Smoke check (raiz do projeto):

```bash
python scripts/smoke_check.py
```

Com `DEBUG=true`, o app pode criar tabelas via `create_all` e usa Tailwind CDN.

## CSS (Tailwind)

Em desenvolvimento (`DEBUG=true`): CDN.

Em produção (`DEBUG=false`): CSS compilado em `frontend/static/css/tailwind.css`.

Build local:

```bash
npm install
npm run build:css
```

O `Dockerfile` já executa esse build no estágio `assets`.

## Migrations

Sempre a partir de `backend/`:

```bash
cd backend
alembic upgrade head
alembic current
```

Modelos registrados no Alembic: `User`, `EngineeringTemplate`, `Project`, `Document`, `MemorialDraft`.

## Carregar templates de engenharia

Após o banco estar migrado:

```bash
cd backend
python scripts/load_templates.py
```

No Docker, o entrypoint já executa o seed quando `SEED_TEMPLATES=true` (padrão no compose).

## Checklist pós-deploy

1. `GET /health` → `healthy` com `checks.database=ok`
2. Abrir `/memorials/new` e criar rascunho
3. Preencher disciplina e gerar ZIP
4. Confirmar que CSS compilado carrega (sem CDN) com `DEBUG=false`
5. Confirmar que `SECRET_KEY` de produção está definida
6. Confirmar que `/api/docs` responde 404 com `DEBUG=false`

## O que ainda não faz parte do deploy mínimo

- Stripe / S3 / Celery
- Rate limit distribuído (Redis) — hoje o limite é em memória por processo
- Observabilidade (Sentry/APM)

## Hardening recomendado para compose

- Mantenha `POSTGRES_PASSWORD` e `SECRET_KEY` vindos do `.env` (não hardcode em YAML).
- Exponha portas de banco/cache só em localhost (`127.0.0.1`) ou remova mapeamento em produção.
- Publique a API atrás de proxy reverso (Nginx/Traefik/Caddy) com TLS.
