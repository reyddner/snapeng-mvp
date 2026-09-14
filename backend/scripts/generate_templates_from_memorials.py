"""
Gera templates JSON a partir de memoriais analisados
Arquivo: backend/scripts/generate_templates_from_memorials.py
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import importlib.util

# Importar analyze_memorial do mesmo diretório
scripts_dir = Path(__file__).parent
spec = importlib.util.spec_from_file_location("analyze_memorial", scripts_dir / "analyze_memorial.py")
analyze_memorial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_memorial)
MemorialAnalyzer = analyze_memorial.MemorialAnalyzer


class TemplateGenerator:
    """Gera templates JSON a partir de memoriais"""

    def __init__(self):
        self.analyzer = MemorialAnalyzer()

    def create_variable_schema(self, variable_name: str, content: str) -> Dict[str, Any]:
        """
        Cria schema de variável baseado no nome e contexto
        
        Args:
            variable_name: Nome da variável
            content: Conteúdo onde a variável aparece
            
        Returns:
            Schema da variável
        """
        # Mapear tipos comuns
        type_mapping = {
            'localizacao': 'text',
            'local': 'text',
            'endereco': 'text',
            'extensao': 'number',
            'comprimento': 'number',
            'largura': 'number',
            'altura': 'number',
            'area': 'number',
            'volume': 'number',
            'cbr': 'number',
            'fck': 'number',
            'tensao': 'number',
            'corrente': 'number',
            'potencia': 'number',
            'data': 'date',
        }
        
        var_lower = variable_name.lower()
        var_type = 'text'  # Default
        
        # Verificar tipo
        for key, vtype in type_mapping.items():
            if key in var_lower:
                var_type = vtype
                break
        
        # Verificar se parece número no conteúdo
        if var_type == 'text':
            # Buscar padrões numéricos próximos à variável
            if any(word in content.lower() for word in ['km', 'metros', 'm²', 'm³', '%', 'mpa', 'kv', 'kva']):
                var_type = 'number'
        
        # Criar label amigável
        label = variable_name.replace('_', ' ').title()
        
        return {
            'name': variable_name.lower(),
            'type': var_type,
            'label': label,
            'required': True  # Por padrão, todas são obrigatórias
        }

    def generate_template_structure(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera estrutura de template a partir da análise
        
        Args:
            analysis: Análise do memorial
            
        Returns:
            Estrutura de template no formato SNAPENG
        """
        # Nome do template baseado no nome do arquivo
        template_name = Path(analysis['filename']).stem
        template_name = template_name.replace('_', ' ').title()
        
        # Criar seções
        sections = []
        for section in analysis['sections']:
            # Processar conteúdo para identificar variáveis
            content = section['content']
            
            # Substituir variáveis por placeholders {{variavel}}
            processed_content = content
            variables_in_section = []
            
            for var in analysis['variables']:
                # Buscar ocorrências da variável no conteúdo
                var_patterns = [
                    var.upper(),
                    var.lower(),
                    var.title(),
                    var.replace('_', ' ').title(),
                    var.replace('_', ' ').upper()
                ]
                
                for pattern in var_patterns:
                    if pattern in content:
                        # Substituir por placeholder
                        placeholder = f"{{{{{var.lower()}}}}}"
                        processed_content = processed_content.replace(pattern, placeholder)
                        if var.lower() not in variables_in_section:
                            variables_in_section.append(var.lower())
            
            sections.append({
                'title': section['title'],
                'content': processed_content,
                'variables': variables_in_section
            })
        
        # Criar schema de variáveis
        variables_schema = []
        for var in analysis['variables']:
            # Buscar contexto da variável no conteúdo completo
            full_content = ' '.join([s['content'] for s in analysis['sections']])
            var_schema = self.create_variable_schema(var, full_content)
            variables_schema.append(var_schema)
        
        # Criar template
        template = {
            'name': template_name,
            'description': f"Template gerado automaticamente a partir de {analysis['filename']}",
            'category': analysis['category'],
            'subcategory': '',  # Pode ser preenchido manualmente depois
            'version': '1.0',
            'sections': sections,
            'variables': variables_schema,
            'normas': analysis['norms'],
            'calculations': [],  # Cálculos podem ser adicionados manualmente
            'metadata': {
                'source_file': analysis['filename'],
                'generated_at': datetime.now().isoformat(),
                'generated_by': 'import_memorials.py'
            }
        }
        
        return template

    def generate_template(self, file_path: Path) -> Dict[str, Any]:
        """
        Gera template completo a partir de um arquivo
        
        Args:
            file_path: Caminho do arquivo de memorial
            
        Returns:
            Template gerado
        """
        # Analisar memorial
        analysis = self.analyzer.analyze(file_path)
        if not analysis:
            return None
        
        # Gerar estrutura de template
        template = self.generate_template_structure(analysis)
        
        return template

    def save_template(self, template: Dict[str, Any], output_dir: Path):
        """
        Salva template em arquivo JSON
        
        Args:
            template: Template a ser salvo
            output_dir: Diretório de saída
        """
        # Criar diretório se não existir
        category_dir = output_dir / template['category']
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome do arquivo
        filename = template['name'].lower().replace(' ', '_') + '.json'
        filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
        
        output_path = category_dir / filename
        
        # Salvar
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        return output_path


def main():
    """Teste do gerador"""
    generator = TemplateGenerator()
    
    # Exemplo de uso
    test_file = Path("D:/test_memorial.docx")
    if test_file.exists():
        template = generator.generate_template(test_file)
        if template:
            output_dir = Path(__file__).parent.parent.parent / "engineering_templates"
            output_path = generator.save_template(template, output_dir)
            print(f"Template salvo em: {output_path}")
    else:
        print("Arquivo de teste não encontrado.")


if __name__ == "__main__":
    main()

