"""
Executor de acoes relacionadas a rondas de inspecao.

Acoes suportadas:
- CREATE_ROUND: Criar nova ronda de inspecao
- START_ROUND: Iniciar ronda (mudar status para EM_ANDAMENTO)
- COMPLETE_ROUND: Completar ronda (mudar status para CONCLUIDA)
- REGISTER_CHECKPOINT: Registrar checkpoint em posto durante ronda
- PAUSE_ROUND: Pausar ronda em andamento
- RESUME_ROUND: Retomar ronda pausada

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from modules.operacional.inspection_rounds.models import (
    CheckpointStatus,
    CheckpointType,
    InspectionRound,
    InspectionRoundStatus,
    InspectorRole,
)
from modules.operacional.inspection_rounds.repositories import InspectionRoundRepository
from modules.operacional.inspection_rounds.schemas import (
    CheckpointCreate,
    CompleteRoundRequest,
    InspectionRoundCreate,
    StartRoundRequest,
)
from modules.operacional.inspection_rounds.services.inspection_round_service import (
    InspectionRoundService,
)

from ..action_schemas import ActionPreview, ActionRequest, ActionResult
from ..action_types import ActionStatus
from .base_executor import BaseActionExecutor

# Import opcional de GeolocationService para validacao de checkpoint
try:
    from modules.operacional.services.geolocation_service import (
        GeolocationService,
        GeoPoint,
    )

    _HAS_GEO_SERVICE = True
except ImportError:
    _HAS_GEO_SERVICE = False

logger = logging.getLogger(__name__)


# =============================================================================
# Action types para rondas de inspecao
# Esses tipos complementam o ActionType existente.
# Devem ser verificados por string para nao modificar o enum original.
# =============================================================================
INSPECTION_ACTION_TYPES = {
    "create_round": "create_round",
    "start_round": "start_round",
    "complete_round": "complete_round",
}

# Novos action types para checkpoints e controle de ronda
INSPECTION_REGISTER_CHECKPOINT = "register_checkpoint"
INSPECTION_PAUSE_ROUND = "pause_round"
INSPECTION_RESUME_ROUND = "resume_round"


class InspectionActionExecutor(BaseActionExecutor):
    """Executor para acoes de rondas de inspecao."""

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para acao de ronda de inspecao."""
        action_type_value = request.action_type
        # Suporta tanto ActionType enum quanto string
        action_str = action_type_value.value if hasattr(action_type_value, "value") else str(action_type_value)

        try:
            if action_str == INSPECTION_ACTION_TYPES["create_round"]:
                return await self._create_round_preview(request)
            elif action_str == INSPECTION_ACTION_TYPES["start_round"]:
                return await self._start_round_preview(request)
            elif action_str == INSPECTION_ACTION_TYPES["complete_round"]:
                return await self._complete_round_preview(request)
            elif action_str == INSPECTION_REGISTER_CHECKPOINT:
                return await self._register_checkpoint_preview(request)
            elif action_str == INSPECTION_PAUSE_ROUND:
                return await self._pause_round_preview(request)
            elif action_str == INSPECTION_RESUME_ROUND:
                return await self._resume_round_preview(request)
            else:
                raise ValueError(f"Acao nao suportada: {action_str}")
        except Exception as e:
            logger.error(f"Erro ao criar preview para {action_str}: {e}")
            return ActionPreview(
                action_id=str(uuid4()),
                action_type=request.action_type,
                title="Erro ao gerar preview",
                description=str(e),
                affected_entities=[],
                changes_summary=[],
                warnings=[f"Erro: {e}"],
                required_permission="inspection_rounds:create",
                user_has_permission=False,
                parameters=request.parameters,
                can_be_undone=False,
                requires_confirmation=True,
            )

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa acao de ronda de inspecao."""
        action_type_value = request.action_type
        action_str = action_type_value.value if hasattr(action_type_value, "value") else str(action_type_value)
        started_at = datetime.utcnow()

        try:
            if action_str == INSPECTION_ACTION_TYPES["create_round"]:
                result = await self._execute_create_round(request, action_id, started_at)
            elif action_str == INSPECTION_ACTION_TYPES["start_round"]:
                result = await self._execute_start_round(request, action_id, started_at)
            elif action_str == INSPECTION_ACTION_TYPES["complete_round"]:
                result = await self._execute_complete_round(request, action_id, started_at)
            elif action_str == INSPECTION_REGISTER_CHECKPOINT:
                result = await self._execute_register_checkpoint(request, action_id, started_at)
            elif action_str == INSPECTION_PAUSE_ROUND:
                result = await self._execute_pause_round(request, action_id, started_at)
            elif action_str == INSPECTION_RESUME_ROUND:
                result = await self._execute_resume_round(request, action_id, started_at)
            else:
                raise ValueError(f"Acao nao suportada: {action_str}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar acao {action_str}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=request.action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar acao: {action_str}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # ==========================================================================
    # HELPER - Buscar ronda por ID ou codigo
    # ==========================================================================

    async def _find_round(self, params: dict[str, Any]) -> InspectionRound | None:
        """Busca ronda por ID ou codigo a partir dos parametros."""
        round_id = params.get("round_id")
        round_code = params.get("round_code")

        repo = InspectionRoundRepository(self.db)
        inspection_round = None

        try:
            if round_id:
                inspection_round = await repo.get_by_id(round_id)
            elif round_code:
                inspection_round = await repo.get_by_code(round_code)
        except Exception as e:
            logger.warning(f"Erro ao buscar ronda: {e}")

        return inspection_round

    # ==========================================================================
    # PREVIEW METHODS
    # ==========================================================================

    async def _create_round_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para criacao de ronda."""
        params = request.parameters
        inspector_name = params.get("inspector_name", "Nao informado")
        inspector_role = params.get("inspector_role", InspectorRole.SUPERVISOR_OPERACIONAL.value)
        scheduled_date = params.get("scheduled_date")
        observations = params.get("observations", "")

        changes_summary = []
        warnings = []
        affected_entities = []

        # Validar parametros
        if not params.get("inspector_id"):
            warnings.append("Inspetor nao informado")
        if not params.get("tenant_id"):
            warnings.append("Tenant nao informado")

        # Exibir cargo do inspetor
        role_display = {
            InspectorRole.GERENTE_OPERACIONAL.value: "Gerente Operacional",
            InspectorRole.SUPERVISOR_OPERACIONAL.value: "Supervisor Operacional",
            InspectorRole.INSPETOR_OPERACIONAL.value: "Inspetor Operacional",
            InspectorRole.LIDER_SERVICO.value: "Lider de Servico",
        }

        changes_summary.append(f"Inspetor: {inspector_name}")
        changes_summary.append(f"Cargo: {role_display.get(inspector_role, inspector_role)}")

        if scheduled_date:
            if isinstance(scheduled_date, str):
                changes_summary.append(f"Data agendada: {scheduled_date}")
            else:
                changes_summary.append(f"Data agendada: {scheduled_date.strftime('%d/%m/%Y %H:%M')}")
        else:
            warnings.append("Data de agendamento nao informada")

        posts_to_visit = params.get("posts_to_visit", [])
        if posts_to_visit:
            changes_summary.append(f"Postos a visitar: {len(posts_to_visit)}")
        else:
            warnings.append("Nenhum posto definido para visita")

        if observations:
            changes_summary.append(f"Observacoes: {observations[:100]}...")

        title = "Criar Ronda de Inspecao"
        description = f"Criar ronda para {inspector_name} ({role_display.get(inspector_role, inspector_role)})"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="inspection_rounds:create",
            user_has_permission=True,  # Verificado pelo middleware
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _start_round_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para inicio de ronda."""
        params = request.parameters
        round_id = params.get("round_id")
        round_code = params.get("round_code")

        warnings = []
        affected_entities = []
        changes_summary = []

        # Buscar ronda
        repo = InspectionRoundRepository(self.db)
        inspection_round = None

        try:
            if round_id:
                inspection_round = await repo.get_by_id(round_id)
            elif round_code:
                inspection_round = await repo.get_by_code(round_code)
        except Exception as e:
            logger.warning(f"Erro ao buscar ronda para preview: {e}")

        if not inspection_round:
            warnings.append("Ronda nao encontrada")
            title = "Iniciar Ronda"
            description = "Ronda nao encontrada"
        else:
            affected_entities.append(
                {
                    "type": "inspection_round",
                    "id": inspection_round.id,
                    "code": inspection_round.code,
                }
            )

            changes_summary.append(f"Ronda: {inspection_round.code}")
            changes_summary.append(f"Inspetor: {inspection_round.inspector_name}")
            changes_summary.append(f"Status atual: {inspection_round.status_display}")
            changes_summary.append("Novo status: Em Andamento")

            if inspection_round.status != InspectionRoundStatus.AGENDADA.value:
                if inspection_round.status == InspectionRoundStatus.EM_ANDAMENTO.value:
                    warnings.append("Ronda ja esta em andamento")
                elif inspection_round.status == InspectionRoundStatus.CONCLUIDA.value:
                    warnings.append("Ronda ja foi concluida")
                elif inspection_round.status == InspectionRoundStatus.CANCELADA.value:
                    warnings.append("Ronda esta cancelada")
                else:
                    warnings.append(f"Status atual ({inspection_round.status}) pode nao permitir inicio")

            posts_count = len(inspection_round.posts_to_visit or [])
            if posts_count > 0:
                changes_summary.append(f"Postos a visitar: {posts_count}")
            else:
                warnings.append("Nenhum posto definido para visita")

            title = f"Iniciar Ronda - {inspection_round.code}"
            description = f"Iniciar ronda {inspection_round.code} de {inspection_round.inspector_name}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="inspection_rounds:start",
            user_has_permission=True,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _complete_round_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para conclusao de ronda."""
        params = request.parameters
        round_id = params.get("round_id")
        round_code = params.get("round_code")
        summary = params.get("summary", "")

        warnings = []
        affected_entities = []
        changes_summary = []

        repo = InspectionRoundRepository(self.db)
        inspection_round = None

        try:
            if round_id:
                inspection_round = await repo.get_by_id(round_id)
            elif round_code:
                inspection_round = await repo.get_by_code(round_code)
        except Exception as e:
            logger.warning(f"Erro ao buscar ronda para preview de conclusao: {e}")

        if not inspection_round:
            warnings.append("Ronda nao encontrada")
            title = "Completar Ronda"
            description = "Ronda nao encontrada"
        else:
            affected_entities.append(
                {
                    "type": "inspection_round",
                    "id": inspection_round.id,
                    "code": inspection_round.code,
                }
            )

            changes_summary.append(f"Ronda: {inspection_round.code}")
            changes_summary.append(f"Inspetor: {inspection_round.inspector_name}")
            changes_summary.append(f"Status atual: {inspection_round.status_display}")
            changes_summary.append("Novo status: Concluida")
            changes_summary.append(f"Checkpoints realizados: {inspection_round.total_checkpoints}")
            changes_summary.append(f"Ocorrencias registradas: {inspection_round.total_occurrences}")

            if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
                if inspection_round.status == InspectionRoundStatus.CONCLUIDA.value:
                    warnings.append("Ronda ja foi concluida")
                elif inspection_round.status == InspectionRoundStatus.AGENDADA.value:
                    warnings.append("Ronda ainda nao foi iniciada")
                else:
                    warnings.append(
                        f"Ronda no status '{inspection_round.status_display}' nao pode ser concluida diretamente"
                    )

            # Verificar postos nao visitados
            remaining = inspection_round.posts_remaining
            if remaining:
                warnings.append(f"{len(remaining)} postos ainda nao visitados")

            if summary:
                changes_summary.append(f"Resumo: {summary[:100]}...")

            title = f"Completar Ronda - {inspection_round.code}"
            description = f"Concluir ronda {inspection_round.code} de {inspection_round.inspector_name}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="inspection_rounds:complete",
            user_has_permission=True,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    # ==========================================================================
    # EXECUTE METHODS
    # ==========================================================================

    async def _execute_create_round(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criacao de ronda de inspecao."""
        params = request.parameters

        service = InspectionRoundService(self.db)

        create_data = InspectionRoundCreate(
            tenant_id=params["tenant_id"],
            inspector_id=params["inspector_id"],
            inspector_name=params["inspector_name"],
            inspector_role=params.get("inspector_role", InspectorRole.SUPERVISOR_OPERACIONAL.value),
            scheduled_date=params.get("scheduled_date"),
            posts_to_visit=params.get("posts_to_visit"),
            observations=params.get("observations"),
        )

        inspection_round = await service.create(create_data)

        logger.info(f"Ronda criada via Bartolo: {inspection_round.code}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ronda {inspection_round.code} criada com sucesso",
            details={
                "round_id": inspection_round.id,
                "code": inspection_round.code,
                "inspector_name": inspection_round.inspector_name,
                "inspector_role": inspection_round.inspector_role,
                "status": inspection_round.status,
                "scheduled_date": inspection_round.scheduled_date.isoformat()
                if inspection_round.scheduled_date
                else None,
                "posts_to_visit": inspection_round.posts_to_visit,
            },
            affected_entities=[
                {"type": "inspection_round", "id": inspection_round.id, "code": inspection_round.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_start_round(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa inicio de ronda."""
        params = request.parameters
        round_id = params.get("round_id")
        round_code = params.get("round_code")

        service = InspectionRoundService(self.db)

        # Buscar ronda por ID ou codigo
        if round_id:
            inspection_round = await service.get_by_id(round_id)
        elif round_code:
            inspection_round = await service.get_by_code(round_code)
        else:
            raise ValueError("round_id ou round_code deve ser informado")

        # Preparar dados de inicio
        start_data = None
        if params.get("latitude") or params.get("longitude"):
            start_data = StartRoundRequest(
                latitude=params.get("latitude"),
                longitude=params.get("longitude"),
            )

        # Iniciar ronda
        inspection_round = await service.start_round(inspection_round.id, start_data)

        logger.info(f"Ronda iniciada via Bartolo: {inspection_round.code}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ronda {inspection_round.code} iniciada com sucesso",
            details={
                "round_id": inspection_round.id,
                "code": inspection_round.code,
                "status": inspection_round.status,
                "started_at": inspection_round.started_at.isoformat() if inspection_round.started_at else None,
                "inspector_name": inspection_round.inspector_name,
                "posts_to_visit": len(inspection_round.posts_to_visit or []),
            },
            affected_entities=[
                {"type": "inspection_round", "id": inspection_round.id, "code": inspection_round.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_complete_round(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa conclusao de ronda."""
        params = request.parameters
        round_id = params.get("round_id")
        round_code = params.get("round_code")

        service = InspectionRoundService(self.db)

        # Buscar ronda por ID ou codigo
        if round_id:
            inspection_round = await service.get_by_id(round_id)
        elif round_code:
            inspection_round = await service.get_by_code(round_code)
        else:
            raise ValueError("round_id ou round_code deve ser informado")

        # Preparar dados de conclusao
        complete_data = None
        if params.get("summary") or params.get("latitude") or params.get("longitude"):
            complete_data = CompleteRoundRequest(
                summary=params.get("summary"),
                latitude=params.get("latitude"),
                longitude=params.get("longitude"),
            )

        # Concluir ronda
        inspection_round = await service.complete_round(inspection_round.id, complete_data)

        logger.info(
            f"Ronda concluida via Bartolo: {inspection_round.code} - {inspection_round.total_occurrences} ocorrencias"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ronda {inspection_round.code} concluida com sucesso",
            details={
                "round_id": inspection_round.id,
                "code": inspection_round.code,
                "status": inspection_round.status,
                "started_at": inspection_round.started_at.isoformat() if inspection_round.started_at else None,
                "completed_at": inspection_round.completed_at.isoformat() if inspection_round.completed_at else None,
                "duration_minutes": inspection_round.duration_minutes,
                "inspector_name": inspection_round.inspector_name,
                "total_checkpoints": inspection_round.total_checkpoints,
                "total_occurrences": inspection_round.total_occurrences,
                "total_disciplinary_actions": inspection_round.total_disciplinary_actions,
                "total_employees_checked": inspection_round.total_employees_checked,
                "posts_visited": len(inspection_round.posts_visited or []),
                "posts_total": len(inspection_round.posts_to_visit or []),
                "progress": inspection_round.progress_percentage,
                "summary": inspection_round.summary,
            },
            affected_entities=[
                {"type": "inspection_round", "id": inspection_round.id, "code": inspection_round.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==========================================================================
    # REGISTER CHECKPOINT - Preview e Execucao
    # ==========================================================================

    async def _register_checkpoint_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para registro de checkpoint durante ronda."""
        params = request.parameters

        warnings: list[str] = []
        affected_entities: list[dict[str, Any]] = []
        changes_summary: list[str] = []

        # Buscar ronda
        inspection_round = await self._find_round(params)

        if not inspection_round:
            warnings.append("Ronda nao encontrada")
            title = "Registrar Checkpoint"
            description = "Ronda nao encontrada"
        else:
            affected_entities.append(
                {
                    "type": "inspection_round",
                    "id": inspection_round.id,
                    "code": inspection_round.code,
                }
            )

            changes_summary.append(f"Ronda: {inspection_round.code}")
            changes_summary.append(f"Inspetor: {inspection_round.inspector_name}")
            changes_summary.append(f"Status da ronda: {inspection_round.status_display}")

            # Verificar se ronda esta em andamento
            if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
                if inspection_round.status == InspectionRoundStatus.PAUSADA.value:
                    warnings.append("Ronda esta pausada. Retome antes de registrar checkpoints.")
                elif inspection_round.status == InspectionRoundStatus.CONCLUIDA.value:
                    warnings.append("Ronda ja foi concluida")
                elif inspection_round.status == InspectionRoundStatus.CANCELADA.value:
                    warnings.append("Ronda esta cancelada")
                else:
                    warnings.append(f"Ronda no status '{inspection_round.status_display}' nao permite checkpoints")

            # Dados do checkpoint
            post_id = params.get("post_id")
            post_name = params.get("post_name", "Nao informado")
            checkpoint_type = params.get("checkpoint_type", CheckpointType.VERIFICACAO_POSTO.value)
            status = params.get("status", CheckpointStatus.CONFORME.value)
            observations = params.get("observations", "")
            photos = params.get("photos", [])
            latitude = params.get("latitude")
            longitude = params.get("longitude")

            changes_summary.append(f"Posto: {post_name}")

            # Display do tipo de checkpoint
            type_display = {
                CheckpointType.VERIFICACAO_POSTO.value: "Verificacao de Posto",
                CheckpointType.VERIFICACAO_FUNCIONARIO.value: "Verificacao de Funcionario",
                CheckpointType.REGISTRO_OCORRENCIA.value: "Registro de Ocorrencia",
                CheckpointType.MEDIDA_DISCIPLINAR.value: "Medida Disciplinar",
                CheckpointType.OBSERVACAO_GERAL.value: "Observacao Geral",
                CheckpointType.FOTO_EVIDENCIA.value: "Foto/Evidencia",
            }
            changes_summary.append(f"Tipo: {type_display.get(checkpoint_type, checkpoint_type)}")

            # Display do status do checkpoint
            status_display = {
                CheckpointStatus.CONFORME.value: "Conforme",
                CheckpointStatus.NAO_CONFORME.value: "Nao Conforme",
                CheckpointStatus.PENDENTE.value: "Pendente",
                CheckpointStatus.COM_OCORRENCIA.value: "Com Ocorrencia",
            }
            changes_summary.append(f"Status checkpoint: {status_display.get(status, status)}")

            if status == CheckpointStatus.NAO_CONFORME.value:
                description_text = params.get("description", "")
                if description_text:
                    changes_summary.append(f"Descricao nao-conformidade: {description_text[:100]}...")
                else:
                    warnings.append("Checkpoint nao conforme sem descricao")

                infraction_category = params.get("infraction_category")
                if infraction_category:
                    changes_summary.append(f"Categoria infracao: {infraction_category}")
                infraction_severity = params.get("infraction_severity")
                if infraction_severity:
                    changes_summary.append(f"Severidade: {infraction_severity}")

            if observations:
                changes_summary.append(f"Observacoes: {observations[:100]}...")

            if photos:
                changes_summary.append(f"Fotos: {len(photos)} anexada(s)")

            # Validacao GPS do checkpoint
            if latitude is not None and longitude is not None:
                changes_summary.append(f"GPS: {latitude:.6f}, {longitude:.6f}")

                # Validar distancia do posto se possivel
                if _HAS_GEO_SERVICE and post_id:
                    try:
                        from modules.operacional.repositories.post_repository import PostRepository

                        post_repo = PostRepository(self.db)
                        post = await post_repo.get_by_id(post_id)
                        if post:
                            post_lat = getattr(post, "latitude", None)
                            post_lon = getattr(post, "longitude", None)
                            if post_lat and post_lon:
                                geo_service = GeolocationService()
                                user_point = GeoPoint(latitude=latitude, longitude=longitude)
                                post_point = GeoPoint(latitude=post_lat, longitude=post_lon)
                                distance = geo_service.calculate_distance(user_point, post_point)
                                changes_summary.append(f"Distancia do posto: {distance:.0f}m")
                                if distance > 200:
                                    warnings.append(f"Inspetor a {distance:.0f}m do posto (distancia elevada)")
                    except Exception as e:
                        logger.warning(f"Erro ao calcular distancia GPS no checkpoint: {e}")
            else:
                changes_summary.append("GPS: Nao fornecido")

            # Progresso da ronda
            total_posts = len(inspection_round.posts_to_visit or [])
            visited = len(inspection_round.posts_visited or [])
            changes_summary.append(
                f"Progresso ronda: {visited}/{total_posts} postos ({inspection_round.progress_percentage:.0f}%)"
            )
            changes_summary.append(f"Checkpoints ja realizados: {inspection_round.total_checkpoints}")

            title = f"Registrar Checkpoint - {inspection_round.code}"
            description = f"Registrar checkpoint no posto {post_name} na ronda {inspection_round.code}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="inspection_rounds:checkpoint",
            user_has_permission=True,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _execute_register_checkpoint(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa registro de checkpoint durante ronda."""
        params = request.parameters
        round_id = params.get("round_id")
        round_code = params.get("round_code")

        service = InspectionRoundService(self.db)

        # Buscar ronda por ID ou codigo
        if round_id:
            inspection_round = await service.get_by_id(round_id)
        elif round_code:
            inspection_round = await service.get_by_code(round_code)
        else:
            raise ValueError("round_id ou round_code deve ser informado")

        # Montar dados do checkpoint
        checkpoint_data = CheckpointCreate(
            post_id=params.get("post_id"),
            post_name=params.get("post_name"),
            client_id=params.get("client_id"),
            client_name=params.get("client_name"),
            checkpoint_type=params.get("checkpoint_type", CheckpointType.VERIFICACAO_POSTO.value),
            status=params.get("status", CheckpointStatus.CONFORME.value),
            employee_id=params.get("employee_id"),
            employee_name=params.get("employee_name"),
            employee_cpf=params.get("employee_cpf"),
            employee_position=params.get("employee_position"),
            title=params.get("title"),
            description=params.get("description"),
            observations=params.get("observations"),
            infraction_category=params.get("infraction_category"),
            infraction_severity=params.get("infraction_severity"),
            photos=params.get("photos"),
            latitude=params.get("latitude"),
            longitude=params.get("longitude"),
        )

        # Criar checkpoint via service
        checkpoint = await service.create_checkpoint(inspection_round.id, checkpoint_data)

        # Adicionar coordenada ao trajeto da ronda se GPS disponivel
        lat = params.get("latitude")
        lon = params.get("longitude")
        if lat is not None and lon is not None:
            try:
                inspection_round.add_route_coordinate(lat, lon)
                repo = InspectionRoundRepository(self.db)
                await repo.update(inspection_round)
            except Exception as e:
                logger.warning(f"Erro ao adicionar coordenada ao trajeto: {e}")

        logger.info(
            f"Checkpoint registrado via Bartolo: ronda={inspection_round.code}, "
            f"tipo={checkpoint.checkpoint_type}, status={checkpoint.status}"
        )

        # Detalhes de GPS para o resultado
        geo_details: dict[str, Any] = {}
        if lat is not None and lon is not None and _HAS_GEO_SERVICE:
            try:
                post_id = params.get("post_id")
                if post_id:
                    from modules.operacional.repositories.post_repository import PostRepository

                    post_repo = PostRepository(self.db)
                    post = await post_repo.get_by_id(post_id)
                    if post:
                        post_lat = getattr(post, "latitude", None)
                        post_lon = getattr(post, "longitude", None)
                        if post_lat and post_lon:
                            geo_service = GeolocationService()
                            user_point = GeoPoint(latitude=lat, longitude=lon)
                            post_point = GeoPoint(latitude=post_lat, longitude=post_lon)
                            distance = geo_service.calculate_distance(user_point, post_point)
                            geo_details["distance_meters"] = distance
            except Exception as e:
                logger.warning(f"Erro ao calcular distancia GPS no resultado: {e}")

        result_details = {
            "round_id": inspection_round.id,
            "round_code": inspection_round.code,
            "checkpoint_id": checkpoint.id,
            "checkpoint_type": checkpoint.checkpoint_type,
            "checkpoint_status": checkpoint.status,
            "post_id": checkpoint.post_id,
            "post_name": checkpoint.post_name,
            "sequence": checkpoint.sequence,
            "total_checkpoints": inspection_round.total_checkpoints,
            "progress": inspection_round.progress_percentage,
            "posts_visited": len(inspection_round.posts_visited or []),
            "posts_total": len(inspection_round.posts_to_visit or []),
        }

        if geo_details:
            result_details["geolocation"] = geo_details

        if checkpoint.status == CheckpointStatus.NAO_CONFORME.value:
            result_details["non_conformity"] = {
                "description": checkpoint.description,
                "infraction_category": checkpoint.infraction_category,
                "infraction_severity": checkpoint.infraction_severity,
            }

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Checkpoint registrado na ronda {inspection_round.code} (#{checkpoint.sequence})",
            details=result_details,
            affected_entities=[
                {"type": "inspection_round", "id": inspection_round.id, "code": inspection_round.code},
                {"type": "inspection_checkpoint", "id": checkpoint.id},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==========================================================================
    # PAUSE ROUND - Preview e Execucao
    # ==========================================================================

    async def _pause_round_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para pausar ronda."""
        params = request.parameters

        warnings: list[str] = []
        affected_entities: list[dict[str, Any]] = []
        changes_summary: list[str] = []

        inspection_round = await self._find_round(params)

        if not inspection_round:
            warnings.append("Ronda nao encontrada")
            title = "Pausar Ronda"
            description = "Ronda nao encontrada"
        else:
            affected_entities.append(
                {
                    "type": "inspection_round",
                    "id": inspection_round.id,
                    "code": inspection_round.code,
                }
            )

            changes_summary.append(f"Ronda: {inspection_round.code}")
            changes_summary.append(f"Inspetor: {inspection_round.inspector_name}")
            changes_summary.append(f"Status atual: {inspection_round.status_display}")
            changes_summary.append("Novo status: Pausada")
            changes_summary.append(f"Checkpoints realizados: {inspection_round.total_checkpoints}")
            changes_summary.append(f"Progresso: {inspection_round.progress_percentage:.0f}%")

            if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
                if inspection_round.status == InspectionRoundStatus.PAUSADA.value:
                    warnings.append("Ronda ja esta pausada")
                elif inspection_round.status == InspectionRoundStatus.CONCLUIDA.value:
                    warnings.append("Ronda ja foi concluida")
                elif inspection_round.status == InspectionRoundStatus.CANCELADA.value:
                    warnings.append("Ronda esta cancelada")
                elif inspection_round.status == InspectionRoundStatus.AGENDADA.value:
                    warnings.append("Ronda ainda nao foi iniciada")
                else:
                    warnings.append(f"Ronda no status '{inspection_round.status_display}' nao pode ser pausada")

            if inspection_round.started_at:
                elapsed = datetime.utcnow() - inspection_round.started_at
                elapsed_minutes = int(elapsed.total_seconds() / 60)
                changes_summary.append(f"Tempo em andamento: {elapsed_minutes} min")

            title = f"Pausar Ronda - {inspection_round.code}"
            description = f"Pausar ronda {inspection_round.code} de {inspection_round.inspector_name}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="inspection_rounds:pause",
            user_has_permission=True,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _execute_pause_round(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa pausa de ronda."""
        params = request.parameters
        round_id = params.get("round_id")
        round_code = params.get("round_code")

        service = InspectionRoundService(self.db)

        # Buscar ronda por ID ou codigo
        if round_id:
            inspection_round = await service.get_by_id(round_id)
        elif round_code:
            inspection_round = await service.get_by_code(round_code)
        else:
            raise ValueError("round_id ou round_code deve ser informado")

        # Pausar ronda
        inspection_round = await service.pause_round(inspection_round.id)

        logger.info(f"Ronda pausada via Bartolo: {inspection_round.code}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ronda {inspection_round.code} pausada com sucesso",
            details={
                "round_id": inspection_round.id,
                "code": inspection_round.code,
                "status": inspection_round.status,
                "paused_at": inspection_round.paused_at.isoformat() if inspection_round.paused_at else None,
                "inspector_name": inspection_round.inspector_name,
                "total_checkpoints": inspection_round.total_checkpoints,
                "progress": inspection_round.progress_percentage,
            },
            affected_entities=[
                {"type": "inspection_round", "id": inspection_round.id, "code": inspection_round.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==========================================================================
    # RESUME ROUND - Preview e Execucao
    # ==========================================================================

    async def _resume_round_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para retomar ronda pausada."""
        params = request.parameters

        warnings: list[str] = []
        affected_entities: list[dict[str, Any]] = []
        changes_summary: list[str] = []

        inspection_round = await self._find_round(params)

        if not inspection_round:
            warnings.append("Ronda nao encontrada")
            title = "Retomar Ronda"
            description = "Ronda nao encontrada"
        else:
            affected_entities.append(
                {
                    "type": "inspection_round",
                    "id": inspection_round.id,
                    "code": inspection_round.code,
                }
            )

            changes_summary.append(f"Ronda: {inspection_round.code}")
            changes_summary.append(f"Inspetor: {inspection_round.inspector_name}")
            changes_summary.append(f"Status atual: {inspection_round.status_display}")
            changes_summary.append("Novo status: Em Andamento")
            changes_summary.append(f"Checkpoints realizados: {inspection_round.total_checkpoints}")
            changes_summary.append(f"Progresso: {inspection_round.progress_percentage:.0f}%")

            if inspection_round.status != InspectionRoundStatus.PAUSADA.value:
                if inspection_round.status == InspectionRoundStatus.EM_ANDAMENTO.value:
                    warnings.append("Ronda ja esta em andamento")
                elif inspection_round.status == InspectionRoundStatus.CONCLUIDA.value:
                    warnings.append("Ronda ja foi concluida")
                elif inspection_round.status == InspectionRoundStatus.CANCELADA.value:
                    warnings.append("Ronda esta cancelada")
                elif inspection_round.status == InspectionRoundStatus.AGENDADA.value:
                    warnings.append("Ronda ainda nao foi iniciada (use start_round)")
                else:
                    warnings.append(f"Ronda no status '{inspection_round.status_display}' nao pode ser retomada")

            # Informar tempo pausado
            if inspection_round.paused_at:
                paused_duration = datetime.utcnow() - inspection_round.paused_at
                paused_minutes = int(paused_duration.total_seconds() / 60)
                changes_summary.append(f"Tempo pausada: {paused_minutes} min")

            # Postos restantes
            remaining = inspection_round.posts_remaining
            if remaining:
                changes_summary.append(f"Postos restantes: {len(remaining)}")

            title = f"Retomar Ronda - {inspection_round.code}"
            description = f"Retomar ronda {inspection_round.code} de {inspection_round.inspector_name}"

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission="inspection_rounds:resume",
            user_has_permission=True,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _execute_resume_round(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa retomada de ronda pausada."""
        params = request.parameters
        round_id = params.get("round_id")
        round_code = params.get("round_code")

        service = InspectionRoundService(self.db)

        # Buscar ronda por ID ou codigo
        if round_id:
            inspection_round = await service.get_by_id(round_id)
        elif round_code:
            inspection_round = await service.get_by_code(round_code)
        else:
            raise ValueError("round_id ou round_code deve ser informado")

        # Retomar ronda
        inspection_round = await service.resume_round(inspection_round.id)

        logger.info(f"Ronda retomada via Bartolo: {inspection_round.code}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Ronda {inspection_round.code} retomada com sucesso",
            details={
                "round_id": inspection_round.id,
                "code": inspection_round.code,
                "status": inspection_round.status,
                "inspector_name": inspection_round.inspector_name,
                "total_checkpoints": inspection_round.total_checkpoints,
                "progress": inspection_round.progress_percentage,
                "posts_remaining": len(inspection_round.posts_remaining),
                "posts_total": len(inspection_round.posts_to_visit or []),
            },
            affected_entities=[
                {"type": "inspection_round", "id": inspection_round.id, "code": inspection_round.code},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
