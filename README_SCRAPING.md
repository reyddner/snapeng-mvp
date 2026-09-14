# Sistema de Scraping de Memoriais de Prefeituras

## 📊 Status Atual

- ✅ Sistema implementado e testado
- ✅ 291 memoriais encontrados na unidade D:\
- ✅ 17 templates gerados automaticamente
- ✅ Medidas de segurança ativas

## ⚠️ AVISOS DE SEGURANÇA

1. **Sites de prefeituras podem conter malware** - O sistema implementa várias camadas de proteção
2. **Sempre valide arquivos antes de processar** - Use o validador antes de analisar
3. **Rate limiting obrigatório** - Não sobrecarregue servidores públicos
4. **Respeite robots.txt** - Verifique antes de fazer scraping

## Estrutura do Sistema

### 1. Scraping Seguro (`scrape_prefeituras.py`)
- Busca memoriais em sites de prefeituras
- Download seguro com validação
- Quarentena automática de arquivos
- Rate limiting (3 segundos entre requisições)
- User-Agent identificável

### 2. Validação (`validate_downloaded_files.py`)
- Verifica tipo real do arquivo (magic bytes)
- Valida extensão vs conteúdo
- Detecta padrões suspeitos
- Calcula hash para verificação

### 3. Processamento (`process_scraped_memorials.py`)
- Processa arquivos validados
- Gera templates automaticamente
- Integra com sistema de importação

## Como Usar

### Passo 1: Preparar lista de municípios

Crie `backend/scripts/municipios_brasil.json`:

```json
{
  "municipios": [
    {
      "nome": "São Paulo",
      "uf": "SP",
      "url": "https://www.prefeitura.sp.gov.br",
      "codigo_ibge": "3550308"
    }
  ]
}
```

### Passo 2: Executar scraping (CUIDADO!)

```bash
# Processar apenas 10 municípios (teste)
cd backend
python scripts/scrape_prefeituras.py --max-municipios 10 --max-docs 3

# Processar mais (pode demorar muito)
python scripts/scrape_prefeituras.py --max-municipios 100 --max-docs 5
```

### Passo 3: Validar arquivos baixados

```bash
python scripts/validate_downloaded_files.py
```

### Passo 4: Processar e gerar templates

```bash
python scripts/process_scraped_memorials.py
```

### Passo 5: Carregar templates no banco

```bash
python scripts/load_templates.py
```

## Medidas de Segurança Implementadas

1. ✅ **Validação de URLs** - Verifica domínios e protocolos
2. ✅ **Quarentena automática** - Todos os arquivos vão para quarentena primeiro
3. ✅ **Verificação de tipo real** - Usa magic bytes, não apenas extensão
4. ✅ **Limite de tamanho** - Máximo 50MB por arquivo
5. ✅ **Rate limiting** - 3 segundos entre requisições
6. ✅ **Timeout** - 10 segundos por requisição
7. ✅ **User-Agent identificável** - Para transparência
8. ✅ **Hash SHA256** - Para verificação de integridade

## Limitações

- **PDFs podem não ser lidos corretamente** - Depende da qualidade do PDF
- **Sites podem bloquear scraping** - Use com moderação
- **Alguns sites podem ter CAPTCHA** - Requer intervenção manual
- **Arquivos corrompidos** - Serão rejeitados na validação

## Recomendações

1. **Comece pequeno** - Teste com 5-10 municípios primeiro
2. **Monitore logs** - Verifique se há problemas
3. **Valide sempre** - Nunca pule a etapa de validação
4. **Respeite servidores** - Não faça muitas requisições simultâneas
5. **Backup** - Faça backup dos arquivos validados

## Dependências Adicionais

```bash
pip install python-magic-bin  # Windows
# ou
pip install python-magic  # Linux/Mac
```

## Estrutura de Diretórios

```
downloads/
└── prefeituras/
    ├── quarantine/          # Arquivos em quarentena
    ├── validated/          # Arquivos validados (após validação)
    ├── scraping_report.json
    └── validation_report.json
```

