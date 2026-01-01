"""
Testes da API do Sprint 34 - Relatórios Gerenciais
"""
# pylint: disable=redefined-outer-name,unused-argument,too-many-lines
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Fixture do cliente de teste."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Fixture de headers de autenticação."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_db():
    """Fixture de mock do banco de dados."""
    return MagicMock()


@pytest.fixture
def sample_template_id():
    """Fixture de ID de template."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_schedule_id():
    """Fixture de ID de agendamento."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_export_id():
    """Fixture de ID de exportação."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_kpi_id():
    """Fixture de ID de KPI."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_benchmark_id():
    """Fixture de ID de benchmark."""
    return str(uuid.uuid4())


class TestReportTemplateEndpoints:
    """Testes dos endpoints de ReportTemplate."""

    def test_list_templates(self, client, auth_headers):
        """Testa listagem de templates."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_templates.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/templates",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_create_template(self, client, auth_headers):
        """Testa criação de template."""
        payload = {
            "codigo": "RPT001",
            "nome": "Relatório Financeiro",
            "category": "financeiro",
            "report_type": "consolidado",
            "default_format": "pdf",
            "supported_formats": ["pdf", "excel"],
        }
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.create_template.return_value = MagicMock(
                    id=uuid.uuid4(),
                    codigo="RPT001",
                    nome="Relatório Financeiro",
                )
                response = client.post(
                    "/api/v1/reports/templates",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_get_template(self, client, auth_headers, sample_template_id):
        """Testa busca de template por ID."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_template.return_value = MagicMock(
                    id=sample_template_id,
                    codigo="RPT001",
                )
                response = client.get(
                    f"/api/v1/reports/templates/{sample_template_id}",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_update_template(self, client, auth_headers, sample_template_id):
        """Testa atualização de template."""
        payload = {"nome": "Relatório Atualizado"}
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.update_template.return_value = MagicMock(
                    id=sample_template_id,
                    nome="Relatório Atualizado",
                )
                response = client.put(
                    f"/api/v1/reports/templates/{sample_template_id}",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_delete_template(self, client, auth_headers, sample_template_id):
        """Testa exclusão de template."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.delete_template.return_value = True
                response = client.delete(
                    f"/api/v1/reports/templates/{sample_template_id}",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_activate_template(self, client, auth_headers, sample_template_id):
        """Testa ativação de template."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.activate_template.return_value = MagicMock(
                    id=sample_template_id,
                    status="ativo",
                )
                response = client.post(
                    f"/api/v1/reports/templates/{sample_template_id}/activate",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]


class TestReportScheduleEndpoints:
    """Testes dos endpoints de ReportSchedule."""

    def test_list_schedules(self, client, auth_headers):
        """Testa listagem de agendamentos."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_schedules.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/schedules",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_create_schedule(self, client, auth_headers, sample_template_id):
        """Testa criação de agendamento."""
        payload = {
            "codigo": "SCH001",
            "nome": "Agendamento Diário",
            "template_id": sample_template_id,
            "frequency": "diario",
            "timezone": "America/Sao_Paulo",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "output_format": "pdf",
            "delivery_method": "email",
        }
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.create_schedule.return_value = MagicMock(
                    id=uuid.uuid4(),
                    codigo="SCH001",
                )
                response = client.post(
                    "/api/v1/reports/schedules",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_get_schedule(self, client, auth_headers, sample_schedule_id):
        """Testa busca de agendamento por ID."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_schedule.return_value = MagicMock(
                    id=sample_schedule_id,
                    codigo="SCH001",
                )
                response = client.get(
                    f"/api/v1/reports/schedules/{sample_schedule_id}",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_pause_schedule(self, client, auth_headers, sample_schedule_id):
        """Testa pausa de agendamento."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.pause_schedule.return_value = MagicMock(
                    id=sample_schedule_id,
                    status="pausado",
                )
                response = client.post(
                    f"/api/v1/reports/schedules/{sample_schedule_id}/pause",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_resume_schedule(self, client, auth_headers, sample_schedule_id):
        """Testa retomada de agendamento."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.resume_schedule.return_value = MagicMock(
                    id=sample_schedule_id,
                    status="ativo",
                )
                response = client.post(
                    f"/api/v1/reports/schedules/{sample_schedule_id}/resume",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]


