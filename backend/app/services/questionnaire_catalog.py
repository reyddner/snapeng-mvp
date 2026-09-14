"""Catalogo inicial de perguntas por disciplina de engenharia."""

from copy import deepcopy
from typing import Any, Dict, List


def _question(
    name: str,
    label: str,
    question_type: str = "text",
    *,
    required: bool = False,
    description: str | None = None,
    unit: str | None = None,
    options: List[Dict[str, str]] | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    depends_on: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "name": name,
        "type": question_type,
        "label": label,
        "required": required,
    }
    if description:
        result["description"] = description
    if unit:
        result["unit"] = unit
    if options:
        result["options"] = options
    if min_value is not None:
        result["min"] = min_value
    if max_value is not None:
        result["max"] = max_value
    if depends_on:
        result["depends_on"] = depends_on
    return result


COMMON_QUESTIONS = [
    _question("localizacao", "Local da obra", required=True),
    _question("municipio", "Municipio", required=True),
    _question("uf", "Estado", required=True),
    _question("contratante", "Contratante"),
    _question("responsavel_tecnico", "Responsavel tecnico"),
    _question("crea_responsavel", "CREA do responsavel tecnico"),
    _question("area_terreno", "Area do terreno", "number", unit="m2", min_value=0),
    _question("area_construida", "Area construida", "number", unit="m2", min_value=0),
]


