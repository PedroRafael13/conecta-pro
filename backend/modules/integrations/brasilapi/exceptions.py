class BrasilAPIError(Exception):
    """Base exception."""


class BrasilAPINotFoundError(BrasilAPIError):
    """CNPJ or CEP not found (404)."""


class BrasilAPIUnavailableError(BrasilAPIError):
    """Service unavailable — 5xx or circuit breaker open."""


class BrasilAPIInvalidFormatError(BrasilAPIError):
    """CNPJ/CEP malformed — 422 equivalent."""
