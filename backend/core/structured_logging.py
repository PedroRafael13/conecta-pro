"""
Sistema de Logging Estruturado - Conecta PRO v3.0.0
====================================================

Configuração de logs em formato JSON para facilitar busca e análise.
"""

import logging
import sys
from datetime import datetime
from typing import Any

from pythonjsonlogger import jsonlogger


class ConectaJSONFormatter(jsonlogger.JsonFormatter):
    """
    Formatter personalizado para logs do Conecta PRO.

    Produz logs estruturados em JSON com campos padronizados.
    """

    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]):
        """Adiciona campos customizados ao log record."""
        super().add_fields(log_record, record, message_dict)

        # Timestamp padronizado
        log_record["timestamp"] = datetime.utcnow().isoformat()

        # Informações do serviço
        log_record["service"] = "Conecta-PRO"
        log_record["version"] = "3.0.0"

        # Module/Controller info
        log_record["module"] = getattr(
            record, "module", record.name.split(".")[-1] if "." in record.name else record.name
        )

        # Campos específicos se disponíveis
        for field in [
            "user_id",
            "action",
            "resource_id",
            "request_id",
            "response_time_ms",
            "endpoint",
            "method",
            "status_code",
        ]:
            if hasattr(record, field):
                log_record[field] = getattr(record, field)


def setup_structured_logging():
    """
    Configura logging estruturado para toda a aplicação.
    """
    # Formatter JSON
    json_formatter = ConectaJSONFormatter(fmt="%(timestamp)s %(level)s %(service)s %(version)s %(module)s %(message)s")

    # Handler para stdout (para produção)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(json_formatter)
    stdout_handler.setLevel(logging.INFO)

    # Handler para stderr (apenas errors)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(json_formatter)
    stderr_handler.setLevel(logging.ERROR)

    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remover handlers existentes para evitar duplicação
    root_logger.handlers.clear()

    # Adicionar novos handlers
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)

    # Configurar loggers específicos
    loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "sqlalchemy",
        "modules.field_service",
        "modules.ai",
        "modules.ai.bartolo",
        "api",
        "core",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = True


class ConectaLogger:
    """
    Logger específico para operações do Conecta PRO com campos estruturados.
    """

    def __init__(self, module_name: str):
        self.logger = logging.getLogger(f"modules.field_service.{module_name}")
        self.module = module_name

    def info(self, message: str, **kwargs):
        """Log de informação com campos extras."""
        extra = self._build_extra(kwargs)
        self.logger.info(message, extra=extra)

    def error(self, message: str, **kwargs):
        """Log de erro com campos extras."""
        extra = self._build_extra(kwargs)
        self.logger.error(message, extra=extra)

    def warning(self, message: str, **kwargs):
        """Log de warning com campos extras."""
        extra = self._build_extra(kwargs)
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log de debug com campos extras."""
        extra = self._build_extra(kwargs)
        self.logger.debug(message, extra=extra)

    def _build_extra(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Constrói campos extras padronizados."""
        extra = {"module": self.module}

        # Campos conhecidos
        known_fields = [
            "user_id",
            "action",
            "resource_id",
            "request_id",
            "response_time_ms",
            "endpoint",
            "method",
            "status_code",
            "technician_id",
            "ticket_id",
            "occurrence_id",
            "equipment_id",
        ]

        for field in known_fields:
            if field in kwargs:
                extra[field] = kwargs[field]

        return extra


def log_api_request(endpoint: str, method: str, status_code: int, response_time_ms: float, **kwargs):
    """
    Log estruturado para requisições de API.
    """
    logger = ConectaLogger("api")

    logger.info(
        f"{method} {endpoint} - {status_code}",
        action="api_request",
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time_ms=response_time_ms,
        **kwargs,
    )


def log_database_operation(operation: str, table: str, duration_ms: float, **kwargs):
    """
    Log estruturado para operações de database.
    """
    logger = ConectaLogger("database")

    logger.info(
        f"Database {operation} on {table}",
        action="database_operation",
        operation=operation,
        table=table,
        duration_ms=duration_ms,
        **kwargs,
    )


def log_security_event(event_type: str, severity: str, description: str, **kwargs):
    """
    Log estruturado para eventos de segurança.
    """
    logger = ConectaLogger("security")

    log_method = logger.error if severity in ["high", "critical"] else logger.warning

    log_method(
        f"Security event: {event_type}",
        action="security_event",
        event_type=event_type,
        severity=severity,
        description=description,
        **kwargs,
    )


def log_campo_operation(operation: str, technician_id: str = None, **kwargs):
    """
    Log estruturado para operações do CAMPO.
    """
    logger = ConectaLogger("campo")

    logger.info(
        f"CAMPO operation: {operation}",
        action="campo_operation",
        operation=operation,
        technician_id=technician_id,
        **kwargs,
    )


# Exemplo de uso no código:
"""
from core.logging import ConectaLogger, log_api_request, log_campo_operation

# Logger específico de módulo
logger = ConectaLogger("campo")
logger.info("Técnico criado com sucesso",
           action="create_technician",
           technician_id="123",
           user_id="admin")

# Log de API
log_api_request("/api/v1/campo/technicians", "POST", 201, 150.5,
               user_id="admin", technician_id="123")

# Log de operação CAMPO
log_campo_operation("create_technician", technician_id="123",
                   name="João Silva", specialty="Instalação")
"""
