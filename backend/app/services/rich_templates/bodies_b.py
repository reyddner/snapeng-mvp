"""Secoes densas — hidraulica, pluvial, sanitario, SPDA, bombeiros."""

from __future__ import annotations

from .bodies_a import sec, sub

HIDRAULICA = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este Memorial Descritivo das Instalações Hidráulicas de água fria (e quente, quando aplicável) estabelece critérios de projeto e execução para a edificação do tipo {{tipo_edificacao}}, com {{numero_pavimentos}} pavimento(s) e ocupação estimada de {{ocupacao_total}} pessoas, localizada em {{localizacao}}.""",
        ),
        sec(
            "2. ABASTECIMENTO E RESERVAÇÃO",
            """A fonte de abastecimento adotada é: {{abastecimento}}.

Volumes de reservação previstos: reservatório inferior {{reservatorio_inferior}} L; reservatório superior {{reservatorio_superior}} L. A reservação considera consumo diário, reserva de emergência e, quando houver, parcela de combate a incêndio definida na disciplina específica.

Os reservatórios deverão possuir acesso para inspeção, extravasor, limpeza, ventilação e proteção sanitária conforme boas práticas e normas aplicáveis.""",
            [
                sub(
                    "2.1 Pressurização",
                    """Quando a pressão disponível da rede ou da reservação elevada for insuficiente, será previsto sistema de pressurização com bombas, barrilete e dispositivos de proteção (válvula de retenção, manômetro, proteção contra falta d'água).""",
                )
            ],
        ),
        sec(
            "3. REDES DE DISTRIBUIÇÃO",
            """As redes de água fria serão executadas com materiais compatíveis com pressão de serviço e qualidade da água. Traçados priorizam shafts acessíveis, evitarão travessias indevidas de elementos estruturais e terão registros setoriais por pavimento/zona.

Materiais e sistemas previstos:

{{materiais_hidraulicos}}""",
        ),
        sec(
            "4. ÁGUA QUENTE",
            """Sistema de água quente: {{agua_quente}}.

Quando aplicável, o aquecimento, a recirculação e o isolamento térmico das tubulações deverão garantir conforto, eficiência energética e segurança contra queimaduras, com misturadores e dispositivos de alívio conforme especificação de projeto.""",
        ),
        sec(
            "5. LOUÇAS, METAIS E PONTOS DE CONSUMO",
            """Os pontos de consumo serão compatibilizados com o layout arquitetônico (lavatórios, duchas, pias, tanques, pontos de máquinas). Vazões e pressões mínimas nos pontos de utilização observarão a NBR 5626. Em áreas de acessibilidade, serão previstos metais e alturas conforme NBR 9050.""",
        ),
        sec(
            "6. PROTEÇÃO SANITÁRIA E CONTROLE DE QUALIDADE",
            """Serão evitadas conexões cruzadas e retrossifonagem. Pontos sujeitos a contaminação receberão dispositivos antisifonagem. Recomenda-se limpeza e desinfecção dos reservatórios antes da entrada em operação, com laudo quando exigido.""",
        ),
        sec(
            "7. ENSAIOS E ENTREGA",
            """As tubulações serão ensaiadas quanto a estanqueidade sob pressão antes do fechamento de shafts e forros. Na entrega, deverão constar identificações de registros, esquema de barrilete e orientações de manutenção periódica.""",
        ),
        sec(
            "8. DISPOSIÇÕES FINAIS",
            """Este memorial complementa plantas, esquemas isométricos e memorial de cálculo hidráulico. Alterações de ocupação, número de pontos ou pressão disponível exigem redimensionamento.""",
        ),
    ],
    "normas": [
        "ABNT NBR 5626 — Instalações prediais de água fria",
        "ABNT NBR 7198 — Projeto e execução de instalações prediais de água quente",
        "ABNT NBR 9050 — Acessibilidade (pontos e metais)",
        "Portaria de vigilância sanitária local para reservatórios (quando aplicável)",
    ],
    "calculations": [],
}

PLUVIAL = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este memorial descreve o sistema de drenagem de águas pluviais da edificação/área em {{localizacao}}, com área de contribuição de {{area_contribuicao}} m², coeficiente de escoamento {{coeficiente_escoamento}}, intensidade de chuva de projeto {{intensidade_chuva}} mm/h e tempo de retorno de {{tempo_retorno}} anos.""",
        ),
        sec(
            "2. CRITÉRIOS HIDROLÓGICOS",
            """O dimensionamento adota método racional ou equivalente, com vazão de projeto proporcional à área impermeabilizada e à intensidade pluviométrica local. O tempo de retorno foi escolhido conforme criticidade da ocupação e diretrizes municipais.