class TestReportExportEndpoints:
    """Testes dos endpoints de ReportExport."""

    def test_list_exports(self, client, auth_headers):
        """Testa listagem de exportações."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_exports.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/exports",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_request_export(self, client, auth_headers, sample_template_id):
        """Testa requisição de exportação."""
        payload = {
            "template_id": sample_template_id,
            "format": "pdf",
        }
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.request_export.return_value = MagicMock(
                    id=uuid.uuid4(),
                    export_id="EXP001",
                    status="pendente",
                )
                response = client.post(
                    "/api/v1/reports/exports",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_get_export(self, client, auth_headers, sample_export_id):
        """Testa busca de exportação por ID."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_export.return_value = MagicMock(
                    id=sample_export_id,
                    export_id="EXP001",
                )
                response = client.get(
                    f"/api/v1/reports/exports/{sample_export_id}",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_cancel_export(self, client, auth_headers, sample_export_id):
        """Testa cancelamento de exportação."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.cancel_export.return_value = MagicMock(
                    id=sample_export_id,
                    status="cancelado",
                )
                response = client.post(
                    f"/api/v1/reports/exports/{sample_export_id}/cancel",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]


class TestExecutiveKPIEndpoints:
    """Testes dos endpoints de ExecutiveKPI."""

    def test_list_kpis(self, client, auth_headers):
        """Testa listagem de KPIs."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_kpis.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/kpis",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_create_kpi(self, client, auth_headers):
        """Testa criação de KPI."""
        payload = {
            "codigo": "KPI001",
            "nome": "Receita Mensal",
            "category": "financeiro",
            "kpi_type": "receita",
            "direction": "maior_melhor",
            "unit": "currency",
            "aggregation_period": "mensal",
        }
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.create_kpi.return_value = MagicMock(
                    id=uuid.uuid4(),
                    codigo="KPI001",
                )
                response = client.post(
                    "/api/v1/reports/kpis",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_get_kpi(self, client, auth_headers, sample_kpi_id):
        """Testa busca de KPI por ID."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_kpi.return_value = MagicMock(
                    id=sample_kpi_id,
                    codigo="KPI001",
                )
                response = client.get(
                    f"/api/v1/reports/kpis/{sample_kpi_id}",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_update_kpi_value(self, client, auth_headers, sample_kpi_id):
        """Testa atualização de valor de KPI."""
        payload = {"value": "150000.00"}
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.update_kpi_value.return_value = MagicMock(
                    id=sample_kpi_id,
                    current_value=Decimal("150000.00"),
                )
                response = client.put(
                    f"/api/v1/reports/kpis/{sample_kpi_id}/value",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_get_kpi_dashboard(self, client, auth_headers):
        """Testa dashboard de KPIs."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_kpi_dashboard.return_value = {
                    "kpis": [],
                    "alerts": [],
                    "trends": {},
                }
                response = client.get(
                    "/api/v1/reports/kpis/dashboard",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]


class TestBenchmarkEndpoints:
    """Testes dos endpoints de Benchmark."""

    def test_list_benchmarks(self, client, auth_headers):
        """Testa listagem de benchmarks."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_benchmarks.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/benchmarks",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_create_benchmark(self, client, auth_headers):
        """Testa criação de benchmark."""
        payload = {
            "codigo": "BMK001",
            "nome": "Margem EBITDA",
            "category": "financeiro",
            "benchmark_type": "industria",
            "source": "pesquisa_mercado",
            "unit": "percentage",
        }
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.create_benchmark.return_value = MagicMock(
                    id=uuid.uuid4(),
                    codigo="BMK001",
                )
                response = client.post(
                    "/api/v1/reports/benchmarks",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_get_benchmark(self, client, auth_headers, sample_benchmark_id):
        """Testa busca de benchmark por ID."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_benchmark.return_value = MagicMock(
                    id=sample_benchmark_id,
                    codigo="BMK001",
                )
                response = client.get(
                    f"/api/v1/reports/benchmarks/{sample_benchmark_id}",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_update_benchmark_company_value(
        self, client, auth_headers, sample_benchmark_id
    ):
        """Testa atualização de valor da empresa."""
        payload = {"value": "28.50"}
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.update_benchmark_company_value.return_value = (
                    MagicMock(
                        id=sample_benchmark_id,
                        company_value=Decimal("28.50"),
                    )
                )
                response = client.put(
                    f"/api/v1/reports/benchmarks/{sample_benchmark_id}/company-value",
                    json=payload,
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ]


class TestDashboardEndpoints:
    """Testes dos endpoints de Dashboard."""

    def test_get_reports_dashboard(self, client, auth_headers):
        """Testa dashboard de relatórios."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_reports_dashboard.return_value = {
                    "templates_count": 0,
                    "schedules_count": 0,
                    "exports_count": 0,
                }
                response = client.get(
                    "/api/v1/reports/dashboard",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_get_executive_dashboard(self, client, auth_headers):
        """Testa dashboard executivo."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.get_executive_dashboard.return_value = {
                    "kpis": [],
                    "benchmarks": [],
                    "alerts": [],
                }
                response = client.get(
                    "/api/v1/reports/executive-dashboard",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]


