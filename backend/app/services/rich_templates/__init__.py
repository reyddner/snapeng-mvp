"""Biblioteca de corpos ricos para templates oficiais."""

from __future__ import annotations

from typing import Any, Dict

from .annexes import with_annexes
from .bodies_a import ARQUITETURA, ELETRICA
from .bodies_b import CORPO_BOMBEIROS, HIDRAULICA, PLUVIAL, SANITARIO, SPDA
from .bodies_c import CONCRETO, FUNDACOES, METALICA, PAVIMENTACAO, SUBESTACAO

# subcategory do JSON -> corpo rico
RICH_BY_SUBCATEGORY: Dict[str, Dict[str, Any]] = {
    "arquitetura": with_annexes(ARQUITETURA, "arquitetura e edificações"),
    "eletrica": with_annexes(ELETRICA, "instalações elétricas"),
    "hidraulica": with_annexes(HIDRAULICA, "instalações hidráulicas"),
    "pluvial": with_annexes(PLUVIAL, "drenagem pluvial"),
    "sanitario": with_annexes(SANITARIO, "instalações sanitárias"),
    "spda": with_annexes(SPDA, "SPDA"),
    "corpo_bombeiros": with_annexes(CORPO_BOMBEIROS, "segurança contra incêndio"),
    "concreto_armado": with_annexes(CONCRETO, "estrutura de concreto armado"),
    "estrutura_metalica": with_annexes(METALICA, "estrutura metálica"),
    "fundacoes": with_annexes(FUNDACOES, "fundações"),
    "pavimentacao": with_annexes(PAVIMENTACAO, "pavimentação asfáltica"),
    "subestacao": with_annexes(SUBESTACAO, "subestação elétrica"),
}
