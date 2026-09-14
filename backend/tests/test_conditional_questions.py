from app.services.questionnaire_catalog import get_questionnaire
from app.services.template_engine import TemplateEngine


def test_sanitary_treatment_is_required_only_without_public_network():
    questionnaire = get_questionnaire("sanitario")
    treatment = next(item for item in questionnaire["questions"] if item["name"] == "sistema_tratamento")
    engine = TemplateEngine()

    assert engine.is_question_active(treatment, {"rede_coletora": "nao"}) is True
    assert engine.is_question_active(treatment, {"rede_coletora": "sim"}) is False
    errors = engine.validate_user_data(
        {"variables": questionnaire["questions"]},
        {"rede_coletora": "sim", "numero_contribuintes": 10, "ventilacao_sanitaria": "primaria"},
    )
    assert "sistema_tratamento" not in errors


def test_generator_fields_are_required_when_enabled():
    questionnaire = get_questionnaire("eletrica")
    variables = questionnaire["questions"]
    engine = TemplateEngine()
    errors = engine.validate_user_data(
        {"variables": variables},
        {"gerador": "sim"},
    )
    assert "potencia_gerador" in errors
    assert "autonomia_gerador" in errors