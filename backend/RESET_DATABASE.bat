@echo off
echo ════════════════════════════════════════════════════════════
echo RESETANDO BANCO DE DADOS SNAPENG
echo ════════════════════════════════════════════════════════════
echo.
echo Este script vai:
echo 1. Deletar o banco de dados antigo
echo 2. Criar as tabelas com a migration corrigida
echo 3. Carregar templates de exemplo
echo.
pause

cd backend

echo.
echo [1/3] Deletando banco antigo...
if exist snapeng.db del /F snapeng.db
if exist sql_app.db del /F sql_app.db
echo [OK] Bancos deletados

echo.
echo [2/3] Criando tabelas com migration corrigida...
python scripts\reset_and_load.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao criar banco
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando templates...
python -c "from app.core.database import SessionLocal; from app.models.template import EngineeringTemplate; db = SessionLocal(); print(f'Templates no banco: {db.query(EngineeringTemplate).count()}'); db.close()"

echo.
echo ════════════════════════════════════════════════════════════
echo BANCO RESETADO COM SUCESSO!
echo ════════════════════════════════════════════════════════════
echo.
echo Agora inicie o servidor:
echo   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
echo.
pause

