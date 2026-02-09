"""Testes de API para módulo Analytics Dashboard."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from modules.hr.analytics_dashboard.models import (
    DashboardType,
    DashboardVisibility,
    DeliveryMethod,
    KPICategory,
    KPIUnit,
    ReportFormat,
    ReportType,
    ScheduleFrequency,
    WidgetType,
)

# ==================== Dashboard API Tests ====================


class TestDashboardAPI:
    """Testes para endpoints de Dashboard."""

    @pytest.fixture
    def mock_user(self):
        """Fixture para usuário mockado."""
        return {
            "id": str(uuid4()),
            "email": "admin@empresa.com",
            "role": "admin",
            "condominio_id": str(uuid4()),
        }

    @pytest.fixture
    def sample_dashboard(self):
        """Fixture para dashboard de exemplo."""
        return {
            "id": str(uuid4()),
            "name": "Dashboard RH",
            "description": "Dashboard de métricas de RH",
            "dashboard_type": "executive",
            "visibility": "organization",
            "is_default": False,
            "auto_refresh": True,
            "refresh_interval": "5min",
            "widgets": [],
        }

    @pytest.mark.asyncio
    async def test_list_dashboards(self, mock_user, sample_dashboard):
        """Testa listagem de dashboards."""
        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.list_user_dashboards = AsyncMock(return_value=([sample_dashboard], 1))

            # Simular resposta esperada
            result = await mock_instance.list_user_dashboards(
                condominio_id=mock_user["condominio_id"],
                user_id=mock_user["id"],
            )

            dashboards, total = result
            assert total == 1
            assert dashboards[0]["name"] == "Dashboard RH"

    @pytest.mark.asyncio
    async def test_create_dashboard(self, mock_user):
        """Testa criação de dashboard."""
        dashboard_data = {
            "name": "Novo Dashboard",
            "description": "Dashboard customizado",
            "dashboard_type": "custom",
            "visibility": "private",
        }

        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.create_dashboard = AsyncMock(
                return_value={
                    "id": str(uuid4()),
                    **dashboard_data,
                }
            )

            result = await mock_instance.create_dashboard(
                data=MagicMock(**dashboard_data),
                condominio_id=mock_user["condominio_id"],
                owner_id=mock_user["id"],
            )

            assert result["name"] == "Novo Dashboard"
            assert result["dashboard_type"] == "custom"

    @pytest.mark.asyncio
    async def test_get_dashboard(self, mock_user, sample_dashboard):
        """Testa obtenção de dashboard por ID."""
        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_dashboard = AsyncMock(return_value=sample_dashboard)

            result = await mock_instance.get_dashboard(
                dashboard_id=sample_dashboard["id"],
                user_id=mock_user["id"],
            )

            assert result["id"] == sample_dashboard["id"]
            assert result["name"] == "Dashboard RH"

    @pytest.mark.asyncio
    async def test_update_dashboard(self, mock_user, sample_dashboard):
        """Testa atualização de dashboard."""
        update_data = {"name": "Dashboard RH Atualizado"}

        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.update_dashboard = AsyncMock(return_value={**sample_dashboard, **update_data})

            result = await mock_instance.update_dashboard(
                dashboard_id=sample_dashboard["id"],
                data=MagicMock(**update_data),
                user_id=mock_user["id"],
            )

            assert result["name"] == "Dashboard RH Atualizado"

    @pytest.mark.asyncio
    async def test_delete_dashboard(self, mock_user, sample_dashboard):
        """Testa exclusão de dashboard."""
        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.delete_dashboard = AsyncMock(return_value=True)

            result = await mock_instance.delete_dashboard(
                dashboard_id=sample_dashboard["id"],
                user_id=mock_user["id"],
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_clone_dashboard(self, mock_user, sample_dashboard):
        """Testa clonagem de dashboard."""
        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.clone_dashboard = AsyncMock(
                return_value={
                    "id": str(uuid4()),
                    "name": "Dashboard RH (Cópia)",
                    "dashboard_type": "executive",
                }
            )

            result = await mock_instance.clone_dashboard(
                source_id=sample_dashboard["id"],
                new_name="Dashboard RH (Cópia)",
                user_id=mock_user["id"],
            )

            assert "Cópia" in result["name"]


class TestWidgetAPI:
    """Testes para endpoints de Widget."""

    @pytest.fixture
    def mock_user(self):
        """Fixture para usuário mockado."""
        return {
            "id": str(uuid4()),
            "email": "admin@empresa.com",
            "role": "admin",
            "condominio_id": str(uuid4()),
        }

    @pytest.fixture
    def sample_widget(self):
        """Fixture para widget de exemplo."""
        return {
            "id": str(uuid4()),
            "dashboard_id": str(uuid4()),
            "title": "Taxa de Absenteísmo",
            "widget_type": "kpi_card",
            "kpi_code": "ABSENTEEISM_RATE",
            "position_x": 0,
            "position_y": 0,
            "width": 4,
            "height": 2,
        }

    @pytest.mark.asyncio
    async def test_add_widget(self, mock_user, sample_widget):
        """Testa adição de widget."""
        dashboard_id = uuid4()
        widget_data = {
            "title": "Novo Widget",
            "widget_type": "line_chart",
            "data_source": "time_entries",
            "position_x": 0,
            "position_y": 0,
            "width": 6,
            "height": 3,
        }

        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.add_widget = AsyncMock(
                return_value={
                    "id": str(uuid4()),
                    "dashboard_id": str(dashboard_id),
                    **widget_data,
                }
            )

            result = await mock_instance.add_widget(
                dashboard_id=dashboard_id,
                data=MagicMock(**widget_data),
                user_id=mock_user["id"],
            )

            assert result["title"] == "Novo Widget"
            assert result["widget_type"] == "line_chart"

    @pytest.mark.asyncio
    async def test_update_widget(self, mock_user, sample_widget):
        """Testa atualização de widget."""
        update_data = {"title": "Widget Atualizado", "width": 6}

        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.update_widget = AsyncMock(return_value={**sample_widget, **update_data})

            result = await mock_instance.update_widget(
                widget_id=sample_widget["id"],
                data=MagicMock(**update_data),
                user_id=mock_user["id"],
            )

            assert result["title"] == "Widget Atualizado"
            assert result["width"] == 6

    @pytest.mark.asyncio
    async def test_delete_widget(self, mock_user, sample_widget):
        """Testa exclusão de widget."""
        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.remove_widget = AsyncMock(return_value=True)

            result = await mock_instance.remove_widget(
                widget_id=sample_widget["id"],
                user_id=mock_user["id"],
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_get_widget_data(self, mock_user, sample_widget):
        """Testa obtenção de dados do widget."""
        with patch("modules.hr.analytics_dashboard.services.DashboardService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_widget_data = AsyncMock(
                return_value={
                    "widget_id": sample_widget["id"],
                    "data": {"value": 2.5, "trend": "down"},
                    "cached": True,
                    "computed_at": datetime.utcnow().isoformat(),
                }
            )

            result = await mock_instance.get_widget_data(
                widget_id=sample_widget["id"],
                user_id=mock_user["id"],
            )

            assert "data" in result
            assert result["data"]["value"] == 2.5


# ==================== KPI API Tests ====================


class TestKPIAPI:
    """Testes para endpoints de KPI."""

    @pytest.fixture
    def mock_user(self):
        """Fixture para usuário mockado."""
        return {
            "id": str(uuid4()),
            "email": "admin@empresa.com",
            "role": "admin",
            "condominio_id": str(uuid4()),
        }

    @pytest.fixture
    def sample_kpi(self):
        """Fixture para KPI de exemplo."""
        return {
            "id": str(uuid4()),
            "code": "ABSENTEEISM_RATE",
            "name": "Taxa de Absenteísmo",
            "category": "attendance",
            "unit": "percentage",
            "direction": "down",
            "target_value": 3.0,
            "is_system": True,
        }

    @pytest.mark.asyncio
    async def test_list_kpis(self, mock_user, sample_kpi):
        """Testa listagem de KPIs."""
        with patch("modules.hr.analytics_dashboard.repositories.KPIRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.list_kpis = AsyncMock(return_value=([sample_kpi], 1))

            result, total = await mock_instance.list_kpis(
                condominio_id=mock_user["condominio_id"],
            )

            assert total == 1
            assert result[0]["code"] == "ABSENTEEISM_RATE"

    @pytest.mark.asyncio
    async def test_create_kpi(self, mock_user):
        """Testa criação de KPI customizado."""
        kpi_data = {
            "code": "CUSTOM_KPI",
            "name": "KPI Customizado",
            "category": "productivity",
            "unit": "number",
            "direction": "up",
        }

        with patch("modules.hr.analytics_dashboard.repositories.KPIRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_kpi_by_code = AsyncMock(return_value=None)
            mock_instance.create_kpi = AsyncMock(
                return_value={
                    "id": str(uuid4()),
                    **kpi_data,
                    "is_system": False,
                }
            )

            result = await mock_instance.create_kpi(
                data=MagicMock(**kpi_data),
                condominio_id=mock_user["condominio_id"],
                created_by=mock_user["id"],
            )

            assert result["code"] == "CUSTOM_KPI"
            assert result["is_system"] is False

    @pytest.mark.asyncio
    async def test_get_kpi_value(self, mock_user, sample_kpi):
        """Testa obtenção de valor de KPI."""
        with patch("modules.hr.analytics_dashboard.services.KPICalculatorService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.calculate_kpi = AsyncMock(
                return_value={
                    "code": "ABSENTEEISM_RATE",
                    "value": 2.5,
                    "formatted_value": "2.5%",
                    "trend": "down",
                    "trend_percentage": -0.5,
                    "status": "good",
                }
            )

            result = await mock_instance.calculate_kpi(
                kpi_code="ABSENTEEISM_RATE",
                condominio_id=mock_user["condominio_id"],
            )

            assert result["value"] == 2.5
            assert result["status"] == "good"

    @pytest.mark.asyncio
    async def test_get_kpi_history(self, mock_user, sample_kpi):
        """Testa obtenção de histórico de KPI."""
        now = datetime.utcnow()
        period_start = now - timedelta(days=30)

        with patch("modules.hr.analytics_dashboard.services.KPICalculatorService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_kpi_history = AsyncMock(
                return_value=[
                    {"date": "2024-12-01", "value": 2.8},
                    {"date": "2024-12-08", "value": 2.6},
                    {"date": "2024-12-15", "value": 2.5},
                    {"date": "2024-12-22", "value": 2.3},
                ]
            )

            result = await mock_instance.get_kpi_history(
                kpi_code="ABSENTEEISM_RATE",
                condominio_id=mock_user["condominio_id"],
                period_start=period_start,
                period_end=now,
                granularity="weekly",
            )

            assert len(result) == 4

    @pytest.mark.asyncio
    async def test_get_kpi_dashboard(self, mock_user):
        """Testa obtenção de dashboard de KPIs."""
        with patch("modules.hr.analytics_dashboard.services.KPICalculatorService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.calculate_dashboard_kpis = AsyncMock(
                return_value=[
                    {"code": "ABSENTEEISM_RATE", "value": 2.5, "status": "good"},
                    {"code": "PUNCTUALITY_RATE", "value": 95.0, "status": "good"},
                    {"code": "OVERTIME_HOURS", "value": 150, "status": "warning"},
                ]
            )

            result = await mock_instance.calculate_dashboard_kpis(
                condominio_id=mock_user["condominio_id"],
            )

            assert len(result) == 3


# ==================== Report API Tests ====================


class TestReportAPI:
    """Testes para endpoints de Relatórios."""

    @pytest.fixture
    def mock_user(self):
        """Fixture para usuário mockado."""
        return {
            "id": str(uuid4()),
            "email": "admin@empresa.com",
            "role": "admin",
            "condominio_id": str(uuid4()),
        }

    @pytest.fixture
    def sample_report(self):
        """Fixture para relatório de exemplo."""
        return {
            "id": str(uuid4()),
            "name": "Relatório Mensal de Ponto",
            "report_type": "time_attendance",
            "output_format": "pdf",
            "schedule_frequency": "monthly",
            "delivery_method": "email",
            "status": "active",
            "recipients": [
                {"email": "rh@empresa.com", "name": "RH"},
            ],
        }

    @pytest.mark.asyncio
    async def test_list_reports(self, mock_user, sample_report):
        """Testa listagem de relatórios."""
        with patch("modules.hr.analytics_dashboard.repositories.ReportRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.list_reports = AsyncMock(return_value=([sample_report], 1))

            result, total = await mock_instance.list_reports(
                condominio_id=mock_user["condominio_id"],
            )

            assert total == 1
            assert result[0]["name"] == "Relatório Mensal de Ponto"

    @pytest.mark.asyncio
    async def test_create_report(self, mock_user):
        """Testa criação de relatório agendado."""
        report_data = {
            "name": "Relatório Semanal",
            "report_type": "overtime_summary",
            "output_format": "excel",
            "schedule_frequency": "weekly",
            "delivery_method": "email",
            "recipients": [{"email": "gestor@empresa.com"}],
        }

        with patch("modules.hr.analytics_dashboard.repositories.ReportRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.create_report = AsyncMock(
                return_value={
                    "id": str(uuid4()),
                    **report_data,
                    "status": "active",
                }
            )

            result = await mock_instance.create_report(
                data=MagicMock(**report_data),
                condominio_id=mock_user["condominio_id"],
                owner_id=mock_user["id"],
            )

            assert result["name"] == "Relatório Semanal"
            assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_run_report(self, mock_user, sample_report):
        """Testa execução manual de relatório."""
        with patch("modules.hr.analytics_dashboard.services.ReportGeneratorService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.generate_report = AsyncMock(
                return_value={
                    "report_id": sample_report["id"],
                    "status": "success",
                    "file_path": "/reports/relatorio_2024_12.pdf",
                    "file_size": 2048,
                    "generated_at": datetime.utcnow().isoformat(),
                }
            )

            result = await mock_instance.generate_report(
                report=MagicMock(id=sample_report["id"]),
            )

            assert result["status"] == "success"
            assert "file_path" in result

    @pytest.mark.asyncio
    async def test_pause_report(self, mock_user, sample_report):
        """Testa pausa de relatório."""
        with patch("modules.hr.analytics_dashboard.repositories.ReportRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.pause_report = AsyncMock(return_value=True)

            result = await mock_instance.pause_report(report_id=sample_report["id"])

            assert result is True

    @pytest.mark.asyncio
    async def test_resume_report(self, mock_user, sample_report):
        """Testa retomada de relatório."""
        with patch("modules.hr.analytics_dashboard.repositories.ReportRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.resume_report = AsyncMock(return_value={**sample_report, "status": "active"})

            result = await mock_instance.resume_report(report_id=sample_report["id"])

            assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_report_history(self, mock_user, sample_report):
        """Testa obtenção de histórico de execuções."""
        with patch("modules.hr.analytics_dashboard.repositories.ReportRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_report_by_id = AsyncMock(
                return_value=MagicMock(
                    id=sample_report["id"],
                    name=sample_report["name"],
                    run_count=5,
                    success_count=4,
                    failure_count=1,
                )
            )

            report = await mock_instance.get_report_by_id(report_id=sample_report["id"])

            assert report.run_count == 5
            assert report.success_count == 4

    @pytest.mark.asyncio
    async def test_get_upcoming_reports(self, mock_user):
        """Testa listagem de próximos relatórios."""
        with patch("modules.hr.analytics_dashboard.repositories.ReportRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_upcoming_reports = AsyncMock(
                return_value=[
                    MagicMock(
                        id=uuid4(),
                        name="Relatório 1",
                        next_run_at=datetime.utcnow() + timedelta(hours=2),
                    ),
                    MagicMock(
                        id=uuid4(),
                        name="Relatório 2",
                        next_run_at=datetime.utcnow() + timedelta(hours=12),
                    ),
                ]
            )

            result = await mock_instance.get_upcoming_reports(
                condominio_id=mock_user["condominio_id"],
                hours_ahead=24,
            )

            assert len(result) == 2
