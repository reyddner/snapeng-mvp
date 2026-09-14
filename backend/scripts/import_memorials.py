"""
Script principal para importar memoriais e gerar templates
Arquivo: backend/scripts/import_memorials.py
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

# Adicionar diretório backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Importar módulos do mesmo diretório
scripts_dir = Path(__file__).parent

# Importar find_memorials
spec_finder = importlib.util.spec_from_file_location("find_memorials", scripts_dir / "find_memorials.py")
find_memorials = importlib.util.module_from_spec(spec_finder)
spec_finder.loader.exec_module(find_memorials)
MemorialFinder = find_memorials.MemorialFinder

# Importar analyze_memorial
spec_analyzer = importlib.util.spec_from_file_location("analyze_memorial", scripts_dir / "analyze_memorial.py")
analyze_memorial = importlib.util.module_from_spec(spec_analyzer)
spec_analyzer.loader.exec_module(analyze_memorial)
MemorialAnalyzer = analyze_memorial.MemorialAnalyzer

# Importar generate_templates_from_memorials
spec_generator = importlib.util.spec_from_file_location("generate_templates_from_memorials", scripts_dir / "generate_templates_from_memorials.py")
generate_templates = importlib.util.module_from_spec(spec_generator)
spec_generator.loader.exec_module(generate_templates)
TemplateGenerator = generate_templates.TemplateGenerator


class MemorialImporter:
    """Orquestra busca, análise e geração de templates"""

    def __init__(self, root_path: str = "D:\\", max_files: int = None):
        self.finder = MemorialFinder(root_path)
        self.analyzer = MemorialAnalyzer()
        self.generator = TemplateGenerator()
        self.max_files = max_files
        self.templates_generated = []

    def import_memorials(self, output_dir: Path = None) -> List[Dict[str, Any]]:
        """
        Processa memoriais e gera templates
        
        Args:
            output_dir: Diretório para salvar templates (None = engineering_templates/)
            
        Returns:
            Lista de templates gerados
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "engineering_templates"
        
        print("=" * 80)
        print("IMPORTAÇÃO DE MEMORIAIS PARA TEMPLATES")
        print("=" * 80)
        print()
        
        # 1. Buscar arquivos
        print("ETAPA 1: Buscando arquivos de memoriais...")
        print("-" * 80)
        files = self.finder.search_files(max_files=self.max_files)
        
        if not files:
            print("\nNenhum arquivo encontrado. Encerrando.")
            return []
        
        print(f"\n{len(files)} arquivos encontrados.")
        print()
        
        # 2. Analisar e gerar templates
        print("ETAPA 2: Analisando memoriais e gerando templates...")
        print("-" * 80)
        
        success_count = 0
        error_count = 0
        
        for i, file_info in enumerate(files, 1):
            file_path = Path(file_info['path'])
            
            print(f"\n[{i}/{len(files)}] Processando: {file_path.name}")
            
            try:
                # Gerar template
                template = self.generator.generate_template(file_path)
                
                if template:
                    # Salvar template
                    output_path = self.generator.save_template(template, output_dir)
                    
                    self.templates_generated.append({
                        'template': template,
                        'source_file': str(file_path),
                        'output_file': str(output_path),
                        'status': 'success'
                    })
                    
                    success_count += 1
                    print(f"  [OK] Template gerado: {template['name']}")
                    print(f"    Salvo em: {output_path}")
                else:
                    error_count += 1
                    print(f"  [ERRO] Nao foi possivel gerar template")
                    
            except Exception as e:
                error_count += 1
                print(f"  [ERRO] Erro: {e}")
                continue
        
        # 3. Resumo
        print()
        print("=" * 80)
        print("RESUMO")
        print("=" * 80)
        print(f"Arquivos processados: {len(files)}")
        print(f"Templates gerados com sucesso: {success_count}")
        print(f"Erros: {error_count}")
        print()
        
        # Agrupar por categoria
        by_category = {}
        for item in self.templates_generated:
            category = item['template']['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item['template']['name'])
        
        if by_category:
            print("Templates por categoria:")
            for category, names in sorted(by_category.items()):
                print(f"  {category}: {len(names)} templates")
                for name in names[:3]:  # Mostrar primeiros 3
                    print(f"    - {name}")
                if len(names) > 3:
                    print(f"    ... e mais {len(names) - 3}")
            print()
        
        return self.templates_generated

    def load_to_database(self):
        """
        Carrega templates gerados no banco de dados
        """
        if not self.templates_generated:
            print("Nenhum template para carregar no banco.")
            return
        
        print("\nETAPA 3: Carregando templates no banco de dados...")
        print("-" * 80)
        
        try:
            from app.core.database import SessionLocal, Base, engine
            from app.models.template import EngineeringTemplate, TemplateCategory
        except ImportError as e:
            print(f"Erro ao importar módulos do banco: {e}")
            print("Pulando carregamento no banco. Use --skip-db para evitar este erro.")
            return
        
        # Garantir que tabelas existem
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        loaded_count = 0
        
        try:
            for item in self.templates_generated:
                template_data = item['template']
                
                # Verificar se já existe
                existing = db.query(EngineeringTemplate).filter(
                    EngineeringTemplate.name == template_data['name']
                ).first()
                
                if existing:
                    print(f"  [SKIP] {template_data['name']} ja existe, pulando...")
                    continue
                
                # Mapear categoria
                category_map = {
                    'civil_infra': TemplateCategory.CIVIL_INFRA,
                    'edificacoes': TemplateCategory.EDIFICACOES,
                    'estruturas': TemplateCategory.ESTRUTURAS,
                    'pontes_viadutos': TemplateCategory.PONTES,
                    'eletrica': TemplateCategory.ELETRICA,
                    'hidraulica': TemplateCategory.HIDRAULICA,
                }
                
                category_enum = category_map.get(
                    template_data['category'], 
                    TemplateCategory.CIVIL_INFRA
                )
                
                # Criar template no banco
                db_template = EngineeringTemplate(
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
                
                db.add(db_template)
                loaded_count += 1
                print(f"  [OK] {template_data['name']} carregado no banco")
            
            db.commit()
            print(f"\n{loaded_count} templates carregados no banco de dados!")
            
        except Exception as e:
            db.rollback()
            print(f"\nErro ao carregar no banco: {e}")
            raise
        finally:
            db.close()


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Importar memoriais e gerar templates')
    parser.add_argument('--max-files', type=int, default=None,
                       help='Número máximo de arquivos para processar')
    parser.add_argument('--skip-db', action='store_true',
                       help='Não carregar templates no banco de dados')
    parser.add_argument('--path', type=str, default='D:\\',
                       help='Caminho raiz para busca (padrão: D:\\)')
    
    args = parser.parse_args()
    
    # Criar importador
    importer = MemorialImporter(root_path=args.path, max_files=args.max_files)
    
    # Importar memoriais
    templates = importer.import_memorials()
    
    # Carregar no banco (se não pular)
    if templates and not args.skip_db:
        try:
            importer.load_to_database()
        except Exception as e:
            print(f"\nAVISO: Erro ao carregar no banco: {e}")
            print("Templates foram salvos em arquivos JSON, mas não no banco.")


if __name__ == "__main__":
    main()

