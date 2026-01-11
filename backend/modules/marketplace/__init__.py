"""
Marketplace de Integracoes - Conecta PRO.

Este modulo fornece infraestrutura completa para integracao
com servicos externos atraves de conectores pre-configurados.

Componentes:
- Connector Registry: Catalogo de conectores disponiveis
- API Gateway: Rate limiting, circuit breaker, retry
- Auth Manager: OAuth2 e API Key management
- Transform Engine: Mapeamento e transformacao de dados
- Webhook Manager: Gerenciamento de webhooks
- SDK: Ferramentas para criar conectores customizados
- Monitoring: Metricas e logs de integracoes
"""

from modules.marketplace.controllers import router as marketplace_router
from modules.marketplace.connectors.registry import (
    ConnectorRegistry,
    ConnectorDefinition,
    ConnectorCategory,
    ConnectorStatus,
    ConnectorCapability,
)
from modules.marketplace.auth.auth_manager import (
    AuthManager,
    AuthMethod,
    OAuthCredentials,
    ApiKeyCredentials,
)
from modules.marketplace.gateway.api_gateway import (
    ApiGateway,
    GatewayConfig,
    RateLimitConfig,
)
from modules.marketplace.webhooks.webhook_manager import WebhookManager
from modules.marketplace.transforms.transform_engine import TransformEngine
from modules.marketplace.monitoring.integration_monitor import IntegrationMonitor
from modules.marketplace.sdk.marketplace_sdk import MarketplaceSDK

__all__ = [
    # Router
    "marketplace_router",
    # Connector Registry
    "ConnectorRegistry",
    "ConnectorDefinition",
    "ConnectorCategory",
    "ConnectorStatus",
    "ConnectorCapability",
    # Auth Manager
    "AuthManager",
    "AuthMethod",
    "OAuthCredentials",
    "ApiKeyCredentials",
    # API Gateway
    "ApiGateway",
    "GatewayConfig",
    "RateLimitConfig",
    # Webhooks
    "WebhookManager",
    # Transforms
    "TransformEngine",
    # Monitoring
    "IntegrationMonitor",
    # SDK
    "MarketplaceSDK",
]
