"""Secoes densas — arquitetura e eletrica."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def sec(title: str, content: str, subsections: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"title": title, "content": content.strip()}
    if subsections:
        item["subsections"] = subsections
    return item


def sub(title: str, content: str) -> Dict[str, str]:
    return {"title": title, "content": content.strip()}


ARQUITETURA = {
    "sections": [
        sec(
            "1. OBJETO E ESCOPO DO MEMORIAL",
            """Este Memorial Descritivo Arquitetônico apresenta as diretrizes de projeto, especificações construtivas e critérios de desempenho adotados para a edificação do tipo {{tipo_edificacao}}, situada em {{localizacao}}, município de {{municipio}}/{{uf}}.

O documento integra o conjunto de peças técnicas necessárias à análise por órgãos competentes, à compatibilização multidisciplinar e à execução da obra, devendo ser lido em conjunto com plantas, cortes, fachadas, detalhamentos e memoriais das demais disciplinas.

Escopo contemplado: organização espacial, sistema construtivo, desempenho funcional, acessibilidade, acabamentos e premissas de compatibilização com estrutura, fundações, instalações e segurança contra incêndio.""",
            [
                sub(
                    "1.1 Premissas de projeto",
                    """Adotam-se premissas de conforto ambiental, racionalização construtiva, manutenção facilitada e aderência à legislação urbanística local. Qualquer alteração de programa, área ou sistema construtivo exigirá revisão deste memorial e das peças gráficas correlatas.""",
                )
            ],
        ),
        sec(
            "2. IDENTIFICAÇÃO DO EMPREENDIMENTO",
            """A edificação ocupa terreno de {{area_terreno}} m², com área construída total de {{area_construida}} m², distribuída em {{numero_pavimentos}} pavimento(s). O uso pretendido é {{tipo_edificacao}}.

A implantação observa afastamentos, taxa de ocupação e parâmetros urbanísticos aplicáveis ao zoneamento de {{municipio}}. A acessibilidade viária e pedonal foi considerada desde a concepção do partido arquitetônico.""",
        ),
        sec(
            "3. PROGRAMA DE NECESSIDADES E ORGANIZAÇÃO ESPACIAL",
            """O programa de necessidades desenvolvido contempla:

{{programa_necessidades}}

A organização espacial prioriza fluxos claros entre áreas sociais, íntimas, de serviço e técnicas, com ventilação e iluminação naturais sempre que possível, e reserva de shafts e casas de máquinas dimensionados para as instalações previstas.""",
            [
                sub(
                    "3.1 Circulações e hierarquia espacial",
                    """As circulações horizontais e verticais foram dimensionadas para o fluxo estimado de usuários e mobiliário e, quando aplicável, para requisitos de saída de emergência da disciplina de segurança contra incêndio.""",
                )
            ],
        ),
        sec(
            "4. SISTEMA CONSTRUTIVO",
            """O sistema construtivo adotado é: {{sistema_construtivo}}.

A escolha considera desempenho estrutural, isolamento térmico e acústico, prazo de execução, disponibilidade regional de materiais e facilidade de manutenção. As interfaces com fundações, estrutura e vedações devem ser detalhadas em projeto executivo antes do início da obra.""",
            [
                sub(
                    "4.1 Vedações e envoltória",
                    """As vedações verticais e a envoltória devem garantir estanqueidade, desempenho térmico compatível com a NBR 15575 (quando habitacional) e adequada interface com esquadrias, impermeabilizações e sistemas de fachada.""",
                )
            ],
        ),
        sec(
            "5. ESPECIFICAÇÕES DE ACABAMENTOS E REVESTIMENTOS",
            """Os acabamentos e revestimentos previstos são:

{{acabamentos}}

As especificações finais de fabricantes, cores e texturas poderão ser refinadas em caderno de encargos, mantendo desempenho equivalente. Superfícies molháveis receberão tratamento impermeabilizante adequado ao uso.""",
        ),
        sec(
            "6. ACESSIBILIDADE E DESEMPENHO",
            """As soluções de acessibilidade previstas contemplam:

