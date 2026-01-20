"""
Service para Notificacoes Operacionais.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.communication.models.notification import (
    Notification,
    NotificationChannel,
    NotificationType,
)
from modules.operacional.communication.repositories.communication_repository import (
    NotificationRepository,
)
from modules.operacional.communication.schemas.communication_schemas import (
    NotificationCreate,
    NotificationFilter,
    NotificationUnreadCount,
)

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    """Excecao base para erros do NotificationService."""

    pass


class NotificationNotFoundError(NotificationServiceError):
    """Notificacao nao encontrada."""

    pass


class NotificationRateLimitError(NotificationServiceError):
    """Rate limit excedido para notificacoes."""

    pass


class NotificationService:
    """
    Service para gerenciamento de Notificacoes.

    Fornece logica de negocio para criar, enviar e gerenciar notificacoes,
    incluindo rate limiting e envio por multiplos canais.

    Attributes:
        db: Sessao assincrona do banco de dados
        repository: Repository de notificacoes
        rate_limits: Configuracao de rate limiting

    Example:
        >>> service = NotificationService(db)
        >>> notification = await service.send(data, tenant_id)
        >>> await service.mark_as_read(notification.id, user_id)
    """

    # Rate limits por tipo de notificacao (por minuto)
    DEFAULT_RATE_LIMITS: Dict[str, int] = {
        NotificationType.OCORRENCIA.value: 10,
        NotificationType.ALERTA.value: 20,
        NotificationType.COMUNICADO.value: 5,
        NotificationType.SISTEMA.value: 30,
    }

    def __init__(
        self,
        db: AsyncSession,
        rate_limits: Optional[Dict[str, int]] = None,
    ) -> None:
        """
        Inicializa o service.

        Args:
            db: Sessao assincrona do banco de dados
            rate_limits: Rate limits customizados por tipo
        """
        self.db = db
        self.repository = NotificationRepository(db)
        self.rate_limits = rate_limits or self.DEFAULT_RATE_LIMITS
        self._rate_cache: Dict[str, List[datetime]] = {}

    async def send(
        self,
        data: NotificationCreate,
        tenant_id: str,
        skip_rate_limit: bool = False,
    ) -> Notification:
        """
        Envia uma notificacao.

        Args:
            data: Dados da notificacao
            tenant_id: ID do tenant
            skip_rate_limit: Se deve ignorar rate limit

        Returns:
            Notificacao enviada

        Raises:
            NotificationRateLimitError: Se rate limit excedido
            NotificationServiceError: Se ocorrer erro no envio
        """
        try:
            # Verifica rate limit
            if not skip_rate_limit:
                await self._check_rate_limit(data.user_id, data.type.value)

            # Cria notificacao
            notification = await self.repository.create(data, tenant_id)

            # Envia por canais configurados
            await self._send_to_channels(notification)

            # Marca como enviada
            notification.mark_as_sent()
            await self.db.commit()

            logger.info(
                f"Notificacao enviada: {notification.id} para {data.user_id}"
            )
            return notification

        except NotificationRateLimitError:
            raise
        except Exception as e:
            logger.error(f"Erro ao enviar notificacao: {e}")
            raise NotificationServiceError(f"Erro ao enviar notificacao: {e}") from e

    async def send_bulk(
        self,
        notifications: List[NotificationCreate],
        tenant_id: str,
        batch_size: int = 50,
    ) -> List[Notification]:
        """
        Envia multiplas notificacoes em lote.

        Args:
            notifications: Lista de dados de notificacao
            tenant_id: ID do tenant
            batch_size: Tamanho do lote

        Returns:
            Lista de notificacoes enviadas
        """
        results: List[Notification] = []

        # Processa em lotes
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]

            # Cria todas do lote
            created = await self.repository.create_bulk(batch, tenant_id)

            # Envia por canais
            for notification in created:
                try:
                    await self._send_to_channels(notification)
                    notification.mark_as_sent()
                except Exception as e:
                    logger.error(f"Erro ao enviar notificacao {notification.id}: {e}")

            await self.db.commit()
            results.extend(created)

            # Pequena pausa entre lotes
            if i + batch_size < len(notifications):
                await asyncio.sleep(0.1)

        logger.info(f"Notificacoes enviadas em massa: {len(results)}")
        return results

    async def _check_rate_limit(
        self,
        user_id: str,
        notification_type: str,
    ) -> None:
        """
        Verifica rate limit para usuario/tipo.

        Args:
            user_id: ID do usuario
            notification_type: Tipo da notificacao

        Raises:
            NotificationRateLimitError: Se limite excedido
        """
        from datetime import timedelta

        key = f"{user_id}:{notification_type}"
        limit = self.rate_limits.get(notification_type, 10)
        now = datetime.utcnow()
        window = timedelta(minutes=1)

        # Limpa entradas antigas
        if key in self._rate_cache:
            self._rate_cache[key] = [
                ts for ts in self._rate_cache[key]
                if now - ts < window
            ]
        else:
            self._rate_cache[key] = []

        # Verifica limite
        if len(self._rate_cache[key]) >= limit:
            logger.warning(
                f"Rate limit excedido para {user_id} tipo {notification_type}"
            )
            raise NotificationRateLimitError(
                f"Limite de {limit} notificacoes por minuto excedido"
            )

        # Registra
        self._rate_cache[key].append(now)

    async def _send_to_channels(self, notification: Notification) -> None:
        """
        Envia notificacao pelos canais configurados.

        Args:
            notification: Notificacao a ser enviada
        """
        from .push_provider import PushProviderFactory

        for channel in notification.channels:
            try:
                if channel == NotificationChannel.PUSH.value:
                    provider = PushProviderFactory.get_provider("firebase")
                    if provider:
                        await provider.send_push(
                            user_id=notification.user_id,
                            title=notification.title,
                            body=notification.body,
                            data={
                                "notification_id": notification.id,
                                "type": notification.type,
                                "action_url": notification.action_url,
                            },
                        )

                elif channel == NotificationChannel.EMAIL.value:
                    # TODO: Integrar com servico de email
                    logger.debug(
                        f"Email para {notification.user_id}: {notification.title}"
                    )

                elif channel == NotificationChannel.SMS.value:
                    # TODO: Integrar com provedor de SMS
                    logger.debug(
                        f"SMS para {notification.user_id}: {notification.body}"
                    )

                elif channel == NotificationChannel.WHATSAPP.value:
                    # TODO: Integrar com WhatsApp Business API
                    logger.debug(
                        f"WhatsApp para {notification.user_id}: {notification.body}"
                    )

            except Exception as e:
                logger.error(
                    f"Erro ao enviar por canal {channel}: {e}"
                )

    async def get_by_id(
        self,
        notification_id: str,
        user_id: str,
    ) -> Notification:
        """
        Busca notificacao por ID.

        Args:
            notification_id: ID da notificacao
            user_id: ID do usuario

        Returns:
            Notificacao encontrada

        Raises:
            NotificationNotFoundError: Se nao encontrada
        """
        notification = await self.repository.get_by_id(
            notification_id, user_id=user_id
        )
        if not notification:
            raise NotificationNotFoundError(
                f"Notificacao nao encontrada: {notification_id}"
            )
        return notification

    async def list_for_user(
        self,
        tenant_id: str,
        user_id: str,
        filters: Optional[NotificationFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Notification], int]:
        """
        Lista notificacoes de um usuario.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            filters: Filtros de busca
            page: Pagina atual
            page_size: Itens por pagina

        Returns:
            Tupla (notificacoes, total)
        """
        return await self.repository.list_for_user(
            tenant_id, user_id, filters, page, page_size
        )

    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
    ) -> Notification:
        """
        Marca notificacao como lida.

        Args:
            notification_id: ID da notificacao
            user_id: ID do usuario

        Returns:
            Notificacao atualizada

        Raises:
            NotificationNotFoundError: Se nao encontrada
        """
        notification = await self.repository.mark_as_read(notification_id, user_id)
        if not notification:
            raise NotificationNotFoundError(
                f"Notificacao nao encontrada: {notification_id}"
            )
        return notification

    async def mark_all_as_read(
        self,
        tenant_id: str,
        user_id: str,
        notification_ids: Optional[List[str]] = None,
    ) -> int:
        """
        Marca todas notificacoes como lidas.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            notification_ids: IDs especificos (opcional)

        Returns:
            Quantidade de notificacoes atualizadas
        """
        return await self.repository.mark_all_as_read(
            tenant_id, user_id, notification_ids
        )

    async def get_unread_count(
        self,
        tenant_id: str,
        user_id: str,
    ) -> NotificationUnreadCount:
        """
        Obtem contagem de notificacoes nao lidas.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario

        Returns:
            Contagem total e por tipo
        """
        stats = await self.repository.get_unread_count(tenant_id, user_id)
        return NotificationUnreadCount(
            total=stats["total"],
            by_type=stats["by_type"],
        )

    async def delete(
        self,
        notification_id: str,
        user_id: str,
    ) -> bool:
        """
        Remove uma notificacao.

        Args:
            notification_id: ID da notificacao
            user_id: ID do usuario

        Returns:
            True se removida

        Raises:
            NotificationNotFoundError: Se nao encontrada
        """
        deleted = await self.repository.delete(notification_id, user_id)
        if not deleted:
            raise NotificationNotFoundError(
                f"Notificacao nao encontrada: {notification_id}"
            )
        return True

    async def cleanup_old(
        self,
        tenant_id: str,
        days: int = 30,
    ) -> int:
        """
        Remove notificacoes antigas.

        Args:
            tenant_id: ID do tenant
            days: Dias de retencao

        Returns:
            Quantidade removida
        """
        count = await self.repository.cleanup_old(tenant_id, days)
        logger.info(f"Notificacoes antigas removidas: {count}")
        return count

    async def send_occurrence_notification(
        self,
        tenant_id: str,
        user_ids: List[str],
        occurrence_id: str,
        occurrence_title: str,
        severity: str,
    ) -> List[Notification]:
        """
        Envia notificacao de ocorrencia.

        Args:
            tenant_id: ID do tenant
            user_ids: Lista de usuarios destinatarios
            occurrence_id: ID da ocorrencia
            occurrence_title: Titulo da ocorrencia
            severity: Severidade da ocorrencia

        Returns:
            Lista de notificacoes enviadas
        """
        channels = [NotificationChannel.IN_APP]
        if severity in ("alta", "critica"):
            channels.append(NotificationChannel.PUSH)

        notifications = [
            NotificationCreate(
                user_id=user_id,
                title=f"Nova Ocorrencia: {occurrence_title}",
                body=f"Uma ocorrencia de severidade {severity} foi registrada.",
                type=NotificationType.OCORRENCIA,
                channels=channels,
                reference_type="occurrence",
                reference_id=occurrence_id,
                action_url=f"/ocorrencias/{occurrence_id}",
            )
            for user_id in user_ids
        ]

        return await self.send_bulk(notifications, tenant_id)

    async def send_scale_notification(
        self,
        tenant_id: str,
        user_id: str,
        scale_id: str,
        message: str,
    ) -> Notification:
        """
        Envia notificacao de escala.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            scale_id: ID da escala
            message: Mensagem da notificacao

        Returns:
            Notificacao enviada
        """
        data = NotificationCreate(
            user_id=user_id,
            title="Alteracao na Escala",
            body=message,
            type=NotificationType.ESCALA,
            channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH],
            reference_type="scale",
            reference_id=scale_id,
            action_url=f"/escalas/{scale_id}",
        )

        return await self.send(data, tenant_id)

    async def send_substitution_notification(
        self,
        tenant_id: str,
        user_id: str,
        substitution_id: str,
        message: str,
        is_urgent: bool = False,
    ) -> Notification:
        """
        Envia notificacao de substituicao.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            substitution_id: ID da substituicao
            message: Mensagem da notificacao
            is_urgent: Se e substituicao urgente

        Returns:
            Notificacao enviada
        """
        channels = [NotificationChannel.IN_APP, NotificationChannel.PUSH]
        if is_urgent:
            channels.append(NotificationChannel.SMS)

        data = NotificationCreate(
            user_id=user_id,
            title="Solicitacao de Substituicao" + (" URGENTE" if is_urgent else ""),
            body=message,
            type=NotificationType.SUBSTITUICAO,
            channels=channels,
            reference_type="substitution",
            reference_id=substitution_id,
            action_url=f"/substituicoes/{substitution_id}",
            extra_data={"urgent": is_urgent},
        )

        return await self.send(data, tenant_id, skip_rate_limit=is_urgent)
