"""
WebhookService - Serviço para gerenciamento de webhooks
Sprint 32: API Gateway / Integrações
"""
# pylint: disable=too-many-locals

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.models import (
    WebhookConfig,
    IntegrationLog,
    WebhookStatus,
    WebhookAuthType,
    LogType,
    LogLevel,
    LogStatus,
)
from modules.integrations.repositories import IntegrationRepository
from modules.integrations.schemas import (
    WebhookConfigCreate,
    WebhookConfigUpdate,
    WebhookTestRequest,
    WebhookTestResponse,
)

logger = logging.getLogger(__name__)


class WebhookService:
    """Serviço para gerenciamento e entrega de webhooks."""

    def __init__(self, db: AsyncSession):
        """Inicializa o serviço."""
        self.db = db
        self.repository = IntegrationRepository(db)
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Obtém cliente HTTP."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                follow_redirects=True
            )
        return self._http_client

    async def close(self) -> None:
        """Fecha recursos."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    # ==================== CRUD Operations ====================

    async def create_webhook(
        self,
        data: WebhookConfigCreate,
        user_id: Optional[UUID] = None
    ) -> WebhookConfig:
        """Cria um novo webhook."""
        # Gera secret key para HMAC
        secret_key = WebhookConfig.generate_secret()

        webhook = WebhookConfig(
            **data.model_dump(),
            secret_key=secret_key,
            created_by=user_id,
            updated_by=user_id
        )

        result = await self.repository.create_webhook(webhook)

        # Log
        log = IntegrationLog(
            webhook_id=result.id,
            log_type=LogType.SYSTEM,
            level=LogLevel.INFO,
            status=LogStatus.SUCCESS,
            action="webhook_created",
            metadata={"name": data.name, "events": data.events}
        )
        await self.repository.create_log(log)

        return result

    async def get_webhook(self, webhook_id: UUID) -> Optional[WebhookConfig]:
        """Busca webhook por ID."""
        return await self.repository.get_webhook_by_id(webhook_id)

    async def list_webhooks(
        self,
        client_id: Optional[UUID] = None,
        status: Optional[WebhookStatus] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[WebhookConfig], int, int]:
        """Lista webhooks com paginação."""
        skip = (page - 1) * page_size
        webhooks, total = await self.repository.list_webhooks(
            client_id=client_id,
            status=status,
            skip=skip,
            limit=page_size
        )
        pages = (total + page_size - 1) // page_size
        return webhooks, total, pages

    async def update_webhook(
        self,
        webhook_id: UUID,
        data: WebhookConfigUpdate,
        user_id: Optional[UUID] = None
    ) -> WebhookConfig:
        """Atualiza webhook."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(webhook, key, value)

        webhook.updated_by = user_id

        return await self.repository.update_webhook(webhook)

    async def delete_webhook(self, webhook_id: UUID) -> bool:
        """Deleta webhook."""
        result = await self.repository.delete_webhook(webhook_id)

        if result:
            log = IntegrationLog(
                webhook_id=webhook_id,
                log_type=LogType.SYSTEM,
                level=LogLevel.INFO,
                status=LogStatus.SUCCESS,
                action="webhook_deleted"
            )
            await self.repository.create_log(log)

        return result

    async def regenerate_secret(
        self,
        webhook_id: UUID,
        user_id: Optional[UUID] = None
    ) -> str:
        """Regenera secret key do webhook."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        new_secret = WebhookConfig.generate_secret()
        webhook.secret_key = new_secret
        webhook.updated_by = user_id

        await self.repository.update_webhook(webhook)

        log = IntegrationLog(
            webhook_id=webhook_id,
            log_type=LogType.SYSTEM,
            level=LogLevel.WARNING,
            status=LogStatus.SUCCESS,
            action="webhook_secret_regenerated"
        )
        await self.repository.create_log(log)

        return new_secret

    # ==================== Status Management ====================

    async def activate_webhook(self, webhook_id: UUID) -> WebhookConfig:
        """Ativa webhook."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        webhook.activate()
        return await self.repository.update_webhook(webhook)

    async def pause_webhook(self, webhook_id: UUID) -> WebhookConfig:
        """Pausa webhook."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        webhook.pause()
        return await self.repository.update_webhook(webhook)

    async def disable_webhook(self, webhook_id: UUID) -> WebhookConfig:
        """Desativa webhook."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        webhook.disable()
        return await self.repository.update_webhook(webhook)

    async def reset_failures(self, webhook_id: UUID) -> WebhookConfig:
        """Reseta contadores de falha."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        webhook.reset_failures()
        return await self.repository.update_webhook(webhook)

    # ==================== Delivery ====================

    async def trigger_event(
        self,
        event: str,
        payload: Dict[str, Any],
        client_id: Optional[UUID] = None,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Dispara evento para todos os webhooks inscritos.
        Retorna lista de resultados das entregas.
        """
        # Busca webhooks para o evento
        webhooks = await self.repository.get_webhooks_for_event(
            event=event,
            client_id=client_id
        )

        if not webhooks:
            logger.debug(f"Nenhum webhook inscrito para evento: {event}")
            return []

        results = []

        # Processa cada webhook
        for webhook in webhooks:
            result = await self._deliver_webhook(
                webhook=webhook,
                event=event,
                payload=payload,
                correlation_id=correlation_id
            )
            results.append(result)

        return results

    async def _deliver_webhook(
        self,
        webhook: WebhookConfig,
        event: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Entrega payload para um webhook."""
        start_time = datetime.utcnow()
        result = {
            "webhook_id": str(webhook.id),
            "webhook_name": webhook.name,
            "event": event,
            "success": False,
            "status_code": None,
            "error": None,
            "response_time_ms": 0,
            "retry_count": retry_count
        }

        try:
            # Prepara payload
            full_payload = self._prepare_payload(webhook, event, payload)
            payload_str = json.dumps(full_payload)

            # Prepara headers
            headers = self._prepare_headers(webhook, payload_str)
            if correlation_id:
                headers["X-Correlation-ID"] = correlation_id

            # Prepara auth
            auth = self._prepare_auth(webhook)

            # Faz requisição
            client = await self._get_http_client()
            response = await client.request(
                method=webhook.method,
                url=webhook.url,
                content=payload_str,
                headers=headers,
                auth=auth
            )

            response_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            result["status_code"] = response.status_code
            result["response_time_ms"] = response_time
            result["success"] = 200 <= response.status_code < 300

            # Registra entrega
            webhook.record_delivery(
                success=result["success"],
                response_time_ms=response_time,
                error=None if result["success"] else f"HTTP {response.status_code}"
            )
            await self.repository.update_webhook(webhook)

            # Log
            log = IntegrationLog.create_webhook_log(
                webhook_id=str(webhook.id),
                success=result["success"],
                duration_ms=response_time,
                status_code=response.status_code,
                correlation_id=correlation_id,
                metadata={"event": event}
            )
            await self.repository.create_log(log)

        except httpx.TimeoutException as e:
            result["error"] = "Timeout"
            result["response_time_ms"] = webhook.timeout_seconds * 1000
            await self._handle_delivery_error(
                webhook, event, str(e), correlation_id
            )

        except httpx.RequestError as e:
            result["error"] = str(e)
            result["response_time_ms"] = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
            await self._handle_delivery_error(
                webhook, event, str(e), correlation_id
            )

        except (ValueError, RuntimeError) as e:
            result["error"] = str(e)
            result["response_time_ms"] = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
            await self._handle_delivery_error(
                webhook, event, str(e), correlation_id
            )

        # Retry se falhou e retry habilitado
        if not result["success"] and webhook.retry_enabled:
            if retry_count < webhook.max_retries:
                delay = webhook.retry_delay_seconds * (
                    webhook.retry_backoff_multiplier ** retry_count
                )
                logger.info(
                    f"Agendando retry {retry_count + 1} para webhook "
                    f"{webhook.id} em {delay}s"
                )
                # Em produção, isso seria feito por um worker
                asyncio.create_task(
                    self._schedule_retry(
                        webhook, event, payload, correlation_id,
                        retry_count + 1, delay
                    )
                )

        return result

    async def _schedule_retry(
        self,
        webhook: WebhookConfig,
        event: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str],
        retry_count: int,
        delay: int
    ) -> None:
        """Agenda retry de entrega."""
        await asyncio.sleep(delay)
        await self._deliver_webhook(
            webhook=webhook,
            event=event,
            payload=payload,
            correlation_id=correlation_id,
            retry_count=retry_count
        )

    async def _handle_delivery_error(
        self,
        webhook: WebhookConfig,
        event: str,
        error: str,
        correlation_id: Optional[str] = None
    ) -> None:
        """Trata erro de entrega."""
        webhook.record_delivery(
            success=False,
            response_time_ms=0,
            error=error
        )
        await self.repository.update_webhook(webhook)

        log = IntegrationLog.create_webhook_log(
            webhook_id=str(webhook.id),
            success=False,
            duration_ms=0,
            error_message=error,
            correlation_id=correlation_id,
            metadata={"event": event}
        )
        await self.repository.create_log(log)

    def _prepare_payload(
        self,
        webhook: WebhookConfig,
        event: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara payload para envio."""
        if webhook.payload_template:
            # Template customizado - em produção usaria Jinja2
            return payload

        # Envelope padrão
        return {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "webhook_id": str(webhook.id),
            "data": payload
        }

    def _prepare_headers(
        self,
        webhook: WebhookConfig,
        payload_str: str
    ) -> Dict[str, str]:
        """Prepara headers para envio."""
        headers = {
            "Content-Type": webhook.content_type,
            "User-Agent": "ERP-ConectaMais-Webhook/1.0",
            "X-Webhook-ID": str(webhook.id)
        }

        # Adiciona assinatura HMAC
        if webhook.auth_type == WebhookAuthType.HMAC and webhook.secret_key:
            signature = webhook.sign_payload(payload_str)
            headers["X-Webhook-Signature"] = signature

        # Headers customizados
        if webhook.custom_headers:
            headers.update(webhook.custom_headers)

        return headers

    def _prepare_auth(
        self,
        webhook: WebhookConfig
    ) -> Optional[httpx.Auth]:
        """Prepara autenticação para envio."""
        if not webhook.auth_credentials:
            return None

        if webhook.auth_type == WebhookAuthType.BASIC:
            return httpx.BasicAuth(
                username=webhook.auth_credentials.get("username", ""),
                password=webhook.auth_credentials.get("password", "")
            )

        if webhook.auth_type == WebhookAuthType.BEARER:
            # Bearer é tratado via header
            return None

        return None

    # ==================== Testing ====================

    async def test_webhook(
        self,
        webhook_id: UUID,
        request: WebhookTestRequest
    ) -> WebhookTestResponse:
        """Testa entrega de webhook."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        # Prepara payload de teste
        test_payload = request.payload or {
            "test": True,
            "message": "Teste de webhook do ERP Conecta Mais"
        }

        start_time = datetime.utcnow()

        try:
            # Prepara request
            full_payload = self._prepare_payload(
                webhook, request.event, test_payload
            )
            payload_str = json.dumps(full_payload)
            headers = self._prepare_headers(webhook, payload_str)
            auth = self._prepare_auth(webhook)

            # Faz requisição
            client = await self._get_http_client()
            response = await client.request(
                method=webhook.method,
                url=webhook.url,
                content=payload_str,
                headers=headers,
                auth=auth
            )

            response_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            return WebhookTestResponse(
                success=200 <= response.status_code < 300,
                status_code=response.status_code,
                response_time_ms=response_time,
                response_body=response.text[:1000] if response.text else None,
                error=None
            )

        except httpx.TimeoutException:
            return WebhookTestResponse(
                success=False,
                response_time_ms=webhook.timeout_seconds * 1000,
                error="Timeout ao conectar"
            )

        except httpx.RequestError as e:
            response_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
            return WebhookTestResponse(
                success=False,
                response_time_ms=response_time,
                error=str(e)
            )

    # ==================== Maintenance ====================

    async def check_failing_webhooks(self) -> List[WebhookConfig]:
        """Verifica webhooks com muitas falhas."""
        return await self.repository.get_failing_webhooks(min_failures=5)

    async def auto_disable_failing_webhooks(
        self,
        min_failures: int = 10
    ) -> int:
        """Desativa automaticamente webhooks com muitas falhas."""
        failing = await self.repository.get_failing_webhooks(
            min_failures=min_failures
        )

        count = 0
        for webhook in failing:
            if webhook.status != WebhookStatus.DISABLED:
                webhook.status = WebhookStatus.FAILING
                await self.repository.update_webhook(webhook)

                log = IntegrationLog(
                    webhook_id=webhook.id,
                    log_type=LogType.SYSTEM,
                    level=LogLevel.WARNING,
                    status=LogStatus.SUCCESS,
                    action="webhook_auto_disabled",
                    metadata={"consecutive_failures": webhook.consecutive_failures}
                )
                await self.repository.create_log(log)
                count += 1

        logger.info(f"Desativados {count} webhooks por falhas consecutivas")
        return count

    async def get_webhook_stats(
        self,
        webhook_id: UUID
    ) -> Dict[str, Any]:
        """Obtém estatísticas de um webhook."""
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            raise ValueError("Webhook não encontrado")

        return {
            "id": str(webhook.id),
            "name": webhook.name,
            "status": webhook.status.value,
            "health": webhook.health_status,
            "total_deliveries": webhook.total_deliveries,
            "successful_deliveries": webhook.successful_deliveries,
            "failed_deliveries": webhook.failed_deliveries,
            "consecutive_failures": webhook.consecutive_failures,
            "delivery_rate": webhook.delivery_rate,
            "avg_response_time_ms": webhook.avg_response_time_ms,
            "last_delivery_at": (
                webhook.last_delivery_at.isoformat()
                if webhook.last_delivery_at else None
            ),
            "last_success_at": (
                webhook.last_success_at.isoformat()
                if webhook.last_success_at else None
            ),
            "last_failure_at": (
                webhook.last_failure_at.isoformat()
                if webhook.last_failure_at else None
            ),
            "last_failure_reason": webhook.last_failure_reason
        }
