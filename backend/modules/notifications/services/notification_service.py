"""NotificationService - Serviço de Orquestração de Notificações.

Sprint 36 - Notification Hub.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from modules.notifications.models import (
    ChannelType,
    LogEventType,
    LogLevel,
    NotificationChannel,
    NotificationLog,
    NotificationPreference,
    NotificationQueue,
    NotificationTemplate,
    QueuePriority,
    QueueStatus,
    TemplateStatus,
)
from modules.notifications.schemas import (
    RecipientSchema,
    SendNotificationRequest,
    SendNotificationResponse,
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço de orquestração de notificações."""

    def __init__(self, db: Session, tenant_id: UUID):
        """Inicializa o serviço.

        Args:
            db: Sessão do banco de dados.
            tenant_id: ID do tenant.
        """
        self.db = db
        self.tenant_id = tenant_id

    def send_notification(
        self,
        request: SendNotificationRequest,
        created_by: Optional[UUID] = None,
    ) -> SendNotificationResponse:
        """Envia notificações para os destinatários.

        Args:
            request: Dados da requisição de envio.
            created_by: ID do usuário que está enviando.

        Returns:
            Resposta com status do envio.
        """
        notification_ids = []
        skipped_count = 0
        skipped_reasons: Dict[str, int] = {}

        # Gerar batch_id se não fornecido
        batch_id = request.batch_id or uuid.uuid4()

        # Buscar template se especificado
        template = None
        if request.template_id:
            template = self._get_template_by_id(request.template_id)
        elif request.template_slug:
            template = self._get_template_by_slug(request.template_slug)

        # Processar cada destinatário
        for recipient in request.recipients:
            try:
                result = self._process_recipient(
                    recipient=recipient,
                    request=request,
                    template=template,
                    batch_id=batch_id,
                    created_by=created_by,
                )

                if result["queued"]:
                    notification_ids.extend(result["notification_ids"])
                else:
                    skipped_count += 1
                    reason = result.get("skip_reason", "unknown")
                    skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1

            except Exception as e:
                logger.error(f"Erro ao processar destinatário: {e}")
                skipped_count += 1
                skipped_reasons["error"] = skipped_reasons.get("error", 0) + 1

        self.db.commit()

        return SendNotificationResponse(
            success=len(notification_ids) > 0,
            message=f"Enfileiradas {len(notification_ids)} notificações",
            notification_ids=notification_ids,
            batch_id=batch_id,
            queued_count=len(notification_ids),
            skipped_count=skipped_count,
            skipped_reasons=skipped_reasons,
        )

    def _process_recipient(
        self,
        recipient: RecipientSchema,
        request: SendNotificationRequest,
        template: Optional[NotificationTemplate],
        batch_id: UUID,
        created_by: Optional[UUID],
    ) -> Dict[str, Any]:
        """Processa um destinatário individual.

        Args:
            recipient: Dados do destinatário.
            request: Dados da requisição.
            template: Template a ser usado.
            batch_id: ID do batch.
            created_by: ID do criador.

        Returns:
            Dicionário com resultado do processamento.
        """
        notification_ids = []

        # Buscar preferências do usuário
        preferences = None
        if recipient.user_id and request.respect_preferences:
            preferences = self._get_user_preferences(recipient.user_id)

            # Verificar opt-out global
            if preferences and preferences.global_unsubscribe:
                return {"queued": False, "skip_reason": "global_unsubscribe"}

            # Verificar categoria
            if preferences and request.category:
                if not preferences.is_category_enabled(request.category):
                    return {"queued": False, "skip_reason": "category_disabled"}

        # Determinar canais a usar
        channels = self._determine_channels(
            recipient=recipient,
            request=request,
            preferences=preferences,
        )

        if not channels:
            return {"queued": False, "skip_reason": "no_channels"}

        # Criar item na fila para cada canal
        for channel_type, channel_config in channels:
            try:
                queue_item = self._create_queue_item(
                    recipient=recipient,
                    request=request,
                    template=template,
                    channel_type=channel_type,
                    channel_config=channel_config,
                    batch_id=batch_id,
                    created_by=created_by,
                )

                self.db.add(queue_item)
                notification_ids.append(queue_item.notification_id)

                # Log de criação
                self._log_event(
                    queue_item=queue_item,
                    event_type=LogEventType.CREATED,
                    message=f"Notificação criada para {channel_type.value}",
                )

            except Exception as e:
                logger.error(f"Erro ao criar item na fila: {e}")

        return {
            "queued": len(notification_ids) > 0,
            "notification_ids": notification_ids,
        }

    def _determine_channels(
        self,
        recipient: RecipientSchema,
        request: SendNotificationRequest,
        preferences: Optional[NotificationPreference],
    ) -> List[Tuple[ChannelType, Optional[NotificationChannel]]]:
        """Determina os canais a usar para o envio.

        Args:
            recipient: Dados do destinatário.
            request: Dados da requisição.
            preferences: Preferências do usuário.

        Returns:
            Lista de tuplas (tipo_canal, config_canal).
        """
        channels = []

        # Se especificou canal específico
        if request.channel_id:
            channel = self._get_channel_by_id(request.channel_id)
            if channel and channel.status.value == "active":
                return [(channel.channel_type, channel)]
            return []

        # Se especificou tipos de canal
        if request.channels:
            for channel_type in request.channels:
                # Verificar preferências
                if preferences and not preferences.is_channel_enabled(channel_type.value):
                    continue

                # Verificar endereço disponível
                address = self._get_recipient_address(recipient, channel_type)
                if not address:
                    continue

                # Buscar canal padrão para o tipo
                channel = self._get_default_channel(channel_type)
                channels.append((channel_type, channel))

            return channels

        # Usar canais das preferências do usuário ou defaults
        preferred = preferences.preferred_channels if preferences else ["email", "in_app"]

        for ch_name in preferred:
            try:
                channel_type = ChannelType(ch_name)
            except ValueError:
                continue

            # Verificar se tem endereço
            address = self._get_recipient_address(recipient, channel_type)
            if not address:
                continue

            # Verificar preferências
            if preferences and not preferences.is_channel_enabled(ch_name):
                continue

            channel = self._get_default_channel(channel_type)
            channels.append((channel_type, channel))

        return channels

    def _get_recipient_address(
        self,
        recipient: RecipientSchema,
        channel_type: ChannelType,
    ) -> Optional[str]:
        """Obtém o endereço do destinatário para um canal.

        Args:
            recipient: Dados do destinatário.
            channel_type: Tipo do canal.

        Returns:
            Endereço ou None.
        """
        if channel_type == ChannelType.EMAIL:
            return recipient.email
        elif channel_type in [ChannelType.SMS, ChannelType.WHATSAPP, ChannelType.VOICE]:
            return recipient.phone
        elif channel_type == ChannelType.PUSH:
            return recipient.device_token
        elif channel_type == ChannelType.IN_APP:
            return str(recipient.user_id) if recipient.user_id else None
        else:
            return None

    def _create_queue_item(
        self,
        recipient: RecipientSchema,
        request: SendNotificationRequest,
        template: Optional[NotificationTemplate],
        channel_type: ChannelType,
        channel_config: Optional[NotificationChannel],
        batch_id: UUID,
        created_by: Optional[UUID],
    ) -> NotificationQueue:
        """Cria um item na fila de notificações.

        Args:
            recipient: Dados do destinatário.
            request: Dados da requisição.
            template: Template a usar.
            channel_type: Tipo do canal.
            channel_config: Configuração do canal.
            batch_id: ID do batch.
            created_by: ID do criador.

        Returns:
            Item da fila criado.
        """
        # Gerar ID único da notificação
        notification_id = f"notif_{uuid.uuid4().hex[:16]}"

        # Obter endereço
        recipient_address = self._get_recipient_address(recipient, channel_type)

        # Renderizar conteúdo
        subject, body, body_html = self._render_content(
            template=template,
            request=request,
            channel_type=channel_type,
            variables=request.template_variables,
        )

        # Determinar status inicial
        status = QueueStatus.PENDING
        if request.scheduled_at and request.scheduled_at > datetime.utcnow():
            status = QueueStatus.SCHEDULED

        return NotificationQueue(
            tenant_id=self.tenant_id,
            notification_id=notification_id,
            batch_id=batch_id,
            user_id=recipient.user_id,
            recipient_type="user" if recipient.user_id else channel_type.value,
            recipient_address=recipient_address,
            recipient_name=recipient.name,
            channel_id=channel_config.id if channel_config else None,
            channel_type=channel_type.value,
            template_id=template.id if template else None,
            subject=subject,
            body=body,
            body_html=body_html,
            template_variables=request.template_variables,
            status=status,
            priority=request.priority,
            scheduled_at=request.scheduled_at,
            not_after=request.not_after,
            max_attempts=channel_config.max_retries if channel_config else 3,
            category=request.category,
            tags=request.tags,
            source_entity_type=request.source_entity_type,
            source_entity_id=request.source_entity_id,
            trigger_type="api",
            created_by=created_by,
        )

    def _render_content(
        self,
        template: Optional[NotificationTemplate],
        request: SendNotificationRequest,
        channel_type: ChannelType,
        variables: Dict[str, Any],
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Renderiza o conteúdo da notificação.

        Args:
            template: Template a usar.
            request: Dados da requisição.
            channel_type: Tipo do canal.
            variables: Variáveis para substituição.

        Returns:
            Tupla (subject, body, body_html).
        """
        subject = None
        body = None
        body_html = None

        if template:
            # Usar template baseado no canal
            if channel_type == ChannelType.EMAIL:
                subject = self._substitute_variables(template.email_subject, variables)
                body = self._substitute_variables(template.email_body_text, variables)
                body_html = self._substitute_variables(template.email_body_html, variables)
            elif channel_type == ChannelType.WHATSAPP:
                body = self._substitute_variables(template.whatsapp_body, variables)
            elif channel_type == ChannelType.SMS:
                body = self._substitute_variables(template.sms_body, variables)
            elif channel_type == ChannelType.PUSH:
                subject = self._substitute_variables(template.push_title, variables)
                body = self._substitute_variables(template.push_body, variables)
            elif channel_type == ChannelType.IN_APP:
                subject = self._substitute_variables(template.in_app_title, variables)
                body = self._substitute_variables(template.in_app_body, variables)
        else:
            # Usar conteúdo direto
            subject = self._substitute_variables(request.subject, variables)
            body = self._substitute_variables(request.body, variables)
            body_html = self._substitute_variables(request.body_html, variables)

        return subject, body, body_html

    def _substitute_variables(
        self,
        content: Optional[str],
        variables: Dict[str, Any],
    ) -> Optional[str]:
        """Substitui variáveis no conteúdo.

        Args:
            content: Conteúdo com placeholders.
            variables: Variáveis para substituição.

        Returns:
            Conteúdo com variáveis substituídas.
        """
        if not content:
            return None

        result = content
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            result = result.replace(placeholder, str(value) if value else "")

        return result

    def _log_event(
        self,
        queue_item: NotificationQueue,
        event_type: LogEventType,
        message: str,
        level: LogLevel = LogLevel.INFO,
        details: Optional[Dict[str, Any]] = None,
    ) -> NotificationLog:
        """Cria uma entrada de log.

        Args:
            queue_item: Item da fila.
            event_type: Tipo do evento.
            message: Mensagem do log.
            level: Nível do log.
            details: Detalhes adicionais.

        Returns:
            Entrada de log criada.
        """
        log = NotificationLog(
            tenant_id=self.tenant_id,
            queue_id=queue_item.id,
            notification_id=queue_item.notification_id,
            channel_id=queue_item.channel_id,
            channel_type=queue_item.channel_type,
            template_id=queue_item.template_id,
            user_id=queue_item.user_id,
            recipient_address=queue_item.recipient_address,
            event_type=event_type,
            level=level,
            message=message,
            details=details or {},
            new_status=queue_item.status.value,
        )

        self.db.add(log)
        return log

    # =========================================================================
    # Métodos de busca
    # =========================================================================

    def _get_template_by_id(self, template_id: UUID) -> Optional[NotificationTemplate]:
        """Busca template por ID."""
        return (
            self.db.query(NotificationTemplate)
            .filter(
                NotificationTemplate.tenant_id == self.tenant_id,
                NotificationTemplate.id == template_id,
                NotificationTemplate.active == True,
                NotificationTemplate.status == TemplateStatus.ACTIVE,
            )
            .first()
        )

    def _get_template_by_slug(self, slug: str) -> Optional[NotificationTemplate]:
        """Busca template por slug."""
        return (
            self.db.query(NotificationTemplate)
            .filter(
                NotificationTemplate.tenant_id == self.tenant_id,
                NotificationTemplate.slug == slug,
                NotificationTemplate.active == True,
                NotificationTemplate.status == TemplateStatus.ACTIVE,
            )
            .first()
        )

    def _get_user_preferences(self, user_id: UUID) -> Optional[NotificationPreference]:
        """Busca preferências do usuário."""
        return (
            self.db.query(NotificationPreference)
            .filter(
                NotificationPreference.tenant_id == self.tenant_id,
                NotificationPreference.user_id == user_id,
                NotificationPreference.active == True,
            )
            .first()
        )

    def _get_channel_by_id(self, channel_id: UUID) -> Optional[NotificationChannel]:
        """Busca canal por ID."""
        return (
            self.db.query(NotificationChannel)
            .filter(
                NotificationChannel.tenant_id == self.tenant_id,
                NotificationChannel.id == channel_id,
                NotificationChannel.active == True,
            )
            .first()
        )

    def _get_default_channel(
        self,
        channel_type: ChannelType,
    ) -> Optional[NotificationChannel]:
        """Busca canal padrão para um tipo."""
        return (
            self.db.query(NotificationChannel)
            .filter(
                NotificationChannel.tenant_id == self.tenant_id,
                NotificationChannel.channel_type == channel_type,
                NotificationChannel.is_default == True,
                NotificationChannel.active == True,
            )
            .first()
        )

    # =========================================================================
    # Métodos de consulta
    # =========================================================================

    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas da fila.

        Returns:
            Dicionário com estatísticas.
        """
        # Contagem por status
        status_counts = (
            self.db.query(
                NotificationQueue.status,
                func.count(NotificationQueue.id),
            )
            .filter(NotificationQueue.tenant_id == self.tenant_id)
            .group_by(NotificationQueue.status)
            .all()
        )

        # Contagem por canal
        channel_counts = (
            self.db.query(
                NotificationQueue.channel_type,
                func.count(NotificationQueue.id),
            )
            .filter(
                NotificationQueue.tenant_id == self.tenant_id,
                NotificationQueue.status == QueueStatus.PENDING,
            )
            .group_by(NotificationQueue.channel_type)
            .all()
        )

        # Item mais antigo pendente
        oldest = (
            self.db.query(NotificationQueue.enqueued_at)
            .filter(
                NotificationQueue.tenant_id == self.tenant_id,
                NotificationQueue.status == QueueStatus.PENDING,
            )
            .order_by(NotificationQueue.enqueued_at.asc())
            .first()
        )

        return {
            "by_status": {s.value: c for s, c in status_counts},
            "by_channel": dict(channel_counts),
            "oldest_pending_at": oldest[0] if oldest else None,
        }

    def get_notification_history(
        self,
        user_id: Optional[UUID] = None,
        channel_type: Optional[str] = None,
        status: Optional[QueueStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[NotificationQueue]:
        """Obtém histórico de notificações.

        Args:
            user_id: Filtrar por usuário.
            channel_type: Filtrar por canal.
            status: Filtrar por status.
            start_date: Data inicial.
            end_date: Data final.
            limit: Limite de resultados.
            offset: Offset para paginação.

        Returns:
            Lista de notificações.
        """
        query = self.db.query(NotificationQueue).filter(
            NotificationQueue.tenant_id == self.tenant_id
        )

        if user_id:
            query = query.filter(NotificationQueue.user_id == user_id)
        if channel_type:
            query = query.filter(NotificationQueue.channel_type == channel_type)
        if status:
            query = query.filter(NotificationQueue.status == status)
        if start_date:
            query = query.filter(NotificationQueue.created_at >= start_date)
        if end_date:
            query = query.filter(NotificationQueue.created_at <= end_date)

        return query.order_by(NotificationQueue.created_at.desc()).offset(offset).limit(limit).all()

    def cancel_notification(
        self,
        notification_id: str,
        reason: Optional[str] = None,
    ) -> bool:
        """Cancela uma notificação pendente.

        Args:
            notification_id: ID da notificação.
            reason: Motivo do cancelamento.

        Returns:
            True se cancelado com sucesso.
        """
        queue_item = (
            self.db.query(NotificationQueue)
            .filter(
                NotificationQueue.tenant_id == self.tenant_id,
                NotificationQueue.notification_id == notification_id,
                NotificationQueue.status.in_([QueueStatus.PENDING, QueueStatus.SCHEDULED]),
            )
            .first()
        )

        if not queue_item:
            return False

        old_status = queue_item.status.value
        queue_item.status = QueueStatus.CANCELLED
        queue_item.completed_at = datetime.utcnow()
        queue_item.last_error = reason

        self._log_event(
            queue_item=queue_item,
            event_type=LogEventType.CANCELLED,
            message=reason or "Notificação cancelada",
            details={"previous_status": old_status},
        )

        self.db.commit()
        return True
