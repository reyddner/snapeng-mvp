"""
Script para resetar o banco e carregar templates simples
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, Base, engine
from app.models.template import EngineeringTemplate, TemplateCategory

# Garantir que as tabelas existam
Base.metadata.create_all(bind=engine)

def load_simple_templates():
    """Carrega templates simples de exemplo"""
    db = SessionLocal()
    
    try:
        # Template 1: Civil
        template1 = EngineeringTemplate(
            name="Pavimentação Asfáltica",
            description="Memorial para pavimentação asfáltica urbana",
            category="civil_infra",  # lowercase!
            subcategory="pavimentacao",
            structure={
                "sections": [
                    {
                        "id": "1",
                        "title": "Introdução",
                        "content": "Memorial descritivo de pavimentação asfáltica",
                        "subsections": []
                    },
                    {
                        "id": "2",
                        "title": "Localizção",
                        "content": "{{localizacao}}",
                        "subsections": []
                    },
                    {
                        "id": "3",
                        "title": "Especificações Técnicas",
                        "content": "Extensão: {{extensao}}m, Largura: {{largura}}m",
                        "subsections": []
                    }
                ]
            },
            variables=[
                {"name": "localizacao", "type": "text", "label": "Localização", "required": True},
                {"name": "extensao", "type": "number", "label": "Extensão (m)", "required": True},
                {"name": "largura", "type": "number", "label": "Largura (m)", "required": True}
            ],
            is_public=1,
            downloads=0,
            rating=0
        )
        
        # Template 2: Elétrica
        template2 = EngineeringTemplate(
            name="Subestação Elétrica",
            description="Memorial para subestação elétrica",
            category="eletrica",  # lowercase!
            subcategory="subestacao",
            structure={
                "sections": [
                    {
                        "id": "1",
                        "title": "Introdução",
                        "content": "Memorial descritivo de subestação elétrica",
                        "subsections": []
                    },
                    {
                        "id": "2",
                        "title": "Características",
                        "content": "Tensão: {{tensao}}kV, Potência: {{potencia}}MVA",
                        "subsections": []
                    }
                ]
            },
            variables=[
                {"name": "tensao", "type": "number", "label": "Tensão (kV)", "required": True},
                {"name": "potencia", "type": "number", "label": "Potência (MVA)", "required": True}
            ],
            is_public=1,
            downloads=0,
            rating=0
        )
        
        # Template 3: Estruturas
        template3 = EngineeringTemplate(
            name="Estrutura de Concreto Armado",
            description="Memorial para estrutura de concreto armado",
            category="estruturas",  # lowercase!
            subcategory="concreto_armado",
            structure={
                "sections": [
                    {
                        "id": "1",
                        "title": "Introdução",
                        "content": "Memorial descritivo de estrutura de concreto armado",
                        "subsections": []
                    },
                    {
                        "id": "2",
                        "title": "Materiais",
                        "content": "Concreto fck: {{fck}}MPa",
                        "subsections": []
                    }
                ]
            },
            variables=[
                {"name": "fck", "type": "number", "label": "Resistência fck (MPa)", "required": True}
            ],
            is_public=1,
            downloads=0,
            rating=0
        )
        
        # Adicionar ao banco
        db.add(template1)
        db.add(template2)
        db.add(template3)
        db.commit()
        
        print("[OK] 3 templates carregados com sucesso!")
        print("  - Pavimentacao Asfaltica (civil_infra)")
        print("  - Subestacao Eletrica (eletrica)")
        print("  - Estrutura de Concreto Armado (estruturas)")
        
    except Exception as e:
        db.rollback()
        print(f"[ERRO] {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Carregando templates...\n")
    load_simple_templates()

