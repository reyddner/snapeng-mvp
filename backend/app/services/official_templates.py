"""Catalogo oficial de templates publicos do SNAP ENG.

Fonte unica para seed, purge e filtros de API — evita recontaminacao.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Optional, Set

# Arquivos JSON permitidos no seed publico.
SEED_ALLOWLIST: FrozenSet[str] = frozenset(
    {
        "arquitetura_base.json",
        "corpo_bombeiros_base.json",
        "eletrica_base.json",
        "spda_base.json",
        "estrutura_metalica_base.json",
        "fundacoes_base.json",
        "concreto_armado.json",
        "pavimentacao_asfaltica.json",
        "hidraulica_base.json",
        "pluvial_base.json",
        "sanitario_base.json",
        "subestacao.json",
    }
)

# Nomes comerciais curtos (apos rename nos JSON).
OFFICIAL_TEMPLATE_NAMES: FrozenSet[str] = frozenset(
    {
        "Pavimentação Asfáltica",
        "Subestação Elétrica",
        "SPDA Base",
        "Estrutura de Concreto Armado",
        "Estrutura Metálica Base",
        "Fundações Base",
        "Arquitetônico Base",
        "Segurança Contra Incêndio Base",
        "Instalações Elétricas Base",
        "Instalações Hidráulicas Base",
        "Drenagem Pluvial Base",
        "Instalações Sanitárias Base",
    }
)

# subcategory do template -> chave do questionario multidisciplinar
SUBCATEGORY_TO_DISCIPLINE: Dict[str, str] = {
    "arquitetura": "arquitetura",
    "corpo_bombeiros": "corpo_bombeiros",
    "eletrica": "eletrica",
    "spda": "spda",
    "estrutura_metalica": "estrutura_metalica",
    "concreto_armado": "estrutura_concreto",
    "fundacoes": "fundacoes",
    "hidraulica": "hidraulica",
    "pluvial": "pluvial",
    "sanitario": "sanitario",
    "pavimentacao": "pavimentacao",
    "subestacao": "subestacao",
}

SENSITIVE_NAME_MARKERS: tuple[str, ...] = (
    "protocolo",
    "proposta",
    "assinado",
    "questões",
    "questoes",
    "processo de engenharia de conhecimento",
    "gerado automaticamente",
    "câmara",
    "camara",
    "estacionamento",
    "modelo_regras",
    "modelo regras",
    "cópia de",
    "copia de",
)

INBOX_DIR_NAMES: FrozenSet[str] = frozenset({"_inbox", "inbox", "_raw", "raw"})


def discipline_for_subcategory(subcategory: Optional[str]) -> Optional[str]:
    if not subcategory:
        return None
    return SUBCATEGORY_TO_DISCIPLINE.get(subcategory.strip().lower())


def is_sensitive_template_name(name: str) -> bool:
    lowered = (name or "").casefold()
    return any(marker in lowered for marker in SENSITIVE_NAME_MARKERS)


def official_names_from_disk(templates_dir) -> Set[str]:
    """Le nomes oficiais a partir dos JSON allowlist (fonte de verdade no disco)."""
    import json
    from pathlib import Path

    root = Path(templates_dir)
    names: Set[str] = set()
    for path in root.rglob("*.json"):
        if any(part in INBOX_DIR_NAMES for part in path.parts):
            continue
        if path.name not in SEED_ALLOWLIST:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        name = data.get("name")
        if name:
            names.add(name)
    return names
