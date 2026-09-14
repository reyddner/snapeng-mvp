"""
Script para carregar templates iniciais no banco de dados
Arquivo: backend/scripts/load_templates.py
"""

import sys
import json
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Importar após adicionar ao path
try:
    from app.config import settings
    from app.core.database import SessionLocal, Base, engine
    from app.models.template import EngineeringTemplate, TemplateCategory
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print(f"Path atual: {sys.path}")
    raise

# Em desenvolvimento local o script pode criar tabelas.
# Em produção o schema deve vir exclusivamente do Alembic.
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

def load_template_from_json(json_path: Path):
    """Carrega um template de um arquivo JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_templates():
    """Carrega todos os templates JSON para o banco"""
    db = SessionLocal()
    
    try:
        # Diretório de templates
        templates_dir = Path(__file__).parent.parent.parent / "engineering_templates"
        
        # Mapear categorias
        category_map = {
            'civil': TemplateCategory.CIVIL_INFRA,
            'civil_infra': TemplateCategory.CIVIL_INFRA,
            'edificacoes': TemplateCategory.EDIFICACOES,
            'estruturas': TemplateCategory.ESTRUTURAS,
            'eletrica': TemplateCategory.ELETRICA,
            'hidraulica': TemplateCategory.HIDRAULICA,
            'pontes_viadutos': TemplateCategory.PONTES,
        }
        
        templates_loaded = 0
        
        # Percorrer subdiretórios
        for category_dir in templates_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            category_name = category_dir.name
            category_enum = category_map.get(category_name)
            
            if not category_enum:
                print(f"[AVISO] Categoria '{category_name}' nao mapeada, pulando...")
                continue
            
            # Carregar templates JSON
            for json_file in category_dir.glob("*.json"):
                try:
                    template_data = load_template_from_json(json_file)
                    
                    # Verificar se já existe
                    existing = db.query(EngineeringTemplate).filter(
                        EngineeringTemplate.name == template_data['name']
                    ).first()
                    
                    if existing:
                        print(f"[SKIP] Template '{template_data['name']}' ja existe, pulando...")
                        continue
                    
                    # Criar template
                    template = EngineeringTemplate(
                        name=template_data['name'],
                        description=template_data.get('description', ''),
                        category=category_enum,
                        subcategory=template_data.get('subcategory', ''),
                        structure=template_data,
                        variables=template_data.get('variables', []),
                        is_public=1,
                        downloads=0,
                        rating=0
                    )
                    
                    db.add(template)
                    templates_loaded += 1
                    print(f"[OK] Template '{template_data['name']}' carregado!")
                    
                except Exception as e:
                    print(f"[ERRO] Erro ao carregar {json_file}: {e}")
        
        db.commit()
        print(f"\n[SUCESSO] {templates_loaded} templates carregados com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERRO] {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Carregando templates iniciais...\n")
    load_templates()

