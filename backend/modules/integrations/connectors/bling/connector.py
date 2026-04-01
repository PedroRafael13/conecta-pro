"""
Conector Bling ERP
Sprint 33: Integration Framework

Documentação: https://developer.bling.com.br/
API Base: https://www.bling.com.br/Api/v3/
"""

import logging
import time
from datetime import datetime
from typing import Any

from modules.integrations.connectors.base.auth import APIKeyAuth
from modules.integrations.connectors.base.connector import (
    BaseConnector,
    ConnectorCapabilities,
    HealthCheckResult,
    SyncResult,
)
from modules.integrations.connectors.base.exceptions import (
    APIError,
    ConnectorError,
)
from modules.integrations.connectors.base.rate_limiter import AdaptiveRateLimiter
from modules.integrations.sync.engine import ConnectorRegistry

logger = logging.getLogger(__name__)


class BlingConnector(BaseConnector):
    """
    Conector para Bling ERP.

    Entidades suportadas:
    - contatos (clientes/fornecedores)
    - produtos
    - estoques
    - pedidos (pedidos de venda)
    - notas (notas fiscais)
    """

    NAME = "bling"
    VERSION = "3.0.0"

    # Mapeamento de entidades para endpoints
    ENTITY_ENDPOINTS = {
        "contatos": "/contatos",
        "produtos": "/produtos",
        "estoques": "/estoques/saldos",
        "pedidos": "/pedidos/vendas",
        "notas": "/nfe",
    }

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            supports_incremental_sync=True,
            supports_full_sync=True,
            supports_webhooks=False,  # Bling tem webhooks limitados
            supports_write=True,
            supports_delete=False,  # API não permite delete
            supported_entities=list(self.ENTITY_ENDPOINTS.keys()),
            rate_limit_per_second=3.0,  # ~3 req/s (conservador)
            rate_limit_per_minute=100.0,
        )

    def _get_base_url(self) -> str:
        """Retorna URL base da API Bling v3."""
        return self.config.get("base_url", "https://www.bling.com.br/Api/v3")

    def _create_auth_strategy(self) -> APIKeyAuth:
        """Cria autenticação via API Key."""
        api_key = self.credentials.get("api_key")
        if not api_key:
            raise ConnectorError("API key do Bling não configurada", connector=self.NAME, error_code="MISSING_API_KEY")

        return APIKeyAuth(api_key=api_key, header_name="Authorization", header_prefix="Bearer")

    def _create_rate_limiter(self) -> AdaptiveRateLimiter:
        """Cria rate limiter adaptativo para Bling."""
        return AdaptiveRateLimiter(initial_rate=3.0, min_rate=0.5, max_rate=5.0, name=f"{self.NAME}-ratelimiter")

    async def health_check(self) -> HealthCheckResult:
        """Verifica conexão com a API Bling."""
        start = time.monotonic()

        try:
            # Buscar 1 contato para testar
            response = await self.http.get("/contatos", params={"limite": 1})

            latency = int((time.monotonic() - start) * 1000)

            if response.status_code == 200:
                return HealthCheckResult(
                    healthy=True, latency_ms=latency, message="Conexão OK", details={"api_version": "v3"}
                )
            else:
                return HealthCheckResult(
                    healthy=False,
                    latency_ms=latency,
                    message=f"Status inesperado: {response.status_code}",
                    details={"response": response.text[:200]},
                )

        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            return HealthCheckResult(
                healthy=False, latency_ms=latency, message=str(e), details={"error_type": type(e).__name__}
            )

    async def fetch_entities(
        self,
        entity_type: str,
        cursor: str | None = None,
        updated_since: datetime | None = None,
        page_size: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> SyncResult:
        """
        Busca entidades do Bling.

        Args:
            entity_type: Tipo de entidade (contatos, produtos, etc.)
            cursor: Página para buscar (Bling usa paginação por página)
            updated_since: Filtrar por data de alteração
            page_size: Tamanho da página (max 100 no Bling)
            filters: Filtros adicionais

        Returns:
            SyncResult com dados e cursor
        """
        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(
                f"Entidade não suportada: {entity_type}", connector=self.NAME, error_code="INVALID_ENTITY"
            )

        endpoint = self.ENTITY_ENDPOINTS[entity_type]

        # Montar parâmetros
        params: dict[str, Any] = {
            "limite": min(page_size, 100),  # Bling max 100
        }

        # Paginação
        if cursor:
            params["pagina"] = int(cursor)
        else:
            params["pagina"] = 1

        # Filtro de data (se suportado pelo endpoint)
        if updated_since and entity_type in ["contatos", "produtos", "pedidos"]:
            params["dataAlteracaoInicial"] = updated_since.strftime("%Y-%m-%d")

        # Filtros adicionais
        if filters:
            params.update(filters)

        try:
            response = await self.http.get(endpoint, params=params)

            if response.status_code == 404:
                return SyncResult(success=True, data=[], cursor=None, has_more=False, total_count=0)

            if response.status_code != 200:
                raise APIError(
                    f"Erro ao buscar {entity_type}: {response.status_code}",
                    connector=self.NAME,
                    status_code=response.status_code,
                    response_body=response.text[:500],
                )

            data = response.json()

            # Bling retorna { "data": [...] }
            items = data.get("data", [])

            # Verificar se tem mais páginas
            # Bling não retorna total, então verificamos pelo tamanho da página
            has_more = len(items) >= params["limite"]
            next_cursor = str(params["pagina"] + 1) if has_more else None

            logger.debug(f"[{self.NAME}] Buscou {len(items)} {entity_type} (página {params['pagina']})")

            return SyncResult(
                success=True,
                data=items,
                cursor=next_cursor,
                has_more=has_more,
                total_count=len(items),
                metadata={"page": params["pagina"]},
            )

        except APIError:
            raise
        except Exception as e:
            logger.error(f"[{self.NAME}] Erro ao buscar {entity_type}: {e}")
            return SyncResult(success=False, data=[], errors=[{"error": str(e), "entity_type": entity_type}])

    async def fetch_entity_by_id(self, entity_type: str, external_id: str) -> dict[str, Any] | None:
        """
        Busca uma entidade específica pelo ID.

        Args:
            entity_type: Tipo de entidade
            external_id: ID no Bling

        Returns:
            Dados da entidade ou None
        """
        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(f"Entidade não suportada: {entity_type}", connector=self.NAME)

        # Endpoint específico
        endpoint = f"{self.ENTITY_ENDPOINTS[entity_type]}/{external_id}"

        try:
            response = await self.http.get(endpoint)

            if response.status_code == 404:
                return None

            if response.status_code != 200:
                raise APIError(
                    f"Erro ao buscar {entity_type}/{external_id}", connector=self.NAME, status_code=response.status_code
                )

            data = response.json()
            return data.get("data")

        except APIError:
            raise
        except Exception as e:
            logger.error(f"[{self.NAME}] Erro ao buscar {entity_type}/{external_id}: {e}")
            return None

    async def create_entity(self, entity_type: str, data: dict[str, Any]):
        """Cria entidade no Bling."""
        from modules.integrations.connectors.base.connector import EntityResult

        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(f"Entidade não suportada: {entity_type}", connector=self.NAME)

        endpoint = self.ENTITY_ENDPOINTS[entity_type]

        try:
            response = await self.http.post(endpoint, json=data)

            if response.status_code in [200, 201]:
                result = response.json()
                external_id = result.get("data", {}).get("id")

                return EntityResult(
                    success=True,
                    external_id=str(external_id) if external_id else None,
                    action="created",
                    data=result.get("data"),
                )
            else:
                return EntityResult(
                    success=False, action="error", error=f"Status {response.status_code}: {response.text[:200]}"
                )

        except Exception as e:
            return EntityResult(success=False, action="error", error=str(e))

    async def update_entity(self, entity_type: str, external_id: str, data: dict[str, Any]):
        """Atualiza entidade no Bling."""
        from modules.integrations.connectors.base.connector import EntityResult

        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(f"Entidade não suportada: {entity_type}", connector=self.NAME)

        endpoint = f"{self.ENTITY_ENDPOINTS[entity_type]}/{external_id}"

        try:
            response = await self.http.put(endpoint, json=data)

            if response.status_code == 200:
                result = response.json()

                return EntityResult(success=True, external_id=external_id, action="updated", data=result.get("data"))
            elif response.status_code == 404:
                return EntityResult(
                    success=False, external_id=external_id, action="not_found", error="Entidade não encontrada"
                )
            else:
                return EntityResult(
                    success=False,
                    external_id=external_id,
                    action="error",
                    error=f"Status {response.status_code}: {response.text[:200]}",
                )

        except Exception as e:
            return EntityResult(success=False, external_id=external_id, action="error", error=str(e))


# Registrar conector
ConnectorRegistry.register(BlingConnector)
