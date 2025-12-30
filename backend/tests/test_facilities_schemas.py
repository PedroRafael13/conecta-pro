"""
Testes unitários para os schemas do módulo Facilities.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from modules.facilities.schemas.area import (
    AreaCreate,
    AreaFilter,
    AreaResponse,
    AreaStats,
    AreaUpdate,
)
from modules.facilities.schemas.checklist import (
    ChecklistClone,
    ChecklistCreate,
    ChecklistFilter,
    ChecklistItemAnswer,
    ChecklistItemCreate,
    ChecklistStats,
    ChecklistUpdate,
)
from modules.facilities.schemas.inspection import (
    InspectionComplete,
    InspectionCreate,
    InspectionFilter,
    InspectionReview,
    InspectionStart,
    InspectionStats,
    InspectionUpdate,
)
from modules.facilities.schemas.maintenance import (
    MaintenanceApprove,
    MaintenanceComplete,
    MaintenanceCreate,
    MaintenanceFilter,
    MaintenanceReject,
    MaintenanceStats,
    MaintenanceUpdate,
)
from modules.facilities.schemas.service_request import (
    ServiceRequestAcknowledge,
    ServiceRequestAssign,
    ServiceRequestCancel,
    ServiceRequestComplete,
    ServiceRequestCreate,
    ServiceRequestFeedback,
    ServiceRequestFilter,
    ServiceRequestReject,
    ServiceRequestStats,
    ServiceRequestUpdate,
)


class TestAreaSchemas:
    """Testes para schemas de Area."""

    def test_area_create_valid(self):
        """Testa criação de área com dados válidos."""
        data = AreaCreate(
            name="Hall de Entrada",
            code="HALL-001",
            area_type="common_area",
            floor="Térreo",
            size_m2=Decimal("150.5"),
        )

        assert data.name == "Hall de Entrada"
        assert data.code == "HALL-001"
        assert data.area_type == "common_area"

    def test_area_create_minimal(self):
        """Testa criação de área com dados mínimos."""
        data = AreaCreate(
            name="Área Teste",
            area_type="other",
        )

        assert data.name == "Área Teste"
        assert data.code is None

    def test_area_create_invalid_name(self):
        """Testa validação de nome inválido."""
        with pytest.raises(ValidationError):
            AreaCreate(
                name="",
                area_type="other",
            )

    def test_area_update_partial(self):
        """Testa atualização parcial de área."""
        data = AreaUpdate(name="Novo Nome")

        assert data.name == "Novo Nome"
        assert data.code is None
        assert data.status is None

    def test_area_filter(self):
        """Testa filtro de área."""
        data = AreaFilter(
            search="hall",
            area_type="common_area",
            status="active",
        )

        assert data.search == "hall"
        assert data.area_type == "common_area"

    def test_area_stats(self):
        """Testa estatísticas de área."""
        data = AreaStats(
            total=100,
            by_type={"common_area": 30, "parking": 50, "technical": 20},
            by_status={"active": 90, "inactive": 10},
            total_size_m2=Decimal("5000.0"),
        )

        assert data.total == 100
        assert data.by_type["common_area"] == 30


class TestMaintenanceSchemas:
    """Testes para schemas de Maintenance."""

    def test_maintenance_create_valid(self):
        """Testa criação de manutenção com dados válidos."""
        data = MaintenanceCreate(
            title="Troca de lâmpadas",
            description="Substituir lâmpadas queimadas",
            maintenance_type="corrective",
            priority="medium",
            scheduled_date=date.today() + timedelta(days=7),
            estimated_hours=Decimal("2.0"),
            estimated_cost=Decimal("500.00"),
        )

        assert data.title == "Troca de lâmpadas"
        assert data.maintenance_type == "corrective"
        assert data.priority == "medium"

    def test_maintenance_complete(self):
        """Testa dados de conclusão de manutenção."""
        data = MaintenanceComplete(
            work_performed="Lâmpadas substituídas",
            actual_hours=Decimal("1.5"),
            actual_cost=Decimal("450.00"),
            labor_cost=Decimal("200.00"),
            material_cost=Decimal("250.00"),
            root_cause="Fim de vida útil",
        )

        assert data.work_performed == "Lâmpadas substituídas"
        assert data.actual_hours == Decimal("1.5")

    def test_maintenance_approve(self):
        """Testa dados de aprovação de manutenção."""
        data = MaintenanceApprove(notes="Aprovado conforme orçamento")

        assert data.notes == "Aprovado conforme orçamento"

    def test_maintenance_reject(self):
        """Testa dados de rejeição de manutenção."""
        data = MaintenanceReject(rejection_reason="Orçamento acima do limite")

        assert data.rejection_reason == "Orçamento acima do limite"

    def test_maintenance_stats(self):
        """Testa estatísticas de manutenção."""
        data = MaintenanceStats(
            total=50,
            by_type={"preventive": 30, "corrective": 20},
            by_status={"completed": 40, "pending": 10},
            by_priority={"high": 5, "medium": 30, "low": 15},
            total_cost=Decimal("25000.00"),
            avg_completion_hours=Decimal("3.5"),
            overdue_count=2,
        )

        assert data.total == 50
        assert data.overdue_count == 2


class TestInspectionSchemas:
    """Testes para schemas de Inspection."""

    def test_inspection_create_valid(self):
        """Testa criação de inspeção com dados válidos."""
        data = InspectionCreate(
            title="Vistoria Mensal",
            description="Inspeção de rotina",
            inspection_type="routine",
            scheduled_date=date.today() + timedelta(days=3),
        )

        assert data.title == "Vistoria Mensal"
        assert data.inspection_type == "routine"

    def test_inspection_start(self):
        """Testa dados de início de inspeção."""
        data = InspectionStart(
            inspector_id="insp-001",
            inspector_name="João Silva",
        )

        assert data.inspector_id == "insp-001"
        assert data.inspector_name == "João Silva"

    def test_inspection_complete(self):
        """Testa dados de conclusão de inspeção."""
        data = InspectionComplete(
            result="approved",
            score=Decimal("95.0"),
            findings="Tudo em conformidade",
            recommendations="Manter rotina de manutenção",
        )

        assert data.result == "approved"
        assert data.score == Decimal("95.0")

    def test_inspection_review(self):
        """Testa dados de revisão de inspeção."""
        data = InspectionReview(
            approved=True,
            internal_notes="Revisão concluída",
        )

        assert data.approved is True

    def test_inspection_stats(self):
        """Testa estatísticas de inspeção."""
        data = InspectionStats(
            total=80,
            by_type={"routine": 60, "special": 20},
            by_status={"completed": 70, "scheduled": 10},
            by_result={"approved": 65, "rejected": 5},
            avg_score=Decimal("88.5"),
            pending_review=3,
        )

        assert data.total == 80
        assert data.avg_score == Decimal("88.5")


class TestChecklistSchemas:
    """Testes para schemas de Checklist."""

    def test_checklist_create_valid(self):
        """Testa criação de checklist com dados válidos."""
        data = ChecklistCreate(
            name="Checklist de Limpeza",
            description="Verificação diária",
            category="cleaning",
            is_template=True,
        )

        assert data.name == "Checklist de Limpeza"
        assert data.is_template is True

    def test_checklist_item_create(self):
        """Testa criação de item de checklist."""
        data = ChecklistItemCreate(
            question="Piso limpo?",
            category="floor",
            is_required=True,
            order=1,
            weight=Decimal("1.0"),
        )

        assert data.question == "Piso limpo?"
        assert data.is_required is True

    def test_checklist_item_answer(self):
        """Testa resposta de item de checklist."""
        data = ChecklistItemAnswer(
            status="ok",
            answer="Sim",
            notes="Piso em perfeitas condições",
        )

        assert data.status == "ok"
        assert data.answer == "Sim"

    def test_checklist_clone(self):
        """Testa dados de clone de checklist."""
        data = ChecklistClone(
            name="Checklist Clonado",
            area_id="area-001",
        )

        assert data.name == "Checklist Clonado"

    def test_checklist_stats(self):
        """Testa estatísticas de checklist."""
        data = ChecklistStats(
            total=25,
            templates=5,
            by_status={"completed": 18, "in_progress": 7},
            by_category={"cleaning": 10, "security": 15},
            avg_completion_rate=Decimal("85.0"),
        )

        assert data.total == 25
        assert data.templates == 5


class TestServiceRequestSchemas:
    """Testes para schemas de ServiceRequest."""

    def test_service_request_create_valid(self):
        """Testa criação de solicitação com dados válidos."""
        data = ServiceRequestCreate(
            title="Vazamento na cozinha",
            description="Vazamento na pia",
            category="plumbing",
            priority="high",
            requester_name="Maria Santos",
            requester_email="maria@email.com",
        )

        assert data.title == "Vazamento na cozinha"
        assert data.category == "plumbing"
        assert data.priority == "high"

    def test_service_request_acknowledge(self):
        """Testa dados de reconhecimento de solicitação."""
        data = ServiceRequestAcknowledge(
            notes="Solicitação recebida, técnico será enviado",
        )

        assert "recebida" in data.notes

    def test_service_request_assign(self):
        """Testa dados de atribuição de solicitação."""
        data = ServiceRequestAssign(
            assigned_to="tech-001",
            assigned_team="Manutenção",
            scheduled_date=date.today() + timedelta(days=1),
            estimated_hours=Decimal("2.0"),
        )

        assert data.assigned_to == "tech-001"
        assert data.assigned_team == "Manutenção"

    def test_service_request_complete(self):
        """Testa dados de conclusão de solicitação."""
        data = ServiceRequestComplete(
            resolution="Vazamento corrigido",
            actual_hours=Decimal("1.5"),
            cost=Decimal("150.00"),
        )

        assert data.resolution == "Vazamento corrigido"

    def test_service_request_feedback(self):
        """Testa dados de feedback de solicitação."""
        data = ServiceRequestFeedback(
            rating=5,
            feedback="Excelente atendimento",
        )

        assert data.rating == 5
        assert data.feedback == "Excelente atendimento"

    def test_service_request_feedback_invalid_rating(self):
        """Testa validação de rating inválido."""
        with pytest.raises(ValidationError):
            ServiceRequestFeedback(
                rating=6,  # Máximo é 5
                feedback="Teste",
            )

    def test_service_request_stats(self):
        """Testa estatísticas de solicitação."""
        data = ServiceRequestStats(
            total=200,
            by_status={"completed": 150, "open": 50},
            by_priority={"high": 30, "medium": 100, "low": 70},
            by_category={"plumbing": 50, "electrical": 80, "general": 70},
            avg_resolution_hours=Decimal("4.5"),
            avg_rating=Decimal("4.2"),
            overdue_count=5,
        )

        assert data.total == 200
        assert data.avg_rating == Decimal("4.2")
