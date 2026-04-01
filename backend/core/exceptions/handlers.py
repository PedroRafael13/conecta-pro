"""
Exception handlers customizados para a aplicação.

Provê exceptions padronizadas e handlers globais para FastAPI.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.logging import logger

# =============================================================================
# EXCEPTIONS CUSTOMIZADAS
# =============================================================================


class NotFoundError(Exception):
    """Recurso não encontrado (404)."""

    def __init__(self, entity: str, identifier: str = None):
        """
        Args:
            entity: Nome da entidade (ex: "Funcionário", "Post", "Escala")
            identifier: ID ou identificador do recurso (opcional)
        """
        self.entity = entity
        self.identifier = identifier

        if identifier:
            message = f"{entity} não encontrado: {identifier}"
        else:
            message = f"{entity} não encontrado"

        super().__init__(message)
        self.message = message


class ConflictError(Exception):
    """Conflito de recursos (409)."""

    def __init__(self, message: str, field: str = None, value: Any = None):
        """
        Args:
            message: Mensagem de erro
            field: Campo que causou conflito (opcional)
            value: Valor conflitante (opcional)
        """
        self.field = field
        self.value = value
        super().__init__(message)
        self.message = message


class ValidationError(Exception):
    """Erro de validação de dados (422)."""

    def __init__(self, message: str, errors: dict[str, Any] = None):
        """
        Args:
            message: Mensagem de erro geral
            errors: Dicionário de erros por campo (opcional)
        """
        self.errors = errors or {}
        super().__init__(message)
        self.message = message


class BusinessRuleError(Exception):
    """Violação de regra de negócio (422)."""

    def __init__(self, message: str, rule: str = None):
        """
        Args:
            message: Mensagem de erro
            rule: Nome da regra violada (opcional)
        """
        self.rule = rule
        super().__init__(message)
        self.message = message


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================


async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handler para NotFoundException."""
    logger.warning(
        "Recurso não encontrado",
        action="not_found_exception",
        path=request.url.path,
        method=request.method,
        entity=exc.entity,
        identifier=exc.identifier,
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": exc.message,
            "entity": exc.entity,
            "identifier": exc.identifier,
        },
    )


async def conflict_exception_handler(request: Request, exc: ConflictError):
    """Handler para ConflictException."""
    logger.warning(
        "Conflito de recurso",
        action="conflict_exception",
        path=request.url.path,
        method=request.method,
        field=exc.field,
        value=exc.value,
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": exc.message,
            "field": exc.field,
            "value": str(exc.value) if exc.value else None,
        },
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handler para ValidationException."""
    logger.warning(
        "Erro de validação",
        action="validation_exception",
        path=request.url.path,
        method=request.method,
        errors=exc.errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.message,
            "errors": exc.errors,
        },
    )


async def business_rule_exception_handler(request: Request, exc: BusinessRuleError):
    """Handler para BusinessRuleException."""
    logger.warning(
        "Violação de regra de negócio",
        action="business_rule_exception",
        path=request.url.path,
        method=request.method,
        rule=exc.rule,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.message,
            "rule": exc.rule,
        },
    )


# =============================================================================
# SETUP
# =============================================================================


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos os exception handlers na aplicação FastAPI.

    Args:
        app: Instância do FastAPI

    Usage:
        >>> from fastapi import FastAPI
        >>> from core.exceptions import setup_exception_handlers
        >>> app = FastAPI()
        >>> setup_exception_handlers(app)
    """
    app.add_exception_handler(NotFoundError, not_found_exception_handler)
    app.add_exception_handler(ConflictError, conflict_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(BusinessRuleError, business_rule_exception_handler)

    logger.info("Exception handlers registrados com sucesso", action="setup_exception_handlers")
