"""
Conectores de Integração
Sprint 33: Integration Framework
"""

from modules.integrations.connectors.base.connector import BaseConnector
from modules.integrations.connectors.base.auth import (
    AuthStrategy,
    APIKeyAuth,
    OAuth2ClientCredentials,
    BasicAuth,
)
from modules.integrations.connectors.base.http_client import IntegrationHTTPClient
from modules.integrations.connectors.base.rate_limiter import RateLimiter
from modules.integrations.connectors.base.exceptions import (
    ConnectorError,
    AuthenticationError,
    RateLimitError,
    APIError,
    ValidationError,
    ConnectionError,
)

__all__ = [
    # Base
    "BaseConnector",
    # Auth
    "AuthStrategy",
    "APIKeyAuth",
    "OAuth2ClientCredentials",
    "BasicAuth",
    # HTTP
    "IntegrationHTTPClient",
    # Rate Limiter
    "RateLimiter",
    # Exceptions
    "ConnectorError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
    "ValidationError",
    "ConnectionError",
]
