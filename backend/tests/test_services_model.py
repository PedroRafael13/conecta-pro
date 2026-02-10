"""
Tests for Services Module - Models
Sprint 31: Gestão de Serviços
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.services.models import (
    ExecutionStatus,
    OrderPriority,
    OrderStatus,
    ReportType,
    ServiceCatalog,
    ServiceCategory,
    ServiceExecution,
    ServiceOrder,
    ServiceReport,
    ServiceStatus,
    ServiceType,
    SLAConfig,
    SLAMetricType,
)


class TestServiceCatalog:
    """Tests for ServiceCatalog model."""

    def test_create_service_catalog(self):
        """Test creating a service catalog."""
        service = ServiceCatalog(
            id=uuid4(),
            code="SRV-001",
            name="Manutenção Predial",
            category=ServiceCategory.SEGURANCA,
            service_type=ServiceType.PREVENTIVO,
            status=ServiceStatus.ATIVO,
            base_price=Decimal("500.00"),
        )

        assert service.name == "Manutenção Predial"
        assert service.category == ServiceCategory.SEGURANCA
        assert service.service_type == ServiceType.PREVENTIVO
        assert service.status == ServiceStatus.ATIVO
        assert service.base_price == Decimal("500.00")

    def test_service_activate(self):
        """Test activating a service."""
        service = ServiceCatalog(id=uuid4(), code="SRV-002", name="Limpeza", status=ServiceStatus.INATIVO)

        service.activate()

        assert service.status == ServiceStatus.ATIVO
        assert service.is_available is True

    def test_service_deactivate(self):
        """Test deactivating a service."""
        service = ServiceCatalog(id=uuid4(), code="SRV-003", name="Segurança", status=ServiceStatus.ATIVO)

        service.deactivate()

        assert service.status == ServiceStatus.INATIVO
        assert service.is_available is False

    def test_service_discontinue(self):
        """Test discontinuing a service."""
        service = ServiceCatalog(id=uuid4(), code="SRV-004", name="Consultoria", status=ServiceStatus.ATIVO)

        service.discontinue()

        assert service.status == ServiceStatus.DESCONTINUADO
        assert service.is_available is False

    def test_calculate_price_base(self):
        """Test calculating price with base price."""
        service = ServiceCatalog(id=uuid4(), code="SRV-005", name="Jardinagem", base_price=Decimal("200.00"))

        price = service.calculate_price()

        assert price == Decimal("200.00")

    def test_calculate_price_with_quantity(self):
        """Test calculating price with quantity."""
        service = ServiceCatalog(id=uuid4(), code="SRV-006", name="Piscina", unit_price=Decimal("50.00"))

        price = service.calculate_price(quantity=3)

        assert price == Decimal("150.00")

    def test_calculate_price_emergency(self):
        """Test calculating emergency price."""
        service = ServiceCatalog(
            id=uuid4(),
            code="SRV-007",
            name="Emergência",
            base_price=Decimal("100.00"),
            is_emergency_available=True,
            emergency_surcharge_percent=Decimal("50.00"),
        )

        price = service.calculate_price(is_emergency=True)

        assert price == Decimal("150.00")

    def test_update_metrics(self):
        """Test updating service metrics."""
        service = ServiceCatalog(
            id=uuid4(),
            code="SRV-008",
            name="Elevadores",
            total_orders=10,
            completed_orders=8,
            total_revenue=Decimal("5000.00"),
        )

        service.update_metrics(Decimal("600.00"), 5)

        assert service.total_orders == 11
        assert service.completed_orders == 9
        assert service.total_revenue == Decimal("5600.00")
        assert service.avg_rating is not None

    def test_completion_rate(self):
        """Test completion rate calculation."""
        service = ServiceCatalog(id=uuid4(), code="SRV-009", name="Portaria", total_orders=100, completed_orders=85)

        assert service.completion_rate == 85.0

    def test_completion_rate_no_orders(self):
        """Test completion rate with no orders."""
        service = ServiceCatalog(id=uuid4(), code="SRV-010", name="Novo Serviço", total_orders=0)

        assert service.completion_rate == 0.0


class TestServiceOrder:
    """Tests for ServiceOrder model."""

    def test_create_service_order(self):
        """Test creating a service order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0001",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Manutenção de Ar Condicionado",
            priority=OrderPriority.ALTA,
        )

        assert order.title == "Manutenção de Ar Condicionado"
        assert order.priority == OrderPriority.ALTA
        assert order.status == OrderStatus.RASCUNHO

    def test_order_submit(self):
        """Test submitting an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0002",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Limpeza Geral",
            status=OrderStatus.RASCUNHO,
        )

        order.submit()

        assert order.status == OrderStatus.PENDENTE

    def test_order_approve(self):
        """Test approving an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0003",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Segurança 24h",
            status=OrderStatus.PENDENTE,
        )

        order.approve()

        assert order.status == OrderStatus.APROVADA
        assert order.approved_at is not None

    def test_order_reject(self):
        """Test rejecting an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0004",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Jardinagem",
            status=OrderStatus.PENDENTE,
        )

        order.reject("Fora do escopo contratual")

        assert order.status == OrderStatus.REJEITADA
        assert order.rejection_reason == "Fora do escopo contratual"

    def test_order_schedule(self):
        """Test scheduling an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0005",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Piscina",
            status=OrderStatus.APROVADA,
        )

        schedule_date = date.today() + timedelta(days=3)
        order.schedule(schedule_date, "09:00", "12:00")

        assert order.status == OrderStatus.AGENDADA
        assert order.scheduled_date == schedule_date
        assert order.scheduled_time_start == "09:00"
        assert order.scheduled_time_end == "12:00"

    def test_order_start(self):
        """Test starting an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0006",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Elevadores",
            status=OrderStatus.AGENDADA,
        )

        order.start()

        assert order.status == OrderStatus.EM_ANDAMENTO
        assert order.started_at is not None

    def test_order_pause(self):
        """Test pausing an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0007",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Portaria",
            status=OrderStatus.EM_ANDAMENTO,
        )

        order.pause("Aguardando material")

        assert order.status == OrderStatus.PAUSADA
        assert order.pause_reason == "Aguardando material"
        assert order.paused_at is not None

    def test_order_resume(self):
        """Test resuming an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0008",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Administração",
            status=OrderStatus.PAUSADA,
        )

        order.resume()

        assert order.status == OrderStatus.EM_ANDAMENTO

    def test_order_complete(self):
        """Test completing an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0009",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Consultoria",
            status=OrderStatus.EM_ANDAMENTO,
            started_at=datetime.utcnow() - timedelta(hours=2),
        )

        order.complete()

        assert order.status == OrderStatus.CONCLUIDA
        assert order.completed_at is not None
        assert order.actual_duration_hours is not None

    def test_order_cancel(self):
        """Test canceling an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0010",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Tecnologia",
            status=OrderStatus.AGENDADA,
        )

        order.cancel("Cliente solicitou cancelamento")

        assert order.status == OrderStatus.CANCELADA
        assert order.cancellation_reason == "Cliente solicitou cancelamento"
        assert order.cancelled_at is not None

    def test_order_rate(self):
        """Test rating an order."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0011",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Eventos",
            status=OrderStatus.CONCLUIDA,
        )

        order.rate(5, "Excelente serviço!")

        assert order.rating == 5
        assert order.rating_feedback == "Excelente serviço!"
        assert order.rated_at is not None

    def test_order_is_overdue(self):
        """Test is_overdue property."""
        order = ServiceOrder(
            id=uuid4(),
            order_number="OS-2026-0012",
            service_id=uuid4(),
            client_id=uuid4(),
            title="Manutenção",
            status=OrderStatus.EM_ANDAMENTO,
            sla_resolution_deadline=datetime.utcnow() - timedelta(hours=1),
        )

        assert order.is_overdue is True

    def test_order_assign_technician(self):
        """Test assigning technician."""
        order = ServiceOrder(
            id=uuid4(), order_number="OS-2026-0013", service_id=uuid4(), client_id=uuid4(), title="Limpeza"
        )

        tech_id = uuid4()
        order.assign_technician(tech_id, "João Silva")

        assert order.assigned_technician_id == tech_id
        assert order.assigned_technician_name == "João Silva"


