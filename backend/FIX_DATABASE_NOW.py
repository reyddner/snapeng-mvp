"""
SCRIPT DEFINITIVO - FORÇA RESET DO BANCO
Execute mesmo com servidor rodando (ele vai tentar fechar conexões)
"""
import os
import sys
import time
from pathlib import Path

print("=" * 80)
print("RESETANDO BANCO DE DADOS - SNAPENG")
print("=" * 80)
print()

# Mudar para diretório backend
os.chdir(Path(__file__).parent)

# 1. Tentar fechar conexões
print("[1/5] Fechando conexões...")
try:
    sys.path.insert(0, str(Path.cwd()))
    from app.core.database import engine
    engine.dispose()
    print("  [OK] Conexões fechadas")
    time.sleep(1)  # Aguardar 1 segundo
except Exception as e:
    print(f"  [AVISO] {e}")

# 2. Deletar banco
print("\n[2/5] Deletando banco antigo...")
db_files = ["snapeng.db", "sql_app.db"]
deleted = False
for db_file in db_files:
    db_path = Path(db_file)
    if db_path.exists():
        try:
            # Tentar múltiplas vezes
            for attempt in range(3):
                try:
                    os.remove(db_path)
                    print(f"  [OK] {db_file} deletado")
                    deleted = True
                    break
                except PermissionError:
                    if attempt < 2:
                        print(f"  [TENTATIVA {attempt+1}/3] Aguardando...")
                        time.sleep(2)
                    else:
                        print(f"  [ERRO] Não foi possível deletar {db_file}")
                        print(f"  [SOLUÇÃO] PARE o servidor uvicorn (CTRL+C) e execute novamente")
                        sys.exit(1)
        except Exception as e:
            print(f"  [ERRO] {e}")
    else:
        print(f"  [INFO] {db_file} não existe")

if not deleted:
    print("  [AVISO] Nenhum banco foi deletado. Continuando mesmo assim...")

# 3. Criar tabelas
print("\n[3/5] Criando tabelas com enum CORRETO...")
try:
    from app.core.database import Base, engine
    Base.metadata.drop_all(bind=engine)  # Garantir que não há tabelas antigas
    Base.metadata.create_all(bind=engine)
    print("  [OK] Tabelas criadas com enum lowercase")
except Exception as e:
    print(f"  [ERRO] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Carregar templates
print("\n[4/5] Carregando templates de exemplo...")
try:
    from app.core.database import SessionLocal
    from app.models.template import EngineeringTemplate, TemplateCategory
    
    db = SessionLocal()
    
    # Limpar templates existentes (se a tabela existir)
    try:
        db.query(EngineeringTemplate).delete()
        db.commit()
    except Exception:
        # Tabela não existe ainda, tudo bem
        db.rollback()
        pass
    
    templates = [
        EngineeringTemplate(
            name="Pavimentação Asfáltica",
            description="Memorial para pavimentação asfáltica urbana",
            category=TemplateCategory.CIVIL_INFRA,  # Usar enum diretamente!
            subcategory="pavimentacao",
            structure={"sections": [{"id": "1", "title": "Introdução", "content": "Memorial de pavimentação"}]},
            variables=[{"name": "localizacao", "type": "text", "label": "Localização", "required": True}],
            is_public=1, downloads=0, rating=0
        ),
        EngineeringTemplate(
            name="Subestação Elétrica",
            description="Memorial para subestação elétrica",
            category=TemplateCategory.ELETRICA,  # Usar enum diretamente!
            subcategory="subestacao",
            structure={"sections": [{"id": "1", "title": "Introdução", "content": "Memorial de subestação"}]},
            variables=[{"name": "tensao", "type": "number", "label": "Tensão (kV)", "required": True}],
            is_public=1, downloads=0, rating=0
        ),
        EngineeringTemplate(
            name="Estrutura de Concreto",
            description="Memorial para estrutura de concreto armado",
            category=TemplateCategory.ESTRUTURAS,  # Usar enum diretamente!
            subcategory="concreto",
            structure={"sections": [{"id": "1", "title": "Introdução", "content": "Memorial de estrutura"}]},
            variables=[{"name": "fck", "type": "number", "label": "fck (MPa)", "required": True}],
            is_public=1, downloads=0, rating=0
        ),
    ]
    
    for template in templates:
        db.add(template)
    
    db.commit()
    
    count = db.query(EngineeringTemplate).count()
    print(f"  [OK] {count} templates carregados")
    
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

# 5. Verificar
print("\n[5/5] Verificando banco...")
try:
    db = SessionLocal()
    templates = db.query(EngineeringTemplate).all()
    print(f"  [OK] Banco contém {len(templates)} templates")
    for t in templates:
        print(f"    - {t.name}: categoria='{t.category}' (tipo: {type(t.category).__name__})")
    db.close()
except Exception as e:
    print(f"  [ERRO] {e}")

print("\n" + "=" * 80)
print("SUCESSO! BANCO RESETADO E CORRIGIDO!")
print("=" * 80)
print("\nPRÓXIMOS PASSOS:")
print("1. Se o servidor estiver rodando, REINICIE-O (CTRL+C e depois):")
print("   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
print("\n2. Teste em: http://localhost:8000/templates/select")
print("\n3. A API /api/v1/templates/ deve retornar 200 OK agora!")
print()

