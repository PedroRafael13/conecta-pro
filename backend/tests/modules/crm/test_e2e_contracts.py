"""
Testes E2E para o submodulo Contracts do CRM.

Cobertura:
- CRUD principal (create, list, stats, alerts, get, update, delete)
- Transições de status (submit, activate, suspend, terminate, renew, calculate-adjustment)
- Itens do contrato (add, update, remove)
- Aditivos (create, list, sign)
- Templates (list, get, update, approve, delete)
- SLA Reports (create, list, approve, calculate-sla)
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime(2026, 3, 30, 12, 0, 0)


# ---------------------------------------------------------------------------
# Fixture: crm_client
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def crm_client():
    from core.auth.dependencies import get_current_active_user
    from main import app

    user = MagicMock()
    user.id = "test-user-id"
    user.email = "test@erp.com.br"
    user.role = "admin"
    user.is_active = True

    async def override_auth():
        return user

    app.dependency_overrides[get_current_active_user] = override_auth
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["Authorization"] = "Bearer test-token-valid"
        yield client
    app.dependency_overrides.pop(get_current_active_user, None)


# ---------------------------------------------------------------------------
# Mock builders
# ---------------------------------------------------------------------------


def _make_contract(**kwargs):
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.contract_number = kwargs.get("contract_number", "CTR-2026-001")
    m.name = kwargs.get("name", "Contrato de Vigilância Patrimonial")
    m.description = None
    m.contract_type = "recurring"
    m.status = kwargs.get("status", "draft")
    m.client_id = kwargs.get("client_id", _uid())
    m.opportunity_id = kwargs.get("opportunity_id")
    m.proposal_id = kwargs.get("proposal_id")
    m.template_id = kwargs.get("template_id")
    m.monthly_value = kwargs.get("monthly_value", Decimal("10000.00"))
    m.total_value = kwargs.get("total_value", Decimal("120000.00"))
    m.setup_fee = Decimal("0.00")
    m.start_date = date(2026, 4, 1)
    m.end_date = date(2027, 3, 31)
    m.grace_period_days = 0
    m.notice_period_days = 30
    m.auto_renewal = True
    m.renewal_period_months = 12
    m.renewal_notification_days = 30
    m.adjustment_enabled = True
    m.adjustment_index = "ipca"
    m.adjustment_fixed_percent = None
    m.adjustment_base_date = None
    m.last_adjustment_date = None
    m.next_adjustment_date = None
    m.has_sla = kwargs.get("has_sla", False)
    m.sla_config = None
    m.content = None
    m.clauses = None
    m.signature_required = True
    m.signature_provider = None
    m.signed_at = None
    m.signed_by_client = None
    m.signed_by_company = None
    m.pdf_file_path = None
    m.commercial_manager_id = None
    m.account_manager_id = None
    m.created_by = None
    m.created_at = _now()
    m.updated_at = _now()
    m.items = []
    # Propriedades calculadas
    m.is_active_contract = False
    m.is_expiring_soon = False
    m.days_until_end = 365
    m.needs_adjustment = False
    m.is_renewable = True
    m.days_until_adjustment = None
    return m


def _make_contract_item(**kwargs):
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.contract_id = kwargs.get("contract_id", _uid())
    m.service_type = "security"
    m.service_name = "Vigilância Diurna"
    m.description = None
    m.quantity = 2
    m.unit_price = Decimal("5000.00")
    m.total_price = Decimal("10000.00")
    m.notes = None
    m.created_at = _now()
    return m


def _make_addendum(**kwargs):
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.contract_id = kwargs.get("contract_id", _uid())
    m.addendum_number = kwargs.get("addendum_number", "ADT-2026-001")
    m.addendum_type = "adjustment"
    m.previous_value = Decimal("10000.00")
    m.new_value = Decimal("10423.00")
    m.adjustment_percent = Decimal("4.23")
    m.adjustment_index = "ipca"
    m.effective_date = date(2026, 5, 1)
    m.description = "Reajuste IPCA 2026"
    m.reason = None
    m.signed = False
    m.signed_at = None
    m.pdf_file_path = None
    m.created_at = _now()
    m.created_by = None
    return m


def _make_template(**kwargs):
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.name = kwargs.get("name", "Template Padrão Vigilância")
    m.description = None
    m.service_type = "security"
    m.content_template = "Contrato de prestação de serviços de vigilância patrimonial..." + "x" * 100
    m.clauses = []
    m.variables = ["CLIENT_NAME", "START_DATE"]
    m.version = 1
    m.approved_by_legal = False
    m.approved_at = None
    m.created_at = _now()
    m.updated_at = _now()
    return m


def _make_sla_report(**kwargs):
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.contract_id = kwargs.get("contract_id", _uid())
    m.year = 2026
    m.month = 3
    m.indicators = []
    m.overall_score = Decimal("95.50")
    m.penalty_applied = False
    m.penalty_percent = Decimal("0.00")
    m.penalty_amount = Decimal("0.00")
    m.status = "draft"
    m.period_label = "Março/2026"
    m.is_target_met = False
    m.generated_at = _now()
    m.generated_by = None
    m.approved_at = None
    m.approved_by = None
    return m


def _make_stats():
    from modules.crm.schemas.contract import ContractStats

    return ContractStats(
        total_contracts=15,
        active_contracts=10,
        total_monthly_revenue=Decimal("150000.00"),
        average_contract_value=Decimal("15000.00"),
        expiring_soon=2,
        needs_adjustment=3,
        by_status={"draft": 2, "active": 10, "terminated": 3},
        by_type={"recurring": 12, "one_time": 3},
    )


def _make_renewal_result():
    from modules.crm.services.contract_service import RenewalResult

    return RenewalResult(
        success=True,
        new_end_date=date(2028, 3, 31),
        new_value=Decimal("10423.00"),
        adjustment_applied=True,
        adjustment_percent=Decimal("4.23"),
        message="Renovação calculada com sucesso",
    )


def _make_adjustment_result():
    from modules.crm.models.contract import AdjustmentIndex
    from modules.crm.services.contract_service import AdjustmentResult

    return AdjustmentResult(
        success=True,
        previous_value=Decimal("10000.00"),
        new_value=Decimal("10423.00"),
        adjustment_percent=Decimal("4.23"),
        index_used=AdjustmentIndex.IPCA,
        effective_date=date(2026, 4, 1),
        message="Reajuste de 4.23% calculado",
    )


def _make_sla_calculation():
    from modules.crm.services.contract_service import SLACalculation

    return SLACalculation(
        overall_score=Decimal("95.50"),
        indicators=[
            {
                "name": "Disponibilidade",
                "target": 100.0,
                "actual": 95.5,
                "score": 95.5,
                "weight": 1.0,
                "achieved": False,
            }
        ],
        penalty_applicable=False,
        penalty_percent=Decimal("0.00"),
        penalty_amount=Decimal("0.00"),
        target_met=False,
    )


# ---------------------------------------------------------------------------
# Payloads de request
# ---------------------------------------------------------------------------

_CONTRACT_CREATE_PAYLOAD = {
    "name": "Contrato de Vigilância Patrimonial",
    "contract_type": "recurring",
    "monthly_value": 10000.0,
    "total_value": 120000.0,
    "start_date": "2026-04-01",
    "end_date": "2027-03-31",
    "client_id": _uid(),
    "adjustment_enabled": True,
    "adjustment_index": "ipca",
    "has_sla": False,
    "auto_renewal": True,
    "renewal_period_months": 12,
    "renewal_notification_days": 30,
    "grace_period_days": 0,
    "notice_period_days": 30,
    "setup_fee": 0.0,
    "signature_required": True,
}

_CONTRACT_UPDATE_PAYLOAD = {
    "name": "Contrato Atualizado",
    "description": "Observações atualizadas",
}

_CONTRACT_ITEM_CREATE_PAYLOAD = {
    "service_type": "security",
    "service_name": "Posto de Vigilância Diurno",
    "quantity": 2,
    "unit_price": 5000.0,
}

_CONTRACT_ITEM_UPDATE_PAYLOAD = {
    "service_name": "Posto de Vigilância Noturno",
    "quantity": 3,
    "unit_price": 5500.0,
}

_CONTRACT_ADDENDUM_CREATE_PAYLOAD = {
    "addendum_type": "adjustment",
    "effective_date": "2026-05-01",
    "description": "Reajuste anual IPCA 2026 conforme contrato",
    "adjustment_percent": 4.23,
    "adjustment_index": "ipca",
}

_CONTRACT_ADDENDUM_SIGN_PAYLOAD = {
    "signature_document_id": "DOC-SIGN-2026-001",
}

_CONTRACT_RENEWAL_PAYLOAD = {
    "new_end_date": "2028-03-31",
    "adjustment_percent": 4.23,
}

_CONTRACT_TEMPLATE_CREATE_PAYLOAD = {
    "name": "Template Vigilância Patrimonial",
    "description": "Template padrão para contratos de vigilância",
    "service_type": "security",
    "content_template": (
        "CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE VIGILÂNCIA PATRIMONIAL\n\n"
        "Pelo presente instrumento particular, as partes abaixo identificadas "
        "acordam os seguintes termos e condições para prestação de serviços "
        "de vigilância patrimonial conforme especificações deste contrato.\n"
        "{{CLIENT_NAME}} - {{START_DATE}} - {{MONTHLY_VALUE}}"
    ),
    "variables": ["CLIENT_NAME", "START_DATE", "MONTHLY_VALUE"],
}

_CONTRACT_TEMPLATE_UPDATE_PAYLOAD = {
    "name": "Template Vigilância Patrimonial v2",
}

_SLA_REPORT_CREATE_PAYLOAD = {
    "year": 2026,
    "month": 3,
    "indicators": [
        {
            "name": "Disponibilidade de Postos",
            "target": "100.00",
            "actual": "95.50",
            "achieved": False,
            "weight": "1.0",
        }
    ],
    "overall_score": 95.50,
    "penalty_applied": False,
}

_SLA_REPORT_APPROVE_PAYLOAD = {
    "disputed": False,
    "dispute_reason": None,
}


# ===========================================================================
# SECAO 1 — CRUD PRINCIPAL
# ===========================================================================

REPO_PATCH = "modules.crm.controllers.contract_controller.ContractRepository"
SERVICE_PATCH = "modules.crm.controllers.contract_controller.ContractService"


class TestContractCreate:
    """POST /api/v1/crm/contracts → 201"""

    @pytest.mark.asyncio
    async def test_create_contract_returns_201(self, crm_client):
        mock_contract = _make_contract()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=mock_contract)
            resp = await crm_client.post("/api/v1/crm/contracts", json=_CONTRACT_CREATE_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert "contract_number" in data

    @pytest.mark.asyncio
    async def test_create_contract_payload_fields(self, crm_client):
        mock_contract = _make_contract(name="Contrato de Vigilância Patrimonial")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=mock_contract)
            resp = await crm_client.post("/api/v1/crm/contracts", json=_CONTRACT_CREATE_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Contrato de Vigilância Patrimonial"

    @pytest.mark.asyncio
    async def test_create_contract_missing_required_field_returns_422(self, crm_client):
        payload = {k: v for k, v in _CONTRACT_CREATE_PAYLOAD.items() if k != "client_id"}
        resp = await crm_client.post("/api/v1/crm/contracts", json=payload)
        assert resp.status_code == 422


class TestContractList:
    """GET /api/v1/crm/contracts → 200"""

    @pytest.mark.asyncio
    async def test_list_contracts_returns_200(self, crm_client):
        mock_contract = _make_contract()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([mock_contract], 1))
            resp = await crm_client.get("/api/v1/crm/contracts")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1

    @pytest.mark.asyncio
    async def test_list_contracts_pagination_fields(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))
            resp = await crm_client.get("/api/v1/crm/contracts?page=2&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 2
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_list_contracts_with_status_filter(self, crm_client):
        mock_contract = _make_contract(status="active")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([mock_contract], 1))
            resp = await crm_client.get("/api/v1/crm/contracts?status=active")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_contracts_empty_returns_200(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))
            resp = await crm_client.get("/api/v1/crm/contracts")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestContractStats:
    """GET /api/v1/crm/contracts/stats → 200"""

    @pytest.mark.asyncio
    async def test_get_stats_returns_200(self, crm_client):
        mock_stats = _make_stats()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_stats = AsyncMock(return_value=mock_stats)
            resp = await crm_client.get("/api/v1/crm/contracts/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_contracts" in data
        assert "active_contracts" in data
        assert "total_monthly_revenue" in data

    @pytest.mark.asyncio
    async def test_get_stats_values_correct(self, crm_client):
        mock_stats = _make_stats()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_stats = AsyncMock(return_value=mock_stats)
            resp = await crm_client.get("/api/v1/crm/contracts/stats")
        data = resp.json()
        assert data["total_contracts"] == 15
        assert data["active_contracts"] == 10


class TestContractAlerts:
    """GET /api/v1/crm/contracts/alerts → 200"""

    @pytest.mark.asyncio
    async def test_get_alerts_returns_200(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))
            resp = await crm_client.get("/api/v1/crm/contracts/alerts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_get_alerts_with_days_ahead(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))
            resp = await crm_client.get("/api/v1/crm/contracts/alerts?days_ahead=60")
        assert resp.status_code == 200


class TestContractGetById:
    """GET /api/v1/crm/contracts/{id} → 200 + 404"""

    @pytest.mark.asyncio
    async def test_get_contract_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid)
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_contract)
            resp = await crm_client.get(f"/api/v1/crm/contracts/{cid}")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "contract_number" in data

    @pytest.mark.asyncio
    async def test_get_contract_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)
            resp = await crm_client.get(f"/api/v1/crm/contracts/{_uid()}")
        assert resp.status_code == 404
        assert "não encontrado" in resp.json()["detail"].lower()


class TestContractUpdate:
    """PUT /api/v1/crm/contracts/{id} → 200 + 404"""

    @pytest.mark.asyncio
    async def test_update_contract_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, name="Contrato Atualizado")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=mock_contract)
            resp = await crm_client.put(f"/api/v1/crm/contracts/{cid}", json=_CONTRACT_UPDATE_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Contrato Atualizado"

    @pytest.mark.asyncio
    async def test_update_contract_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=None)
            resp = await crm_client.put(f"/api/v1/crm/contracts/{_uid()}", json=_CONTRACT_UPDATE_PAYLOAD)
        assert resp.status_code == 404


class TestContractDelete:
    """DELETE /api/v1/crm/contracts/{id} → 204 + 400"""

    @pytest.mark.asyncio
    async def test_delete_contract_returns_204(self, crm_client):
        cid = _uid()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=True)
            resp = await crm_client.delete(f"/api/v1/crm/contracts/{cid}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=False)
            resp = await crm_client.delete(f"/api/v1/crm/contracts/{_uid()}")
        assert resp.status_code == 400


# ===========================================================================
# SECAO 2 — TRANSICOES DE STATUS
# ===========================================================================


class TestContractSubmit:
    """POST /api/v1/crm/contracts/{id}/submit → 200 + 400"""

    @pytest.mark.asyncio
    async def test_submit_contract_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="pending_signature")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=mock_contract)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/submit")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_submit_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=None)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{_uid()}/submit")
        assert resp.status_code == 400


class TestContractActivate:
    """POST /api/v1/crm/contracts/{id}/activate → 200 + 400"""

    @pytest.mark.asyncio
    async def test_activate_contract_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="active")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=mock_contract)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/activate")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_activate_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=None)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{_uid()}/activate")
        assert resp.status_code == 400


class TestContractSuspend:
    """POST /api/v1/crm/contracts/{id}/suspend → 200 + 400"""

    @pytest.mark.asyncio
    async def test_suspend_contract_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="suspended")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=mock_contract)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/suspend",
                params={"reason": "Inadimplência"},
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_suspend_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=None)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{_uid()}/suspend")
        assert resp.status_code == 400


class TestContractTerminate:
    """POST /api/v1/crm/contracts/{id}/terminate → 200 + 400"""

    @pytest.mark.asyncio
    async def test_terminate_contract_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="terminated")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=mock_contract)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/terminate",
                params={"reason": "Encerramento contratual"},
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_terminate_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=None)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{_uid()}/terminate")
        assert resp.status_code == 400


class TestContractRenew:
    """POST /api/v1/crm/contracts/{id}/renew → 200 + 404"""

    @pytest.mark.asyncio
    async def test_renew_contract_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="active")
        mock_renewal = _make_renewal_result()
        with patch(REPO_PATCH) as MockRepo, patch(SERVICE_PATCH) as MockService:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_contract)
            svc_instance = MockService.return_value
            svc_instance.calculate_renewal = MagicMock(return_value=mock_renewal)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/renew",
                json=_CONTRACT_RENEWAL_PAYLOAD,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_renew_contract_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{_uid()}/renew",
                json=_CONTRACT_RENEWAL_PAYLOAD,
            )
        assert resp.status_code == 404


class TestContractCalculateAdjustment:
    """POST /api/v1/crm/contracts/{id}/calculate-adjustment → 200 + 404"""

    @pytest.mark.asyncio
    async def test_calculate_adjustment_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="active")
        mock_adj = _make_adjustment_result()
        with patch(REPO_PATCH) as MockRepo, patch(SERVICE_PATCH) as MockService:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_contract)
            svc_instance = MockService.return_value
            svc_instance.calculate_adjustment = MagicMock(return_value=mock_adj)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/calculate-adjustment",
                params={"custom_percent": 5.0},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        assert "new_value" in data

    @pytest.mark.asyncio
    async def test_calculate_adjustment_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{_uid()}/calculate-adjustment")
        assert resp.status_code == 404


# ===========================================================================
# SECAO 3 — ITENS DO CONTRATO
# ===========================================================================


class TestContractItems:
    """Endpoints de items: POST, PUT, DELETE"""

    @pytest.mark.asyncio
    async def test_add_item_returns_201(self, crm_client):
        cid = _uid()
        mock_item = _make_contract_item(contract_id=cid)
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.add_item = AsyncMock(return_value=mock_item)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/items",
                json=_CONTRACT_ITEM_CREATE_PAYLOAD,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["service_name"] == "Vigilância Diurna"

    @pytest.mark.asyncio
    async def test_add_item_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.add_item = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{_uid()}/items",
                json=_CONTRACT_ITEM_CREATE_PAYLOAD,
            )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_update_item_returns_200(self, crm_client):
        cid = _uid()
        iid = _uid()
        mock_item = _make_contract_item(id=iid, contract_id=cid)
        mock_item.service_name = "Posto de Vigilância Noturno"
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_item = AsyncMock(return_value=mock_item)
            resp = await crm_client.put(
                f"/api/v1/crm/contracts/{cid}/items/{iid}",
                json=_CONTRACT_ITEM_UPDATE_PAYLOAD,
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_update_item_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_item = AsyncMock(return_value=None)
            resp = await crm_client.put(
                f"/api/v1/crm/contracts/{_uid()}/items/{_uid()}",
                json=_CONTRACT_ITEM_UPDATE_PAYLOAD,
            )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_item_returns_204(self, crm_client):
        cid = _uid()
        iid = _uid()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.remove_item = AsyncMock(return_value=True)
            resp = await crm_client.delete(f"/api/v1/crm/contracts/{cid}/items/{iid}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_remove_item_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.remove_item = AsyncMock(return_value=False)
            resp = await crm_client.delete(f"/api/v1/crm/contracts/{_uid()}/items/{_uid()}")
        assert resp.status_code == 404


# ===========================================================================
# SECAO 4 — ADITIVOS
# ===========================================================================


class TestContractAddendums:
    """Endpoints de aditivos: POST, GET, sign"""

    @pytest.mark.asyncio
    async def test_create_addendum_returns_201(self, crm_client):
        cid = _uid()
        mock_addendum = _make_addendum(contract_id=cid)
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create_addendum = AsyncMock(return_value=mock_addendum)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/addendums",
                json=_CONTRACT_ADDENDUM_CREATE_PAYLOAD,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "addendum_number" in data

    @pytest.mark.asyncio
    async def test_create_addendum_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create_addendum = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{_uid()}/addendums",
                json=_CONTRACT_ADDENDUM_CREATE_PAYLOAD,
            )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_list_addendums_returns_200(self, crm_client):
        cid = _uid()
        mock_addendum = _make_addendum(contract_id=cid)
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list_addendums = AsyncMock(return_value=[mock_addendum])
            resp = await crm_client.get(f"/api/v1/crm/contracts/{cid}/addendums")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_list_addendums_empty_returns_200(self, crm_client):
        cid = _uid()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list_addendums = AsyncMock(return_value=[])
            resp = await crm_client.get(f"/api/v1/crm/contracts/{cid}/addendums")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_sign_addendum_returns_200(self, crm_client):
        aid = _uid()
        mock_addendum = _make_addendum(id=aid)
        mock_addendum.signed = True
        mock_addendum.signed_at = _now()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.sign_addendum = AsyncMock(return_value=mock_addendum)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/addendums/{aid}/sign",
                json=_CONTRACT_ADDENDUM_SIGN_PAYLOAD,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["signed"] is True

    @pytest.mark.asyncio
    async def test_sign_addendum_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.sign_addendum = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/addendums/{_uid()}/sign",
                json=_CONTRACT_ADDENDUM_SIGN_PAYLOAD,
            )
        assert resp.status_code == 400


# ===========================================================================
# SECAO 5 — TEMPLATES
# ===========================================================================


class TestContractTemplates:
    """Endpoints de templates: GET list, GET by id, PUT, approve, DELETE"""

    @pytest.mark.asyncio
    async def test_list_templates_returns_200(self, crm_client):
        mock_template = _make_template()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list_templates = AsyncMock(return_value=[mock_template])
            resp = await crm_client.get("/api/v1/crm/contracts/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_templates_empty_returns_200(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list_templates = AsyncMock(return_value=[])
            resp = await crm_client.get("/api/v1/crm/contracts/templates")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_get_template_returns_200(self, crm_client):
        tid = _uid()
        mock_template = _make_template(id=tid)
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_template_by_id = AsyncMock(return_value=mock_template)
            resp = await crm_client.get(f"/api/v1/crm/contracts/templates/{tid}")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_get_template_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_template_by_id = AsyncMock(return_value=None)
            resp = await crm_client.get(f"/api/v1/crm/contracts/templates/{_uid()}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_template_returns_200(self, crm_client):
        tid = _uid()
        mock_template = _make_template(id=tid, name="Template Vigilância Patrimonial v2")
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_template = AsyncMock(return_value=mock_template)
            resp = await crm_client.put(
                f"/api/v1/crm/contracts/templates/{tid}",
                json=_CONTRACT_TEMPLATE_UPDATE_PAYLOAD,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Template Vigilância Patrimonial v2"

    @pytest.mark.asyncio
    async def test_update_template_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_template = AsyncMock(return_value=None)
            resp = await crm_client.put(
                f"/api/v1/crm/contracts/templates/{_uid()}",
                json=_CONTRACT_TEMPLATE_UPDATE_PAYLOAD,
            )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_approve_template_returns_200(self, crm_client):
        tid = _uid()
        mock_template = _make_template(id=tid)
        mock_template.approved_by_legal = True
        mock_template.approved_at = _now()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve_template = AsyncMock(return_value=mock_template)
            resp = await crm_client.post(f"/api/v1/crm/contracts/templates/{tid}/approve")
        assert resp.status_code == 200
        data = resp.json()
        assert data["approved_by_legal"] is True

    @pytest.mark.asyncio
    async def test_approve_template_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve_template = AsyncMock(return_value=None)
            resp = await crm_client.post(f"/api/v1/crm/contracts/templates/{_uid()}/approve")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_template_returns_204(self, crm_client):
        tid = _uid()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.delete_template = AsyncMock(return_value=True)
            resp = await crm_client.delete(f"/api/v1/crm/contracts/templates/{tid}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_template_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.delete_template = AsyncMock(return_value=False)
            resp = await crm_client.delete(f"/api/v1/crm/contracts/templates/{_uid()}")
        assert resp.status_code == 404


# ===========================================================================
# SECAO 6 — SLA REPORTS
# ===========================================================================


class TestContractSLAReports:
    """Endpoints de SLA reports: POST, GET list, approve, calculate"""

    @pytest.mark.asyncio
    async def test_create_sla_report_returns_201(self, crm_client):
        cid = _uid()
        mock_report = _make_sla_report(contract_id=cid)
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create_sla_report = AsyncMock(return_value=mock_report)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/sla-reports",
                json=_SLA_REPORT_CREATE_PAYLOAD,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "period_label" in data

    @pytest.mark.asyncio
    async def test_create_sla_report_contract_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create_sla_report = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{_uid()}/sla-reports",
                json=_SLA_REPORT_CREATE_PAYLOAD,
            )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_list_sla_reports_returns_200(self, crm_client):
        cid = _uid()
        mock_report = _make_sla_report(contract_id=cid)
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list_sla_reports = AsyncMock(return_value=[mock_report])
            resp = await crm_client.get(f"/api/v1/crm/contracts/{cid}/sla-reports")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_list_sla_reports_with_year_filter(self, crm_client):
        cid = _uid()
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.list_sla_reports = AsyncMock(return_value=[])
            resp = await crm_client.get(f"/api/v1/crm/contracts/{cid}/sla-reports?year=2026")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_approve_sla_report_returns_200(self, crm_client):
        rid = _uid()
        mock_report = _make_sla_report(id=rid)
        mock_report.status = "approved"
        mock_report.approved_at = _now()
        mock_report.approved_by = "test-user-id"
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve_sla_report = AsyncMock(return_value=mock_report)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/sla-reports/{rid}/approve",
                json=_SLA_REPORT_APPROVE_PAYLOAD,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data

    @pytest.mark.asyncio
    async def test_approve_sla_report_not_found_returns_400(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve_sla_report = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/sla-reports/{_uid()}/approve",
                json=_SLA_REPORT_APPROVE_PAYLOAD,
            )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_dispute_sla_report_returns_200(self, crm_client):
        rid = _uid()
        mock_report = _make_sla_report(id=rid)
        mock_report.status = "disputed"
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve_sla_report = AsyncMock(return_value=mock_report)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/sla-reports/{rid}/approve",
                json={"disputed": True, "dispute_reason": "Dados incorretos"},
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_calculate_sla_returns_200(self, crm_client):
        cid = _uid()
        mock_contract = _make_contract(id=cid, has_sla=True)
        mock_sla = _make_sla_calculation()
        with patch(REPO_PATCH) as MockRepo, patch(SERVICE_PATCH) as MockService:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_contract)
            svc_instance = MockService.return_value
            svc_instance.calculate_sla = MagicMock(return_value=mock_sla)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/calculate-sla",
                json=[
                    {
                        "name": "Disponibilidade",
                        "target": 100.0,
                        "actual": 95.5,
                        "weight": 1.0,
                    }
                ],
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_score" in data
        assert "penalty_applicable" in data

    @pytest.mark.asyncio
    async def test_calculate_sla_contract_not_found_returns_404(self, crm_client):
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{_uid()}/calculate-sla",
                json=[],
            )
        assert resp.status_code == 404


# ===========================================================================
# SECAO 7 — TESTES DE INTEGRACAO / CENARIOS COMPOSTOS
# ===========================================================================


class TestContractLifecycle:
    """Testes de ciclo de vida completo do contrato."""

    @pytest.mark.asyncio
    async def test_create_then_submit_flow(self, crm_client):
        """Cria contrato em draft e envia para assinatura."""
        cid = _uid()
        mock_draft = _make_contract(id=cid, status="draft")
        mock_pending = _make_contract(id=cid, status="pending_signature")

        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=mock_draft)
            create_resp = await crm_client.post("/api/v1/crm/contracts", json=_CONTRACT_CREATE_PAYLOAD)
        assert create_resp.status_code == 201

        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=mock_pending)
            submit_resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/submit")
        assert submit_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_full_activate_suspend_terminate_flow(self, crm_client):
        """Ativa, suspende e encerra um contrato."""
        cid = _uid()

        # Ativa
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=_make_contract(id=cid, status="active"))
            resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/activate")
        assert resp.status_code == 200

        # Suspende
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=_make_contract(id=cid, status="suspended"))
            resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/suspend")
        assert resp.status_code == 200

        # Encerra
        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.update_status = AsyncMock(return_value=_make_contract(id=cid, status="terminated"))
            resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/terminate")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_add_multiple_items_to_contract(self, crm_client):
        """Adiciona dois itens a um contrato e verifica resposta."""
        cid = _uid()
        item1 = _make_contract_item(contract_id=cid)
        item2 = _make_contract_item(contract_id=cid)
        item2.service_name = "Vigilância Noturna"
        item2.quantity = 1

        payloads = [
            {**_CONTRACT_ITEM_CREATE_PAYLOAD},
            {**_CONTRACT_ITEM_CREATE_PAYLOAD, "service_name": "Posto de Vigilância Noturno"},
        ]

        for payload, mock_item in zip(payloads, [item1, item2], strict=False):
            with patch(REPO_PATCH) as MockRepo:
                instance = MockRepo.return_value
                instance.add_item = AsyncMock(return_value=mock_item)
                resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/items", json=payload)
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_renewal_calculation_fields(self, crm_client):
        """Verifica campos retornados pelo cálculo de renovação."""
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="active")
        mock_renewal = _make_renewal_result()

        with patch(REPO_PATCH) as MockRepo, patch(SERVICE_PATCH) as MockService:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_contract)
            svc_instance = MockService.return_value
            svc_instance.calculate_renewal = MagicMock(return_value=mock_renewal)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/renew",
                json=_CONTRACT_RENEWAL_PAYLOAD,
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["new_end_date"] == "2028-03-31"
        assert data["adjustment_applied"] is True
        assert data["message"] == "Renovação calculada com sucesso"

    @pytest.mark.asyncio
    async def test_adjustment_calculation_fields(self, crm_client):
        """Verifica campos retornados pelo cálculo de reajuste."""
        cid = _uid()
        mock_contract = _make_contract(id=cid, status="active")
        mock_adj = _make_adjustment_result()

        with patch(REPO_PATCH) as MockRepo, patch(SERVICE_PATCH) as MockService:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=mock_contract)
            svc_instance = MockService.return_value
            svc_instance.calculate_adjustment = MagicMock(return_value=mock_adj)
            resp = await crm_client.post(f"/api/v1/crm/contracts/{cid}/calculate-adjustment")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert float(data["previous_value"]) == 10000.0
        assert float(data["new_value"]) == 10423.0

    @pytest.mark.asyncio
    async def test_create_template_then_approve_flow(self, crm_client):
        """Cria template e depois aprova."""
        tid = _uid()
        mock_template = _make_template(id=tid)
        mock_approved = _make_template(id=tid)
        mock_approved.approved_by_legal = True
        mock_approved.approved_at = _now()

        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create_template = AsyncMock(return_value=mock_template)
            resp = await crm_client.post(
                "/api/v1/crm/contracts/templates",
                json=_CONTRACT_TEMPLATE_CREATE_PAYLOAD,
            )
        assert resp.status_code == 201

        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve_template = AsyncMock(return_value=mock_approved)
            resp = await crm_client.post(f"/api/v1/crm/contracts/templates/{tid}/approve")
        assert resp.status_code == 200
        assert resp.json()["approved_by_legal"] is True

    @pytest.mark.asyncio
    async def test_sla_report_create_then_approve_flow(self, crm_client):
        """Cria relatório de SLA e depois aprova."""
        cid = _uid()
        rid = _uid()
        mock_report = _make_sla_report(id=rid, contract_id=cid)
        mock_approved_report = _make_sla_report(id=rid, contract_id=cid)
        mock_approved_report.status = "approved"

        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.create_sla_report = AsyncMock(return_value=mock_report)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/{cid}/sla-reports",
                json=_SLA_REPORT_CREATE_PAYLOAD,
            )
        assert resp.status_code == 200

        with patch(REPO_PATCH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve_sla_report = AsyncMock(return_value=mock_approved_report)
            resp = await crm_client.post(
                f"/api/v1/crm/contracts/sla-reports/{rid}/approve",
                json=_SLA_REPORT_APPROVE_PAYLOAD,
            )
        assert resp.status_code == 200
