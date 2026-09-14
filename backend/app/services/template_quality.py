"""Valida a prontidao de um template para geracao tecnica."""

import re
from typing import Any, Dict, List


PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def validate_template_structure(structure: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    sections = structure.get("sections")
    variables = structure.get("variables", [])
    calculations = structure.get("calculations", [])

    if not isinstance(sections, list) or not sections:
        errors.append("O template não possui seções geráveis.")
    if not isinstance(variables, list):
        errors.append("variables deve ser uma lista.")
    if not isinstance(calculations, list):
        errors.append("calculations deve ser uma lista.")

    variable_names = {
        item.get("name")
        for item in variables
        if isinstance(item, dict) and item.get("name")
    }
    calculation_names = {
        item.get("name")
        for item in calculations
        if isinstance(item, dict) and item.get("name")
    }
    placeholders = set()
    for section in sections if isinstance(sections, list) else []:
        if not isinstance(section, dict) or not section.get("title"):
            errors.append("Toda seção precisa de um título.")
            continue
        content = section.get("content", "")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"A seção '{section.get('title')}' não possui conteúdo.")
            continue
        placeholders.update(PLACEHOLDER_PATTERN.findall(content))
        for subsection in section.get("subsections", []):
            if isinstance(subsection, dict):
                placeholders.update(PLACEHOLDER_PATTERN.findall(subsection.get("content", "")))

    missing = sorted(placeholders - variable_names - calculation_names)
    errors.extend(f"Placeholder não declarado: {name}." for name in missing)

    for calculation in calculations if isinstance(calculations, list) else []:
        if not isinstance(calculation, dict) or not calculation.get("name"):
            errors.append("Cada cálculo precisa de um nome.")
        elif not calculation.get("formula"):
            errors.append(f"O cálculo '{calculation['name']}' não possui fórmula.")

    return errors


def assess_template(template: Dict[str, Any]) -> Dict[str, Any]:
    errors = validate_template_structure(template)
    return {
        "ready": not errors,
        "kind": "generator" if not errors else "reference",
        "errors": errors,
    }
