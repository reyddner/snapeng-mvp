# STATUS — SNAP ENG (atualizado 2026-09-14)

**MVP publico em estabilizacao.** Dominio proprio / billing fora de escopo agora.

## Corrigido nesta rodada (P0–P4 + estabilizacao)
1. Catalogo publico limpo (allowlist + purge) — sem protocolo/proposta/OCR/apostila
2. `GET /api/v1/templates/` so retorna templates `assess_template.ready`
3. Fluxo template unico cria **draft no servidor** e abre `/memorials/draft/{id}`
4. Formulario: **nome primeiro**; demais dados do projeto no **final** (UI + bloco no DOCX/PDF)
5. `load_templates.py` ignora `_inbox` e exige ready; `purge_bad_templates.py` para producao
6. Testes: catalogo limpo + create draft + ordem do formulario
7. **SQLite unico** na raiz do repo (`app/core/paths.py`) — fim do bug de dois `snapeng.db`
8. Editor permite editar **responsavel tecnico** no final; bloqueia gerar com "A definir"
9. **Projetos-modelo publicos** em `/exemplos` (residencia ~312 m² + galpao ~1050 m²)
10. API `GET/POST /api/v1/demos/*` — listar, abrir no editor, baixar ZIP real
11. Dashboard com `x-init`, link aos exemplos e auto-claim se usuario logado ao criar
12. Fix template pavimentacao: `penetracao_asfalto` como texto (ex. 50/70)

## Loop MVP
1. `/exemplos` para ver qualidade real **ou** `/memorials/new` para criar o seu
2. Preencher, validar, gerar ZIP (DOCX/PDF) — plantas CAD/DWG fora do MVP
3. Claim (automatico se logado) → `/editor/{id}` → Dashboard

## Projetos-modelo
| Slug | Tipologia | Disciplinas |
|------|-----------|-------------|
| `residencia-alto-padrao-alphaville-go` | Residencia alto padrao ~312 m² | 9 |
| `galpao-logistico-aparecida-go` | Galpao logistico ~1050 m² | 11 |

Juntos cobrem **todas as 12 disciplinas** do questionario. Geracao E2E coberta em `tests/test_demos.py`.

## Producao — limpar catalogo contaminado
```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\python.exe backend\scripts\purge_bad_templates.py
.\.venv\Scripts\python.exe backend\scripts\load_templates.py
```
O SQLite local e **sempre** `{raiz}/snapeng.db` (nao depende se voce sobe o uvicorn da raiz ou de `backend/`).
O arquivo legado `backend/snapeng.db` pode ser apagado apos o purge/load na raiz.

## Validar
```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
.\.venv\Scripts\python.exe scripts\smoke_check.py
```

## Ainda aberto (pos-MVP)
- Dominio proprio, Stripe, S3, Sentry, Docker compose no host
- Geracao de plantas CAD/DWG (explicitamente fora do escopo atual)
