from app.services.discipline_rules import validate_discipline_rules


def test_fundation_without_survey_is_blocked():
    errors = validate_discipline_rules(
        "fundacoes",
        {"tipo_fundacao": "sapata", "sondagem_disponivel": "nao"},
    )
    assert any(error["field"] == "sondagem_disponivel" for error in errors)


def test_generator_requires_operational_data():
    errors = validate_discipline_rules("eletrica", {"gerador": "sim"})
    fields = {error["field"] for error in errors}
    assert {"potencia_gerador", "autonomia_gerador", "transferencia_gerador"} <= fields


def test_spda_requires_risk_analysis():
    errors = validate_discipline_rules("spda", {"nivel_protecao": "III"})
    assert any(error["field"] == "analise_risco_spda" for error in errors)