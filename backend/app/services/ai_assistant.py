"""
Integração com Claude API para assistência inteligente
Arquivo: backend/app/services/ai_assistant.py
"""

from typing import Dict, Any, List
from app.config import settings

# Tentar importar anthropic, mas não falhar se não estiver disponível
try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None


class AIAssistant:
    """
    Assistente IA para:
    - Sugestões de conteúdo
    - Geração automática de seções
    - Validação de conformidade com normas
    """

    def __init__(self):
        self.client = None
        self.model = "claude-sonnet-4-20250514"

        if ANTHROPIC_AVAILABLE and settings.ANTHROPIC_API_KEY:
            try:
                self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except (ValueError, TypeError, AttributeError):
                self.client = None

    async def suggest_content(
        self,
        section_title: str,
        context: Dict[str, Any],
        template_type: str,
    ) -> str:
        """
        Sugere conteúdo para uma seção específica

        Args:
            section_title: Título da seção (ex: "1. OBJETO")
            context: Contexto do projeto (tipo de obra, local, etc)
            template_type: Tipo de template (pavimentacao, edificacao, etc)

        Returns:
            Sugestão de conteúdo
        """
        if not self.client:
            raise ValueError("Claude API não configurada. Configure ANTHROPIC_API_KEY no .env")

        prompt = f"""Você é um engenheiro civil especializado em elaboração de memoriais descritivos técnicos.
CONTEXTO DO PROJETO:
- Tipo de obra: {context.get('tipo_obra', 'N/A')}
- Local: {context.get('local', 'N/A')}
- Template: {template_type}

TAREFA:
Escreva o conteúdo técnico para a seção "{section_title}" do memorial descritivo.

REQUISITOS:
- Linguagem técnica e formal
- Conforme normas ABNT
- Objetivo e preciso
- Entre 100-200 palavras

Escreva apenas o conteúdo da seção, sem introduções ou explicações adicionais."""

        message = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

    async def generate_full_memorial(
        self,
        template_structure: Dict[str, Any],
        project_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Gera memorial completo usando IA

        TODO: Implementar lógica de geração completa
        """
        raise NotImplementedError("Geração completa será implementada na Sprint 4")

    async def validate_norm_compliance(
        self, content: str, applicable_norms: List[str]
    ) -> Dict[str, Any]:
        """
        Verifica se o conteúdo está conforme as normas

        Args:
            content: Conteúdo a ser validado
            applicable_norms: Lista de normas aplicáveis

        Returns:
            Dict com análise de conformidade
        """
        if not self.client:
            raise ValueError("Claude API não configurada. Configure ANTHROPIC_API_KEY no .env")

        prompt = f"""Analise o seguinte trecho de memorial descritivo e verifique conformidade com as normas: {', '.join(applicable_norms)}

CONTEÚDO:
{content}

Retorne:
1. Status: conforme/não conforme
2. Pontos de atenção
3. Sugestões de melhoria"""

        message = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        return {
            "analysis": message.content[0].text,
            "status": "pending_review",  # Parser da resposta
        }

    async def auto_complete(
        self, partial_text: str, context: Dict[str, Any]
    ) -> List[str]:
        """
        Fornece sugestões de auto-complete enquanto usuário digita

        TODO: Implementar cache para performance
        TODO: Usar embeddings para sugestões contextuais
        """
        raise NotImplementedError("Auto-complete será implementado na Sprint 4")

