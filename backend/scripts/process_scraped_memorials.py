"""
Processa memoriais baixados de prefeituras e gera templates
Arquivo: backend/scripts/process_scraped_memorials.py

Integra scraping → validação → análise → geração de templates
"""

import sys
import importlib.util
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos do mesmo diretório usando importlib
scripts_dir = Path(__file__).parent

# Importar validate_downloaded_files
spec_validator = importlib.util.spec_from_file_location(
    "validate_downloaded_files", scripts_dir / "validate_downloaded_files.py"
)
validate_downloaded_files = importlib.util.module_from_spec(spec_validator)
spec_validator.loader.exec_module(validate_downloaded_files)
FileValidator = validate_downloaded_files.FileValidator

# Importar analyze_memorial
spec_analyzer = importlib.util.spec_from_file_location(
    "analyze_memorial", scripts_dir / "analyze_memorial.py"
)
analyze_memorial = importlib.util.module_from_spec(spec_analyzer)
spec_analyzer.loader.exec_module(analyze_memorial)
MemorialAnalyzer = analyze_memorial.MemorialAnalyzer

# Importar generate_templates_from_memorials
spec_generator = importlib.util.spec_from_file_location(
    "generate_templates_from_memorials", scripts_dir / "generate_templates_from_memorials.py"
)
generate_templates_from_memorials = importlib.util.module_from_spec(spec_generator)
spec_generator.loader.exec_module(generate_templates_from_memorials)
TemplateGenerator = generate_templates_from_memorials.TemplateGenerator


class ScrapedMemorialProcessor:
    """Processa memoriais baixados de prefeituras"""

    def __init__(self):
        self.validator = FileValidator()
        self.analyzer = MemorialAnalyzer()
        self.generator = TemplateGenerator()

    def process_quarantine(self, quarantine_dir: Path, output_dir: Path = None):
        """
        Processa arquivos em quarentena validados
        
        Args:
            quarantine_dir: Diretório de quarentena
            output_dir: Diretório para templates gerados
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "engineering_templates"
        
        print("=" * 80)
        print("PROCESSAMENTO DE MEMORIAIS BAIXADOS")
        print("=" * 80)
        
        # 1. Validar arquivos
        print("\nETAPA 1: Validando arquivos...")
        print("-" * 80)
        validation_results = self.validator.validate_quarantine(quarantine_dir)
        
        valid_files = [r for r in validation_results if r['valid']]
        print(f"\nArquivos válidos: {len(valid_files)}")
        print(f"Arquivos rejeitados: {len(validation_results) - len(valid_files)}")
        
        if not valid_files:
            print("Nenhum arquivo válido para processar.")
            return
        
        # 2. Analisar e gerar templates
        print("\nETAPA 2: Analisando e gerando templates...")
        print("-" * 80)
        
        templates_generated = 0
        
        for result in valid_files:
            file_path = Path(result['file_path'])
            print(f"\nProcessando: {file_path.name}")
            
            try:
                # Gerar template
                template = self.generator.generate_template(file_path)
                
                if template:
                    # Adicionar metadados de origem
                    template['metadata']['source'] = 'prefeitura_scraping'
                    template['metadata']['validated'] = True
                    template['metadata']['file_hash'] = result.get('hash')
                    
                    # Salvar template
                    output_path = self.generator.save_template(template, output_dir)
                    templates_generated += 1
                    print(f"  [OK] Template gerado: {template['name']}")
                else:
                    print(f"  [ERRO] Nao foi possivel gerar template")
                    
            except Exception as e:
                print(f"  [ERRO] {e}")
        
        print(f"\n{'='*80}")
        print(f"Templates gerados: {templates_generated}")
        print(f"{'='*80}")


def main():
    """Função principal"""
    quarantine_dir = Path(__file__).parent.parent.parent / "downloads" / "prefeituras" / "quarantine"
    
    if not quarantine_dir.exists():
        print(f"Diretório de quarentena não encontrado: {quarantine_dir}")
        print("Execute primeiro o scraper: python scripts/scrape_prefeituras.py")
        return
    
    processor = ScrapedMemorialProcessor()
    processor.process_quarantine(quarantine_dir)


if __name__ == "__main__":
    main()

