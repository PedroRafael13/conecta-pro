"""
Exceções padronizadas para conectores de integração.
Sprint 33: Integration Framework
"""

from typing import Optional, Dict, Any


class ConnectorError(Exception):
    """Exceção base para erros de conectores."""

    def __init__(
        self,
        message: str,
        connector: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
        recoverable: bool = True
    ):
        super().__init__(message)
        self.message = message
        self.connector = connector
        self.error_code = error_code or "CONNECTOR_ERROR"
        self.details = details or {}
        self.retry_after = retry_after
        self.recoverable = recoverable

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "error": self.error_code,
            "message": self.message,
            "connector": self.connector,
            "details": self.details,
            "retry_after": self.retry_after,
            "recoverable": self.recoverable,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.error_code}: {self.message}>"


class AuthenticationError(ConnectorError):
    """Erro de autenticação com o sistema externo."""

    def __init__(
        self,
        message: str = "Falha na autenticação",
        connector: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            recoverable=False  # Geralmente precisa de intervenção manual
        )


class TokenExpiredError(AuthenticationError):
    """Token expirado."""

    def __init__(
        self,
        message: str = "Token de acesso expirado",
        connector: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            details=details
        )
        self.error_code = "TOKEN_EXPIRED"
        self.recoverable = True  # Pode tentar refresh


class RateLimitError(ConnectorError):
    """Limite de requisições excedido."""

    def __init__(
        self,
        message: str = "Limite de requisições excedido",
        connector: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            retry_after=retry_after or 60,
            recoverable=True
        )


class APIError(ConnectorError):
    """Erro retornado pela API externa."""

    def __init__(
        self,
        message: str,
        connector: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="API_ERROR",
            details={
                **(details or {}),
                "status_code": status_code,
                "response_body": response_body,
            },
            recoverable=self._is_recoverable(status_code)
        )
        self.status_code = status_code
        self.response_body = response_body

    @staticmethod
    def _is_recoverable(status_code: Optional[int]) -> bool:
        """Determina se o erro é recuperável baseado no status code."""
        if not status_code:
            return True
        # 5xx são geralmente recuperáveis (problemas do servidor)
        if 500 <= status_code < 600:
            return True
        # 429 é rate limit
        if status_code == 429:
            return True
        # 4xx geralmente não são recuperáveis (erro do cliente)
        if 400 <= status_code < 500:
            return False
        return True


class ValidationError(ConnectorError):
    """Erro de validação de dados."""

    def __init__(
        self,
        message: str,
        connector: Optional[str] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="VALIDATION_ERROR",
            details={
                **(details or {}),
                "field": field,
                "value": str(value) if value else None,
            },
            recoverable=False
        )
        self.field = field
        self.value = value


class ConnectionError(ConnectorError):
    """Erro de conexão com o sistema externo."""

    def __init__(
        self,
        message: str = "Erro de conexão",
        connector: Optional[str] = None,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="CONNECTION_ERROR",
            details={
                **(details or {}),
                "original_error": str(original_error) if original_error else None,
            },
            retry_after=30,
            recoverable=True
        )
        self.original_error = original_error


class TimeoutError(ConnectorError):
    """Timeout na requisição."""

    def __init__(
        self,
        message: str = "Timeout na requisição",
        connector: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="TIMEOUT",
            details={
                **(details or {}),
                "timeout_seconds": timeout_seconds,
            },
            retry_after=60,
            recoverable=True
        )
        self.timeout_seconds = timeout_seconds


class ConfigurationError(ConnectorError):
    """Erro de configuração do conector."""

    def __init__(
        self,
        message: str,
        connector: Optional[str] = None,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="CONFIGURATION_ERROR",
            details={
                **(details or {}),
                "config_key": config_key,
            },
            recoverable=False
        )
        self.config_key = config_key


class NotFoundError(ConnectorError):
    """Recurso não encontrado no sistema externo."""

    def __init__(
        self,
        message: str = "Recurso não encontrado",
        connector: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="NOT_FOUND",
            details={
                **(details or {}),
                "resource_type": resource_type,
                "resource_id": resource_id,
            },
            recoverable=False
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConflictError(ConnectorError):
    """Conflito de dados (ex: duplicata)."""

    def __init__(
        self,
        message: str = "Conflito de dados",
        connector: Optional[str] = None,
        resource_type: Optional[str] = None,
        conflicting_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            connector=connector,
            error_code="CONFLICT",
            details={
                **(details or {}),
                "resource_type": resource_type,
                "conflicting_id": conflicting_id,
            },
            recoverable=False
        )
        self.resource_type = resource_type
        self.conflicting_id = conflicting_id
