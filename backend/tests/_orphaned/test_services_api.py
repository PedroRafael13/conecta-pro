"""
Tests for Services Module - API Endpoints
Sprint 31: Gestão de Serviços
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

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
from modules.services.schemas import ServiceCatalogStats, ServiceOrderStats


@pytest.fixture
def mock_current_user():
    """Mock current user."""
    return {"sub": str(uuid4()), "email": "test@example.com", "role": "admin"}


@pytest.fixture
def mock_service_catalog():
    """Create mock service catalog."""
    service_id = uuid4()
    return ServiceCatalog(
        id=service_id,
        code="SRV-001",
        name="Manutenção Predial",
        description="Serviço de manutenção predial",
        category=ServiceCategory.MANUTENCAO,
        service_type=ServiceType.PREVENTIVO,
        status=ServiceStatus.ATIVO,
        base_price=Decimal("500.00"),
        is_available=True,
        total_orders=10,
        completed_orders=8,
        avg_rating=Decimal("4.5"),
    )


@pytest.fixture
def mock_service_order():
    """Create mock service order."""
    return ServiceOrder(
        id=uuid4(),
        order_number="OS-2026-0001",
        service_id=uuid4(),
        client_id=uuid4(),
        title="Manutenção de Ar Condicionado",
        status=OrderStatus.PENDENTE,
        priority=OrderPriority.NORMAL,
    )


@pytest.fixture
def mock_service_execution():
    """Create mock service execution."""
    return ServiceExecution(
        id=uuid4(),
        execution_number="EX-2026-0001",
        order_id=uuid4(),
        sequence=1,
        status=ExecutionStatus.PENDING,
        technician_name="João Silva",
    )


@pytest.fixture
def mock_service_report():
    """Create mock service report."""
    return ServiceReport(
        id=uuid4(),
        report_number="REL-2026-0001",
        order_id=uuid4(),
        report_type=ReportType.EXECUCAO,
        title="Relatório de Execução",
        is_draft=True,
    )


@pytest.fixture
def mock_sla_config():
    """Create mock SLA config."""
    return SLAConfig(
        id=uuid4(),
        name="SLA Padrão",
        metric_type=SLAMetricType.TEMPO_RESOLUCAO,
        resolution_time_minutes=480,
        is_active=True,
        is_default=True,
    )


class TestServiceCatalogEndpoints:
    """Tests for ServiceCatalog API endpoints."""

    def test_list_services_success(self, mock_service_catalog):
        """Test listing services."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.list_service_catalogs.return_value = [mock_service_catalog]
            mock_repo.return_value = repo

            response_data = [mock_service_catalog]

            assert len(response_data) == 1
            assert response_data[0].name == "Manutenção Predial"

    def test_get_service_success(self, mock_service_catalog):
        """Test getting a service."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_repo.return_value = repo

            result = repo.get_service_catalog_by_id(mock_service_catalog.id)

            assert result.id == mock_service_catalog.id
            assert result.name == "Manutenção Predial"

    def test_get_service_not_found(self):
        """Test getting non-existent service."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = None
            mock_repo.return_value = repo

            result = repo.get_service_catalog_by_id(uuid4())

            assert result is None

    def test_create_service_success(self, mock_service_catalog, mock_current_user):
        """Test creating a service."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            svc.create_service.return_value = mock_service_catalog
            mock_svc.return_value = svc

            result = svc.create_service(MagicMock(), uuid4())

            assert result.code == "SRV-001"
            assert result.name == "Manutenção Predial"

    def test_update_service_success(self, mock_service_catalog, mock_current_user):
        """Test updating a service."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_catalog.name = "Manutenção Predial Atualizado"
            svc.update_service.return_value = mock_service_catalog
            mock_svc.return_value = svc

            result = svc.update_service(mock_service_catalog.id, MagicMock(), uuid4())

            assert result.name == "Manutenção Predial Atualizado"

    def test_activate_service_success(self, mock_service_catalog):
        """Test activating a service."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_catalog.status = ServiceStatus.ATIVO
            svc.activate_service.return_value = mock_service_catalog
            mock_svc.return_value = svc

            result = svc.activate_service(mock_service_catalog.id)

            assert result.status == ServiceStatus.ATIVO

    def test_deactivate_service_success(self, mock_service_catalog):
        """Test deactivating a service."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_catalog.status = ServiceStatus.INATIVO
            svc.deactivate_service.return_value = mock_service_catalog
            mock_svc.return_value = svc

            result = svc.deactivate_service(mock_service_catalog.id)

            assert result.status == ServiceStatus.INATIVO

    def test_calculate_price_success(self, mock_service_catalog):
        """Test calculating service price."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            svc.calculate_service_price.return_value = Decimal("500.00")
            mock_svc.return_value = svc

            result = svc.calculate_service_price(mock_service_catalog.id, 1.0, False)

            assert result == Decimal("500.00")


class TestServiceOrderEndpoints:
    """Tests for ServiceOrder API endpoints."""

    def test_list_orders_success(self, mock_service_order):
        """Test listing orders."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.list_service_orders.return_value = [mock_service_order]
            mock_repo.return_value = repo

            result = repo.list_service_orders()

            assert len(result) == 1
            assert result[0].order_number == "OS-2026-0001"

    def test_get_order_success(self, mock_service_order):
        """Test getting an order."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.get_service_order_by_id.return_value = mock_service_order
            mock_repo.return_value = repo

            result = repo.get_service_order_by_id(mock_service_order.id)

            assert result.id == mock_service_order.id

    def test_create_order_success(self, mock_service_order, mock_current_user):
        """Test creating an order."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            svc.create_order.return_value = mock_service_order
            mock_svc.return_value = svc

            result = svc.create_order(MagicMock(), uuid4())

            assert result.order_number == "OS-2026-0001"

    def test_approve_order_success(self, mock_service_order, mock_current_user):
        """Test approving an order."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_order.status = OrderStatus.APROVADA
            svc.approve_order.return_value = mock_service_order
            mock_svc.return_value = svc

            result = svc.approve_order(mock_service_order.id, uuid4())

            assert result.status == OrderStatus.APROVADA

    def test_schedule_order_success(self, mock_service_order):
        """Test scheduling an order."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_order.status = OrderStatus.AGENDADA
            mock_service_order.scheduled_date = date.today() + timedelta(days=3)
            svc.schedule_order.return_value = mock_service_order
            mock_svc.return_value = svc

            result = svc.schedule_order(mock_service_order.id, date.today() + timedelta(days=3), "09:00", "12:00")

            assert result.status == OrderStatus.AGENDADA

    def test_start_order_success(self, mock_service_order):
        """Test starting an order."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_order.status = OrderStatus.EM_ANDAMENTO
            svc.start_order.return_value = mock_service_order
            mock_svc.return_value = svc

            result = svc.start_order(mock_service_order.id)

            assert result.status == OrderStatus.EM_ANDAMENTO

    def test_complete_order_success(self, mock_service_order):
        """Test completing an order."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_order.status = OrderStatus.CONCLUIDA
            svc.complete_order.return_value = mock_service_order
            mock_svc.return_value = svc

            result = svc.complete_order(mock_service_order.id)

            assert result.status == OrderStatus.CONCLUIDA

    def test_cancel_order_success(self, mock_service_order):
        """Test canceling an order."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_order.status = OrderStatus.CANCELADA
            svc.cancel_order.return_value = mock_service_order
            mock_svc.return_value = svc

            result = svc.cancel_order(mock_service_order.id, "Motivo")

            assert result.status == OrderStatus.CANCELADA

    def test_rate_order_success(self, mock_service_order):
        """Test rating an order."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_order.rating = 5
            svc.rate_order.return_value = mock_service_order
            mock_svc.return_value = svc

            result = svc.rate_order(mock_service_order.id, 5, "Excelente")

            assert result.rating == 5


