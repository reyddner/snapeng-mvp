"""
Script para corrigir categorias de templates (UPPERCASE -> lowercase)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.template import EngineeringTemplate

def fix_categories():
    db = SessionLocal()
    
    try:
        templates = db.query(EngineeringTemplate).all()
        print(f"Encontrados {len(templates)} templates no banco")
        
        updated = 0
        for template in templates:
            old_category = str(template.category)
            # Extrair apenas o valor do enum (depois do ponto)
            if '.' in old_category:
                new_category = old_category.split('.')[-1]
            else:
                new_category = old_category.lower()
            
            if old_category != new_category:
                template.category = new_category
                updated += 1
                print(f"  [UPDATE] {template.name}: {old_category} -> {new_category}")
        
        db.commit()
        print(f"\n[OK] {updated} templates atualizados com sucesso!")
        
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_categories()

