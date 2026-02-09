"""
Conectores de Integração
Sprint 33: Integration Framework
"""

from modules.integrations.connectors.base.auth import (
    APIKeyAuth,
    AuthStrategy,
    BasicAuth,
    OAuth2ClientCredentials,
)
from modules.integrations.connectors.base.connector import BaseConnector
from modules.integrations.connectors.base.exceptions import (
    APIError,
    AuthenticationError,
    ConnectorConnectionError,
    ConnectorError,
    RateLimitError,
    ValidationError,
)
from modules.integrations.connectors.base.http_client import IntegrationHTTPClient
from modules.integrations.connectors.base.rate_limiter import RateLimiter

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
    "ConnectorConnectionError",
]