CATALOG: Dict[str, Dict[str, Any]] = {
    "eletrica": {
        "label": "Instalacoes eletricas",
        "document_types": ["memorial descritivo", "memorial de calculo"],
        "questions": [
            _question("tipo_edificacao", "Tipo de edificacao", required=True),
            _question("uso_edificacao", "Uso da edificacao", required=True),
            _question("tensao_fornecimento", "Tensao de fornecimento", "select", required=True, options=[{"value": "127_220", "label": "127/220 V"}, {"value": "220_380", "label": "220/380 V"}, {"value": "media_tensao", "label": "Media tensao"}]),
            _question("potencia_instalada", "Potencia instalada", "number", required=True, unit="kW", min_value=0),
            _question("carga_demanda", "Demanda calculada", "number", unit="kW", min_value=0),
            _question("padrao_entrada", "Tipo de padrao de entrada"),
            _question("gerador", "Possui gerador?", "select", options=[{"value": "nao", "label": "Nao"}, {"value": "sim", "label": "Sim"}]),
            _question("potencia_gerador", "Potencia do gerador", "number", required=True, unit="kVA", min_value=0, depends_on={"field": "gerador", "equals": "sim"}),
            _question("autonomia_gerador", "Autonomia do gerador", "number", required=True, unit="h", min_value=0, depends_on={"field": "gerador", "equals": "sim"}),
            _question("transferencia_gerador", "Transferencia e cargas atendidas", "textarea", required=True, depends_on={"field": "gerador", "equals": "sim"}),
            _question("aterramento_eletrico", "Descricao do sistema de aterramento", "textarea"),
        ],
    },
    "hidraulica": {
        "label": "Instalacoes hidraulicas",
        "document_types": ["memorial descritivo", "memorial de calculo"],
        "questions": [
            _question("tipo_edificacao", "Tipo de edificacao", required=True),
            _question("numero_pavimentos", "Numero de pavimentos", "number", required=True, min_value=1),
            _question("ocupacao_total", "Populacao estimada", "number", required=True, min_value=1),
            _question("abastecimento", "Fonte de abastecimento", "select", required=True, options=[{"value": "rede_publica", "label": "Rede publica"}, {"value": "poco", "label": "Poco"}, {"value": "mista", "label": "Rede publica e poco"}]),
            _question("reservatorio_inferior", "Volume do reservatorio inferior", "number", unit="L", min_value=0),
            _question("reservatorio_superior", "Volume do reservatorio superior", "number", unit="L", min_value=0),
            _question("agua_quente", "Possui sistema de agua quente?", "select", options=[{"value": "nao", "label": "Nao"}, {"value": "sim", "label": "Sim"}]),
            _question("materiais_hidraulicos", "Materiais e sistemas previstos", "textarea"),
        ],
    },
    "pluvial": {
        "label": "Drenagem de aguas pluviais",
        "document_types": ["memorial descritivo", "memorial de calculo"],
        "questions": [
            _question("area_contribuicao", "Area de contribuicao", "number", required=True, unit="m2", min_value=0),
            _question("coeficiente_escoamento", "Coeficiente de escoamento", "number", required=True, min_value=0, max_value=1),
            _question("intensidade_chuva", "Intensidade de chuva de projeto", "number", unit="mm/h", min_value=0),
            _question("tempo_retorno", "Tempo de retorno", "number", unit="anos", min_value=1),
            _question("destino_aguas", "Destino das aguas pluviais", required=True),
            _question("sistema_drenagem", "Sistema de drenagem previsto", "textarea"),
            _question("pontos_lancamento", "Pontos de lancamento"),
        ],
    },
    "sanitario": {
        "label": "Instalacoes sanitarias",
        "document_types": ["memorial descritivo", "memorial de calculo"],
        "questions": [
            _question("numero_contribuintes", "Numero de contribuintes", "number", required=True, min_value=1),
            _question("rede_coletora", "Existe rede coletora publica?", "select", required=True, options=[{"value": "sim", "label": "Sim"}, {"value": "nao", "label": "Nao"}]),
            _question("sistema_tratamento", "Sistema de tratamento", required=True, depends_on={"field": "rede_coletora", "equals": "nao"}),
            _question("vazao_diaria", "Vazao diaria estimada", "number", unit="L/dia", min_value=0, depends_on={"field": "rede_coletora", "equals": "nao"}),
            _question("destino_efluente", "Destino do efluente tratado", depends_on={"field": "rede_coletora", "equals": "nao"}),
            _question("ventilacao_sanitaria", "Solucao de ventilacao sanitaria", "textarea", required=True),
        ],
    },
    "spda": {
        "label": "SPDA e protecao contra descargas atmosfericas",
        "document_types": ["memorial descritivo", "memorial de calculo"],
        "questions": [
            _question("tipo_edificacao", "Tipo de edificacao", required=True),
            _question("altura_edificacao", "Altura da edificacao", "number", required=True, unit="m", min_value=0),
            _question("numero_pavimentos", "Numero de pavimentos", "number", required=True, min_value=1),
            _question("analise_risco_spda", "Resultado da analise de risco", "textarea", required=True),
            _question("nivel_protecao", "Nivel de protecao adotado", "select", required=True, options=[{"value": "I", "label": "Nivel I"}, {"value": "II", "label": "Nivel II"}, {"value": "III", "label": "Nivel III"}, {"value": "IV", "label": "Nivel IV"}], depends_on={"field": "analise_risco_spda", "not_empty": True}),
            _question("metodo_spda", "Metodo do SPDA", required=True),
            _question("subsistema_captacao", "Solucao de captacao", "textarea", required=True),
            _question("aterramento_spda", "Solucao de aterramento", "textarea", required=True),
            _question("equipotencializacao", "Medidas de equipotencializacao", "textarea", required=True),
        ],
    },
    "corpo_bombeiros": {
        "label": "Seguranca contra incendio e panico",
        "document_types": ["memorial de seguranca contra incendio"],
        "questions": [
            _question("ocupacao_bombeiros", "Ocupacao conforme uso da edificacao", required=True),
            _question("area_total_bombeiros", "Area total da edificacao", "number", required=True, unit="m2", min_value=0),
            _question("altura_edificacao", "Altura da edificacao", "number", required=True, unit="m", min_value=0),
            _question("populacao_bombeiros", "Populacao prevista", "number", required=True, min_value=1),
            _question("risco_incendio", "Classificacao de risco", required=True),
            _question("saidas_emergencia", "Descricao das saidas de emergencia", "textarea", required=True),
            _question("sistema_hidrantes", "Sistema de hidrantes", "select", options=[{"value": "nao_aplicavel", "label": "Nao aplicavel"}, {"value": "sim", "label": "Aplicavel"}]),
            _question("sistemas_protecao", "Outros sistemas de protecao", "textarea"),
        ],
    },
    "arquitetura": {
        "label": "Arquitetura e edificacoes",
        "document_types": ["memorial descritivo arquitetonico", "especificacoes tecnicas"],
        "questions": [
            _question("tipo_edificacao", "Tipo de edificacao", required=True),
            _question("programa_necessidades", "Programa de necessidades", "textarea", required=True),
            _question("numero_pavimentos", "Numero de pavimentos", "number", required=True, min_value=1),
            _question("area_terreno", "Area do terreno", "number", required=True, unit="m2", min_value=0),
            _question("area_construida", "Area construida", "number", required=True, unit="m2", min_value=0),
            _question("sistema_construtivo", "Sistema construtivo", required=True),
            _question("acabamentos", "Acabamentos e revestimentos", "textarea"),
            _question("acessibilidade", "Solucao de acessibilidade", "textarea"),
        ],
    },
    "estrutura_metalica": {
        "label": "Estrutura metalica",
        "document_types": ["memorial descritivo estrutural", "memorial de calculo"],
        "questions": [
            _question("tipo_estrutura", "Tipo de estrutura", required=True),
            _question("vao_maximo", "Vao maximo", "number", required=True, unit="m", min_value=0),
            _question("area_cobertura", "Area de cobertura", "number", unit="m2", min_value=0),
            _question("aco_estrutural", "Tipo de aco estrutural", required=True),
            _question("proteccao_corrosao", "Sistema de protecao contra corrosao", required=True),
            _question("ligacoes", "Tipo de ligacoes", required=True),
            _question("cargas_adotadas", "Cargas consideradas", "textarea", required=True),
            _question("contraventamento", "Sistema de contraventamento", "textarea"),
        ],
    },
    "estrutura_concreto": {
        "label": "Estrutura de concreto armado",
        "document_types": ["memorial descritivo estrutural", "memorial de calculo"],
        "questions": [
            _question("tipo_estrutura", "Tipo de estrutura", required=True),
            _question("numero_pavimentos", "Numero de pavimentos", "number", required=True, min_value=1),
            _question("fck", "Resistencia caracteristica do concreto", "number", required=True, unit="MPa", min_value=1),
            _question("tipo_aco", "Classe do aco", required=True),
            _question("cobrimento", "Cobrimento nominal", "number", required=True, unit="cm", min_value=0),
            _question("sistema_estrutural", "Sistema estrutural", required=True),
            _question("cargas_adotadas", "Cargas consideradas", "textarea", required=True),
            _question("controle_execucao", "Controle tecnologico e de execucao", "textarea"),
        ],
    },
    "fundacoes": {
        "label": "Fundacoes",
        "document_types": ["memorial descritivo de fundacoes", "memorial de calculo"],
        "questions": [
            _question("tipo_fundacao", "Tipo de fundacao", required=True),
            _question("sondagem_disponivel", "Existe sondagem do terreno?", "select", required=True, options=[{"value": "sim", "label": "Sim"}, {"value": "nao", "label": "Nao"}]),
            _question("tipo_solo", "Tipo de solo"),
            _question("tensao_admissivel", "Tensao admissivel do solo", "number", unit="kPa", min_value=0),
            _question("nivel_agua", "Nivel do lencol freatico", "number", unit="m", min_value=0),
            _question("cargas_fundacao", "Cargas transmitidas para a fundacao", "textarea", required=True),
            _question("criterios_execucao", "Criterios de escavacao e execucao", "textarea"),
        ],
    },
}


def list_disciplines() -> List[Dict[str, Any]]:
    return [
        {"key": key, "label": item["label"], "document_types": item["document_types"]}
        for key, item in CATALOG.items()
    ]


def get_questionnaire(discipline: str) -> Dict[str, Any] | None:
    item = CATALOG.get(discipline.lower())
    if item is None:
        return None
    specific_questions = deepcopy(item["questions"])
    specific_names = {question["name"] for question in specific_questions}
    common_questions = [
        question for question in deepcopy(COMMON_QUESTIONS)
        if question["name"] not in specific_names
    ]
    return {
        "discipline": discipline.lower(),
        "questions": common_questions + specific_questions,
        "label": item["label"],
        "document_types": item["document_types"],
    }
