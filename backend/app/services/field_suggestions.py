"""Heuristicas deterministas de sugestao de campos a partir de texto."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Set

from app.services.questionnaire_catalog import get_questionnaire

UF_PATTERN = re.compile(
    r"\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b",
    re.IGNORECASE,
)
AREA_PATTERN = re.compile(
    r"(?:área|area)\s*(?:constru[ií]da|total)?[^0-9]{0,20}(\d+(?:[.,]\d+)?)\s*(?:m²|m2)?",
    re.IGNORECASE,
)
AREA_TERRENO_PATTERN = re.compile(
    r"(?:área|area)\s*(?:do\s+)?terreno[^0-9]{0,20}(\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)
PAVIMENTOS_PATTERN = re.compile(
    r"(?:n[uú]mero\s+de\s+)?pavimentos?\s*(?:[:\-])?\s*(\d+)",
    re.IGNORECASE,
)
MUNICIPIO_PATTERN = re.compile(
    r"(?:munic[ií]pio|cidade)\s*(?:de|:)?\s*([A-Za-zÀ-ÿ\-']+(?:\s+[A-Za-zÀ-ÿ\-']+){0,5})",
    re.IGNORECASE,
)
LOCAL_PATTERN = re.compile(
    r"(?:local(?:iza[cç][aã]o)?|endere[cç]o|obra)\s*(?:da obra)?\s*(?:[:\-])\s*([^\n]+)",
    re.IGNORECASE,
)
CONTRATANTE_PATTERN = re.compile(
    r"contratante\s*(?:[:\-])\s*([^\n]+)",
    re.IGNORECASE,
)
CREA_PATTERN = re.compile(
    r"crea(?:[/\-\s]*[A-Z]{2})?\s*(?:n[ºo°.]*)?\s*([0-9./\-]+)",
    re.IGNORECASE,
)
POTENCIA_KW_PATTERN = re.compile(
    r"(?:pot[eê]ncia\s+instalada|demanda(?:\s+calculada)?)\s*(?:[:\-])?\s*(\d+(?:[.,]\d+)?)\s*kW",
    re.IGNORECASE,
)
POTENCIA_KVA_PATTERN = re.compile(
    r"(?:pot[eê]ncia\s+(?:do\s+)?gerador|gerador)\s*(?:[:\-])?\s*(\d+(?:[.,]\d+)?)\s*kVA",
    re.IGNORECASE,
)
ALTURA_PATTERN = re.compile(
    r"altura(?:\s+da\s+edifica[cç][aã]o)?\s*(?:[:\-])?\s*(\d+(?:[.,]\d+)?)\s*m\b",
    re.IGNORECASE,
)
POPULACAO_PATTERN = re.compile(
    r"(?:popula[cç][aã]o|ocupa[cç][aã]o|contribuintes)\s*(?:estimada|prevista|total)?\s*(?:[:\-])?\s*(\d+)",
    re.IGNORECASE,
)
TIPO_EDIFICACAO_PATTERN = re.compile(
    r"tipo\s+(?:da\s+)?edifica[cç][aã]o\s*(?:[:\-])\s*([^\n]+)",
    re.IGNORECASE,
)
TENSAO_PATTERN = re.compile(
    r"(?:tens[aã]o(?:\s+de\s+fornecimento)?)\s*(?:[:\-])?\s*(127\s*/\s*220|220\s*/\s*380|m[eé]dia\s+tens[aã]o)",
    re.IGNORECASE,
)
NIVEL_SPDA_PATTERN = re.compile(
    r"n[ií]vel\s+(?:de\s+)?prote[cç][aã]o\s*(?:[:\-])?\s*(I{1,3}|IV|[1-4])",
    re.IGNORECASE,
)
AREA_CONTRIB_PATTERN = re.compile(
    r"(?:área|area)\s*(?:de\s+)?contribui[cç][aã]o\s*(?:[:\-])?\s*(\d+(?:[.,]\d+)?)",
    re.IGNORECASE,
)
INTENSIDADE_CHUVA_PATTERN = re.compile(
    r"intensidade\s*(?:de\s+)?chuva\s*(?:[:\-])?\s*(\d+(?:[.,]\d+)?)\s*(?:mm/?h)?",
    re.IGNORECASE,
)
TEMPO_RETORNO_PATTERN = re.compile(
    r"tempo\s+de\s+retorno\s*(?:[:\-])?\s*(\d+)",
    re.IGNORECASE,
)
TIPO_FUNDACAO_PATTERN = re.compile(
    r"tipo\s+(?:de\s+)?funda[cç][aã]o\s*(?:[:\-])\s*([^\n]+)",
    re.IGNORECASE,
)
TENSAO_SOLO_PATTERN = re.compile(
    r"tens[aã]o\s+admiss[ií]vel(?:\s+do\s+solo)?\s*(?:[:\-])?\s*(\d+(?:[.,]\d+)?)\s*(?:kPa|kpa)?",
    re.IGNORECASE,
)
FCK_PATTERN = re.compile(
    r"\bfck\b\s*(?:[:\-])?\s*(\d+(?:[.,]\d+)?)\s*(?:MPa|mpa)?",
    re.IGNORECASE,
)
RISCO_INCENDIO_PATTERN = re.compile(
    r"(?:classifica[cç][aã]o\s+de\s+)?risco(?:\s+de\s+inc[eê]ndio)?\s*(?:[:\-])\s*([^\n]+)",
    re.IGNORECASE,
)
OCUPACAO_BOMBEIROS_PATTERN = re.compile(
    r"ocupa[cç][aã]o(?:\s+conforme\s+uso)?\s*(?:[:\-])\s*([^\n]+)",
    re.IGNORECASE,
)

SHARED_FIELDS = {
    "localizacao",
    "municipio",
    "uf",
    "area_construida",
    "numero_pavimentos",
    "area_terreno",
    "contratante",
}


def _clean_place_name(value: str) -> str:
    cleaned = " ".join(value.split()).strip(" .,;")
    stop_words = {"uf", "area", "área", "localizacao", "localização", "endereco", "endereço"}
    parts = []
    for part in cleaned.split():
        if part.lower().rstrip(":") in stop_words:
            break
        parts.append(part)
    return " ".join(parts).strip(" .,;")


def _suggestion(
    field: str,
    label: str,
    value: Any,
    *,
    confidence: str,
    source: str,
    target: str = "shared",
    discipline: Optional[str] = None,
) -> Dict[str, Any]:
    item = {
        "field": field,
        "label": label,
        "value": value,
        "confidence": confidence,
        "source": source,
        "target": target,
    }
    if discipline:
        item["discipline"] = discipline
        item["label"] = f"{label} ({discipline})"
    return item


def _parse_float(raw: str) -> Optional[float]:
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


def _allowed_fields(disciplines: Iterable[str]) -> Set[str]:
    allowed = set(SHARED_FIELDS)
    for discipline in disciplines:
        questionnaire = get_questionnaire(discipline)
        if not questionnaire:
            continue
        for question in questionnaire.get("questions", []):
            allowed.add(question["name"])
    return allowed


def suggest_fields_from_text(
    text: str,
    disciplines: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Heuristicas deterministas — sempre exigem confirmacao humana."""
    if not text or not text.strip():
        return []

    selected = [item.lower().strip() for item in (disciplines or []) if item]
    allowed = _allowed_fields(selected) if selected else None
    suggestions: List[Dict[str, Any]] = []

    def accept(field: str) -> bool:
        return allowed is None or field in allowed

    uf_match = UF_PATTERN.search(text)
    if uf_match and accept("uf"):
        suggestions.append(_suggestion("uf", "UF", uf_match.group(1).upper(), confidence="probable", source="regex_uf"))

    area_match = AREA_PATTERN.search(text)
    if area_match and accept("area_construida"):
        value = _parse_float(area_match.group(1))
        if value is not None:
            suggestions.append(
                _suggestion("area_construida", "Área construída", value, confidence="probable", source="regex_area")
            )

    terreno_match = AREA_TERRENO_PATTERN.search(text)
    if terreno_match and accept("area_terreno"):
        value = _parse_float(terreno_match.group(1))
        if value is not None:
            suggestions.append(
                _suggestion("area_terreno", "Área do terreno", value, confidence="probable", source="regex_area_terreno")
            )

    pav_match = PAVIMENTOS_PATTERN.search(text)
    if pav_match and accept("numero_pavimentos"):
        suggestions.append(
            _suggestion(
                "numero_pavimentos",
                "Número de pavimentos",
                int(pav_match.group(1)),
                confidence="probable",
                source="regex_pavimentos",
            )
        )

    municipio_match = MUNICIPIO_PATTERN.search(text)
    if municipio_match and accept("municipio"):
        municipio = _clean_place_name(municipio_match.group(1))
        if municipio:
            suggestions.append(
                _suggestion("municipio", "Município", municipio.title(), confidence="probable", source="regex_municipio")
            )

    local_match = LOCAL_PATTERN.search(text)
    if local_match and accept("localizacao"):
        local = _clean_place_name(local_match.group(1).splitlines()[0])
        if local and len(local) <= 200:
            suggestions.append(
                _suggestion("localizacao", "Local da obra", local, confidence="unclear", source="regex_localizacao")
            )

    contratante_match = CONTRATANTE_PATTERN.search(text)
    if contratante_match and accept("contratante"):
        value = _clean_place_name(contratante_match.group(1).splitlines()[0])
        if value:
            suggestions.append(
                _suggestion("contratante", "Contratante", value, confidence="probable", source="regex_contratante")
            )

    crea_match = CREA_PATTERN.search(text)
    if crea_match and accept("crea_responsavel"):
        suggestions.append(
            _suggestion(
                "crea_responsavel",
                "CREA do responsável",
                crea_match.group(1).strip(),
                confidence="probable",
                source="regex_crea",
            )
        )

    # Sugestões específicas por disciplina ativa
    for discipline in selected or []:
        if discipline == "eletrica":
            pot = POTENCIA_KW_PATTERN.search(text)
            if pot:
                value = _parse_float(pot.group(1))
                label_raw = pot.group(0).lower()
                field = "potencia_instalada" if "instalada" in label_raw else "carga_demanda"
                if value is not None and accept(field):
                    suggestions.append(
                        _suggestion(
                            field,
                            "Potência instalada" if field == "potencia_instalada" else "Demanda calculada",
                            value,
                            confidence="probable",
                            source="regex_potencia_kw",
                            target="discipline",
                            discipline=discipline,
                        )
                    )

            gerador = POTENCIA_KVA_PATTERN.search(text)
            if gerador and accept("potencia_gerador"):
                value = _parse_float(gerador.group(1))
                if value is not None:
                    suggestions.append(
                        _suggestion(
                            "potencia_gerador",
                            "Potência do gerador",
                            value,
                            confidence="probable",
                            source="regex_potencia_kva",
                            target="discipline",
                            discipline=discipline,
                        )
                    )
                    suggestions.append(
                        _suggestion(
                            "gerador",
                            "Possui gerador?",
                            "sim",
                            confidence="probable",
                            source="regex_gerador_flag",
                            target="discipline",
                            discipline=discipline,
                        )
                    )

            tensao = TENSAO_PATTERN.search(text)
            if tensao and accept("tensao_fornecimento"):
                raw = re.sub(r"\s+", "", tensao.group(1).lower())
                mapping = {
                    "127/220": "127_220",
                    "220/380": "220_380",
                    "médiatensão": "media_tensao",
                    "mediatensao": "media_tensao",
                }
                value = mapping.get(raw, raw.replace("/", "_"))
                suggestions.append(
                    _suggestion(
                        "tensao_fornecimento",
                        "Tensão de fornecimento",
                        value,
                        confidence="probable",
                        source="regex_tensao",
                        target="discipline",
                        discipline=discipline,
                    )
                )

        if discipline == "spda":
            altura = ALTURA_PATTERN.search(text)
            if altura and accept("altura_edificacao"):
                value = _parse_float(altura.group(1))
                if value is not None:
                    suggestions.append(
                        _suggestion(
                            "altura_edificacao",
                            "Altura da edificação",
                            value,
                            confidence="probable",
                            source="regex_altura",
                            target="discipline",
                            discipline=discipline,
                        )
                    )
            nivel = NIVEL_SPDA_PATTERN.search(text)
            if nivel and accept("nivel_protecao"):
                raw = nivel.group(1).upper()
                mapping = {"1": "I", "2": "II", "3": "III", "4": "IV"}
                value = mapping.get(raw, raw)
                suggestions.append(
                    _suggestion(
                        "nivel_protecao",
                        "Nível de proteção SPDA",
                        value,
                        confidence="probable",
                        source="regex_nivel_spda",
                        target="discipline",
                        discipline=discipline,
                    )
                )

        if discipline == "hidraulica":
            pop = POPULACAO_PATTERN.search(text)
            if pop and accept("ocupacao_total"):
                suggestions.append(
                    _suggestion(
                        "ocupacao_total",
                        "População estimada",
                        int(pop.group(1)),
                        confidence="probable",
                        source="regex_populacao",
                        target="discipline",
                        discipline=discipline,
                    )
                )

        if discipline == "sanitario":
            pop = POPULACAO_PATTERN.search(text)
            if pop and accept("numero_contribuintes"):
                suggestions.append(
                    _suggestion(
                        "numero_contribuintes",
                        "Número de contribuintes",
                        int(pop.group(1)),
                        confidence="probable",
                        source="regex_populacao",
                        target="discipline",
                        discipline=discipline,
                    )
                )

        if discipline in {"eletrica", "spda", "hidraulica", "arquitetura", "corpo_bombeiros"}:
            tipo = TIPO_EDIFICACAO_PATTERN.search(text)
            if tipo and accept("tipo_edificacao"):
                value = _clean_place_name(tipo.group(1).splitlines()[0])
                if value:
                    suggestions.append(
                        _suggestion(
                            "tipo_edificacao",
                            "Tipo de edificação",
                            value,
                            confidence="unclear",
                            source="regex_tipo_edificacao",
                            target="discipline",
                            discipline=discipline,
                        )
                    )

        if discipline == "pluvial":
            area = AREA_CONTRIB_PATTERN.search(text)
            if area and accept("area_contribuicao"):
                value = _parse_float(area.group(1))
                if value is not None:
                    suggestions.append(
                        _suggestion(
                            "area_contribuicao",
                            "Área de contribuição",
                            value,
                            confidence="probable",
                            source="regex_area_contribuicao",
                            target="discipline",
                            discipline=discipline,
                        )
                    )
            intensidade = INTENSIDADE_CHUVA_PATTERN.search(text)
            if intensidade and accept("intensidade_chuva"):
                value = _parse_float(intensidade.group(1))
                if value is not None:
                    suggestions.append(
                        _suggestion(
                            "intensidade_chuva",
                            "Intensidade de chuva",
                            value,
                            confidence="probable",
                            source="regex_intensidade_chuva",
                            target="discipline",
                            discipline=discipline,
                        )
                    )
            retorno = TEMPO_RETORNO_PATTERN.search(text)
            if retorno and accept("tempo_retorno"):
                suggestions.append(
                    _suggestion(
                        "tempo_retorno",
                        "Tempo de retorno",
                        int(retorno.group(1)),
                        confidence="probable",
                        source="regex_tempo_retorno",
                        target="discipline",
                        discipline=discipline,
                    )
                )

        if discipline == "fundacoes":
            tipo_f = TIPO_FUNDACAO_PATTERN.search(text)
            if tipo_f and accept("tipo_fundacao"):
                value = _clean_place_name(tipo_f.group(1).splitlines()[0])
                if value:
                    suggestions.append(
                        _suggestion(
                            "tipo_fundacao",
                            "Tipo de fundação",
                            value,
                            confidence="probable",
                            source="regex_tipo_fundacao",
                            target="discipline",
                            discipline=discipline,
                        )
                    )
            if re.search(r"sondagem", text, re.IGNORECASE) and accept("sondagem_disponivel"):
                suggestions.append(
                    _suggestion(
                        "sondagem_disponivel",
                        "Existe sondagem do terreno?",
                        "sim",
                        confidence="probable",
                        source="regex_sondagem",
                        target="discipline",
                        discipline=discipline,
                    )
                )
            tensao = TENSAO_SOLO_PATTERN.search(text)
            if tensao and accept("tensao_admissivel"):
                value = _parse_float(tensao.group(1))
                if value is not None:
                    suggestions.append(
                        _suggestion(
                            "tensao_admissivel",
                            "Tensão admissível do solo",
                            value,
                            confidence="probable",
                            source="regex_tensao_solo",
                            target="discipline",
                            discipline=discipline,
                        )
                    )

        if discipline == "estrutura_concreto":
            fck = FCK_PATTERN.search(text)
            if fck and accept("fck"):
                value = _parse_float(fck.group(1))
                if value is not None:
                    suggestions.append(
                        _suggestion(
                            "fck",
                            "fck do concreto",
                            value,
                            confidence="probable",
                            source="regex_fck",
                            target="discipline",
                            discipline=discipline,
                        )
                    )

        if discipline == "corpo_bombeiros":
            altura = ALTURA_PATTERN.search(text)
            if altura and accept("altura_edificacao"):
                value = _parse_float(altura.group(1))
                if value is not None:
                    suggestions.append(
                        _suggestion(
                            "altura_edificacao",
                            "Altura da edificação",
                            value,
                            confidence="probable",
                            source="regex_altura",
                            target="discipline",
                            discipline=discipline,
                        )
                    )
            pop = POPULACAO_PATTERN.search(text)
            if pop and accept("populacao_bombeiros"):
                suggestions.append(
                    _suggestion(
                        "populacao_bombeiros",
                        "População prevista",
                        int(pop.group(1)),
                        confidence="probable",
                        source="regex_populacao",
                        target="discipline",
                        discipline=discipline,
                    )
                )
            risco = RISCO_INCENDIO_PATTERN.search(text)
            if risco and accept("risco_incendio"):
                value = _clean_place_name(risco.group(1).splitlines()[0])
                if value:
                    suggestions.append(
                        _suggestion(
                            "risco_incendio",
                            "Classificação de risco",
                            value,
                            confidence="unclear",
                            source="regex_risco_incendio",
                            target="discipline",
                            discipline=discipline,
                        )
                    )
            ocup = OCUPACAO_BOMBEIROS_PATTERN.search(text)
            if ocup and accept("ocupacao_bombeiros"):
                value = _clean_place_name(ocup.group(1).splitlines()[0])
                if value:
                    suggestions.append(
                        _suggestion(
                            "ocupacao_bombeiros",
                            "Ocupação",
                            value,
                            confidence="unclear",
                            source="regex_ocupacao_bombeiros",
                            target="discipline",
                            discipline=discipline,
                        )
                    )

    # Deduplicar por target+discipline+field
    unique: Dict[str, Dict[str, Any]] = {}
    for item in suggestions:
        key = f"{item.get('target')}:{item.get('discipline') or ''}:{item['field']}"
        unique[key] = item
    return list(unique.values())