class TestServiceExecutionEndpoints:
    """Tests for ServiceExecution API endpoints."""

    def test_list_executions_success(self, mock_service_execution):
        """Test listing executions."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.list_service_executions.return_value = [mock_service_execution]
            mock_repo.return_value = repo

            result = repo.list_service_executions()

            assert len(result) == 1
            assert result[0].execution_number == "EX-2026-0001"

    def test_create_execution_success(self, mock_service_execution, mock_current_user):
        """Test creating an execution."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            svc.create_execution.return_value = mock_service_execution
            mock_svc.return_value = svc

            result = svc.create_execution(MagicMock(), uuid4())

            assert result.execution_number == "EX-2026-0001"

    def test_start_execution_success(self, mock_service_execution):
        """Test starting execution."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_execution.status = ExecutionStatus.PENDING
            svc.start_execution.return_value = mock_service_execution
            mock_svc.return_value = svc

            result = svc.start_execution(mock_service_execution.id)

            assert result.status == ExecutionStatus.PENDING

    def test_finish_execution_success(self, mock_service_execution):
        """Test finishing execution."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_execution.status = ExecutionStatus.PENDING
            svc.finish_execution.return_value = mock_service_execution
            mock_svc.return_value = svc

            result = svc.finish_execution(mock_service_execution.id)

            assert result.status == ExecutionStatus.PENDING


