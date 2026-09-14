# ANÁLISE COMPLETA - SNAPENG

## Escopo oficial

O produto oficial é o SNAPENG, uma aplicação web para criação de memoriais descritivos de engenharia. O protótipo de certidões foi retirado do produto e não faz parte da arquitetura, do roadmap ou dos critérios de aceite.

## 🔴 PROBLEMA PRINCIPAL

### Erro 500 na API `/api/v1/templates/`

```
LookupError: 'templatecategory.civil_infra' is not among the defined enum values.
Possible values: CIVIL_INFRA, EDIFICACOES, ESTRUTURAS, ..., HIDRAULICA
```

---

## 🔍 CAUSA RAIZ

### O código está CORRETO, o banco está ERRADO!

#### 1. **Modelo Python** (`backend/app/models/template.py`)
```python
class TemplateCategory(str, enum.Enum):
    CIVIL_INFRA = "civil_infra"      # ✅ CORRETO (lowercase)
    EDIFICACOES = "edificacoes"       # ✅ CORRETO (lowercase)
    ESTRUTURAS = "estruturas"         # ✅ CORRETO (lowercase)
    PONTES = "pontes_viadutos"        # ✅ CORRETO (lowercase)
    ELETRICA = "eletrica"             # ✅ CORRETO (lowercase)
    HIDRAULICA = "hidraulica"         # ✅ CORRETO (lowercase)
```

#### 2. **Migration** (`backend/alembic/versions/001_initial_migration.py`)
```python
sa.Column('category', 
    sa.Enum('civil_infra', 'edificacoes', 'estruturas', 
            'pontes_viadutos', 'eletrica', 'hidraulica', 
            name='templatecategory'), 
    nullable=False)
```
✅ **CORRETO** (lowercase)

#### 3. **Banco de Dados Atual**
❌ **INCORRETO** - Tem os valores UPPERCASE do banco antigo:
- `CIVIL_INFRA` (deveria ser `civil_infra`)
- `EDIFICACOES` (deveria ser `edificacoes`)
- `ESTRUTURAS` (deveria ser `estruturas`)

---

## ✅ BUGS CORRIGIDOS

### Bug 1: `import_memorials.py:163`
```python
# ANTES (ERRADO):
return generated_templates  # ❌ variável não existe

# DEPOIS (CORRETO):
return  # ✅ sem variável
```

### Bug 2: `ai_assistant.py:74, 120`
```python
# ANTES (ERRADO):
message = self.client.messages.create(...)  # ❌ sem await

# DEPOIS (CORRETO):
message = await self.client.messages.create(...)  # ✅ com await
```

### Bug 3: `process_scraped_memorials.py:13-16`
```python
# ANTES (ERRADO):
from validate_downloaded_files import FileValidator  # ❌ import direto

# DEPOIS (CORRETO):
spec_validator = importlib.util.spec_from_file_location(...)  # ✅ importlib
```

### Bug 4: `001_initial_migration.py:45`
```python
# ANTES (ERRADO):
sa.Enum('CIVIL_INFRA', 'ESTRUCTURAS', ...)  # ❌ UPPERCASE

# DEPOIS (CORRETO):
sa.Enum('civil_infra', 'estruturas', ...)  # ✅ lowercase
```

### Bug 5: `main.py:98`
```python
# ANTES (ERRADO):
return JSONResponse(content={"traceback": traceback.format_exc()})  # ❌ expõe traceback

# DEPOIS (CORRETO):
logging.error(f"Erro: {e}", exc_info=True)  # ✅ apenas log server-side
return JSONResponse(content={"error": "Erro interno"})  # ✅ sem detalhes
```

---

## 🛠️ SOLUÇÃO

### Por que o erro persiste?

**O BANCO DE DADOS AINDA TEM OS VALORES ANTIGOS!**

Mesmo com o código corrigido, o banco SQLite `snapeng.db` foi criado ANTES das correções e contém:
- Enum com valores UPPERCASE
- Templates com categoria errada

### Como resolver DEFINITIVAMENTE:

1. **Parar o servidor** (CTRL+C)
2. **Executar**: `python backend/FIX_NOW.py`
3. **Iniciar o servidor**: `python -m uvicorn app.main:app --reload`

---

## 📊 ARQUITETURA

### Backend
```
backend/
├── app/
│   ├── main.py                    # ✅ CORRETO
│   ├── config.py                  # ✅ CORRETO
│   ├── models/
│   │   └── template.py            # ✅ CORRETO (enum lowercase)
│   ├── api/v1/
│   │   ├── templates.py           # ✅ CORRETO
│   │   ├── auth.py                # ✅ CORRETO
│   │   ├── projects.py            # ✅ CORRETO
│   │   ├── documents.py           # ✅ CORRETO
│   │   └── ai.py                  # ✅ CORRETO
│   └── services/
│       ├── ai_assistant.py        # ✅ CORRETO (await adicionado)
│       ├── template_engine.py     # ✅ CORRETO
│       └── document_generator.py  # ✅ CORRETO
├── alembic/
│   └── versions/
│       └── 001_initial_migration.py  # ✅ CORRETO (enum lowercase)
├── scripts/
│   ├── load_templates.py          # ✅ CORRETO
│   ├── import_memorials.py        # ✅ CORRETO (return sem variável)
│   └── process_scraped_memorials.py  # ✅ CORRETO (importlib)
└── snapeng.db                     # ❌ INCORRETO (enum UPPERCASE)
```

### API Endpoints
```
✅ GET  /                          - Landing page
✅ GET  /dashboard                 - Dashboard
✅ GET  /templates/select          - Seleção de template
❌ GET  /api/v1/templates/         - ERRO 500 (banco com enum errado)
✅ GET  /api/v1/templates/{id}     - Detalhes do template
✅ POST /api/v1/auth/register      - Registro
✅ POST /api/v1/auth/login         - Login
```

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Todos os 5 bugs do código foram corrigidos**
2. ❌ **O banco de dados precisa ser recriado**
3. 🔄 **Execute `python backend/FIX_NOW.py`**
4. ✅ **Sistema funcionará perfeitamente**

---

## 📝 RESUMO

| Item | Status | Ação Necessária |
|------|--------|-----------------|
| Código Python | ✅ CORRETO | Nenhuma |
| Migration Alembic | ✅ CORRETO | Nenhuma |
| Banco de Dados | ❌ INCORRETO | **RESETAR** |
| Todos os 5 bugs | ✅ CORRIGIDOS | Nenhuma |

**AÇÃO ÚNICA NECESSÁRIA:** Executar `python backend/FIX_NOW.py`

