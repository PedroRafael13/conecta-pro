"""
Conector Sólides - Gestão de Pessoas
Sprint 33: Integration Framework

Documentação: https://developers.solides.com.br/
API Base: https://api.solides.com.br/v1/
"""

import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from modules.integrations.connectors.base.connector import (
    BaseConnector,
    ConnectorCapabilities,
    SyncResult,
    HealthCheckResult,
)
from modules.integrations.connectors.base.auth import OAuth2ClientCredentials
from modules.integrations.connectors.base.rate_limiter import AdaptiveRateLimiter
from modules.integrations.connectors.base.exceptions import (
    ConnectorError,
    APIError,
    AuthenticationError,
)

logger = logging.getLogger(__name__)


class SolidesConnector(BaseConnector):
    """
    Conector para Sólides - Plataforma de Gestão de Pessoas.

    Entidades suportadas:
    - colaboradores (funcionários)
    - departamentos
    - cargos
    - vagas (recrutamento)
    - candidatos
    - inscricoes (candidaturas)
    - avaliacoes (desempenho)
    - pesquisas_clima
    """

    NAME = "solides"
    VERSION = "1.0.0"

    # Mapeamento de entidades para endpoints
    ENTITY_ENDPOINTS = {
        "colaboradores": "/employees",
        "departamentos": "/departments",
        "cargos": "/positions",
        "vagas": "/job-openings",
        "candidatos": "/candidates",
        "inscricoes": "/applications",
        "avaliacoes": "/assessments",
        "pesquisas_clima": "/climate-surveys",
    }

    # Campos de data por entidade para sync incremental
    DATE_FIELDS = {
        "colaboradores": "updated_at",
        "departamentos": "updated_at",
        "cargos": "updated_at",
        "vagas": "updated_at",
        "candidatos": "updated_at",
        "inscricoes": "updated_at",
        "avaliacoes": "updated_at",
        "pesquisas_clima": "updated_at",
    }

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            supports_incremental_sync=True,
            supports_full_sync=True,
            supports_webhooks=True,
            supports_write=True,
            supports_delete=False,
            supported_entities=list(self.ENTITY_ENDPOINTS.keys()),
            rate_limit_per_second=10.0,
            rate_limit_per_minute=300.0,
        )

    def _get_base_url(self) -> str:
        """Retorna URL base da API Sólides."""
        return self.config.get("base_url", "https://api.solides.com.br/v1")

    def _create_auth_strategy(self) -> OAuth2ClientCredentials:
        """Cria autenticação via OAuth2 Client Credentials."""
        client_id = self.credentials.get("client_id")
        client_secret = self.credentials.get("client_secret")

        if not client_id or not client_secret:
            raise ConnectorError(
                "Credenciais OAuth2 do Sólides não configuradas",
                connector=self.NAME,
                error_code="MISSING_OAUTH_CREDENTIALS"
            )

        token_url = self.config.get(
            "token_url",
            "https://api.solides.com.br/oauth/token"
        )

        return OAuth2ClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=self.config.get("scopes", ["read", "write"])
        )

    def _create_rate_limiter(self) -> AdaptiveRateLimiter:
        """Cria rate limiter adaptativo para Sólides."""
        return AdaptiveRateLimiter(
            initial_rate=10.0,
            min_rate=1.0,
            max_rate=20.0,
            name=f"{self.NAME}-ratelimiter"
        )

    async def health_check(self) -> HealthCheckResult:
        """Verifica conexão com a API Sólides."""
        start = time.monotonic()

        try:
            # Buscar 1 departamento para testar conexão
            response = await self.http.get(
                "/departments",
                params={"per_page": 1}
            )

            latency = int((time.monotonic() - start) * 1000)

            if response.status_code == 200:
                return HealthCheckResult(
                    healthy=True,
                    latency_ms=latency,
                    message="Conexão OK",
                    details={"api_version": "v1"}
                )
            elif response.status_code == 401:
                return HealthCheckResult(
                    healthy=False,
                    latency_ms=latency,
                    message="Falha de autenticação",
                    details={"status_code": 401}
                )
            else:
                return HealthCheckResult(
                    healthy=False,
                    latency_ms=latency,
                    message=f"Status inesperado: {response.status_code}",
                    details={"response": response.text[:200]}
                )

        except AuthenticationError as e:
            latency = int((time.monotonic() - start) * 1000)
            return HealthCheckResult(
                healthy=False,
                latency_ms=latency,
                message=f"Erro de autenticação: {str(e)}",
                details={"error_type": "AuthenticationError"}
            )
        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            return HealthCheckResult(
                healthy=False,
                latency_ms=latency,
                message=str(e),
                details={"error_type": type(e).__name__}
            )

    async def fetch_entities(
        self,
        entity_type: str,
        cursor: Optional[str] = None,
        updated_since: Optional[datetime] = None,
        page_size: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> SyncResult:
        """
        Busca entidades do Sólides.

        Args:
            entity_type: Tipo de entidade (colaboradores, vagas, etc.)
            cursor: Página para buscar (paginação por página)
            updated_since: Filtrar por data de alteração
            page_size: Tamanho da página (default 50)
            filters: Filtros adicionais

        Returns:
            SyncResult com dados e cursor
        """
        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(
                f"Entidade não suportada: {entity_type}",
                connector=self.NAME,
                error_code="INVALID_ENTITY"
            )

        endpoint = self.ENTITY_ENDPOINTS[entity_type]

        # Montar parâmetros
        params: Dict[str, Any] = {
            "per_page": min(page_size, 100),
        }

        # Paginação
        if cursor:
            params["page"] = int(cursor)
        else:
            params["page"] = 1

        # Filtro de data (sync incremental)
        if updated_since:
            date_field = self.DATE_FIELDS.get(entity_type, "updated_at")
            params[f"{date_field}_from"] = updated_since.strftime("%Y-%m-%dT%H:%M:%S")

        # Filtros adicionais
        if filters:
            params.update(filters)

        try:
            response = await self.http.get(endpoint, params=params)

            if response.status_code == 404:
                return SyncResult(
                    success=True,
                    data=[],
                    cursor=None,
                    has_more=False,
                    total_count=0
                )

            if response.status_code != 200:
                raise APIError(
                    f"Erro ao buscar {entity_type}: {response.status_code}",
                    connector=self.NAME,
                    status_code=response.status_code,
                    response_body=response.text[:500]
                )

            data = response.json()

            # Sólides retorna { "data": [...], "meta": {...} }
            items = data.get("data", [])
            meta = data.get("meta", {})

            # Verificar se tem mais páginas
            total_pages = meta.get("total_pages", 1)
            current_page = meta.get("current_page", params["page"])
            has_more = current_page < total_pages
            next_cursor = str(current_page + 1) if has_more else None

            logger.debug(
                f"[{self.NAME}] Buscou {len(items)} {entity_type} "
                f"(página {current_page}/{total_pages})"
            )

            return SyncResult(
                success=True,
                data=items,
                cursor=next_cursor,
                has_more=has_more,
                total_count=meta.get("total", len(items)),
                metadata={
                    "page": current_page,
                    "total_pages": total_pages,
                    "per_page": params["per_page"]
                }
            )

        except APIError:
            raise
        except Exception as e:
            logger.error(f"[{self.NAME}] Erro ao buscar {entity_type}: {e}")
            return SyncResult(
                success=False,
                data=[],
                errors=[{"error": str(e), "entity_type": entity_type}]
            )

    async def fetch_entity_by_id(
        self,
        entity_type: str,
        external_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca uma entidade específica pelo ID.

        Args:
            entity_type: Tipo de entidade
            external_id: ID no Sólides

        Returns:
            Dados da entidade ou None
        """
        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(
                f"Entidade não suportada: {entity_type}",
                connector=self.NAME
            )

        endpoint = f"{self.ENTITY_ENDPOINTS[entity_type]}/{external_id}"

        try:
            response = await self.http.get(endpoint)

            if response.status_code == 404:
                return None

            if response.status_code != 200:
                raise APIError(
                    f"Erro ao buscar {entity_type}/{external_id}",
                    connector=self.NAME,
                    status_code=response.status_code
                )

            data = response.json()
            return data.get("data")

        except APIError:
            raise
        except Exception as e:
            logger.error(f"[{self.NAME}] Erro ao buscar {entity_type}/{external_id}: {e}")
            return None

    async def create_entity(
        self,
        entity_type: str,
        data: Dict[str, Any]
    ):
        """Cria entidade no Sólides."""
        from modules.integrations.connectors.base.connector import EntityResult

        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(
                f"Entidade não suportada: {entity_type}",
                connector=self.NAME
            )

        # Entidades que não permitem criação via API
        read_only_entities = ["pesquisas_clima", "avaliacoes"]
        if entity_type in read_only_entities:
            return EntityResult(
                success=False,
                action="error",
                error=f"Entidade {entity_type} é somente leitura"
            )

        endpoint = self.ENTITY_ENDPOINTS[entity_type]

        try:
            response = await self.http.post(endpoint, json=data)

            if response.status_code in [200, 201]:
                result = response.json()
                result_data = result.get("data", {})
                external_id = result_data.get("id")

                return EntityResult(
                    success=True,
                    external_id=str(external_id) if external_id else None,
                    action="created",
                    data=result_data
                )
            elif response.status_code == 422:
                # Erro de validação
                error_data = response.json()
                return EntityResult(
                    success=False,
                    action="validation_error",
                    error=str(error_data.get("errors", error_data))
                )
            else:
                return EntityResult(
                    success=False,
                    action="error",
                    error=f"Status {response.status_code}: {response.text[:200]}"
                )

        except Exception as e:
            return EntityResult(
                success=False,
                action="error",
                error=str(e)
            )

    async def update_entity(
        self,
        entity_type: str,
        external_id: str,
        data: Dict[str, Any]
    ):
        """Atualiza entidade no Sólides."""
        from modules.integrations.connectors.base.connector import EntityResult

        if entity_type not in self.ENTITY_ENDPOINTS:
            raise ConnectorError(
                f"Entidade não suportada: {entity_type}",
                connector=self.NAME
            )

        endpoint = f"{self.ENTITY_ENDPOINTS[entity_type]}/{external_id}"

        try:
            response = await self.http.put(endpoint, json=data)

            if response.status_code == 200:
                result = response.json()

                return EntityResult(
                    success=True,
                    external_id=external_id,
                    action="updated",
                    data=result.get("data")
                )
            elif response.status_code == 404:
                return EntityResult(
                    success=False,
                    external_id=external_id,
                    action="not_found",
                    error="Entidade não encontrada"
                )
            elif response.status_code == 422:
                error_data = response.json()
                return EntityResult(
                    success=False,
                    external_id=external_id,
                    action="validation_error",
                    error=str(error_data.get("errors", error_data))
                )
            else:
                return EntityResult(
                    success=False,
                    external_id=external_id,
                    action="error",
                    error=f"Status {response.status_code}: {response.text[:200]}"
                )

        except Exception as e:
            return EntityResult(
                success=False,
                external_id=external_id,
                action="error",
                error=str(e)
            )

    async def fetch_employee_profile(
        self,
        employee_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca perfil comportamental de um colaborador.

        Args:
            employee_id: ID do colaborador

        Returns:
            Dados do perfil ou None
        """
        try:
            response = await self.http.get(
                f"/employees/{employee_id}/profile"
            )

            if response.status_code == 404:
                return None

            if response.status_code != 200:
                logger.warning(
                    f"[{self.NAME}] Erro ao buscar perfil do colaborador "
                    f"{employee_id}: {response.status_code}"
                )
                return None

            data = response.json()
            return data.get("data")

        except Exception as e:
            logger.error(
                f"[{self.NAME}] Erro ao buscar perfil do colaborador "
                f"{employee_id}: {e}"
            )
            return None

    async def fetch_application_history(
        self,
        application_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Busca histórico de etapas de uma candidatura.

        Args:
            application_id: ID da candidatura

        Returns:
            Lista de etapas ou None
        """
        try:
            response = await self.http.get(
                f"/applications/{application_id}/history"
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return data.get("data", [])

        except Exception as e:
            logger.error(
                f"[{self.NAME}] Erro ao buscar histórico da candidatura "
                f"{application_id}: {e}"
            )
            return None


# Registrar conector
from modules.integrations.sync.engine import ConnectorRegistry
ConnectorRegistry.register(SolidesConnector)
