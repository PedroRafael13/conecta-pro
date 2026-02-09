"""
Executor de acoes relacionadas a comunicados/anuncios.

Suporta:
- CREATE_ANNOUNCEMENT: Criar novo comunicado
- PUBLISH_ANNOUNCEMENT: Publicar comunicado existente

Nota: Os ActionTypes CREATE_ANNOUNCEMENT e PUBLISH_ANNOUNCEMENT devem ser
adicionados ao enum ActionType em action_types.py para integracao completa.
Este executor usa comparacao por string value para compatibilidade.

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from modules.operacional.communication.models.announcement import (
    AnnouncementCategory,
    AnnouncementPriority,
    AnnouncementStatus,
    AnnouncementTargetType,
)
from modules.operacional.communication.repositories.communication_repository import (
    AnnouncementRepository,
)
from modules.operacional.communication.schemas.communication_schemas import (
    AnnouncementCreate,
)

from ..action_schemas import ActionPreview, ActionResult
from ..action_types import ActionStatus
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos de acao de comunicacao (a serem integrados em ActionType futuramente)
# ---------------------------------------------------------------------------


class CommunicationActionType(StrEnum):
    """Tipos de acoes de comunicacao."""

    CREATE_ANNOUNCEMENT = "create_announcement"
    PUBLISH_ANNOUNCEMENT = "publish_announcement"


class CommunicationActionExecutor(BaseActionExecutor):
    """
    Executor para acoes de comunicados.

    Utiliza AnnouncementRepository para operacoes reais no banco.
    Preview mostra dados e warnings. Execute realiza a operacao.
    """

    # Constantes de acao
    ACTION_CREATE = CommunicationActionType.CREATE_ANNOUNCEMENT.value
    ACTION_PUBLISH = CommunicationActionType.PUBLISH_ANNOUNCEMENT.value

    async def create_preview(self, request) -> ActionPreview:
        """Cria preview para acao de comunicado."""
        action_type_value = self._get_action_value(request)

        if action_type_value == self.ACTION_CREATE:
            return await self._create_announcement_preview(request)
        elif action_type_value == self.ACTION_PUBLISH:
            return await self._publish_announcement_preview(request)
        else:
            raise ValueError(f"Acao nao suportada: {action_type_value}")

    async def execute(self, request, action_id: str) -> ActionResult:
        """Executa acao de comunicado."""
        action_type_value = self._get_action_value(request)
        started_at = datetime.utcnow()

        try:
            if action_type_value == self.ACTION_CREATE:
                result = await self._execute_create_announcement(request, action_id, started_at)
            elif action_type_value == self.ACTION_PUBLISH:
                result = await self._execute_publish_announcement(request, action_id, started_at)
            else:
                raise ValueError(f"Acao nao suportada: {action_type_value}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar acao {action_type_value}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=self._get_action_type_enum(request),
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar acao: {action_type_value}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # =========================================================================
    # Helpers
    # =========================================================================

    @staticmethod
    def _get_action_value(request) -> str:
        """Extrai o valor string do action_type do request."""
        action_type = getattr(request, "action_type", None)
        if action_type is None:
            return ""
        if hasattr(action_type, "value"):
            return action_type.value
        return str(action_type)

    @staticmethod
    def _get_action_type_enum(request):
        """Retorna o action_type do request (enum ou string)."""
        return getattr(request, "action_type", CommunicationActionType.CREATE_ANNOUNCEMENT)

    # =========================================================================
    # Preview methods
    # =========================================================================

    async def _create_announcement_preview(self, request) -> ActionPreview:
        """Cria preview para criacao de comunicado."""
        params = getattr(request, "parameters", {}) or {}
        title = params.get("title", "")
        content = params.get("content", "")
        priority = params.get("priority", "normal")
        category = params.get("category", "informativo")
        target_type = params.get("target_type", "all")

        changes_summary = []
        warnings = []
        affected_entities = []

        # Validar parametros minimos
        if not title:
            warnings.append("Titulo do comunicado nao informado")
        else:
            changes_summary.append(f"Titulo: {title}")

        if not content:
            warnings.append("Conteudo do comunicado nao informado")
        else:
            content_preview = content[:100] + "..." if len(content) > 100 else content
            changes_summary.append(f"Conteudo: {content_preview}")

        changes_summary.append(f"Prioridade: {priority}")
        changes_summary.append(f"Categoria: {category}")
        changes_summary.append(f"Destinatarios: {target_type}")

        # Validar prioridade
        valid_priorities = [p.value for p in AnnouncementPriority]
        if priority not in valid_priorities:
            warnings.append(f"Prioridade '{priority}' invalida. Opcoes: {', '.join(valid_priorities)}")

        # Validar categoria
        valid_categories = [c.value for c in AnnouncementCategory]
        if category not in valid_categories:
            warnings.append(f"Categoria '{category}' invalida. Opcoes: {', '.join(valid_categories)}")

        # Aviso para comunicados urgentes
        if priority in ("urgente", "alta"):
            warnings.append("Comunicado com prioridade alta/urgente: sera enviada notificacao push aos destinatarios")

        # Verificar se requer confirmacao
        requires_ack = params.get("requires_acknowledgment", False)
        if requires_ack:
            changes_summary.append("Requer confirmacao de leitura: Sim")

        title_text = f"Criar Comunicado - {title}" if title else "Criar Comunicado"
        description = f"Criar comunicado '{title}' com prioridade {priority}" if title else "Criar novo comunicado"

        # Permissao
        required_perm = "posts:view"
        user_role = getattr(self, "user_role", None)
        user_has_perm = True

        if user_role:
            try:
                from modules.operacional.permissions import Permission, has_permission

                user_has_perm = has_permission(user_role, Permission.POSTS_VIEW)
            except Exception as e:
                logger.warning(f"Erro ao verificar permissao: {e}")
                user_has_perm = True

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=self._get_action_type_enum(request),
            title=title_text,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _publish_announcement_preview(self, request) -> ActionPreview:
        """Cria preview para publicacao de comunicado."""
        params = getattr(request, "parameters", {}) or {}
        announcement_id = params.get("announcement_id")
        tenant_id = params.get("tenant_id", "")

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar comunicado
        announcement = None
        if announcement_id:
            try:
                repo = AnnouncementRepository(self.db)
                announcement = await repo.get_by_id(announcement_id, tenant_id or None)
            except Exception as e:
                logger.warning(f"Erro ao buscar comunicado {announcement_id}: {e}")

        if not announcement:
            warnings.append(f"Comunicado '{announcement_id}' nao encontrado")
            title_text = "Publicar Comunicado"
            description = "Comunicado nao encontrado"
        else:
            affected_entities.append(
                {
                    "type": "announcement",
                    "id": announcement.id,
                    "title": getattr(announcement, "titulo", getattr(announcement, "title", "N/A")),
                }
            )

            ann_title = getattr(announcement, "titulo", getattr(announcement, "title", "N/A"))
            ann_status = getattr(announcement, "status", "N/A")

            changes_summary.append(f"Comunicado: {ann_title}")
            changes_summary.append(f"Status atual: {ann_status}")
            changes_summary.append(f"Novo status: {AnnouncementStatus.PUBLISHED.value}")

            # Verificar se pode ser publicado
            if ann_status in (AnnouncementStatus.PUBLISHED.value, AnnouncementStatus.PUBLICADO.value):
                warnings.append("Comunicado ja esta publicado")
            elif ann_status in (
                AnnouncementStatus.CANCELLED.value,
                AnnouncementStatus.EXPIRED.value,
                AnnouncementStatus.ARQUIVADO.value,
            ):
                warnings.append(f"Comunicado com status '{ann_status}' nao pode ser publicado")

            ann_priority = getattr(announcement, "prioridade", getattr(announcement, "priority", "normal"))
            if ann_priority in ("urgente", "alta"):
                warnings.append("Comunicado urgente/alta prioridade: sera enviada notificacao push")

            title_text = f"Publicar Comunicado - {ann_title}"
            description = f"Publicar comunicado '{ann_title}'"

        # Permissao
        required_perm = "posts:view"
        user_role = getattr(self, "user_role", None)
        user_has_perm = True

        if user_role:
            try:
                from modules.operacional.permissions import Permission, has_permission

                user_has_perm = has_permission(user_role, Permission.POSTS_VIEW)
            except Exception as e:
                logger.warning(f"Erro ao verificar permissao: {e}")
                user_has_perm = True

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=self._get_action_type_enum(request),
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
    # Execute methods
    # =========================================================================

    async def _execute_create_announcement(
        self,
        request,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criacao de comunicado."""
        params = getattr(request, "parameters", {}) or {}
        title = params.get("title", "")
        content = params.get("content", "")
        priority = params.get("priority", "normal")
        category = params.get("category", "informativo")
        target_type_str = params.get("target_type", "all")
        tenant_id = params.get("tenant_id", "")
        requires_ack = params.get("requires_acknowledgment", False)

        if not title:
            raise ValueError("Titulo do comunicado e obrigatorio")
        if not content:
            raise ValueError("Conteudo do comunicado e obrigatorio")
        if not tenant_id:
            raise ValueError("Tenant ID e obrigatorio")

        # Mapear strings para enums
        try:
            priority_enum = AnnouncementPriority(priority)
        except ValueError:
            priority_enum = AnnouncementPriority.NORMAL

        try:
            category_enum = AnnouncementCategory(category)
        except ValueError:
            category_enum = AnnouncementCategory.INFORMATIVO

        try:
            target_enum = AnnouncementTargetType(target_type_str)
        except ValueError:
            target_enum = AnnouncementTargetType.ALL

        # Criar schema
        announcement_data = AnnouncementCreate(
            title=title,
            content=content,
            priority=priority_enum,
            category=category_enum,
            target_type=target_enum,
            target_ids=params.get("target_ids"),
            target_roles=params.get("target_roles"),
            requires_acknowledgment=requires_ack,
            publish_at=params.get("publish_at"),
            expires_at=params.get("expires_at"),
        )

        # Usar UUID real do usuario
        user_uuid = getattr(self, "user_uuid", None) or getattr(request, "user_id", "")

        # Criar via repository
        repo = AnnouncementRepository(self.db)
        announcement = await repo.create(
            data=announcement_data,
            tenant_id=tenant_id,
            created_by=user_uuid,
        )

        logger.info(f"Comunicado criado via Bartolo: {announcement.id}")

        return ActionResult(
            action_id=action_id,
            action_type=self._get_action_type_enum(request),
            status=ActionStatus.COMPLETED,
            success=True,
            message="Comunicado criado com sucesso",
            details={
                "announcement_id": announcement.id,
                "title": title,
                "priority": priority,
                "category": category,
                "target_type": target_type_str,
                "status": announcement.status,
                "requires_acknowledgment": requires_ack,
            },
            affected_entities=[
                {"type": "announcement", "id": announcement.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_publish_announcement(
        self,
        request,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa publicacao de comunicado."""
        params = getattr(request, "parameters", {}) or {}
        announcement_id = params.get("announcement_id")
        tenant_id = params.get("tenant_id", "")

        if not announcement_id:
            raise ValueError("ID do comunicado e obrigatorio")
        if not tenant_id:
            raise ValueError("Tenant ID e obrigatorio")

        # Usar UUID real do usuario
        user_uuid = getattr(self, "user_uuid", None) or getattr(request, "user_id", "")

        # Buscar comunicado
        repo = AnnouncementRepository(self.db)
        announcement = await repo.get_by_id(announcement_id, tenant_id)

        if not announcement:
            raise ValueError(f"Comunicado '{announcement_id}' nao encontrado")

        ann_status = getattr(announcement, "status", "")

        # Verificar se pode ser publicado
        if ann_status in (AnnouncementStatus.PUBLISHED.value, AnnouncementStatus.PUBLICADO.value):
            raise ValueError("Comunicado ja esta publicado")
        if ann_status in (
            AnnouncementStatus.CANCELLED.value,
            AnnouncementStatus.EXPIRED.value,
            AnnouncementStatus.ARQUIVADO.value,
        ):
            raise ValueError(f"Comunicado com status '{ann_status}' nao pode ser publicado")

        # Publicar via repository
        schedule_at = params.get("schedule_at")
        published = await repo.publish(
            announcement_id=announcement_id,
            tenant_id=tenant_id,
            published_by=user_uuid,
            schedule_at=schedule_at,
        )

        if not published:
            raise ValueError(f"Nao foi possivel publicar o comunicado. Status atual: {ann_status}.")

        action_label = "agendado" if schedule_at else "publicado"
        logger.info(f"Comunicado {action_label} via Bartolo: {published.id}")

        ann_title = getattr(published, "titulo", getattr(published, "title", "N/A"))

        return ActionResult(
            action_id=action_id,
            action_type=self._get_action_type_enum(request),
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Comunicado {action_label} com sucesso",
            details={
                "announcement_id": published.id,
                "title": ann_title,
                "status": published.status,
                "published_by": user_uuid,
                "published_at": (
                    getattr(published, "published_at", None).isoformat()
                    if getattr(published, "published_at", None)
                    else None
                ),
                "scheduled_at": (schedule_at.isoformat() if schedule_at else None),
            },
            affected_entities=[
                {"type": "announcement", "id": published.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
