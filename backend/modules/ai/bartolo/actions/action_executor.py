"""
Orquestrador principal do sistema de ações executivas.
"""

import logging
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from modules.audit.models import AuditAction, AuditCategory, AuditResult, AuditSeverity
from modules.audit.schemas import AuditLogCreate
from modules.audit.services.audit_service import AuditService

from .action_schemas import ActionConfirmation, ActionPreview, ActionRequest, ActionResult
from .action_types import ActionStatus, ActionType
from .executors.allocation_executor import AllocationActionExecutor
from .executors.base_executor import BaseActionExecutor
from .executors.communication_executor import CommunicationActionExecutor
from .executors.diarist_executor import DiaristActionExecutor
from .executors.disciplinary_executor import DisciplinaryActionExecutor
from .executors.inspection_executor import InspectionActionExecutor
from .executors.notification_executor import NotificationActionExecutor
from .executors.occurrence_executor import OccurrenceActionExecutor
from .executors.post_executor import PostActionExecutor
from .executors.report_executor import ReportActionExecutor
from .executors.scale_executor import ScaleActionExecutor
from .executors.shift_executor import ShiftActionExecutor
from .executors.substitution_executor import SubstitutionActionExecutor
from .executors.time_bank_executor import TimeBankActionExecutor

logger = logging.getLogger(__name__)

# Dicionário global para armazenar ações pendentes (compartilhado entre instâncias)
# Em produção, usar Redis ou banco de dados
_GLOBAL_PENDING_ACTIONS: dict[str, tuple] = {}


