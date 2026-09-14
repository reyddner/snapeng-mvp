# Documentação da API - SNAPENG

## Base URL

```
http://localhost:8000/api/v1
```

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Para acessar endpoints protegidos, inclua o token no header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Autenticação

#### POST `/auth/register`
Registra um novo usuário.

**Request Body:**
```json
{
  "email": "engenheiro@example.com",
  "password": "senha123",
  "full_name": "João Silva",
  "crea": "CREA-GO 123456"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "engenheiro@example.com",
  "full_name": "João Silva",
  "crea": "CREA-GO 123456",
  "is_active": true,
  "plan": "free"
}
```

#### POST `/auth/login`
Realiza login e retorna tokens.

**Request Body (form-data):**
```
username: engenheiro@example.com
password: senha123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### POST `/auth/refresh`
Renova tokens usando refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### GET `/auth/me`
Retorna informações do usuário autenticado.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "engenheiro@example.com",
  "full_name": "João Silva",
  "crea": "CREA-GO 123456"
}
```

### Templates

#### GET `/templates`
Lista templates disponíveis.

**Query Parameters:**
- `skip` (int): Número de registros para pular (default: 0)
- `limit` (int): Limite de registros (default: 100)
- `category` (str): Filtrar por categoria

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Pavimentação Asfáltica",
    "category": "civil_infra",
    "description": "..."
  }
]
```

#### GET `/templates/{template_id}`
Obtém um template específico.

#### GET `/templates/{template_id}/questionnaire`
Retorna as perguntas e lacunas necessárias para iniciar um memorial. Este endpoint é público durante a fase inicial do produto.

#### POST `/templates/{template_id}/preview`
Valida as respostas do questionário e retorna o memorial renderizado para revisão, sem criar usuário ou projeto.

**Request Body:**
```json
{
  "project_data": {
    "localizacao": "Rua Principal, Centro",
    "extensao": 2.5
  }
}
```

#### POST `/templates/{template_id}/generate`
Gera um arquivo DOCX diretamente a partir das respostas válidas, sem autenticação ou persistência. O salvamento permanente será conectado posteriormente ao fluxo de conta.

**Request Body:**
```json
{
  "project_name": "Pavimentação Rua Principal",
  "description": "Memorial inicial",
  "project_data": {
    "localizacao": "Rua Principal, Centro",
    "extensao": 2.5
  }
}
```

#### POST `/templates`
Cria um novo template (requer autenticação).

#### PUT `/templates/{template_id}`
Atualiza um template (requer autenticação, apenas autor).

#### DELETE `/templates/{template_id}`
Deleta um template (requer autenticação, apenas autor).

### Projetos

#### GET `/projects`
Lista projetos do usuário autenticado.

**Headers:** `Authorization: Bearer <token>`

#### GET `/projects/{project_id}`
Obtém um projeto específico.

#### POST `/projects`
Cria um novo projeto.

**Request Body:**
```json
{
  "name": "Pavimentação Rua Principal",
  "description": "...",
  "template_id": 1,
  "project_data": {
    "tipo_obra": "pavimentação asfáltica",
    "localizacao": "Rua Principal, Centro",
    "extensao": 2.5,
    "cbr_campo": 12
  }
}
```

#### PUT `/projects/{project_id}`
Atualiza um projeto.

#### DELETE `/projects/{project_id}`
Deleta um projeto.

### Documentos

#### GET `/documents/project/{project_id}`
Lista documentos gerados de um projeto.

#### POST `/documents/generate/{project_id}`
Gera documento a partir de um projeto.

**Query Parameters:**
- `format` (str): Formato do documento (DOCX, PDF, HTML)

**Response:** Arquivo binário para download

### IA

#### POST `/ai/suggest-content`
Sugere conteúdo para uma seção usando IA.

**Request Body:**
```json
{
  "section_title": "1. OBJETO",
  "context": {
    "tipo_obra": "pavimentação asfáltica",
    "local": "Rua Principal"
  },
  "template_type": "pavimentacao_asfaltica"
}
```

#### POST `/ai/validate-norm`
Valida conformidade com normas técnicas.

**Request Body:**
```json
{
  "content": "Texto do memorial...",
  "applicable_norms": ["NBR 15115", "NBR 7207"]
}
```

### Questionarios por disciplina

#### GET `/questionnaires`
Lista as disciplinas disponiveis para iniciar um memorial.

#### GET `/questionnaires/{discipline}`
Retorna as perguntas-chave, tipos de resposta, unidades e opcoes da disciplina. Disciplinas iniciais:

- `eletrica`
- `hidraulica`
- `pluvial`
- `sanitario`
- `spda`
- `corpo_bombeiros`
- `arquitetura`
- `estrutura_metalica`
- `estrutura_concreto`
- `fundacoes`

Esses questionarios sao publicos durante a fase inicial. A autenticacao sera adicionada depois que o fluxo de preenchimento, preview e geracao estiver validado.

### Empreendimentos multidisciplinares

### Rascunhos públicos

#### POST `/drafts`
Cria um rascunho temporário de empreendimento sem autenticação. O prazo padrão é de 7 dias, limitado a 30 dias.

#### GET `/drafts/{draft_id}`
Recupera um rascunho ativo.

#### PATCH `/drafts/{draft_id}`
Atualiza os dados do empreendimento, disciplinas, modo ou profissional.

#### DELETE `/drafts/{draft_id}`
Exclui o rascunho.

O formulário `/memorials/new` cria automaticamente um rascunho e guarda o `draft_id` no navegador para a próxima etapa do preenchimento.
O preenchimento das disciplinas continua em `/memorials/draft/{draft_id}`.

#### POST `/memorials/plan`
Cria um plano de trabalho em memoria, sem autenticação. O plano permite gerar uma disciplina, várias disciplinas separadamente ou um documento combinado.

Modos aceitos: `individual`, `combined` e `both`.

O cadastro profissional aceita nome, título, CREA/UF, ART, RRT, empresa e demais dados que devem aparecer no bloco técnico do documento. Isso ainda não representa uma assinatura eletrônica juridicamente válida; essa etapa dependerá de um provedor certificado.

#### POST `/memorials/generate-bundle`
Gera um arquivo ZIP com os memoriais selecionados. Com `mode=individual`, retorna um documento por disciplina; com `mode=combined`, retorna um documento único; com `mode=both`, retorna os dois formatos.

#### POST `/memorials/compatibility`
Verifica conflitos entre dados compartilhados do empreendimento e dados específicos das disciplinas antes da geração.

As regras determinísticas por disciplina detectam pendências objetivas, como ausência de sondagem para fundações, dados operacionais de gerador, análise de risco do SPDA e parâmetros de tratamento sanitário. Elas não substituem cálculo, aprovação do órgão competente ou responsabilidade de profissional habilitado.

#### GET `/memorials/template-options/{discipline}`
Lista os templates geradores compatíveis com uma disciplina. Templates sem seções, placeholders declarados ou cálculos válidos não são oferecidos para geração e permanecem como material de referência.

A entrada web pública para esse fluxo está disponível em `/memorials/new`.

### Ingestão de arquivos

#### POST `/ingestion/extract`
Extrai texto de PDF, DOCX ou TXT (máx. 10 MB) para revisão humana.

**Request:** `multipart/form-data` com:
- `file` (obrigatório)
- `disciplines` (opcional, CSV: `eletrica,spda`) — ativa heurísticas do questionário

**Response:** `200 OK`
```json
{
  "filename": "memorial.pdf",
  "extension": ".pdf",
  "text": "...",
  "suggestions": [
    {"field": "uf", "label": "UF", "value": "GO", "target": "shared", "confidence": "probable"},
    {"field": "potencia_instalada", "value": 85.5, "target": "discipline", "discipline": "eletrica"}
  ],
  "status": "pending_confirmation"
}
```

As sugestões só entram no rascunho após confirmação no editor (`/memorials/draft/{draft_id}`), persistidas em `source_documents`.

#### POST `/memorials/generate-bundle`
Gera ZIP com DOCX e PDF (individuais e/ou combinado, conforme `mode`).

## Códigos de Status

- `200 OK` - Sucesso
- `201 Created` - Recurso criado
- `204 No Content` - Sucesso sem conteúdo
- `400 Bad Request` - Requisição inválida
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro do servidor
- `503 Service Unavailable` - Serviço indisponível (ex: IA não configurada)

## Documentação Interativa

Acesse a documentação interativa Swagger em:
```
http://localhost:8000/api/docs
```

Ou ReDoc em:
```
http://localhost:8000/api/redoc
```

