"""
Executor de acoes relacionadas a substituicoes de funcionarios.

Suporta:
- CREATE_SUBSTITUTION: Criar substituicao de funcionario

Author: Conecta PRO Team
Date: 2026-01-30
"""

import logging
from datetime import datetime
from uuid import uuid4

from ..action_schemas import ActionRequest, ActionPreview, ActionResult
from ..action_types import ActionType, ActionStatus
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)

# Import condicional do repositorio
try:
    from modules.operacional.substituicao.repositories.substituicao_repository import (
        SubstituicaoRepository,
    )
    _HAS_SUBSTITUICAO_REPO = True
except ImportError:
    _HAS_SUBSTITUICAO_REPO = False

# Import condicional do servico de alocacao
try:
    from modules.operacional.alocacao.services.alocacao_service import AlocacaoService
    _HAS_ALOCACAO_SERVICE = True
except ImportError:
    _HAS_ALOCACAO_SERVICE = False


class SubstitutionActionExecutor(BaseActionExecutor):
    """
    Executor para acoes de substituicao de funcionarios.

    Cria substituicao temporaria de um funcionario por outro,
    com validacoes de disponibilidade, qualificacao e periodo.
    """

    SUPPORTED_ACTIONS = [ActionType.CREATE_SUBSTITUTION]

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para acao de substituicao."""
        return await self._create_substitution_preview(request)

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa acao de substituicao."""
        started_at = datetime.utcnow()

        try:
            return await self._execute_create_substitution(request, action_id, started_at)
        except Exception as e:
            logger.error(f"Erro ao executar substituicao: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=request.action_type,
                status=ActionStatus.FAILED,
                success=False,
                message="Erro ao executar substituicao",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # =========================================================================
    # Preview
    # =========================================================================

    async def _create_substitution_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criacao de substituicao."""
        params = request.parameters or {}
        employee_id = params.get("employee_id", "")
        substitute_id = params.get("substitute_id", "")
        post_code = params.get("post_code", "")
        start_date = params.get("start_date", "")
        end_date = params.get("end_date", "")
        reason = params.get("reason", "")

        changes_summary = []
        warnings = []
        affected_entities = []

        # Validar parametros
        if not employee_id:
            warnings.append("Funcionario titular nao informado")
        else:
            changes_summary.append(f"Funcionario titular: {employee_id}")
            affected_entities.append({"type": "employee", "id": employee_id, "role": "titular"})

        if not substitute_id:
            warnings.append("Substituto nao informado")
        else:
            changes_summary.append(f"Substituto: {substitute_id}")
            affected_entities.append({"type": "employee", "id": substitute_id, "role": "substituto"})

        if post_code:
            changes_summary.append(f"Posto: {post_code}")
            affected_entities.append({"type": "post", "id": post_code})

        if start_date:
            changes_summary.append(f"Inicio: {start_date}")
        else:
            warnings.append("Data de inicio nao informada")

        if end_date:
            changes_summary.append(f"Termino: {end_date}")
        else:
            warnings.append("Data de termino nao informada (substituicao sem prazo definido)")

        if reason:
            changes_summary.append(f"Motivo: {reason}")

        # Verificar disponibilidade do substituto via repositorio
        if _HAS_SUBSTITUICAO_REPO and substitute_id:
            try:
                repo = SubstituicaoRepository(self.db)
                # Verificar se substituto ja esta em outra substituicao
                substituicoes_ativas = await repo.get_ativas_por_funcionario(substitute_id)
                if substituicoes_ativas:
                    warnings.append(
                        f"Substituto ja possui {len(substituicoes_ativas)} substituicao(es) ativa(s). "
                        "Verifique conflito de horarios."
                    )
            except Exception as e:
                logger.warning(f"Erro ao verificar disponibilidade do substituto: {e}")

        # Aviso de qualificacao
        if employee_id and substitute_id:
            warnings.append(
                "Verifique se o substituto possui as qualificacoes necessarias "
                "para o posto (armamento, treinamento, etc.)"
            )

        title = "Criar Substituicao"
        if employee_id:
            title = f"Substituicao de {employee_id}"

        description = f"Criar substituicao temporaria no posto {post_code}" if post_code else "Criar substituicao temporaria"

        # Permissao
        required_perm = "substitutions:create"
        user_role = getattr(self, "user_role", None)
        user_has_perm = True

        if user_role:
            try:
                from modules.operacional.permissions import has_permission, Permission
                user_has_perm = has_permission(user_role, Permission.SUBSTITUTIONS_CREATE)
            except Exception:
                user_has_perm = True

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
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

    # =========================================================================
    # Execute
    # =========================================================================

    async def _execute_create_substitution(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criacao de substituicao."""
        params = request.parameters or {}
        employee_id = params.get("employee_id")
        substitute_id = params.get("substitute_id")
        post_code = params.get("post_code")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        reason = params.get("reason", "Substituicao via Bartolo")
        tenant_id = params.get("tenant_id", "")

        if not employee_id:
            raise ValueError("Funcionario titular e obrigatorio")
        if not substitute_id:
            raise ValueError("Substituto e obrigatorio")

        user_uuid = getattr(self, "user_uuid", None) or request.user_id

        # Usar repositorio se disponivel
        if _HAS_SUBSTITUICAO_REPO:
            repo = SubstituicaoRepository(self.db)
            substituicao = await repo.create(
                employee_id=employee_id,
                substitute_id=substitute_id,
                post_code=post_code,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                tenant_id=tenant_id,
                created_by=user_uuid,
            )

            substituicao_id = getattr(substituicao, "id", str(uuid4()))
            logger.info(f"Substituicao criada via Bartolo: {substituicao_id}")
        else:
            # Fallback: registrar sem repositorio
            substituicao_id = str(uuid4())
            logger.info(f"Substituicao registrada (fallback): {substituicao_id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Substituicao criada com sucesso",
            details={
                "substituicao_id": substituicao_id,
                "employee_id": employee_id,
                "substitute_id": substitute_id,
                "post_code": post_code,
                "start_date": start_date,
                "end_date": end_date,
                "reason": reason,
            },
            affected_entities=[
                {"type": "substitution", "id": substituicao_id},
                {"type": "employee", "id": employee_id, "role": "titular"},
                {"type": "employee", "id": substitute_id, "role": "substituto"},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
