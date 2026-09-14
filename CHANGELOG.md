# Changelog - SNAPENG

## [1.1.0] - 2026-09-09

### Adicionado
- Fluxo público multidisciplinar com rascunhos, compatibilidade e ZIP (DOCX + PDF via ReportLab)
- Ingestão de arquivos com sugestões e confirmação humana
- CI GitHub Actions executando a suíte pytest
- Healthcheck `/health` com verificação de banco
- Limite de payload em rascunhos públicos (512 KB)
- Rate limiting híbrido (Redis com fallback em memória)
- Cookies HttpOnly de sessão + endpoint `/auth/logout`
- CSP e headers básicos de segurança (Alpine self-hosted)
- Proteção server-side das rotas HTML `/dashboard` e `/editor`
- Script `scripts/smoke_check.py` para validação local sem Docker

### Segurança
- Substituição segura de placeholders (bloqueio de SSTI Jinja2)
- Endpoints públicos de template exigem `is_public=1`
- Access token com `type=access`; refresh rejeitado em rotas autenticadas
- Docs/OpenAPI desabilitados quando `DEBUG=false`
- Compose: portas em localhost e credenciais via variáveis de ambiente

### Alterado
- STATUS consolidado (removidas seções contraditórias do checklist antigo)

## [1.0.0] - 2025-11-25

### Adicionado
- Autenticação JWT (registro, login, refresh)
- CRUD de Templates, Projects e Documents
- Geração DOCX, motor de templates, frontend HTMX/Alpine/Tailwind
- Landing, dashboard, editor básico, login/registro
- Scripts de importação de memoriais e scraping auxiliar

## Próximas versões

### [1.2.0] - Planejado
- Remover tokens do localStorage no editor legado; Alpine self-hosted com SRI

### [1.3.0] - Planejado
- IA completa (Claude), validação avançada de normas

### [1.4.0] - Planejado
- Stripe, planos Free/Pro/Enterprise, armazenamento S3