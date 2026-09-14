"""Catalogo de projetos-modelo publicos para demonstracao e validacao E2E.

Entregaveis reais da plataforma hoje: memoriais descritivos em DOCX/PDF (ZIP).
Plantas CAD/DWG nao sao geradas pelo MVP — os demos deixam isso explicito.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.template import EngineeringTemplate
from app.services.official_templates import SUBCATEGORY_TO_DISCIPLINE
from app.services.questionnaire_catalog import get_questionnaire

# disciplina -> subcategory do template oficial
DISCIPLINE_TO_SUBCATEGORY = {
    value: key for key, value in SUBCATEGORY_TO_DISCIPLINE.items()
}
# Fix inverse collisions (estrutura_concreto maps from concreto_armado)
DISCIPLINE_TO_SUBCATEGORY.update(
    {
        "estrutura_concreto": "concreto_armado",
        "arquitetura": "arquitetura",
        "corpo_bombeiros": "corpo_bombeiros",
        "eletrica": "eletrica",
        "spda": "spda",
        "estrutura_metalica": "estrutura_metalica",
        "fundacoes": "fundacoes",
        "hidraulica": "hidraulica",
        "pluvial": "pluvial",
        "sanitario": "sanitario",
        "pavimentacao": "pavimentacao",
        "subestacao": "subestacao",
    }
)


PROFESSIONAL_DEMO = {
    "full_name": "Eng. Ana Clara Montenegro",
    "professional_title": "Engenheira Civil",
    "crea_number": "12345/D",
    "crea_state": "GO",
    "art_number": "ART-2026-004812",
    "company_name": "Montenegro Projetos e Consultoria Ltda",
    "email": "projetos@montenegro.eng.br",
    "phone": "(62) 99999-4410",
}


def _residencia_disciplines() -> Dict[str, Dict[str, Any]]:
    return {
        "arquitetura": {
            "tipo_edificacao": "Residencia unifamiliar de alto padrao",
            "programa_necessidades": (
                "Terreo: living integrado, lavabo, gourmet, cozinha, despensa, "
                "suite de hospedes, home office, garagem coberta para 3 veiculos, "
                "area de servico e deposito. Superior: suite master com closet e "
                "spa, duas suites, sala intima e varanda. Cobertura: solarium e "
                "casa de maquinas."
            ),
            "numero_pavimentos": 2,
            "area_terreno": 540,
            "area_construida": 312,
            "sistema_construtivo": "Alvenaria estrutural parcial + concreto armado moldado in loco",
            "acabamentos": (
                "Fachada em porcelanato 90x180, esquadrias de aluminio com vidro "
                "temperado, piso interno em porcelanato acetinado, forro de gesso "
                "com sancas, bancadas em quartzito."
            ),
            "acessibilidade": (
                "Rota acessivel do portao a sala, lavabo adaptavel, elevador "
                "residencial previsto no poço tecnico (fase 2)."
            ),
        },
        "eletrica": {
            "tipo_edificacao": "Residencia unifamiliar",
            "uso_edificacao": "Residencial permanente",
            "tensao_fornecimento": "127_220",
            "potencia_instalada": 48.5,
            "carga_demanda": 32.0,
            "padrao_entrada": "Padrao trifasico 70 A com medicao individual",
            "gerador": "sim",
            "potencia_gerador": 25,
            "autonomia_gerador": 8,
            "transferencia_gerador": (
                "QTA automatico atendendo iluminacao de emergencia, refrigeracao "
                "seletiva, portoes, bombas e circuito de seguranca."
            ),
            "aterramento_eletrico": (
                "Sistema TN-S com haste copperweld 3/4 x 2,40 m em anel, "
                "equipotencializacao no QGBT e no quadro de SPDA."
            ),
        },
        "hidraulica": {
            "tipo_edificacao": "Residencia unifamiliar",
            "numero_pavimentos": 2,
            "ocupacao_total": 8,
            "abastecimento": "mista",
            "reservatorio_inferior": 5000,
            "reservatorio_superior": 3000,
            "agua_quente": "sim",
            "materiais_hidraulicos": (
                "PPR para agua quente, PVC soldavel para agua fria, sistema de "
                "pressurizacao com bombas em paralelo e retorno de recirculacao."
            ),
        },
        "pluvial": {
            "area_contribuicao": 420,
            "coeficiente_escoamento": 0.85,
            "intensidade_chuva": 180,
            "tempo_retorno": 10,
            "destino_aguas": "Rede pluvial do condominio apos caixa de retenção",
            "sistema_drenagem": (
                "Calhas de aluminio, condutores PVC 100 mm, caixas de passagem, "
                "caixa de retenção 8 m3 com orificio de fundo e extravasor."
            ),
            "pontos_lancamento": "PV-01 no alinhamento frontal e PV-02 no limite lateral",
        },
        "sanitario": {
            "numero_contribuintes": 8,
            "rede_coletora": "sim",
            "ventilacao_sanitaria": (
                "Colunas de ventilacao primaria e secundaria conforme NBR 8160, "
                "com terminais acima da cobertura e sifonamento em todos os "
                "aparelhos sanitarios."
            ),
        },
        "spda": {
            "tipo_edificacao": "Residencia unifamiliar",
            "altura_edificacao": 9.5,
            "numero_pavimentos": 2,
            "analise_risco_spda": (
                "Analise de risco NBR 5419 indica necessidade de SPDA nivel III "
                "devido a localizacao em area aberta do condominio e presença de "
                "equipamentos eletronicos sensiveis."
            ),
            "nivel_protecao": "III",
            "metodo_spda": "Metodo da esfera rolante / malha",
            "subsistema_captacao": (
                "Malha de captacao com cabos de cobre nu 35 mm2 na cobertura e "
                "terminais aereos nos pontos salientes."
            ),
            "aterramento_spda": (
                "Anel de aterramento perimetral interligado as hastes e ao "
                "sistema de aterramento das instalacoes eletricas."
            ),
            "equipotencializacao": (
                "BEP no QGBT, ligacao de tubulacoes metalicas, trilhos e "
                "estruturas metalicas da cobertura."
            ),
        },
        "corpo_bombeiros": {
            "ocupacao_bombeiros": "Residencial unifamiliar (Grupo A)",
            "area_total_bombeiros": 312,
            "altura_edificacao": 9.5,
            "populacao_bombeiros": 12,
            "risco_incendio": "Baixo",
            "saidas_emergencia": (
                "Escada interna com largura 1,20 m, portas de saida com sentido "
                "de fuga, iluminacao de emergencia e sinalizacao fotoluminescente."
            ),
            "sistema_hidrantes": "nao_aplicavel",
            "sistemas_protecao": (
                "Extintores portateis conforme NBR 12693, detectores de fumaca "
                "nos dormitorios e central de alarme residencial."
            ),
        },
        "estrutura_concreto": {
            "tipo_estrutura": "Concreto armado moldado in loco — pavimentos e lajes nervuradas",
            "numero_pavimentos": 2,
            "fck": 30,
            "tipo_aco": "CA-50",
            "cobrimento": 3.0,
            "sistema_estrutural": (
                "Pilares, vigas e lajes nervuradas; paredes de contraventamento "
                "em alvenaria estrutural nos eixos A e D."
            ),
            "cargas_adotadas": (
                "Permanentes conforme NBR 6120; sobrecarga salas 2,0 kN/m2; "
                "suites 1,5 kN/m2; terraço 3,0 kN/m2; vento NBR 6123."
            ),
            "controle_execucao": (
                "Controle tecnologico do concreto (moldagem de corpos de prova), "
                "conferencia de armaduras e fôrmas antes da concretagem."
            ),
        },
        "fundacoes": {
            "tipo_fundacao": "Sapatas isoladas e vigas de baldrame",
            "sondagem_disponivel": "sim",
            "tipo_solo": "Silte arenoso compacto a partir de 1,80 m",
            "tensao_admissivel": 250,
            "nivel_agua": 4.5,
            "cargas_fundacao": (
                "Reacoes de pilares entre 180 kN e 620 kN; sapatas dimensionadas "
                "com tensao admissivel 250 kPa e lastro de concreto magro."
            ),
            "criterios_execucao": (
                "Escavacao mecanizada, limpeza do fundo, lastro 5 cm, "
                "impermeabilizacao das faces e reaterro compactado em camadas."
            ),
        },
    }


def _galpao_disciplines() -> Dict[str, Dict[str, Any]]:
    return {
        "arquitetura": {
            "tipo_edificacao": "Galpao industrial / logistico",
            "programa_necessidades": (
                "Area de armazenagem 850 m2, docas, escritorio administrativo, "
                "vestiarios, refeitorio, casa de bombas, subestacao abrigada e "
                "patio de manobra."
            ),
            "numero_pavimentos": 1,
            "area_terreno": 3200,
            "area_construida": 1050,
            "sistema_construtivo": "Estrutura metalica + fechamento em painel termoisolante",
            "acabamentos": (
                "Piso industrial concreto polido fck 30 MPa, pintura epoxi em "
                "areas administrativas, forro mineral nos escritorios."
            ),
            "acessibilidade": (
                "Rampas de acesso as docas administrativas, sanitarios PNE, "
                "vagas reservadas e rota acessivel ate o escritorio."
            ),
        },
        "eletrica": {
            "tipo_edificacao": "Galpao industrial",
            "uso_edificacao": "Armazenagem e expedicao",
            "tensao_fornecimento": "220_380",
            "potencia_instalada": 185.0,
            "carga_demanda": 120.0,
            "padrao_entrada": "Entrada em media tensao com medicao no primario",
            "gerador": "sim",
            "potencia_gerador": 150,
            "autonomia_gerador": 12,
            "transferencia_gerador": (
                "QTA para iluminacao de emergencia, portoes, bombas de incendio, "
                "servidores e circuito de refrigeracao de TI."
            ),
            "aterramento_eletrico": (
                "Malha de aterramento sob o piso industrial, conexao ao SPDA e "
                "a subestacao, condutores de cobre nu 50/70 mm2."
            ),
        },
        "hidraulica": {
            "tipo_edificacao": "Galpao industrial",
            "numero_pavimentos": 1,
            "ocupacao_total": 45,
            "abastecimento": "rede_publica",
            "reservatorio_inferior": 20000,
            "reservatorio_superior": 5000,
            "agua_quente": "nao",
            "materiais_hidraulicos": (
                "PVC soldavel e PEAD para agua fria; reservatorio elevado metalico "
                "para combate a incendio e consumo."
            ),
        },
        "pluvial": {
            "area_contribuicao": 1400,
            "coeficiente_escoamento": 0.9,
            "intensidade_chuva": 160,
            "tempo_retorno": 25,
            "destino_aguas": "Sistema de drenagem do condominio industrial",
            "sistema_drenagem": (
                "Calhas industriais, condutores 150 mm, canaletas de piso no patio "
                "e caixa de sedimentacao antes do lancamento."
            ),
            "pontos_lancamento": "CL-01 e CL-02 na divisa com via interna do condominio",
        },
        "sanitario": {
            "numero_contribuintes": 45,
            "rede_coletora": "sim",
            "ventilacao_sanitaria": (
                "Rede coletora com caixas de gordura no refeitorio, ventilacao "
                "primaria nas colunas e inspeções a cada 20 m."
            ),
        },
        "spda": {
            "tipo_edificacao": "Galpao metalico",
            "altura_edificacao": 12.0,
            "numero_pavimentos": 1,
            "analise_risco_spda": (
                "Analise NBR 5419 indica SPDA nivel II pela altura, area coberta "
                "e risco de parada operacional."
            ),
            "nivel_protecao": "II",
            "metodo_spda": "Componentes naturais da estrutura metalica + descidas dedicadas",
            "subsistema_captacao": (
                "Aproveitamento das terças e cumeeiras como captadores naturais, "
                "com interligacoes soldadas e terminais nos lanternins."
            ),
            "aterramento_spda": (
                "Anel perimetral com hastes copperweld e conexao a malha do piso."
            ),
            "equipotencializacao": (
                "Barramentos de equipotencializacao nas colunas, docas, racks e "
                "quadros eletricos."
            ),
        },
        "corpo_bombeiros": {
            "ocupacao_bombeiros": "Industrial / deposito (Grupo I/J conforme IT local)",
            "area_total_bombeiros": 1050,
            "altura_edificacao": 12.0,
            "populacao_bombeiros": 60,
            "risco_incendio": "Medio",
            "saidas_emergencia": (
                "Duas saidas opostas com portas corta-fogo, corredores com largura "
                "minima 1,20 m, iluminacao e sinalizacao de emergencia."
            ),
            "sistema_hidrantes": "sim",
            "sistemas_protecao": (
                "Hidrantes internos e externos, sprinklers nas areas de risco, "
                "extintores, detecção e alarme endereçavel, brigada treinada."
            ),
        },
        "estrutura_metalica": {
            "tipo_estrutura": "Porticos metalicos em perfil soldado",
            "vao_maximo": 25,
            "area_cobertura": 1050,
            "aco_estrutural": "ASTM A572 Grau 50 / equivalente",
            "proteccao_corrosao": "Jateamento SA 2.1/2 + primer epoxi + poliuretano",
            "ligacoes": "Parafusadas de alta resistencia com chumbadores quimicos nas bases",
            "cargas_adotadas": (
                "Peso proprio, sobrecarga de cobertura 0,25 kN/m2, vento NBR 6123, "
                "ponte rolante futura 5 t considerada nas colunas centrais."
            ),
            "contraventamento": (
                "Contraventamento em X nas faces longitudinais e transversais, "
                "com tirantes e cantoneiras."
            ),
        },
        "fundacoes": {
            "tipo_fundacao": "Blocos sobre estacas helice continua",
            "sondagem_disponivel": "sim",
            "tipo_solo": "Argila siltosa mole ate 6 m; areia media compacta abaixo",
            "tensao_admissivel": 0,
            "nivel_agua": 3.2,
            "cargas_fundacao": (
                "Cargas de pilares metalicos ate 900 kN; estacas helices 400 mm "
                "com capacidade de trabalho 450 kN."
            ),
            "criterios_execucao": (
                "Controle de torque e profundidade, ensaio de integridade, "
                "blocos com arrasamento e chumbadores posicionados em gabarito."
            ),
        },
        "pavimentacao": {
            "tipo_obra": "Patio de manobra e acesso de caminhoes",
            "extensao": 0.18,
            "cbr_campo": 12,
            "espessura_base": 20,
            "espessura_revestimento": 7,
            "tipo_asfalto": "CBUQ CAP 50/70",
            "penetracao_asfalto": "50/70",
            "etapas_execucao": (
                "Regularizacao do subleito, base granular brita graduada, imprimacao, "
                "CBUQ em duas camadas com controle de densidade e temperatura."
            ),
        },
        "subestacao": {
            "tipo_subestacao": "Abrigada, cabine primaria compacta",
            "potencia_instalada": 300,
            "tensao_primaria": 13.8,
            "tensao_secundaria": 0.38,
            "demanda_maxima": 220,
            "potencia_transformador": 300,
            "equipamentos": (
                "Transformador a oleo 300 kVA, seccionadora, religador, TP/TC de "
                "medicao, quadro de media e baixa tensao."
            ),
            "sistemas_protecao": (
                "Reles de sobrecorrente 50/51, diferencial do transformador, "
                "DPS e intertravamentos de porta."
            ),
        },
    }


DEMO_PROJECTS: List[Dict[str, Any]] = [
    {
        "slug": "residencia-alto-padrao-alphaville-go",
        "title": "Residência Alto Padrão — Alphaville Goiás",
        "subtitle": "Casa unifamiliar ~312 m² em condomínio fechado",
        "summary": (
            "Projeto-modelo completo de residência de alto padrão com memoriais "
            "multidisciplinares (arquitetura, estruturas, instalações, SPDA e "
            "segurança contra incêndio). Demonstra o pacote DOCX/PDF gerado pela plataforma."
        ),
        "typology": "residencia",
        "area_m2": 312,
        "highlights": [
            "312 m² construídos em terreno de 540 m²",
            "9 disciplinas técnicas preenchidas",
            "Gerador, SPDA nível III e reservatórios dimensionados",
            "Entrega: ZIP com memoriais individuais + documento único",
        ],
        "scope_note": (
            "A plataforma gera memoriais descritivos profissionais (DOCX/PDF). "
            "Plantas CAD/DWG e detalhes construtivos gráficos não fazem parte deste MVP."
        ),
        "enterprise": {
            "name": "Residência Alto Padrão — Alphaville Goiás",
            "description": (
                "Residência unifamiliar de alto padrão em condomínio fechado, "
                "Goiânia/GO, com programa completo de lazer e suporte técnico."
            ),
            "shared_data": {
                "localizacao": "Alameda das Figueiras, Qd. 12, Lt. 08 — Alphaville Goiás",
                "municipio": "Goiânia",
                "uf": "GO",
                "area_construida": 312,
                "numero_pavimentos": 2,
                "contratante": "Familia Ribeiro Campos",
            },
        },
        "mode": "both",
        "professional": PROFESSIONAL_DEMO,
        "disciplines_data": _residencia_disciplines(),
    },
    {
        "slug": "galpao-logistico-aparecida-go",
        "title": "Galpão Logístico — Aparecida de Goiânia",
        "subtitle": "Galpão industrial ~1.050 m² com pátio e subestação",
        "summary": (
            "Projeto-modelo de galpão logístico com estrutura metálica, fundações "
            "em estacas, subestação abrigada, pavimentação do pátio e memorial de "
            "segurança contra incêndio completo."
        ),
        "typology": "galpao",
        "area_m2": 1050,
        "highlights": [
            "1.050 m² de área construída + pátio de manobra",
            "11 disciplinas (inclui pavimentação e subestação)",
            "SPDA nível II e hidrantes aplicáveis",
            "Pacote ZIP multidisciplinar para validação profissional",
        ],
        "scope_note": (
            "A plataforma gera memoriais descritivos profissionais (DOCX/PDF). "
            "Plantas CAD/DWG e detalhes construtivos gráficos não fazem parte deste MVP."
        ),
        "enterprise": {
            "name": "Galpão Logístico — Polo Industrial Aparecida",
            "description": (
                "Galpão para armazenagem e expedição com docas, escritórios, "
                "subestação abrigada e pátio asfaltado para caminhões."
            ),
            "shared_data": {
                "localizacao": "Via Interna 03, Lote 22 — Polo Industrial",
                "municipio": "Aparecida de Goiânia",
                "uf": "GO",
                "area_construida": 1050,
                "numero_pavimentos": 1,
                "contratante": "Horizonte Logística S.A.",
            },
        },
        "mode": "both",
        "professional": {
            **PROFESSIONAL_DEMO,
            "full_name": "Eng. Rafael Duarte Nogueira",
            "professional_title": "Engenheiro Eletricista / Mecânico",
            "crea_number": "67890/D",
            "art_number": "ART-2026-009103",
        },
        "disciplines_data": _galpao_disciplines(),
    },
]


def list_demos() -> List[Dict[str, Any]]:
    result = []
    for demo in DEMO_PROJECTS:
        result.append(
            {
                "slug": demo["slug"],
                "title": demo["title"],
                "subtitle": demo["subtitle"],
                "summary": demo["summary"],
                "typology": demo["typology"],
                "area_m2": demo["area_m2"],
                "highlights": demo["highlights"],
                "scope_note": demo["scope_note"],
                "disciplines": sorted(demo["disciplines_data"].keys()),
                "discipline_count": len(demo["disciplines_data"]),
            }
        )
    return result


def get_demo(slug: str) -> Optional[Dict[str, Any]]:
    for demo in DEMO_PROJECTS:
        if demo["slug"] == slug:
            return deepcopy(demo)
    return None


def _template_id_for_discipline(db: Session, discipline: str) -> Optional[int]:
    subcategory = DISCIPLINE_TO_SUBCATEGORY.get(discipline)
    query = db.query(EngineeringTemplate).filter(EngineeringTemplate.is_public == 1)
    if subcategory:
        match = query.filter(EngineeringTemplate.subcategory == subcategory).first()
        if match:
            return match.id
    # fallback: any public in preferred category map via memorials would be better;
    # keep simple — first ready public with matching subcategory prefix
    for template in query.all():
        if (template.subcategory or "") == (subcategory or ""):
            return template.id
    return None


def build_plan_payload(db: Session, slug: str) -> Dict[str, Any]:
    demo = get_demo(slug)
    if demo is None:
        raise KeyError(slug)

    disciplines = []
    missing_templates = []
    for discipline, data in demo["disciplines_data"].items():
        if get_questionnaire(discipline) is None:
            continue
        template_id = _template_id_for_discipline(db, discipline)
        if template_id is None:
            missing_templates.append(discipline)
            continue
        disciplines.append(
            {
                "discipline": discipline,
                "template_id": template_id,
                "data": data,
            }
        )

    if missing_templates:
        raise RuntimeError(
            "Templates oficiais ausentes para: " + ", ".join(missing_templates)
        )
    if not disciplines:
        raise RuntimeError("Nenhuma disciplina resolvida para o demo.")

    return {
        "enterprise": demo["enterprise"],
        "mode": demo.get("mode") or "both",
        "disciplines": disciplines,
        "professional": demo["professional"],
        "status": "memorial_gerado",
        "demo_slug": demo["slug"],
        "demo_meta": {
            "title": demo["title"],
            "scope_note": demo["scope_note"],
        },
    }