class TestServiceExecution:
    """Tests for ServiceExecution model."""

    def test_create_service_execution(self):
        """Test creating a service execution."""
        execution = ServiceExecution(
            id=uuid4(), execution_number="EX-2026-0001", order_id=uuid4(), sequence=1, technician_name="Carlos Santos"
        )

        assert execution.execution_number == "EX-2026-0001"
        assert execution.sequence == 1
        assert execution.technician_name == "Carlos Santos"
        assert execution.status == ExecutionStatus.PENDING

    def test_execution_start_travel(self):
        """Test starting travel."""
        execution = ServiceExecution(
            id=uuid4(), execution_number="EX-2026-0002", order_id=uuid4(), status=ExecutionStatus.PENDING
        )

        execution.start_travel()

        assert execution.status == ExecutionStatus.PENDING
        assert execution.travel_start is not None

    def test_execution_arrive_at_location(self):
        """Test arriving at location."""
        execution = ServiceExecution(
            id=uuid4(),
            execution_number="EX-2026-0003",
            order_id=uuid4(),
            status=ExecutionStatus.PENDING,
            travel_start=datetime.utcnow() - timedelta(minutes=30),
        )

        execution.arrive_at_location()

        assert execution.status == ExecutionStatus.PENDING
        assert execution.arrival_at_location is not None
        assert execution.travel_duration_minutes is not None

    def test_execution_start_execution(self):
        """Test starting execution."""
        execution = ServiceExecution(
            id=uuid4(), execution_number="EX-2026-0004", order_id=uuid4(), status=ExecutionStatus.PENDING
        )

        execution.start_execution()

        assert execution.status == ExecutionStatus.PENDING
        assert execution.actual_start is not None

    def test_execution_pause(self):
        """Test pausing execution."""
        execution = ServiceExecution(
            id=uuid4(), execution_number="EX-2026-0005", order_id=uuid4(), status=ExecutionStatus.PENDING
        )

        execution.pause_execution("Aguardando aprovação")

        assert execution.status == ExecutionStatus.PENDING
        assert execution.pause_reason == "Aguardando aprovação"
        assert execution.paused_at is not None

    def test_execution_resume(self):
        """Test resuming execution."""
        execution = ServiceExecution(
            id=uuid4(), execution_number="EX-2026-0006", order_id=uuid4(), status=ExecutionStatus.PENDING
        )

        execution.resume_execution()

        assert execution.status == ExecutionStatus.PENDING
        assert execution.resumed_at is not None

    def test_execution_finish(self):
        """Test finishing execution."""
        execution = ServiceExecution(
            id=uuid4(),
            execution_number="EX-2026-0007",
            order_id=uuid4(),
            status=ExecutionStatus.PENDING,
            actual_start=datetime.utcnow() - timedelta(hours=2),
        )

        execution.finish_execution()

        assert execution.status == ExecutionStatus.PENDING
        assert execution.actual_end is not None
        assert execution.execution_duration_minutes is not None
        assert execution.is_finished is True

    def test_execution_add_material(self):
        """Test adding material."""
        execution = ServiceExecution(id=uuid4(), execution_number="EX-2026-0008", order_id=uuid4())

        execution.add_material("Parafusos", 10, Decimal("0.50"))

        assert execution.materials_used is not None
        assert len(execution.materials_used) == 1
        assert execution.materials_cost == Decimal("5.00")

    def test_execution_update_checklist_item(self):
        """Test updating checklist item."""
        execution = ServiceExecution(
            id=uuid4(),
            execution_number="EX-2026-0009",
            order_id=uuid4(),
            checklist_items=[
                {"index": 0, "name": "Item 1", "completed": False},
                {"index": 1, "name": "Item 2", "completed": False},
            ],
        )

        execution.update_checklist_item(0, True, "Concluído")

        assert execution.checklist_items[0]["completed"] is True
        assert execution.checklist_items[0].get("notes") == "Concluído"

    def test_execution_add_signature(self):
        """Test adding signature."""
        execution = ServiceExecution(id=uuid4(), execution_number="EX-2026-0010", order_id=uuid4())

        execution.add_signature("Cliente", "base64data", "Responsável")

        assert execution.signatures is not None
        assert len(execution.signatures) == 1
        assert execution.has_signatures is True

    def test_execution_total_cost(self):
        """Test total cost calculation."""
        execution = ServiceExecution(
            id=uuid4(),
            execution_number="EX-2026-0011",
            order_id=uuid4(),
            materials_cost=Decimal("100.00"),
            labor_cost=Decimal("200.00"),
            travel_cost=Decimal("50.00"),
        )

        execution._calculate_total_cost()

        assert execution.total_cost == Decimal("350.00")


