"""Normaliza categorias legadas UPPERCASE no SQLite de desenvolvimento."""

from pathlib import Path
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "snapeng.db"

MAPPING = {
    "CIVIL_INFRA": "civil_infra",
    "EDIFICACOES": "edificacoes",
    "ESTRUTURAS": "estruturas",
    "PONTES": "pontes_viadutos",
    "PONTES_VIADUTOS": "pontes_viadutos",
    "ELETRICA": "eletrica",
    "HIDRAULICA": "hidraulica",
}


def main() -> None:
    engine = create_engine(f"sqlite:///{DB}")
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, category FROM engineering_templates")
        ).fetchall()
        for template_id, category in rows:
            new_value = MAPPING.get(category, category.lower() if category else category)
            if new_value != category:
                conn.execute(
                    text(
                        "UPDATE engineering_templates SET category = :cat WHERE id = :id"
                    ),
                    {"cat": new_value, "id": template_id},
                )
                print(f"id={template_id}: {category} -> {new_value}")
        cats = conn.execute(
            text("SELECT DISTINCT category FROM engineering_templates")
        ).fetchall()
        print("categorias:", cats)


if __name__ == "__main__":
    main()
