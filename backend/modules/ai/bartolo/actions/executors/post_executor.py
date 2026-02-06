"""
Executor de acoes relacionadas a postos de trabalho.
"""
import logging
from datetime import datetime
from uuid import uuid4
from typing import Optional

from modules.operacional.repositories.post_repository import PostRepository
from modules.operacional.schemas.post import PostCreate, PostUpdate
from modules.operacional.models.post import PostType, PostStatus, ShiftType
from modules.operacional.permissions import has_permission, Permission
from ..action_schemas import ActionRequest, ActionPreview, ActionResult
from ..action_types import ActionCategory, ActionStatus
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)

# Constantes de tipo de acao para postos
POST_ACTION_CREATE = "create_post"
POST_ACTION_UPDATE = "update_post"
POST_ACTION_DELETE = "delete_post"
POST_ACTION_STATS = "get_post_stats"


class PostActionExecutor(BaseActionExecutor):
    """Executor para acoes de postos de trabalho."""

    # Mapeamento de acoes para permissoes
    ACTION_PERMISSION_MAP = {
        POST_ACTION_CREATE: Permission.POSTS_CREATE,
        POST_ACTION_UPDATE: Permission.POSTS_EDIT,
        POST_ACTION_DELETE: Permission.POSTS_DELETE,
        POST_ACTION_STATS: Permission.POSTS_VIEW,
    }

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para acao de posto."""
        action_type_value = request.action_type.value if hasattr(request.action_type, 'value') else str(request.action_type)
        params = request.parameters

        if action_type_value == POST_ACTION_CREATE:
            return await self._create_post_preview(request)
        elif action_type_value == POST_ACTION_UPDATE:
            return await self._update_post_preview(request)
        elif action_type_value == POST_ACTION_DELETE:
            return await self._delete_post_preview(request)
        elif action_type_value == POST_ACTION_STATS:
            return await self._stats_post_preview(request)
        else:
            raise ValueError(f"Acao nao suportada: {action_type_value}")

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa acao de posto."""
        action_type_value = request.action_type.value if hasattr(request.action_type, 'value') else str(request.action_type)
        started_at = datetime.utcnow()

        try:
            if action_type_value == POST_ACTION_CREATE:
                result = await self._execute_create_post(request, action_id, started_at)
            elif action_type_value == POST_ACTION_UPDATE:
                result = await self._execute_update_post(request, action_id, started_at)
            elif action_type_value == POST_ACTION_DELETE:
                result = await self._execute_delete_post(request, action_id, started_at)
            elif action_type_value == POST_ACTION_STATS:
                result = await self._execute_get_stats(request, action_id, started_at)
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
    # PREVIEWS
    # =========================================================================

    async def _create_post_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criacao de posto."""
        params = request.parameters

        name = params.get('name', '')
        post_type = params.get('post_type', PostType.VIGILANTE.value)
        shift_type = params.get('shift_type', ShiftType.DIURNO.value)
        required_headcount = params.get('required_headcount', 1)

        changes_summary = []
        warnings = []
        affected_entities = []

        # Validar parametros minimos
        if not name:
            warnings.append("Nome do posto nao informado")

        changes_summary.append(f"Nome: {name}")
        changes_summary.append(f"Tipo: {post_type}")
        changes_summary.append(f"Turno: {shift_type}")
        changes_summary.append(f"Efetivo requerido: {required_headcount}")

        if params.get('requires_armed'):
            changes_summary.append("Requer armamento: SIM")
        if params.get('requires_vehicle'):
            changes_summary.append("Requer veiculo: SIM")
        if params.get('address'):
            changes_summary.append(f"Endereco: {params['address']}")
        if params.get('monthly_cost'):
            changes_summary.append(f"Custo mensal: R$ {params['monthly_cost']:,.2f}")

        # Verificar se ja existe posto com mesmo nome
        try:
            post_repo = PostRepository(self.db)
            existing_posts, _ = await post_repo.list(page=1, page_size=100)
            for existing in existing_posts:
                if existing.name.lower() == name.lower():
                    warnings.append(f"Ja existe um posto com o nome '{name}' ({existing.code})")
                    break
        except Exception as e:
            logger.warning(f"Erro ao verificar postos existentes: {e}")

        title = f"Criar Posto - {name}" if name else "Criar Posto"
        description = f"Criar novo posto de trabalho: {name} ({post_type}, {shift_type})"

        # Verificar permissao
        required_perm = self.ACTION_PERMISSION_MAP.get(POST_ACTION_CREATE, Permission.POSTS_CREATE)
        user_role = getattr(self, 'user_role', None)
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

    async def _update_post_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para atualizacao de posto."""
        params = request.parameters
        post_code = params.get('post_code')
        post_id = params.get('post_id')

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = None

        if post_id:
            post = await post_repo.get_by_id(post_id)
        elif post_code:
            post = await post_repo.get_by_code(post_code)

        if not post:
            warnings.append(f"Posto '{post_code or post_id}' nao encontrado")
            title = "Atualizar Posto"
            description = "Posto nao encontrado"
        else:
            affected_entities.append({
                "type": "post",
                "id": post.id,
                "name": post.name,
                "code": post.code,
            })

            changes_summary.append(f"Posto: {post.code} - {post.name}")

            # Listar campos que serao alterados
            update_fields = params.get('updates', {})
            if isinstance(update_fields, dict):
                for field, value in update_fields.items():
                    old_value = getattr(post, field, 'N/A')
                    changes_summary.append(f"{field}: {old_value} -> {value}")
            elif isinstance(update_fields, list):
                for item in update_fields:
                    changes_summary.append(f"Alteracao: {item}")

            title = f"Atualizar Posto - {post.code}"
            description = f"Atualizar dados do posto {post.name}"

        # Verificar permissao
        required_perm = self.ACTION_PERMISSION_MAP.get(POST_ACTION_UPDATE, Permission.POSTS_EDIT)
        user_role = getattr(self, 'user_role', None)
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

    async def _delete_post_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para desativacao (soft delete) de posto."""
        params = request.parameters
        post_code = params.get('post_code')
        post_id = params.get('post_id')

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = None

        if post_id:
            post = await post_repo.get_by_id(post_id)
        elif post_code:
            post = await post_repo.get_by_code(post_code)

        if not post:
            warnings.append(f"Posto '{post_code or post_id}' nao encontrado")
            title = "Desativar Posto"
            description = "Posto nao encontrado"
        else:
            affected_entities.append({
                "type": "post",
                "id": post.id,
                "name": post.name,
                "code": post.code,
            })

            changes_summary.append(f"Posto: {post.code} - {post.name}")
            changes_summary.append(f"Status atual: {post.status}")
            changes_summary.append(f"Novo status: {PostStatus.INACTIVE.value}")

            if post.status == PostStatus.INACTIVE.value:
                warnings.append("Posto ja esta inativo")

            if post.current_headcount > 0:
                warnings.append(
                    f"Posto possui {post.current_headcount} funcionario(s) alocado(s). "
                    f"Sera necessario realocar antes de desativar."
                )

            title = f"Desativar Posto - {post.code}"
            description = f"Desativar posto {post.name} (soft delete)"

        # Verificar permissao
        required_perm = self.ACTION_PERMISSION_MAP.get(POST_ACTION_DELETE, Permission.POSTS_DELETE)
        user_role = getattr(self, 'user_role', None)
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

    async def _stats_post_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para consulta de estatisticas."""
        params = request.parameters
        post_code = params.get('post_code')

        title = f"Estatisticas do Posto - {post_code}" if post_code else "Estatisticas Gerais de Postos"
        description = "Consultar estatisticas e indicadores dos postos"

        # Verificar permissao
        required_perm = self.ACTION_PERMISSION_MAP.get(POST_ACTION_STATS, Permission.POSTS_VIEW)
        user_role = getattr(self, 'user_role', None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=[],
            changes_summary=["Consulta somente leitura - nenhuma alteracao sera realizada"],
            warnings=[],
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=False,
        )

    # =========================================================================
    # EXECUCOES
    # =========================================================================

    async def _execute_create_post(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criacao de posto."""
        params = request.parameters

        name = params.get('name')
        if not name:
            raise ValueError("Nome do posto e obrigatorio")

        # Resolver enums
        post_type_str = params.get('post_type', PostType.VIGILANTE.value)
        shift_type_str = params.get('shift_type', ShiftType.DIURNO.value)

        try:
            post_type_enum = PostType(post_type_str)
        except ValueError:
            post_type_enum = PostType.VIGILANTE
            logger.warning(f"Tipo de posto invalido '{post_type_str}', usando VIGILANTE como padrao")

        try:
            shift_type_enum = ShiftType(shift_type_str)
        except ValueError:
            shift_type_enum = ShiftType.DIURNO
            logger.warning(f"Tipo de turno invalido '{shift_type_str}', usando DIURNO como padrao")

        # Criar schema
        post_data = PostCreate(
            name=name,
            description=params.get('description'),
            post_type=post_type_enum,
            shift_type=shift_type_enum,
            contract_id=params.get('contract_id'),
            client_id=params.get('client_id'),
            address=params.get('address'),
            city=params.get('city'),
            state=params.get('state'),
            zip_code=params.get('zip_code'),
            latitude=params.get('latitude'),
            longitude=params.get('longitude'),
            shift_start_time=params.get('shift_start_time'),
            shift_end_time=params.get('shift_end_time'),
            break_duration_minutes=params.get('break_duration_minutes', 60),
            night_shift_bonus_percent=params.get('night_shift_bonus_percent', 20.0),
            hazard_pay_percent=params.get('hazard_pay_percent', 0.0),
            required_headcount=params.get('required_headcount', 1),
            requires_experience_months=params.get('requires_experience_months', 0),
            hourly_rate=params.get('hourly_rate', 0.0),
            monthly_cost=params.get('monthly_cost', 0.0),
            requires_armed=params.get('requires_armed', False),
            requires_vehicle=params.get('requires_vehicle', False),
            required_certifications=params.get('required_certifications'),
            supervisor_name=params.get('supervisor_name'),
            supervisor_phone=params.get('supervisor_phone'),
            emergency_contact=params.get('emergency_contact'),
            emergency_phone=params.get('emergency_phone'),
            notes=params.get('notes'),
        )

        # Criar via repository
        post_repo = PostRepository(self.db)
        user_uuid = getattr(self, 'user_uuid', None)
        post = await post_repo.create(post_data, created_by=user_uuid)

        logger.info(f"Posto criado via Bartolo: {post.id} ({post.code})")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Posto '{post.name}' criado com sucesso ({post.code})",
            details={
                "post_id": post.id,
                "post_code": post.code,
                "post_name": post.name,
                "post_type": post.post_type,
                "shift_type": post.shift_type,
                "status": post.status,
                "required_headcount": post.required_headcount,
            },
            affected_entities=[
                {"type": "post", "id": post.id, "code": post.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_update_post(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa atualizacao de posto."""
        params = request.parameters
        post_code = params.get('post_code')
        post_id = params.get('post_id')

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = None

        if post_id:
            post = await post_repo.get_by_id(post_id)
        elif post_code:
            post = await post_repo.get_by_code(post_code)

        if not post:
            raise ValueError(f"Posto '{post_code or post_id}' nao encontrado")

        # Construir update
        update_fields = params.get('updates', {})
        if not isinstance(update_fields, dict):
            raise ValueError("Campos de atualizacao devem ser um dicionario")

        # Resolver enums se necessario
        if 'post_type' in update_fields:
            try:
                update_fields['post_type'] = PostType(update_fields['post_type'])
            except ValueError:
                raise ValueError(f"Tipo de posto invalido: {update_fields['post_type']}")

        if 'status' in update_fields:
            try:
                update_fields['status'] = PostStatus(update_fields['status'])
            except ValueError:
                raise ValueError(f"Status invalido: {update_fields['status']}")

        if 'shift_type' in update_fields:
            try:
                update_fields['shift_type'] = ShiftType(update_fields['shift_type'])
            except ValueError:
                raise ValueError(f"Tipo de turno invalido: {update_fields['shift_type']}")

        post_update = PostUpdate(**update_fields)
        updated_post = await post_repo.update(post.id, post_update)

        if not updated_post:
            raise ValueError(f"Nao foi possivel atualizar o posto {post.code}")

        logger.info(f"Posto atualizado via Bartolo: {updated_post.id} ({updated_post.code})")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Posto '{updated_post.name}' atualizado com sucesso ({updated_post.code})",
            details={
                "post_id": updated_post.id,
                "post_code": updated_post.code,
                "post_name": updated_post.name,
                "updated_fields": list(update_fields.keys()),
            },
            affected_entities=[
                {"type": "post", "id": updated_post.id, "code": updated_post.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_delete_post(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa desativacao (soft delete) de posto."""
        params = request.parameters
        post_code = params.get('post_code')
        post_id = params.get('post_id')

        # Buscar posto
        post_repo = PostRepository(self.db)
        post = None

        if post_id:
            post = await post_repo.get_by_id(post_id)
        elif post_code:
            post = await post_repo.get_by_code(post_code)

        if not post:
            raise ValueError(f"Posto '{post_code or post_id}' nao encontrado")

        # Verificar se tem funcionarios alocados
        if post.current_headcount > 0:
            logger.warning(
                f"Desativando posto {post.code} com {post.current_headcount} "
                f"funcionario(s) alocado(s)"
            )

        # Guardar dados antes de desativar
        post_code_saved = post.code
        post_name_saved = post.name
        post_id_saved = post.id

        # Executar soft delete
        deleted = await post_repo.delete(post.id)

        if not deleted:
            raise ValueError(f"Nao foi possivel desativar o posto {post_code_saved}")

        logger.info(f"Posto desativado via Bartolo: {post_id_saved} ({post_code_saved})")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Posto '{post_name_saved}' desativado com sucesso ({post_code_saved})",
            details={
                "post_id": post_id_saved,
                "post_code": post_code_saved,
                "post_name": post_name_saved,
                "action": "soft_delete",
                "new_status": PostStatus.INACTIVE.value,
            },
            affected_entities=[
                {"type": "post", "id": post_id_saved, "code": post_code_saved},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_get_stats(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa consulta de estatisticas dos postos."""
        params = request.parameters
        post_code = params.get('post_code')

        post_repo = PostRepository(self.db)

        if post_code:
            # Stats de um posto especifico
            post = await post_repo.get_by_code(post_code)
            if not post:
                raise ValueError(f"Posto '{post_code}' nao encontrado")

            cobertura_pct = round(
                (post.current_headcount / post.required_headcount) * 100, 1
            ) if post.required_headcount > 0 else 0

            details = {
                "post_id": post.id,
                "post_code": post.code,
                "post_name": post.name,
                "post_type": post.post_type,
                "shift_type": post.shift_type,
                "status": post.status,
                "required_headcount": post.required_headcount,
                "current_headcount": post.current_headcount,
                "vacancy_count": post.vacancy_count,
                "cobertura_pct": cobertura_pct,
                "monthly_cost": post.monthly_cost,
                "hourly_rate": post.hourly_rate,
                "requires_armed": post.requires_armed,
                "requires_vehicle": post.requires_vehicle,
            }

            message = (
                f"Estatisticas do posto {post.code}: "
                f"Cobertura {cobertura_pct}% ({post.current_headcount}/{post.required_headcount}), "
                f"Custo R$ {post.monthly_cost:,.2f}"
            )
        else:
            # Stats gerais
            stats = await post_repo.get_stats()
            cobertura_geral = round(
                (stats.total_allocated / stats.total_headcount) * 100, 1
            ) if stats.total_headcount > 0 else 0

            details = {
                "total": stats.total,
                "filled": stats.filled,
                "with_vacancy": stats.with_vacancy,
                "total_headcount": stats.total_headcount,
                "total_allocated": stats.total_allocated,
                "cobertura_geral": cobertura_geral,
                "total_monthly_cost": stats.total_monthly_cost,
                "by_status": stats.by_status,
                "by_type": stats.by_type,
                "by_shift": stats.by_shift,
            }

            message = (
                f"Estatisticas gerais: {stats.total} postos, "
                f"Cobertura {cobertura_geral}% ({stats.total_allocated}/{stats.total_headcount}), "
                f"Custo total R$ {stats.total_monthly_cost:,.2f}"
            )

        logger.info(f"Estatisticas de postos consultadas via Bartolo")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=message,
            details=details,
            affected_entities=[],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
