"""
Sistema seguro para buscar memoriais descritivos em sites de prefeituras
Arquivo: backend/scripts/scrape_prefeituras.py

SEGURANÇA:
- Validação de URLs antes de acessar
- Download seguro com verificação de tipo de arquivo
- Quarentena de arquivos suspeitos
- Rate limiting para não sobrecarregar servidores
- User-Agent identificável
- Timeout em requisições
"""

import requests
from pathlib import Path
import time
import re
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
import hashlib
from datetime import datetime
import json


class SafeWebScraper:
    """Web scraper com medidas de segurança"""

    def __init__(self, rate_limit: float = 2.0, timeout: int = 10):
        """
        Args:
            rate_limit: Segundos entre requisições
            timeout: Timeout em segundos para requisições
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SNAPENG-Bot/1.0 (Memorial Scraper - Contato: suporte@snapeng.com.br)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9',
        })
        
        # Domínios suspeitos conhecidos (pode ser expandido)
        self.blocked_domains = set()
        self.safe_domains = {
            'gov.br', 'prefeitura.sp.gov.br', 'prefeitura.rio.gov.br',
            'portaltransparencia.gov.br'
        }

    def is_safe_url(self, url: str) -> bool:
        """
        Verifica se URL é segura para acessar
        
        Args:
            url: URL para verificar
            
        Returns:
            True se URL parece segura
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Verificar se está na lista de bloqueados
            if any(blocked in domain for blocked in self.blocked_domains):
                return False
            
            # Verificar se é domínio governamental
            if '.gov.br' in domain or any(safe in domain for safe in self.safe_domains):
                return True
            
            # Verificar protocolo
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Verificar se não tem caracteres suspeitos
            suspicious_chars = ['<', '>', '"', "'", 'javascript:', 'data:']
            if any(char in url.lower() for char in suspicious_chars):
                return False
            
            return True
        except Exception:
            return False

    def safe_request(self, url: str) -> Optional[requests.Response]:
        """
        Faz requisição HTTP segura com rate limiting
        
        Args:
            url: URL para acessar
            
        Returns:
            Response ou None se houver erro
        """
        if not self.is_safe_url(url):
            print(f"[BLOQUEADO] URL suspeita: {url}")
            return None
        
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            self.last_request_time = time.time()
            
            # Verificar status
            if response.status_code == 200:
                return response
            else:
                print(f"[ERRO] Status {response.status_code} para {url}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] {url}: {e}")
            return None

    def find_document_links(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """
        Encontra links para documentos (PDF, DOCX) no HTML
        
        Args:
            html_content: Conteúdo HTML
            base_url: URL base para resolver links relativos
            
        Returns:
            Lista de dicionários com informações dos links
        """
        links = []
        
        # Padrões para encontrar links de documentos
        patterns = [
            r'href=["\']([^"\']*\.(pdf|docx?|doc))["\']',
            r'href=["\']([^"\']*memorial[^"\']*\.(pdf|docx?|doc))["\']',
            r'href=["\']([^"\']*descritivo[^"\']*\.(pdf|docx?|doc))["\']',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE)
            for match in matches:
                link_url = match.group(1)
                full_url = urljoin(base_url, link_url)
                
                if self.is_safe_url(full_url):
                    links.append({
                        'url': full_url,
                        'filename': Path(urlparse(full_url).path).name,
                        'type': match.group(2).lower() if len(match.groups()) > 1 else 'unknown'
                    })
        
        # Remover duplicatas
        seen = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links

    def safe_download(self, url: str, output_dir: Path, max_size: int = 50 * 1024 * 1024) -> Optional[Path]:
        """
        Baixa arquivo de forma segura
        
        Args:
            url: URL do arquivo
            output_dir: Diretório de saída
            max_size: Tamanho máximo em bytes (50MB padrão)
            
        Returns:
            Caminho do arquivo baixado ou None
        """
        if not self.is_safe_url(url):
            return None
        
        response = self.safe_request(url)
        if not response:
            return None
        
        # Verificar Content-Type
        content_type = response.headers.get('Content-Type', '').lower()
        safe_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        
        if not any(safe_type in content_type for safe_type in safe_types):
            # Verificar extensão do arquivo
            ext = Path(urlparse(url).path).suffix.lower()
            if ext not in ['.pdf', '.doc', '.docx', '.txt']:
                print(f"[BLOQUEADO] Tipo de arquivo não permitido: {content_type}")
                return None
        
        # Verificar tamanho
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > max_size:
            print(f"[BLOQUEADO] Arquivo muito grande: {content_length} bytes")
            return None
        
        # Baixar em chunks para verificar tamanho durante download
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(urlparse(url).path).name
        
        # Sanitizar nome do arquivo
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        if not filename:
            filename = f"document_{hashlib.md5(url.encode()).hexdigest()[:8]}"
        
        file_path = output_dir / filename
        
        try:
            downloaded = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded > max_size:
                            file_path.unlink()
                            print(f"[BLOQUEADO] Arquivo excedeu tamanho máximo durante download")
                            return None
            
            # Verificar tamanho final
            if file_path.stat().st_size > max_size:
                file_path.unlink()
                return None
            
            print(f"[OK] Baixado: {filename} ({file_path.stat().st_size:,} bytes)")
            return file_path
            
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            print(f"[ERRO] Erro ao baixar {url}: {e}")
            return None


class PrefeituraScraper:
    """Scraper especializado em sites de prefeituras"""

    def __init__(self, output_dir: Path = None):
        """
        Args:
            output_dir: Diretório para salvar arquivos baixados
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "downloads" / "prefeituras"
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.scraper = SafeWebScraper(rate_limit=3.0)  # 3 segundos entre requisições
        self.processed_urls = set()
        self.found_documents = []

    def get_municipio_urls(self) -> List[Dict[str, str]]:
        """
        Obtém lista de URLs de prefeituras
        
        Returns:
            Lista de dicionários com nome do município e URL
        """
        # URLs comuns de prefeituras
        common_paths = [
            '/licitacoes',
            '/transparencia',
            '/obras',
            '/projetos',
            '/memorial',
            '/documentos',
            '/arquivos',
            '/downloads',
        ]
        
        # Por enquanto, retornar lista vazia
        # Em produção, carregar de arquivo ou API
        municipios = []
        
        # Exemplo: carregar de arquivo JSON se existir
        municipios_file = Path(__file__).parent / "municipios_brasil.json"
        if municipios_file.exists():
            with open(municipios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                municipios = data.get('municipios', [])
        
        return municipios

    def search_memorials_in_site(self, base_url: str, max_pages: int = 10) -> List[Dict[str, str]]:
        """
        Busca memoriais em um site de prefeitura
        
        Args:
            base_url: URL base do site
            max_pages: Número máximo de páginas para buscar
            
        Returns:
            Lista de documentos encontrados
        """
        if base_url in self.processed_urls:
            return []
        
        self.processed_urls.add(base_url)
        documents = []
        
        print(f"\n[BUSCANDO] {base_url}")
        
        # Buscar na página principal
        response = self.scraper.safe_request(base_url)
        if not response:
            return documents
        
        # Encontrar links de documentos
        doc_links = self.scraper.find_document_links(response.text, base_url)
        
        for link in doc_links:
            # Verificar se parece ser memorial
            filename_lower = link['filename'].lower()
            if any(keyword in filename_lower for keyword in ['memorial', 'descritivo', 'técnico']):
                documents.append({
                    'url': link['url'],
                    'filename': link['filename'],
                    'source_site': base_url,
                    'found_at': datetime.now().isoformat()
                })
        
        # Buscar em páginas comuns
        common_paths = ['/licitacoes', '/transparencia', '/obras', '/projetos']
        for path in common_paths[:max_pages]:
            page_url = urljoin(base_url, path)
            if page_url in self.processed_urls:
                continue
            
            self.processed_urls.add(page_url)
            page_response = self.scraper.safe_request(page_url)
            
            if page_response:
                page_links = self.scraper.find_document_links(page_response.text, page_url)
                for link in page_links:
                    filename_lower = link['filename'].lower()
                    if any(keyword in filename_lower for keyword in ['memorial', 'descritivo']):
                        documents.append({
                            'url': link['url'],
                            'filename': link['filename'],
                            'source_site': base_url,
                            'source_page': page_url,
                            'found_at': datetime.now().isoformat()
                        })
        
        return documents

    def download_and_quarantine(self, doc_info: Dict[str, str]) -> Optional[Path]:
        """
        Baixa documento e coloca em quarentena para análise
        
        Args:
            doc_info: Informações do documento
            
        Returns:
            Caminho do arquivo em quarentena ou None
        """
        # Diretório de quarentena
        quarantine_dir = self.output_dir / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        # Baixar arquivo
        file_path = self.scraper.safe_download(
            doc_info['url'],
            quarantine_dir,
            max_size=50 * 1024 * 1024  # 50MB
        )
        
        if file_path:
            # Criar arquivo de metadados
            metadata = {
                'original_url': doc_info['url'],
                'filename': doc_info['filename'],
                'source_site': doc_info.get('source_site', ''),
                'downloaded_at': datetime.now().isoformat(),
                'file_size': file_path.stat().st_size,
                'file_hash': self._calculate_hash(file_path),
                'status': 'quarantine'
            }
            
            metadata_file = file_path.with_suffix('.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return file_path

    def _calculate_hash(self, file_path: Path) -> str:
        """Calcula hash SHA256 do arquivo"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def process_municipios(self, municipios: List[Dict[str, str]], max_per_municipio: int = 5):
        """
        Processa lista de municípios
        
        Args:
            municipios: Lista de municípios com URLs
            max_per_municipio: Máximo de documentos por município
        """
        total = len(municipios)
        print(f"\nProcessando {total} municípios...")
        print("=" * 80)
        
        for i, municipio in enumerate(municipios, 1):
            nome = municipio.get('nome', 'Desconhecido')
            url = municipio.get('url', '')
            
            if not url:
                continue
            
            print(f"\n[{i}/{total}] {nome} - {url}")
            
            try:
                # Buscar memoriais no site
                documents = self.search_memorials_in_site(url, max_pages=3)
                
                # Limitar quantidade
                documents = documents[:max_per_municipio]
                
                # Baixar documentos
                for doc in documents:
                    file_path = self.download_and_quarantine(doc)
                    if file_path:
                        self.found_documents.append({
                            **doc,
                            'local_path': str(file_path),
                            'municipio': nome
                        })
                
                print(f"  Encontrados: {len(documents)} documentos")
                
            except Exception as e:
                print(f"  [ERRO] {e}")
                continue
            
            # Pausa entre municípios
            time.sleep(5)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Buscar memoriais em sites de prefeituras')
    parser.add_argument('--max-municipios', type=int, default=10,
                       help='Número máximo de municípios para processar (padrão: 10)')
    parser.add_argument('--max-docs', type=int, default=5,
                       help='Máximo de documentos por município (padrão: 5)')
    parser.add_argument('--municipios-file', type=str,
                       help='Arquivo JSON com lista de municípios')
    
    args = parser.parse_args()
    
    scraper = PrefeituraScraper()
    
    # Carregar municípios
    if args.municipios_file:
        with open(args.municipios_file, 'r', encoding='utf-8') as f:
            municipios_data = json.load(f)
            municipios = municipios_data.get('municipios', [])
    else:
        # Usar lista padrão (vazia por enquanto)
        municipios = scraper.get_municipio_urls()
    
    # Limitar quantidade
    municipios = municipios[:args.max_municipios]
    
    if not municipios:
        print("Nenhum município encontrado. Crie um arquivo municipios_brasil.json")
        return
    
    # Processar
    scraper.process_municipios(municipios, max_per_municipio=args.max_docs)
    
    # Salvar relatório
    report = {
        'total_documents': len(scraper.found_documents),
        'processed_urls': len(scraper.processed_urls),
        'documents': scraper.found_documents,
        'generated_at': datetime.now().isoformat()
    }
    
    report_file = scraper.output_dir / "scraping_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"RELATÓRIO FINAL")
    print(f"{'='*80}")
    print(f"Documentos encontrados: {len(scraper.found_documents)}")
    print(f"Relatório salvo em: {report_file}")


if __name__ == "__main__":
    main()

