#!/usr/bin/env bash
# Boot de producao (Render / Docker / local prod).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/backend"

export PYTHONPATH="${ROOT_DIR}/backend:${PYTHONPATH:-}"

echo "[snapeng] migrations..."
alembic upgrade head

if [ "${SEED_TEMPLATES:-true}" = "true" ]; then
  echo "[snapeng] seed templates..."
  python scripts/load_templates.py || echo "[snapeng] seed avisou/falhou; seguindo."
fi

PORT="${PORT:-8000}"
echo "[snapeng] uvicorn :${PORT}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
