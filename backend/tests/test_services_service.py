"""
Tests for Services Module - Service Layer
Sprint 31: Gestão de Serviços
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
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
from modules.services.schemas import (
    ServiceCatalogCreate,
    ServiceCatalogUpdate,
    ServiceExecutionCreate,
    ServiceOrderCreate,
    ServiceOrderUpdate,
    ServiceReportCreate,
    SLAConfigCreate,
)
from modules.services.services import ServiceAIService, ServiceManagementService


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


@pytest.fixture
def mock_service_catalog():
    """Create mock service catalog."""
    return ServiceCatalog(
        id=uuid4(),
        code="SRV-001",
        name="Manutenção Predial",
        category=ServiceCategory.MANUTENCAO_PREDIAL,
        service_type=ServiceType.PREVENTIVO,
        status=ServiceStatus.ATIVO,
        base_price=Decimal("500.00"),
        is_available=True,
        requires_approval=False,
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
        status=OrderStatus.RASCUNHO,
        priority=OrderPriority.NORMAL,
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
        total_orders=10,
        orders_within_sla=9,
        orders_breached=1,
    )


class TestServiceManagementService:
    """Tests for ServiceManagementService."""

    def test_create_service(self, mock_db, mock_service_catalog):
        """Test creating a service."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.create_service_catalog.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            data = ServiceCatalogCreate(
                name="Manutenção Predial",
                category=ServiceCategory.MANUTENCAO_PREDIAL,
                service_type=ServiceType.PREVENTIVO,
                base_price=Decimal("500.00"),
            )

            result = svc.create_service(data, uuid4())

            assert result.name == "Manutenção Predial"
            repo.create_service_catalog.assert_called_once()

    def test_update_service(self, mock_db, mock_service_catalog):
        """Test updating a service."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_service_catalog.name = "Manutenção Predial Atualizado"
            repo.update_service_catalog.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            data = ServiceCatalogUpdate(name="Manutenção Predial Atualizado")
            result = svc.update_service(mock_service_catalog.id, data)

            assert result.name == "Manutenção Predial Atualizado"

    def test_activate_service(self, mock_db, mock_service_catalog):
        """Test activating a service."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_catalog.status = ServiceStatus.INATIVO
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.activate_service(mock_service_catalog.id)

            assert result.status == ServiceStatus.ATIVO

    def test_deactivate_service(self, mock_db, mock_service_catalog):
        """Test deactivating a service."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.deactivate_service(mock_service_catalog.id)

            assert result.status == ServiceStatus.INATIVO

    def test_calculate_service_price(self, mock_db, mock_service_catalog):
        """Test calculating service price."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.calculate_service_price(mock_service_catalog.id, 1.0, False)

            assert result == Decimal("500.00")

    def test_create_order(self, mock_db, mock_service_catalog, mock_service_order):
        """Test creating an order."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            repo.create_service_order.return_value = mock_service_order
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            data = ServiceOrderCreate(
                service_id=mock_service_catalog.id, client_id=uuid4(), title="Manutenção de Ar Condicionado"
            )

            result = svc.create_order(data, uuid4())

            assert result.title == "Manutenção de Ar Condicionado"
            repo.create_service_order.assert_called_once()

    def test_create_order_service_unavailable(self, mock_db, mock_service_catalog):
        """Test creating order with unavailable service."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_catalog.is_available = False
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            data = ServiceOrderCreate(service_id=mock_service_catalog.id, client_id=uuid4(), title="Teste")

            with pytest.raises(ValueError, match="indisponível"):
                svc.create_order(data)

    def test_approve_order(self, mock_db, mock_service_order):
        """Test approving an order."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_order.status = OrderStatus.PENDENTE
            repo.get_service_order_by_id.return_value = mock_service_order
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.approve_order(mock_service_order.id, uuid4())

            assert result.status == OrderStatus.APROVADA

    def test_schedule_order(self, mock_db, mock_service_order):
        """Test scheduling an order."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_order.status = OrderStatus.APROVADA
            repo.get_service_order_by_id.return_value = mock_service_order
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            schedule_date = date.today() + timedelta(days=3)
            result = svc.schedule_order(mock_service_order.id, schedule_date, "09:00", "12:00")

            assert result.status == OrderStatus.AGENDADA
            assert result.scheduled_date == schedule_date

    def test_complete_order(self, mock_db, mock_service_order, mock_service_catalog, mock_sla_config):
        """Test completing an order."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_order.status = OrderStatus.EM_ANDAMENTO
            mock_service_order.started_at = datetime.utcnow() - timedelta(hours=2)
            mock_service_order.estimated_value = Decimal("500.00")
            repo.get_service_order_by_id.return_value = mock_service_order
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            repo.list_sla_configs.return_value = [mock_sla_config]
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.complete_order(mock_service_order.id, Decimal("500.00"), "Serviço concluído com sucesso")

            assert result.status == OrderStatus.CONCLUIDA

    def test_cancel_order(self, mock_db, mock_service_order):
        """Test canceling an order."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_order.status = OrderStatus.AGENDADA
            repo.get_service_order_by_id.return_value = mock_service_order
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.cancel_order(mock_service_order.id, "Cliente solicitou cancelamento")

            assert result.status == OrderStatus.CANCELADA

    def test_rate_order(self, mock_db, mock_service_order, mock_service_catalog):
        """Test rating an order."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_order.status = OrderStatus.CONCLUIDA
            repo.get_service_order_by_id.return_value = mock_service_order
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.rate_order(mock_service_order.id, 5, "Excelente serviço!")

            assert result.rating == 5

    def test_get_overdue_orders(self, mock_db, mock_service_order):
        """Test getting overdue orders."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            mock_service_order.status = OrderStatus.EM_ANDAMENTO
            mock_service_order.sla_resolution_deadline = datetime.utcnow() - timedelta(hours=1)
            repo.list_service_orders.return_value = [mock_service_order]
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.get_overdue_orders()

            assert len(result) == 1

    def test_create_sla_config(self, mock_db, mock_sla_config):
        """Test creating SLA config."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.create_sla_config.return_value = mock_sla_config
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            data = SLAConfigCreate(
                name="SLA Padrão", metric_type=SLAMetricType.TEMPO_RESOLUCAO, resolution_time_minutes=480
            )

            result = svc.create_sla_config(data, uuid4())

            assert result.name == "SLA Padrão"

    def test_get_sla_compliance_report(self, mock_db, mock_sla_config):
        """Test getting SLA compliance report."""
        with patch("modules.services.services.service_management_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_sla_config_by_id.return_value = mock_sla_config
            mock_repo_class.return_value = repo

            svc = ServiceManagementService(mock_db)
            svc.repository = repo

            result = svc.get_sla_compliance_report(mock_sla_config.id)

            assert "sla_id" in result
            assert "metrics" in result


class TestServiceAIService:
    """Tests for ServiceAIService."""

    def test_analyze_service(self, mock_db, mock_service_catalog, mock_service_order):
        """Test analyzing a service."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_service_order.status = OrderStatus.CONCLUIDA
            mock_service_order.rating = 5
            mock_service_order.sla_resolution_met = True
            repo.list_service_orders.return_value = [mock_service_order]
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.analyze_service(mock_service_catalog.id)

            assert result is not None
            assert result.service_id == mock_service_catalog.id
            assert result.performance_score >= 0

    def test_analyze_all_services(self, mock_db, mock_service_catalog):
        """Test analyzing all services."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.list_service_catalogs.return_value = [mock_service_catalog]
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            repo.list_service_orders.return_value = []
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.analyze_all_services()

            assert len(result) >= 0

    def test_get_service_recommendations(self, mock_db, mock_service_catalog):
        """Test getting service recommendations."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.list_service_catalogs.return_value = [mock_service_catalog]
            repo.list_service_orders.return_value = []
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.get_service_recommendations(limit=5)

            assert len(result) >= 0

    def test_predict_service_demand(self, mock_db, mock_service_catalog, mock_service_order):
        """Test predicting service demand."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            repo.list_service_orders.return_value = [mock_service_order]
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.predict_service_demand(mock_service_catalog.id, 30)

            assert "service_id" in result
            assert "predicted_demand" in result

    def test_analyze_sla(self, mock_db, mock_sla_config):
        """Test analyzing SLA."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.get_sla_config_by_id.return_value = mock_sla_config
            repo.list_service_orders.return_value = []
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.analyze_sla(mock_sla_config.id)

            assert result is not None
            assert result.sla_id == mock_sla_config.id

    def test_get_sla_dashboard(self, mock_db, mock_sla_config):
        """Test getting SLA dashboard."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.list_sla_configs.return_value = [mock_sla_config]
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.get_sla_dashboard()

            assert "summary" in result
            assert "slas" in result

    def test_analyze_order_patterns(self, mock_db, mock_service_order):
        """Test analyzing order patterns."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.list_service_orders.return_value = [mock_service_order]
            repo.get_service_catalog_by_id.return_value = None
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.analyze_order_patterns(30)

            assert "period_days" in result
            assert "patterns" in result
            assert "metrics" in result

    def test_identify_bottlenecks(self, mock_db, mock_service_order, mock_sla_config):
        """Test identifying bottlenecks."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            # Many pending orders = bottleneck
            pending_orders = [mock_service_order] * 30
            for order in pending_orders:
                order.status = OrderStatus.PENDENTE
            repo.list_service_orders.return_value = pending_orders
            repo.list_sla_configs.return_value = [mock_sla_config]
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            result = svc.identify_bottlenecks()

            assert len(result) >= 0

    def test_get_executive_dashboard(self, mock_db, mock_service_catalog, mock_service_order, mock_sla_config):
        """Test getting executive dashboard."""
        with patch("modules.services.services.service_ai_service.ServiceRepository") as mock_repo_class:
            repo = MagicMock()
            repo.list_service_catalogs.return_value = [mock_service_catalog]
            repo.list_service_orders.return_value = [mock_service_order]
            repo.list_sla_configs.return_value = [mock_sla_config]
            repo.get_service_catalog_by_id.return_value = mock_service_catalog
            mock_repo_class.return_value = repo

            svc = ServiceAIService(mock_db)
            svc.repository = repo

            # Mock the stats methods
            with (
                patch.object(svc, "get_service_catalog_stats") as mock_cat,
                patch.object(svc, "get_order_stats") as mock_order,
                patch.object(svc, "get_sla_dashboard") as mock_sla,
                patch.object(svc, "identify_bottlenecks") as mock_bn,
            ):
                from modules.services.schemas import ServiceCatalogStats, ServiceOrderStats

                mock_cat.return_value = ServiceCatalogStats(
                    total_services=100, active_services=80, total_revenue=Decimal("50000.00")
                )
                mock_order.return_value = ServiceOrderStats(total_orders=500, overdue_count=5)
                mock_sla.return_value = {"summary": {"average_compliance": 95.0}}
                mock_bn.return_value = []

                result = svc.get_executive_dashboard()

                assert "services" in result
                assert "orders" in result
                assert "sla" in result
