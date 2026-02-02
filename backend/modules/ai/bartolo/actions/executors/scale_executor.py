"""
Executor de ações relacionadas a escalas.

Suporta ações básicas (criar, aprovar, publicar) e avançadas
(geração automática, otimização inteligente, templates).
"""

import logging
from datetime import datetime
from uuid import uuid4

from modules.operacional.models.scale import ScaleStatus, ScaleType
from modules.operacional.permissions import has_permission
from modules.operacional.repositories.scale_repository import ScaleRepository
from modules.operacional.schemas.scale import ScaleCreate

from ..action_permissions import get_required_permission
from ..action_schemas import ActionPreview, ActionRequest, ActionResult
from ..action_types import ActionStatus, ActionType
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes para novos action types (escalas avançadas)
# Usadas como string para não alterar o enum ActionType existente.
# ---------------------------------------------------------------------------
SCALE_AUTO_GENERATE = "auto_generate_scale"
SCALE_OPTIMIZE = "optimize_scale"
SCALE_CREATE_TEMPLATE = "create_scale_template"
SCALE_APPLY_TEMPLATE = "apply_scale_template"


class ScaleActionExecutor(BaseActionExecutor):
    """Executor para ações de escala."""

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para ação de escala."""
        action_type = request.action_type
        action_value = action_type.value if isinstance(action_type, ActionType) else str(action_type)

        if action_value == ActionType.CREATE_SCALE.value:
            return await self._create_scale_preview(request)
        elif action_value == ActionType.APPROVE_SCALE.value:
            return await self._approve_scale_preview(request)
        elif action_value == ActionType.PUBLISH_SCALE.value:
            return await self._publish_scale_preview(request)
        elif action_value == SCALE_AUTO_GENERATE:
            return await self._auto_generate_preview(request)
        elif action_value == SCALE_OPTIMIZE:
            return await self._optimize_preview(request)
        elif action_value == SCALE_CREATE_TEMPLATE:
            return await self._create_template_preview(request)
        elif action_value == SCALE_APPLY_TEMPLATE:
            return await self._apply_template_preview(request)
        else:
            raise ValueError(f"Ação não suportada: {action_value}")

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa ação de escala."""
        action_type = request.action_type
        action_value = action_type.value if isinstance(action_type, ActionType) else str(action_type)
        started_at = datetime.utcnow()

        try:
            if action_value == ActionType.CREATE_SCALE.value:
                result = await self._execute_create_scale(request, action_id, started_at)
            elif action_value == ActionType.APPROVE_SCALE.value:
                result = await self._execute_approve_scale(request, action_id, started_at)
            elif action_value == ActionType.PUBLISH_SCALE.value:
                result = await self._execute_publish_scale(request, action_id, started_at)
            elif action_value == SCALE_AUTO_GENERATE:
                result = await self._execute_auto_generate(request, action_id, started_at)
            elif action_value == SCALE_OPTIMIZE:
                result = await self._execute_optimize(request, action_id, started_at)
            elif action_value == SCALE_CREATE_TEMPLATE:
                result = await self._execute_create_template(request, action_id, started_at)
            elif action_value == SCALE_APPLY_TEMPLATE:
                result = await self._execute_apply_template(request, action_id, started_at)
            else:
                raise ValueError(f"Ação não suportada: {action_value}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar ação {action_value}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar ação: {action_value}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    async def _create_scale_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criação de escala."""
        params = request.parameters
        month = params.get("month")
        year = params.get("year")

        changes_summary = []
        warnings = []
        affected_entities = []

        # Validar parâmetros mínimos
        if not params.get("post_code") and not params.get("post_name"):
            warnings.append("⚠️ Código ou nome do posto não informado")
        if not month:
            warnings.append("⚠️ Mês não informado")
        if not year:
            # Usar ano atual como padrão
            year = datetime.now().year
            params["year"] = year

        # Resolver posto (code primeiro, depois name)
        post, post_warnings = await self.resolve_post(params)
        warnings.extend(post_warnings)

        # Se resolveu por nome, propagar post_code para execução
        if post and not params.get("post_code"):
            params["post_code"] = post.code

        if not post:
            title = "Criar Escala"
            description = "Não foi possível criar preview - posto não encontrado"
        else:
            affected_entities.append({"type": "post", "id": post.id, "name": post.name, "code": post.code})

            changes_summary.append(f"Posto: {post.code} - {post.name}")
            changes_summary.append(f"Período: {month:02d}/{year}")
            changes_summary.append("Tipo: Escala 12x36 (padrão)")

            # Verificar se já existe escala
            scale_repo = ScaleRepository(self.db)
            existing = await scale_repo.get_by_post_and_period(post.id, month, year) if month and year else None

            if existing:
                warnings.append(f"⚠️ Já existe escala para {post.code} em {month:02d}/{year}")
                warnings.append(f"   Status: {existing.status}")

            title = f"Criar Escala - {post.code}"
            description = f"Criar escala para {post.name} em {month:02d}/{year}"

        # Verificar permissão
        required_perm = get_required_permission(request.action_type)
        # Usa role que foi setado pelo ActionExecutor
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissão {required_perm.value}: role={user_role}, has_perm={user_has_perm}")

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

    async def _approve_scale_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para aprovação de escala."""
        params = request.parameters
        scale_id = params.get("scale_id")
        post_code = params.get("post_code")

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar escala
        scale_repo = ScaleRepository(self.db)
        scale = None

        if scale_id:
            scale = await scale_repo.get_by_id(scale_id)
        elif post_code or params.get("post_name"):
            # Buscar última escala do posto
            post, _ = await self.resolve_post(params)
            if post:
                # Buscar escalas do mês atual
                now = datetime.now()
                scale = await scale_repo.get_by_post_and_period(post.id, now.month, now.year)

        if not scale:
            warnings.append("⚠️ Escala não encontrada")
            title = "Aprovar Escala"
            description = "Escala não encontrada"
        else:
            affected_entities.append(
                {
                    "type": "scale",
                    "id": scale.id,
                    "code": getattr(scale, "code", "N/A"),
                }
            )

            changes_summary.append(f"Escala: {getattr(scale, 'code', scale.id)}")
            changes_summary.append(f"Período: {scale.month:02d}/{scale.year}")
            changes_summary.append(f"Status atual: {scale.status}")
            changes_summary.append(f"Novo status: {ScaleStatus.APPROVED.value}")

            if scale.status == ScaleStatus.APPROVED.value:
                warnings.append("⚠️ Escala já está aprovada")

            if scale.status == ScaleStatus.PUBLISHED.value:
                warnings.append("⚠️ Escala já foi publicada")

            title = f"Aprovar Escala - {getattr(scale, 'code', scale.id)}"
            description = f"Aprovar escala {scale.month:02d}/{scale.year}"

        # Verificar permissão
        required_perm = get_required_permission(request.action_type)
        # Usa role que foi setado pelo ActionExecutor
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissão {required_perm.value}: role={user_role}, has_perm={user_has_perm}")

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
            can_be_undone=False,  # Aprovação não pode ser desfeita facilmente
            requires_confirmation=True,
        )

    async def _publish_scale_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para publicação de escala."""
        params = request.parameters
        scale_id = params.get("scale_id")

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar escala
        scale_repo = ScaleRepository(self.db)
        scale = await scale_repo.get_by_id(scale_id) if scale_id else None

        if not scale:
            warnings.append("⚠️ Escala não encontrada")
            title = "Publicar Escala"
            description = "Escala não encontrada"
        else:
            affected_entities.append(
                {
                    "type": "scale",
                    "id": scale.id,
                    "code": getattr(scale, "code", "N/A"),
                }
            )

            changes_summary.append(f"Escala: {getattr(scale, 'code', scale.id)}")
            changes_summary.append(f"Status atual: {scale.status}")
            changes_summary.append(f"Novo status: {ScaleStatus.PUBLISHED.value}")

            if scale.status != ScaleStatus.APPROVED.value:
                warnings.append("⚠️ Escala precisa estar aprovada antes de publicar")

            if scale.status == ScaleStatus.PUBLISHED.value:
                warnings.append("⚠️ Escala já está publicada")

            title = f"Publicar Escala - {getattr(scale, 'code', scale.id)}"
            description = f"Publicar escala {scale.month:02d}/{scale.year}"

        # Verificar permissão
        required_perm = get_required_permission(request.action_type)
        # Usa role que foi setado pelo ActionExecutor
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False
        logger.info(f"Permissão {required_perm.value}: role={user_role}, has_perm={user_has_perm}")

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

    async def _execute_create_scale(self, request: ActionRequest, action_id: str, started_at: datetime) -> ActionResult:
        """Executa criação de escala."""
        params = request.parameters
        month = params.get("month")
        year = params.get("year", datetime.now().year)

        # Resolver posto (code ou name)
        post, _ = await self.resolve_post(params)

        if not post:
            raise ValueError(f"Posto não encontrado (code={params.get('post_code')}, name={params.get('post_name')})")

        # Criar escala
        scale_data = ScaleCreate(
            post_id=post.id,
            scale_type=ScaleType.SCALE_12X36,  # Padrão
            month=month,
            year=year,
            notes=params.get("notes"),
            config=params.get("config"),
        )

        scale_repo = ScaleRepository(self.db)
        # Usa UUID real do usuário que foi setado pelo ActionExecutor
        user_uuid = getattr(self, "user_uuid", None)
        scale = await scale_repo.create(scale_data, created_by=user_uuid)

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Escala criada com sucesso",
            details={
                "scale_id": scale.id,
                "post_code": post.code,
                "post_name": post.name,
                "month": month,
                "year": year,
                "status": scale.status,
            },
            affected_entities=[
                {"type": "scale", "id": scale.id},
                {"type": "post", "id": post.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_approve_scale(
        self, request: ActionRequest, action_id: str, started_at: datetime
    ) -> ActionResult:
        """Executa aprovação de escala."""
        params = request.parameters
        scale_id = params.get("scale_id")
        post_code = params.get("post_code")
        notes = params.get("notes")

        scale_repo = ScaleRepository(self.db)
        scale = None

        # Buscar escala por ID direto ou pelo posto
        if scale_id:
            scale = await scale_repo.get_by_id(scale_id)
        elif post_code or params.get("post_name"):
            post, _ = await self.resolve_post(params)
            if post:
                now = datetime.now()
                scale = await scale_repo.get_by_post_and_period(post.id, now.month, now.year)

        if not scale:
            raise ValueError("Escala não encontrada")

        # Verificar se escala pode ser aprovada
        if scale.status == ScaleStatus.APPROVED.value:
            raise ValueError("Escala já está aprovada")
        if scale.status == ScaleStatus.PUBLISHED.value:
            raise ValueError("Escala já foi publicada")

        # Usar UUID real do usuário
        user_uuid = getattr(self, "user_uuid", None)

        # Se a escala está em DRAFT, mudar para PENDING_APPROVAL antes de aprovar
        if scale.status == ScaleStatus.DRAFT.value:
            from modules.operacional.schemas.scale import ScaleUpdate

            await scale_repo.update(scale.id, ScaleUpdate(status=ScaleStatus.PENDING_APPROVAL))
            # Recarregar a escala após update
            scale = await scale_repo.get_by_id(scale.id)

        # Aprovar via repository
        approved_scale = await scale_repo.approve(
            scale_id=scale.id,
            approved_by=user_uuid,
            notes=notes,
        )

        if not approved_scale:
            raise ValueError(
                f"Não foi possível aprovar a escala. "
                f"Status atual: {scale.status}. "
                f"Status requerido: {ScaleStatus.PENDING_APPROVAL.value}"
            )

        logger.info(f"Escala aprovada via Bartolo: {approved_scale.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Escala aprovada com sucesso",
            details={
                "scale_id": approved_scale.id,
                "month": approved_scale.month,
                "year": approved_scale.year,
                "status": approved_scale.status,
                "approved_by": user_uuid,
                "approved_at": approved_scale.approved_at.isoformat() if approved_scale.approved_at else None,
            },
            affected_entities=[
                {"type": "scale", "id": approved_scale.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_publish_scale(
        self, request: ActionRequest, action_id: str, started_at: datetime
    ) -> ActionResult:
        """Executa publicação de escala."""
        params = request.parameters
        scale_id = params.get("scale_id")
        post_code = params.get("post_code")

        scale_repo = ScaleRepository(self.db)
        scale = None

        # Buscar escala por ID direto ou pelo posto
        if scale_id:
            scale = await scale_repo.get_by_id(scale_id)
        elif post_code or params.get("post_name"):
            post, _ = await self.resolve_post(params)
            if post:
                now = datetime.now()
                scale = await scale_repo.get_by_post_and_period(post.id, now.month, now.year)

        if not scale:
            raise ValueError("Escala não encontrada")

        # Verificar se escala pode ser publicada
        if scale.status == ScaleStatus.PUBLISHED.value:
            raise ValueError("Escala já está publicada")
        if scale.status != ScaleStatus.APPROVED.value:
            raise ValueError(f"Escala precisa estar aprovada antes de publicar. Status atual: {scale.status}")

        # Usar UUID real do usuário
        user_uuid = getattr(self, "user_uuid", None)

        # Publicar via repository
        published_scale = await scale_repo.publish(
            scale_id=scale.id,
            published_by=user_uuid,
        )

        if not published_scale:
            raise ValueError(
                f"Não foi possível publicar a escala. "
                f"Status atual: {scale.status}. "
                f"Status requerido: {ScaleStatus.APPROVED.value}"
            )

        logger.info(f"Escala publicada via Bartolo: {published_scale.id}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message="Escala publicada com sucesso",
            details={
                "scale_id": published_scale.id,
                "month": published_scale.month,
                "year": published_scale.year,
                "status": published_scale.status,
                "published_by": user_uuid,
                "published_at": published_scale.published_at.isoformat() if published_scale.published_at else None,
            },
            affected_entities=[
                {"type": "scale", "id": published_scale.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ======================================================================
    # AÇÕES AVANÇADAS: AutoScale, Otimização Inteligente, Templates
    # ======================================================================

    # --- Previews ---

    async def _auto_generate_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para geração automática de escalas."""
        params = request.parameters
        month = params.get("month")
        year = params.get("year", datetime.now().year)

        warnings = []
        changes_summary = []

        if not month:
            month = datetime.now().month
            params["month"] = month
            warnings.append("⚠️ Mês não informado, usando mês atual")

        changes_summary.append(f"Período: {month:02d}/{year}")
        changes_summary.append("Gerar escalas para TODOS os postos com alocações ativas")
        changes_summary.append("Tipo padrão: 12x36")
        changes_summary.append("Postos que já possuem escala serão ignorados")

        # Verificar permissão
        required_perm = get_required_permission(ActionType.CREATE_SCALE)
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=f"Geração Automática de Escalas - {month:02d}/{year}",
            description=f"Gerar escalas automaticamente para todos os postos em {month:02d}/{year}",
            affected_entities=[{"type": "all_posts", "description": "Todos os postos com alocações ativas"}],
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _optimize_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para otimização inteligente de escala."""
        params = request.parameters
        month = params.get("month", datetime.now().month)
        year = params.get("year", datetime.now().year)
        schedule_id = params.get("schedule_id")

        changes_summary = [
            f"Período: {month:02d}/{year}",
            "Otimização com IA: previsão de demanda + matching de skills",
            "Análise de custo (horas normais, extras, noturnas)",
            "Score de eficiência e cobertura",
        ]
        warnings = [
            "⚠️ A otimização pode alterar alocações existentes",
            "⚠️ Recomenda-se validar a escala após otimização",
        ]

        required_perm = get_required_permission(ActionType.CREATE_SCALE)
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=f"Otimização Inteligente - {month:02d}/{year}",
            description=f"Otimizar escalas com IA para {month:02d}/{year}",
            affected_entities=[{"type": "schedule", "id": schedule_id or "novo"}],
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _create_template_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criação de template de escala."""
        params = request.parameters
        scale_id = params.get("scale_id")
        template_name = params.get("name", "Sem nome")

        changes_summary = [
            f"Escala base: {scale_id or 'N/A'}",
            f"Nome do template: {template_name}",
            "Extrair padrões de turno da escala",
            "Salvar como template reutilizável",
        ]
        warnings = []

        if not scale_id:
            warnings.append("⚠️ ID da escala não informado")

        required_perm = get_required_permission(ActionType.CREATE_SCALE)
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=f"Criar Template - {template_name}",
            description=f"Criar template '{template_name}' a partir da escala {scale_id}",
            affected_entities=[
                {"type": "scale", "id": scale_id or "N/A"},
                {"type": "scale_template", "name": template_name},
            ],
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _apply_template_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para aplicação de template."""
        params = request.parameters
        template_id = params.get("template_id")
        post_id = params.get("post_id")
        month = params.get("month")
        year = params.get("year", datetime.now().year)

        changes_summary = [
            f"Template: {template_id or 'N/A'}",
            f"Posto: {post_id or 'N/A'}",
            f"Período: {month:02d}/{year}" if month else "Período: não informado",
            "Criar nova escala baseada no template",
            "Gerar turnos conforme padrões do template",
        ]
        warnings = []

        if not template_id:
            warnings.append("⚠️ ID do template não informado")
        if not post_id:
            warnings.append("⚠️ Posto não informado")
        if not month:
            warnings.append("⚠️ Mês não informado")

        # Verificar se já existe escala para o período
        if post_id and month:
            try:
                post, _ = await self.resolve_post({"post_code": post_id, "post_name": params.get("post_name")})
                if post:
                    scale_repo = ScaleRepository(self.db)
                    existing = await scale_repo.get_by_post_and_period(post.id, month, year)
                    if existing:
                        warnings.append(f"⚠️ Já existe escala para {post_id} em {month:02d}/{year}")
            except Exception as e:
                logger.warning(f"Erro ao verificar escala existente: {e}")

        required_perm = get_required_permission(ActionType.CREATE_SCALE)
        user_role = getattr(self, "user_role", None)
        user_has_perm = has_permission(user_role, required_perm) if user_role else False

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=f"Aplicar Template - {post_id or 'N/A'} {month:02d}/{year}" if month else "Aplicar Template",
            description=f"Aplicar template {template_id} no posto {post_id} em {month:02d}/{year}"
            if month
            else "Aplicar template de escala",
            affected_entities=[
                {"type": "scale_template", "id": template_id or "N/A"},
                {"type": "post", "id": post_id or "N/A"},
            ],
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm.value,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    # --- Execuções ---

    async def _execute_auto_generate(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa geração automática de escalas via AutoScaleService."""
        params = request.parameters
        month = params.get("month")
        year = params.get("year", datetime.now().year)
        user_uuid = getattr(self, "user_uuid", None)

        try:
            from modules.operacional.services.auto_scale_service import AutoScaleService
        except ImportError:
            raise ValueError(
                "AutoScaleService não disponível. O módulo operacional de geração automática não está instalado."
            )

        service = AutoScaleService(self.db)

        if month:
            result = await service.generate_scales_for_month(
                month=month, year=year, created_by=str(user_uuid) if user_uuid else None
            )
        else:
            result = await service.generate_scales_for_current_month(created_by=str(user_uuid) if user_uuid else None)

        logger.info(
            f"Auto-geração via Bartolo: {result.get('scales_created', 0)} escalas, "
            f"{result.get('shifts_created', 0)} turnos"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=result.get("success", False),
            message=result.get("message", "Geração automática concluída"),
            details={
                "month": month,
                "year": year,
                "scales_created": result.get("scales_created", 0),
                "shifts_created": result.get("shifts_created", 0),
                "errors": result.get("errors", []),
            },
            affected_entities=[
                {"type": "scales_batch", "count": result.get("scales_created", 0)},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_optimize(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa otimização inteligente via IntelligentOperationsService."""
        import calendar

        params = request.parameters
        month = params.get("month", datetime.now().month)
        year = params.get("year", datetime.now().year)
        tenant_id = params.get("tenant_id")

        if not tenant_id:
            raise ValueError("tenant_id é obrigatório para otimização inteligente. Informe o ID do cliente/condomínio.")

        try:
            from modules.operacional.services.intelligent_operations_service import (
                IntelligentOperationsService,
            )
        except ImportError:
            raise ValueError(
                "IntelligentOperationsService não disponível. O módulo de operações inteligentes não está instalado."
            )

        _, last_day = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day, 23, 59, 59)

        service = IntelligentOperationsService(self.db, tenant_id)
        schedule = await service.optimize_schedule(start_date, end_date)
        insights = await service.generate_operational_insights(schedule)

        logger.info(
            f"Otimização inteligente via Bartolo: schedule={schedule.id}, "
            f"efficiency={schedule.efficiency_score:.2f}, coverage={schedule.coverage_score:.2f}"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Escala otimizada com eficiência {schedule.efficiency_score:.1%} e cobertura {schedule.coverage_score:.1%}",
            details={
                "schedule_id": schedule.id,
                "month": month,
                "year": year,
                "efficiency_score": schedule.efficiency_score,
                "coverage_score": schedule.coverage_score,
                "optimization_metrics": schedule.optimization_metrics,
                "cost_analysis": schedule.cost_analysis,
                "total_assignments": len(schedule.assignments),
                "insights_count": len(insights),
                "insights": [
                    {
                        "type": ins.type,
                        "description": ins.description,
                        "impact": ins.impact,
                        "recommendation": ins.recommendation,
                        "estimated_savings": ins.estimated_savings,
                    }
                    for ins in insights
                ],
            },
            affected_entities=[
                {"type": "optimized_schedule", "id": schedule.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_create_template(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criação de template a partir de escala."""
        params = request.parameters
        scale_id = params.get("scale_id")
        template_name = params.get("name", "Template sem nome")
        description = params.get("description", "")
        tenant_id = params.get("tenant_id")
        user_uuid = getattr(self, "user_uuid", None)

        if not scale_id:
            raise ValueError("scale_id é obrigatório para criar template")
        if not tenant_id:
            raise ValueError("tenant_id é obrigatório para criar template")

        try:
            from modules.operacional.repositories.scale_template_repository import ScaleTemplateRepository
            from modules.operacional.schemas.scale_template import ScaleTemplateCreate
            from modules.operacional.services.scale_template_service import ScaleTemplateService
        except ImportError:
            raise ValueError(
                "Módulo de templates de escala não disponível. Verifique se o módulo operacional está instalado."
            )

        template_service = ScaleTemplateService(self.db)
        template_repo = ScaleTemplateRepository(self.db)

        # Extrair template da escala
        template_data = await template_service.extract_template_from_scale(
            scale_id=scale_id,
            include_employee_mapping=False,
        )

        # Criar template no banco
        create_data = ScaleTemplateCreate(
            name=template_name,
            description=description or f"Template criado via Bartolo a partir da escala {scale_id}",
            template_data=template_data,
        )
        template = await template_repo.create(
            data=create_data,
            tenant_id=tenant_id,
            created_by=str(user_uuid) if user_uuid else "",
        )

        logger.info(f"Template criado via Bartolo: {template.id} - {template.name}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Template '{template_name}' criado com sucesso",
            details={
                "template_id": template.id,
                "template_name": template.name,
                "scale_id": scale_id,
                "total_employees": template_data.metadata.total_employees,
                "total_shifts": template_data.metadata.total_shifts_per_month,
                "coverage": template_data.metadata.coverage_percentage,
                "scale_type": template_data.scale_type,
            },
            affected_entities=[
                {"type": "scale_template", "id": template.id},
                {"type": "scale", "id": scale_id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_apply_template(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa aplicação de template em posto/mês."""
        params = request.parameters
        template_id = params.get("template_id")
        post_id = params.get("post_id")
        month = params.get("month")
        year = params.get("year", datetime.now().year)
        tenant_id = params.get("tenant_id")
        user_uuid = getattr(self, "user_uuid", None)

        if not template_id:
            raise ValueError("template_id é obrigatório")
        if not post_id:
            raise ValueError("post_id é obrigatório")
        if not month:
            raise ValueError("month é obrigatório")
        if not tenant_id:
            raise ValueError("tenant_id é obrigatório")

        try:
            from modules.operacional.repositories.scale_template_repository import ScaleTemplateRepository
            from modules.operacional.schemas.scale_template import ScaleTemplateApplyRequest
            from modules.operacional.services.scale_template_service import ScaleTemplateService
        except ImportError:
            raise ValueError(
                "Módulo de templates de escala não disponível. Verifique se o módulo operacional está instalado."
            )

        template_repo = ScaleTemplateRepository(self.db)
        template_service = ScaleTemplateService(self.db)

        # Buscar template
        template = await template_repo.get_by_id(template_id, tenant_id)
        if not template:
            raise ValueError(f"Template '{template_id}' não encontrado")

        # Aplicar template
        apply_request = ScaleTemplateApplyRequest(
            month=month,
            year=year,
            post_id=post_id,
        )
        scale = await template_service.apply_template_to_period(
            template_data=template.template_data,
            apply_request=apply_request,
            created_by=str(user_uuid) if user_uuid else "",
        )

        # Incrementar uso do template
        await template_repo.increment_usage(template_id)

        logger.info(
            f"Template {template_id} aplicado via Bartolo: "
            f"escala {scale.id} criada para posto {post_id} em {month:02d}/{year}"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Template '{template.name}' aplicado com sucesso. Escala {scale.id} criada.",
            details={
                "template_id": template.id,
                "template_name": template.name,
                "scale_id": scale.id,
                "post_id": post_id,
                "month": month,
                "year": year,
                "status": scale.status,
            },
            affected_entities=[
                {"type": "scale_template", "id": template.id},
                {"type": "scale", "id": scale.id},
                {"type": "post", "id": post_id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
