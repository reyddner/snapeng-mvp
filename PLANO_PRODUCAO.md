# Plano: Preparação da Plataforma SNAPENG para Produção

## Objetivo
Preparar a plataforma web SNAPENG para produção, corrigindo bugs críticos e concluindo o fluxo de criação de memoriais descritivos.

## Problemas Identificados

### Fluxo funcional prioritário
- Fundação de banco e migrations validada em SQLite limpo
- Questionário inicial por template, com perguntas, lacunas, unidades e regras de preenchimento
- Validação determinística dos dados antes de usar IA
- Cálculos técnicos do template antes da renderização
- Preview do memorial sem autenticação
- Geração DOCX sem autenticação
- Rascunho persistente e editor completo
- Autenticação, contas e permissões somente depois do fluxo anônimo estar validado

### 1. Bugs Críticos
- **Alpine.js Error**: validar a tela completa após a consolidação do questionário dinâmico
- **Editor incompleto**: Não carrega dados do projeto da API, usa token errado (`'token'` vs `'access_token'`)
- **Dashboard**: Não carrega projetos da API
- **Geração de documentos**: Endpoint existe mas precisa validação completa

### 2. Configuração de Produção
- **Tailwind CSS**: Usando CDN (não adequado para produção)
- **PostgreSQL**: Configuração necessária para produção
- **Variáveis de ambiente**: `.env.example` incompleto
- **Migrations**: Verificar se estão funcionando corretamente

### 3. Funcionalidades Faltantes
- Editor não carrega projeto existente
- Preview não funcional no editor
- Dashboard não lista projetos
- Geração de PDF não implementada (apenas DOCX)

## Etapas do Plano

### Fase 1: Correção de Bugs Críticos (Prioridade ALTA)

#### 1.1 Corrigir erro Alpine.js em `new_memorial.html`
- Adicionar verificação `x-show="template && template.variables"` antes do loop
- Garantir que `template` seja inicializado como `null` e só renderize após carregar

#### 1.2 Corrigir Editor (`editor.html`)
- Carregar projeto da API no `init()`
- Corrigir `localStorage.getItem('token')` para `'access_token'`
- Implementar carregamento de dados do projeto
- Adicionar tratamento de erros

#### 1.3 Implementar Dashboard funcional
- Carregar projetos da API `/api/v1/projects/`
- Exibir lista de projetos com ações (editar, gerar documento, deletar)
- Calcular estatísticas reais (total, em progresso, concluídos)

#### 1.4 Validar geração de documentos
- Testar endpoint `/api/v1/documents/generate/{project_id}`
- Verificar se DOCX é gerado corretamente
- Adicionar feedback visual durante geração

### Fase 2: Configuração de Produção (Prioridade ALTA)

#### 2.1 Instalar e configurar Tailwind CSS
- Criar `package.json` com scripts de build
- Criar `tailwind.config.js`
- Criar `frontend/static/css/input.css` com diretivas Tailwind
- Atualizar `base.html` para usar CSS compilado em produção
- Adicionar script de build no processo de deploy

#### 2.2 Configurar PostgreSQL
- Atualizar `config.py` para suportar PostgreSQL via `DATABASE_URL`
- Criar script de migração de SQLite para PostgreSQL (opcional)
- Atualizar `alembic.ini` se necessário
- Testar conexão e migrations com PostgreSQL

#### 2.3 Criar `.env.example` completo
- Incluir todas as variáveis necessárias
- Adicionar comentários explicativos
- Separar por seções (Database, Security, AI, Storage, etc)

#### 2.4 Verificar e corrigir migrations
- Testar `alembic upgrade head` com banco limpo
- Verificar se enum values estão corretos (lowercase)
- Garantir que todas as tabelas são criadas corretamente

### Fase 3: Melhorias de Funcionalidades (Prioridade MÉDIA)

