import json
from pathlib import Path

from app.services.template_quality import assess_template


TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "engineering_templates"


def test_all_template_files_are_valid_json():
    files = list(TEMPLATES_DIR.rglob("*.json"))
    assert files
    for path in files:
        template = json.loads(path.read_text(encoding="utf-8"))
        result = assess_template(template)
        assert isinstance(result["ready"], bool)


def test_official_bases_are_generation_ready():
    ready_files = list(TEMPLATES_DIR.rglob("*_base.json")) + list(
        TEMPLATES_DIR.rglob("concreto_armado.json")
    )
    assert ready_files
    for path in ready_files:
        result = assess_template(json.loads(path.read_text(encoding="utf-8")))
        assert result["ready"] is True, f"{path.name}: {result['errors']}"


def test_incomplete_structure_is_not_generation_ready():
    result = assess_template(
        {
            "name": "Material de referencia",
            "sections": [],
            "variables": [],
            "calculations": [],
        }
    )
    assert result["ready"] is False
    assert result["kind"] == "reference"
