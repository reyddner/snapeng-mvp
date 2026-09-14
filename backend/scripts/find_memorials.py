"""
Script para buscar memoriais descritivos na unidade D:\
Arquivo: backend/scripts/find_memorials.py
"""

import os
from pathlib import Path
from typing import List, Dict
import re
from datetime import datetime


class MemorialFinder:
    """Busca arquivos de memoriais na unidade D:\\"""

    def __init__(self, root_path: str = "D:\\"):
        self.root_path = Path(root_path)
        self.extensions = ['.docx', '.doc', '.pdf', '.txt']
        self.keywords = ['memorial', 'descritivo', 'técnico', 'engenharia']
        self.found_files = []

    def is_memorial_file(self, file_path: Path) -> bool:
        """
        Verifica se um arquivo parece ser um memorial descritivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se parece ser um memorial
        """
        # Verificar extensão
        if file_path.suffix.lower() not in self.extensions:
            return False

        # Verificar nome do arquivo
        filename_lower = file_path.name.lower()
        has_keyword = any(keyword in filename_lower for keyword in self.keywords)
        
        return has_keyword

    def search_files(self, max_files: int = None, exclude_paths: List[str] = None) -> List[Dict]:
        """
        Busca arquivos de memoriais na unidade D:\
        
        Args:
            max_files: Número máximo de arquivos para buscar (None = todos)
            exclude_paths: Lista de caminhos para excluir da busca
            
        Returns:
            Lista de dicionários com informações dos arquivos encontrados
        """
        if exclude_paths is None:
            exclude_paths = [
                'Windows', 'Program Files', 'Program Files (x86)', 
                '$Recycle.Bin', 'System Volume Information',
                'AppData', 'node_modules', '.git'
            ]

        self.found_files = []
        count = 0
        
        print(f"Buscando memoriais em {self.root_path}...")
        print(f"Extensoes: {', '.join(self.extensions)}")
        print(f"Palavras-chave: {', '.join(self.keywords)}")
        print("-" * 60)

        try:
            for root, dirs, files in os.walk(self.root_path):
                # Pular diretórios excluídos
                dirs[:] = [d for d in dirs if not any(
                    exclude.lower() in d.lower() for exclude in exclude_paths
                )]

                for file in files:
                    if max_files and count >= max_files:
                        break

                    file_path = Path(root) / file
                    
                    try:
                        if self.is_memorial_file(file_path):
                            file_info = {
                                'path': str(file_path),
                                'name': file_path.name,
                                'size': file_path.stat().st_size,
                                'extension': file_path.suffix.lower(),
                                'modified': datetime.fromtimestamp(
                                    file_path.stat().st_mtime
                                ).isoformat(),
                                'directory': str(file_path.parent)
                            }
                            self.found_files.append(file_info)
                            count += 1
                            
                            if count % 10 == 0:
                                print(f"Encontrados {count} arquivos...", end='\r')
                                
                    except (PermissionError, OSError) as e:
                        # Ignorar arquivos sem permissão
                        continue
                    except Exception as e:
                        print(f"\nErro ao processar {file_path}: {e}")
                        continue

                if max_files and count >= max_files:
                    break

        except KeyboardInterrupt:
            print("\n\nBusca interrompida pelo usuário.")
        except Exception as e:
            print(f"\nErro durante a busca: {e}")

        print(f"\n\nTotal de arquivos encontrados: {len(self.found_files)}")
        return self.found_files

    def save_report(self, output_file: str = "memorials_found.txt"):
        """
        Salva relatório dos arquivos encontrados
        
        Args:
            output_file: Nome do arquivo de saída
        """
        report_path = Path(__file__).parent.parent / output_file
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE MEMORIAIS ENCONTRADOS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de arquivos: {len(self.found_files)}\n\n")
            
            # Agrupar por extensão
            by_extension = {}
            for file_info in self.found_files:
                ext = file_info['extension']
                if ext not in by_extension:
                    by_extension[ext] = []
                by_extension[ext].append(file_info)
            
            f.write("RESUMO POR EXTENSÃO:\n")
            f.write("-" * 80 + "\n")
            for ext, files in sorted(by_extension.items()):
                f.write(f"{ext}: {len(files)} arquivos\n")
            f.write("\n")
            
            # Lista completa
            f.write("ARQUIVOS ENCONTRADOS:\n")
            f.write("-" * 80 + "\n")
            for i, file_info in enumerate(self.found_files, 1):
                f.write(f"\n{i}. {file_info['name']}\n")
                f.write(f"   Caminho: {file_info['path']}\n")
                f.write(f"   Tamanho: {file_info['size']:,} bytes\n")
                f.write(f"   Modificado: {file_info['modified']}\n")
        
        print(f"\nRelatório salvo em: {report_path}")


def main():
    """Função principal"""
    finder = MemorialFinder()
    
    # Buscar arquivos (limitar a 1000 inicialmente para teste)
    print("Iniciando busca de memoriais...\n")
    files = finder.search_files(max_files=1000)
    
    if files:
        # Salvar relatório
        finder.save_report()
        
        # Mostrar resumo
        print("\n" + "=" * 60)
        print("RESUMO:")
        print("=" * 60)
        by_ext = {}
        for f in files:
            ext = f['extension']
            by_ext[ext] = by_ext.get(ext, 0) + 1
        
        for ext, count in sorted(by_ext.items()):
            print(f"  {ext}: {count} arquivos")
        
        print(f"\nTotal: {len(files)} arquivos encontrados")
        print(f"\nPrimeiros 5 arquivos:")
        for i, f in enumerate(files[:5], 1):
            print(f"  {i}. {f['name']} ({f['extension']}) - {f['path'][:60]}...")
    else:
        print("\nNenhum arquivo de memorial encontrado.")


if __name__ == "__main__":
    main()

