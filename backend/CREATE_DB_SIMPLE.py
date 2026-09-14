"""
Script simples para criar banco e templates
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import Base, engine, SessionLocal
from app.models.template import EngineeringTemplate, TemplateCategory
from app.models.user import User
from app.models.project import Project
from app.models.document import Document

print("=" * 80)
print("CRIANDO BANCO DE DADOS")
print("=" * 80)
print()

# Deletar banco se existir
db_path = Path(__file__).parent / "snapeng.db"
if db_path.exists():
    db_path.unlink()
    print("[OK] Banco antigo deletado")

# Criar todas as tabelas
print("\n[1/2] Criando tabelas...")
Base.metadata.create_all(bind=engine)
print("[OK] Tabelas criadas")

# Carregar templates
print("\n[2/2] Carregando templates...")
db = SessionLocal()

templates = [
    EngineeringTemplate(
        name="Pavimentação Asfáltica",
        description="Memorial para pavimentação asfáltica urbana",
        category=TemplateCategory.CIVIL_INFRA,
        subcategory="pavimentacao",
        structure={"sections": [{"id": "1", "title": "Introdução", "content": "Memorial de pavimentação"}]},
        variables=[{"name": "localizacao", "type": "text", "label": "Localização", "required": True}],
        is_public=1, downloads=0, rating=0
    ),
    EngineeringTemplate(
        name="Subestação Elétrica",
        description="Memorial para subestação elétrica",
        category=TemplateCategory.ELETRICA,
        subcategory="subestacao",
        structure={"sections": [{"id": "1", "title": "Introdução", "content": "Memorial de subestação"}]},
        variables=[{"name": "tensao", "type": "number", "label": "Tensão (kV)", "required": True}],
        is_public=1, downloads=0, rating=0
    ),
    EngineeringTemplate(
        name="Estrutura de Concreto",
        description="Memorial para estrutura de concreto armado",
        category=TemplateCategory.ESTRUTURAS,
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
print(f"[OK] {count} templates carregados")

for t in db.query(EngineeringTemplate).all():
    print(f"  - {t.name} (categoria: {t.category})")

db.close()

print("\n" + "=" * 80)
print("SUCESSO!")
print("=" * 80)

