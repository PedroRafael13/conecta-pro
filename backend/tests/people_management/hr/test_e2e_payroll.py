"""
Testes E2E da Folha de Pagamento (DP) — endpoints FastAPI com DB mockado e services mockados.

Endpoints cobertos:
  GET /payroll/employee/{id}/calculate      — calcular folha de pagamento
  GET /payroll/employee/{id}/payslip-pdf    — gerar contracheque PDF
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.auth.dependencies import get_current_active_user
from core.database.session import get_db
from modules.people_management.hr.controllers.payroll_controller import (
    router as payroll_router,
)

# ===========================================================================
# FAKE DB + FAKE USER
# ===========================================================================


class FakeAsyncSession:
    """AsyncSession fake (sem banco real)."""

    def __init__(self):
        self._added: list = []

    def add(self, obj):
        self._added.append(obj)

    async def flush(self):
        self._added.clear()

    async def refresh(self, obj):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def execute(self, stmt, params=None):
        return FakeResult()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeResult:
    """Resultado fake de query SQLAlchemy."""

    def scalar_one_or_none(self):
        return None

    def scalar(self):
        return 0

    def scalars(self):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def fetchall(self):
        return []

    def fetchone(self):
        return None

    def mappings(self):
        return self


async def get_fake_db():
    yield FakeAsyncSession()


class FakeUser:
    id = "user-test-001"
    email = "admin@conectapro.com.br"
    role = "admin"
    is_active = True
    permissions = ["*"]


async def get_fake_current_user():
    return FakeUser()


# ===========================================================================
# FIXTURES
# ===========================================================================

PATCH_PAYROLL_SERVICE = "modules.people_management.hr.controllers.payroll_controller.PayrollService"

# Folha de pagamento realista para uso nos testes
MOCK_PAYROLL_FULL = {
    "employee_id": "emp-001",
    "employee_name": "João Silva",
    "cargo": "Vigilante Patrimonial",
    "matricula": "VIG-001",
    "cpf": "123.456.789-01",
    "data_admissao": "2023-01-15",
    "reference": "03/2026",
    "salario_base": 2000.00,
    "valor_hora": 9.09,
    "proventos": [
        {"codigo": "001", "descricao": "Salário Base", "ref": "30d", "valor": 2000.00},
        {"codigo": "010", "descricao": "Periculosidade 30%", "ref": "30%", "valor": 600.00},
    ],
    "descontos": [
        {"codigo": "201", "descricao": "INSS Progressivo", "ref": "", "valor": 228.96},
        {"codigo": "210", "descricao": "VT 4%", "ref": "4%", "valor": 80.00},
    ],
    "total_proventos": 2600.00,
    "total_descontos": 308.96,
    "salario_liquido": 2291.04,
    "fgts_8_pct": 208.00,
    "base_inss": 2600.00,
    "base_irrf": 2371.04,
}

MOCK_PAYROLL_MINIMAL = {
    "employee_id": "emp-002",
    "employee_name": "Maria Santos",
    "cargo": "Porteiro",
    "matricula": "PRT-002",
    "cpf": "987.654.321-00",
    "data_admissao": "2024-06-01",
    "reference": "03/2026",
    "salario_base": 1518.00,
    "valor_hora": 6.90,
    "proventos": [
        {"codigo": "001", "descricao": "Salário Base", "ref": "30d", "valor": 1518.00},
    ],
    "descontos": [
        {"codigo": "201", "descricao": "INSS Progressivo", "ref": "", "valor": 114.00},
        {"codigo": "210", "descricao": "VT 4%", "ref": "4%", "valor": 60.72},
    ],
    "total_proventos": 1518.00,
    "total_descontos": 174.72,
    "salario_liquido": 1343.28,
    "fgts_8_pct": 121.44,
    "base_inss": 1518.00,
    "base_irrf": 1404.00,
}


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(payroll_router, prefix="/api/v1")
    application.dependency_overrides[get_db] = get_fake_db
    application.dependency_overrides[get_current_active_user] = get_fake_current_user
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ===========================================================================
# GET /payroll/employee/{employee_id}/calculate
# ===========================================================================


class TestCalculatePayroll:
    """Testes E2E para GET /payroll/employee/{id}/calculate."""

    @pytest.mark.asyncio
    async def test_calculate_happy_path(self, client):
        """Happy path — retorna folha completa com proventos, descontos e totais."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=MOCK_PAYROLL_FULL)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-001/calculate",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == "emp-001"
        assert data["employee_name"] == "João Silva"
        assert data["reference"] == "03/2026"
        assert data["salario_base"] == 2000.00
        assert data["total_proventos"] == 2600.00
        assert data["total_descontos"] == 308.96
        assert data["salario_liquido"] == 2291.04
        assert data["fgts_8_pct"] == 208.00
        assert len(data["proventos"]) == 2
        assert len(data["descontos"]) == 2

    @pytest.mark.asyncio
    async def test_calculate_minimal_salary(self, client):
        """Funcionario com salario minimo — sem periculosidade, sem extras."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=MOCK_PAYROLL_MINIMAL)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-002/calculate",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == "emp-002"
        assert data["salario_base"] == 1518.00
        assert data["total_proventos"] == 1518.00
        assert data["salario_liquido"] == 1343.28

    @pytest.mark.asyncio
    async def test_calculate_employee_not_found_returns_400(self, client):
        """Funcionario inexistente → service lanca ValueError → 400."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(
            side_effect=ValueError("Funcionário emp-999 não encontrado")
        )

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-999/calculate",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 400
        data = response.json()
        assert "não encontrado" in data["detail"] or "não encontrado" in data.get("detail", "")

    @pytest.mark.asyncio
    async def test_calculate_missing_month_returns_422(self, client):
        """Sem parametro month → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/calculate",
            params={"year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_missing_year_returns_422(self, client):
        """Sem parametro year → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/calculate",
            params={"month": 3},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_month_zero_returns_422(self, client):
        """month=0 (abaixo do minimo ge=1) → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/calculate",
            params={"month": 0, "year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_month_thirteen_returns_422(self, client):
        """month=13 (acima do maximo le=12) → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/calculate",
            params={"month": 13, "year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_year_before_2020_returns_422(self, client):
        """year=2019 (abaixo do minimo ge=2020) → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/calculate",
            params={"month": 3, "year": 2019},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_year_after_2030_returns_422(self, client):
        """year=2031 (acima do maximo le=2030) → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/calculate",
            params={"month": 3, "year": 2031},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_january_boundary(self, client):
        """Mes de Janeiro (month=1) — limite inferior valido."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(
            return_value={**MOCK_PAYROLL_MINIMAL, "reference": "01/2026"}
        )

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-001/calculate",
                params={"month": 1, "year": 2026},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["reference"] == "01/2026"

    @pytest.mark.asyncio
    async def test_calculate_december_boundary(self, client):
        """Mes de Dezembro (month=12) — limite superior valido."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(
            return_value={**MOCK_PAYROLL_MINIMAL, "reference": "12/2026"}
        )

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-001/calculate",
                params={"month": 12, "year": 2026},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["reference"] == "12/2026"

    @pytest.mark.asyncio
    async def test_calculate_calls_service_with_correct_args(self, client):
        """Verifica que o service recebe employee_id, month e year corretos."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=MOCK_PAYROLL_FULL)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            await client.get(
                "/api/v1/payroll/employee/emp-verify/calculate",
                params={"month": 5, "year": 2025},
            )

        mock_service.calculate_employee_payroll.assert_awaited_once_with("emp-verify", 5, 2025)

    @pytest.mark.asyncio
    async def test_calculate_with_extras_and_discounts(self, client):
        """Folha com horas extras, adicional noturno e multiplos descontos."""
        mock_payroll_extras = {
            **MOCK_PAYROLL_FULL,
            "proventos": [
                {"codigo": "001", "descricao": "Salário Base", "ref": "30d", "valor": 2000.00},
                {"codigo": "010", "descricao": "Periculosidade 30%", "ref": "30%", "valor": 600.00},
                {"codigo": "020", "descricao": "Ad. Noturno 20%", "ref": "48h", "valor": 87.27},
                {"codigo": "030", "descricao": "Hora Extra 50%", "ref": "8h", "valor": 109.09},
                {"codigo": "040", "descricao": "DSR s/ Extras", "ref": "", "valor": 39.67},
            ],
            "total_proventos": 2836.03,
            "descontos": [
                {"codigo": "201", "descricao": "INSS Progressivo", "ref": "", "valor": 284.25},
                {"codigo": "202", "descricao": "IRRF", "ref": "", "valor": 45.00},
                {"codigo": "210", "descricao": "VT 4%", "ref": "4%", "valor": 80.00},
            ],
            "total_descontos": 409.25,
            "salario_liquido": 2426.78,
        }
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=mock_payroll_extras)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-001/calculate",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["proventos"]) == 5
        assert len(data["descontos"]) == 3
        assert data["total_proventos"] == 2836.03
        assert data["salario_liquido"] == 2426.78


# ===========================================================================
# GET /payroll/employee/{employee_id}/payslip-pdf
# ===========================================================================


class TestGeneratePayslipPdf:
    """Testes E2E para GET /payroll/employee/{id}/payslip-pdf."""

    @pytest.mark.asyncio
    async def test_payslip_pdf_happy_path(self, client):
        """Happy path — retorna PDF com Content-Type correto e nome de arquivo."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=MOCK_PAYROLL_FULL)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-001/payslip-pdf",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 200
        assert "application/pdf" in response.headers["content-type"]
        assert "content-disposition" in response.headers
        assert "contracheque" in response.headers["content-disposition"].lower()
        assert len(response.content) > 100  # PDF nao eh vazio

    @pytest.mark.asyncio
    async def test_payslip_pdf_filename_contains_employee_name(self, client):
        """Nome do arquivo PDF deve conter nome do funcionario e competencia."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=MOCK_PAYROLL_FULL)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-001/payslip-pdf",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 200
        content_disposition = response.headers.get("content-disposition", "")
        assert "03" in content_disposition
        assert "2026" in content_disposition

    @pytest.mark.asyncio
    async def test_payslip_pdf_employee_not_found_returns_400(self, client):
        """Funcionario inexistente → service lanca ValueError → 400."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(
            side_effect=ValueError("Funcionário emp-999 não encontrado")
        )

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-999/payslip-pdf",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 400
        data = response.json()
        assert "não encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_payslip_pdf_missing_month_returns_422(self, client):
        """Sem parametro month → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/payslip-pdf",
            params={"year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_payslip_pdf_missing_year_returns_422(self, client):
        """Sem parametro year → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/payslip-pdf",
            params={"month": 3},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_payslip_pdf_month_zero_returns_422(self, client):
        """month=0 → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/payslip-pdf",
            params={"month": 0, "year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_payslip_pdf_month_thirteen_returns_422(self, client):
        """month=13 → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/payslip-pdf",
            params={"month": 13, "year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_payslip_pdf_year_before_2020_returns_422(self, client):
        """year=2019 → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/payslip-pdf",
            params={"month": 3, "year": 2019},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_payslip_pdf_year_after_2030_returns_422(self, client):
        """year=2031 → 422."""
        response = await client.get(
            "/api/v1/payroll/employee/emp-001/payslip-pdf",
            params={"month": 3, "year": 2031},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_payslip_pdf_content_is_valid_pdf_header(self, client):
        """Conteudo binario deve comecar com header PDF (%PDF)."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=MOCK_PAYROLL_MINIMAL)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-002/payslip-pdf",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 200
        # ReportLab gera PDF valido comecando com %PDF
        assert response.content[:4] == b"%PDF"

    @pytest.mark.asyncio
    async def test_payslip_pdf_december_boundary(self, client):
        """Mes de Dezembro (month=12) — limite superior valido."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(
            return_value={**MOCK_PAYROLL_MINIMAL, "reference": "12/2025", "employee_name": "Carlos Teste"}
        )

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-003/payslip-pdf",
                params={"month": 12, "year": 2025},
            )

        assert response.status_code == 200
        assert "application/pdf" in response.headers["content-type"]
        assert "12" in response.headers.get("content-disposition", "")
        assert "2025" in response.headers.get("content-disposition", "")

    @pytest.mark.asyncio
    async def test_payslip_pdf_inline_disposition(self, client):
        """Content-Disposition deve ser inline (nao attachment)."""
        mock_service = MagicMock()
        mock_service.calculate_employee_payroll = AsyncMock(return_value=MOCK_PAYROLL_FULL)

        with patch(PATCH_PAYROLL_SERVICE, return_value=mock_service):
            response = await client.get(
                "/api/v1/payroll/employee/emp-001/payslip-pdf",
                params={"month": 3, "year": 2026},
            )

        assert response.status_code == 200
        assert "inline" in response.headers.get("content-disposition", "").lower()
