"""Secoes densas — estruturas, fundacoes, pavimentacao, subestacao."""

from __future__ import annotations

from .bodies_a import sec, sub

CONCRETO = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este Memorial Descritivo Estrutural apresenta os critérios de projeto e execução da estrutura de concreto armado do tipo {{tipo_estrutura}}, localizada em {{localizacao}}, com {{numero_pavimentos}} pavimento(s).""",
        ),
        sec(
            "2. SISTEMA ESTRUTURAL E AÇÕES",
            """O sistema estrutural adotado é: {{sistema_estrutural}}.

Cargas e ações consideradas:

{{cargas_adotadas}}

O dimensionamento observa a NBR 6118 quanto a estados limites últimos e de serviço, incluindo flechas, fissuração e estabilidade global.""",
            [
                sub(
                    "2.1 Modelo estrutural",
                    """O modelo analítico/computacional considera rigideces compatíveis com a sequência construtiva e as condições de apoio nas fundações. Lajes, vigas e pilares serão detalhados com taxa de armadura e espaçamentos conforme norma.""",
                )
            ],
        ),
        sec(
            "3. MATERIAIS",
            """Concreto com resistência característica fck = {{fck}} MPa. Armaduras em aço {{tipo_aco}}, com cobrimento nominal de {{cobrimento}} cm, definido conforme classe de agressividade ambiental e tipo de elemento.

Agregados, cimento e aditivos deverão atender às normas brasileiras, com controle tecnológico em laboratório idôneo.""",
        ),
        sec(
            "4. EXECUÇÃO, FÔRMAS E CURA",
            """A execução seguirá a NBR 14931. Fôrmas e escoramentos serão dimensionados para as cargas de concretagem. A cura será mantida pelo período mínimo normativo, evitando retração precoce e perda de resistência superficial.""",
        ),
        sec(
            "5. CONTROLE TECNOLÓGICO",
            """Controle tecnológico e de execução:

{{controle_execucao}}

Devem ser moldados corpos de prova por betonada/caminhão conforme plano de amostragem, com ruptura e registro. Não conformidades implicarão plano de ação (esclerometria, ultrassom, reforço) sob responsabilidade técnica.""",
        ),
        sec(
            "6. JUNTAS, IMPERMEABILIZAÇÃO E INTERFACES",
            """Juntas de dilatação/construção serão detalhadas para permitir movimentação sem dano aos acabamentos. Interfaces com impermeabilização, shafts e instalações não poderão reduzir cobrimentos nem seccionar armaduras sem autorização do projetista.""",
        ),
        sec(
            "7. DISPOSIÇÕES FINAIS",
            """Alterações de vãos, cargas especiais (cofre, piscina, equipamentos) ou remoção de elementos estruturais exigem novo cálculo e atualização deste memorial.""",
        ),
    ],
    "normas": [
        "ABNT NBR 6118 — Projeto de estruturas de concreto",
        "ABNT NBR 6120 — Ações para o cálculo de estruturas de edificações",
        "ABNT NBR 6123 — Forças devidas ao vento em edificações",
        "ABNT NBR 12655 — Concreto de cimento Portland — Preparo, controle e recebimento",
        "ABNT NBR 14931 — Execução de estruturas de concreto",
    ],
    "calculations": [],
}

METALICA = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este memorial descreve a estrutura metálica do tipo {{tipo_estrutura}}, com vão máximo de {{vao_maximo}} m e área de cobertura de {{area_cobertura}} m², em {{localizacao}}.""",
        ),
        sec(
            "2. MATERIAIS E LIGAÇÕES",
            """Aço estrutural: {{aco_estrutural}}.

Ligações: {{ligacoes}}.

Proteção contra corrosão: {{proteccao_corrosao}}.

Parafusos, soldas e chumbadores atenderão às normas de fabricação e montagem, com qualificação de procedimentos de soldagem quando aplicável.""",
        ),
        sec(
            "3. AÇÕES E DESEMPENHO",
            """Cargas consideradas:

{{cargas_adotadas}}

O dimensionamento observa NBR 8800 (ou NBR 14762 para perfis formados a frio, quando aplicável), com verificação de estabilidade, flechas e vibrações.""",
        ),
        sec(
            "4. CONTRAVENTAMENTO E ESTABILIDADE",
            """Sistema de contraventamento:

{{contraventamento}}

Durante a montagem, deverão ser previstos estabilizadores temporários até a conclusão dos diafragmas e ligações definitivas.""",
        ),
        sec(
            "5. FABRICAÇÃO, TRANSPORTE E MONTAGEM",
            """Peças serão fabricadas com controle dimensional, identificação e proteção de superfícies. O transporte evitará deformações permanentes. A montagem seguirá sequência que garanta estabilidade e segurança dos montadores (NR-18/NR-35 no que couber).""",
        ),
        sec(
            "6. CONTROLE DE QUALIDADE",
            """Soldas críticas poderão exigir ENS (líquido penetrante, ultrassom) conforme especificação. Torque de parafusos de alta resistência será controlado. Recebimento em obra incluirá conferência de chumbadores e nivelamento de bases.""",
        ),
        sec(
            "7. DISPOSIÇÕES FINAIS",
            """Perfurações adicionais, cortes ou soldas de campo não previstos no projeto são vedados sem autorização do responsável técnico.""",
        ),
    ],
    "normas": [
        "ABNT NBR 8800 — Projeto de estruturas de aço e de estruturas mistas de aço e concreto de edifícios",
        "ABNT NBR 14762 — Dimensionamento de estruturas de aço constituídas por perfis formados a frio",
        "ABNT NBR 6123 — Forças devidas ao vento em edificações",
        "Especificações AWS/AWS D1.1 para soldagem (quando aplicável)",
    ],
    "calculations": [],
}

