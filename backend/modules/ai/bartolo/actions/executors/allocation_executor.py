"""
Executor de ações relacionadas a alocações.
"""
import logging
from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import select

from modules.operacional.repositories.allocation_repository import AllocationRepository
from modules.operacional.repositories.post_repository import PostRepository
from modules.operacional.models.allocation import AllocationStatus
from modules.operacional.models.employee import Employee
from modules.operacional.schemas.allocation import AllocationCreate
from modules.operacional.permissions import has_permission
from ..action_schemas import ActionRequest, ActionPreview, ActionResult
from ..action_types import ActionType, ActionStatus
from ..action_permissions import get_required_permission
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class AllocationActionExecutor(BaseActionExecutor):
    """Executor para ações de alocação."""

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para ação de alocação."""
        action_type = request.action_type

        if action_type == ActionType.ALLOCATE_EMPLOYEE:
            return await self._allocate_preview(request)
        elif action_type == ActionType.TERMINATE_ALLOCATION:
            return await self._terminate_preview(request)
        elif action_type == ActionType.TRANSFER_EMPLOYEE:
            return await self._transfer_preview(request)
        else:
            raise ValueError(f"Ação não suportada: {action_type.value}")

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa ação de alocação."""
        action_type = request.action_type
        started_at = datetime.utcnow()

        try:
            if action_type == ActionType.ALLOCATE_EMPLOYEE:
                result = await self._execute_allocate(request, action_id, started_at)
            elif action_type == ActionType.TERMINATE_ALLOCATION:
                result = await self._execute_terminate(request, action_id, started_at)
            elif action_type == ActionType.TRANSFER_EMPLOYEE:
                result = await self._execute_transfer(request, action_id, started_at)
            else:
                raise ValueError(f"Ação não suportada: {action_type.value}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar ação {action_type.value}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar ação: {action_type.value}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # ── Helpers ──────────────────────────────────────────────────────────

    async def _get_employee(self, employee_id: str) -> Optional[Employee]:
        """Busca funcionário por ID."""
        result = await self.db.execute(
            select(Employee).where(
                Employee.id == employee_id,
                Employee.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    def _build_permission_info(self, request: ActionRequest) -> tuple:
        """Retorna (required_perm, user_has_perm)."""
        required_perm = get_required_permission(request.action_type)
        user_role = getattr(self, 'user_role', None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissão {required_perm.value}: role={user_role}, has_perm={user_has_perm}")
        return required_perm, user_has_perm

    # ── Previews ─────────────────────────────────────────────────────────

    async def _allocate_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para alocação de funcionário."""
        params = request.parameters
        employee_id = params.get('employee_id')
        post_code = params.get('post_code')
        start_date_str = params.get('start_date')
        role = params.get('role')

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar funcionário
        employee = await self._get_employee(employee_id) if employee_id else None
        if not employee:
            warnings.append("⚠️ Funcionário não encontrado")
        else:
            affected_entities.append({
                "type": "employee",
                "id": str(employee.id),
                "name": employee.nome,
                "matricula": employee.matricula,
            })
            changes_summary.append(f"Funcionário: {employee.nome} ({employee.matricula or 'sem matrícula'})")

            # Verificar alocações atuais
            alloc_repo = AllocationRepository(self.db)
            current_allocs = await alloc_repo.get_current_by_employee(str(employee.id))
            if current_allocs:
                warnings.append(
                    f"⚠️ Funcionário já possui {len(current_allocs)} alocação(ões) ativa(s)"
                )

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = await post_repo.get_by_code(post_code) if post_code else None
        if not post:
            warnings.append(f"⚠️ Posto '{post_code}' não encontrado")
        else:
            affected_entities.append({
                "type": "post",
                "id": post.id,
                "name": post.name,
                "code": post.code,
            })
            changes_summary.append(f"Posto: {post.code} - {post.name}")

        # Data de início
        if start_date_str:
            changes_summary.append(f"Início: {start_date_str}")
        else:
            changes_summary.append(f"Início: {date.today().isoformat()} (hoje)")

        if role:
            changes_summary.append(f"Função: {role}")

        title = "Alocar Funcionário"
        description = "Criar nova alocação de funcionário em posto"
        if employee and post:
            title = f"Alocar {employee.nome} - {post.code}"
            description = f"Alocar {employee.nome} no posto {post.name}"

        required_perm, user_has_perm = self._build_permission_info(request)

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

    async def _terminate_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para encerramento de alocação."""
        params = request.parameters
        allocation_id = params.get('allocation_id')
        employee_id = params.get('employee_id')
        reason = params.get('reason', 'Encerramento via Bartolo')

        warnings = []
        affected_entities = []
        changes_summary = []

        alloc_repo = AllocationRepository(self.db)

        # Buscar alocação por ID direto ou pela alocação ativa do funcionário
        allocation = None
        if allocation_id:
            allocation = await alloc_repo.get_by_id(allocation_id)
        elif employee_id:
            current_allocs = await alloc_repo.get_current_by_employee(employee_id)
            if current_allocs:
                allocation = current_allocs[0]  # Pega a primeira alocação ativa

        if not allocation:
            warnings.append("⚠️ Alocação não encontrada")
            title = "Encerrar Alocação"
            description = "Alocação não encontrada"
        else:
            affected_entities.append({
                "type": "allocation",
                "id": str(allocation.id),
                "status": allocation.status,
            })
            changes_summary.append(f"Alocação: {allocation.id}")
            changes_summary.append(f"Status atual: {allocation.status}")
            changes_summary.append(f"Novo status: {AllocationStatus.TERMINATED.value}")
            changes_summary.append(f"Motivo: {reason}")

            if allocation.status == AllocationStatus.TERMINATED.value:
                warnings.append("⚠️ Alocação já está encerrada")

            # Buscar dados do funcionário
            employee = await self._get_employee(str(allocation.employee_id))
            if employee:
                changes_summary.insert(0, f"Funcionário: {employee.nome}")

            title = "Encerrar Alocação"
            description = f"Encerrar alocação {allocation.id}"

        required_perm, user_has_perm = self._build_permission_info(request)

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

    async def _transfer_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para transferência de funcionário."""
        params = request.parameters
        employee_id = params.get('employee_id')
        target_post_code = params.get('post_code') or params.get('target_post_code')

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar funcionário
        employee = await self._get_employee(employee_id) if employee_id else None
        if not employee:
            warnings.append("⚠️ Funcionário não encontrado")
        else:
            affected_entities.append({
                "type": "employee",
                "id": str(employee.id),
                "name": employee.nome,
            })
            changes_summary.append(f"Funcionário: {employee.nome}")

        # Buscar posto destino
        post_repo = PostRepository(self.db)
        target_post = await post_repo.get_by_code(target_post_code) if target_post_code else None
        if not target_post:
            warnings.append(f"⚠️ Posto destino '{target_post_code}' não encontrado")
        else:
            affected_entities.append({
                "type": "post",
                "id": target_post.id,
                "name": target_post.name,
                "code": target_post.code,
            })
            changes_summary.append(f"Posto destino: {target_post.code} - {target_post.name}")

        # Verificar alocação atual
        if employee:
            alloc_repo = AllocationRepository(self.db)
            current_allocs = await alloc_repo.get_current_by_employee(str(employee.id))
            if current_allocs:
                current_post_id = current_allocs[0].post_id
                current_post = await post_repo.get_by_id(current_post_id)
                if current_post:
                    changes_summary.append(f"Posto atual: {current_post.code} - {current_post.name}")
            else:
                warnings.append("⚠️ Funcionário não possui alocação ativa para transferir")

        title = "Transferir Funcionário"
        description = "Transferir funcionário para outro posto"
        if employee and target_post:
            title = f"Transferir {employee.nome} para {target_post.code}"
            description = f"Transferir {employee.nome} para {target_post.name}"

        required_perm, user_has_perm = self._build_permission_info(request)

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

    # ── Execuções ────────────────────────────────────────────────────────

    async def _execute_allocate(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa alocação de funcionário em posto."""
        params = request.parameters
        employee_id = params.get('employee_id')
        post_code = params.get('post_code')
        start_date_str = params.get('start_date')
        end_date_str = params.get('end_date')
        role = params.get('role')
        is_temporary = params.get('is_temporary', False)
        notes = params.get('notes')

        # Buscar funcionário
        employee = await self._get_employee(employee_id)
        if not employee:
            raise ValueError(f"Funcionário '{employee_id}' não encontrado")

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = await post_repo.get_by_code(post_code)
        if not post:
            raise ValueError(f"Posto '{post_code}' não encontrado")

        # Preparar datas
        start_dt = (
            date.fromisoformat(start_date_str) if start_date_str else date.today()
        )
        end_dt = date.fromisoformat(end_date_str) if end_date_str else None

        # Criar alocação
        alloc_data = AllocationCreate(
            post_id=post.id,
            employee_id=str(employee.id),
            start_date=start_dt,
            end_date=end_dt,
            is_primary=True,
            is_temporary=is_temporary,
            role=role,
            notes=notes,
        )

        alloc_repo = AllocationRepository(self.db)
        user_uuid = getattr(self, 'user_uuid', None)
        allocation = await alloc_repo.create(alloc_data, created_by=user_uuid)

        logger.info(f"Alocação criada via Bartolo: {allocation.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Funcionário alocado com sucesso",
            details={
                "allocation_id": allocation.id,
                "employee_id": str(employee.id),
                "employee_name": employee.nome,
                "post_id": post.id,
                "post_code": post.code,
                "post_name": post.name,
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat() if end_dt else None,
                "status": allocation.status,
            },
            affected_entities=[
                {"type": "allocation", "id": allocation.id},
                {"type": "employee", "id": str(employee.id)},
                {"type": "post", "id": post.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_terminate(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa encerramento de alocação."""
        params = request.parameters
        allocation_id = params.get('allocation_id')
        employee_id = params.get('employee_id')
        reason = params.get('reason', 'Encerramento via Bartolo')
        end_date_str = params.get('end_date')
        notes = params.get('notes')

        alloc_repo = AllocationRepository(self.db)

        # Buscar alocação
        allocation = None
        if allocation_id:
            allocation = await alloc_repo.get_by_id(allocation_id)
        elif employee_id:
            current_allocs = await alloc_repo.get_current_by_employee(employee_id)
            if current_allocs:
                allocation = current_allocs[0]

        if not allocation:
            raise ValueError("Alocação não encontrada")

        if allocation.status == AllocationStatus.TERMINATED.value:
            raise ValueError("Alocação já está encerrada")

        # Data de encerramento
        end_dt = date.fromisoformat(end_date_str) if end_date_str else date.today()

        # Encerrar via repository
        terminated = await alloc_repo.terminate(
            allocation_id=allocation.id,
            end_date=end_dt,
            reason=reason,
            notes=notes,
        )

        if not terminated:
            raise ValueError("Não foi possível encerrar a alocação")

        logger.info(f"Alocação encerrada via Bartolo: {terminated.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Alocação encerrada com sucesso",
            details={
                "allocation_id": terminated.id,
                "employee_id": str(terminated.employee_id),
                "post_id": str(terminated.post_id),
                "end_date": end_dt.isoformat(),
                "reason": reason,
                "status": terminated.status,
            },
            affected_entities=[
                {"type": "allocation", "id": terminated.id},
                {"type": "employee", "id": str(terminated.employee_id)},
                {"type": "post", "id": str(terminated.post_id)},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_transfer(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa transferência de funcionário entre postos."""
        params = request.parameters
        employee_id = params.get('employee_id')
        target_post_code = params.get('post_code') or params.get('target_post_code')
        notes = params.get('notes')

        # Buscar funcionário
        employee = await self._get_employee(employee_id)
        if not employee:
            raise ValueError(f"Funcionário '{employee_id}' não encontrado")

        # Buscar posto destino
        post_repo = PostRepository(self.db)
        target_post = await post_repo.get_by_code(target_post_code)
        if not target_post:
            raise ValueError(f"Posto destino '{target_post_code}' não encontrado")

        # Buscar alocação atual
        alloc_repo = AllocationRepository(self.db)
        current_allocs = await alloc_repo.get_current_by_employee(str(employee.id))
        if not current_allocs:
            raise ValueError("Funcionário não possui alocação ativa para transferir")

        old_allocation = current_allocs[0]
        old_post_id = old_allocation.post_id
        today = date.today()

        # 1. Encerrar alocação atual
        await alloc_repo.terminate(
            allocation_id=old_allocation.id,
            end_date=today,
            reason="Transferência via Bartolo",
            notes=notes,
        )

        # 2. Criar nova alocação no posto destino
        new_alloc_data = AllocationCreate(
            post_id=target_post.id,
            employee_id=str(employee.id),
            start_date=today,
            is_primary=old_allocation.is_primary,
            is_temporary=old_allocation.is_temporary,
            hourly_rate=old_allocation.hourly_rate,
            monthly_salary=old_allocation.monthly_salary,
            additional_benefits=old_allocation.additional_benefits,
            role=old_allocation.role,
            notes=f"Transferido de {old_post_id}. {notes or ''}".strip(),
        )

        user_uuid = getattr(self, 'user_uuid', None)
        new_allocation = await alloc_repo.create(new_alloc_data, created_by=user_uuid)

        logger.info(
            f"Transferência via Bartolo: {employee.nome} de {old_post_id} "
            f"para {target_post.id}"
        )

        # Buscar nome do posto anterior para detalhes
        old_post = await post_repo.get_by_id(old_post_id)

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Funcionário transferido com sucesso para {target_post.name}",
            details={
                "employee_id": str(employee.id),
                "employee_name": employee.nome,
                "old_allocation_id": old_allocation.id,
                "old_post_id": old_post_id,
                "old_post_code": old_post.code if old_post else None,
                "old_post_name": old_post.name if old_post else None,
                "new_allocation_id": new_allocation.id,
                "new_post_id": target_post.id,
                "new_post_code": target_post.code,
                "new_post_name": target_post.name,
                "transfer_date": today.isoformat(),
            },
            affected_entities=[
                {"type": "allocation", "id": old_allocation.id},
                {"type": "allocation", "id": new_allocation.id},
                {"type": "employee", "id": str(employee.id)},
                {"type": "post", "id": old_post_id},
                {"type": "post", "id": target_post.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