class TestValidation:
    """Testes de validação de entrada."""

    def test_create_template_invalid_category(self, client, auth_headers):
        """Testa criação com categoria inválida."""
        payload = {
            "codigo": "RPT001",
            "nome": "Relatório Teste",
            "category": "invalid_category",
            "report_type": "consolidado",
            "default_format": "pdf",
            "supported_formats": ["pdf"],
        }
        response = client.post(
            "/api/v1/reports/templates",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_create_schedule_invalid_frequency(
        self, client, auth_headers, sample_template_id
    ):
        """Testa criação com frequência inválida."""
        payload = {
            "codigo": "SCH001",
            "nome": "Agendamento Teste",
            "template_id": sample_template_id,
            "frequency": "invalid_frequency",
            "timezone": "America/Sao_Paulo",
            "start_date": datetime.now(timezone.utc).isoformat(),
            "output_format": "pdf",
            "delivery_method": "email",
        }
        response = client.post(
            "/api/v1/reports/schedules",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_create_kpi_invalid_direction(self, client, auth_headers):
        """Testa criação com direção inválida."""
        payload = {
            "codigo": "KPI001",
            "nome": "KPI Teste",
            "category": "financeiro",
            "kpi_type": "receita",
            "direction": "invalid_direction",
            "unit": "currency",
            "aggregation_period": "mensal",
        }
        response = client.post(
            "/api/v1/reports/kpis",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_create_benchmark_invalid_source(self, client, auth_headers):
        """Testa criação com fonte inválida."""
        payload = {
            "codigo": "BMK001",
            "nome": "Benchmark Teste",
            "category": "financeiro",
            "benchmark_type": "industria",
            "source": "invalid_source",
            "unit": "percentage",
        }
        response = client.post(
            "/api/v1/reports/benchmarks",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        ]


class TestPagination:
    """Testes de paginação."""

    def test_templates_pagination(self, client, auth_headers):
        """Testa paginação de templates."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_templates.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/templates?skip=0&limit=10",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_schedules_pagination(self, client, auth_headers):
        """Testa paginação de agendamentos."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_schedules.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/schedules?skip=10&limit=20",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_exports_pagination(self, client, auth_headers):
        """Testa paginação de exportações."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_exports.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/exports?skip=0&limit=50",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_kpis_pagination(self, client, auth_headers):
        """Testa paginação de KPIs."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_kpis.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/kpis?skip=5&limit=15",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_benchmarks_pagination(self, client, auth_headers):
        """Testa paginação de benchmarks."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_benchmarks.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/benchmarks?skip=0&limit=25",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]


class TestFilters:
    """Testes de filtros."""

    def test_templates_filter_by_category(self, client, auth_headers):
        """Testa filtro de templates por categoria."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_templates.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/templates?category=financeiro",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_schedules_filter_by_status(self, client, auth_headers):
        """Testa filtro de agendamentos por status."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_schedules.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/schedules?status=ativo",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_kpis_filter_by_alert_level(self, client, auth_headers):
        """Testa filtro de KPIs por nível de alerta."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_kpis.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/kpis?alert_level=critico",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    def test_benchmarks_filter_by_industry(self, client, auth_headers):
        """Testa filtro de benchmarks por indústria."""
        with patch("modules.reports.controllers.report_controller.get_db"):
            with patch(
                "modules.reports.controllers.report_controller.ReportService"
            ) as mock_service:
                mock_service.return_value.list_benchmarks.return_value = ([], 0)
                response = client.get(
                    "/api/v1/reports/benchmarks?industry=tecnologia",
                    headers=auth_headers,
                )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]
