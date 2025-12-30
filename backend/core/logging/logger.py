"""
Sistema de logging estruturado com sanitização de dados sensíveis.
"""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Any, Dict

from loguru import logger

from core.config import settings

if TYPE_CHECKING:
    from loguru import Record

# Padrões de dados sensíveis para sanitização
SENSITIVE_PATTERNS = [
    (r'"password"\s*:\s*"[^"]*"', '"password": "[REDACTED]"'),
    (r'"senha"\s*:\s*"[^"]*"', '"senha": "[REDACTED]"'),
    (r'"token"\s*:\s*"[^"]*"', '"token": "[REDACTED]"'),
    (r'"access_token"\s*:\s*"[^"]*"', '"access_token": "[REDACTED]"'),
    (r'"refresh_token"\s*:\s*"[^"]*"', '"refresh_token": "[REDACTED]"'),
    (r'"api_key"\s*:\s*"[^"]*"', '"api_key": "[REDACTED]"'),
    (r'"secret"\s*:\s*"[^"]*"', '"secret": "[REDACTED]"'),
    (r'"cpf"\s*:\s*"\d{11}"', '"cpf": "[REDACTED]"'),
    (r'"cnpj"\s*:\s*"\d{14}"', '"cnpj": "[REDACTED]"'),
    (r"password=[^&\s]+", "password=[REDACTED]"),
    (r"Bearer [A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+", "Bearer [REDACTED]"),
    (r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[CPF_REDACTED]"),  # CPF formatado
    (r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", "[CNPJ_REDACTED]"),  # CNPJ formatado
]


def sanitize_message(message: str) -> str:
    """
    Remove dados sensíveis de uma mensagem de log.

    Args:
        message: Mensagem a sanitizar

    Returns:
        Mensagem com dados sensíveis removidos
    """
    sanitized = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def sanitize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitiza um record de log completo.

    Args:
        record: Record do loguru

    Returns:
        Record sanitizado
    """
    if "message" in record:
        record["message"] = sanitize_message(str(record["message"]))

    # Sanitizar extra data
    if "extra" in record:
        for key, value in record["extra"].items():
            if isinstance(value, str):
                record["extra"][key] = sanitize_message(value)

    return record


def sanitizing_filter(record: Record) -> bool:
    """Filtro que sanitiza mensagens de log."""
    # Sanitiza o record in-place
    if "message" in record:
        record["message"] = sanitize_message(str(record["message"]))
    return True


def configure_logging() -> None:
    """
    Configura o sistema de logging.

    Deve ser chamado no startup da aplicação.
    """
    # Remove handlers padrão
    logger.remove()

    # Formato baseado na configuração
    if settings.log_format == "json":
        log_format = (
            "{{"
            '"time": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"message": "{message}", '
            '"module": "{module}", '
            '"function": "{function}", '
            '"line": {line}'
            "}}"
        )
    else:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Adiciona handler para stdout com sanitização
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        filter=sanitizing_filter,
        colorize=settings.log_format != "json",
    )

    # Adiciona handler para arquivo em produção
    if settings.environment == "production":
        logger.add(
            "/opt/erp-conecta-mais/logs/app.log",
            format=log_format,
            level="INFO",
            filter=sanitizing_filter,
            rotation="10 MB",
            retention="30 days",
            compression="gz",
        )

        # Arquivo separado para erros
        logger.add(
            "/opt/erp-conecta-mais/logs/error.log",
            format=log_format,
            level="ERROR",
            filter=sanitizing_filter,
            rotation="10 MB",
            retention="90 days",
            compression="gz",
        )


def get_logger(name: str) -> Any:
    """
    Retorna logger configurado para um módulo.

    Args:
        name: Nome do módulo

    Returns:
        Logger configurado
    """
    return logger.bind(module=name)


# Exporta logger principal
__all__ = ["logger", "get_logger", "configure_logging", "sanitize_message"]
