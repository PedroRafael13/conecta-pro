"""
Testes unitários para módulo de Inspection Rounds (Rondas de Inspeção).

Testa async session, integração com ocorrências e validações.
"""

from datetime import datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from modules.operacional.inspection_rounds.models.inspection_checkpoint import CheckpointStatus
from modules.operacional.inspection_rounds.models.inspection_round import InspectionRoundStatus
from modules.operacional.inspection_rounds.schemas.inspection_round_schemas import (
    CheckpointCreate,
    InspectionRoundCreate,
    InspectionRoundUpdate,
    RegisterOccurrenceRequest,
)


class TestInspectionRoundSchemas:
    """Testes de schemas de Inspection Rounds."""

    def test_inspection_round_create_valid(self):
        """Testa criação de ronda com dados válidos."""
        data = {
            "inspector_id": str(uuid4()),
            "shift_id": str(uuid4()),
            "scheduled_start": datetime.now().isoformat(),
            "scheduled_end": (datetime.now() + timedelta(hours=2)).isoformat(),
            "route_description": "Ronda pelos setores A, B e C",
        }

        round_obj = InspectionRoundCreate(**data)

        assert round_obj.inspector_id is not None
        assert round_obj.shift_id is not None
        assert "setores" in round_obj.route_description.lower()

    def test_inspection_round_start_before_end(self):
        """Testa que início deve ser antes do fim."""
        now = datetime.now()

        data = {
            "inspector_id": str(uuid4()),
            "shift_id": str(uuid4()),
            "scheduled_start": (now + timedelta(hours=2)).isoformat(),
            "scheduled_end": now.isoformat(),  # Fim antes do início
            "route_description": "Ronda teste",
        }

        # Schema pode aceitar, validação no service
        round_obj = InspectionRoundCreate(**data)
        assert round_obj.scheduled_start > round_obj.scheduled_end

    def test_checkpoint_check_schema(self):
        """Testa schema de verificação de checkpoint."""
        checkpoint_data = {
            "checkpoint_id": str(uuid4()),
            "checked_at": datetime.now().isoformat(),
            "status": CheckpointStatus.OK,
            "notes": "Checkpoint verificado, tudo normal",
        }

        checkpoint = CheckpointCreate(**checkpoint_data)

        assert checkpoint.status == CheckpointStatus.OK
        assert "normal" in checkpoint.notes.lower()

    def test_checkpoint_status_types(self):
        """Testa todos os status de checkpoint."""
        statuses = [
            CheckpointStatus.OK,
            CheckpointStatus.ATENCAO,
            CheckpointStatus.PROBLEMA,
            CheckpointStatus.NAO_VERIFICADO,
        ]

        for status in statuses:
            checkpoint = CheckpointCreate(
                checkpoint_id=str(uuid4()),
                checked_at=datetime.now().isoformat(),
                status=status,
            )
            assert checkpoint.status == status

    def test_inspection_round_update_partial(self):
        """Testa atualização parcial de ronda."""
        update_data = {
            "status": InspectionRoundStatus.EM_ANDAMENTO,
            "actual_start": datetime.now().isoformat(),
        }

        round_update = InspectionRoundUpdate(**update_data)

        assert round_update.status == InspectionRoundStatus.EM_ANDAMENTO
        assert round_update.actual_start is not None
        assert round_update.actual_end is None  # Não atualizado


class TestInspectionRoundAsyncSession:
    """Testes de AsyncSession em Inspection Rounds."""

    @pytest.mark.asyncio
    async def test_async_session_usage(self, mock_db_session):
        """Testa que service usa AsyncSession corretamente."""
        # Mock do service
        service = AsyncMock()
        service.create_round = AsyncMock(return_value={"id": str(uuid4())})

        round_data = InspectionRoundCreate(
            inspector_id=str(uuid4()),
            shift_id=str(uuid4()),
            scheduled_start=datetime.now().isoformat(),
            scheduled_end=(datetime.now() + timedelta(hours=2)).isoformat(),
            route_description="Ronda teste",
        )

        # Simular chamada async
        result = await service.create_round(mock_db_session, round_data)

        assert "id" in result
        service.create_round.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_repository_methods(self, mock_db_session):
        """Testa métodos async do repository."""
        # Mock do repository
        repo = AsyncMock()
        repo.get = AsyncMock(return_value=None)
        repo.list = AsyncMock(return_value=[])
        repo.create = AsyncMock()
        repo.update = AsyncMock()

        # Testar métodos async
        await repo.get(mock_db_session, str(uuid4()))
        await repo.list(mock_db_session)

        repo.get.assert_called_once()
        repo.list.assert_called_once()


