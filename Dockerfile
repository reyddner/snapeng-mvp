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
    && apt-get install --no-install-recommends -y bash build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt ./
RUN pip install -r requirements-prod.txt

COPY backend ./backend
COPY frontend ./frontend
COPY engineering_templates ./engineering_templates
COPY scripts ./scripts
COPY --from=assets /build/frontend/static/css/tailwind.css ./frontend/static/css/tailwind.css

RUN chmod +x /app/scripts/start.sh /app/scripts/docker-entrypoint.sh \
    && useradd --create-home --shell /bin/bash snapeng \
    && chown -R snapeng:snapeng /app

USER snapeng
EXPOSE 8000
ENTRYPOINT ["bash", "/app/scripts/start.sh"]