Recomenda-se verificar calhas, condutores, canaletas e dispositivos de amortecimento para a vazão de projeto, com folga operacional para manutenção.""",
        ),
        sec(
            "3. SISTEMA DE CAPTAÇÃO E CONDUÇÃO",
            """Sistema de drenagem previsto:

{{sistema_drenagem}}

Calhas e condutores serão executados com caimento adequado, juntas estanques e dispositivos de limpeza. Evitar-se-á lançamento direto sobre passeios sem dissipação.""",
        ),
        sec(
            "4. DESTINO DAS ÁGUAS E PONTOS DE LANÇAMENTO",
            """Destino das águas pluviais: {{destino_aguas}}.

Pontos de lançamento: {{pontos_lancamento}}.

Quando houver exigência municipal, serão previstos dispositivos de retenção, infiltração ou tratamento preliminar (caixa de areia/sedimentação) antes do lançamento na rede pública.""",
        ),
        sec(
            "5. INTERFACES E MANUTENÇÃO",
            """A drenagem será compatibilizada com impermeabilização de lajes, paisagismo e pavimentação. Deve haver acesso para limpeza de caixas e condutores. A manutenção periódica é condição para o desempenho hidráulico de longo prazo.""",
        ),
        sec(
            "6. DISPOSIÇÕES FINAIS",
            """Alterações de impermeabilização do terreno ou de cotas de lançamento invalidam o dimensionamento e exigem revisão do projeto pluvial.""",
        ),
    ],
    "normas": [
        "ABNT NBR 10844 — Instalações prediais de águas pluviais",
        "Diretrizes de drenagem urbana do município",
        "Instruções da concessionária/órgão gestor de drenagem (quando houver)",
    ],
    "calculations": [],
}

SANITARIO = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este Memorial Descritivo das Instalações Sanitárias de esgoto predial define critérios para coleta, ventilação e disposição dos efluentes da edificação em {{localizacao}}, considerando {{numero_contribuintes}} contribuintes.""",
        ),
        sec(
            "2. SISTEMA DE COLETA",
            """Existência de rede coletora pública: {{rede_coletora}}.

As tubulações de esgoto sanitário serão executadas com caimento normativo, juntas adequadas, caixas de inspeção/gordura quando necessárias e ramais dimensionados pela unidade de Hunter ou método equivalente da NBR 8160.""",
        ),
        sec(
            "3. TRATAMENTO E DISPOSIÇÃO (QUANDO APLICÁVEL)",
            """Quando não houver rede pública, o sistema de tratamento previsto é: {{sistema_tratamento}}.

Vazão diária estimada: {{vazao_diaria}} L/dia. Destino do efluente tratado: {{destino_efluente}}.

O sistema deverá observar normas ambientais e exigências do órgão licenciador, com acesso para manutenção e limpeza de fossa/filtro/sumidouro ou ETE compacta.""",
        ),
        sec(
            "4. VENTILAÇÃO SANITÁRIA",
            """Solução de ventilação sanitária:

{{ventilacao_sanitaria}}

A ventilação primária e secundária evitará pressão negativa excessiva nos desconectores e o escape de gases para ambientes ocupados, com terminais acima da cobertura conforme NBR 8160.""",
        ),
        sec(
            "5. ENSAIOS E ENTREGA",
            """As tubulações serão submetidas a ensaio de estanqueidade com água ou ar antes do fechamento. Caixas sifonadas e desconectores devem permanecer acessíveis para manutenção.""",
        ),
        sec(
            "6. DISPOSIÇÕES FINAIS",
            """Este memorial complementa plantas de esgoto e detalhes de caixas. Mudança do número de aparelhos ou do destino do efluente exige revisão do projeto.""",
        ),
    ],
    "normas": [
        "ABNT NBR 8160 — Sistemas prediais de esgoto sanitário — Projeto e execução",
        "ABNT NBR 7229 — Projeto, construção e operação de sistemas de tanques sépticos (quando aplicável)",
        "ABNT NBR 13969 — Tanques sépticos — Unidades de tratamento complementar (quando aplicável)",
        "Legislação ambiental estadual/municipal",
    ],
    "calculations": [],
}

SPDA = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este memorial apresenta a solução de Sistema de Proteção contra Descargas Atmosféricas (SPDA) para a edificação do tipo {{tipo_edificacao}}, com altura {{altura_edificacao}} m e {{numero_pavimentos}} pavimento(s), localizada em {{localizacao}}, conforme ABNT NBR 5419.""",
        ),
        sec(
            "2. ANÁLISE DE RISCO",
            """Resultado da análise de risco:

