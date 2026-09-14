# SNAPENG - Plataforma SaaS para Memoriais Descritivos de Engenharia

Plataforma web para geração automatizada de memoriais descritivos de engenharia civil, elétrica, estruturas e infraestrutura.

## 📋 Sobre o Projeto

O SNAPENG automatiza a criação de memoriais técnicos de engenharia, reduzindo o tempo de elaboração de horas para minutos por meio de:

- **Templates pré-configurados** para diferentes áreas de engenharia
- **IA Generativa** para sugestões e geração de conteúdo
- **Cálculos automáticos** de dimensionamentos
- **Validação de normas** técnicas (NBR/ABNT)
- **Geração profissional** de documentos DOCX, com PDF no roadmap imediato
- **Projetos organizados** com acompanhamento de status
- **API REST** para integração com o frontend e futuras integrações

O produto é uma aplicação web para engenheiros, escritórios e equipes técnicas. O foco oficial do SNAPENG é a elaboração, validação e exportação de memoriais descritivos. IA avançada, PDF, colaboração, armazenamento externo e pagamentos serão liberados por etapas após a estabilização do fluxo principal.

## 🏗️ Arquitetura

### Stack Tecnológica

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: HTMX + Alpine.js + Tailwind CSS
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **IA**: Anthropic Claude API
- **Documentos**: python-docx, reportlab, weasyprint

### Estrutura do Projeto

```
snapeng/
├── backend/          # API FastAPI
├── frontend/         # Templates HTML + Static files
├── engineering_templates/  # Templates JSON de engenharia
└── docs/             # Documentação
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL 15+ (ou SQLite para desenvolvimento)
- Redis (opcional, para Celery)

### Setup Local

1. **Clone o repositório**

```bash
git clone <repository-url>
cd snapeng
```

2. **Crie um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**

```powershell
Copy-Item .env.example .env
# Edite o .env com suas configurações
```

5. **Configure o banco de dados**

Com Docker Compose:
```bash
docker-compose up -d postgres redis
```

Ou configure PostgreSQL localmente e atualize `DATABASE_URL` no `.env`.

6. **Execute as migrations**

```bash
cd backend
alembic upgrade head
```

7. **Inicie o servidor**

```bash
cd backend
uvicorn app.main:app --reload
```

O servidor estará disponível em `http://localhost:8000`

- API Docs: `http://localhost:8000/api/docs`
- Landing Page: `http://localhost:8000/`

## 📚 Documentação

- [Documentação da API](docs/api.md)
- [Arquitetura do Sistema](docs/architecture.md)
- [Guia de Deploy](docs/deployment.md)

## 🔍 Importar Memoriais Existentes

O SNAPENG pode importar memoriais do seu computador e gerar templates automaticamente:

```bash
# Buscar memoriais na unidade D:\
cd backend
python scripts/find_memorials.py

# Importar e gerar templates (exemplo: 50 arquivos)
python scripts/import_memorials.py --max-files 50

# Carregar templates no banco
python scripts/load_templates.py
```

**Resultado:** 291 arquivos encontrados na unidade D:\ | 17 templates gerados automaticamente

## 🧪 Testes

```bash
pytest backend/tests
```

## 🛠️ Desenvolvimento

### Estrutura de Branches

- `main` - Produção
- `develop` - Desenvolvimento
- `feature/*` - Novas features

### Code Style

O projeto usa Black para formatação:

```bash
black backend/
```

## 📊 Estatísticas do Projeto

- **Templates disponíveis:** 20+ (3 manuais + 17 gerados automaticamente)
- **Memoriais encontrados no computador:** 291 arquivos
- **Categorias:** Civil, Estruturas, Elétrica, Hidráulica, Edificações
- **Formatos de documentos:** DOCX e PDF (PDF em implementação)
- **Formatos de arquivos de referência:** DOCX, PDF e TXT

## 📝 Licença

Proprietário - Todos os direitos reservados

## 👥 Contato

Para dúvidas ou suporte, entre em contato através do email: suporte@snapeng.com.br

