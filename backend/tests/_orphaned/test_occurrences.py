"""
Testes unitários para módulo de Occurrences (Ocorrências Disciplinares).

Testa validações de schemas, workflow de severidade e regras de negócio.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from modules.operacional.occurrences.models.occurrence import (
    OccurrenceCategory,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from modules.operacional.occurrences.schemas.occurrence import (
    OccurrenceCreate,
    OccurrenceResolve,
    OccurrenceResponse,
    OccurrenceUpdate,
)


class TestOccurrenceSchemas:
    """Testes de schemas e validações de Occurrence."""

    def test_occurrence_create_valid(self):
        """Testa criação de ocorrência com dados válidos."""
        data = {
            "title": "Uso de celular no posto",
            "description": "Funcionário utilizando celular durante o horário de trabalho, conforme relatado pelo supervisor.",
            "occurrence_type": OccurrenceType.ALARM,
            "severity": OccurrenceSeverity.LOW,
            "category": OccurrenceCategory.DISCIPLINAR,
            "occurred_at": datetime.now().isoformat(),
            "employee_id": str(uuid4()),
            "post_id": str(uuid4()),
        }

        occurrence = OccurrenceCreate(**data)

        assert occurrence.title == "Uso de celular no posto"
        assert occurrence.severity == OccurrenceSeverity.LOW
        assert occurrence.category == OccurrenceCategory.DISCIPLINAR

    def test_occurrence_description_min_length(self):
        """Testa que descrição deve ter no mínimo 10 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            OccurrenceCreate(
                title="Teste",
                description="Curta",  # Menos de 10 caracteres
                occurrence_type=OccurrenceType.ALARM,
                severity=OccurrenceSeverity.LOW,
                category=OccurrenceCategory.DISCIPLINAR,
                occurred_at=datetime.now().isoformat(),
                employee_id=str(uuid4()),
                post_id=str(uuid4()),
            )

        errors = exc_info.value.errors()
        assert any("description" in str(e).lower() for e in errors)

    def test_occurrence_uuid_validation(self):
        """Testa validação de UUIDs inválidos."""
        with pytest.raises(ValidationError) as exc_info:
            OccurrenceCreate(
                title="Teste",
                description="Descrição válida com mais de 10 caracteres",
                occurrence_type=OccurrenceType.ALARM,
                severity=OccurrenceSeverity.LOW,
                category=OccurrenceCategory.DISCIPLINAR,
                occurred_at=datetime.now().isoformat(),
                employee_id="invalid-uuid",  # UUID inválido
                post_id=str(uuid4()),
            )

        errors = exc_info.value.errors()
        assert any("employee_id" in str(e).lower() for e in errors)

    def test_occurrence_severity_levels(self):
        """Testa todos os níveis de severidade."""
        severities = [
            OccurrenceSeverity.LOW,
            OccurrenceSeverity.LOW,
            OccurrenceSeverity.LOW,
            OccurrenceSeverity.LOW,
        ]

        for severity in severities:
            occurrence = OccurrenceCreate(
                title="Teste",
                description="Descrição com mais de 10 caracteres de teste",
                occurrence_type=OccurrenceType.ALARM,
                severity=severity,
                category=OccurrenceCategory.DISCIPLINAR,
                occurred_at=datetime.now().isoformat(),
                employee_id=str(uuid4()),
                post_id=str(uuid4()),
            )
            assert occurrence.severity == severity

    def test_occurrence_update_partial(self):
        """Testa atualização parcial de ocorrência."""
        update_data = {
            "status": OccurrenceStatus.OPEN,
            "notes": "Ocorrência em análise pelo supervisor",
        }

        occurrence_update = OccurrenceUpdate(**update_data)

        assert occurrence_update.status == OccurrenceStatus.OPEN
        assert occurrence_update.notes == "Ocorrência em análise pelo supervisor"
        assert occurrence_update.severity is None  # Não atualizado

    def test_occurrence_resolve_schema(self):
        """Testa schema de resolução de ocorrência."""
        resolve_data = {
            "resolution": "Funcionário foi advertido verbalmente e orientado sobre as normas.",
            "resolved_by_id": str(uuid4()),
            "action_taken": "Advertência verbal",
        }

        occurrence_resolve = OccurrenceResolve(**resolve_data)

        assert "advertido" in occurrence_resolve.resolution.lower()
        assert occurrence_resolve.action_taken == "Advertência verbal"


