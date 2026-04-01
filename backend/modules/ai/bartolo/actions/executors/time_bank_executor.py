"""
Executor de acoes relacionadas a banco de horas.

Gerencia aprovacao de hora extra, solicitacao de compensacao
e consulta de saldo via sistema de acoes do Bartolo.
"""

import logging
from datetime import datetime
from uuid import uuid4

from modules.operacional.models.time_bank import TimeBankEntryType, TimeBankStatus
from modules.operacional.permissions import Permission, has_permission
from modules.operacional.repositories.time_bank_repository import TimeBankRepository
from modules.operacional.schemas.time_bank import TimeBankCreate

from ..action_schemas import ActionPreview, ActionRequest, ActionResult
from ..action_types import ActionStatus
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)

# Constantes locais de action types para banco de horas
# Serao integrados no ActionType enum posteriormente
TIMEBANK_APPROVE_OVERTIME = "approve_overtime"
TIMEBANK_REQUEST_COMPENSATION = "request_compensation"
TIMEBANK_VIEW_BALANCE = "view_balance"

# Mapeamento de action type para permissao
TIMEBANK_PERMISSIONS = {
    TIMEBANK_APPROVE_OVERTIME: Permission.TIMEBANK_APPROVE,
    TIMEBANK_REQUEST_COMPENSATION: Permission.TIMEBANK_CREATE,
    TIMEBANK_VIEW_BALANCE: Permission.TIMEBANK_VIEW_ALL,
}


