# Configuração do Tailwind CSS

## Desenvolvimento

Com `DEBUG=true`, o `base.html` usa o CDN do Tailwind.

## Produção

Com `DEBUG=false`, o `base.html` carrega `/static/css/tailwind.css` (compilado).

```bash
npm install
npm run build:css
```

Arquivos:

- entrada: `frontend/static/css/input.css`
- saída: `frontend/static/css/tailwind.css`
- config: `tailwind.config.js`

O `Dockerfile` já executa `npm run build:css` no estágio de assets.