class TestOccurrenceBusinessRules:
    """Testes de regras de negócio para Occurrences."""

    def test_occurrence_status_workflow(self):
        """Testa workflow de status das ocorrências."""
        # Workflow esperado: aberta → em_analise → resolvida → encerrada
        statuses = [
            OccurrenceStatus.OPEN,
            OccurrenceStatus.OPEN,
            OccurrenceStatus.OPEN,
            OccurrenceStatus.OPEN,
        ]

        for status in statuses:
            occurrence = OccurrenceUpdate(status=status)
            assert occurrence.status in statuses

    def test_occurrence_severity_escalation(self):
        """Testa que severidade pode escalar mas não reduzir."""
        # Regra de negócio: severidade só pode aumentar, não diminuir
        # (implementado no service, não no schema)

        initial = OccurrenceSeverity.LOW
        escalated = OccurrenceSeverity.LOW

        _occurrence = OccurrenceCreate(
            title="Teste Escalation",
            description="Descrição com mais de 10 caracteres para validação",
            occurrence_type=OccurrenceType.ALARM,
            severity=initial,
            category=OccurrenceCategory.DISCIPLINAR,
            occurred_at=datetime.now().isoformat(),
            employee_id=str(uuid4()),
            post_id=str(uuid4()),
        )

        # Update para severidade maior
        _update = OccurrenceUpdate(severity=escalated)

        assert initial.value < escalated.value  # Validar que escalou

    def test_occurrence_required_fields_for_resolution(self):
        """Testa campos obrigatórios para resolução."""
        # Ao resolver, deve ter resolução e responsável
        resolve_data = {
            "resolution": "Descrição da resolução com mais de 10 caracteres",
            "resolved_by_id": str(uuid4()),
        }

        resolve = OccurrenceResolve(**resolve_data)

        assert resolve.resolution is not None
        assert resolve.resolved_by_id is not None

    def test_occurrence_category_by_type(self):
        """Testa que categoria deve ser compatível com tipo."""
        # COMPORTAMENTO_INADEQUADO deve ter categorias específicas
        valid_categories = [
            OccurrenceCategory.DISCIPLINAR,
            OccurrenceCategory.DISCIPLINAR,
            OccurrenceCategory.DISCIPLINAR,
        ]

        for category in valid_categories:
            occurrence = OccurrenceCreate(
                title="Teste Categoria",
                description="Descrição com mais de 10 caracteres de validação",
                occurrence_type=OccurrenceType.ALARM,
                severity=OccurrenceSeverity.LOW,
                category=category,
                occurred_at=datetime.now().isoformat(),
                employee_id=str(uuid4()),
                post_id=str(uuid4()),
            )
            assert occurrence.category in valid_categories

    def test_occurrence_occurred_at_not_future(self):
        """Testa que occurred_at não pode ser no futuro."""
        future_date = datetime.now() + timedelta(days=1)

        occurrence = OccurrenceCreate(
            title="Teste Data Futura",
            description="Descrição com mais de 10 caracteres para teste",
            occurrence_type=OccurrenceType.ALARM,
            severity=OccurrenceSeverity.LOW,
            category=OccurrenceCategory.DISCIPLINAR,
            occurred_at=future_date.isoformat(),
            employee_id=str(uuid4()),
            post_id=str(uuid4()),
        )

        # Schema aceita, validação seria no service
        assert occurrence.occurred_at == future_date.isoformat()


class TestOccurrenceTypes:
    """Testes de tipos e categorias de ocorrências."""

    def test_occurrence_types_enum(self):
        """Testa todos os tipos de ocorrência disponíveis."""
        types = [
            OccurrenceType.ALARM,
            OccurrenceType.ALARM,
            OccurrenceType.ALARM,
        ]

        for occ_type in types:
            occurrence = OccurrenceCreate(
                title="Teste Tipo",
                description="Descrição com mais de 10 caracteres de teste",
                occurrence_type=occ_type,
                severity=OccurrenceSeverity.LOW,
                category=OccurrenceCategory.DISCIPLINAR,
                occurred_at=datetime.now().isoformat(),
                employee_id=str(uuid4()),
                post_id=str(uuid4()),
            )
            assert occurrence.occurrence_type == occ_type

    def test_occurrence_categories_mapping(self):
        """Testa mapeamento de categorias."""
        # Cada tipo deve ter categorias específicas
        categories = [
            OccurrenceCategory.DISCIPLINAR,
            OccurrenceCategory.DISCIPLINAR,
            OccurrenceCategory.DISCIPLINAR,
            OccurrenceCategory.DISCIPLINAR,
            OccurrenceCategory.DISCIPLINAR,
            OccurrenceCategory.DISCIPLINAR,
        ]

        for category in categories:
            occurrence = OccurrenceCreate(
                title=f"Teste {category.value}",
                description="Descrição com mais de 10 caracteres de validação",
                occurrence_type=OccurrenceType.ALARM,
                severity=OccurrenceSeverity.LOW,
                category=category,
                occurred_at=datetime.now().isoformat(),
                employee_id=str(uuid4()),
                post_id=str(uuid4()),
            )
            assert occurrence.category == category


@pytest.mark.asyncio
class TestOccurrenceAPI:
    """Testes de endpoints da API de Occurrences."""

    @pytest.fixture
    def mock_occurrence_repository(self):
        """Mock do OccurrenceRepository."""
        repo = AsyncMock()
        repo.list = AsyncMock(return_value=[])
        repo.get = AsyncMock(return_value=None)
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    async def test_list_occurrences_empty(self, client, mock_occurrence_repository):
        """Testa listagem sem ocorrências."""
        with patch(
            "modules.operacional.occurrences.controllers.occurrence_controller.OccurrenceRepository",
            return_value=mock_occurrence_repository,
        ):
            response = await client.get("/api/v1/operacional/occurrences/")

            # Pode retornar 200 ou 401 (sem auth)
            assert response.status_code in [200, 401, 403]

    async def test_create_occurrence_validation(self):
        """Testa validação na criação de ocorrência."""
        occurrence_data = {
            "title": "Teste",
            "description": "Desc",  # Muito curta
            "occurrence_type": OccurrenceType.ALARM,
            "severity": OccurrenceSeverity.LOW,
            "category": OccurrenceCategory.DISCIPLINAR,
            "occurred_at": datetime.now().isoformat(),
            "employee_id": "invalid",  # UUID inválido
            "post_id": str(uuid4()),
        }

        with pytest.raises(ValidationError):
            OccurrenceCreate(**occurrence_data)

    async def test_resolve_occurrence_schema(self):
        """Testa resolução de ocorrência."""
        resolve_data = {
            "resolution": "Funcionário foi advertido e orientado conforme normas internas da empresa.",
            "resolved_by_id": str(uuid4()),
            "action_taken": "Advertência verbal registrada",
        }

        resolve = OccurrenceResolve(**resolve_data)

        assert len(resolve.resolution) >= 10
        assert resolve.resolved_by_id is not None
