#!/bin/sh
set -e

cd /app/backend

echo "Aplicando migrations Alembic..."
alembic upgrade head

if [ "${SEED_TEMPLATES:-true}" = "true" ]; then
  echo "Carregando templates de engenharia (idempotente)..."
  python scripts/load_templates.py || echo "Aviso: seed de templates falhou; a API ainda sobe."
fi

echo "Iniciando SNAPENG..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
