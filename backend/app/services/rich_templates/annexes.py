"""Anexos tecnicos comuns — aumentam densidade sem novos placeholders."""

from __future__ import annotations

from typing import Any, Dict, List

from .bodies_a import sec, sub


def professional_annexes(discipline_label: str) -> List[Dict[str, Any]]:
    return [
        sec(
            "A. METODOLOGIA DE PROJETO E CONTROLE DE QUALIDADE",
            f"""A elaboração deste memorial de {discipline_label} seguiu fluxo de levantamento de dados, definição de premissas, dimensionamento/parametrização técnica, compatibilização preliminar com disciplinas correlatas e revisão interna de coerência normativa.

O controle de qualidade documental contempla verificação de consistência entre memorial, plantas e memoriais de cálculo (quando houver), checagem de unidades, conferência de hipóteses de carga/uso e rastreabilidade das normas citadas.

Recomenda-se matriz de pendências aberta até a emissão da versão “para execução”, com responsáveis e prazos. Alterações de escopo devem gerar nova revisão tipada (R0, R1, R2…), com histórico resumido no carimbo das peças.""",
            [
                sub(
                    "A.1 Entregáveis mínimos recomendados",
                    """Além deste memorial, recomenda-se manter atualizados: plantas e detalhes da disciplina; memorial de cálculo ou planilhas de dimensionamento; lista de materiais críticos; e registro de compatibilização com arquitetura/estrutura/instalações.""",
                ),
                sub(
                    "A.2 Critérios de aceite em obra",
                    """Não se recomenda liberar etapas ocultas (concretagem, fechamento de shafts, aterro, revestimento) sem inspeção registrada. Desvios em relação ao projeto devem ser formalizados em RFI/RFO e respondidos pelo responsável técnico antes da continuidade.""",
                ),
            ],
        ),
        sec(
            "B. SEGURANÇA DO TRABALHO, MEIO AMBIENTE E SAÚDE OCUPACIONAL",
            """A execução das intervenções previstas neste memorial deverá observar as Normas Regulamentadoras aplicáveis (NR-18, NR-10, NR-35, NR-6, entre outras conforme a atividade), o PCMAT/PCMSO da obra e as exigências do responsável pela segurança do canteiro.

Áreas de risco elétrico, escavação, trabalho em altura, soldagem, movimentação de cargas e espaços confinados (quando houver) exigem procedimentos específicos, EPIs/EPCs e autorização de trabalho. Resíduos de construção serão segregados e destinados conforme legislação ambiental local.

O projetista não substitui a gestão de SST da obra; contudo, as soluções técnicas aqui descritas pressupõem condições seguras de montagem, inspeção e manutenção futura (acessos, distâncias, ventilação e sinalização).""",
        ),
        sec(
            "C. MANUTENÇÃO, OPERAÇÃO E VIDA ÚTIL",
            """Após a entrega, a preservação do desempenho depende de plano de manutenção preventiva: inspeções periódicas, limpeza de dispositivos, reaperto/reaperto torque quando aplicável, verificação de estanqueidade, testes de proteções e atualização de as-built.

Recomenda-se manual do proprietário/operador contendo: periodicidade sugerida de inspeção; pontos de acesso; sinais de anomalia; e contatos do responsável técnico. Intervenções que alterem cargas, trajetos, pressões, seções ou proteções devem ser precedidas de análise técnica.

A vida útil de projeto pressupõe uso compatível com o programa informado, manutenção regular e ausência de sobrecargas não previstas. Ambientes agressivos (litorâneos, industriais, com vapores químicos) podem exigir inspeções mais frequentes e proteção adicional.""",
            [
                sub(
                    "C.1 As-built e documentação final",
                    """Ao término da execução, devem ser consolidados desenhos as-built, relatórios de comissionamento, certificados de materiais críticos e ART/RRT de execução, arquivados junto ao memorial aprovado.""",
                )
            ],
        ),
        sec(
            "D. LIMITAÇÕES, EXCLUSÕES E RESPONSABILIDADES",
            """Este memorial reflete as informações disponíveis na data de emissão. Não cobre, salvo menção explícita: projetos de outras disciplinas; orçamento detalhado; cronograma físico-financeiro; laudos laboratoriais; ou licenciamento ambiental completo.

O contratante é responsável pela veracidade dos dados de uso, ocupação, cargas especiais e restrições do terreno. O executor é responsável pela conformidade com o projeto, boas práticas e normas de segurança. O responsável técnico autor responde pelos critérios de projeto aqui descritos, nos limites da legislação profissional.

Em caso de conflito entre memorial e desenho, prevalece a interpretação mais conservadora sob o ponto de vista de segurança, até esclarecimento formal do autor do projeto.""",
        ),
        sec(
            "E. LISTA DE VERIFICAÇÃO PRÉ-EMISSÃO",
            """Antes da emissão definitiva, recomenda-se conferir:

- Premissas de uso/ocupação ainda válidas;
- Compatibilidade com arquitetura e estrutura (vãos, shafts, cargas);
- Normas citadas vigentes e aplicáveis à tipología;
- Dimensionamentos revisados após última alteração de layout;
- Identificação clara de revisões e responsável técnico;
- Anexos (plantas/cálculos) coerentes com o texto deste memorial;
- Requisitos de concessionárias e órgãos locais considerados;
- Plano mínimo de ensaios/comissionamento definido.

Itens não verificados devem constar como pendência explícita, nunca como premissa oculta.""",
        ),
    ]


def with_annexes(body: Dict[str, Any], label: str) -> Dict[str, Any]:
    sections = list(body.get("sections") or []) + professional_annexes(label)
    return {
        "sections": sections,
        "normas": list(body.get("normas") or []),
        "calculations": list(body.get("calculations") or []),
    }
