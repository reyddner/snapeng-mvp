"""
Configuração de logs estruturados
Arquivo: backend/app/utils/logger.py
"""

import logging
import sys
from app.config import settings

# Configurar logger
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("snapeng")

