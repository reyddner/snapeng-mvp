"""
Purge idempotente de templates publicos contaminados.

Uso (local ou producao):
  PYTHONPATH=backend python backend/scripts/purge_bad_templates.py
  PYTHONPATH=backend python backend/scripts/purge_bad_templates.py --soft

Padrao: APAGA registros fora da allowlist / sensiveis / nao-ready.
Com --soft: apenas marca is_public=0.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.core.paths import default_sqlite_path
from app.models.template import EngineeringTemplate
from app.services.official_templates import (
    is_sensitive_template_name,
    official_names_from_disk,
)
from app.services.template_quality import assess_template


def purge(*, soft: bool = False) -> dict:
    templates_root = Path(__file__).resolve().parent.parent.parent / "engineering_templates"
    keep_names = official_names_from_disk(templates_root)
    db = SessionLocal()
    deactivated = 0
    deleted = 0
    kept = 0
    try:
        for template in db.query(EngineeringTemplate).all():
            structure = dict(template.structure or {})
            structure.setdefault("variables", template.variables or [])
            ready = assess_template(structure).get("ready", False)
            description = (template.description or "").casefold()
            auto_import = "gerado automaticamente" in description
            sensitive = is_sensitive_template_name(template.name or "")
            allowed = template.name in keep_names and ready and not sensitive and not auto_import

            if allowed:
                if template.is_public != 1:
                    template.is_public = 1
                kept += 1
                continue

            if soft:
                if template.is_public != 0:
                    template.is_public = 0
                    deactivated += 1
            else:
                db.delete(template)
                deleted += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {
        "db_path": str(default_sqlite_path()),
        "kept_public_or_restored": kept,
        "deactivated": deactivated,
        "deleted": deleted,
        "keep_names": sorted(keep_names),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge templates publicos ruins do SNAP ENG")
    parser.add_argument(
        "--soft",
        action="store_true",
        help="Apenas despublica (is_public=0). Padrao apaga registros ruins.",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="(Legado) Apaga registros ruins — ja e o comportamento padrao.",
    )
    args = parser.parse_args()
    soft = args.soft and not args.delete
    result = purge(soft=soft)
    print("[PURGE] db=", result["db_path"])
    print("[PURGE] keep=", result["keep_names"])
    print(
        f"[PURGE] kept={result['kept_public_or_restored']} "
        f"deactivated={result['deactivated']} deleted={result['deleted']}"
    )


if __name__ == "__main__":
    main()
