"""
Executor de acoes relacionadas a medidas disciplinares.

Acoes:
- CREATE_DISCIPLINARY: Criar acao disciplinar
- APPROVE_DISCIPLINARY: Aprovar acao disciplinar
- REJECT_DISCIPLINARY: Rejeitar acao disciplinar

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from datetime import date, datetime
from uuid import uuid4

from modules.operacional.disciplinary.models.disciplinary_action import (
    DisciplinaryActionStatus,
    DisciplinaryActionType,
)
from modules.operacional.disciplinary.repositories.disciplinary_repository import DisciplinaryRepository
from modules.operacional.disciplinary.schemas import (
    ApproveRequest,
    DisciplinaryActionCreate,
    ReasonCategory,
    RejectRequest,
)
from modules.operacional.disciplinary.services.disciplinary_service import DisciplinaryService

from ..action_schemas import ActionPreview, ActionRequest, ActionResult
from ..action_types import ActionStatus
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class DisciplinaryActionExecutor(BaseActionExecutor):
    """Executor para acoes disciplinares."""

    # Mapeamento de action types disciplinares
    # Nota: Estes tipos devem ser adicionados ao ActionType enum
    # em action_types.py quando este executor for registrado.
    # Por ora, usamos strings para as acoes disciplinares.
    ACTION_CREATE = "create_disciplinary"
    ACTION_APPROVE = "approve_disciplinary"
    ACTION_REJECT = "reject_disciplinary"

    TIPO_DISPLAY = {
        "advertencia_verbal": "Advertencia Verbal",
        "advertencia_escrita": "Advertencia Escrita",
        "suspensao": "Suspensao",
        "demissao_justa_causa": "Demissao por Justa Causa",
    }

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para acao disciplinar."""
        action_type_str = (
            request.action_type.value if hasattr(request.action_type, "value") else str(request.action_type)
        )

        try:
            if action_type_str == self.ACTION_CREATE:
                return await self._create_disciplinary_preview(request)
            elif action_type_str == self.ACTION_APPROVE:
                return await self._approve_disciplinary_preview(request)
            elif action_type_str == self.ACTION_REJECT:
                return await self._reject_disciplinary_preview(request)
            else:
                raise ValueError(f"Acao disciplinar nao suportada: {action_type_str}")
        except Exception as e:
            logger.error(f"Erro ao criar preview disciplinar: {e}")
            return ActionPreview(
                action_id=str(uuid4()),
                action_type=request.action_type,
                title="Erro ao criar preview",
                description=str(e),
                affected_entities=[],
                changes_summary=[],
                warnings=[f"Erro: {e}"],
                required_permission="disciplinary:create",
                user_has_permission=False,
                parameters=request.parameters,
                can_be_undone=False,
                requires_confirmation=True,
            )

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa acao disciplinar."""
        action_type_str = (
            request.action_type.value if hasattr(request.action_type, "value") else str(request.action_type)
        )
        started_at = datetime.utcnow()

        try:
            if action_type_str == self.ACTION_CREATE:
                result = await self._execute_create_disciplinary(request, action_id, started_at)
            elif action_type_str == self.ACTION_APPROVE:
                result = await self._execute_approve_disciplinary(request, action_id, started_at)
            elif action_type_str == self.ACTION_REJECT:
                result = await self._execute_reject_disciplinary(request, action_id, started_at)
            else:
                raise ValueError(f"Acao disciplinar nao suportada: {action_type_str}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar acao disciplinar {action_type_str}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=request.action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar acao disciplinar: {action_type_str}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # ==========================================================================
    # CREATE DISCIPLINARY
    # ==========================================================================

    async def _create_disciplinary_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criacao de medida disciplinar."""
        params = request.parameters
        action_type = params.get("action_type", "advertencia_escrita")
        employee_name = params.get("employee_name", "N/A")
        employee_id = params.get("employee_id")
        reason_description = params.get("reason_description", "N/A")
        reason_category = params.get("reason_category", "outros")
        incident_date_str = params.get("incident_date")
        suspension_days = params.get("suspension_days")

        tipo_display = self.TIPO_DISPLAY.get(action_type, action_type)

        changes_summary = [
            f"Tipo: {tipo_display}",
            f"Funcionario: {employee_name}",
            f"Motivo: {reason_category.replace('_', ' ').title()}",
            f"Descricao: {reason_description[:80]}{'...' if len(reason_description) > 80 else ''}",
        ]

        if incident_date_str:
            changes_summary.append(f"Data do incidente: {incident_date_str}")

        if suspension_days and action_type == "suspensao":
            changes_summary.append(f"Dias de suspensao: {suspension_days}")

        warnings = []
        affected_entities = []

        # Validacoes de preview
        if employee_id:
            affected_entities.append(
                {
                    "type": "employee",
                    "id": employee_id,
                    "name": employee_name,
                }
            )

            # Buscar historico do funcionario
            try:
                repo = DisciplinaryRepository(self.db)
                tenant_id = params.get("tenant_id", "")
                if tenant_id:
                    history = await repo.get_by_employee(employee_id, tenant_id)
                    applied = [h for h in history if h.status == DisciplinaryActionStatus.APLICADA.value]
                    adv_count = sum(
                        1
                        for h in applied
                        if h.action_type
                        in [
                            DisciplinaryActionType.ADVERTENCIA_VERBAL.value,
                            DisciplinaryActionType.ADVERTENCIA_ESCRITA.value,
                        ]
                    )
                    sus_count = sum(1 for h in applied if h.action_type == DisciplinaryActionType.SUSPENSAO.value)

                    changes_summary.append(f"Advertencias anteriores: {adv_count}")
                    changes_summary.append(f"Suspensoes anteriores: {sus_count}")

                    # Alertas de proporcionalidade
                    if action_type == "suspensao" and adv_count == 0:
                        warnings.append("Suspensao sem advertencia previa - risco de reversao judicial")
                    if action_type == "demissao_justa_causa" and sus_count == 0 and adv_count == 0:
                        warnings.append("Justa causa sem medidas previas - alto risco de reversao judicial")
            except Exception as e:
                logger.warning(f"Erro ao buscar historico para preview: {e}")

        # Validar imediaticidade
        if incident_date_str:
            try:
                incident_date = (
                    date.fromisoformat(incident_date_str) if isinstance(incident_date_str, str) else incident_date_str
                )
                days_since = (date.today() - incident_date).days
                if days_since > 30:
                    warnings.append(f"Imediaticidade: {days_since} dias desde o incidente (recomendado max 30)")
            except (ValueError, TypeError):
                pass

        # Validar suspensao
        if action_type == "suspensao" and suspension_days:
            if int(suspension_days) > 30:
                warnings.append(f"Suspensao de {suspension_days} dias excede limite CLT de 30 dias (Art. 474)")

        title = f"Criar {tipo_display}"
        description = f"Criar medida disciplinar ({tipo_display}) para {employee_name}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="disciplinary:create",
            user_has_permission=True,  # Verificar via sistema de permissoes
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _execute_create_disciplinary(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criacao de medida disciplinar."""
        params = request.parameters
        tenant_id = params.get("tenant_id", "")
        user_uuid = getattr(self, "user_uuid", None)

        # Usar DisciplinaryService para criacao completa com validacoes
        service = DisciplinaryService(self.db)

        # Montar dados para criacao
        action_type_str = params.get("action_type", "advertencia_escrita")
        incident_date_str = params.get("incident_date", date.today().isoformat())

        try:
            incident_date = (
                date.fromisoformat(incident_date_str) if isinstance(incident_date_str, str) else incident_date_str
            )
        except (ValueError, TypeError):
            incident_date = date.today()

        create_data = DisciplinaryActionCreate(
            action_type=DisciplinaryActionType(action_type_str),
            employee_id=params.get("employee_id", ""),
            employee_name=params.get("employee_name", ""),
            employee_cpf=params.get("employee_cpf", "00000000000"),
            employee_position=params.get("employee_position"),
            employee_admission_date=params.get("employee_admission_date"),
            reason_category=ReasonCategory(params.get("reason_category", "outros")),
            reason_description=params.get("reason_description", ""),
            incident_date=incident_date,
            occurrence_id=params.get("occurrence_id"),
            post_id=params.get("post_id"),
            client_id=params.get("client_id"),
            suspension_days=params.get("suspension_days"),
            suspension_start_date=params.get("suspension_start_date"),
            suspension_end_date=params.get("suspension_end_date"),
            requires_approval=params.get("requires_approval", True),
        )

        action = await service.create(create_data, tenant_id, user_uuid or "")

        tipo_display = self.TIPO_DISPLAY.get(action.action_type, action.action_type)

        logger.info(f"Medida disciplinar criada via Bartolo: {action.code}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Medida disciplinar criada com sucesso: {action.code}",
            details={
                "disciplinary_id": action.id,
                "code": action.code,
                "action_type": action.action_type,
                "type_display": tipo_display,
                "employee_name": action.employee_name,
                "status": action.status,
                "incident_date": str(action.incident_date),
            },
            affected_entities=[
                {"type": "disciplinary_action", "id": action.id, "code": action.code},
                {"type": "employee", "id": action.employee_id, "name": action.employee_name},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==========================================================================
    # APPROVE DISCIPLINARY
    # ==========================================================================

    async def _approve_disciplinary_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para aprovacao de medida disciplinar."""
        params = request.parameters
        code = params.get("code")
        action_id_param = params.get("action_id")
        tenant_id = params.get("tenant_id", "")

        warnings = []
        affected_entities = []
        changes_summary = []

        repo = DisciplinaryRepository(self.db)
        action = None

        try:
            if code and tenant_id:
                action = await repo.get_by_code(code, tenant_id)
            elif action_id_param and tenant_id:
                action = await repo.get_by_id(action_id_param, tenant_id)
        except Exception as e:
            logger.warning(f"Erro ao buscar medida para preview de aprovacao: {e}")

        if not action:
            warnings.append("Medida disciplinar nao encontrada")
            title = "Aprovar Medida Disciplinar"
            description = "Medida nao encontrada"
        else:
            tipo_display = self.TIPO_DISPLAY.get(action.action_type, action.action_type)
            affected_entities.append(
                {
                    "type": "disciplinary_action",
                    "id": action.id,
                    "code": action.code,
                }
            )

            changes_summary.append(f"Medida: {action.code}")
            changes_summary.append(f"Tipo: {tipo_display}")
            changes_summary.append(f"Funcionario: {action.employee_name}")
            changes_summary.append(f"Status atual: {action.status_display_name}")
            changes_summary.append("Novo status: Pendente Assinatura")

            if not action.can_be_approved:
                warnings.append(f"Medida nao pode ser aprovada no status atual ({action.status_display_name})")

            if action.status == DisciplinaryActionStatus.APROVADA.value:
                warnings.append("Medida ja esta aprovada")

            title = f"Aprovar Medida - {action.code}"
            description = f"Aprovar {tipo_display} para {action.employee_name}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="disciplinary:approve",
            user_has_permission=True,  # Verificar via sistema de permissoes
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _execute_approve_disciplinary(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa aprovacao de medida disciplinar."""
        params = request.parameters
        code = params.get("code")
        action_id_param = params.get("action_id")
        tenant_id = params.get("tenant_id", "")
        notes = params.get("notes")
        user_uuid = getattr(self, "user_uuid", None)

        service = DisciplinaryService(self.db)

        # Buscar medida
        if code:
            disc_action = await service.get_by_code(code, tenant_id)
        elif action_id_param:
            disc_action = await service.get_by_id(action_id_param, tenant_id)
        else:
            raise ValueError("Codigo ou ID da medida e obrigatorio")

        # Aprovar
        approve_request = ApproveRequest(
            notes=notes,
            application_date=date.today(),
        )
        approved = await service.approve(disc_action.id, tenant_id, user_uuid or "", approve_request)

        logger.info(f"Medida disciplinar aprovada via Bartolo: {approved.code}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Medida {approved.code} aprovada com sucesso",
            details={
                "disciplinary_id": approved.id,
                "code": approved.code,
                "status": approved.status,
                "approved_by": user_uuid,
                "approved_at": approved.approved_at.isoformat() if approved.approved_at else None,
            },
            affected_entities=[
                {"type": "disciplinary_action", "id": approved.id, "code": approved.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==========================================================================
    # REJECT DISCIPLINARY
    # ==========================================================================

    async def _reject_disciplinary_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para rejeicao de medida disciplinar."""
        params = request.parameters
        code = params.get("code")
        action_id_param = params.get("action_id")
        tenant_id = params.get("tenant_id", "")
        rejection_reason = params.get("reason", "")

        warnings = []
        affected_entities = []
        changes_summary = []

        repo = DisciplinaryRepository(self.db)
        action = None

        try:
            if code and tenant_id:
                action = await repo.get_by_code(code, tenant_id)
            elif action_id_param and tenant_id:
                action = await repo.get_by_id(action_id_param, tenant_id)
        except Exception as e:
            logger.warning(f"Erro ao buscar medida para preview de rejeicao: {e}")

        if not action:
            warnings.append("Medida disciplinar nao encontrada")
            title = "Rejeitar Medida Disciplinar"
            description = "Medida nao encontrada"
        else:
            tipo_display = self.TIPO_DISPLAY.get(action.action_type, action.action_type)
            affected_entities.append(
                {
                    "type": "disciplinary_action",
                    "id": action.id,
                    "code": action.code,
                }
            )

            changes_summary.append(f"Medida: {action.code}")
            changes_summary.append(f"Tipo: {tipo_display}")
            changes_summary.append(f"Funcionario: {action.employee_name}")
            changes_summary.append(f"Status atual: {action.status_display_name}")
            changes_summary.append("Novo status: Rejeitada")

            if rejection_reason:
                changes_summary.append(f"Motivo rejeicao: {rejection_reason}")

            if not action.can_be_approved:
                warnings.append(f"Medida nao pode ser rejeitada no status atual ({action.status_display_name})")

            if not rejection_reason:
                warnings.append("Motivo de rejeicao e obrigatorio")

            title = f"Rejeitar Medida - {action.code}"
            description = f"Rejeitar {tipo_display} para {action.employee_name}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="disciplinary:approve",
            user_has_permission=True,  # Verificar via sistema de permissoes
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _execute_reject_disciplinary(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa rejeicao de medida disciplinar."""
        params = request.parameters
        code = params.get("code")
        action_id_param = params.get("action_id")
        tenant_id = params.get("tenant_id", "")
        reason = params.get("reason", "")
        user_uuid = getattr(self, "user_uuid", None)

        if not reason:
            raise ValueError("Motivo de rejeicao e obrigatorio")

        service = DisciplinaryService(self.db)

        # Buscar medida
        if code:
            disc_action = await service.get_by_code(code, tenant_id)
        elif action_id_param:
            disc_action = await service.get_by_id(action_id_param, tenant_id)
        else:
            raise ValueError("Codigo ou ID da medida e obrigatorio")

        # Rejeitar
        reject_request = RejectRequest(reason=reason)
        rejected = await service.reject(disc_action.id, tenant_id, user_uuid or "", reject_request)

        logger.info(f"Medida disciplinar rejeitada via Bartolo: {rejected.code}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Medida {rejected.code} rejeitada",
            details={
                "disciplinary_id": rejected.id,
                "code": rejected.code,
                "status": rejected.status,
                "rejected_by": user_uuid,
                "rejected_at": rejected.rejected_at.isoformat() if rejected.rejected_at else None,
                "rejection_reason": reason,
            },
            affected_entities=[
                {"type": "disciplinary_action", "id": rejected.id, "code": rejected.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
