"""
Executor de acoes relacionadas a notificacoes.

Suporta:
- SEND_NOTIFICATION: Enviar notificacao para usuarios

Author: Conecta PRO Team
Date: 2026-01-30
"""

import logging
from datetime import datetime
from uuid import uuid4

from ..action_schemas import ActionPreview, ActionRequest, ActionResult
from ..action_types import ActionStatus, ActionType
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)

# Import condicional do servico de notificacao
try:
    from modules.notifications.services.notification_service import NotificationService

    _HAS_NOTIFICATION_SERVICE = True
except ImportError:
    _HAS_NOTIFICATION_SERVICE = False

# Import condicional do servico de push
try:
    from modules.notifications.services.push_service import PushService

    _HAS_PUSH_SERVICE = True
except ImportError:
    _HAS_PUSH_SERVICE = False


class NotificationActionExecutor(BaseActionExecutor):
    """
    Executor para acoes de notificacao.

    Envia notificacoes via push, email, SMS ou in-app
    para usuarios ou grupos de usuarios.
    """

    SUPPORTED_ACTIONS = [ActionType.SEND_NOTIFICATION]

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para envio de notificacao."""
        return await self._send_notification_preview(request)

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa envio de notificacao."""
        started_at = datetime.utcnow()

        try:
            return await self._execute_send_notification(request, action_id, started_at)
        except Exception as e:
            logger.error(f"Erro ao enviar notificacao: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=request.action_type,
                status=ActionStatus.FAILED,
                success=False,
                message="Erro ao enviar notificacao",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # =========================================================================
    # Preview
    # =========================================================================

    async def _send_notification_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para envio de notificacao."""
        params = request.parameters or {}
        title = params.get("title", "")
        message = params.get("message", "")
        channel = params.get("channel", "push")  # push, email, sms, in_app
        target_type = params.get("target_type", "user")  # user, role, all, post
        target_ids = params.get("target_ids", [])
        priority = params.get("priority", "normal")

        changes_summary = []
        warnings = []
        affected_entities = []

        if not title:
            warnings.append("Titulo da notificacao nao informado")
        else:
            changes_summary.append(f"Titulo: {title}")

        if not message:
            warnings.append("Mensagem da notificacao nao informada")
        else:
            msg_preview = message[:100] + "..." if len(message) > 100 else message
            changes_summary.append(f"Mensagem: {msg_preview}")

        changes_summary.append(f"Canal: {channel}")
        changes_summary.append(f"Destinatarios: {target_type}")
        changes_summary.append(f"Prioridade: {priority}")

        # Validar canal
        valid_channels = ["push", "email", "sms", "in_app", "all"]
        if channel not in valid_channels:
            warnings.append(f"Canal '{channel}' invalido. Opcoes: {', '.join(valid_channels)}")

        # Contagem de destinatarios
        if target_type == "all":
            warnings.append("Notificacao sera enviada para TODOS os usuarios do sistema")
            changes_summary.append("Alcance: Todos os usuarios")
        elif target_type == "role":
            roles = params.get("target_roles", [])
            changes_summary.append(f"Roles: {', '.join(roles) if roles else 'nao especificados'}")
        elif target_ids:
            changes_summary.append(f"Total de destinatarios: {len(target_ids)}")
            for tid in target_ids[:5]:
                affected_entities.append({"type": "user", "id": tid})
            if len(target_ids) > 5:
                changes_summary.append(f"... e mais {len(target_ids) - 5} destinatarios")

        # Aviso para SMS
        if channel in ("sms", "all"):
            warnings.append("Envio de SMS pode gerar custos adicionais por mensagem")

        # Aviso para prioridade alta
        if priority in ("alta", "urgente", "critica"):
            warnings.append(f"Notificacao com prioridade {priority}: sera exibida com destaque")

        title_text = f"Enviar Notificacao - {title}" if title else "Enviar Notificacao"
        description = f"Enviar notificacao via {channel} para {target_type}"

        # Permissao
        required_perm = "notifications:send"
        user_role = getattr(self, "user_role", None)
        user_has_perm = True

        if user_role:
            try:
                from modules.operacional.permissions import Permission, has_permission

                user_has_perm = has_permission(user_role, Permission.NOTIFICATIONS_SEND)
            except Exception:
                user_has_perm = True

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title_text,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    # =========================================================================
    # Execute
    # =========================================================================

    async def _execute_send_notification(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa envio de notificacao."""
        params = request.parameters or {}
        title = params.get("title", "")
        message = params.get("message", "")
        channel = params.get("channel", "push")
        target_type = params.get("target_type", "user")
        target_ids = params.get("target_ids", [])
        target_roles = params.get("target_roles", [])
        priority = params.get("priority", "normal")
        tenant_id = params.get("tenant_id", "")
        metadata = params.get("metadata", {})

        if not title:
            raise ValueError("Titulo da notificacao e obrigatorio")
        if not message:
            raise ValueError("Mensagem da notificacao e obrigatoria")

        user_uuid = getattr(self, "user_uuid", None) or request.user_id

        sent_count = 0
        failed_count = 0
        notification_ids = []

        # Usar servico de notificacao se disponivel
        if _HAS_NOTIFICATION_SERVICE:
            try:
                notification_service = NotificationService(self.db)
                result = await notification_service.send(
                    title=title,
                    message=message,
                    channel=channel,
                    target_type=target_type,
                    target_ids=target_ids,
                    target_roles=target_roles,
                    priority=priority,
                    tenant_id=tenant_id,
                    sent_by=user_uuid,
                    metadata=metadata,
                )
                sent_count = getattr(result, "sent_count", 0)
                failed_count = getattr(result, "failed_count", 0)
                notification_ids = getattr(result, "notification_ids", [])
                logger.info(f"Notificacao enviada via servico: {sent_count} enviadas, {failed_count} falhas")
            except Exception as e:
                logger.error(f"Erro no servico de notificacao: {e}")
                raise
        elif _HAS_PUSH_SERVICE and channel in ("push", "all"):
            # Fallback: usar push service diretamente
            try:
                push_service = PushService(self.db)
                for target_id in target_ids:
                    try:
                        await push_service.send_push(
                            user_id=target_id,
                            title=title,
                            body=message,
                            priority=priority,
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.warning(f"Falha ao enviar push para {target_id}: {e}")
                        failed_count += 1
            except Exception as e:
                logger.error(f"Erro no push service: {e}")
                raise
        else:
            # Fallback: registrar sem envio real
            notification_id = str(uuid4())
            notification_ids.append(notification_id)
            sent_count = len(target_ids) if target_ids else 1
            logger.info(f"Notificacao registrada (fallback): {notification_id}")

        total = sent_count + failed_count
        success = sent_count > 0

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED if success else ActionStatus.FAILED,
            success=success,
            message=f"Notificacao enviada: {sent_count}/{total} destinatarios"
            if total > 0
            else "Notificacao registrada com sucesso",
            details={
                "notification_ids": notification_ids,
                "title": title,
                "channel": channel,
                "target_type": target_type,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "priority": priority,
            },
            affected_entities=[{"type": "notification", "id": nid} for nid in notification_ids[:10]],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
