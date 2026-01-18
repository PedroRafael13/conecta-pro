"""
Conector Sólides DP (Tangerino) - Gestão de Pessoas (RH + DP)
Sprint 33: Integration Framework

Documentação API: https://employer.tangerino.com.br
Autenticação: Basic <base64_token>

Endpoints disponíveis:
- /employee - Colaboradores
- /job-role - Cargos
- /workplace - Locais de trabalho
- /work-schedule - Escalas de trabalho
- /absence - Absenteísmos
- /occurrence - Ocorrências
"""

import logging
import time
import os
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from uuid import UUID
from dataclasses import dataclass

import httpx

from modules.integrations.connectors.base.connector import (
    BaseConnector,
    ConnectorCapabilities,
    SyncResult,
    HealthCheckResult,
    EntityResult,
)
from modules.integrations.connectors.base.auth import AuthStrategy
from modules.integrations.connectors.base.rate_limiter import AdaptiveRateLimiter
from modules.integrations.connectors.base.http_client import HTTPClientConfig
from modules.integrations.connectors.base.exceptions import (
    ConnectorError,
    APIError,
    AuthenticationError,
)

logger = logging.getLogger(__name__)


@dataclass
class SolidesTokenAuth(AuthStrategy):
    """
    Autenticação via Basic Auth Sólides.
    Formato: Basic <base64_encoded_credentials>
    """
    api_token: str  # Token já em base64

    async def authenticate(self, client: httpx.AsyncClient) -> None:
        """Aplica Basic auth ao cliente."""
        if not self.api_token:
            raise AuthenticationError("Token Sólides não configurado")

        client.headers["Authorization"] = f"Basic {self.api_token}"
        logger.debug("SolidesTokenAuth: Autenticação Basic aplicada")

    async def refresh_if_needed(self, client: httpx.AsyncClient) -> bool:
        """Token Sólides não expira automaticamente."""
        return False

    def get_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação."""
        return {"Authorization": f"Basic {self.api_token}"}

    def is_expired(self) -> bool:
        """Token Sólides não expira automaticamente."""
        return False


class SolidesConnector(BaseConnector):
    """
    Conector para Sólides DP (Tangerino) - Plataforma de Gestão de Pessoas.

    API: https://employer.tangerino.com.br

    Entidades suportadas:
    - employees (colaboradores)
    - job_roles (cargos)
    - workplaces (locais de trabalho)
    - work_schedules (escalas de trabalho)
    - absences (faltas, atrasos, afastamentos)
    - occurrences (advertências, elogios, etc.)
    - departments (departamentos)
    - cost_centers (centros de custo)
    """

    NAME = "solides"
    VERSION = "2.0.0"

    # URL base da API Sólides DP (Tangerino)
    BASE_URL = "https://employer.tangerino.com.br"

    # Mapeamento de entidades para endpoints
    ENTITY_ENDPOINTS = {
        "employees": "/employee/find-all",
        "job_roles": "/job-role/find-all",
        "workplaces": "/workplace/find-all",
        "work_schedules": "/work-schedule",
        "absences": "/absence/find-all",
        "occurrences": "/occurrence/find-all",
        "departments": "/department/find-all",
        "cost_centers": "/cost-center/find-all",
    }

    # Endpoints para operações específicas
    ENTITY_DETAIL_ENDPOINTS = {
        "employees": "/employee/{id}",
        "job_roles": "/job-role/{id}",
        "workplaces": "/workplace/{id}",
        "work_schedules": "/work-schedule/{id}",
        "absences": "/absence/{id}",
        "occurrences": "/occurrence/{id}",
        "departments": "/department/{id}",
        "cost_centers": "/cost-center/{id}",
    }

    # Endpoints para criação
    ENTITY_CREATE_ENDPOINTS = {
        "employees": "/employee",
        "occurrences": "/occurrence",
        "absences": "/absence",
    }

    # Campos de data por entidade para sync incremental
    DATE_FIELDS = {
        "employees": "updatedAt",
        "job_roles": "updatedAt",
        "workplaces": "updatedAt",
        "work_schedules": "updatedAt",
        "absences": "startDate",
        "occurrences": "date",
        "departments": "updatedAt",
        "cost_centers": "updatedAt",
    }

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            supports_incremental_sync=True,
            supports_full_sync=True,
            supports_webhooks=True,
            supports_write=True,
            supports_delete=False,  # Sólides DP não suporta delete direto
            supported_entities=list(self.ENTITY_ENDPOINTS.keys()),
            rate_limit_per_second=2.0,
            rate_limit_per_minute=60.0,
        )

    def _get_base_url(self) -> str:
        """Retorna URL base da API Sólides DP."""
        return self.config.get("base_url", self.BASE_URL)

    def _create_auth_strategy(self) -> SolidesTokenAuth:
        """Cria autenticação via Token Sólides."""
        api_token = self.credentials.get("api_token") or self.credentials.get("token")

        # Também verifica variável de ambiente
        if not api_token:
            api_token = os.getenv("SOLIDES_API_TOKEN")

        if not api_token:
            raise ConnectorError(
                "Token Sólides não configurado. Configure 'api_token' nas credenciais ou SOLIDES_API_TOKEN no ambiente.",
                connector=self.NAME,
                error_code="MISSING_TOKEN"
            )

        return SolidesTokenAuth(api_token=api_token)

    def _create_rate_limiter(self) -> AdaptiveRateLimiter:
        """Cria rate limiter adaptativo para Sólides."""
        rate_limit = self.config.get("rate_limit_per_minute", 60)
        return AdaptiveRateLimiter(
            initial_rate=rate_limit / 60,  # Converte para req/s
            min_rate=0.5,
            max_rate=2.0,
            name=f"{self.NAME}-ratelimiter"
        )

    def _create_http_config(self) -> HTTPClientConfig:
        """Cria configuração HTTP customizada."""
        return HTTPClientConfig(
            base_url=self._get_base_url(),
            timeout_connect=10.0,
            timeout_read=60.0,  # Sólides pode ser lento em listagens grandes
            timeout_write=30.0,
            max_retries=3,
            headers={
                "User-Agent": f"ConectaPRO-Integration/{self.VERSION}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _get_endpoint(self, entity_type: str, operation: str = "list") -> str:
        """
        Retorna endpoint para a entidade.

        Args:
            entity_type: Tipo da entidade
            operation: 'list', 'detail', 'create'
        """
        if operation == "detail":
            return self.ENTITY_DETAIL_ENDPOINTS.get(entity_type, "")
        elif operation == "create":
            return self.ENTITY_CREATE_ENDPOINTS.get(entity_type, "")
        return self.ENTITY_ENDPOINTS.get(entity_type, "")

    async def health_check(self) -> HealthCheckResult:
        """Verifica conexão com a API Sólides DP."""
        start = time.monotonic()

        try:
            # Usa endpoint /test para verificar conexão
            response = await self.http.get("/test")

            latency = int((time.monotonic() - start) * 1000)

            if response.status_code == 200:
                # Tenta extrair mensagem de boas-vindas
                try:
                    welcome_msg = response.text[:100] if response.text else "OK"
                except Exception:
                    welcome_msg = "OK"

                return HealthCheckResult(
                    healthy=True,
                    latency_ms=latency,
                    message=f"Conexão OK - {welcome_msg}",
                    details={"api": "Sólides DP (Tangerino)", "api_url": self._get_base_url()}
                )
            elif response.status_code == 401:
                return HealthCheckResult(
                    healthy=False,
                    latency_ms=latency,
                    message="Falha de autenticação - Token inválido ou expirado",
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
        page_size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> SyncResult:
        """
        Busca entidades do Sólides DP.

        Args:
            entity_type: Tipo de entidade (employees, job_roles, etc.)
            cursor: Página para buscar (paginação por página)
            updated_since: Filtrar por data de alteração
            page_size: Tamanho da página (max 100)
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

        endpoint = self._get_endpoint(entity_type)

        # Montar parâmetros - Sólides DP usa 'size' e 'page'
        params: Dict[str, Any] = {
            "size": min(page_size, 100),
        }

        # Paginação
        if cursor:
            params["page"] = int(cursor)
        else:
            params["page"] = 0  # Sólides DP usa 0-indexed

        # Filtro de data (sync incremental)
        if updated_since:
            date_field = self.DATE_FIELDS.get(entity_type, "updatedAt")
            params["updatedAfter"] = updated_since.strftime("%Y-%m-%dT%H:%M:%S")

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

            # Sólides DP retorna:
            # - Lista direta para find-all
            # - { content: [...], totalElements, totalPages, ... } para paginados
            if isinstance(data, dict):
                items = data.get("content", data.get("data", []))
                total_pages = data.get("totalPages", 1)
                current_page = data.get("number", params["page"])
                total_count = data.get("totalElements", len(items))
            elif isinstance(data, list):
                items = data
                total_pages = 1
                current_page = 0
                total_count = len(items)
            else:
                items = []
                total_pages = 1
                current_page = 0
                total_count = 0

            has_more = current_page < (total_pages - 1)
            next_cursor = str(current_page + 1) if has_more else None

            logger.debug(
                f"[{self.NAME}] Buscou {len(items)} {entity_type} "
                f"(página {current_page + 1}/{total_pages})"
            )

            return SyncResult(
                success=True,
                data=items,
                cursor=next_cursor,
                has_more=has_more,
                total_count=total_count,
                metadata={
                    "page": current_page,
                    "total_pages": total_pages,
                    "per_page": params["size"]
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
            external_id: ID no Sólides DP

        Returns:
            Dados da entidade ou None
        """
        if entity_type not in self.ENTITY_DETAIL_ENDPOINTS:
            raise ConnectorError(
                f"Entidade não suportada: {entity_type}",
                connector=self.NAME
            )

        # Usa o endpoint de detalhe com o ID
        endpoint_template = self._get_endpoint(entity_type, operation="detail")
        endpoint = endpoint_template.format(id=external_id)

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
            # Retorna dados diretos ou dentro de "data"
            return data.get("data", data) if isinstance(data, dict) else data

        except APIError:
            raise
        except Exception as e:
            logger.error(f"[{self.NAME}] Erro ao buscar {entity_type}/{external_id}: {e}")
            return None

    async def create_entity(
        self,
        entity_type: str,
        data: Dict[str, Any]
    ) -> EntityResult:
        """Cria entidade no Sólides DP."""
        if entity_type not in self.ENTITY_CREATE_ENDPOINTS:
            return EntityResult(
                success=False,
                action="error",
                error=f"Entidade {entity_type} não suporta criação"
            )

        endpoint = self._get_endpoint(entity_type, operation="create")

        try:
            response = await self.http.post(endpoint, json=data)

            if response.status_code in [200, 201]:
                result = response.json()
                result_data = result.get("data", result)
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
                    error=str(error_data.get("errors", error_data.get("message", error_data)))
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
    ) -> EntityResult:
        """Atualiza entidade no Sólides DP."""
        if entity_type not in self.ENTITY_DETAIL_ENDPOINTS:
            return EntityResult(
                success=False,
                external_id=external_id,
                action="error",
                error=f"Entidade {entity_type} não suporta atualização"
            )

        endpoint_template = self._get_endpoint(entity_type, operation="detail")
        endpoint = endpoint_template.format(id=external_id)

        try:
            response = await self.http.put(endpoint, json=data)

            if response.status_code == 200:
                result = response.json()

                return EntityResult(
                    success=True,
                    external_id=external_id,
                    action="updated",
                    data=result.get("data", result)
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
                    error=str(error_data.get("errors", error_data.get("message", error_data)))
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

    async def delete_entity(
        self,
        entity_type: str,
        external_id: str
    ) -> EntityResult:
        """
        Remove/demite entidade no Sólides DP.
        Nota: Sólides DP geralmente não suporta DELETE direto.
        """
        # Sólides DP não suporta delete direto na maioria das entidades
        return EntityResult(
            success=False,
            external_id=external_id,
            action="error",
            error="Sólides DP não suporta remoção direta de entidades"
        )

    async def _delete_entity_internal(
        self,
        entity_type: str,
        external_id: str
    ) -> EntityResult:
        """Método interno para delete (caso futura API suporte)."""
        endpoint_template = self._get_endpoint(entity_type, operation="detail")
        endpoint = endpoint_template.format(id=external_id)

        try:
            response = await self.http.delete(endpoint)

            if response.status_code in [200, 204]:
                return EntityResult(
                    success=True,
                    external_id=external_id,
                    action="deleted"
                )
            elif response.status_code == 404:
                return EntityResult(
                    success=False,
                    external_id=external_id,
                    action="not_found",
                    error="Entidade não encontrada"
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

    # ==================== MÉTODOS ESPECÍFICOS SÓLIDES DP ====================

    async def fetch_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Busca colaborador específico com todos os dados."""
        return await self.fetch_entity_by_id("employees", employee_id)

    async def fetch_employees_active(
        self,
        page: int = 0,
        per_page: int = 100
    ) -> SyncResult:
        """Busca apenas colaboradores ativos."""
        return await self.fetch_entities(
            entity_type="employees",
            cursor=str(page),
            page_size=per_page,
            filters={"status": "ACTIVE"}
        )

    async def create_employee(self, data: Dict[str, Any]) -> EntityResult:
        """Cria novo colaborador no Sólides DP."""
        return await self.create_entity("employees", data)

    async def update_employee(
        self,
        employee_id: str,
        data: Dict[str, Any]
    ) -> EntityResult:
        """Atualiza colaborador existente."""
        return await self.update_entity("employees", employee_id, data)

    async def terminate_employee(
        self,
        employee_id: str,
        termination_date: date,
        reason: Optional[str] = None
    ) -> EntityResult:
        """Demite colaborador."""
        data = {
            "terminationDate": termination_date.isoformat(),
            "status": "TERMINATED"
        }
        if reason:
            data["terminationReason"] = reason

        return await self.update_entity("employees", employee_id, data)

    async def fetch_occurrences_by_employee(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca ocorrências de um colaborador específico.

        Args:
            employee_id: ID do colaborador
            start_date: Data inicial do período
            end_date: Data final do período

        Returns:
            Lista de ocorrências
        """
        filters = {"employeeId": employee_id}
        if start_date:
            filters["startDate"] = start_date.isoformat()
        if end_date:
            filters["endDate"] = end_date.isoformat()

        result = await self.fetch_entities(
            entity_type="occurrences",
            filters=filters
        )

        return result.data if result.success else []

    async def create_occurrence(
        self,
        employee_id: str,
        occurrence_type: str,
        description: str,
        occurrence_date: date,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> EntityResult:
        """
        Cria nova ocorrência para colaborador.

        Args:
            employee_id: ID do colaborador
            occurrence_type: Tipo da ocorrência
            description: Descrição da ocorrência
            occurrence_date: Data da ocorrência
            additional_data: Dados extras

        Returns:
            EntityResult com resultado
        """
        data = {
            "employeeId": int(employee_id),
            "type": occurrence_type,
            "description": description,
            "date": occurrence_date.isoformat(),
        }
        if additional_data:
            data.update(additional_data)

        return await self.create_entity("occurrences", data)

    async def fetch_absences_by_employee(
        self,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca absenteísmos de um colaborador específico.

        Args:
            employee_id: ID do colaborador
            start_date: Data inicial do período
            end_date: Data final do período

        Returns:
            Lista de absenteísmos
        """
        filters = {"employeeId": employee_id}
        if start_date:
            filters["startDate"] = start_date.isoformat()
        if end_date:
            filters["endDate"] = end_date.isoformat()

        result = await self.fetch_entities(
            entity_type="absences",
            filters=filters
        )

        return result.data if result.success else []

    async def fetch_departments(self) -> List[Dict[str, Any]]:
        """Busca todos os departamentos."""
        result = await self.fetch_entities("departments")
        return result.data if result.success else []

    async def fetch_job_roles(self) -> List[Dict[str, Any]]:
        """Busca todos os cargos."""
        result = await self.fetch_entities("job_roles")
        return result.data if result.success else []

    async def fetch_workplaces(self) -> List[Dict[str, Any]]:
        """Busca todos os locais de trabalho."""
        result = await self.fetch_entities("workplaces")
        return result.data if result.success else []

    async def fetch_work_schedules(self) -> List[Dict[str, Any]]:
        """Busca todas as escalas de trabalho."""
        result = await self.fetch_entities("work_schedules")
        return result.data if result.success else []

    async def fetch_cost_centers(self) -> List[Dict[str, Any]]:
        """Busca todos os centros de custo."""
        result = await self.fetch_entities("cost_centers")
        return result.data if result.success else []

    # ==================== WEBHOOKS ====================

    async def validate_webhook(
        self,
        headers: Dict[str, str],
        body: bytes
    ) -> bool:
        """
        Valida assinatura de webhook do Sólides.

        Args:
            headers: Headers da requisição
            body: Body raw da requisição

        Returns:
            True se válido
        """
        import hmac
        import hashlib

        webhook_secret = self.credentials.get("webhook_secret") or os.getenv("SOLIDES_WEBHOOK_SECRET")

        if not webhook_secret:
            logger.warning(f"[{self.NAME}] Webhook secret não configurado, pulando validação")
            return True

        # Sólides usa X-Solides-Signature ou X-Webhook-Signature
        signature = headers.get("X-Solides-Signature") or headers.get("X-Webhook-Signature", "")

        if not signature:
            logger.warning(f"[{self.NAME}] Assinatura não encontrada no header")
            return False

        # Calcula HMAC SHA256
        expected = hmac.new(
            webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        # Remove prefixo sha256= se presente
        if signature.startswith("sha256="):
            signature = signature[7:]

        is_valid = hmac.compare_digest(signature, expected)

        if not is_valid:
            logger.warning(f"[{self.NAME}] Assinatura de webhook inválida")

        return is_valid


# Registrar conector (se o registry existir)
try:
    from modules.integrations.sync.engine import ConnectorRegistry
    ConnectorRegistry.register(SolidesConnector)
except ImportError:
    pass
