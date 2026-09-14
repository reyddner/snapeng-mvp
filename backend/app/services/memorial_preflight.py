"""Preflight unificado antes de gerar memoriais multidisciplinares.

Centraliza validação de conflitos, templates, campos obrigatórios e regras
por disciplina — usado pela API de pré-checagem e por generate-bundle.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.template import EngineeringTemplate
from app.services.discipline_compatibility import validate_discipline_compatibility
from app.services.discipline_rules import validate_discipline_rules
from app.services.questionnaire_catalog import get_questionnaire
from app.services.template_engine import TemplateEngine
from app.services.template_quality import assess_template


def _is_empty(value: Any) -> bool:
    return value is None or value == ""


def _question_visible(question: Dict[str, Any], data: Dict[str, Any]) -> bool:
    dependency = question.get("depends_on")
    if not dependency:
        return True
    value = data.get(dependency.get("field"))
    if "equals" in dependency:
        return value == dependency["equals"]
    if dependency.get("not_empty"):
        return not _is_empty(value)
    if "in" in dependency:
        return value in dependency["in"]
    return True


def _missing_required(questions: List[Dict[str, Any]], data: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for question in questions:
        if not question.get("required"):
            continue
        if not _question_visible(question, data):
            continue
        if _is_empty(data.get(question["name"])):
            missing.append(question["name"])
    return missing


def _load_public_template(
    db: Session, template_id: Optional[int]
) -> Tuple[Optional[EngineeringTemplate], Optional[str]]:
    if template_id is None:
        return None, "Informe um modelo de memorial (template) para a disciplina."
    template = (
        db.query(EngineeringTemplate)
        .filter(EngineeringTemplate.id == template_id)
        .filter(EngineeringTemplate.is_public == 1)
        .first()
    )
    if template is None:
        return None, f"Template {template_id} não encontrado ou não é público."
    structure = dict(template.structure or {})
    structure.setdefault("variables", template.variables or [])
    assessment = assess_template(structure)
    if not assessment.get("ready"):
        reasons = assessment.get("errors") or ["template incompleto"]
        detail = "; ".join(str(item) for item in reasons[:3])
        return template, f"Template '{template.name}' não está pronto para geração: {detail}"
    return template, None


def run_memorial_preflight(
    db: Session,
    *,
    enterprise: Dict[str, Any],
    disciplines: List[Dict[str, Any]],
    shared_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Retorna relatório estruturado de prontidão para geração."""
    shared = dict(shared_data or enterprise.get("shared_data") or {})
    blocking: List[str] = []
    warnings: List[str] = []
    discipline_reports: List[Dict[str, Any]] = []

    if not disciplines:
        blocking.append("Selecione ao menos uma disciplina.")

    seen = set()
    for selection in disciplines:
        discipline = str(selection.get("discipline") or "").lower().strip()
        if not discipline:
            blocking.append("Há uma seleção de disciplina sem identificador.")
            continue
        if discipline in seen:
            blocking.append(f"A disciplina '{discipline}' foi selecionada mais de uma vez.")
            continue
        seen.add(discipline)

        questionnaire = get_questionnaire(discipline)
        if questionnaire is None:
            blocking.append(f"Disciplina '{discipline}' não encontrada no catálogo.")
            discipline_reports.append(
                {
                    "discipline": discipline,
                    "label": discipline,
                    "ok": False,
                    "missing_fields": [],
                    "rule_errors": [],
                    "template_id": selection.get("template_id"),
                    "template_ready": False,
                    "errors": ["Disciplina não encontrada."],
                }
            )
            continue

        merged_data = {**shared, **(selection.get("data") or {})}
        template, template_error = _load_public_template(db, selection.get("template_id"))
        missing = _missing_required(questionnaire.get("questions") or [], merged_data)
        rule_errors = validate_discipline_rules(discipline, merged_data)

        engine_errors: Dict[str, str] = {}
        if template is not None and template_error is None:
            structure = dict(template.structure or {})
            structure.setdefault("variables", template.variables or [])
            engine_errors = TemplateEngine().validate_user_data(structure, merged_data)

        errors: List[str] = []
        if template_error:
            errors.append(template_error)
        for field in missing:
            errors.append(f"Campo obrigatório ausente: {field}")
        for item in rule_errors:
            errors.append(item.get("message") or item.get("field") or "Regra inválida")
        for field, message in engine_errors.items():
            errors.append(f"{field}: {message}")

        ok = not errors
        if not ok:
            for err in errors:
                blocking.append(f"{questionnaire['label']}: {err}")

        discipline_reports.append(
            {
                "discipline": discipline,
                "label": questionnaire["label"],
                "ok": ok,
                "missing_fields": missing,
                "rule_errors": rule_errors,
                "template_id": selection.get("template_id"),
                "template_name": template.name if template else None,
                "template_ready": template is not None and template_error is None,
                "errors": errors,
            }
        )

    conflicts = validate_discipline_compatibility(
        shared,
        [
            {
                "discipline": item.get("discipline"),
                "data": {**shared, **(item.get("data") or {})},
            }
            for item in disciplines
        ],
    )
    if conflicts:
        blocking.append("Existem conflitos entre dados compartilhados e disciplinas.")

    if not shared.get("localizacao") and not shared.get("municipio"):
        warnings.append(
            "Local da obra e município estão vazios — o memorial ficará genérico."
        )

    return {
        "can_generate": len(blocking) == 0 and bool(disciplines),
        "blocking": blocking,
        "warnings": warnings,
        "conflicts": conflicts,
        "disciplines": discipline_reports,
        "summary": {
            "disciplines_total": len(discipline_reports),
            "disciplines_ready": sum(1 for item in discipline_reports if item["ok"]),
            "missing_total": sum(len(item["missing_fields"]) for item in discipline_reports),
        },
    }
