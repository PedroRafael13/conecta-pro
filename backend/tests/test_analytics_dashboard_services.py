"""Testes unitários para services do módulo Analytics Dashboard."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from modules.hr.analytics_dashboard.services import (
    KPICalculatorService,
    MetricsAggregatorService,
    ReportGeneratorService,
    DashboardService,
)
from modules.hr.analytics_dashboard.models import (
    KPIDefinition,
    KPICategory,
    KPIUnit,
    KPIDirection,
    DashboardConfig,
    DashboardType,
    DashboardVisibility,
    ScheduledReport,
    ReportType,
    ReportFormat,
    ScheduleFrequency,
    DeliveryMethod,
)


class TestKPICalculatorService:
    """Testes para KPICalculatorService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco de dados."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Fixture para instância do serviço."""
        return KPICalculatorService(mock_db)

    @pytest.mark.asyncio
    async def test_calculate_absenteeism_rate(self, service):
        """Testa cálculo de taxa de absenteísmo."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=30)

        with patch.object(service, '_calculate_absenteeism_rate', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = {
                "value": Decimal("2.5"),
                "trend": "down",
                "trend_percentage": -0.5,
            }

            result = await service._calculate_absenteeism_rate(
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
            )

            assert result["value"] == Decimal("2.5")
            assert result["trend"] == "down"

    @pytest.mark.asyncio
    async def test_calculate_punctuality_rate(self, service):
        """Testa cálculo de taxa de pontualidade."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=30)

        with patch.object(service, '_calculate_punctuality_rate', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = {
                "value": Decimal("95.5"),
                "trend": "up",
                "trend_percentage": 2.0,
            }

            result = await service._calculate_punctuality_rate(
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
            )

            assert result["value"] == Decimal("95.5")
            assert result["trend"] == "up"

    @pytest.mark.asyncio
    async def test_calculate_overtime_hours(self, service):
        """Testa cálculo de horas extra."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=30)

        with patch.object(service, '_calculate_overtime_hours', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = {
                "value": Decimal("150.5"),
                "trend": "up",
                "trend_percentage": 10.0,
            }

            result = await service._calculate_overtime_hours(
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
            )

            assert result["value"] == Decimal("150.5")

    @pytest.mark.asyncio
    async def test_calculate_dashboard_kpis(self, service):
        """Testa cálculo de múltiplos KPIs para dashboard."""
        condominio_id = uuid4()
        kpi_codes = ["ABSENTEEISM_RATE", "PUNCTUALITY_RATE"]

        with patch.object(service, 'calculate_kpi', new_callable=AsyncMock) as mock_calc:
            mock_calc.side_effect = [
                {"code": "ABSENTEEISM_RATE", "value": 2.5},
                {"code": "PUNCTUALITY_RATE", "value": 95.0},
            ]

            results = await service.calculate_dashboard_kpis(
                condominio_id=condominio_id,
                kpi_codes=kpi_codes,
            )

            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_get_kpi_history(self, service):
        """Testa obtenção de histórico de KPI."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=30)

        with patch.object(service, 'get_kpi_history', new_callable=AsyncMock) as mock_history:
            mock_history.return_value = [
                {"date": "2024-12-01", "value": 2.5},
                {"date": "2024-12-02", "value": 2.3},
                {"date": "2024-12-03", "value": 2.6},
            ]

            result = await service.get_kpi_history(
                kpi_code="ABSENTEEISM_RATE",
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
                granularity="daily",
            )

            assert len(result) == 3


class TestMetricsAggregatorService:
    """Testes para MetricsAggregatorService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco de dados."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Fixture para instância do serviço."""
        return MetricsAggregatorService(mock_db)

    @pytest.mark.asyncio
    async def test_aggregate_time_entries(self, service):
        """Testa agregação de registros de ponto."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=7)

        with patch.object(service, 'aggregate_time_entries', new_callable=AsyncMock) as mock_agg:
            mock_agg.return_value = {
                "total_entries": 500,
                "total_hours": 4000.0,
                "avg_hours_per_day": 8.0,
            }

            result = await service.aggregate_time_entries(
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
            )

            assert result["total_entries"] == 500
            assert result["total_hours"] == 4000.0

    @pytest.mark.asyncio
    async def test_aggregate_checkins(self, service):
        """Testa agregação de check-ins."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=7)

        with patch.object(service, 'aggregate_checkins', new_callable=AsyncMock) as mock_agg:
            mock_agg.return_value = {
                "total_checkins": 1000,
                "on_time": 950,
                "late": 50,
                "on_time_percentage": 95.0,
            }

            result = await service.aggregate_checkins(
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
            )

            assert result["on_time_percentage"] == 95.0

    @pytest.mark.asyncio
    async def test_aggregate_overtime(self, service):
        """Testa agregação de horas extra."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=30)

        with patch.object(service, 'aggregate_overtime', new_callable=AsyncMock) as mock_agg:
            mock_agg.return_value = {
                "total_overtime_hours": 500.0,
                "employees_with_overtime": 45,
                "avg_overtime_per_employee": 11.1,
            }

            result = await service.aggregate_overtime(
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
            )

            assert result["total_overtime_hours"] == 500.0

    @pytest.mark.asyncio
    async def test_generate_time_series(self, service):
        """Testa geração de série temporal."""
        condominio_id = uuid4()
        now = datetime.utcnow()
        period_start = now - timedelta(days=7)

        with patch.object(service, 'generate_time_series', new_callable=AsyncMock) as mock_series:
            mock_series.return_value = [
                {"date": "2024-12-25", "value": 100},
                {"date": "2024-12-26", "value": 105},
                {"date": "2024-12-27", "value": 98},
            ]

            result = await service.generate_time_series(
                data_source="time_entries",
                aggregation="count",
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=now,
                granularity="daily",
            )

            assert len(result) == 3


class TestReportGeneratorService:
    """Testes para ReportGeneratorService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco de dados."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Fixture para instância do serviço."""
        return ReportGeneratorService(mock_db)

    @pytest.mark.asyncio
    async def test_generate_report(self, service):
        """Testa geração de relatório."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório de Ponto",
            report_type=ReportType.TIME_ATTENDANCE,
            output_format=ReportFormat.PDF,
            schedule_frequency=ScheduleFrequency.MONTHLY,
            delivery_method=DeliveryMethod.DOWNLOAD,
        )

        with patch.object(service, 'generate_report', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {
                "report_id": str(report.id),
                "status": "success",
                "file_path": "/tmp/report.pdf",
                "file_size": 1024,
            }

            result = await service.generate_report(report=report)

            assert result["status"] == "success"
            assert "file_path" in result

    @pytest.mark.asyncio
    async def test_generate_report_excel(self, service):
        """Testa geração de relatório em Excel."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório de Horas Extra",
            report_type=ReportType.OVERTIME_SUMMARY,
            output_format=ReportFormat.EXCEL,
            schedule_frequency=ScheduleFrequency.WEEKLY,
            delivery_method=DeliveryMethod.EMAIL,
        )

        with patch.object(service, 'generate_report', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {
                "report_id": str(report.id),
                "status": "success",
                "file_path": "/tmp/report.xlsx",
            }

            result = await service.generate_report(report=report)

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_process_due_reports(self, service):
        """Testa processamento de relatórios pendentes."""
        with patch.object(service, 'process_due_reports', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                "processed": 3,
                "success": 2,
                "failed": 1,
                "errors": ["Report X failed: connection error"],
            }

            result = await service.process_due_reports()

            assert result["processed"] == 3
            assert result["success"] == 2


class TestDashboardService:
    """Testes para DashboardService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco de dados."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Fixture para instância do serviço."""
        return DashboardService(mock_db)

    @pytest.mark.asyncio
    async def test_list_user_dashboards(self, service):
        """Testa listagem de dashboards do usuário."""
        condominio_id = uuid4()
        user_id = uuid4()

        with patch.object(service, 'list_user_dashboards', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = (
                [
                    {"id": str(uuid4()), "name": "Dashboard 1"},
                    {"id": str(uuid4()), "name": "Dashboard 2"},
                ],
                2,
            )

            dashboards, total = await service.list_user_dashboards(
                condominio_id=condominio_id,
                user_id=user_id,
            )

            assert total == 2
            assert len(dashboards) == 2

    @pytest.mark.asyncio
    async def test_create_dashboard(self, service):
        """Testa criação de dashboard."""
        condominio_id = uuid4()
        owner_id = uuid4()

        with patch.object(service, 'create_dashboard', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {
                "id": str(uuid4()),
                "name": "Novo Dashboard",
                "dashboard_type": "custom",
            }

            from modules.hr.analytics_dashboard.schemas import DashboardConfigCreate
            data = MagicMock(spec=DashboardConfigCreate)
            data.name = "Novo Dashboard"

            result = await service.create_dashboard(
                data=data,
                condominio_id=condominio_id,
                owner_id=owner_id,
            )

            assert result["name"] == "Novo Dashboard"

    @pytest.mark.asyncio
    async def test_clone_dashboard(self, service):
        """Testa clonagem de dashboard."""
        source_id = uuid4()
        user_id = uuid4()

        with patch.object(service, 'clone_dashboard', new_callable=AsyncMock) as mock_clone:
            mock_clone.return_value = {
                "id": str(uuid4()),
                "name": "Dashboard Clonado",
            }

            result = await service.clone_dashboard(
                source_id=source_id,
                new_name="Dashboard Clonado",
                user_id=user_id,
            )

            assert result["name"] == "Dashboard Clonado"

    @pytest.mark.asyncio
    async def test_add_widget(self, service):
        """Testa adição de widget."""
        dashboard_id = uuid4()
        user_id = uuid4()

        with patch.object(service, 'add_widget', new_callable=AsyncMock) as mock_add:
            mock_add.return_value = {
                "id": str(uuid4()),
                "title": "Novo Widget",
                "widget_type": "kpi_card",
            }

            from modules.hr.analytics_dashboard.schemas import DashboardWidgetCreate
            data = MagicMock(spec=DashboardWidgetCreate)
            data.title = "Novo Widget"

            result = await service.add_widget(
                dashboard_id=dashboard_id,
                data=data,
                user_id=user_id,
            )

            assert result["title"] == "Novo Widget"

    @pytest.mark.asyncio
    async def test_refresh_dashboard_data(self, service):
        """Testa atualização de dados do dashboard."""
        dashboard_id = uuid4()
        user_id = uuid4()

        with patch.object(service, 'refresh_dashboard_data', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = {
                "dashboard_id": str(dashboard_id),
                "widgets_refreshed": 5,
                "refreshed_at": datetime.utcnow().isoformat(),
            }

            result = await service.refresh_dashboard_data(
                dashboard_id=dashboard_id,
                user_id=user_id,
            )

            assert result["widgets_refreshed"] == 5

    @pytest.mark.asyncio
    async def test_get_widget_data(self, service):
        """Testa obtenção de dados de widget."""
        widget_id = uuid4()
        user_id = uuid4()

        with patch.object(service, 'get_widget_data', new_callable=AsyncMock) as mock_data:
            mock_data.return_value = {
                "widget_id": str(widget_id),
                "data": [
                    {"label": "Jan", "value": 100},
                    {"label": "Fev", "value": 120},
                ],
                "cached": False,
            }

            result = await service.get_widget_data(
                widget_id=widget_id,
                user_id=user_id,
            )

            assert len(result["data"]) == 2


class TestKPIThresholdEvaluation:
    """Testes para avaliação de thresholds de KPI."""

    def test_evaluate_threshold_good(self):
        """Testa avaliação de threshold - bom."""
        kpi = KPIDefinition(
            id=uuid4(),
            code="PUNCTUALITY_RATE",
            name="Taxa de Pontualidade",
            category=KPICategory.PUNCTUALITY,
            unit=KPIUnit.PERCENTAGE,
            direction=KPIDirection.UP,
            target_value=Decimal("95.0"),
            threshold_warning=Decimal("90.0"),
            threshold_critical=Decimal("85.0"),
        )

        # Valor acima do target para KPI com direção UP
        value = Decimal("96.0")
        status = _evaluate_threshold(kpi, value)
        assert status == "good"

    def test_evaluate_threshold_warning(self):
        """Testa avaliação de threshold - warning."""
        kpi = KPIDefinition(
            id=uuid4(),
            code="ABSENTEEISM_RATE",
            name="Taxa de Absenteísmo",
            category=KPICategory.ATTENDANCE,
            unit=KPIUnit.PERCENTAGE,
            direction=KPIDirection.DOWN,
            target_value=Decimal("3.0"),
            threshold_warning=Decimal("5.0"),
            threshold_critical=Decimal("8.0"),
        )

        # Valor acima do warning para KPI com direção DOWN
        value = Decimal("6.0")
        status = _evaluate_threshold(kpi, value)
        assert status == "warning"

    def test_evaluate_threshold_critical(self):
        """Testa avaliação de threshold - critical."""
        kpi = KPIDefinition(
            id=uuid4(),
            code="ABSENTEEISM_RATE",
            name="Taxa de Absenteísmo",
            category=KPICategory.ATTENDANCE,
            unit=KPIUnit.PERCENTAGE,
            direction=KPIDirection.DOWN,
            target_value=Decimal("3.0"),
            threshold_warning=Decimal("5.0"),
            threshold_critical=Decimal("8.0"),
        )

        # Valor acima do critical para KPI com direção DOWN
        value = Decimal("10.0")
        status = _evaluate_threshold(kpi, value)
        assert status == "critical"


def _evaluate_threshold(kpi: KPIDefinition, value: Decimal) -> str:
    """Função auxiliar para avaliar threshold de KPI."""
    if kpi.threshold_critical is None or kpi.threshold_warning is None:
        return "neutral"

    if kpi.direction == KPIDirection.UP:
        # Maior é melhor
        if value >= kpi.target_value:
            return "good"
        elif value >= kpi.threshold_warning:
            return "warning"
        else:
            return "critical"
    elif kpi.direction == KPIDirection.DOWN:
        # Menor é melhor
        if value <= kpi.target_value:
            return "good"
        elif value <= kpi.threshold_warning:
            return "warning"
        else:
            return "critical"
    else:
        # Target ou Neutral
        if kpi.target_value:
            diff = abs(value - kpi.target_value)
            if diff <= kpi.target_value * Decimal("0.05"):
                return "good"
            elif diff <= kpi.target_value * Decimal("0.15"):
                return "warning"
            else:
                return "critical"
        return "neutral"