#### 3.1 Melhorar Editor
- Implementar preview funcional (renderizar template com dados)
- Adicionar botão de salvar com feedback
- Adicionar validação de campos obrigatórios
- Melhorar UX com loading states

#### 3.2 Implementar geração de PDF
- Avaliar bibliotecas (WeasyPrint, ReportLab, ou DOCX->PDF)
- Implementar `generate_pdf()` em `document_generator.py`
- Adicionar endpoint para PDF
- Testar geração

#### 3.3 Melhorar autenticação
- Verificar se login/registro funcionam corretamente
- Adicionar proteção de rotas no frontend
- Implementar logout
- Adicionar redirecionamento após login

### Fase 4: Preparação para Deploy (Prioridade ALTA)

#### 4.1 Criar Dockerfile
- Dockerfile otimizado para produção
- Multi-stage build se necessário
- Configurar variáveis de ambiente

#### 4.2 Atualizar documentação
- Atualizar `README.md` com instruções de deploy
- Criar `DEPLOY.md` com guia passo a passo
- Documentar variáveis de ambiente
- Adicionar troubleshooting

#### 4.3 Criar scripts de deploy
- Script para build de assets (CSS)
- Script para migrations
- Script para inicialização do banco
- Script para verificação de saúde

#### 4.4 Configurar logging
- Configurar logging estruturado para produção
- Adicionar logs de erro e acesso
- Configurar níveis de log por ambiente

### Fase 5: Testes e Validação (Prioridade ALTA)

#### 5.1 Testar fluxo completo
- Registro de usuário
- Login
- Seleção de template
- Criação de projeto
- Edição de projeto
- Geração de DOCX
- Geração de PDF (se implementado)

#### 5.2 Testar com PostgreSQL
- Criar banco PostgreSQL
- Executar migrations
- Testar todas as operações CRUD
- Verificar performance

#### 5.3 Testar em ambiente de produção simulado
- Build de assets
- Verificar se CSS compilado funciona
- Testar com `DEBUG=False`
- Verificar CORS e segurança

## Arquivos a Modificar/Criar

### Modificar
- `frontend/templates/new_memorial.html` - Corrigir Alpine.js
- `frontend/templates/editor.html` - Implementar carregamento de projeto
- `frontend/templates/dashboard.html` - Carregar projetos da API
- `frontend/templates/base.html` - Configurar Tailwind CSS compilado
- `backend/app/config.py` - Melhorar configuração PostgreSQL
- `backend/app/services/document_generator.py` - Implementar PDF
- `backend/app/api/v1/documents.py` - Validar geração

### Criar
- `package.json` - Configuração Node.js para Tailwind
- `tailwind.config.js` - Configuração Tailwind
- `frontend/static/css/input.css` - CSS de entrada
- `.env.example` - Template de variáveis de ambiente
- `Dockerfile` - Container para produção
- `DEPLOY.md` - Guia de deploy
- `scripts/build.sh` - Script de build
- `scripts/deploy.sh` - Script de deploy

## Priorização

**CRÍTICO (Fazer primeiro):**
1. Correção de bugs Alpine.js e Editor
2. Configuração Tailwind CSS
3. Configuração PostgreSQL
4. Dashboard funcional

**IMPORTANTE (Fazer em seguida):**
5. Geração de PDF
6. Melhorias no Editor
7. Testes completos

**DESEJÁVEL (Se houver tempo):**
8. Melhorias de UX
9. Otimizações de performance
10. Documentação adicional

## Tempo Estimado

- Fase 1: 2-3 horas
- Fase 2: 2-3 horas
- Fase 3: 3-4 horas
- Fase 4: 2-3 horas
- Fase 5: 2-3 horas

**Total: 11-16 horas**

## Notas

- Focar primeiro nos bugs críticos que impedem uso básico
- Testar cada funcionalidade após implementação
- Manter compatibilidade com SQLite para desenvolvimento
- Garantir que migrations funcionem tanto com SQLite quanto PostgreSQL