{{analise_risco_spda}}

Com base na análise, adotou-se o nível de proteção {{nivel_protecao}}.""",
        ),
        sec(
            "3. MÉTODO E SUBSISTEMAS",
            """Método do SPDA: {{metodo_spda}}.

Captação: {{subsistema_captacao}}.

Descidas serão distribuídas perimetralmente com espaçamento compatível ao nível de proteção, com conexões inspecionáveis e identificação.""",
        ),
        sec(
            "4. ATERRAMENTO E EQUIPOTENCIALIZAÇÃO",
            """Aterramento: {{aterramento_spda}}.

Equipotencialização: {{equipotencializacao}}.

A integração com o aterramento das instalações elétricas será feita de modo a evitar diferenças de potencial perigosas, observando a NBR 5419 e a NBR 5410.""",
        ),
        sec(
            "5. DPS E PROTEÇÃO INTERNA",
            """Será avaliada a necessidade de dispositivos de proteção contra surtos (DPS) nas entradas de energia e sinal, coordenados por zona de proteção, conforme o risco e a criticidade dos equipamentos.""",
        ),
        sec(
            "6. INSPEÇÃO E MANUTENÇÃO",
            """Após a instalação, deverá ser emitido relatório de inspeção com medições de continuidade e verificação visual. Inspeções periódicas são recomendadas, especialmente após descargas ou intervenções na cobertura.""",
        ),
        sec(
            "7. DISPOSIÇÕES FINAIS",
            """Alterações de altura, volume edificado ou instalação de antenas/painéis sem revisão do SPDA podem invalidar o nível de proteção adotado.""",
        ),
    ],
    "normas": [
        "ABNT NBR 5419 — Proteção contra descargas atmosféricas (Partes 1 a 4)",
        "ABNT NBR 5410 — Instalações elétricas de baixa tensão (interfaces de aterramento)",
    ],
    "calculations": [],
}

CORPO_BOMBEIROS = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este Memorial de Segurança contra Incêndio e Pânico descreve as medidas de proteção ativa e passiva previstas para a edificação de ocupação {{ocupacao_bombeiros}}, com área total {{area_total_bombeiros}} m², altura {{altura_edificacao}} m e população {{populacao_bombeiros}} pessoas, em {{localizacao}}.""",
        ),
        sec(
            "2. CLASSIFICAÇÃO E RISCO",
            """Classificação de risco de incêndio: {{risco_incendio}}.

A classificação observa a legislação do Corpo de Bombeiros da unidade federativa e as Instruções Técnicas aplicáveis à ocupação e à altura da edificação.""",
        ),
        sec(
            "3. SAÍDAS DE EMERGÊNCIA",
            """Descrição das saídas de emergência:

{{saidas_emergencia}}

As rotas de fuga terão largura, distanciamento e sinalização conformes à IT/NBR aplicável, com portas na sentido do fluxo e iluminação de emergência.""",
        ),
        sec(
            "4. SISTEMA DE HIDRANTES E PROTEÇÃO ATIVA",
            """Sistema de hidrantes: {{sistema_hidrantes}}.

Demais sistemas de proteção:

{{sistemas_protecao}}

Extintores serão distribuídos conforme risco e carga de incêndio, com sinalização e acesso desimpedido.""",
        ),
        sec(
            "5. SINALIZAÇÃO, ILUMINAÇÃO E DETECÇÃO",
            """Serão previstos sistemas de sinalização fotoluminescente/adequada, iluminação de emergência e, quando exigido, detecção e alarme de incêndio endereçável ou convencional conforme a IT local.""",
        ),
        sec(
            "6. GESTÃO E MANUTENÇÃO",
            """Após a aprovação e execução, a edificação deverá manter plano de manutenção dos sistemas de segurança contra incêndio, treinamento de brigada quando exigido e registros de inspeção.""",
        ),
        sec(
            "7. DISPOSIÇÕES FINAIS",
            """Este memorial subsidia o processo de AVCB/ALCB junto ao Corpo de Bombeiros e deve ser compatibilizado com arquitetura, hidráulica de incêndio e elétrica de emergência.""",
        ),
    ],
    "normas": [
        "Instruções Técnicas do Corpo de Bombeiros do estado de implantação",
        "ABNT NBR 9077 — Saídas de emergência em edifícios",
        "ABNT NBR 10898 — Sistema de iluminação de emergência",
        "ABNT NBR 12693 — Sistemas de proteção por extintores de incêndio",
        "ABNT NBR 13714 — Sistemas de hidrantes e de mangotinhos para combate a incêndio",
    ],
    "calculations": [],
}
