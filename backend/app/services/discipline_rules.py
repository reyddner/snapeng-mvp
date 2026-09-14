"""Regras deterministicas iniciais por disciplina.

Estas regras detectam dados ausentes ou incoerentes; nao substituem calculo,
analise normativa oficial ou responsabilidade de profissional habilitado.
"""

from typing import Any, Dict, List


def validate_discipline_rules(discipline: str, data: Dict[str, Any]) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []
    discipline = discipline.lower().strip()

    def required(field: str, message: str) -> None:
        if data.get(field) in (None, ""):
            errors.append({"field": field, "message": message})

    def positive_pair(first: str, second: str, message: str) -> None:
        first_value = data.get(first)
        second_value = data.get(second)
        if first_value not in (None, "") and second_value not in (None, ""):
            try:
                if float(second_value) < float(first_value):
                    errors.append({"field": second, "message": message})
            except (TypeError, ValueError):
                pass

    if discipline == "eletrica":
        required("tensao_fornecimento", "Informe a tensão de fornecimento.")
        required("potencia_instalada", "Informe a potência instalada.")
        if data.get("gerador") == "sim":
            required("potencia_gerador", "Gerador exige potência nominal.")
            required("autonomia_gerador", "Gerador exige autonomia.")
            required("transferencia_gerador", "Informe transferência e cargas atendidas.")

    elif discipline == "spda":
        required("analise_risco_spda", "Informe a análise de risco antes do nível de proteção.")
        required("nivel_protecao", "Informe o nível de proteção definido pela análise de risco.")
        required("aterramento_spda", "Informe a solução de aterramento.")

    elif discipline == "sanitario":
        required("numero_contribuintes", "Informe o número de contribuintes.")
        required("ventilacao_sanitaria", "Informe a solução de ventilação sanitária.")
        if data.get("rede_coletora") == "nao":
            required("sistema_tratamento", "Sem rede pública, informe o sistema de tratamento.")
            required("vazao_diaria", "Sem rede pública, informe a vazão diária.")
            required("destino_efluente", "Sem rede pública, informe o destino do efluente.")

    elif discipline == "pluvial":
        required("area_contribuicao", "Informe a área contribuinte.")
        required("intensidade_chuva", "Informe a intensidade de chuva de projeto.")
        required("tempo_retorno", "Informe o tempo de retorno.")
        required("destino_aguas", "Informe o destino das águas pluviais.")

    elif discipline == "fundacoes":
        required("tipo_fundacao", "Informe o tipo de fundação.")
        required("sondagem_disponivel", "Informe se existe sondagem.")
        if data.get("sondagem_disponivel") == "sim":
            required("tipo_solo", "Informe o tipo de solo identificado.")
            required("tensao_admissivel", "Informe a tensão admissível do solo.")
        elif data.get("sondagem_disponivel") == "nao":
            errors.append({"field": "sondagem_disponivel", "message": "A fundação não deve ser liberada sem sondagem ou justificativa técnica registrada."})

    elif discipline == "corpo_bombeiros":
        required("ocupacao_bombeiros", "Informe a ocupação conforme o regulamento local.")
        required("saidas_emergencia", "Informe quantidade, larguras e distâncias das saídas.")
        required("risco_incendio", "Informe a classificação de risco.")
        if data.get("sistema_hidrantes") == "sim":
            required("sistemas_protecao", "Descreva os sistemas de proteção e parâmetros dos hidrantes.")

    elif discipline == "estrutura_concreto":
        required("fck", "Informe o fck do concreto.")
        required("tipo_aco", "Informe a classe do aço.")
        positive_pair("diametro_min", "diametro_max", "O diâmetro máximo deve ser maior ou igual ao mínimo.")

    return errors
