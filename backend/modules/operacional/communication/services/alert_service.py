"""
Service para Alertas em Tempo Real.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

import asyncio
import logging
from typing import Callable, Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.communication.models.alert import (
    Alert,
    AlertSeverity,
    AlertType,
)
from modules.operacional.communication.repositories.communication_repository import (
    AlertRepository,
)
from modules.operacional.communication.schemas.communication_schemas import (
    AlertCreate,
    AlertFilter,
    AlertResponse,
)

logger = logging.getLogger(__name__)


class AlertServiceError(Exception):
    """Excecao base para erros do AlertService."""

    pass


class AlertNotFoundError(AlertServiceError):
    """Alerta nao encontrado."""

    pass


class AlertService:
    """
    Service para gerenciamento de Alertas em Tempo Real.

    Fornece logica de negocio para criar, disparar e gerenciar alertas,
    incluindo broadcast via WebSocket e notificacoes.

    Attributes:
        db: Sessao assincrona do banco de dados
        repository: Repository de alertas
        broadcast_handlers: Handlers para broadcast

    Example:
        >>> service = AlertService(db)
        >>> alert = await service.create_and_broadcast(data, tenant_id)
        >>> await service.acknowledge(alert.id, user_id, tenant_id)
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o service.

        Args:
            db: Sessao assincrona do banco de dados
        """
        self.db = db
        self.repository = AlertRepository(db)
        self._broadcast_handlers: List[Callable] = []

    def register_broadcast_handler(
        self,
        handler: Callable[[Alert, str], asyncio.coroutine],
    ) -> None:
        """
        Registra handler para broadcast de alertas.

        Args:
            handler: Funcao async que recebe (Alert, tenant_id)
        """
        self._broadcast_handlers.append(handler)
        logger.debug(f"Handler de broadcast registrado: {handler.__name__}")

    async def create_alert(
        self,
        data: AlertCreate,
        tenant_id: str,
    ) -> Alert:
        """
        Cria um novo alerta.

        Args:
            data: Dados do alerta
            tenant_id: ID do tenant

        Returns:
            Alerta criado

        Raises:
            AlertServiceError: Se ocorrer erro na criacao
        """
        try:
            alert = await self.repository.create(data, tenant_id)
            logger.info(f"Alerta criado: {alert.id} [{alert.severity}]")
            return alert
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
            raise AlertServiceError(f"Erro ao criar alerta: {e}") from e

    async def create_and_broadcast(
        self,
        data: AlertCreate,
        tenant_id: str,
    ) -> Alert:
        """
        Cria alerta e faz broadcast via WebSocket.

        Args:
            data: Dados do alerta
            tenant_id: ID do tenant

        Returns:
            Alerta criado e transmitido

        Raises:
            AlertServiceError: Se ocorrer erro
        """
        # Cria o alerta
        alert = await self.create_alert(data, tenant_id)

        # Faz broadcast
        await self._broadcast_alert(alert, tenant_id)

        # Envia notificacao se for critico
        if alert.is_critical:
            await self._send_critical_notification(alert, tenant_id)

        return alert

    async def _broadcast_alert(
        self,
        alert: Alert,
        tenant_id: str,
    ) -> None:
        """
        Faz broadcast do alerta para handlers registrados.

        Args:
            alert: Alerta a ser transmitido
            tenant_id: ID do tenant
        """
        for handler in self._broadcast_handlers:
            try:
                await handler(alert, tenant_id)
            except Exception as e:
                logger.error(f"Erro no handler de broadcast: {e}")

    async def _send_critical_notification(
        self,
        alert: Alert,
        tenant_id: str,
    ) -> None:
        """
        Envia notificacao para alertas criticos.

        Args:
            alert: Alerta critico
            tenant_id: ID do tenant
        """
        try:
            from .notification_service import NotificationService
            from modules.operacional.communication.models.notification import (
                NotificationType,
                NotificationChannel,
            )
            from modules.operacional.communication.schemas.communication_schemas import (
                NotificationCreate,
            )

            notification_service = NotificationService(self.db)

            # Envia para usuarios destinatarios
            for user_id in (alert.target_users or []):
                data = NotificationCreate(
                    user_id=user_id,
                    title=f"ALERTA CRITICO: {alert.title}",
                    body=alert.message[:200],  # Trunca mensagem
                    type=NotificationType.ALERTA,
                    channels=[
                        NotificationChannel.IN_APP,
                        NotificationChannel.PUSH,
                    ],
                    reference_type="alert",
                    reference_id=alert.id,
                    extra_data={
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                    },
                )
                await notification_service.send(data, tenant_id, skip_rate_limit=True)

            logger.info(
                f"Notificacoes criticas enviadas para alerta {alert.id}"
            )

        except Exception as e:
            logger.error(f"Erro ao enviar notificacao critica: {e}")

    async def get_by_id(
        self,
        alert_id: str,
        tenant_id: str,
    ) -> Alert:
        """
        Busca alerta por ID.

        Args:
            alert_id: ID do alerta
            tenant_id: ID do tenant

        Returns:
            Alerta encontrado

        Raises:
            AlertNotFoundError: Se nao encontrado
        """
        alert = await self.repository.get_by_id(alert_id, tenant_id)
        if not alert:
            raise AlertNotFoundError(f"Alerta nao encontrado: {alert_id}")
        return alert

    async def get_active_alerts(
        self,
        tenant_id: str,
        filters: Optional[AlertFilter] = None,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
    ) -> List[Alert]:
        """
        Lista alertas ativos.

        Args:
            tenant_id: ID do tenant
            filters: Filtros de busca
            user_id: ID do usuario (para filtrar por destinatario)
            user_roles: Roles do usuario

        Returns:
            Lista de alertas ativos
        """
        return await self.repository.list_active(
            tenant_id, filters, user_id, user_roles
        )

    async def acknowledge(
        self,
        alert_id: str,
        user_id: str,
        tenant_id: str,
    ) -> Alert:
        """
        Confirma recebimento de alerta.

        Args:
            alert_id: ID do alerta
            user_id: ID do usuario
            tenant_id: ID do tenant

        Returns:
            Alerta atualizado

        Raises:
            AlertNotFoundError: Se nao encontrado
        """
        alert = await self.repository.acknowledge(alert_id, user_id, tenant_id)
        if not alert:
            raise AlertNotFoundError(f"Alerta nao encontrado: {alert_id}")

        logger.info(f"Alerta confirmado: {alert_id} por {user_id}")

        # Notifica sobre a confirmacao via broadcast
        await self._broadcast_acknowledgment(alert, user_id, tenant_id)

        return alert

    async def _broadcast_acknowledgment(
        self,
        alert: Alert,
        user_id: str,
        tenant_id: str,
    ) -> None:
        """
        Faz broadcast de confirmacao de alerta.

        Args:
            alert: Alerta confirmado
            user_id: ID do usuario que confirmou
            tenant_id: ID do tenant
        """
        # Notifica outros usuarios sobre a confirmacao
        # Implementar quando necessario
        pass

    async def deactivate(
        self,
        alert_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Desativa um alerta.

        Args:
            alert_id: ID do alerta
            tenant_id: ID do tenant

        Returns:
            True se desativado

        Raises:
            AlertNotFoundError: Se nao encontrado
        """
        deactivated = await self.repository.deactivate(alert_id, tenant_id)
        if not deactivated:
            raise AlertNotFoundError(f"Alerta nao encontrado: {alert_id}")
        return True

    async def process_expired(self) -> int:
        """
        Processa alertas expirados.

        Returns:
            Quantidade de alertas desativados
        """
        count = await self.repository.process_expired()
        if count > 0:
            logger.info(f"Alertas expirados processados: {count}")
        return count

    # ==========================================================================
    # FACTORY METHODS PARA TIPOS COMUNS DE ALERTA
    # ==========================================================================

    async def create_occurrence_alert(
        self,
        tenant_id: str,
        occurrence_id: str,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        target_roles: Optional[List[str]] = None,
    ) -> Alert:
        """
        Cria alerta de ocorrencia.

        Args:
            tenant_id: ID do tenant
            occurrence_id: ID da ocorrencia
            title: Titulo do alerta
            message: Mensagem detalhada
            severity: Severidade
            target_roles: Roles destinatarias

        Returns:
            Alerta criado e transmitido
        """
        data = AlertCreate(
            alert_type=AlertType.OCORRENCIA_CRITICA,
            severity=severity,
            title=title,
            message=message,
            reference_type="occurrence",
            reference_id=occurrence_id,
            target_roles=target_roles or ["supervisor", "gerente"],
        )
        return await self.create_and_broadcast(data, tenant_id)

    async def create_sla_alert(
        self,
        tenant_id: str,
        reference_type: str,
        reference_id: str,
        sla_name: str,
        time_remaining_minutes: int,
        target_users: Optional[List[str]] = None,
    ) -> Alert:
        """
        Cria alerta de SLA prestes a vencer.

        Args:
            tenant_id: ID do tenant
            reference_type: Tipo da entidade
            reference_id: ID da entidade
            sla_name: Nome do SLA
            time_remaining_minutes: Minutos restantes
            target_users: Usuarios destinatarios

        Returns:
            Alerta criado e transmitido
        """
        severity = AlertSeverity.WARNING
        if time_remaining_minutes <= 15:
            severity = AlertSeverity.CRITICAL
        elif time_remaining_minutes <= 30:
            severity = AlertSeverity.ERROR

        data = AlertCreate(
            alert_type=AlertType.SLA_VENCENDO,
            severity=severity,
            title=f"SLA Vencendo: {sla_name}",
            message=f"O SLA '{sla_name}' vence em {time_remaining_minutes} minutos.",
            reference_type=reference_type,
            reference_id=reference_id,
            target_users=target_users,
            expires_in_minutes=time_remaining_minutes + 5,
        )
        return await self.create_and_broadcast(data, tenant_id)

    async def create_uncovered_post_alert(
        self,
        tenant_id: str,
        post_id: str,
        post_name: str,
        start_time: str,
        target_roles: Optional[List[str]] = None,
    ) -> Alert:
        """
        Cria alerta de posto descoberto.

        Args:
            tenant_id: ID do tenant
            post_id: ID do posto
            post_name: Nome do posto
            start_time: Hora de inicio do turno
            target_roles: Roles destinatarias

        Returns:
            Alerta criado e transmitido
        """
        data = AlertCreate(
            alert_type=AlertType.POSTO_DESCOBERTO,
            severity=AlertSeverity.CRITICAL,
            title=f"Posto Descoberto: {post_name}",
            message=f"O posto '{post_name}' esta sem cobertura a partir de {start_time}.",
            reference_type="post",
            reference_id=post_id,
            target_roles=target_roles or ["supervisor", "coordenador", "gerente"],
            expires_in_minutes=60,
        )
        return await self.create_and_broadcast(data, tenant_id)

    async def create_absence_alert(
        self,
        tenant_id: str,
        employee_id: str,
        employee_name: str,
        post_name: str,
        target_roles: Optional[List[str]] = None,
    ) -> Alert:
        """
        Cria alerta de falta detectada.

        Args:
            tenant_id: ID do tenant
            employee_id: ID do funcionario
            employee_name: Nome do funcionario
            post_name: Nome do posto
            target_roles: Roles destinatarias

        Returns:
            Alerta criado e transmitido
        """
        data = AlertCreate(
            alert_type=AlertType.FALTA_DETECTADA,
            severity=AlertSeverity.ERROR,
            title=f"Falta Detectada: {employee_name}",
            message=f"O funcionario '{employee_name}' nao compareceu ao posto '{post_name}'.",
            reference_type="employee",
            reference_id=employee_id,
            target_roles=target_roles or ["supervisor", "rh"],
            expires_in_minutes=120,
        )
        return await self.create_and_broadcast(data, tenant_id)

    async def create_urgent_substitution_alert(
        self,
        tenant_id: str,
        substitution_id: str,
        post_name: str,
        start_time: str,
        target_users: Optional[List[str]] = None,
        target_roles: Optional[List[str]] = None,
    ) -> Alert:
        """
        Cria alerta de substituicao urgente.

        Args:
            tenant_id: ID do tenant
            substitution_id: ID da substituicao
            post_name: Nome do posto
            start_time: Hora de inicio
            target_users: Usuarios destinatarios
            target_roles: Roles destinatarias

        Returns:
            Alerta criado e transmitido
        """
        data = AlertCreate(
            alert_type=AlertType.SUBSTITUICAO_URGENTE,
            severity=AlertSeverity.CRITICAL,
            title=f"Substituicao Urgente: {post_name}",
            message=f"Substituicao urgente necessaria para '{post_name}' as {start_time}.",
            reference_type="substitution",
            reference_id=substitution_id,
            target_users=target_users or [],
            target_roles=target_roles or ["supervisor", "funcionario_reserva"],
            expires_in_minutes=30,
        )
        return await self.create_and_broadcast(data, tenant_id)

    async def create_panic_alert(
        self,
        tenant_id: str,
        user_id: str,
        user_name: str,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Alert:
        """
        Cria alerta de panico acionado.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            user_name: Nome do usuario
            location: Descricao do local
            latitude: Latitude GPS
            longitude: Longitude GPS

        Returns:
            Alerta criado e transmitido
        """
        location_info = location or "Localizacao desconhecida"
        if latitude and longitude:
            location_info += f" (GPS: {latitude}, {longitude})"

        data = AlertCreate(
            alert_type=AlertType.PANICO_ACIONADO,
            severity=AlertSeverity.CRITICAL,
            title=f"PANICO: {user_name}",
            message=f"Botao de panico acionado por '{user_name}' em {location_info}.",
            reference_type="user",
            reference_id=user_id,
            target_roles=["supervisor", "seguranca", "central_monitoramento"],
            expires_in_minutes=60,
        )
        return await self.create_and_broadcast(data, tenant_id)
