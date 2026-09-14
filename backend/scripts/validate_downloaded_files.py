"""
Valida arquivos baixados antes de processar
Arquivo: backend/scripts/validate_downloaded_files.py

SEGURANÇA:
- Verifica tipo real do arquivo (magic bytes)
- Valida extensão vs conteúdo
- Verifica tamanho
- Escaneia por padrões suspeitos
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import hashlib


class FileValidator:
    """Valida arquivos baixados antes de processar"""

    def __init__(self):
        # Assinaturas de arquivo (magic bytes)
        self.file_signatures = {
            b'%PDF': 'application/pdf',
            b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'application/msword',  # DOC antigo
            b'PK\x03\x04': 'application/zip',  # DOCX é ZIP
        }
        
        self.suspicious_patterns = [
            b'MZ',  # Executável Windows (.exe, .dll)
            b'\x7fELF',  # Executável Linux
        ]
        
        # Extensões permitidas
        self.allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}

    def validate_file(self, file_path: Path) -> Dict[str, any]:
        """
        Valida um arquivo baixado
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com resultado da validação
        """
        result = {
            'file_path': str(file_path),
            'valid': False,
            'errors': [],
            'warnings': [],
            'mime_type': None,
            'size': 0,
            'hash': None
        }
        
        if not file_path.exists():
            result['errors'].append('Arquivo não existe')
            return result
        
        # Verificar tamanho
        size = file_path.stat().st_size
        result['size'] = size
        
        if size == 0:
            result['errors'].append('Arquivo vazio')
            return result
        
        if size > 100 * 1024 * 1024:  # 100MB
            result['errors'].append('Arquivo muito grande')
            return result
        
        # Ler primeiros bytes para verificar tipo
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)
            
            # Verificar padrões suspeitos
            for pattern in self.suspicious_patterns:
                if header.startswith(pattern):
                    result['errors'].append(f'Padrão suspeito detectado: {pattern}')
                    return result
            
            # Verificar tipo de arquivo por assinatura (magic bytes)
            detected_type = None
            for signature, mime_type in self.file_signatures.items():
                if header.startswith(signature):
                    detected_type = mime_type
                    break
            
            result['mime_type'] = detected_type or 'unknown'
            
            # Verificar se extensão corresponde ao tipo detectado
            ext = file_path.suffix.lower()
            if ext not in self.allowed_extensions:
                result['errors'].append(f'Extensão não permitida: {ext}')
                return result
            
            # Verificar correspondência extensão vs tipo
            if detected_type:
                if ext == '.pdf' and detected_type != 'application/pdf':
                    result['warnings'].append(f'Extensão .pdf mas tipo detectado: {detected_type}')
                elif ext in ['.doc', '.docx'] and 'msword' not in detected_type and 'zip' not in detected_type:
                    result['warnings'].append(f'Extensão {ext} mas tipo detectado: {detected_type}')
            
            # Verificar se é DOCX (ZIP com estrutura específica)
            if ext == '.docx' and header.startswith(b'PK\x03\x04'):
                # DOCX é um ZIP, verificar se tem estrutura correta
                # Por enquanto, aceitar se começa com PK (ZIP)
                pass
            
            # Calcular hash
            result['hash'] = self._calculate_hash(file_path)
            
            # Se passou todas as validações
            result['valid'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f'Erro ao validar: {e}')
        
        return result

    def _calculate_hash(self, file_path: Path) -> str:
        """Calcula hash SHA256"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def validate_quarantine(self, quarantine_dir: Path) -> List[Dict]:
        """
        Valida todos os arquivos em quarentena
        
        Args:
            quarantine_dir: Diretório de quarentena
            
        Returns:
            Lista de resultados de validação
        """
        results = []
        
        for file_path in quarantine_dir.glob('*'):
            if file_path.suffix in ['.pdf', '.doc', '.docx', '.txt']:
                result = self.validate_file(file_path)
                results.append(result)
                
                if result['valid']:
                    print(f"[OK] {file_path.name} - Válido")
                else:
                    print(f"[REJEITADO] {file_path.name} - {', '.join(result['errors'])}")
        
        return results


def main():
    """Função principal"""
    from pathlib import Path
    
    quarantine_dir = Path(__file__).parent.parent.parent / "downloads" / "prefeituras" / "quarantine"
    
    if not quarantine_dir.exists():
        print(f"Diretório de quarentena não encontrado: {quarantine_dir}")
        return
    
    validator = FileValidator()
    results = validator.validate_quarantine(quarantine_dir)
    
    # Separar válidos e inválidos
    valid_files = [r for r in results if r['valid']]
    invalid_files = [r for r in results if not r['valid']]
    
    print(f"\n{'='*80}")
    print(f"VALIDAÇÃO CONCLUÍDA")
    print(f"{'='*80}")
    print(f"Arquivos válidos: {len(valid_files)}")
    print(f"Arquivos rejeitados: {len(invalid_files)}")
    
    # Salvar relatório
    report = {
        'valid': valid_files,
        'invalid': invalid_files,
        'total': len(results)
    }
    
    report_file = quarantine_dir.parent / "validation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Relatório salvo em: {report_file}")


if __name__ == "__main__":
    main()

