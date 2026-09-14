"""
SCRIPT DEFINITIVO - RESOLVE O PROBLEMA DO ENUM DE UMA VEZ
Execute: python FIX_NOW.py
"""
import os
import sys
from pathlib import Path

print("=" * 80)
print("CORRIGINDO BANCO DE DADOS - SNAPENG")
print("=" * 80)
print()

# 1. Fechar todas as conexões
print("[1/4] Fechando conexões com o banco...")
try:
    from app.core.database import engine
    engine.dispose()
    print("  [OK] Conexões fechadas")
except Exception as e:
    print(f"  [AVISO] {e}")

# 2. Deletar banco antigo
print("\n[2/4] Deletando banco antigo...")
db_files = ["snapeng.db", "sql_app.db"]
for db_file in db_files:
    db_path = Path(__file__).parent / db_file
    if db_path.exists():
        try:
            os.remove(db_path)
            print(f"  [OK] {db_file} deletado")
        except Exception as e:
            print(f"  [ERRO] Não foi possível deletar {db_file}: {e}")
            print(f"  [SOLUÇÃO] Pare o servidor uvicorn e execute novamente")
            sys.exit(1)
    else:
        print(f"  [INFO] {db_file} não existe")

# 3. Criar tabelas
print("\n[3/4] Criando tabelas com enum CORRETO...")
try:
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print("  [OK] Tabelas criadas")
except Exception as e:
    print(f"  [ERRO] {e}")
    sys.exit(1)

# 4. Carregar templates de exemplo
print("\n[4/4] Carregando templates de exemplo...")
try:
    from app.core.database import SessionLocal
    from app.models.template import EngineeringTemplate
    
    db = SessionLocal()
    
    templates = [
        EngineeringTemplate(
            name="Pavimentação Asfáltica",
            description="Memorial para pavimentação asfáltica urbana",
            category="civil_infra",  # lowercase!
            subcategory="pavimentacao",
            structure={
                "sections": [
                    {"id": "1", "title": "Introdução", "content": "Memorial de pavimentação"}
                ]
            },
            variables=[
                {"name": "localizacao", "type": "text", "label": "Localização", "required": True}
            ],
            is_public=1, downloads=0, rating=0
        ),
        EngineeringTemplate(
            name="Subestação Elétrica",
            description="Memorial para subestação elétrica",
            category="eletrica",  # lowercase!
            subcategory="subestacao",
            structure={
                "sections": [
                    {"id": "1", "title": "Introdução", "content": "Memorial de subestação"}
                ]
            },
            variables=[
                {"name": "tensao", "type": "number", "label": "Tensão (kV)", "required": True}
            ],
            is_public=1, downloads=0, rating=0
        ),
        EngineeringTemplate(
            name="Estrutura de Concreto",
            description="Memorial para estrutura de concreto armado",
            category="estruturas",  # lowercase!
            subcategory="concreto",
            structure={
                "sections": [
                    {"id": "1", "title": "Introdução", "content": "Memorial de estrutura"}
                ]
            },
            variables=[
                {"name": "fck", "type": "number", "label": "fck (MPa)", "required": True}
            ],
            is_public=1, downloads=0, rating=0
        ),
    ]
    
    for template in templates:
        db.add(template)
    
    db.commit()
    
    # Verificar
    count = db.query(EngineeringTemplate).count()
    print(f"  [OK] {count} templates carregados")
    
    # Mostrar templates
    all_templates = db.query(EngineeringTemplate).all()
    print("\n  Templates no banco:")
    for t in all_templates:
        print(f"    - {t.name} (categoria: {t.category})")
    
    db.close()
    
except Exception as e:
    print(f"  [ERRO] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("SUCESSO! BANCO CORRIGIDO!")
print("=" * 80)
print("\nAgora inicie o servidor:")
print("  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
print("\nE teste em: http://localhost:8000/templates/select")
print()