class TestServiceReport:
    """Tests for ServiceReport model."""

    def test_create_service_report(self):
        """Test creating a service report."""
        report = ServiceReport(
            id=uuid4(),
            report_number="REL-2026-0001",
            order_id=uuid4(),
            report_type=ReportType.EXECUCAO,
            title="Relatório de Execução",
        )

        assert report.report_number == "REL-2026-0001"
        assert report.report_type == ReportType.EXECUCAO
        assert report.is_draft is True

    def test_report_finalize(self):
        """Test finalizing a report."""
        report = ServiceReport(
            id=uuid4(), report_number="REL-2026-0002", order_id=uuid4(), title="Laudo Técnico", is_draft=True
        )

        report.finalize()

        assert report.is_draft is False

    def test_report_review(self):
        """Test reviewing a report."""
        report = ServiceReport(
            id=uuid4(), report_number="REL-2026-0003", order_id=uuid4(), title="Vistoria", is_draft=False
        )

        reviewer_id = uuid4()
        report.review(reviewer_id, "Maria Souza", "Aprovado com ressalvas")

        assert report.is_reviewed is True
        assert report.reviewer_id == reviewer_id
        assert report.reviewer_name == "Maria Souza"
        assert report.review_notes == "Aprovado com ressalvas"

    def test_report_approve(self):
        """Test approving a report."""
        report = ServiceReport(
            id=uuid4(), report_number="REL-2026-0004", order_id=uuid4(), title="Inspeção", is_reviewed=True
        )

        approver_id = uuid4()
        report.approve(approver_id, "José Lima")

        assert report.is_approved is True
        assert report.approver_id == approver_id
        assert report.approver_name == "José Lima"
        assert report.approved_at is not None

    def test_report_send(self):
        """Test sending a report."""
        report = ServiceReport(
            id=uuid4(), report_number="REL-2026-0005", order_id=uuid4(), title="Orçamento", is_approved=True
        )

        report.send("cliente@email.com")

        assert report.is_sent is True
        assert report.sent_at is not None
        assert "cliente@email.com" in report.sent_to

    def test_report_add_section(self):
        """Test adding a section."""
        report = ServiceReport(id=uuid4(), report_number="REL-2026-0006", order_id=uuid4(), title="Relatório Técnico")

        report.add_section("Introdução", "Texto da introdução", 1)

        assert report.sections is not None
        assert len(report.sections) == 1

    def test_report_add_photo(self):
        """Test adding a photo."""
        report = ServiceReport(id=uuid4(), report_number="REL-2026-0007", order_id=uuid4(), title="Auditoria")

        report.add_photo("http://example.com/foto.jpg", "Foto do local")

        assert report.photos is not None
        assert len(report.photos) == 1
        assert report.photo_count == 1

    def test_report_add_non_conformity(self):
        """Test adding non-conformity."""
        report = ServiceReport(id=uuid4(), report_number="REL-2026-0008", order_id=uuid4(), title="Preventivo")

        report.add_non_conformity("Equipamento danificado", "alta")

        assert report.non_conformities is not None
        assert len(report.non_conformities) == 1
        assert report.non_conformity_count == 1

    def test_report_is_complete(self):
        """Test is_complete property."""
        report = ServiceReport(
            id=uuid4(),
            report_number="REL-2026-0009",
            order_id=uuid4(),
            title="Relatório Final",
            summary="Resumo",
            conclusions="Conclusões",
            is_approved=True,
        )

        assert report.is_complete is True