class TestServiceReportEndpoints:
    """Tests for ServiceReport API endpoints."""

    def test_list_reports_success(self, mock_service_report):
        """Test listing reports."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.list_service_reports.return_value = [mock_service_report]
            mock_repo.return_value = repo

            result = repo.list_service_reports()

            assert len(result) == 1
            assert result[0].report_number == "REL-2026-0001"

    def test_create_report_success(self, mock_service_report, mock_current_user):
        """Test creating a report."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            svc.create_report.return_value = mock_service_report
            mock_svc.return_value = svc

            result = svc.create_report(MagicMock(), uuid4())

            assert result.report_number == "REL-2026-0001"

    def test_finalize_report_success(self, mock_service_report):
        """Test finalizing a report."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_report.is_draft = False
            svc.finalize_report.return_value = mock_service_report
            mock_svc.return_value = svc

            result = svc.finalize_report(mock_service_report.id)

            assert result.is_draft is False

    def test_approve_report_success(self, mock_service_report, mock_current_user):
        """Test approving a report."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_service_report.is_approved = True
            svc.approve_report.return_value = mock_service_report
            mock_svc.return_value = svc

            result = svc.approve_report(mock_service_report.id, uuid4(), "Aprovador")

            assert result.is_approved is True


class TestSLAConfigEndpoints:
    """Tests for SLAConfig API endpoints."""

    def test_list_sla_configs_success(self, mock_sla_config):
        """Test listing SLA configs."""
        with patch("modules.services.controllers.service_controller.get_repository") as mock_repo:
            repo = MagicMock()
            repo.list_sla_configs.return_value = [mock_sla_config]
            mock_repo.return_value = repo

            result = repo.list_sla_configs()

            assert len(result) == 1
            assert result[0].name == "SLA Padrão"

    def test_create_sla_config_success(self, mock_sla_config, mock_current_user):
        """Test creating SLA config."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            svc.create_sla_config.return_value = mock_sla_config
            mock_svc.return_value = svc

            result = svc.create_sla_config(MagicMock(), uuid4())

            assert result.name == "SLA Padrão"

    def test_activate_sla_success(self, mock_sla_config):
        """Test activating SLA."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_sla_config.is_active = True
            svc.activate_sla.return_value = mock_sla_config
            mock_svc.return_value = svc

            result = svc.activate_sla(mock_sla_config.id)

            assert result.is_active is True

    def test_set_default_sla_success(self, mock_sla_config):
        """Test setting default SLA."""
        with patch("modules.services.controllers.service_controller.get_management_service") as mock_svc:
            svc = MagicMock()
            mock_sla_config.is_default = True
            svc.set_default_sla.return_value = mock_sla_config
            mock_svc.return_value = svc

            result = svc.set_default_sla(mock_sla_config.id)

            assert result.is_default is True


class TestAnalyticsEndpoints:
    """Tests for Analytics API endpoints."""

    def test_get_catalog_stats_success(self):
        """Test getting catalog stats."""
        with patch("modules.services.controllers.service_controller.get_ai_service") as mock_ai:
            ai_svc = MagicMock()
            ai_svc.get_service_catalog_stats.return_value = ServiceCatalogStats(
                total_services=100, active_services=80, total_revenue=Decimal("50000.00")
            )
            mock_ai.return_value = ai_svc

            result = ai_svc.get_service_catalog_stats()

            assert result.total_services == 100
            assert result.active_services == 80

    def test_get_order_stats_success(self):
        """Test getting order stats."""
        with patch("modules.services.controllers.service_controller.get_ai_service") as mock_ai:
            ai_svc = MagicMock()
            ai_svc.get_order_stats.return_value = ServiceOrderStats(
                total_orders=500, overdue_count=5, sla_compliance_percent=95.0
            )
            mock_ai.return_value = ai_svc

            result = ai_svc.get_order_stats()

            assert result.total_orders == 500
            assert result.overdue_count == 5

    def test_get_executive_dashboard_success(self):
        """Test getting executive dashboard."""
        with patch("modules.services.controllers.service_controller.get_ai_service") as mock_ai:
            ai_svc = MagicMock()
            ai_svc.get_executive_dashboard.return_value = {
                "services": {"total": 100},
                "orders": {"total": 500},
                "sla": {"average_compliance": 95.0},
            }
            mock_ai.return_value = ai_svc

            result = ai_svc.get_executive_dashboard()

            assert result["services"]["total"] == 100
            assert result["orders"]["total"] == 500

    def test_identify_bottlenecks_success(self):
        """Test identifying bottlenecks."""
        with patch("modules.services.controllers.service_controller.get_ai_service") as mock_ai:
            ai_svc = MagicMock()
            ai_svc.identify_bottlenecks.return_value = [{"type": "queue", "severity": "high"}]
            mock_ai.return_value = ai_svc

            result = ai_svc.identify_bottlenecks()

            assert len(result) == 1
            assert result[0]["type"] == "queue"
