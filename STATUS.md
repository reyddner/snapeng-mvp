# Veredito atual (2026-09-10)

**MVP de piloto pronto** (fluxo publico + conta + edicao completa).  
Ainda nao e SaaS publico completo (billing, S3, APM).

### Loop MVP fechado
1. Criar empreendimento sem login (`/memorials/new`)
2. Preencher disciplinas, validar, gerar ZIP
3. **Salvar na minha conta** (`POST /drafts/{id}/claim`)
4. Reabrir no `/editor/{id}` com o **mesmo editor rico** (modo projeto)
5. Editar, autosave na conta, gerar de novo

### Hardening ja aplicado
- Rate limit sem bypass de X-Forwarded-For
- PyJWT + multipart atualizado
- Open redirect bloqueado; formulas AST; senha min. 8
- HSTS + TrustedHost em prod; JWT no body so em DEBUG

### Ainda aberto (pos-MVP)
1. Docker compose no host
2. Sentry
3. Stripe / S3 / IA avancada

## Validar

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
.\.venv\Scripts\python.exe scripts\smoke_check.py
```

50+ testes. Fluxo demo: memorial -> claim -> editor da conta.