FUNDACOES = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este Memorial Descritivo de Fundações apresenta o tipo {{tipo_fundacao}} adotado para a edificação em {{localizacao}}, com base nas informações geotécnicas disponíveis.""",
        ),
        sec(
            "2. INVESTIGAÇÃO GEOTÉCNICA",
            """Sondagem disponível: {{sondagem_disponivel}}.

Tipo de solo considerado: {{tipo_solo}}.

Tensão admissível adotada: {{tensao_admissivel}} kPa. Nível d'água: {{nivel_agua}} m.

Na ausência de investigação completa, recomenda-se campanha mínima de sondagens SPT antes da execução, podendo haver ajuste do tipo de fundação.""",
        ),
        sec(
            "3. CARGAS E DIMENSIONAMENTO",
            """Cargas transmitidas às fundações:

{{cargas_fundacao}}

O dimensionamento considera combinações de ações da estrutura, peso próprio dos blocos/sapatas e efeitos de momento. Recalques diferenciais serão limitados para não comprometer a superestrutura.""",
        ),
        sec(
            "4. CRITÉRIOS DE EXECUÇÃO",
            """Critérios de escavação e execução:

{{criterios_execucao}}

O fundo das escavações deverá ser limpo e inspecionado. Em presença de água, adotar esgotamento que não cause piping. Concretagem de elementos profundos seguirá procedimentos específicos (estacas/tubulões).""",
        ),
        sec(
            "5. CONTROLE E INSTRUMENTAÇÃO",
            """Para fundações profundas, recomenda-se controle de integridade e, quando pertinente, prova de carga. Desvios de locação e verticalidade fora da tolerância exigem avaliação estrutural.""",
        ),
        sec(
            "6. DISPOSIÇÕES FINAIS",
            """Qualquer divergência entre o perfil real do terreno e o previsto na sondagem deve ser comunicada imediatamente ao projetista antes de prosseguir.""",
        ),
    ],
    "normas": [
        "ABNT NBR 6122 — Projeto e execução de fundações",
        "ABNT NBR 8036 — Programação de sondagens de simples reconhecimento",
        "ABNT NBR 12131 — Estacas — Prova de carga estática (quando aplicável)",
    ],
    "calculations": [],
}

PAVIMENTACAO = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este memorial descreve o projeto de pavimentação asfáltica para {{tipo_obra}}, com extensão de {{extensao}} km, localizado em {{localizacao}}.""",
        ),
        sec(
            "2. PARÂMETROS DE DIMENSIONAMENTO",
            """CBR de campo: {{cbr_campo}} %. Espessura de base: {{espessura_base}} cm. Espessura de revestimento: {{espessura_revestimento}} cm.

Tipo de asfalto: {{tipo_asfalto}}. Penetração: {{penetracao_asfalto}}.

O dimensionamento considera tráfego previsto, suporte do subleito e clima regional.""",
        ),
        sec(
            "3. ESTRUTURA DO PAVIMENTO",
            """A estrutura típica compreende regularização do subleito, base granular e revestimento betuminoso. Camadas serão compactadas até o grau de compactação especificado, com controle de umidade e densidade.""",
        ),
        sec(
            "4. ETAPAS DE EXECUÇÃO",
            """{{etapas_execucao}}

A imprimação/pintura de ligação será executada sobre superfície limpa. O CBUQ será usinado, transportado e aplicado com controle de temperatura e compactação.""",
        ),
        sec(
            "5. CONTROLE TECNOLÓGICO",
            """Devem ser realizados ensaios de granulometria, CBR, densidade, teor de ligante e extração, conforme plano de qualidade da obra. Trechos não conformes serão refeitos.""",
        ),
        sec(
            "6. DRENAGEM E ACABAMENTO",
            """A drenagem superficial e profunda (quando prevista) é condição de desempenho do pavimento. Acabamento inclui sinalização e limpeza de dispositivos.""",
        ),
        sec(
            "7. DISPOSIÇÕES FINAIS",
            """Alterações de tráfego de projeto ou de CBR de subleito exigem redimensionamento das espessuras.""",
        ),
    ],
    "normas": [
        "ABNT NBR 15115 — Materiais reciclados de resíduos sólidos da construção civil — Execução de camadas de pavimentação",
        "ABNT NBR 15116 — Agregados reciclados de resíduos sólidos da construção civil",
        "Especificações DNIT/DER aplicáveis a CBUQ e bases granulares",
        "Normas de ensaio ABNT/DNIT para controle tecnológico de pavimentos",
    ],
    "calculations": [],
}

