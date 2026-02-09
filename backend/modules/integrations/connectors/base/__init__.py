"""
Base Connector Framework
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
    "ConnectorConnectionError",
]
