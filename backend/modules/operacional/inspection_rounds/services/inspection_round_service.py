"""
Service de Rondas de Inspecao.

Contem toda a logica de negocio para gerenciamento de rondas,
checkpoints, registro de ocorrencias e aplicacao de medidas disciplinares.

Author: Conecta PRO Team
Date: 2026-01-23
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import (
    InspectionRound,
    InspectionRoundStatus,
    InspectorRole,
    InspectionCheckpoint,
    CheckpointType,
    CheckpointStatus,
)
from ..repositories import InspectionRoundRepository
from ..schemas import (
    InspectionRoundCreate,
    InspectionRoundUpdate,
    InspectionRoundFilter,
    CheckpointCreate,
    CheckpointUpdate,
    StartRoundRequest,
    CompleteRoundRequest,
    RegisterOccurrenceRequest,
    ApplyDisciplinaryRequest,
    InspectionDashboardStats,
    InspectorStats,
)

logger = logging.getLogger(__name__)


class InspectionRoundNotFoundError(Exception):
    """Ronda nao encontrada."""
    pass


class InspectionRoundValidationError(Exception):
    """Erro de validacao."""
    pass


class InspectionRoundService:
    """Service para gerenciamento de Rondas de Inspecao."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = InspectionRoundRepository(db)

    # ==========================================================================
    # CRUD RONDAS
    # ==========================================================================

    def create(self, data: InspectionRoundCreate) -> InspectionRound:
        """Cria uma nova ronda de inspecao."""
        # Validar cargo do inspetor
        valid_roles = [r.value for r in InspectorRole]
        if data.inspector_role not in valid_roles:
            raise InspectionRoundValidationError(
                f"Cargo invalido. Valores validos: {valid_roles}"
            )

        # Gerar codigo
        year = datetime.utcnow().year
        sequence = self.repository.get_next_sequence(str(data.tenant_id), year)
        code = InspectionRound.generate_code(year, sequence)

        # Preparar dados
        round_data = {
            "code": code,
            "tenant_id": str(data.tenant_id),
            "inspector_id": str(data.inspector_id),
            "inspector_name": data.inspector_name,
            "inspector_role": data.inspector_role,
            "status": InspectionRoundStatus.AGENDADA.value,
            "scheduled_date": data.scheduled_date,
            "posts_to_visit": [str(p) for p in data.posts_to_visit] if data.posts_to_visit else [],
            "observations": data.observations,
            "created_by": str(data.inspector_id),
        }

        inspection_round = self.repository.create(round_data)
        logger.info(f"Ronda criada: {code} por {data.inspector_name}")

        return inspection_round

    def get_by_id(self, round_id: str) -> InspectionRound:
        """Busca ronda por ID."""
        inspection_round = self.repository.get_by_id(round_id)
        if not inspection_round:
            raise InspectionRoundNotFoundError(f"Ronda {round_id} nao encontrada")
        return inspection_round

    def get_by_code(self, code: str) -> InspectionRound:
        """Busca ronda por codigo."""
        inspection_round = self.repository.get_by_code(code)
        if not inspection_round:
            raise InspectionRoundNotFoundError(f"Ronda {code} nao encontrada")
        return inspection_round

    def list(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[InspectionRoundFilter] = None,
    ) -> Tuple[List[InspectionRound], int]:
        """Lista rondas com filtros."""
        return self.repository.list(tenant_id, skip, limit, filters)

    def update(self, round_id: str, data: InspectionRoundUpdate) -> InspectionRound:
        """Atualiza uma ronda."""
        inspection_round = self.get_by_id(round_id)

        # Validar se pode ser editada
        if inspection_round.status not in [
            InspectionRoundStatus.AGENDADA.value,
            InspectionRoundStatus.PAUSADA.value,
        ]:
            raise InspectionRoundValidationError(
                "Ronda nao pode ser editada no status atual"
            )

        # Atualizar campos
        if data.scheduled_date is not None:
            inspection_round.scheduled_date = data.scheduled_date
        if data.posts_to_visit is not None:
            inspection_round.posts_to_visit = [str(p) for p in data.posts_to_visit]
        if data.observations is not None:
            inspection_round.observations = data.observations
        if data.summary is not None:
            inspection_round.summary = data.summary

        return self.repository.update(inspection_round)

    def delete(self, round_id: str) -> None:
        """Remove uma ronda (soft delete)."""
        inspection_round = self.get_by_id(round_id)

        # Nao permitir deletar rondas em andamento
        if inspection_round.status == InspectionRoundStatus.EM_ANDAMENTO.value:
            raise InspectionRoundValidationError(
                "Nao e possivel deletar ronda em andamento"
            )

        self.repository.delete(inspection_round)
        logger.info(f"Ronda deletada: {inspection_round.code}")

    # ==========================================================================
    # WORKFLOW DA RONDA
    # ==========================================================================

    def start_round(
        self,
        round_id: str,
        data: Optional[StartRoundRequest] = None,
    ) -> InspectionRound:
        """Inicia uma ronda."""
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status not in [
            InspectionRoundStatus.AGENDADA.value,
            InspectionRoundStatus.PAUSADA.value,
        ]:
            raise InspectionRoundValidationError(
                f"Ronda no status '{inspection_round.status}' nao pode ser iniciada"
            )

        latitude = data.latitude if data else None
        longitude = data.longitude if data else None

        inspection_round.start(latitude, longitude)
        self.repository.update(inspection_round)

        logger.info(f"Ronda iniciada: {inspection_round.code}")
        return inspection_round

    def pause_round(self, round_id: str) -> InspectionRound:
        """Pausa uma ronda."""
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
            raise InspectionRoundValidationError("Ronda nao esta em andamento")

        inspection_round.pause()
        self.repository.update(inspection_round)

        logger.info(f"Ronda pausada: {inspection_round.code}")
        return inspection_round

    def resume_round(self, round_id: str) -> InspectionRound:
        """Retoma uma ronda pausada."""
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status != InspectionRoundStatus.PAUSADA.value:
            raise InspectionRoundValidationError("Ronda nao esta pausada")

        inspection_round.resume()
        self.repository.update(inspection_round)

        logger.info(f"Ronda retomada: {inspection_round.code}")
        return inspection_round

    def complete_round(
        self,
        round_id: str,
        data: Optional[CompleteRoundRequest] = None,
    ) -> InspectionRound:
        """Conclui uma ronda."""
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
            raise InspectionRoundValidationError("Ronda nao esta em andamento")

        summary = data.summary if data else None
        latitude = data.latitude if data else None
        longitude = data.longitude if data else None

        inspection_round.complete(summary, latitude, longitude)

        # Atualizar contadores finais
        checkpoints = self.repository.get_checkpoints_by_round(round_id)
        inspection_round.total_checkpoints = len(checkpoints)

        self.repository.update(inspection_round)

        logger.info(
            f"Ronda concluida: {inspection_round.code} - "
            f"{inspection_round.total_occurrences} ocorrencias, "
            f"{inspection_round.total_disciplinary_actions} medidas disciplinares"
        )
        return inspection_round

    def cancel_round(self, round_id: str, reason: Optional[str] = None) -> InspectionRound:
        """Cancela uma ronda."""
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status == InspectionRoundStatus.CONCLUIDA.value:
            raise InspectionRoundValidationError("Ronda ja concluida nao pode ser cancelada")

        inspection_round.cancel(reason)
        self.repository.update(inspection_round)

        logger.info(f"Ronda cancelada: {inspection_round.code}")
        return inspection_round

    # ==========================================================================
    # CHECKPOINTS
    # ==========================================================================

    def create_checkpoint(
        self,
        round_id: str,
        data: CheckpointCreate,
    ) -> InspectionCheckpoint:
        """Cria um checkpoint durante a ronda."""
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
            raise InspectionRoundValidationError("Ronda nao esta em andamento")

        # Obter proximo sequencial
        sequence = self.repository.get_next_checkpoint_sequence(round_id)

        checkpoint_data = {
            "inspection_round_id": round_id,
            "post_id": str(data.post_id) if data.post_id else None,
            "post_name": data.post_name,
            "client_id": str(data.client_id) if data.client_id else None,
            "client_name": data.client_name,
            "checkpoint_type": data.checkpoint_type,
            "status": data.status,
            "employee_id": str(data.employee_id) if data.employee_id else None,
            "employee_name": data.employee_name,
            "employee_cpf": data.employee_cpf,
            "employee_position": data.employee_position,
            "title": data.title,
            "description": data.description,
            "observations": data.observations,
            "infraction_category": data.infraction_category,
            "infraction_severity": data.infraction_severity,
            "photos": data.photos or [],
            "latitude": data.latitude,
            "longitude": data.longitude,
            "sequence": sequence,
            "created_by": inspection_round.inspector_id,
        }

        checkpoint = self.repository.create_checkpoint(checkpoint_data)

        # Atualizar contador e postos visitados
        inspection_round.total_checkpoints += 1
        if data.post_id:
            inspection_round.add_visited_post(str(data.post_id))

        # Incrementar contador de funcionarios se for verificacao de funcionario
        if data.checkpoint_type == CheckpointType.VERIFICACAO_FUNCIONARIO.value:
            inspection_round.increment_employees_checked()

        # Adicionar coordenada ao trajeto
        if data.latitude and data.longitude:
            inspection_round.add_route_coordinate(data.latitude, data.longitude)

        self.repository.update(inspection_round)

        logger.info(f"Checkpoint criado na ronda {inspection_round.code}: {data.checkpoint_type}")
        return checkpoint

    def update_checkpoint(
        self,
        checkpoint_id: str,
        data: CheckpointUpdate,
    ) -> InspectionCheckpoint:
        """Atualiza um checkpoint."""
        checkpoint = self.repository.get_checkpoint_by_id(checkpoint_id)
        if not checkpoint:
            raise InspectionRoundNotFoundError(f"Checkpoint {checkpoint_id} nao encontrado")

        if data.status is not None:
            checkpoint.status = data.status
        if data.description is not None:
            checkpoint.description = data.description
        if data.observations is not None:
            checkpoint.observations = data.observations
        if data.infraction_category is not None:
            checkpoint.infraction_category = data.infraction_category
        if data.infraction_severity is not None:
            checkpoint.infraction_severity = data.infraction_severity
        if data.photos is not None:
            checkpoint.photos = data.photos

        return self.repository.update_checkpoint(checkpoint)

    def get_checkpoints(self, round_id: str) -> List[InspectionCheckpoint]:
        """Lista checkpoints de uma ronda."""
        return self.repository.get_checkpoints_by_round(round_id)

    # ==========================================================================
    # REGISTRO DE OCORRENCIA
    # ==========================================================================

    def register_occurrence(
        self,
        round_id: str,
        data: RegisterOccurrenceRequest,
    ) -> Tuple[InspectionCheckpoint, dict]:
        """
        Registra uma ocorrencia durante a ronda.

        Cria um checkpoint do tipo REGISTRO_OCORRENCIA e uma Occurrence vinculada.
        """
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
            raise InspectionRoundValidationError("Ronda nao esta em andamento")

        # Importar servico de ocorrencias
        from modules.operacional.occurrences.services import OccurrenceService
        from modules.operacional.occurrences.schemas import OccurrenceCreate

        occurrence_service = OccurrenceService(self.db)

        # Criar ocorrencia
        occurrence_data = OccurrenceCreate(
            tenant_id=UUID(inspection_round.tenant_id),
            post_id=data.post_id,
            employee_involved_id=data.employee_id,
            title=data.title,
            description=data.description,
            category=data.category,
            severity=data.severity,
            type=data.type,
            priority=data.priority,
            reported_by_id=UUID(inspection_round.inspector_id),
            location_description=data.location_description,
            occurred_at=datetime.utcnow(),
        )

        occurrence = occurrence_service.create(occurrence_data)

        # Criar checkpoint vinculado
        sequence = self.repository.get_next_checkpoint_sequence(round_id)
        checkpoint_data = {
            "inspection_round_id": round_id,
            "post_id": str(data.post_id),
            "post_name": data.post_name,
            "checkpoint_type": CheckpointType.REGISTRO_OCORRENCIA.value,
            "status": CheckpointStatus.COM_OCORRENCIA.value,
            "employee_id": str(data.employee_id) if data.employee_id else None,
            "employee_name": data.employee_name,
            "employee_cpf": data.employee_cpf,
            "employee_position": data.employee_position,
            "title": data.title,
            "description": data.description,
            "occurrence_id": occurrence.id,
            "occurrence_code": occurrence.code,
            "infraction_category": data.category,
            "infraction_severity": data.severity,
            "photos": data.photos or [],
            "latitude": data.latitude,
            "longitude": data.longitude,
            "sequence": sequence,
            "created_by": inspection_round.inspector_id,
        }

        checkpoint = self.repository.create_checkpoint(checkpoint_data)

        # Atualizar contadores da ronda
        inspection_round.total_checkpoints += 1
        inspection_round.increment_occurrences()
        inspection_round.add_visited_post(str(data.post_id))

        if data.latitude and data.longitude:
            inspection_round.add_route_coordinate(data.latitude, data.longitude)

        self.repository.update(inspection_round)

        logger.info(
            f"Ocorrencia {occurrence.code} registrada na ronda {inspection_round.code}"
        )

        return checkpoint, {
            "occurrence_id": occurrence.id,
            "occurrence_code": occurrence.code,
        }

    # ==========================================================================
    # APLICACAO DE MEDIDA DISCIPLINAR
    # ==========================================================================

    def apply_disciplinary_action(
        self,
        round_id: str,
        data: ApplyDisciplinaryRequest,
    ) -> Tuple[InspectionCheckpoint, dict]:
        """
        Aplica medida disciplinar durante a ronda.

        Cria um checkpoint do tipo MEDIDA_DISCIPLINAR e uma DisciplinaryAction vinculada.
        """
        inspection_round = self.get_by_id(round_id)

        if inspection_round.status != InspectionRoundStatus.EM_ANDAMENTO.value:
            raise InspectionRoundValidationError("Ronda nao esta em andamento")

        # Importar servico de medidas disciplinares
        from modules.operacional.disciplinary.services import DisciplinaryService
        from modules.operacional.disciplinary.schemas import DisciplinaryActionCreate

        disciplinary_service = DisciplinaryService(self.db)

        # Criar medida disciplinar
        action_data = DisciplinaryActionCreate(
            tenant_id=UUID(inspection_round.tenant_id),
            action_type=data.action_type,
            employee_id=data.employee_id,
            employee_name=data.employee_name,
            employee_cpf=data.employee_cpf,
            employee_position=data.employee_position,
            employee_admission_date=data.employee_admission_date.date() if data.employee_admission_date else None,
            post_id=data.post_id,
            client_id=data.client_id,
            reason_category=data.reason_category,
            reason_description=data.reason_description,
            occurrence_id=data.occurrence_id,
            incident_date=data.incident_date.date() if data.incident_date else datetime.utcnow().date(),
            suspension_days=data.suspension_days,
            suspension_start_date=data.suspension_start_date.date() if data.suspension_start_date else None,
            witness_1_name=data.witness_1_name,
            witness_1_cpf=data.witness_1_cpf,
            witness_2_name=data.witness_2_name,
            witness_2_cpf=data.witness_2_cpf,
            created_by=UUID(inspection_round.inspector_id),
        )

        action = disciplinary_service.create(action_data)

        # Criar checkpoint vinculado
        sequence = self.repository.get_next_checkpoint_sequence(round_id)
        checkpoint_data = {
            "inspection_round_id": round_id,
            "post_id": str(data.post_id),
            "checkpoint_type": CheckpointType.MEDIDA_DISCIPLINAR.value,
            "status": CheckpointStatus.COM_OCORRENCIA.value,
            "employee_id": str(data.employee_id),
            "employee_name": data.employee_name,
            "employee_cpf": data.employee_cpf,
            "employee_position": data.employee_position,
            "title": f"Medida Disciplinar: {action.type_display_name}",
            "description": data.reason_description,
            "occurrence_id": str(data.occurrence_id) if data.occurrence_id else None,
            "disciplinary_action_id": action.id,
            "disciplinary_action_code": action.code,
            "disciplinary_action_type": action.action_type,
            "infraction_category": data.reason_category,
            "sequence": sequence,
            "created_by": inspection_round.inspector_id,
        }

        checkpoint = self.repository.create_checkpoint(checkpoint_data)

        # Se veio de um checkpoint existente, atualizar o vinculo
        if data.checkpoint_id:
            original_checkpoint = self.repository.get_checkpoint_by_id(str(data.checkpoint_id))
            if original_checkpoint:
                original_checkpoint.link_disciplinary_action(
                    action.id, action.code, action.action_type
                )
                self.repository.update_checkpoint(original_checkpoint)

        # Atualizar contadores da ronda
        inspection_round.total_checkpoints += 1
        inspection_round.increment_disciplinary_actions()
        inspection_round.add_visited_post(str(data.post_id))

        self.repository.update(inspection_round)

        logger.info(
            f"Medida disciplinar {action.code} aplicada na ronda {inspection_round.code}"
        )

        return checkpoint, {
            "disciplinary_action_id": action.id,
            "disciplinary_action_code": action.code,
            "disciplinary_action_type": action.action_type,
        }

    # ==========================================================================
    # DASHBOARD E ESTATISTICAS
    # ==========================================================================

    def get_dashboard_stats(
        self,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> InspectionDashboardStats:
        """Retorna estatisticas do dashboard."""
        # Contar por status
        status_counts = self.repository.count_by_status(tenant_id)

        # Rondas hoje
        today_rounds = self.repository.get_rounds_scheduled_today(tenant_id)
        in_progress = self.repository.get_rounds_in_progress(tenant_id)

        # Estatisticas por inspetor
        inspector_stats_data = self.repository.get_stats_by_inspector(tenant_id)
        inspector_stats = [
            InspectorStats(
                inspector_id=UUID(s['inspector_id']),
                inspector_name=s['inspector_name'],
                inspector_role=s['inspector_role'],
                total_rounds=s['total_rounds'],
                total_occurrences=s['total_occurrences'],
                total_disciplinary_actions=s['total_disciplinary_actions'],
                avg_duration_minutes=s['avg_duration_minutes'],
                last_round_date=s['last_round_date'],
            )
            for s in inspector_stats_data
        ]

        # Calcular totais
        total_rounds = sum(status_counts.values())
        rounds_completed = status_counts.get(InspectionRoundStatus.CONCLUIDA.value, 0)
        rounds_scheduled = status_counts.get(InspectionRoundStatus.AGENDADA.value, 0)

        # Totais de ocorrencias e medidas
        total_occurrences = sum(s.total_occurrences for s in inspector_stats)
        total_disciplinary = sum(s.total_disciplinary_actions for s in inspector_stats)

        return InspectionDashboardStats(
            total_rounds=total_rounds,
            rounds_in_progress=len(in_progress),
            rounds_completed=rounds_completed,
            rounds_scheduled=rounds_scheduled,
            total_occurrences=total_occurrences,
            occurrences_pending=0,  # TODO: buscar do servico de ocorrencias
            occurrences_resolved=0,
            total_disciplinary_actions=total_disciplinary,
            warnings_count=0,  # TODO: buscar do servico disciplinar
            suspensions_count=0,
            rounds_today=len(today_rounds),
            rounds_this_week=0,  # TODO: implementar
            rounds_this_month=0,
            top_inspectors=inspector_stats,
            most_visited_posts=[],  # TODO: implementar
            top_infraction_categories=[],
        )

    def get_rounds_by_inspector(
        self,
        inspector_id: str,
        tenant_id: str,
        limit: int = 50,
    ) -> List[InspectionRound]:
        """Retorna rondas de um inspetor."""
        return self.repository.get_rounds_by_inspector(inspector_id, tenant_id, limit)