SUBESTACAO = {
    "sections": [
        sec(
            "1. OBJETO",
            """Este memorial descreve a subestação elétrica do tipo {{tipo_subestacao}}, com potência instalada {{potencia_instalada}} kVA, tensão primária {{tensao_primaria}} kV e tensão secundária {{tensao_secundaria}} kV, em {{localizacao}}.""",
        ),
        sec(
            "2. DEMANDA E TRANSFORMADOR",
            """Demanda máxima considerada: {{demanda_maxima}} kVA. Potência do transformador: {{potencia_transformador}} kVA.

O transformador será especificado com perdas, ligação e classe de isolamento compatíveis com a rede da concessionária e com a carga prevista, incluindo margem de expansão.""",
        ),
        sec(
            "3. EQUIPAMENTOS PRINCIPAIS",
            """{{equipamentos}}

A disposição física observará distâncias de segurança, ventilação, acesso para manutenção e restrição a pessoas não autorizadas.""",
        ),
        sec(
            "4. PROTEÇÕES E MEDIÇÃO",
            """Sistemas de proteção:

{{sistemas_protecao}}

A coordenação de proteções primária/secundária buscará seletividade com a rede da concessionária. Medição atenderá ao padrão exigido (primário/secundário).""",
        ),
        sec(
            "5. ATERRAMENTO E SEGURANÇA",
            """A malha de aterramento da subestação será dimensionada para correntes de falta, com equipotencialização de carcaças e portas. Sinalização de risco elétrico, EPIs e procedimentos NR-10 são obrigatórios na operação.""",
        ),
        sec(
            "6. COMISSIONAMENTO",
            """Antes da energização, realizar inspeções, ensaios de relação de transformação, resistência de isolação, operação de seccionadoras/disjuntores e verificação de intertravamentos. Registrar em relatório técnico.""",
        ),
        sec(
            "7. DISPOSIÇÕES FINAIS",
            """Qualquer alteração de potência contratada ou de arranjo de barras exige revisão do projeto da subestação e anuência da concessionária quando cabível.""",
        ),
    ],
    "normas": [
        "ABNT NBR 14039 — Instalações elétricas de média tensão de 1,0 kV a 36,2 kV",
        "ABNT NBR 5410 — Instalações elétricas de baixa tensão (lado BT)",
        "NR-10 — Segurança em instalações e serviços em eletricidade",
        "Padrões técnicos da concessionária local",
    ],
    "calculations": [],
}
