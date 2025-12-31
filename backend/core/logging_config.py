"""
Configuração de logging para inicialização da aplicação.
"""

from core.structured_logging import setup_structured_logging


def configure_application_logging():
    """
    Configura logging estruturado na inicialização da aplicação.
    """
    setup_structured_logging()

    # Log de inicialização
    import logging
    logger = logging.getLogger("guardian.startup")
    logger.info("Guardian Unified v3.0.0 structured logging initialized")