"""
Interface base para conectores de integração.
Sprint 33: Integration Framework
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, AsyncIterator, TypeVar, Generic
from uuid import UUID

from modules.integrations.connectors.base.auth import AuthStrategy
from modules.integrations.connectors.base.http_client import (
    IntegrationHTTPClient,
    HTTPClientConfig
)
from modules.integrations.connectors.base.rate_limiter import RateLimiter
from modules.integrations.connectors.base.exceptions import ConnectorError

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ConnectorCapabilities:
    """Capacidades do conector."""
    supports_incremental_sync: bool = True
    supports_full_sync: bool = True
    supports_webhooks: bool = False
    supports_write: bool = False
    supports_delete: bool = False
    supported_entities: List[str] = field(default_factory=list)
    rate_limit_per_second: Optional[float] = None
    rate_limit_per_minute: Optional[float] = None


@dataclass
class SyncResult(Generic[T]):
    """Resultado de uma operação de sync."""
    success: bool
    data: Optional[List[T]] = None
    cursor: Optional[str] = None
    has_more: bool = False
    total_count: Optional[int] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityResult:
    """Resultado de operação em uma entidade."""
    success: bool
    external_id: Optional[str] = None
    internal_id: Optional[UUID] = None
    action: str = "none"  # created, updated, deleted, skipped
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class HealthCheckResult:
    """Resultado do health check."""
    healthy: bool
    latency_ms: int
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BaseConnector(ABC):
    """
    Classe base abstrata para conectores de integração.
    Todos os conectores devem herdar desta classe.
    """

    # Nome do conector (deve ser sobrescrito)
    NAME: str = "base"
    VERSION: str = "1.0.0"

    def __init__(
        self,
        account_id: UUID,
        tenant_id: UUID,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa o conector.

        Args:
            account_id: ID da conta de integração
            tenant_id: ID do tenant
            credentials: Credenciais decriptografadas
            config: Configurações adicionais
        """
        self.account_id = account_id
        self.tenant_id = tenant_id
        self.credentials = credentials
        self.config = config or {}

        # Cliente HTTP (criado no setup)
        self._http_client: Optional[IntegrationHTTPClient] = None

        # Auth strategy (criado no setup)
        self._auth: Optional[AuthStrategy] = None

        # Estado
        self._initialized = False

    @property
    @abstractmethod
    def capabilities(self) -> ConnectorCapabilities:
        """Retorna as capacidades do conector."""
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        """Retorna a URL base da API."""
        pass

    @abstractmethod
    def _create_auth_strategy(self) -> AuthStrategy:
        """Cria a estratégia de autenticação."""
        pass

    def _create_rate_limiter(self) -> RateLimiter:
        """Cria o rate limiter. Pode ser sobrescrito."""
        caps = self.capabilities
        return RateLimiter(
            requests_per_second=caps.rate_limit_per_second,
            requests_per_minute=caps.rate_limit_per_minute,
            name=self.NAME
        )

    def _create_http_config(self) -> HTTPClientConfig:
        """Cria configuração HTTP. Pode ser sobrescrito."""
        return HTTPClientConfig(
            base_url=self._get_base_url(),
            timeout_connect=5.0,
            timeout_read=30.0,
            timeout_write=10.0,
            max_retries=3,
            headers={
                "User-Agent": f"ConectaPRO-Integration/{self.VERSION}",
                "Accept": "application/json",
            }
        )

    async def setup(self) -> None:
        """
        Inicializa o conector.
        Deve ser chamado antes de usar.
        """
        if self._initialized:
            return

        logger.info(f"[{self.NAME}] Inicializando conector...")

        try:
            # Criar auth strategy
            self._auth = self._create_auth_strategy()

            # Criar HTTP client
            http_config = self._create_http_config()
            rate_limiter = self._create_rate_limiter()

            self._http_client = IntegrationHTTPClient(
                config=http_config,
                auth=self._auth,
                rate_limiter=rate_limiter,
                connector_name=self.NAME
            )

            # Setup adicional (pode ser sobrescrito)
            await self._on_setup()

            self._initialized = True
            logger.info(f"[{self.NAME}] Conector inicializado com sucesso")

        except Exception as e:
            logger.error(f"[{self.NAME}] Falha ao inicializar: {e}")
            raise ConnectorError(
                f"Falha ao inicializar conector: {e}",
                connector=self.NAME
            )

    async def _on_setup(self) -> None:
        """Hook para setup adicional. Pode ser sobrescrito."""
        pass

    async def teardown(self) -> None:
        """Finaliza o conector."""
        if self._http_client:
            await self._http_client.close()
            self._http_client = None
        self._initialized = False
        logger.info(f"[{self.NAME}] Conector finalizado")

    async def __aenter__(self) -> "BaseConnector":
        """Context manager entry."""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.teardown()

    def _ensure_initialized(self) -> None:
        """Verifica se está inicializado."""
        if not self._initialized:
            raise ConnectorError(
                "Conector não inicializado. Chame setup() primeiro.",
                connector=self.NAME
            )

    @property
    def http(self) -> IntegrationHTTPClient:
        """Acesso ao cliente HTTP."""
        self._ensure_initialized()
        return self._http_client

    # ==================== Health Check ====================

    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """
        Verifica saúde da conexão.
        Deve testar autenticação e conectividade.
        """
        pass

    # ==================== Sync Operations ====================

    @abstractmethod
    async def fetch_entities(
        self,
        entity_type: str,
        cursor: Optional[str] = None,
        updated_since: Optional[datetime] = None,
        page_size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> SyncResult:
        """
        Busca entidades do sistema externo.

        Args:
            entity_type: Tipo de entidade (ex: "products", "clients")
            cursor: Cursor para paginação
            updated_since: Filtrar por data de modificação
            page_size: Tamanho da página
            filters: Filtros adicionais

        Returns:
            SyncResult com dados e cursor para próxima página
        """
        pass

    async def fetch_all_entities(
        self,
        entity_type: str,
        updated_since: Optional[datetime] = None,
        page_size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[SyncResult]:
        """
        Generator que busca todas as entidades com paginação automática.

        Yields:
            SyncResult para cada página
        """
        cursor = None
        page = 0

        while True:
            page += 1
            logger.debug(f"[{self.NAME}] Buscando {entity_type} página {page}...")

            result = await self.fetch_entities(
                entity_type=entity_type,
                cursor=cursor,
                updated_since=updated_since,
                page_size=page_size,
                filters=filters
            )

            yield result

            if not result.has_more or not result.cursor:
                break

            cursor = result.cursor

    @abstractmethod
    async def fetch_entity_by_id(
        self,
        entity_type: str,
        external_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca uma entidade específica pelo ID externo.

        Args:
            entity_type: Tipo de entidade
            external_id: ID no sistema externo

        Returns:
            Dados da entidade ou None se não encontrada
        """
        pass

    # ==================== Write Operations ====================

    async def create_entity(
        self,
        entity_type: str,
        data: Dict[str, Any]
    ) -> EntityResult:
        """
        Cria entidade no sistema externo.

        Args:
            entity_type: Tipo de entidade
            data: Dados da entidade

        Returns:
            EntityResult com ID externo criado
        """
        if not self.capabilities.supports_write:
            raise ConnectorError(
                f"Conector {self.NAME} não suporta escrita",
                connector=self.NAME
            )
        raise NotImplementedError()

    async def update_entity(
        self,
        entity_type: str,
        external_id: str,
        data: Dict[str, Any]
    ) -> EntityResult:
        """
        Atualiza entidade no sistema externo.

        Args:
            entity_type: Tipo de entidade
            external_id: ID no sistema externo
            data: Dados para atualizar

        Returns:
            EntityResult com resultado
        """
        if not self.capabilities.supports_write:
            raise ConnectorError(
                f"Conector {self.NAME} não suporta escrita",
                connector=self.NAME
            )
        raise NotImplementedError()

    async def delete_entity(
        self,
        entity_type: str,
        external_id: str
    ) -> EntityResult:
        """
        Remove entidade no sistema externo.

        Args:
            entity_type: Tipo de entidade
            external_id: ID no sistema externo

        Returns:
            EntityResult com resultado
        """
        if not self.capabilities.supports_delete:
            raise ConnectorError(
                f"Conector {self.NAME} não suporta deleção",
                connector=self.NAME
            )
        raise NotImplementedError()

    # ==================== Webhook Operations ====================

    async def validate_webhook(
        self,
        headers: Dict[str, str],
        body: bytes
    ) -> bool:
        """
        Valida assinatura de webhook.

        Args:
            headers: Headers da requisição
            body: Body raw da requisição

        Returns:
            True se válido
        """
        if not self.capabilities.supports_webhooks:
            raise ConnectorError(
                f"Conector {self.NAME} não suporta webhooks",
                connector=self.NAME
            )
        raise NotImplementedError()

    async def process_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> List[EntityResult]:
        """
        Processa payload de webhook.

        Args:
            event_type: Tipo de evento
            payload: Payload do webhook

        Returns:
            Lista de EntityResult com entidades afetadas
        """
        if not self.capabilities.supports_webhooks:
            raise ConnectorError(
                f"Conector {self.NAME} não suporta webhooks",
                connector=self.NAME
            )
        raise NotImplementedError()

    # ==================== Utilities ====================

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do conector."""
        if self._http_client:
            return self._http_client.get_metrics()
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """Retorna informações do conector."""
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "initialized": self._initialized,
            "capabilities": {
                "incremental_sync": self.capabilities.supports_incremental_sync,
                "full_sync": self.capabilities.supports_full_sync,
                "webhooks": self.capabilities.supports_webhooks,
                "write": self.capabilities.supports_write,
                "delete": self.capabilities.supports_delete,
                "entities": self.capabilities.supported_entities,
            },
            "account_id": str(self.account_id),
            "tenant_id": str(self.tenant_id),
        }
