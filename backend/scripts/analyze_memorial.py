"""
Script para analisar estrutura e conteúdo de memoriais
Arquivo: backend/scripts/analyze_memorial.py
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from docx import Document
import json


class MemorialAnalyzer:
    """Analisa memoriais e extrai estrutura e variáveis"""

    def __init__(self):
        self.section_patterns = [
            r'^\d+[\.\)]\s*[A-ZÁÊÔÇ][^\.]+',  # 1. TÍTULO ou 1) TÍTULO
            r'^[A-ZÁÊÔÇ][A-ZÁÊÔÇ\s]+$',  # TÍTULO EM MAIÚSCULAS
        ]
        self.norm_pattern = r'(NBR|ABNT|ABNT NBR)\s*\d+[\.\-]?\d*'
        self.variable_patterns = [
            r'\{\{(\w+)\}\}',  # {{variavel}}
            r'\[(\w+)\]',  # [variavel]
            r'<(\w+)>',  # <variavel>
        ]

    def read_docx(self, file_path: Path) -> Optional[str]:
        """Lê conteúdo de arquivo DOCX"""
        try:
            doc = Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                text_parts.append(paragraph.text)
            
            return '\n'.join(text_parts)
        except Exception as e:
            print(f"Erro ao ler DOCX {file_path}: {e}")
            return None

    def read_txt(self, file_path: Path) -> Optional[str]:
        """Lê conteúdo de arquivo TXT"""
        try:
            encodings = ['utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            return None
        except Exception as e:
            print(f"Erro ao ler TXT {file_path}: {e}")
            return None

    def read_pdf(self, file_path: Path) -> Optional[str]:
        """Lê conteúdo de arquivo PDF"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            return '\n'.join(text_parts) if text_parts else None
        except ImportError:
            print(f"AVISO: pypdf nao instalado. Execute: pip install pypdf")
            return None
        except Exception as e:
            print(f"Erro ao ler PDF {file_path}: {e}")
            return None

    def read_file(self, file_path: Path) -> Optional[str]:
        """Lê conteúdo de arquivo baseado na extensão"""
        ext = file_path.suffix.lower()
        
        if ext == '.docx':
            return self.read_docx(file_path)
        elif ext == '.txt':
            return self.read_txt(file_path)
        elif ext == '.pdf':
            return self.read_pdf(file_path)
        else:
            return None

    def extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrai seções do memorial
        
        Args:
            content: Conteúdo do memorial
            
        Returns:
            Lista de seções com título e conteúdo
        """
        sections = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Verificar se é título de seção
            is_section = False
            for pattern in self.section_patterns:
                if re.match(pattern, line):
                    # Salvar seção anterior
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'content': '\n'.join(current_content).strip()
                        })
                    
                    # Nova seção
                    current_section = line
                    current_content = []
                    is_section = True
                    break
            
            if not is_section and current_section:
                current_content.append(line)
        
        # Adicionar última seção
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        return sections

    def extract_variables(self, content: str) -> List[str]:
        """
        Extrai variáveis dinâmicas do conteúdo
        
        Args:
            content: Conteúdo do memorial
            
        Returns:
            Lista de nomes de variáveis encontradas
        """
        variables = set()
        
        # Buscar padrões de variáveis
        for pattern in self.variable_patterns:
            matches = re.findall(pattern, content)
            variables.update(matches)
        
        # Buscar palavras que parecem variáveis (em maiúsculas, isoladas)
        # Ex: "LOCALIZAÇÃO", "EXTENSÃO", etc.
        potential_vars = re.findall(r'\b([A-ZÁÊÔÇ]{3,})\b', content)
        # Filtrar palavras muito comuns
        common_words = {'OBJETO', 'MEMORIAL', 'DESCRITIVO', 'TÉCNICO', 'ENGENHARIA', 
                       'NBR', 'ABNT', 'CONFORME', 'ESTE', 'QUE', 'PARA', 'COM'}
        potential_vars = [v for v in potential_vars if v not in common_words]
        variables.update(potential_vars)
        
        return sorted(list(variables))

    def extract_norms(self, content: str) -> List[str]:
        """
        Extrai normas técnicas mencionadas
        
        Args:
            content: Conteúdo do memorial
            
        Returns:
            Lista de normas encontradas
        """
        norms = re.findall(self.norm_pattern, content, re.IGNORECASE)
        # Normalizar formato
        normalized = []
        for norm in norms:
            # Padronizar formato: NBR 12345
            norm = re.sub(r'[\.\-]', '', norm)
            norm = norm.upper()
            if norm not in normalized:
                normalized.append(norm)
        
        return normalized

    def identify_category(self, content: str, filename: str) -> str:
        """
        Identifica categoria do memorial
        
        Args:
            content: Conteúdo do memorial
            filename: Nome do arquivo
            
        Returns:
            Categoria identificada
        """
        content_lower = content.lower()
        filename_lower = filename.lower()
        combined = content_lower + ' ' + filename_lower
        
        # Palavras-chave por categoria
        categories = {
            'civil_infra': ['pavimentação', 'pavimentacao', 'asfalto', 'estrada', 'rodovia', 
                           'drenagem', 'terraplenagem', 'cbr', 'subleito'],
            'estruturas': ['concreto', 'armado', 'estrutura', 'laje', 'viga', 'pilar', 
                          'fck', 'ca-50', 'ca-60', 'ferragem'],
            'eletrica': ['elétrica', 'eletrica', 'subestação', 'subestacao', 'transformador',
                        'tensão', 'tensao', 'kva', 'kv', 'corrente'],
            'hidraulica': ['hidráulica', 'hidraulica', 'água', 'agua', 'esgoto', 'tubulação',
                          'tubulacao', 'bomba', 'reservatório'],
            'edificacoes': ['edificação', 'edificacao', 'construção', 'construcao', 'obra',
                           'arquitetura', 'alvenaria'],
            'pontes_viadutos': ['ponte', 'viaduto', 'ponte', 'tabuleiro', 'pilares']
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in combined)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return 'civil_infra'  # Default

    def analyze(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Analisa um memorial completo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com análise do memorial
        """
        print(f"Analisando: {file_path.name}...")
        
        content = self.read_file(file_path)
        if not content:
            return None
        
        # Extrair informações
        sections = self.extract_sections(content)
        variables = self.extract_variables(content)
        norms = self.extract_norms(content)
        category = self.identify_category(content, file_path.name)
        
        analysis = {
            'file_path': str(file_path),
            'filename': file_path.name,
            'category': category,
            'sections': sections,
            'variables': variables,
            'norms': norms,
            'content_length': len(content),
            'section_count': len(sections)
        }
        
        return analysis

    def save_analysis(self, analysis: Dict[str, Any], output_path: Path):
        """Salva análise em arquivo JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)


def main():
    """Teste do analisador"""
    analyzer = MemorialAnalyzer()
    
    # Exemplo de uso
    test_file = Path("D:/test_memorial.docx")
    if test_file.exists():
        analysis = analyzer.analyze(test_file)
        if analysis:
            print(f"\nAnálise de {test_file.name}:")
            print(f"  Categoria: {analysis['category']}")
            print(f"  Seções: {analysis['section_count']}")
            print(f"  Variáveis: {len(analysis['variables'])}")
            print(f"  Normas: {len(analysis['norms'])}")
    else:
        print("Arquivo de teste não encontrado.")


if __name__ == "__main__":
    main()