class ActionExecutor:
    """Orquestrador principal do sistema de ações."""

    # Mapeamento de tipos de ação para executores
    EXECUTORS: dict[ActionType, type[BaseActionExecutor]] = {
        # Escalas
        ActionType.CREATE_SCALE: ScaleActionExecutor,
        ActionType.APPROVE_SCALE: ScaleActionExecutor,
        ActionType.PUBLISH_SCALE: ScaleActionExecutor,
        # Alocações
        ActionType.ALLOCATE_EMPLOYEE: AllocationActionExecutor,
        ActionType.TERMINATE_ALLOCATION: AllocationActionExecutor,
        ActionType.TRANSFER_EMPLOYEE: AllocationActionExecutor,
        # Turnos
        ActionType.CREATE_SHIFT: ShiftActionExecutor,
        ActionType.REGISTER_CHECKIN: ShiftActionExecutor,
        ActionType.REGISTER_CHECKOUT: ShiftActionExecutor,
        ActionType.MARK_ABSENCE: ShiftActionExecutor,
        # Ocorrências
        ActionType.CREATE_OCCURRENCE: OccurrenceActionExecutor,
        ActionType.RESOLVE_OCCURRENCE: OccurrenceActionExecutor,
        ActionType.UPDATE_OCCURRENCE: OccurrenceActionExecutor,
        # Disciplinares
        ActionType.CREATE_DISCIPLINARY: DisciplinaryActionExecutor,
        ActionType.APPROVE_DISCIPLINARY: DisciplinaryActionExecutor,
        ActionType.REJECT_DISCIPLINARY: DisciplinaryActionExecutor,
        # Rondas
        ActionType.CREATE_ROUND: InspectionActionExecutor,
        ActionType.START_ROUND: InspectionActionExecutor,
        ActionType.COMPLETE_ROUND: InspectionActionExecutor,
        # Diaristas
        ActionType.CREATE_DIARIST: DiaristActionExecutor,
        ActionType.SCHEDULE_DIARIST: DiaristActionExecutor,
        # Comunicados
        ActionType.CREATE_ANNOUNCEMENT: CommunicationActionExecutor,
        ActionType.PUBLISH_ANNOUNCEMENT: CommunicationActionExecutor,
        # Banco de Horas
        ActionType.APPROVE_OVERTIME: TimeBankActionExecutor,
        ActionType.REQUEST_COMPENSATION: TimeBankActionExecutor,
        ActionType.VIEW_BALANCE: TimeBankActionExecutor,
        # Postos
        ActionType.CREATE_POST: PostActionExecutor,
        ActionType.UPDATE_POST: PostActionExecutor,
        ActionType.DELETE_POST: PostActionExecutor,
        ActionType.GET_POST_STATS: PostActionExecutor,
        # Escalas (avançado)
        ActionType.AUTO_GENERATE_SCALE: ScaleActionExecutor,
        ActionType.OPTIMIZE_SCALE: ScaleActionExecutor,
        ActionType.CREATE_SCALE_TEMPLATE: ScaleActionExecutor,
        ActionType.APPLY_SCALE_TEMPLATE: ScaleActionExecutor,
        # Diaristas (avançado)
        ActionType.EVALUATE_DIARIST: DiaristActionExecutor,
        ActionType.APPROVE_DIARIST_PAYMENT: DiaristActionExecutor,
        ActionType.GENERATE_DIARIST_PAYMENT: DiaristActionExecutor,
        # Rondas (avançado)
        ActionType.REGISTER_CHECKPOINT: InspectionActionExecutor,
        ActionType.PAUSE_ROUND: InspectionActionExecutor,
        ActionType.RESUME_ROUND: InspectionActionExecutor,
        # Substituições
        ActionType.CREATE_SUBSTITUTION: SubstitutionActionExecutor,
        # Notificações
        ActionType.SEND_NOTIFICATION: NotificationActionExecutor,
        # Relatórios
        ActionType.GENERATE_REPORT: ReportActionExecutor,
    }

    # Timeout para ações pendentes (5 minutos)
    ACTION_TIMEOUT_MINUTES = 5

    def __init__(self, db: AsyncSession):
        """
        Inicializa orquestrador.

        Args:
            db: Sessão async do SQLAlchemy
        """
        self.db = db
        self.audit_service = AuditService(db)

        # Usa dicionário global compartilhado entre todas as instâncias
        # Em produção, usar Redis ou banco de dados
        self._pending_actions = _GLOBAL_PENDING_ACTIONS

    async def get_user_info(self, user_id: str) -> tuple[str, str] | None:
        """
        Busca informações do usuário no banco de dados.

        Args:
            user_id: ID do usuário (pode ser string numérica ou UUID)

        Returns:
            Tupla (uuid, role) do usuário ou None se não encontrado
        """
        try:
            # Tenta converter para UUID se for string UUID
            from uuid import UUID

            try:
                user_uuid = UUID(user_id) if isinstance(user_id, str) and len(user_id) > 10 else None
            except ValueError:
                user_uuid = None

            # Query para buscar id e role
            from sqlalchemy import text

            if user_uuid:
                result = await self.db.execute(
                    text("SELECT id, role FROM users WHERE id = :user_id AND is_active = true"),
                    {"user_id": str(user_uuid)},
                )
            else:
                # Se não for UUID, busca pelo ID convertido (fallback)
                result = await self.db.execute(
                    text(
                        "SELECT id, role FROM users WHERE CAST(id AS TEXT) LIKE :user_id AND is_active = true LIMIT 1"
                    ),
                    {"user_id": f"%{user_id}%"},
                )

            row = result.first()
            if row:
                user_uuid_str = str(row[0])
                user_role = row[1]
                logger.info(f"Usuário encontrado: UUID={user_uuid_str}, role={user_role}")
                return (user_uuid_str, user_role)

            logger.warning(f"Usuário {user_id} não encontrado ou inativo")
            return None

        except Exception as e:
            logger.error(f"Erro ao buscar info do usuário {user_id}: {e}")
            return None

    async def get_user_role(self, user_id: str) -> str | None:
        """
        Busca apenas o role do usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Role do usuário ou None
        """
        info = await self.get_user_info(user_id)
        return info[1] if info else None

    async def create_action_preview(self, request: ActionRequest) -> ActionPreview:
        """
        Cria preview da ação para confirmação do usuário.

        Args:
            request: Request de ação

        Returns:
            Preview com detalhes da ação

        Raises:
            ValueError: Se tipo de ação não é suportado
        """
        executor_class = self.EXECUTORS.get(request.action_type)
        if not executor_class:
            raise ValueError(f"Tipo de ação não suportado: {request.action_type.value}")

        logger.info(f"Criando preview para ação: {request.action_type.value}")

        # Buscar info do usuário (UUID e role)
        user_info = await self.get_user_info(request.user_id)
        if user_info:
            user_uuid, user_role = user_info
            logger.info(f"User {request.user_id}: UUID={user_uuid}, role={user_role}")
        else:
            user_uuid, user_role = None, None
            logger.warning(f"Usuário {request.user_id} não encontrado")

        # Criar executor e gerar preview (passando user info)
        executor = executor_class(self.db)
        executor.user_role = user_role  # Adiciona role ao executor
        executor.user_uuid = user_uuid  # Adiciona UUID ao executor
        preview = await executor.create_preview(request)

        # Armazenar request pendente
        self._pending_actions[preview.action_id] = (request, datetime.utcnow())
        logger.debug(f"Ação {preview.action_id} armazenada para confirmação")

        # Limpar ações expiradas
        await self._cleanup_expired_actions()

        return preview

    async def execute_action(self, confirmation: ActionConfirmation) -> ActionResult:
        """
        Executa ação após confirmação do usuário.

        Args:
            confirmation: Confirmação do usuário

        Returns:
            Resultado da execução

        Raises:
            ValueError: Se ação não encontrada ou expirada
        """
        # Buscar ação pendente
        pending = self._pending_actions.get(confirmation.action_id)
        if not pending:
            raise ValueError(f"Ação {confirmation.action_id} não encontrada ou expirada")

        request, created_at = pending

        # Verificar timeout
        if datetime.utcnow() - created_at > timedelta(minutes=self.ACTION_TIMEOUT_MINUTES):
            del self._pending_actions[confirmation.action_id]
            raise ValueError(
                f"Ação {confirmation.action_id} expirou (timeout de {self.ACTION_TIMEOUT_MINUTES} minutos)"
            )

        # Verificar se foi cancelada
        if not confirmation.confirmed:
            logger.info(f"Ação {confirmation.action_id} cancelada pelo usuário")

            # Auditar cancelamento
            await self._audit_action_cancelled(request, confirmation)

            # Remover da lista pendente
            del self._pending_actions[confirmation.action_id]

            return ActionResult(
                action_id=confirmation.action_id,
                action_type=request.action_type,
                status=ActionStatus.CANCELLED,
                success=False,
                message="Ação cancelada pelo usuário",
                started_at=datetime.utcnow(),
            )

        # Executar ação
        logger.info(f"Executando ação {confirmation.action_id}: {request.action_type.value}")

        # Gera correlation_id para auditoria
        correlation_id = str(uuid4())

        # Registrar início na auditoria
        await self._audit_action_start(request, confirmation, correlation_id)

        # Executar
        executor_class = self.EXECUTORS.get(request.action_type)
        executor = executor_class(self.db)

        # Buscar info do usuário para passar ao executor
        user_info = await self.get_user_info(request.user_id)
        if user_info:
            user_uuid, user_role = user_info
            executor.user_role = user_role
            executor.user_uuid = user_uuid
            logger.info(f"Executor configurado: UUID={user_uuid}, role={user_role}")
        else:
            logger.warning(f"Usuário {request.user_id} não encontrado para execução")

        try:
            result = await executor.execute(request, confirmation.action_id)

            # Registrar conclusão na auditoria
            await self._audit_action_complete(request, result, correlation_id)

            # Remover da lista pendente
            del self._pending_actions[confirmation.action_id]

            logger.info(f"Ação {confirmation.action_id} concluída: {'sucesso' if result.success else 'falha'}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar ação {confirmation.action_id}: {e}")

            # Auditar erro
            await self._audit_action_error(request, str(e), correlation_id)

            # Remover da lista pendente
            del self._pending_actions[confirmation.action_id]

            return ActionResult(
                action_id=confirmation.action_id,
                action_type=request.action_type,
                status=ActionStatus.FAILED,
                success=False,
                message="Erro ao executar ação",
                error_message=str(e),
                started_at=datetime.utcnow(),
            )

    async def _cleanup_expired_actions(self):
        """Remove ações pendentes expiradas."""
        now = datetime.utcnow()
        timeout = timedelta(minutes=self.ACTION_TIMEOUT_MINUTES)

        expired = [
            action_id for action_id, (_, created_at) in self._pending_actions.items() if now - created_at > timeout
        ]

        for action_id in expired:
            del self._pending_actions[action_id]
            logger.debug(f"Ação expirada removida: {action_id}")

    async def _audit_action_start(self, request: ActionRequest, confirmation: ActionConfirmation, correlation_id: str):
        """Registra início da ação na auditoria."""
        try:
            await self.audit_service.create_audit_log(
                AuditLogCreate(
                    action=AuditAction.CREATE.value,
                    category=AuditCategory.OPERATION.value,
                    description=f"Bartolo: Iniciando ação {request.action_type.value}",
                    user_id=request.user_id,
                    entity_type="bartolo_action",
                    entity_id=confirmation.action_id,
                    severity=AuditSeverity.MEDIUM.value,
                    result=AuditResult.SUCCESS.value,
                    metadata={
                        "action_type": request.action_type.value,
                        "category": request.category.value,
                        "parameters": request.parameters,
                        "confidence": request.confidence,
                        "detected_from": request.detected_from_message,
                        "user_notes": confirmation.user_notes,
                    },
                    tags=["bartolo", "action", "start", request.action_type.value],
                ),
                correlation_id=correlation_id,
            )
        except Exception as e:
            logger.error(f"Erro ao auditar início de ação: {e}")

    async def _audit_action_complete(self, request: ActionRequest, result: ActionResult, correlation_id: str):
        """Registra conclusão da ação na auditoria."""
        try:
            await self.audit_service.create_audit_log(
                AuditLogCreate(
                    action=AuditAction.CREATE.value,
                    category=AuditCategory.OPERATION.value,
                    description=f"Bartolo: Ação {request.action_type.value} {'concluída' if result.success else 'falhou'}",
                    user_id=request.user_id,
                    entity_type="bartolo_action",
                    entity_id=result.action_id,
                    severity=AuditSeverity.MEDIUM.value if result.success else AuditSeverity.HIGH.value,
                    result=AuditResult.SUCCESS.value if result.success else AuditResult.FAILURE.value,
                    metadata={
                        "action_type": request.action_type.value,
                        "status": result.status.value,
                        "success": result.success,
                        "message": result.message,
                        "details": result.details,
                        "affected_entities": result.affected_entities,
                        "duration_seconds": result.duration_seconds,
                        "error_message": result.error_message,
                    },
                    tags=["bartolo", "action", "complete", request.action_type.value],
                ),
                correlation_id=correlation_id,
            )

            # Armazena audit_log_id no resultado
            result.audit_log_id = correlation_id

        except Exception as e:
            logger.error(f"Erro ao auditar conclusão de ação: {e}")

    async def _audit_action_cancelled(self, request: ActionRequest, confirmation: ActionConfirmation):
        """Registra cancelamento da ação na auditoria."""
        try:
            await self.audit_service.create_audit_log(
                AuditLogCreate(
                    action=AuditAction.CREATE.value,
                    category=AuditCategory.OPERATION.value,
                    description=f"Bartolo: Ação {request.action_type.value} cancelada pelo usuário",
                    user_id=request.user_id,
                    entity_type="bartolo_action",
                    entity_id=confirmation.action_id,
                    severity=AuditSeverity.LOW.value,
                    result=AuditResult.CANCELLED.value,
                    metadata={
                        "action_type": request.action_type.value,
                        "user_notes": confirmation.user_notes,
                    },
                    tags=["bartolo", "action", "cancelled", request.action_type.value],
                ),
            )
        except Exception as e:
            logger.error(f"Erro ao auditar cancelamento de ação: {e}")

    async def _audit_action_error(self, request: ActionRequest, error_message: str, correlation_id: str):
        """Registra erro na execução da ação."""
        try:
            await self.audit_service.create_audit_log(
                AuditLogCreate(
                    action=AuditAction.CREATE.value,
                    category=AuditCategory.OPERATION.value,
                    description=f"Bartolo: Erro ao executar ação {request.action_type.value}",
                    user_id=request.user_id,
                    entity_type="bartolo_action",
                    severity=AuditSeverity.HIGH.value,
                    result=AuditResult.FAILURE.value,
                    metadata={
                        "action_type": request.action_type.value,
                        "error": error_message,
                    },
                    tags=["bartolo", "action", "error", request.action_type.value],
                ),
                correlation_id=correlation_id,
            )
        except Exception as e:
            logger.error(f"Erro ao auditar erro de ação: {e}")
