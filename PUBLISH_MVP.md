# Publicacao MVP (sem dominio proprio)

## Por que nao Vercel?

O SNAPENG e **FastAPI + Jinja + geracao DOCX/PDF + banco**.  
Vercel e otimizado para frontends serverless (Next.js). Neste stack:

- timeouts curtos quebram geracao de memorial/ZIP
- filesystem efemero (SQLite nao serve)
- WeasyPrint/ReportLab pesados nao encaixam bem

**Mesmo objetivo (URL publica gratis, sem dominio):** use **Render** ou **Railway**.

## 1) GitHub

```powershell
cd "C:\Users\Vorthys.VORTHYS\OneDrive\Documentos\GitHub\SNAP ENG"
gh auth login
gh repo create snapeng --public --source=. --remote=origin --push
```

## 2) Render (recomendado para este MVP)

1. Abra o link direto de Blueprint:
   https://dashboard.render.com/blueprints/new
2. Conecte o GitHub (se pedir) e selecione o repo **reyddner/snapeng-mvp**
3. Confirme o `render.yaml` e clique **Deploy Blueprint**
4. Aguarde o build (3–8 min). URL tipica: `https://snapeng-api.onrender.com`
5. Se a URL real for diferente, em Environment ajuste:
   - `ALLOWED_ORIGINS=https://SUA-URL.onrender.com`
   - `ALLOWED_HOSTS=.onrender.com,SUA-URL.onrender.com`

Health: `GET /health`  
App: `/` e `/memorials/new`

> Plano free do Render “dorme” apos inatividade (~15 min). O primeiro request pode demorar ~30–60s.

## 3) Alternativa Railway

1. https://railway.app → New Project → Deploy from GitHub
2. Selecione o repo e o `Dockerfile`
3. Adicione Postgres e vincule `DATABASE_URL`
4. Variaveis:
   - `DEBUG=false`
   - `SECRET_KEY=` (32+ chars aleatorios)
   - `ALLOWED_HOSTS=*`
   - `ALLOWED_ORIGINS=https://SEU-APP.up.railway.app`
   - `TRUST_PROXY_HEADERS=true`
   - `SEED_TEMPLATES=true`

## Variaveis obrigatorias

| Variavel | Exemplo |
|---|---|
| `DEBUG` | `false` |
| `SECRET_KEY` | chave aleatoria 32+ (sem `dev-secret`/`changeme`) |
| `DATABASE_URL` | Postgres do provedor |
| `ALLOWED_ORIGINS` | URL https do app |
| `ALLOWED_HOSTS` | host do app ou `*` |
| `TRUST_PROXY_HEADERS` | `true` atras do proxy do provedor |
