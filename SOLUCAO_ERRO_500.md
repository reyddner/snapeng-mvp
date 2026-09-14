# 🔴 SOLUÇÃO PARA ERRO 500 - API /api/v1/templates/

## ⚠️ PROBLEMA
O banco de dados `snapeng.db` tem enum **UPPERCASE** (antigo), mas o código espera **lowercase** (novo).

**Erro:** `LookupError: 'templatecategory.civil_infra' is not among the defined enum values`

---

## ✅ SOLUÇÃO (3 PASSOS)

### **PASSO 1: PARAR O SERVIDOR**
No terminal onde o uvicorn está rodando:
```
Pressione: CTRL + C
```

### **PASSO 2: RESETAR O BANCO**
No PowerShell, execute:
```powershell
cd backend
python FIX_DATABASE_NOW.py
```

### **PASSO 3: REINICIAR O SERVIDOR**
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🎯 RESULTADO ESPERADO

Após executar os 3 passos:
- ✅ API `/api/v1/templates/` retorna **200 OK**
- ✅ 3 templates aparecem na página
- ✅ Erro 500 desaparece

---

## 📋 COMANDOS COMPLETOS (COPIE E COLE)

```powershell
# 1. Pare o servidor (CTRL+C no terminal do uvicorn)

# 2. Execute estes comandos:
cd "C:\Users\Vorthys.VORTHYS\OneDrive\Documentos\GitHub\SNAP ENG\backend"
python FIX_DATABASE_NOW.py

# 3. Reinicie o servidor:
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## ❓ SE AINDA DER ERRO

Se o script `FIX_DATABASE_NOW.py` falhar ao deletar o banco:

1. **Feche TODOS os terminais** que possam estar usando o banco
2. **Feche o Cursor/VS Code** temporariamente
3. **Execute novamente:** `python FIX_DATABASE_NOW.py`
4. **Reabra o Cursor** e reinicie o servidor

---

## ✅ VERIFICAÇÃO

Após executar, teste:
- http://localhost:8000/templates/select
- Deve mostrar 3 templates (não mais erro 500)

