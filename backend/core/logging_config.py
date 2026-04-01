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

    logger = logging.getLogger("conecta.startup")
    logger.info("Conecta PRO structured logging initialized")
