"""Valida coerencia entre dados compartilhados e disciplinas."""

from typing import Any, Dict, List


SHARED_FIELDS = {
    "localizacao": "Localizacao",
    "municipio": "Municipio",
    "uf": "UF",
    "area_construida": "Area construida",
    "numero_pavimentos": "Numero de pavimentos",
}


def _normalized(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(value.strip().lower().split())
    return value


def validate_discipline_compatibility(
    shared_data: Dict[str, Any], disciplines: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    conflicts: List[Dict[str, Any]] = []
    for field, label in SHARED_FIELDS.items():
        values = []
        for item in disciplines:
            value = item.get("data", {}).get(field)
            if value is not None and value != "":
                values.append((item.get("discipline", "desconhecida"), value))
        if not values:
            continue
        baseline = _normalized(shared_data.get(field))
        if baseline not in (None, ""):
            different = [
                {"discipline": discipline, "value": value}
                for discipline, value in values
                if _normalized(value) != baseline
            ]
            if different:
                conflicts.append(
                    {
                        "field": field,
                        "label": label,
                        "shared_value": shared_data[field],
                        "differences": different,
                    }
                )
        unique_values = {_normalized(value) for _, value in values}
        if len(unique_values) > 1:
            conflicts.append(
                {
                    "field": field,
                    "label": label,
                    "shared_value": shared_data.get(field),
                    "differences": [
                        {"discipline": discipline, "value": value}
                        for discipline, value in values
                    ],
                }
            )
    return conflicts
