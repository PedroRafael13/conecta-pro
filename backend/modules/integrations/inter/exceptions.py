"""D6 — Exceções específicas do módulo Inter."""


class InterError(Exception):
    """Erro genérico Inter."""


class InterAuthError(InterError):
    """Falha de autenticação OAuth2/mTLS."""


class InterRateLimitError(InterError):
    """Rate limit atingido na API Inter."""


class InterNotFoundError(InterError):
    """Recurso não encontrado na API Inter."""


class InterTimeoutError(InterError):
    """Timeout na comunicação com Inter."""