{{acessibilidade}}

Observa-se a ABNT NBR 9050 quanto a rotas acessíveis, desníveis, sanitários, sinalização e vagas reservadas, no que for aplicável à tipologia. Para edificações habitacionais, a NBR 15575 orienta isolamento, estanqueidade e durabilidade.""",
        ),
        sec(
            "7. CONFORTO AMBIENTAL E SUSTENTABILIDADE",
            """O partido arquitetônico busca ventilação cruzada, controle de insolação e redução de cargas térmicas. Recomenda-se esquadrias com desempenho compatível e iluminância natural adequada aos ambientes de permanência prolongada.

Medidas de racionalização de água e energia devem ser compatibilizadas com os projetos de instalações (medição setorizada, iluminação eficiente, eventual aproveitamento pluvial).""",
        ),
        sec(
            "8. COMPATIBILIZAÇÃO MULTIDISCIPLINAR",
            """Antes da execução, este projeto deverá ser compatibilizado com estrutura, fundações, instalações elétricas, hidrossanitárias, SPDA, segurança contra incêndio e demais complementares. Conflitos de shafts, vãos, peitoris, lajes e cargas especiais devem ser resolvidos formalmente, com registro técnico.""",
        ),
        sec(
            "9. DIRETRIZES DE EXECUÇÃO E CONTROLE",
            """A execução observará boas práticas de canteiro, proteção de elementos acabados, controle dimensional de vãos e níveis, e armazenamento adequado de materiais. Recomenda-se plano de qualidade com inspeções por etapa e registro fotográfico.

Não serão aceitas substituições de sistema construtivo ou de desempenho sem anuência do responsável técnico e revisão documental.""",
        ),
        sec(
            "10. DISPOSIÇÕES FINAIS",
            """Este memorial complementa as peças gráficas do projeto arquitetônico e não as substitui. Em caso de divergência, prevalece a interpretação mais restritiva sob o ponto de vista de segurança e desempenho, mediante esclarecimento do autor do projeto.

Alterações de uso, ocupação ou geometria invalidam parcialmente as premissas aqui descritas e exigem atualização do memorial.""",
        ),
    ],
    "normas": [
        "ABNT NBR 6492 — Documentação técnica para projetos arquitetônicos",
        "ABNT NBR 9050 — Acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos",
        "ABNT NBR 15575 — Edificações habitacionais — Desempenho",
        "ABNT NBR 16636-1 — Elaboração e desenvolvimento de serviços técnicos especializados de projetos",
        "Código de Obras e legislação urbanística do município de implantação",
    ],
    "calculations": [],
}


ELETRICA = {
    "sections": [
        sec(
            "1. OBJETO E ABRANGÊNCIA",
            """O presente Memorial Descritivo das Instalações Elétricas descreve critérios de projeto, dimensionamento e execução das instalações de baixa tensão da edificação do tipo {{tipo_edificacao}}, com uso {{uso_edificacao}}, localizada em {{localizacao}}.

Abrange entrada de energia, medição, distribuição, circuitos terminais, proteções, aterramento, iluminação, tomadas, força e, quando previsto, geração auxiliar. O projeto observa a ABNT NBR 5410 e as normas da concessionária local.""",
        ),
        sec(
            "2. DADOS DE FORNECIMENTO E CARGAS",
            """A tensão de fornecimento adotada é {{tensao_fornecimento}}. A potência instalada total estimada é de {{potencia_instalada}} kW, com demanda calculada de {{carga_demanda}} kW, considerando fatores de demanda adequados ao uso {{uso_edificacao}}.

O padrão de entrada especificado é: {{padrao_entrada}}.

