"""Avaliador seguro de formulas numericas (sem sympy arbitrario)."""

from __future__ import annotations

import ast
import operator
import re
from typing import Any

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TOKEN = re.compile(
    r"\s+|"
    r"[+\-*/%()]|"
    r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|"
    r"[A-Za-z_][A-Za-z0-9_]*"
)

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def substitute_inputs(formula: str, inputs: list[str], data: dict[str, Any]) -> str:
    """Substitui nomes de variavel por literais numericos (word-boundary)."""
    result = formula
    for var in inputs:
        if not _IDENT.match(var):
            raise ValueError(f"Nome de variável inválido na fórmula: {var}")
        if var not in data:
            continue
        try:
            numeric = float(data[var])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Entrada não numérica para '{var}'") from exc
        result = re.sub(rf"\b{re.escape(var)}\b", repr(numeric), result)
    return result


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return float(_UNARY_OPS[type(node.op)](_eval_node(node.operand)))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and (abs(left) > 1e6 or abs(right) > 100):
            raise ValueError("Potência fora dos limites permitidos")
        return float(_BIN_OPS[type(node.op)](left, right))
    raise ValueError("Fórmula contém operação ou token não permitido")


def evaluate_formula(formula: str) -> float:
    """
    Avalia expressao aritmetica simples.

    Aceita apenas digitos, operadores +-*/%()** e parenteses.
    """
    cleaned = formula.strip()
    if not cleaned:
        raise ValueError("Fórmula vazia")
    if len(cleaned) > 200:
        raise ValueError("Fórmula muito longa")
    if not is_numeric_expression(cleaned):
        raise ValueError("Fórmula contém caracteres não permitidos")
    try:
        tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Fórmula inválida") from exc
    value = _eval_node(tree)
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError("Resultado numérico inválido")
    return value


def is_numeric_expression(formula: str) -> bool:
    """Apos substituicao de variaveis: so literais e operadores."""
    return bool(re.fullmatch(r"[\d\s+\-*/().%eE]+", formula or ""))


def is_formula_shape_safe(formula: str) -> bool:
    """Valida formato bruto (ainda com nomes de variavel) antes de persistir template."""
    if not formula or len(formula) > 200:
        return False
    pos = 0
    s = formula.strip()
    if not s:
        return False
    while pos < len(s):
        match = _TOKEN.match(s, pos)
        if not match:
            return False
        pos = match.end()
    return pos == len(s)
