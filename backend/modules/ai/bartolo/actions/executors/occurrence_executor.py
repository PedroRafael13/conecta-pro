"""
Executor de acoes relacionadas a ocorrencias disciplinares.
"""

import contextlib
import logging
from datetime import datetime
from uuid import uuid4

from modules.operacional.occurrences.models import (
    OccurrenceCategory,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from modules.operacional.occurrences.repositories.occurrence_repository import OccurrenceRepository
from modules.operacional.occurrences.schemas import (
    OccurrenceCreate,
    OccurrenceResolve,
    OccurrenceUpdate,
)
from modules.operacional.permissions import Permission, has_permission

from ..action_schemas import ActionPreview, ActionRequest, ActionResult
from ..action_types import ActionStatus, ActionType
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


# Permissoes necessarias para acoes de ocorrencia
# Usa permissoes existentes do sistema operacional
OCCURRENCE_PERMISSIONS = {
    "CREATE_OCCURRENCE": Permission.SHIFTS_MARK_MISSED,  # Inspetor+ pode criar
    "RESOLVE_OCCURRENCE": Permission.SHIFTS_MARK_MISSED,  # Inspetor+ pode resolver
    "UPDATE_OCCURRENCE": Permission.SHIFTS_MARK_MISSED,  # Inspetor+ pode atualizar
}


class OccurrenceActionExecutor(BaseActionExecutor):
    """Executor para acoes de ocorrencia disciplinar."""

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para acao de ocorrencia."""
        action_type = request.action_type

        if action_type == ActionType.CREATE_OCCURRENCE:
            return await self._create_occurrence_preview(request)
        elif action_type == ActionType.RESOLVE_OCCURRENCE:
            return await self._resolve_occurrence_preview(request)
        elif action_type == ActionType.UPDATE_OCCURRENCE:
            return await self._update_occurrence_preview(request)
        else:
            raise ValueError(f"Acao nao suportada: {action_type.value}")

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa acao de ocorrencia."""
        action_type = request.action_type
        started_at = datetime.utcnow()

        try:
            if action_type == ActionType.CREATE_OCCURRENCE:
                result = await self._execute_create_occurrence(request, action_id, started_at)
            elif action_type == ActionType.RESOLVE_OCCURRENCE:
                result = await self._execute_resolve_occurrence(request, action_id, started_at)
            elif action_type == ActionType.UPDATE_OCCURRENCE:
                result = await self._execute_update_occurrence(request, action_id, started_at)
            else:
                raise ValueError(f"Acao nao suportada: {action_type.value}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar acao {action_type.value}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar acao: {action_type.value}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # =========================================================================
    # PREVIEWS
    # =========================================================================

    async def _create_occurrence_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criacao de ocorrencia."""
        params = request.parameters
        title = params.get("title", "")
        description = params.get("description", "")
        occurrence_type = params.get("occurrence_type", "")
        severity = params.get("severity", "")
        category = params.get("category", "")
        employee_id = params.get("employee_id", "")
        post_id = params.get("post_id", "")
        witnesses = params.get("witnesses")

        changes_summary = []
        warnings = []
        affected_entities = []

        # Validar parametros minimos
        if not title:
            warnings.append("Titulo da ocorrencia nao informado")
        if not description:
            warnings.append("Descricao da ocorrencia nao informada")
        if not employee_id:
            warnings.append("Funcionario nao informado")
        if not post_id:
            warnings.append("Posto nao informado")

        # Montar resumo de mudancas
        if title:
            changes_summary.append(f"Titulo: {title}")
        if occurrence_type:
            tipo_label = occurrence_type.replace("_", " ").title()
            changes_summary.append(f"Tipo: {tipo_label}")
        if severity:
            sev_icons = {"leve": "🟡", "moderada": "🟠", "grave": "🔴", "gravissima": "🚨"}
            changes_summary.append(f"Severidade: {sev_icons.get(severity, '')} {severity}")
        if category:
            changes_summary.append(f"Categoria: {category.replace('_', ' ').title()}")
        if employee_id:
            affected_entities.append({"type": "employee", "id": employee_id})
            changes_summary.append(f"Funcionario: {employee_id}")
        if post_id:
            affected_entities.append({"type": "post", "id": post_id})
            changes_summary.append(f"Posto: {post_id}")
        if witnesses:
            changes_summary.append(f"Testemunhas: {witnesses}")

        # Alertas por severidade
        if severity in ("grave", "gravissima"):
            warnings.append(f"🚨 Ocorrencia de severidade {severity.upper()} - requer atencao imediata")
        if severity == "gravissima":
            warnings.append("⚠️ Gravissima pode levar a demissao por justa causa")

        # Verificar permissao
        user_role = getattr(self, "user_role", None)
        required_perm = OCCURRENCE_PERMISSIONS["CREATE_OCCURRENCE"]
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissao {required_perm.value}: role={user_role}, has_perm={user_has_perm}")

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=f"Registrar Ocorrencia - {title}" if title else "Registrar Ocorrencia",
            description=f"Criar nova ocorrencia disciplinar: {title}",
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _resolve_occurrence_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para resolucao de ocorrencia."""
        params = request.parameters
        occurrence_id = params.get("occurrence_id")
        occurrence_code = params.get("occurrence_code")
        corrective_action = params.get("corrective_action", "")
        resolution_notes = params.get("resolution_notes", "")

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar ocorrencia
        repo = OccurrenceRepository(self.db)
        occurrence = None

        if occurrence_id:
            occurrence = await repo.get_by_id(occurrence_id)

        if not occurrence and occurrence_code:
            # Buscar por codigo
            items, total = await repo.list(page=1, page_size=200)
            for item in items:
                if item.code == occurrence_code:
                    occurrence = item
                    break

        if not occurrence:
            warnings.append("Ocorrencia nao encontrada")
            title = "Resolver Ocorrencia"
            description = "Ocorrencia nao encontrada"
        else:
            affected_entities.append(
                {
                    "type": "occurrence",
                    "id": occurrence.id,
                    "code": occurrence.code,
                }
            )

            changes_summary.append(f"Ocorrencia: {occurrence.code}")
            changes_summary.append(f"Titulo: {occurrence.title}")
            changes_summary.append(f"Severidade: {occurrence.severity}")
            changes_summary.append(f"Status atual: {occurrence.status}")
            changes_summary.append(f"Novo status: {OccurrenceStatus.RESOLVIDA.value}")

            if corrective_action:
                changes_summary.append(f"Acao corretiva: {corrective_action}")
            if resolution_notes:
                changes_summary.append(f"Notas: {resolution_notes}")

            if occurrence.status == OccurrenceStatus.RESOLVIDA.value:
                warnings.append("Ocorrencia ja esta resolvida")
            if occurrence.status == OccurrenceStatus.CANCELADA.value:
                warnings.append("Ocorrencia esta cancelada")
            if occurrence.status == OccurrenceStatus.ARQUIVADA.value:
                warnings.append("Ocorrencia esta arquivada")

            if not corrective_action:
                warnings.append("Acao corretiva nao informada (obrigatoria)")

            title = f"Resolver Ocorrencia - {occurrence.code}"
            description = f"Resolver ocorrencia {occurrence.code}: {occurrence.title}"

        # Verificar permissao
        user_role = getattr(self, "user_role", None)
        required_perm = OCCURRENCE_PERMISSIONS["RESOLVE_OCCURRENCE"]
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

    async def _update_occurrence_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para atualizacao de ocorrencia."""
        params = request.parameters
        occurrence_id = params.get("occurrence_id")
        occurrence_code = params.get("occurrence_code")

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar ocorrencia
        repo = OccurrenceRepository(self.db)
        occurrence = None

        if occurrence_id:
            occurrence = await repo.get_by_id(occurrence_id)

        if not occurrence and occurrence_code:
            items, total = await repo.list(page=1, page_size=200)
            for item in items:
                if item.code == occurrence_code:
                    occurrence = item
                    break

        if not occurrence:
            warnings.append("Ocorrencia nao encontrada")
            title = "Atualizar Ocorrencia"
            description = "Ocorrencia nao encontrada"
        else:
            affected_entities.append(
                {
                    "type": "occurrence",
                    "id": occurrence.id,
                    "code": occurrence.code,
                }
            )

            changes_summary.append(f"Ocorrencia: {occurrence.code}")
            changes_summary.append(f"Status atual: {occurrence.status}")

            # Listar mudancas solicitadas
            update_fields = {
                "title": "Titulo",
                "description": "Descricao",
                "occurrence_type": "Tipo",
                "severity": "Severidade",
                "category": "Categoria",
                "status": "Status",
            }
            for field, label in update_fields.items():
                if field in params and params[field]:
                    old_value = getattr(occurrence, field, "N/A")
                    new_value = params[field]
                    changes_summary.append(f"{label}: {old_value} -> {new_value}")

            if occurrence.is_resolved:
                warnings.append("Ocorrencia ja esta resolvida - alteracoes podem ser limitadas")

            title = f"Atualizar Ocorrencia - {occurrence.code}"
            description = f"Atualizar ocorrencia {occurrence.code}"

        # Verificar permissao
        user_role = getattr(self, "user_role", None)
        required_perm = OCCURRENCE_PERMISSIONS["UPDATE_OCCURRENCE"]
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

    # =========================================================================
    # EXECUCOES
    # =========================================================================

    async def _execute_create_occurrence(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criacao de ocorrencia."""
        params = request.parameters

        # Validar e converter enums
        try:
            occ_type = OccurrenceType(params.get("occurrence_type", "outros"))
        except ValueError:
            occ_type = OccurrenceType.OUTROS

        try:
            severity = OccurrenceSeverity(params.get("severity", "leve"))
        except ValueError:
            severity = OccurrenceSeverity.LEVE

        try:
            category = OccurrenceCategory(params.get("category", "outros"))
        except ValueError:
            category = OccurrenceCategory.OUTROS

        occurred_at = params.get("occurred_at")
        if isinstance(occurred_at, str):
            try:
                occurred_at = datetime.fromisoformat(occurred_at)
            except (ValueError, TypeError):
                occurred_at = datetime.utcnow()
        elif not occurred_at:
            occurred_at = datetime.utcnow()

        # Criar schema
        occurrence_data = OccurrenceCreate(
            title=params.get("title", "Ocorrencia sem titulo"),
            description=params.get("description", "Descricao nao informada"),
            occurrence_type=occ_type,
            severity=severity,
            category=category,
            occurred_at=occurred_at,
            employee_id=params.get("employee_id", ""),
            post_id=params.get("post_id", ""),
            patrol_round_id=params.get("patrol_round_id"),
            witnesses=params.get("witnesses"),
        )

        # Usar UUID real do usuario
        user_uuid = getattr(self, "user_uuid", None) or request.user_id

        # Criar via repository
        repo = OccurrenceRepository(self.db)
        occurrence = await repo.create(occurrence_data, inspector_id=user_uuid)

        logger.info(f"Ocorrencia criada via Bartolo: {occurrence.id} ({occurrence.code})")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ocorrencia {occurrence.code} criada com sucesso",
            details={
                "occurrence_id": occurrence.id,
                "code": occurrence.code,
                "title": occurrence.title,
                "severity": occurrence.severity,
                "category": occurrence.category,
                "status": occurrence.status,
                "employee_id": occurrence.employee_id,
                "post_id": occurrence.post_id,
            },
            affected_entities=[
                {"type": "occurrence", "id": occurrence.id, "code": occurrence.code},
                {"type": "employee", "id": occurrence.employee_id},
                {"type": "post", "id": occurrence.post_id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_resolve_occurrence(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa resolucao de ocorrencia."""
        params = request.parameters
        occurrence_id = params.get("occurrence_id")
        occurrence_code = params.get("occurrence_code")
        corrective_action = params.get("corrective_action", "")
        resolution_notes = params.get("resolution_notes")

        if not corrective_action:
            raise ValueError("Acao corretiva e obrigatoria para resolver uma ocorrencia")

        repo = OccurrenceRepository(self.db)
        occurrence = None

        # Buscar ocorrencia
        if occurrence_id:
            occurrence = await repo.get_by_id(occurrence_id)

        if not occurrence and occurrence_code:
            items, total = await repo.list(page=1, page_size=200)
            for item in items:
                if item.code == occurrence_code:
                    occurrence = item
                    break

        if not occurrence:
            raise ValueError("Ocorrencia nao encontrada")

        if occurrence.is_resolved:
            raise ValueError(f"Ocorrencia {occurrence.code} ja esta resolvida")

        # Criar schema de resolucao
        resolve_data = OccurrenceResolve(
            corrective_action=corrective_action,
            resolution_notes=resolution_notes,
        )

        # Usar UUID real do usuario
        user_uuid = getattr(self, "user_uuid", None) or request.user_id

        # Resolver via repository
        resolved = await repo.resolve(
            occurrence_id=occurrence.id,
            data=resolve_data,
            resolved_by_id=user_uuid,
        )

        if not resolved:
            raise ValueError(f"Nao foi possivel resolver a ocorrencia {occurrence.code}")

        logger.info(f"Ocorrencia resolvida via Bartolo: {resolved.id} ({resolved.code})")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ocorrencia {resolved.code} resolvida com sucesso",
            details={
                "occurrence_id": resolved.id,
                "code": resolved.code,
                "title": resolved.title,
                "status": resolved.status,
                "corrective_action": resolved.corrective_action,
                "resolution_notes": resolved.resolution_notes,
                "resolved_by": user_uuid,
                "resolved_at": resolved.resolved_at.isoformat() if resolved.resolved_at else None,
            },
            affected_entities=[
                {"type": "occurrence", "id": resolved.id, "code": resolved.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_update_occurrence(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa atualizacao de ocorrencia."""
        params = request.parameters
        occurrence_id = params.get("occurrence_id")
        occurrence_code = params.get("occurrence_code")

        repo = OccurrenceRepository(self.db)
        occurrence = None

        # Buscar ocorrencia
        if occurrence_id:
            occurrence = await repo.get_by_id(occurrence_id)

        if not occurrence and occurrence_code:
            items, total = await repo.list(page=1, page_size=200)
            for item in items:
                if item.code == occurrence_code:
                    occurrence = item
                    break

        if not occurrence:
            raise ValueError("Ocorrencia nao encontrada")

        # Montar dados de atualizacao (apenas campos fornecidos)
        update_fields = {}
        field_mapping = {
            "title": "title",
            "description": "description",
            "occurrence_type": "occurrence_type",
            "severity": "severity",
            "category": "category",
            "status": "status",
            "witnesses": "witnesses",
            "corrective_action": "corrective_action",
        }

        for param_key, schema_key in field_mapping.items():
            if param_key in params and params[param_key] is not None:
                value = params[param_key]
                # Converter strings para enums quando necessario
                if param_key == "occurrence_type":
                    with contextlib.suppress(ValueError):
                        value = OccurrenceType(value)
                elif param_key == "severity":
                    with contextlib.suppress(ValueError):
                        value = OccurrenceSeverity(value)
                elif param_key == "category":
                    with contextlib.suppress(ValueError):
                        value = OccurrenceCategory(value)
                elif param_key == "status":
                    with contextlib.suppress(ValueError):
                        value = OccurrenceStatus(value)
                update_fields[schema_key] = value

        if not update_fields:
            raise ValueError("Nenhum campo para atualizar foi informado")

        update_data = OccurrenceUpdate(**update_fields)

        # Atualizar via repository
        updated = await repo.update(occurrence.id, update_data)

        if not updated:
            raise ValueError(f"Nao foi possivel atualizar a ocorrencia {occurrence.code}")

        logger.info(f"Ocorrencia atualizada via Bartolo: {updated.id} ({updated.code})")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ocorrencia {updated.code} atualizada com sucesso",
            details={
                "occurrence_id": updated.id,
                "code": updated.code,
                "title": updated.title,
                "status": updated.status,
                "updated_fields": list(update_fields.keys()),
            },
            affected_entities=[
                {"type": "occurrence", "id": updated.id, "code": updated.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
