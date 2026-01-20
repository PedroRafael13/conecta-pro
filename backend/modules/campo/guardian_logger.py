"""
Logger Estruturado Guardian - Integração com Loguru
==================================================

Extensão do sistema Loguru existente com logs JSON estruturados.
"""

import json
import time
from datetime import datetime
from typing import Optional
from functools import wraps

from loguru import logger
from core.logging.logger import sanitize_message


class GuardianStructuredLogger:
    """
    Logger estruturado específico para Guardian Unified v3.0.0.

    Integra com Loguru existente e adiciona campos estruturados JSON.
    """

    def __init__(self, module_name: str):
        self.module = module_name

    def _build_structured_message(self, message: str, **fields) -> str:
        """
        Constrói mensagem estruturada em formato JSON.
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": "Guardian-Unified",
            "version": "3.0.0",
            "module": self.module,
            "message": message,
            **fields
        }

        # Sanitizar dados sensíveis
        json_str = json.dumps(log_data, ensure_ascii=False)
        return sanitize_message(json_str)

    def info(self, message: str, **fields):
        """Log estruturado de informação."""
        structured_msg = self._build_structured_message(message, level="INFO", **fields)
        logger.info(structured_msg)

    def error(self, message: str, **fields):
        """Log estruturado de erro."""
        structured_msg = self._build_structured_message(message, level="ERROR", **fields)
        logger.error(structured_msg)

    def warning(self, message: str, **fields):
        """Log estruturado de warning."""
        structured_msg = self._build_structured_message(message, level="WARNING", **fields)
        logger.warning(structured_msg)

    def debug(self, message: str, **fields):
        """Log estruturado de debug."""
        structured_msg = self._build_structured_message(message, level="DEBUG", **fields)
        logger.debug(structured_msg)

    def security(self, event_type: str, severity: str, description: str, **fields):
        """Log estruturado para eventos de segurança."""
        log_fields = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            "description": description,
            **fields
        }

        if severity in ['critical', 'high']:
            self.error(f"SECURITY: {event_type} - {description}", **log_fields)
        else:
            self.warning(f"SECURITY: {event_type} - {description}", **log_fields)


# Instâncias pré-configuradas para módulos principais
campo_logger = GuardianStructuredLogger("campo")
security_logger = GuardianStructuredLogger("security")
api_logger = GuardianStructuredLogger("api")
database_logger = GuardianStructuredLogger("database")
monitoring_logger = GuardianStructuredLogger("monitoring")


def log_api_operation(endpoint: str, method: str, status_code: int, response_time_ms: float, **fields):
    """
    Log para operações de API com estrutura padronizada.
    """
    api_logger.info(
        f"{method} {endpoint} -> {status_code}",
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time_ms=response_time_ms,
        event_type="api_request",
        **fields
    )


def log_campo_operation(
    operation: str, technician_id: Optional[str] = None, success: bool = True, **fields
):
    """
    Log para operações CAMPO.
    """
    op_status = "success" if success else "failure"

    campo_logger.info(
        f"CAMPO {operation} - {op_status}",
        operation=operation,
        technician_id=technician_id,
        success=success,
        event_type="campo_operation",
        **fields
    )


def log_database_operation(
    operation: str, table: str, duration_ms: float, success: bool = True, **fields
):
    """
    Log para operações de database.
    """
    db_status = "success" if success else "failure"

    database_logger.info(
        f"DB {operation} on {table} - {db_status} ({duration_ms}ms)",
        operation=operation,
        table=table,
        duration_ms=duration_ms,
        status=db_status,
        success=success,
        event_type="database_operation",
        **fields
    )


def log_monitoring_event(event_type: str, status: str, details: str, **fields):
    """
    Log para eventos de monitoramento.
    """
    monitoring_logger.info(
        f"MONITORING: {event_type} - {status}",
        event_type=f"monitoring_{event_type}",
        status=status,
        details=details,
        **fields
    )


def api_logger_middleware():
    """
    Decorator para logging automático de APIs.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = getattr(func, '__name__', 'unknown')
            method = 'UNKNOWN'

            try:
                # Executar função
                result = await func(*args, **kwargs)

                # Calcular tempo de resposta
                response_time = (time.time() - start_time) * 1000

                # Log de sucesso
                log_api_operation(
                    endpoint=endpoint,
                    method=method,
                    status_code=200,
                    response_time_ms=response_time
                )

                return result

            except Exception as e:
                # Calcular tempo de resposta mesmo em erro
                response_time = (time.time() - start_time) * 1000

                # Log de erro
                log_api_operation(
                    endpoint=endpoint,
                    method=method,
                    status_code=500,
                    response_time_ms=response_time,
                    error=str(e),
                    error_type=type(e).__name__
                )

                raise

        return wrapper
    return decorator


# Funções de conveniência para Guardian modules
def get_guardian_logger(module_name: str) -> GuardianStructuredLogger:
    """
    Obtém logger estruturado para um módulo Guardian.
    """
    return GuardianStructuredLogger(module_name)
