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


def test_reference_material_is_not_generation_ready():
    reference = TEMPLATES_DIR / "civil_infra" / "1.000_questões_comentadas_de_engenharia_civil.json"
    result = assess_template(json.loads(reference.read_text(encoding="utf-8")))
    assert result["ready"] is False
    assert result["kind"] == "reference"
