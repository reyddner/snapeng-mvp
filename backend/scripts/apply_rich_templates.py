"""Aplica corpos ricos aos JSON oficiais e revalida prontidao."""

from __future__ import annotations

import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
repo_root = backend_dir.parent
sys.path.insert(0, str(backend_dir))

from app.services.official_templates import SEED_ALLOWLIST
from app.services.rich_templates import RICH_BY_SUBCATEGORY
from app.services.template_quality import assess_template


def main() -> int:
    templates_dir = repo_root / "engineering_templates"
    updated = 0
    errors = []

    for path in sorted(templates_dir.rglob("*.json")):
        if path.name not in SEED_ALLOWLIST:
            continue
        if "_inbox" in path.parts:
            continue

        data = json.loads(path.read_text(encoding="utf-8"))
        subcategory = (data.get("subcategory") or "").strip().lower()
        rich = RICH_BY_SUBCATEGORY.get(subcategory)
        if rich is None:
            errors.append(f"Sem corpo rico para subcategory={subcategory} ({path.name})")
            continue

        data["sections"] = rich["sections"]
        data["normas"] = rich.get("normas") or data.get("normas") or []
        if "calculations" in rich:
            data["calculations"] = rich["calculations"]
        data["version"] = "2.0"
        data["description"] = (
            data.get("description", "").split(" Versao enriquecida")[0].strip()
            + " Memorial técnico expandido (v2)."
        ).strip()

        assessment = assess_template(data)
        if not assessment["ready"]:
            errors.append(f"{path.name}: {assessment['errors']}")
            continue

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        updated += 1
        print(f"[OK] {path.relative_to(repo_root)} ({len(data['sections'])} secoes)")

    print(f"\nAtualizados: {updated}")
    if errors:
        print("Erros:")
        for item in errors:
            print(" -", item)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
