"""
Handler de Webhooks Sólides.
Sprint 33: Integration Framework

Processa eventos de webhook recebidos do Sólides.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, Awaitable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.connectors.solides.connector import SolidesConnector
from modules.integrations.connectors.solides.models import (
    SolidesWebhookLog,
    SolidesIntegrationConfig,
    SyncSource,
    log_webhook,
    log_webhook_async,
)
from modules.integrations.connectors.solides.schemas import (
    SolidesWebhookEvent,
    SolidesWebhookEventType,
)

logger = logging.getLogger(__name__)


class SolidesWebhookHandler:
    """
    Handler para processar webhooks do Sólides.

    Eventos suportados:
    - novo_colaborador: Novo colaborador cadastrado
    - edicao_colaborador: Colaborador atualizado
    - demissao_colaborador: Colaborador demitido
    - nova_ocorrencia: Nova ocorrência registrada
    - novo_absenteismo: Novo absenteísmo registrado
    - nova_resposta_pesquisa: Resposta em pesquisa
    - novo_curriculo: Novo currículo recebido
    - nova_inscricao: Nova inscrição em vaga
    - mudanca_etapa: Mudança de etapa em processo seletivo
    """

    # Mapeamento de eventos para handlers
    EVENT_HANDLERS = {
        "novo_colaborador": "_handle_new_employee",
        "edicao_colaborador": "_handle_employee_update",
        "demissao_colaborador": "_handle_employee_termination",
        "nova_ocorrencia": "_handle_new_occurrence",
        "novo_absenteismo": "_handle_new_absence",
        "nova_resposta_pesquisa": "_handle_survey_response",
        "novo_curriculo": "_handle_new_resume",
        "nova_inscricao": "_handle_new_application",
        "mudanca_etapa": "_handle_stage_change",
    }

    def __init__(
        self,
        db: AsyncSession,
        redis_client=None,
        async_processing: bool = True
    ):
        """
        Inicializa o handler.

        Args:
            db: Sessão do banco de dados (AsyncSession)
            redis_client: Cliente Redis para fila de processamento
            async_processing: Se True, processa assincronamente via fila
        """
        self.db = db
        self.redis = redis_client
        self.async_processing = async_processing and redis_client is not None

    async def handle_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        raw_body: bytes,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processa webhook recebido.

        Args:
            event_type: Tipo do evento
            payload: Dados do evento
            headers: Headers da requisição
            raw_body: Body raw para validação
            request_id: ID da requisição
            ip_address: IP de origem

        Returns:
            Dict com status do processamento
        """
        # Extrair condominio_id do payload
        empresa_id = payload.get("empresa_id")
        condominio_id = await self._get_condominio_from_empresa(empresa_id)

        # Log do webhook recebido
        webhook_log = await log_webhook_async(
            self.db,
            event_type=event_type,
            payload=payload,
            condominio_id=condominio_id,
            headers=dict(headers),
            request_id=request_id,
            ip_address=ip_address
        )

        logger.info(
            f"[Solides Webhook] Recebido evento '{event_type}' "
            f"(id={webhook_log.id}, empresa={empresa_id})"
        )

        # Validar assinatura se configurado
        if condominio_id:
            config = await self._get_config(condominio_id)
            if config and config.webhook_secret:
                connector = SolidesConnector(
                    credentials={"webhook_secret": config.webhook_secret}
                )
                if not await connector.validate_webhook(headers, raw_body):
                    webhook_log.status = "invalid_signature"
                    webhook_log.error = "Assinatura inválida"
                    await self.db.commit()

                    logger.warning(f"[Solides Webhook] Assinatura inválida para {webhook_log.id}")
                    return {"status": "error", "message": "Invalid signature"}

        # Processar evento
        if self.async_processing:
            # Enfileirar para processamento assíncrono
            await self._enqueue_for_processing(webhook_log.id)
            return {"status": "queued", "webhook_id": str(webhook_log.id)}
        else:
            # Processar sincronamente
            result = await self._process_event(webhook_log)
            return {"status": result, "webhook_id": str(webhook_log.id)}

    async def _process_event(
        self,
        webhook_log: SolidesWebhookLog
    ) -> str:
        """
        Processa evento de webhook.

        Args:
            webhook_log: Log do webhook

        Returns:
            Status do processamento
        """
        try:
            webhook_log.status = "processing"
            await self.db.commit()

            event_type = webhook_log.event_type
            payload = webhook_log.payload

            # Encontrar handler
            handler_name = self.EVENT_HANDLERS.get(event_type)
            if not handler_name:
                logger.warning(f"[Solides Webhook] Evento não suportado: {event_type}")
                webhook_log.status = "unsupported"
                await self.db.commit()
                return "unsupported"

            handler = getattr(self, handler_name, None)
            if not handler:
                logger.error(f"[Solides Webhook] Handler não encontrado: {handler_name}")
                webhook_log.status = "error"
                webhook_log.error = f"Handler não implementado: {handler_name}"
                await self.db.commit()
                return "error"

            # Executar handler
            await handler(webhook_log.condominio_id, payload)

            webhook_log.status = "processed"
            webhook_log.processed_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"[Solides Webhook] Evento {event_type} processado com sucesso")
            return "processed"

        except Exception as e:
            logger.error(f"[Solides Webhook] Erro processando evento: {e}")
            webhook_log.status = "failed"
            webhook_log.error = str(e)
            webhook_log.retry_count += 1
            await self.db.commit()
            return "failed"

    async def _enqueue_for_processing(self, webhook_id: UUID) -> None:
        """
        Enfileira webhook para processamento assíncrono.

        Args:
            webhook_id: ID do webhook
        """
        if self.redis:
            await self.redis.lpush(
                "solides:webhooks:queue",
                str(webhook_id)
            )
            logger.debug(f"[Solides Webhook] Enfileirado {webhook_id}")

    async def _get_condominio_from_empresa(
        self,
        empresa_id: Optional[int]
    ) -> Optional[UUID]:
        """
        Mapeia empresa_id do Sólides para condominio_id.

        Args:
            empresa_id: ID da empresa no Sólides

        Returns:
            UUID do condomínio ou None
        """
        if not empresa_id:
            return None

        # Buscar mapeamento
        stmt = select(SolidesIntegrationConfig).where(
            SolidesIntegrationConfig.extra_config['empresa_id'].astext == str(empresa_id)
        )
        result = await self.db.execute(stmt)
        config = result.scalar_one_or_none()

        return config.condominio_id if config else None

    async def _get_config(
        self,
        condominio_id: UUID
    ) -> Optional[SolidesIntegrationConfig]:
        """
        Obtém configuração da integração.
        """
        stmt = select(SolidesIntegrationConfig).where(
            SolidesIntegrationConfig.condominio_id == condominio_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ==================== HANDLERS DE EVENTOS ====================

    async def _handle_new_employee(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de novo colaborador.
        """
        if not condominio_id:
            logger.warning("[Solides Webhook] Condomínio não identificado para novo colaborador")
            return

        colaborador_data = payload.get("data", payload)
        solides_id = str(colaborador_data.get("id"))

        logger.info(f"[Solides Webhook] Processando novo colaborador {solides_id}")
        # Sincronização será implementada via integration_service

    async def _handle_employee_update(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de atualização de colaborador.
        """
        if not condominio_id:
            return

        colaborador_data = payload.get("data", payload)
        solides_id = str(colaborador_data.get("id"))

        logger.info(f"[Solides Webhook] Processando atualização colaborador {solides_id}")

    async def _handle_employee_termination(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de demissão de colaborador.
        """
        if not condominio_id:
            return

        colaborador_data = payload.get("data", payload)
        solides_id = str(colaborador_data.get("id"))

        logger.info(f"[Solides Webhook] Processando demissão colaborador {solides_id}")

    async def _handle_new_occurrence(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de nova ocorrência.
        """
        if not condominio_id:
            return

        ocorrencia_data = payload.get("data", payload)
        solides_id = str(ocorrencia_data.get("id"))

        logger.info(f"[Solides Webhook] Processando nova ocorrência {solides_id}")

    async def _handle_new_absence(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de novo absenteísmo.
        """
        if not condominio_id:
            return

        absenteismo_data = payload.get("data", payload)
        solides_id = str(absenteismo_data.get("id"))

        logger.info(f"[Solides Webhook] Processando novo absenteísmo {solides_id}")

    async def _handle_survey_response(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de resposta em pesquisa.
        """
        logger.info("[Solides Webhook] Resposta de pesquisa recebida (não processado)")

    async def _handle_new_resume(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de novo currículo.
        """
        if not condominio_id:
            return

        candidato_data = payload.get("data", payload)
        solides_id = str(candidato_data.get("id"))

        logger.info(f"[Solides Webhook] Processando novo currículo {solides_id}")

    async def _handle_new_application(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de nova inscrição em vaga.
        """
        if not condominio_id:
            return

        inscricao_data = payload.get("data", payload)
        solides_id = str(inscricao_data.get("id"))

        logger.info(f"[Solides Webhook] Processando nova inscrição {solides_id}")

    async def _handle_stage_change(
        self,
        condominio_id: Optional[UUID],
        payload: Dict[str, Any]
    ) -> None:
        """
        Processa evento de mudança de etapa em processo seletivo.
        """
        if not condominio_id:
            return

        inscricao_data = payload.get("data", payload)
        solides_id = str(inscricao_data.get("id"))

        logger.info(f"[Solides Webhook] Processando mudança de etapa {solides_id}")


# ==================== WORKER PARA FILA ====================

async def process_webhook_queue(
    db: AsyncSession,
    redis_client,
    batch_size: int = 10
) -> int:
    """
    Processa webhooks enfileirados.

    Args:
        db: Sessão do banco (AsyncSession)
        redis_client: Cliente Redis
        batch_size: Quantidade a processar por vez

    Returns:
        Quantidade processada
    """
    handler = SolidesWebhookHandler(db, async_processing=False)
    processed = 0

    for _ in range(batch_size):
        # Pegar da fila
        webhook_id_bytes = await redis_client.rpop("solides:webhooks:queue")
        if not webhook_id_bytes:
            break

        webhook_id = webhook_id_bytes.decode()

        # Buscar webhook
        stmt = select(SolidesWebhookLog).where(
            SolidesWebhookLog.id == webhook_id
        )
        result = await db.execute(stmt)
        webhook_log = result.scalar_one_or_none()

        if webhook_log:
            await handler._process_event(webhook_log)
            processed += 1

    return processed
