"""
Base Connector Framework
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
    "BaseConnector",
    "AuthStrategy",
    "APIKeyAuth",
    "OAuth2ClientCredentials",
    "BasicAuth",
    "IntegrationHTTPClient",
    "RateLimiter",
    "ConnectorError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
    "ValidationError",
    "ConnectionError",
]