class TimeBankActionExecutor(BaseActionExecutor):
    """Executor para acoes de banco de horas."""

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para acao de banco de horas."""
        action_type_value = (
            request.action_type.value if hasattr(request.action_type, "value") else str(request.action_type)
        )

        if action_type_value == TIMEBANK_APPROVE_OVERTIME:
            return await self._approve_overtime_preview(request)
        elif action_type_value == TIMEBANK_REQUEST_COMPENSATION:
            return await self._request_compensation_preview(request)
        elif action_type_value == TIMEBANK_VIEW_BALANCE:
            return await self._view_balance_preview(request)
        else:
            raise ValueError(f"Acao nao suportada: {action_type_value}")

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa acao de banco de horas."""
        action_type_value = (
            request.action_type.value if hasattr(request.action_type, "value") else str(request.action_type)
        )
        started_at = datetime.utcnow()

        try:
            if action_type_value == TIMEBANK_APPROVE_OVERTIME:
                result = await self._execute_approve_overtime(request, action_id, started_at)
            elif action_type_value == TIMEBANK_REQUEST_COMPENSATION:
                result = await self._execute_request_compensation(request, action_id, started_at)
            elif action_type_value == TIMEBANK_VIEW_BALANCE:
                result = await self._execute_view_balance(request, action_id, started_at)
            else:
                raise ValueError(f"Acao nao suportada: {action_type_value}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar acao {action_type_value}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=request.action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar acao: {action_type_value}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # =========================================================================
    # PREVIEW METHODS
    # =========================================================================

    async def _approve_overtime_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para aprovacao de hora extra."""
        params = request.parameters
        entry_id = params.get("entry_id") or params.get("id")

        warnings = []
        affected_entities = []
        changes_summary = []

        repo = TimeBankRepository(self.db)
        entry = None

        if entry_id:
            entry = await repo.get_by_id(entry_id)

        if not entry:
            warnings.append("Registro de hora extra nao encontrado")
            title = "Aprovar Hora Extra"
            description = "Registro nao encontrado"
        else:
            affected_entities.append(
                {
                    "type": "time_bank",
                    "id": entry.id,
                    "employee_id": entry.employee_id,
                }
            )

            ref_date = entry.reference_date.strftime("%d/%m/%Y") if entry.reference_date else "N/A"
            changes_summary.append(f"Funcionario: {entry.employee_id}")
            changes_summary.append(f"Horas: {entry.hours:.1f}h")
            changes_summary.append(f"Data referencia: {ref_date}")
            changes_summary.append(f"Status atual: {entry.status}")
            changes_summary.append(f"Novo status: {TimeBankStatus.APPROVED.value}")

            if entry.status != TimeBankStatus.PENDING.value:
                warnings.append(f"Registro nao esta pendente (status atual: {entry.status})")

            if entry.hours > 10:
                warnings.append(f"Quantidade de horas acima de 10h ({entry.hours:.1f}h) - verificar necessidade")

            title = f"Aprovar Hora Extra - {entry.hours:.1f}h"
            description = f"Aprovar {entry.hours:.1f}h extras do funcionario {entry.employee_id}"

        # Verificar permissao
        required_perm = TIMEBANK_PERMISSIONS[TIMEBANK_APPROVE_OVERTIME]
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissao {required_perm.value}: role={user_role}, has_perm={user_has_perm}")

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _request_compensation_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para solicitacao de compensacao."""
        params = request.parameters
        employee_id = params.get("employee_id")
        hours = params.get("hours", 0)
        compensation_date = params.get("compensation_date")

        warnings = []
        affected_entities = []
        changes_summary = []

        if not employee_id:
            warnings.append("ID do funcionario nao informado")

        if not hours or hours <= 0:
            warnings.append("Quantidade de horas nao informada ou invalida")

        if not compensation_date:
            warnings.append("Data da compensacao nao informada")

        # Verificar saldo do funcionario
        if employee_id:
            repo = TimeBankRepository(self.db)
            try:
                summary = await repo.get_summary(employee_id)
                current_balance = summary.current_balance

                affected_entities.append(
                    {
                        "type": "employee",
                        "id": employee_id,
                        "current_balance": current_balance,
                    }
                )

                changes_summary.append(f"Funcionario: {employee_id}")
                changes_summary.append(f"Saldo atual: {current_balance:+.1f}h")
                changes_summary.append(f"Horas a compensar: {hours:.1f}h")
                changes_summary.append(f"Saldo apos compensacao: {current_balance - hours:+.1f}h")

                if hours > current_balance:
                    warnings.append(f"Saldo insuficiente! Disponivel: {current_balance:.1f}h, Solicitado: {hours:.1f}h")

                if compensation_date:
                    changes_summary.append(f"Data da compensacao: {compensation_date}")

            except Exception as e:
                logger.warning(f"Erro ao verificar saldo: {e}")
                warnings.append("Nao foi possivel verificar o saldo atual")
                changes_summary.append(f"Funcionario: {employee_id}")
                changes_summary.append(f"Horas a compensar: {hours:.1f}h")

        title = f"Solicitar Compensacao - {hours:.1f}h"
        description = f"Solicitar compensacao de {hours:.1f}h para funcionario {employee_id or 'N/A'}"

        # Verificar permissao
        required_perm = TIMEBANK_PERMISSIONS[TIMEBANK_REQUEST_COMPENSATION]
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissao {required_perm.value}: role={user_role}, has_perm={user_has_perm}")

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _view_balance_preview(self, request: ActionRequest) -> ActionPreview:
        """
        Cria preview para consulta de saldo (read-only, sem confirmacao).

        Esta acao e apenas leitura, nao requer confirmacao do usuario.
        """
        params = request.parameters
        employee_id = params.get("employee_id")

        warnings = []
        affected_entities = []
        changes_summary = []

        if not employee_id:
            warnings.append("ID do funcionario nao informado")

        if employee_id:
            affected_entities.append(
                {
                    "type": "employee",
                    "id": employee_id,
                }
            )
            changes_summary.append(f"Consulta de saldo para: {employee_id}")

        # Verificar permissao
        required_perm = TIMEBANK_PERMISSIONS[TIMEBANK_VIEW_BALANCE]
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissao {required_perm.value}: role={user_role}, has_perm={user_has_perm}")

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title="Consultar Saldo - Banco de Horas",
            description=f"Consultar saldo do funcionario {employee_id or 'N/A'}",
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=False,  # Read-only, sem confirmacao
        )

    # =========================================================================
    # EXECUTE METHODS
    # =========================================================================

    async def _execute_approve_overtime(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa aprovacao de hora extra."""
        params = request.parameters
        entry_id = params.get("entry_id") or params.get("id")
        notes = params.get("notes")

        if not entry_id:
            raise ValueError("ID do registro de hora extra nao informado")

        repo = TimeBankRepository(self.db)
        entry = await repo.get_by_id(entry_id)

        if not entry:
            raise ValueError(f"Registro '{entry_id}' nao encontrado")

        if entry.status != TimeBankStatus.PENDING.value:
            raise ValueError(f"Registro nao esta pendente. Status atual: {entry.status}")

        # Usar UUID real do usuario
        user_uuid = getattr(self, "user_uuid", None)

        # Aprovar via repository
        approved_entry = await repo.approve(
            time_bank_id=entry.id,
            approved_by=user_uuid or "system",
            notes=notes,
        )

        if not approved_entry:
            raise ValueError(f"Nao foi possivel aprovar o registro. Status atual: {entry.status}")

        logger.info(f"Hora extra aprovada via Bartolo: {approved_entry.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Hora extra aprovada com sucesso ({approved_entry.hours:.1f}h)",
            details={
                "entry_id": approved_entry.id,
                "employee_id": approved_entry.employee_id,
                "hours": approved_entry.hours,
                "status": approved_entry.status,
                "balance_before": approved_entry.balance_before,
                "balance_after": approved_entry.balance_after,
                "approved_by": user_uuid,
                "approved_at": approved_entry.approved_at.isoformat() if approved_entry.approved_at else None,
            },
            affected_entities=[
                {"type": "time_bank", "id": approved_entry.id},
                {"type": "employee", "id": approved_entry.employee_id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_request_compensation(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa solicitacao de compensacao de horas."""
        params = request.parameters
        employee_id = params.get("employee_id")
        hours = params.get("hours")
        compensation_date_str = params.get("compensation_date")
        reason = params.get("reason", "Compensacao de horas via Bartolo")

        if not employee_id:
            raise ValueError("ID do funcionario nao informado")
        if not hours or hours <= 0:
            raise ValueError("Quantidade de horas invalida")

        repo = TimeBankRepository(self.db)

        # Verificar saldo
        summary = await repo.get_summary(employee_id)
        if hours > summary.current_balance:
            raise ValueError(
                f"Saldo insuficiente. Disponivel: {summary.current_balance:.1f}h, Solicitado: {hours:.1f}h"
            )

        # Criar entrada de compensacao
        from datetime import date as date_type

        if compensation_date_str:
            try:
                # Tentar dd/mm/yyyy
                parts = compensation_date_str.split("/")
                if len(parts) == 3:
                    ref_date = date_type(int(parts[2]), int(parts[1]), int(parts[0]))
                else:
                    ref_date = date_type.today()
            except (ValueError, IndexError):
                ref_date = date_type.today()
        else:
            ref_date = date_type.today()

        create_data = TimeBankCreate(
            employee_id=employee_id,
            entry_type=TimeBankEntryType.COMPENSATION,
            hours=abs(hours),
            reference_date=ref_date,
            description=f"Compensacao solicitada via Bartolo - {reason}",
            reason=reason,
        )

        user_uuid = getattr(self, "user_uuid", None)
        new_entry = await repo.create(create_data, created_by=user_uuid)

        logger.info(f"Compensacao solicitada via Bartolo: {new_entry.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Compensacao de {hours:.1f}h solicitada com sucesso",
            details={
                "entry_id": new_entry.id,
                "employee_id": new_entry.employee_id,
                "hours": new_entry.hours,
                "compensation_date": ref_date.isoformat(),
                "status": new_entry.status,
                "balance_before": summary.current_balance,
                "balance_after_approval": summary.current_balance - hours,
                "created_by": user_uuid,
            },
            affected_entities=[
                {"type": "time_bank", "id": new_entry.id},
                {"type": "employee", "id": new_entry.employee_id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_view_balance(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa consulta de saldo (read-only)."""
        params = request.parameters
        employee_id = params.get("employee_id")

        if not employee_id:
            raise ValueError("ID do funcionario nao informado")

        repo = TimeBankRepository(self.db)
        summary = await repo.get_summary(employee_id)

        logger.info(f"Saldo consultado via Bartolo: {employee_id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Saldo atual: {summary.current_balance:+.1f}h",
            details={
                "employee_id": employee_id,
                "current_balance": summary.current_balance,
                "total_credit": summary.total_credit,
                "total_debit": summary.total_debit,
                "total_compensated": summary.total_compensated,
                "total_expired": summary.total_expired,
                "pending_approval": summary.pending_approval,
                "expiring_soon": summary.expiring_soon,
                "entries_count": summary.entries_count,
            },
            affected_entities=[
                {"type": "employee", "id": employee_id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