class TestSLAConfig:
    """Tests for SLAConfig model."""

    def test_create_sla_config(self):
        """Test creating an SLA config."""
        sla = SLAConfig(
            id=uuid4(), name="SLA Padrão", metric_type=SLAMetricType.TEMPO_RESOLUCAO, resolution_time_minutes=480
        )

        assert sla.name == "SLA Padrão"
        assert sla.metric_type == SLAMetricType.TEMPO_RESOLUCAO
        assert sla.resolution_time_minutes == 480

    def test_sla_activate(self):
        """Test activating an SLA."""
        sla = SLAConfig(id=uuid4(), name="SLA Premium", is_active=False)

        sla.activate()

        assert sla.is_active is True

    def test_sla_deactivate(self):
        """Test deactivating an SLA."""
        sla = SLAConfig(id=uuid4(), name="SLA Básico", is_active=True)

        sla.deactivate()

        assert sla.is_active is False

    def test_sla_set_as_default(self):
        """Test setting SLA as default."""
        sla = SLAConfig(id=uuid4(), name="SLA Geral", is_default=False)

        sla.set_as_default()

        assert sla.is_default is True

    def test_sla_update_metrics(self):
        """Test updating SLA metrics."""
        sla = SLAConfig(id=uuid4(), name="SLA Corporativo", total_orders=10, orders_within_sla=8, orders_breached=2)

        sla.update_metrics(within_sla=True)

        assert sla.total_orders == 11
        assert sla.orders_within_sla == 9
        assert sla.current_compliance_percent is not None

    def test_sla_calculate_deadline(self):
        """Test calculating deadline."""
        sla = SLAConfig(id=uuid4(), name="SLA Express", resolution_time_minutes=240)

        start = datetime.utcnow()
        deadline = sla.calculate_deadline(start)

        expected = start + timedelta(minutes=240)
        assert deadline == expected

    def test_sla_calculate_penalty(self):
        """Test calculating penalty."""
        sla = SLAConfig(
            id=uuid4(),
            name="SLA com Penalidade",
            penalty_enabled=True,
            penalty_percent_per_breach=Decimal("5.00"),
            max_penalty_percent=Decimal("30.00"),
        )

        penalty = sla.calculate_penalty(3)

        assert penalty == Decimal("15.0")

    def test_sla_calculate_bonus(self):
        """Test calculating bonus."""
        sla = SLAConfig(
            id=uuid4(),
            name="SLA com Bônus",
            bonus_enabled=True,
            bonus_percent_on_exceed=Decimal("2.00"),
            max_bonus_percent=Decimal("10.00"),
        )

        bonus = sla.calculate_bonus(300)

        assert bonus == Decimal("6.0")

    def test_sla_compliance_status(self):
        """Test compliance status property."""
        sla = SLAConfig(
            id=uuid4(),
            name="SLA Status",
            current_compliance_percent=Decimal("99.5"),
            target_availability_percent=Decimal("99.0"),
        )

        assert sla.compliance_status == "dentro_meta"

    def test_sla_breach_rate(self):
        """Test breach rate calculation."""
        sla = SLAConfig(id=uuid4(), name="SLA Breach", total_orders=100, orders_breached=5)

        assert sla.breach_rate == 5.0

    def test_sla_is_valid(self):
        """Test is_valid method."""
        sla = SLAConfig(
            id=uuid4(),
            name="SLA Válido",
            is_active=True,
            valid_from=datetime.utcnow() - timedelta(days=30),
            valid_until=datetime.utcnow() + timedelta(days=30),
        )

        assert sla.is_valid() is True

    def test_sla_get_response_time_hours(self):
        """Test get_response_time_hours method."""
        sla = SLAConfig(id=uuid4(), name="SLA Tempo", response_time_minutes=120)

        assert sla.get_response_time_hours() == 2.0

    def test_sla_get_resolution_time_hours(self):
        """Test get_resolution_time_hours method."""
        sla = SLAConfig(id=uuid4(), name="SLA Resolução", resolution_time_minutes=480)

        assert sla.get_resolution_time_hours() == 8.0