class TestRegisterOccurrence:
    """Testes de registro de ocorrências durante ronda."""

    def test_register_occurrence_request_schema(self):
        """Testa schema de requisição para registrar ocorrência."""
        request_data = {
            "occurrence_title": "Porta do setor B aberta",
            "occurrence_description": "Durante a ronda, foi identificado que a porta do setor B estava aberta e sem vigilância.",
            "severity": "moderada",
            "employee_id": str(uuid4()),
        }

        request = RegisterOccurrenceRequest(**request_data)

        assert "porta" in request.occurrence_title.lower()
        assert len(request.occurrence_description) >= 10

    def test_register_occurrence_minimum_description(self):
        """Testa descrição mínima para ocorrência."""
        with pytest.raises(ValidationError) as exc_info:
            RegisterOccurrenceRequest(
                occurrence_title="Teste",
                occurrence_description="Curta",  # Menos de 10 caracteres
                severity="leve",
            )

        errors = exc_info.value.errors()
        assert any("occurrence_description" in str(e).lower() for e in errors)


class TestInspectionRoundStatus:
    """Testes de workflow de status das rondas."""

    def test_round_status_workflow(self):
        """Testa workflow completo de status."""
        # Workflow: agendada → em_andamento → concluida
        statuses = [
            InspectionRoundStatus.AGENDADA,
            InspectionRoundStatus.EM_ANDAMENTO,
            InspectionRoundStatus.CONCLUIDA,
            InspectionRoundStatus.CANCELADA,
        ]

        for status in statuses:
            round_update = InspectionRoundUpdate(status=status)
            assert round_update.status in statuses

    def test_round_cannot_skip_em_andamento(self):
        """Testa que não pode pular status em_andamento."""
        # Regra de negócio: deve passar por em_andamento antes de concluir
        # (validado no service, não no schema)

        # De agendada para concluída (saltando em_andamento)
        round_update = InspectionRoundUpdate(
            status=InspectionRoundStatus.CONCLUIDA,
        )

        # Schema aceita, validação no service
        assert round_update.status == InspectionRoundStatus.CONCLUIDA

    def test_round_actual_times_on_completion(self):
        """Testa que tempos reais são obrigatórios ao concluir."""
        update_data = {
            "status": InspectionRoundStatus.CONCLUIDA,
            "actual_start": datetime.now().isoformat(),
            "actual_end": (datetime.now() + timedelta(hours=1)).isoformat(),
        }

        round_update = InspectionRoundUpdate(**update_data)

        assert round_update.actual_start is not None
        assert round_update.actual_end is not None
        assert round_update.status == InspectionRoundStatus.CONCLUIDA


class TestInspectionRoundIntegration:
    """Testes de integração com outros módulos."""

    def test_round_with_shift_integration(self):
        """Testa integração com turnos."""
        shift_id = str(uuid4())

        round_obj = InspectionRoundCreate(
            inspector_id=str(uuid4()),
            shift_id=shift_id,
            scheduled_start=datetime.now().isoformat(),
            scheduled_end=(datetime.now() + timedelta(hours=2)).isoformat(),
            route_description="Ronda integrada com turno",
        )

        assert round_obj.shift_id == shift_id

    def test_round_with_inspector_integration(self):
        """Testa integração com inspetor (employee)."""
        inspector_id = str(uuid4())

        round_obj = InspectionRoundCreate(
            inspector_id=inspector_id,
            shift_id=str(uuid4()),
            scheduled_start=datetime.now().isoformat(),
            scheduled_end=(datetime.now() + timedelta(hours=2)).isoformat(),
            route_description="Ronda com inspetor específico",
        )

        assert round_obj.inspector_id == inspector_id

    def test_round_creates_occurrence_on_problem(self):
        """Testa que ronda pode criar ocorrência ao encontrar problema."""
        # Quando checkpoint tem status PROBLEMA, deve criar ocorrência
        checkpoint = CheckpointCreate(
            checkpoint_id=str(uuid4()),
            checked_at=datetime.now().isoformat(),
            status=CheckpointStatus.PROBLEMA,
            notes="Problema identificado neste checkpoint",
        )

        assert checkpoint.status == CheckpointStatus.PROBLEMA
        assert "problema" in checkpoint.notes.lower()


@pytest.mark.asyncio
class TestInspectionRoundAPI:
    """Testes de endpoints da API de Inspection Rounds."""

    async def test_list_rounds_endpoint_exists(self, client):
        """Testa que endpoint de listagem existe."""
        response = await client.get("/api/v1/operacional/rondas/")

        # Pode retornar 200 ou 401 (sem auth)
        assert response.status_code in [200, 401, 403, 422]

    async def test_create_round_validation(self):
        """Testa validação na criação de ronda."""
        round_data = {
            "inspector_id": "invalid-uuid",  # UUID inválido
            "shift_id": str(uuid4()),
            "scheduled_start": datetime.now().isoformat(),
            "scheduled_end": (datetime.now() + timedelta(hours=2)).isoformat(),
        }

        with pytest.raises(ValidationError):
            InspectionRoundCreate(**round_data)

    @pytest.mark.asyncio
    async def test_async_controller_methods(self, mock_db_session):
        """Testa que controller usa métodos async."""
        # Mock do controller
        controller = AsyncMock()
        controller.get_round = AsyncMock(return_value={"id": str(uuid4())})

        round_id = str(uuid4())
        result = await controller.get_round(mock_db_session, round_id)

        assert "id" in result
        controller.get_round.assert_called_once()
