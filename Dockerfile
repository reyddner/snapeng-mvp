FROM node:20-alpine AS assets
WORKDIR /build
COPY package.json ./
COPY tailwind.config.js ./
COPY frontend/templates ./frontend/templates
COPY frontend/static/css/input.css ./frontend/static/css/input.css
RUN npm install && npm run build:css

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt ./
RUN pip install -r requirements-prod.txt

COPY backend ./backend
COPY frontend ./frontend
COPY engineering_templates ./engineering_templates
COPY --from=assets /build/frontend/static/css/tailwind.css ./frontend/static/css/tailwind.css
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh \
    && useradd --create-home --shell /bin/bash snapeng \
    && chown -R snapeng:snapeng /app

USER snapeng
WORKDIR /app/backend
EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]