Os quadros de distribuição serão setorizados por pavimento/uso, com reserva de espaço para expansão mínima de 20% em número de polos, salvo restrição física justificada.""",
            [
                sub(
                    "2.1 Critérios de demanda",
                    """A demanda foi estimada a partir do levantamento de cargas de iluminação, tomadas de uso geral, equipamentos específicos, climatização e cargas especiais. Revisões de carga durante a obra devem ser comunicadas ao projetista.""",
                )
            ],
        ),
        sec(
            "3. ENTRADA DE ENERGIA, MEDIÇÃO E PROTEÇÃO GERAL",
            """A entrada de serviço será executada conforme padrão da concessionária, com eletrodutos, condutores e dispositivos de proteção dimensionados para a demanda e o tipo de fornecimento.

No quadro geral (QGBT) serão previstos dispositivo de proteção geral, DPS quando aplicável pela avaliação de risco, barramentos dimensionados e identificação clara dos circuitos.""",
        ),
        sec(
            "4. DISTRIBUIÇÃO, CONDUTORES E ELETRODUTOS",
            """Os circuitos terminais serão discriminados em diagramas unifilares, com seção mínima conforme NBR 5410 e queda de tensão limitada aos valores normativos. Condutores de cobre com isolação adequada à temperatura e ao meio.

Eletrodutos e eletrocalhas terão taxa de ocupação controlada, com caixas de passagem acessíveis e trajetos que evitem interferência com estrutura e hidráulica.""",
        ),
        sec(
            "5. ILUMINAÇÃO E TOMADAS",
            """A iluminação artificial será dimensionada para níveis de iluminância compatíveis com o uso dos ambientes, priorizando luminárias eficientes e circuitos setorizados. Tomadas de uso geral (TUG) e específicas (TUE) seguirão a densidade mínima normativa e as necessidades do programa arquitetônico.

Em áreas molhadas e externas serão adotados dispositivos DR e graus de proteção IP compatíveis com a exposição.""",
        ),
        sec(
            "6. GERAÇÃO AUXILIAR E TRANSFERÊNCIA",
            """Presença de gerador: {{gerador}}.

Quando aplicável: potência {{potencia_gerador}} kVA; autonomia estimada {{autonomia_gerador}} h. Transferência e cargas atendidas: {{transferencia_gerador}}.

O sistema de transferência (QTA) deverá garantir intertravamento que impeça paralelismo indevido com a rede, sinalização de estado e manutenção segura.""",
        ),
        sec(
            "7. ATERRAMENTO E EQUIPOTENCIALIZAÇÃO",
            """Sistema de aterramento previsto:

{{aterramento_eletrico}}

Será prevista equipotencialização principal (BEP) e ligações suplementares nos ambientes exigidos pela NBR 5410, com continuidade verificável no comissionamento.""",
        ),
        sec(
            "8. PROTEÇÕES, SELETIVIDADE E COORDENAÇÃO",
            """Os dispositivos de proteção (disjuntores, DR, DPS) serão selecionados para sobrecarga, curto-circuito e choque elétrico, buscando seletividade entre proteção geral e terminais. Capacidades de interrupção devem ser compatíveis com a corrente de curto-circuito estimada no ponto de instalação.""",
        ),
        sec(
            "9. ENSAIOS, COMISSIONAMENTO E ENTREGA",
            """Antes da energização definitiva, deverão ser realizados ensaios de continuidade, resistência de isolação, polaridade, disparo de DR, verificação de aterramento e inspeção visual conforme NBR 5410. Recomenda-se termo de comissionamento com registro de medições.""",
        ),
        sec(
            "10. DISPOSIÇÕES FINAIS",
            """Este memorial deve ser interpretado em conjunto com plantas, diagramas unifilares e quadro de cargas. Alterações de carga ou de layout elétrico sem revisão do projetista comprometem a validade do dimensionamento.""",
        ),
    ],
    "normas": [
        "ABNT NBR 5410 — Instalações elétricas de baixa tensão",
        "ABNT NBR 5419 — Proteção contra descargas atmosféricas (interfaces)",
        "Normas e padrões da concessionária local de energia",
        "NR-10 — Segurança em instalações e serviços em eletricidade",
    ],
    "calculations": [],
}
