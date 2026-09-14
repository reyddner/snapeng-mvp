"""
Exceções customizadas
Arquivo: backend/app/utils/exceptions.py
"""


class SnapengException(Exception):
    """Exceção base do SNAPENG"""
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


class TemplateNotFoundError(SnapengException):
    """Template não encontrado"""
    pass  # noqa: WPS420


class ProjectNotFoundError(SnapengException):
    """Projeto não encontrado"""
    pass  # noqa: WPS420


class DocumentGenerationError(SnapengException):
    """Erro ao gerar documento"""
    pass  # noqa: WPS420


class AIAssistantError(SnapengException):
    """Erro no assistente de IA"""
    pass  # noqa: WPS420

