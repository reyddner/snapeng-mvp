# Guia de Deploy - SNAPENG

## Pré-requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis (opcional, para Celery)
- Conta AWS/Cloudflare (para S3/R2)
- Conta Stripe (para pagamentos)
- Conta Anthropic (para IA)

## Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/snapeng

# Security
SECRET_KEY=your-secret-key-min-32-chars

# AI Services
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=snapeng-documents

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@snapeng.com.br
```

## Deploy Local

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

Com Docker:
```bash
docker-compose up -d postgres redis
```

Ou instalar PostgreSQL localmente.

### 3. Executar Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Iniciar Servidor

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Deploy em Produção

### Opção 1: Railway

1. Conecte repositório GitHub ao Railway
2. Configure variáveis de ambiente
3. Railway detecta automaticamente e faz deploy

### Opção 2: Render

1. Crie novo Web Service no Render
2. Conecte repositório
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Adicione PostgreSQL e Redis como serviços
5. Configure variáveis de ambiente

### Opção 3: Fly.io

1. Instale Fly CLI
2. Execute `fly launch`
3. Configure `fly.toml`:
```toml
[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  internal_port = 8000
  protocol = "tcp"
```

4. Configure secrets:
```bash
fly secrets set DATABASE_URL=...
fly secrets set SECRET_KEY=...
```

### Opção 4: Docker

1. Crie `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build e run:
```bash
docker build -t snapeng .
docker run -p 8000:8000 --env-file .env snapeng
```

## Configuração do Banco de Dados

### PostgreSQL

1. Criar database:
```sql
CREATE DATABASE snapeng;
```

2. Executar migrations:
```bash
cd backend
alembic upgrade head
```

### Backup

Configure backup automático:
```bash
# Backup diário
pg_dump snapeng > backup_$(date +%Y%m%d).sql
```

## SSL/HTTPS

### Let's Encrypt (Nginx)

1. Instale Certbot
2. Configure Nginx como reverse proxy
3. Obtenha certificado:
```bash
certbot --nginx -d snapeng.com.br
```

### Cloudflare

1. Configure DNS no Cloudflare
2. Ative SSL/TLS (Full)
3. Configure proxy reverso se necessário

## Monitoramento

### Logs

Configure logging estruturado:
```python
# Em produção, usar serviços como:
# - Sentry (erros)
# - DataDog (métricas)
# - Logtail (logs)
```

### Health Check

Endpoint disponível:
```
GET /health
```

## Performance

### Cache

Configure Redis para cache:
```python
# Cache de templates e dados frequentes
```

### CDN

Configure CDN para assets estáticos:
- Cloudflare
- AWS CloudFront
- Vercel

## Segurança em Produção

1. **HTTPS obrigatório**
2. **SECRET_KEY forte** (mínimo 32 caracteres aleatórios)
3. **CORS restrito** (apenas domínios permitidos)
4. **Rate limiting** (FastAPI-Limiter)
5. **Backup diário** do banco
6. **Logs de auditoria**
7. **2FA opcional** (TOTP)

## Troubleshooting

### Erro de conexão com banco

Verifique `DATABASE_URL` e se o PostgreSQL está acessível.

### Erro de importação

Certifique-se de estar no diretório correto e que todas as dependências estão instaladas.

### Erro de migração

Execute `alembic current` para verificar estado atual.

### Erro de IA não configurada

Configure `ANTHROPIC_API_KEY` no `.env` ou desabilite endpoints de IA.

