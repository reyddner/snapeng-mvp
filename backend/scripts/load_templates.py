"""
Script para carregar templates oficiais (allowlist) no banco.
Remove do catalogo publico qualquer template fora da allowlist.
Nunca carrega pastas _inbox / inbox.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models.template import EngineeringTemplate, TemplateCategory
from app.services.official_templates import (
    INBOX_DIR_NAMES,
    SEED_ALLOWLIST,
    is_sensitive_template_name,
)
from app.services.template_quality import assess_template

if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

CATEGORY_MAP = {
    "civil": TemplateCategory.CIVIL_INFRA,
    "civil_infra": TemplateCategory.CIVIL_INFRA,
    "edificacoes": TemplateCategory.EDIFICACOES,
    "estruturas": TemplateCategory.ESTRUTURAS,
    "eletrica": TemplateCategory.ELETRICA,
    "hidraulica": TemplateCategory.HIDRAULICA,
    "pontes_viadutos": TemplateCategory.PONTES,
}


def load_template_from_json(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_inbox_path(path: Path) -> bool:
    return any(part in INBOX_DIR_NAMES for part in path.parts)


def _purge_non_allowlist(db) -> int:
    keep_names = set()
    templates_dir = Path(__file__).parent.parent.parent / "engineering_templates"
    for json_file in templates_dir.rglob("*.json"):
        if _is_inbox_path(json_file):
            continue
        if json_file.name in SEED_ALLOWLIST:
            data = load_template_from_json(json_file)
            keep_names.add(data.get("name"))

    removed = 0
    for template in db.query(EngineeringTemplate).all():
        if template.name not in keep_names or is_sensitive_template_name(template.name or ""):
            if template.is_public != 0:
                template.is_public = 0
                removed += 1
    return removed


def load_templates(*, allow_inbox: bool = False) -> None:
    db = SessionLocal()
    try:
        templates_dir = Path(__file__).parent.parent.parent / "engineering_templates"
        loaded = 0
        updated = 0
        skipped = 0

        for category_dir in templates_dir.iterdir():
            if not category_dir.is_dir():
                continue
            if category_dir.name in INBOX_DIR_NAMES:
                print(f"[SKIP] Pasta inbox ignorada: {category_dir.name}")
                continue
            category_enum = CATEGORY_MAP.get(category_dir.name)
            if not category_enum:
                continue

            for json_file in sorted(category_dir.rglob("*.json")):
                if _is_inbox_path(json_file) and not allow_inbox:
                    print(f"[SKIP] Inbox: {json_file}")
                    skipped += 1
                    continue
                if json_file.name not in SEED_ALLOWLIST:
                    print(f"[SKIP] Fora da allowlist: {json_file.name}")
                    skipped += 1
                    continue

                template_data = load_template_from_json(json_file)
                if is_sensitive_template_name(template_data.get("name", "")):
                    print(f"[SKIP] Nome sensivel: {template_data.get('name')}")
                    skipped += 1
                    continue

                assessment = assess_template(template_data)
                if not assessment.get("ready"):
                    print(
                        f"[SKIP] Nao ready: {json_file.name} -> {assessment.get('errors')}"
                    )
                    skipped += 1
                    continue

                meta = template_data.get("metadata") or {}
                generated_by = str(meta.get("generated_by") or "")
                if generated_by and "memorial" in generated_by.casefold() and not allow_inbox:
                    print(f"[SKIP] Import automatico sem --allow-inbox: {json_file.name}")
                    skipped += 1
                    continue

                existing = (
                    db.query(EngineeringTemplate)
                    .filter(EngineeringTemplate.name == template_data["name"])
                    .first()
                )
                if existing:
                    existing.description = template_data.get("description", "")
                    existing.category = category_enum
                    existing.subcategory = template_data.get("subcategory", "")
                    existing.structure = template_data
                    existing.variables = template_data.get("variables", [])
                    existing.is_public = 1
                    updated += 1
                    print(f"[UPD] {template_data['name']}")
                    continue

                db.add(
                    EngineeringTemplate(
                        name=template_data["name"],
                        description=template_data.get("description", ""),
                        category=category_enum,
                        subcategory=template_data.get("subcategory", ""),
                        structure=template_data,
                        variables=template_data.get("variables", []),
                        is_public=1,
                        downloads=0,
                        rating=0,
                    )
                )
                loaded += 1
                print(f"[OK] {template_data['name']}")

        purged = _purge_non_allowlist(db)
        db.commit()
        print(
            f"\n[SUCESSO] carregados={loaded} atualizados={updated} "
            f"desativados={purged} ignorados={skipped}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-inbox",
        action="store_true",
        help="Permite carregar material de _inbox (nao recomendado em producao)",
    )
    args = parser.parse_args()
    print("Carregando templates oficiais...\n")
    load_templates(allow_inbox=args.allow_inbox)
