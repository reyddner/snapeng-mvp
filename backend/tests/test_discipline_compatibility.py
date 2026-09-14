from app.services.discipline_compatibility import validate_discipline_compatibility


def test_detects_shared_location_conflict():
    conflicts = validate_discipline_compatibility(
        {"localizacao": "Rua A", "area_construida": 180},
        [
            {"discipline": "arquitetura", "data": {"localizacao": "Rua A", "area_construida": 180}},
            {"discipline": "eletrica", "data": {"localizacao": "Rua B", "area_construida": 180}},
        ],
    )
    assert any(item["field"] == "localizacao" for item in conflicts)


def test_accepts_consistent_shared_data():
    conflicts = validate_discipline_compatibility(
        {"localizacao": "Rua A", "area_construida": 180},
        [
            {"discipline": "arquitetura", "data": {"localizacao": "Rua A", "area_construida": 180}},
            {"discipline": "eletrica", "data": {"localizacao": "rua a", "area_construida": 180}},
        ],
    )
    assert conflicts == []
