"""
Testes E2E para o submodulo Commissions do CRM.

Cobre todos os endpoints do commission_controller.py com mocks de repositório
e serviço injetados no nível do controller.

Patcher: modules.crm.controllers.commission_controller.CommissionRepository
Service: modules.crm.controllers.commission_controller.CommissionService
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from modules.crm.models.commission import CommissionStatus, CommissionTrigger, CommissionType
from modules.crm.schemas.commission import CommissionStats, SellerCommissionStats

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime(2026, 3, 30, 12, 0, 0)


# ---------------------------------------------------------------------------
# Mock builders
# ---------------------------------------------------------------------------


def _make_commission_rule(**kwargs) -> MagicMock:
    """Cria mock de CommissionRule com todos os atributos obrigatórios."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.name = kwargs.get("name", "Regra Padrão")
    m.description = kwargs.get("description")
    m.commission_type = kwargs.get("commission_type", CommissionType.PERCENTAGE.value)
    m.base_value = kwargs.get("base_value", 5.0)
    m.min_value = kwargs.get("min_value")
    m.max_value = kwargs.get("max_value")
    m.progressive_scale = kwargs.get("progressive_scale")
    m.trigger = kwargs.get("trigger", CommissionTrigger.ON_FIRST_PAYMENT.value)
    m.trigger_delay_days = kwargs.get("trigger_delay_days", 0)
    m.applies_to_all = kwargs.get("applies_to_all", True)
    m.product_categories = kwargs.get("product_categories")
    m.service_types = kwargs.get("service_types")
    m.min_sale_value = kwargs.get("min_sale_value")
    m.max_sale_value = kwargs.get("max_sale_value")
    m.valid_from = kwargs.get("valid_from", date(2026, 1, 1))
    m.valid_until = kwargs.get("valid_until")
    m.priority = kwargs.get("priority", 0)
    m.is_valid = kwargs.get("is_valid", True)
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    m.created_by_id = kwargs.get("created_by_id", "test-user-id")
    return m


def _make_commission(**kwargs) -> MagicMock:
    """Cria mock de Commission com todos os atributos obrigatórios para CommissionResponse."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.reference_number = kwargs.get("reference_number", "COM-2026-00001")
    m.seller_id = kwargs.get("seller_id", _uid())
    m.proposal_id = kwargs.get("proposal_id")
    m.rule_id = kwargs.get("rule_id", _uid())
    m.rule = kwargs.get("rule")
    m.payments = kwargs.get("payments", [])

    # Valores da venda
    m.sale_value = kwargs.get("sale_value", 50000.0)
    m.sale_margin = kwargs.get("sale_margin", 0.0)

    # Cálculo
    m.commission_type = kwargs.get("commission_type", CommissionType.PERCENTAGE.value)
    m.commission_rate = kwargs.get("commission_rate", 5.0)
    m.base_commission = kwargs.get("base_commission", 2500.0)
    m.adjustments = kwargs.get("adjustments", 0.0)
    m.final_commission = kwargs.get("final_commission", 2500.0)

    # Status e datas
    m.status = kwargs.get("status", CommissionStatus.PENDING.value)
    m.trigger = kwargs.get("trigger", CommissionTrigger.ON_FIRST_PAYMENT.value)
    m.trigger_date = kwargs.get("trigger_date")
    m.due_date = kwargs.get("due_date")
    m.paid_date = kwargs.get("paid_date")

    # Período
    m.period_start = kwargs.get("period_start")
    m.period_end = kwargs.get("period_end")

    # Descrição
    m.description = kwargs.get("description")
    m.notes = kwargs.get("notes")

    # Propriedades calculadas
    m.is_pending = kwargs.get("is_pending", True)
    m.is_approved = kwargs.get("is_approved", False)
    m.is_paid = kwargs.get("is_paid", False)
    m.paid_amount = kwargs.get("paid_amount", 0.0)
    m.pending_amount = kwargs.get("pending_amount", 2500.0)
    m.is_overdue = kwargs.get("is_overdue", False)
    m.days_until_due = kwargs.get("days_until_due")

    # Controle
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    m.created_by_id = kwargs.get("created_by_id", "test-user-id")
    m.approved_by_id = kwargs.get("approved_by_id")
    m.approved_at = kwargs.get("approved_at")

    return m


def _make_commission_summary(**kwargs) -> MagicMock:
    """Cria mock de CommissionSummary com todos os atributos obrigatórios."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.seller_id = kwargs.get("seller_id", _uid())
    m.year = kwargs.get("year", 2026)
    m.month = kwargs.get("month", 3)
    m.total_sales = kwargs.get("total_sales", 150000.0)
    m.total_sales_count = kwargs.get("total_sales_count", 3)
    m.total_commissions = kwargs.get("total_commissions", 7500.0)
    m.total_paid = kwargs.get("total_paid", 2500.0)
    m.total_pending = kwargs.get("total_pending", 5000.0)
    m.sales_target = kwargs.get("sales_target")
    m.target_percentage = kwargs.get("target_percentage")
    m.bonus_earned = kwargs.get("bonus_earned", 0.0)
    m.is_target_achieved = kwargs.get("is_target_achieved", False)
    m.remaining_to_target = kwargs.get("remaining_to_target", 0.0)
    m.is_closed = kwargs.get("is_closed", False)
    m.closed_at = kwargs.get("closed_at")
    m.created_at = kwargs.get("created_at", _now())
    m.updated_at = kwargs.get("updated_at", _now())
    return m


def _make_seller_commission_rule(**kwargs) -> MagicMock:
    """Cria mock de SellerCommissionRule com todos os atributos obrigatórios."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.seller_id = kwargs.get("seller_id", _uid())
    m.rule_id = kwargs.get("rule_id", _uid())
    m.custom_base_value = kwargs.get("custom_base_value")
    m.valid_from = kwargs.get("valid_from", date(2026, 1, 1))
    m.valid_until = kwargs.get("valid_until")
    m.is_active = kwargs.get("is_active", True)
    m.created_at = kwargs.get("created_at", _now())
    return m


def _make_commission_payment(**kwargs) -> MagicMock:
    """Cria mock de CommissionPayment com todos os atributos obrigatórios."""
    m = MagicMock()
    m.id = kwargs.get("id", _uid())
    m.commission_id = kwargs.get("commission_id", _uid())
    m.amount = kwargs.get("amount", 2500.0)
    m.payment_method = kwargs.get("payment_method", "payroll")
    m.payment_date = kwargs.get("payment_date", date(2026, 3, 30))
    m.payment_reference = kwargs.get("payment_reference")
    m.bank_account = kwargs.get("bank_account")
    m.transaction_id = kwargs.get("transaction_id")
    m.is_confirmed = kwargs.get("is_confirmed", False)
    m.confirmed_at = kwargs.get("confirmed_at")
    m.confirmed_by_id = kwargs.get("confirmed_by_id")
    m.notes = kwargs.get("notes")
    m.created_at = kwargs.get("created_at", _now())
    m.created_by_id = kwargs.get("created_by_id", "test-user-id")
    return m


def _make_commission_stats() -> CommissionStats:
    """Cria instância real de CommissionStats."""
    return CommissionStats(
        total_commissions=10,
        pending_count=4,
        approved_count=3,
        paid_count=2,
        cancelled_count=1,
        total_value=25000.0,
        pending_value=10000.0,
        approved_value=7500.0,
        paid_value=5000.0,
        overdue_count=1,
        overdue_value=2500.0,
        avg_commission_value=2500.0,
        avg_days_to_payment=7.0,
        by_status={"pending": 4, "approved": 3, "paid": 2, "cancelled": 1},
        by_trigger={"on_first_payment": 7, "on_signature": 3},
        by_month={"2026-03": 25000.0},
    )


def _make_seller_stats(seller_id: str | None = None) -> SellerCommissionStats:
    """Cria instância real de SellerCommissionStats."""
    return SellerCommissionStats(
        seller_id=seller_id or _uid(),
        seller_name=None,
        total_sales=150000.0,
        total_commissions=7500.0,
        pending_commissions=5000.0,
        paid_commissions=2500.0,
        commission_rate_avg=5.0,
        sales_count=3,
        current_month_sales=50000.0,
        current_month_commissions=2500.0,
        target=None,
        target_percentage=None,
    )


# ---------------------------------------------------------------------------
# Fixture: AsyncClient autenticado
# ---------------------------------------------------------------------------

PATCHER = "modules.crm.controllers.commission_controller.CommissionRepository"
SERVICE_PATCHER = "modules.crm.controllers.commission_controller.CommissionService"


@pytest_asyncio.fixture
async def crm_client():
    """
    AsyncClient autenticado para testes E2E do CRM.

    Injeta override em get_current_active_user para evitar autenticação real.
    """
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


# ===========================================================================
# TESTES — Commission Rules
# ===========================================================================


class TestCommissionRulesCreate:
    """POST /api/v1/crm/commissions/rules → 201"""

    @pytest.mark.asyncio
    async def test_create_rule_returns_201(self, crm_client):
        """Criar regra com dados mínimos obrigatórios retorna 201."""
        rule = _make_commission_rule(name="Regra Percentual 5%")
        payload = {
            "name": "Regra Percentual 5%",
            "commission_type": "percentage",
            "base_value": 5.0,
            "trigger": "on_first_payment",
            "trigger_delay_days": 0,
        }
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.create_rule = AsyncMock(return_value=rule)
            resp = await crm_client.post("/api/v1/crm/commissions/rules", json=payload)

        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == rule.name
        assert data["commission_type"] == "percentage"

    @pytest.mark.asyncio
    async def test_create_rule_fixed_type(self, crm_client):
        """Criar regra do tipo 'fixed' com valor fixo retorna 201."""
        rule = _make_commission_rule(name="Comissão Fixa R$500", commission_type="fixed", base_value=500.0)
        payload = {
            "name": "Comissão Fixa R$500",
            "commission_type": "fixed",
            "base_value": 500.0,
            "trigger": "on_signature",
            "trigger_delay_days": 0,
        }
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.create_rule = AsyncMock(return_value=rule)
            resp = await crm_client.post("/api/v1/crm/commissions/rules", json=payload)

        assert resp.status_code == 201
        assert resp.json()["commission_type"] == "fixed"

    @pytest.mark.asyncio
    async def test_create_rule_passes_created_by_id(self, crm_client):
        """Verifica que created_by_id é passado para o repositório."""
        rule = _make_commission_rule()
        payload = {
            "name": "Regra teste",
            "commission_type": "percentage",
            "base_value": 3.0,
            "trigger": "on_first_payment",
            "trigger_delay_days": 0,
        }
        with patch(PATCHER) as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.create_rule = AsyncMock(return_value=rule)
            resp = await crm_client.post("/api/v1/crm/commissions/rules", json=payload)

        assert resp.status_code == 201
        mock_instance.create_rule.assert_awaited_once()
        call_kwargs = mock_instance.create_rule.call_args
        assert call_kwargs.kwargs.get("created_by_id") == "test-user-id"


class TestCommissionRulesList:
    """GET /api/v1/crm/commissions/rules → 200"""

    @pytest.mark.asyncio
    async def test_list_rules_returns_200(self, crm_client):
        """Listar regras retorna estrutura paginada correta."""
        rules = [_make_commission_rule(name=f"Regra {i}") for i in range(3)]
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list_rules = AsyncMock(return_value=(rules, 3))
            resp = await crm_client.get("/api/v1/crm/commissions/rules")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 20

    @pytest.mark.asyncio
    async def test_list_rules_empty_returns_200(self, crm_client):
        """Lista vazia retorna 200 com items=[]."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list_rules = AsyncMock(return_value=([], 0))
            resp = await crm_client.get("/api/v1/crm/commissions/rules")

        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["items"] == []

    @pytest.mark.asyncio
    async def test_list_rules_pagination_params(self, crm_client):
        """Parâmetros de paginação são repassados ao repositório."""
        rules = [_make_commission_rule()]
        with patch(PATCHER) as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.list_rules = AsyncMock(return_value=(rules, 10))
            resp = await crm_client.get("/api/v1/crm/commissions/rules?page=2&page_size=5")

        assert resp.status_code == 200
        mock_instance.list_rules.assert_awaited_once_with(active_only=True, skip=5, limit=5)


class TestCommissionRulesGetById:
    """GET /api/v1/crm/commissions/rules/{rule_id} → 200 / 404"""

    @pytest.mark.asyncio
    async def test_get_rule_by_id_returns_200(self, crm_client):
        """Buscar regra existente retorna 200 com dados corretos."""
        rule_id = _uid()
        rule = _make_commission_rule(id=rule_id, name="Regra Específica")
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.get_rule_by_id = AsyncMock(return_value=rule)
            resp = await crm_client.get(f"/api/v1/crm/commissions/rules/{rule_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == rule_id
        assert resp.json()["name"] == "Regra Específica"

    @pytest.mark.asyncio
    async def test_get_rule_by_id_not_found_returns_404(self, crm_client):
        """Buscar regra inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.get_rule_by_id = AsyncMock(return_value=None)
            resp = await crm_client.get(f"/api/v1/crm/commissions/rules/{_uid()}")

        assert resp.status_code == 404
        assert "não encontrada" in resp.json()["detail"]


class TestCommissionRulesUpdate:
    """PUT /api/v1/crm/commissions/rules/{rule_id} → 200 / 404"""

    @pytest.mark.asyncio
    async def test_update_rule_returns_200(self, crm_client):
        """Atualizar regra existente retorna 200."""
        rule_id = _uid()
        updated_rule = _make_commission_rule(id=rule_id, name="Regra Atualizada", base_value=7.0)
        payload = {"name": "Regra Atualizada", "base_value": 7.0}
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_rule = AsyncMock(return_value=updated_rule)
            resp = await crm_client.put(f"/api/v1/crm/commissions/rules/{rule_id}", json=payload)

        assert resp.status_code == 200
        assert resp.json()["name"] == "Regra Atualizada"

    @pytest.mark.asyncio
    async def test_update_rule_not_found_returns_404(self, crm_client):
        """Atualizar regra inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_rule = AsyncMock(return_value=None)
            resp = await crm_client.put(
                f"/api/v1/crm/commissions/rules/{_uid()}",
                json={"name": "Inexistente"},
            )

        assert resp.status_code == 404


class TestCommissionRulesDelete:
    """DELETE /api/v1/crm/commissions/rules/{rule_id} → 204 / 404"""

    @pytest.mark.asyncio
    async def test_delete_rule_returns_204(self, crm_client):
        """Deletar regra existente retorna 204."""
        rule_id = _uid()
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.delete_rule = AsyncMock(return_value=True)
            resp = await crm_client.delete(f"/api/v1/crm/commissions/rules/{rule_id}")

        assert resp.status_code == 204
        assert resp.content == b""

    @pytest.mark.asyncio
    async def test_delete_rule_not_found_returns_404(self, crm_client):
        """Deletar regra inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.delete_rule = AsyncMock(return_value=False)
            resp = await crm_client.delete(f"/api/v1/crm/commissions/rules/{_uid()}")

        assert resp.status_code == 404


# ===========================================================================
# TESTES — Commissions CRUD
# ===========================================================================


class TestCommissionCreate:
    """POST /api/v1/crm/commissions/ → 201"""

    @pytest.mark.asyncio
    async def test_create_commission_manual_returns_201(self, crm_client):
        """Criar comissão manualmente retorna 201."""
        commission = _make_commission()
        payload = {
            "seller_id": _uid(),
            "sale_value": 50000.0,
            "sale_margin": 0.0,
        }
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.create = AsyncMock(return_value=commission)
            resp = await crm_client.post("/api/v1/crm/commissions/", json=payload)

        assert resp.status_code == 201
        data = resp.json()
        assert data["reference_number"] == "COM-2026-00001"
        assert data["sale_value"] == 50000.0


class TestCommissionCalculate:
    """POST /api/v1/crm/commissions/calculate → 200"""

    @pytest.mark.asyncio
    async def test_calculate_commission_returns_200(self, crm_client):
        """Calcular comissão por oportunidade/proposta retorna 200."""
        seller_id = _uid()
        proposal_id = _uid()
        rule = _make_commission_rule()
        commission = _make_commission(seller_id=seller_id, proposal_id=proposal_id)
        payload = {
            "seller_id": seller_id,
            "proposal_id": proposal_id,
            "sale_value": 50000.0,
            "sale_margin": 0.0,
        }
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER) as MockService:
            mock_repo = MockRepo.return_value
            mock_repo.get_valid_rules = AsyncMock(return_value=[rule])
            mock_repo.create = AsyncMock(return_value=commission)
            mock_service = MockService.return_value
            mock_service.find_applicable_rule = MagicMock(return_value=rule)

            resp = await crm_client.post("/api/v1/crm/commissions/calculate", json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert data["seller_id"] == seller_id

    @pytest.mark.asyncio
    async def test_calculate_commission_no_rules_returns_400(self, crm_client):
        """Calcular comissão sem regras válidas retorna 400."""
        payload = {
            "seller_id": _uid(),
            "proposal_id": _uid(),
            "sale_value": 50000.0,
            "sale_margin": 0.0,
        }
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.get_valid_rules = AsyncMock(return_value=[])
            resp = await crm_client.post("/api/v1/crm/commissions/calculate", json=payload)

        assert resp.status_code == 400
        assert "regra" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_calculate_commission_no_applicable_rule_returns_400(self, crm_client):
        """Calcular comissão sem regra aplicável para o valor retorna 400."""
        rule = _make_commission_rule()
        payload = {
            "seller_id": _uid(),
            "proposal_id": _uid(),
            "sale_value": 1.0,
            "sale_margin": 0.0,
        }
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER) as MockService:
            MockRepo.return_value.get_valid_rules = AsyncMock(return_value=[rule])
            MockService.return_value.find_applicable_rule = MagicMock(return_value=None)
            resp = await crm_client.post("/api/v1/crm/commissions/calculate", json=payload)

        assert resp.status_code == 400
        assert "aplicável" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_calculate_commission_with_specific_rule_id(self, crm_client):
        """Calcular comissão com rule_id específico usa aquela regra."""
        seller_id = _uid()
        rule_id = _uid()
        rule = _make_commission_rule(id=rule_id)
        commission = _make_commission(seller_id=seller_id)
        payload = {
            "seller_id": seller_id,
            "proposal_id": _uid(),
            "sale_value": 50000.0,
            "sale_margin": 0.0,
            "rule_id": rule_id,
        }
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER):
            mock_repo = MockRepo.return_value
            mock_repo.get_valid_rules = AsyncMock(return_value=[rule])
            mock_repo.get_rule_by_id = AsyncMock(return_value=rule)
            mock_repo.create = AsyncMock(return_value=commission)
            resp = await crm_client.post("/api/v1/crm/commissions/calculate", json=payload)

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_calculate_commission_rule_id_not_found_returns_404(self, crm_client):
        """Calcular comissão com rule_id inexistente retorna 404."""
        rule = _make_commission_rule()
        payload = {
            "seller_id": _uid(),
            "proposal_id": _uid(),
            "sale_value": 50000.0,
            "sale_margin": 0.0,
            "rule_id": _uid(),
        }
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER):
            mock_repo = MockRepo.return_value
            mock_repo.get_valid_rules = AsyncMock(return_value=[rule])
            mock_repo.get_rule_by_id = AsyncMock(return_value=None)
            resp = await crm_client.post("/api/v1/crm/commissions/calculate", json=payload)

        assert resp.status_code == 404


class TestCommissionList:
    """GET /api/v1/crm/commissions → 200"""

    @pytest.mark.asyncio
    async def test_list_commissions_returns_200(self, crm_client):
        """Listar comissões retorna estrutura paginada correta."""
        commissions = [_make_commission() for _ in range(5)]
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list = AsyncMock(return_value=(commissions, 5))
            resp = await crm_client.get("/api/v1/crm/commissions")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5

    @pytest.mark.asyncio
    async def test_list_commissions_with_seller_filter(self, crm_client):
        """Filtro seller_id é repassado corretamente."""
        seller_id = _uid()
        commissions = [_make_commission(seller_id=seller_id)]
        with patch(PATCHER) as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.list = AsyncMock(return_value=(commissions, 1))
            resp = await crm_client.get(f"/api/v1/crm/commissions?seller_id={seller_id}")

        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    @pytest.mark.asyncio
    async def test_list_commissions_with_status_filter(self, crm_client):
        """Filtro de status é aceito e repassado."""
        commissions = [_make_commission(status=CommissionStatus.APPROVED.value)]
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list = AsyncMock(return_value=(commissions, 1))
            resp = await crm_client.get("/api/v1/crm/commissions?status=approved")

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_commissions_empty_returns_200(self, crm_client):
        """Lista vazia retorna 200."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list = AsyncMock(return_value=([], 0))
            resp = await crm_client.get("/api/v1/crm/commissions")

        assert resp.status_code == 200
        assert resp.json()["items"] == []


class TestCommissionStats:
    """GET /api/v1/crm/commissions/stats → 200"""

    @pytest.mark.asyncio
    async def test_get_commission_stats_returns_200(self, crm_client):
        """Stats gerais retorna 200 com estrutura correta."""
        stats = _make_commission_stats()
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER) as MockService:
            MockRepo.return_value.get_all_for_stats = AsyncMock(return_value=[])
            MockService.return_value.calculate_stats = MagicMock(return_value=stats)
            resp = await crm_client.get("/api/v1/crm/commissions/stats")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_commissions"] == 10
        assert data["pending_count"] == 4
        assert data["total_value"] == 25000.0
        assert "by_status" in data
        assert "by_trigger" in data
        assert "by_month" in data

    @pytest.mark.asyncio
    async def test_get_commission_stats_with_date_filters(self, crm_client):
        """Stats com filtros de data retorna 200."""
        stats = _make_commission_stats()
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER) as MockService:
            MockRepo.return_value.get_all_for_stats = AsyncMock(return_value=[])
            MockService.return_value.calculate_stats = MagicMock(return_value=stats)
            resp = await crm_client.get("/api/v1/crm/commissions/stats?date_from=2026-03-01&date_to=2026-03-31")

        assert resp.status_code == 200


class TestSellerCommissionStats:
    """GET /api/v1/crm/commissions/seller/{seller_id}/stats → 200"""

    @pytest.mark.asyncio
    async def test_get_seller_stats_returns_200(self, crm_client):
        """Stats de vendedor específico retorna 200."""
        seller_id = _uid()
        seller_stats = _make_seller_stats(seller_id=seller_id)
        commissions = []
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER) as MockService:
            MockRepo.return_value.list = AsyncMock(return_value=(commissions, 0))
            MockService.return_value.calculate_seller_stats = MagicMock(return_value=seller_stats)
            resp = await crm_client.get(f"/api/v1/crm/commissions/seller/{seller_id}/stats")

        assert resp.status_code == 200
        data = resp.json()
        assert data["seller_id"] == seller_id
        assert data["total_sales"] == 150000.0
        assert data["total_commissions"] == 7500.0

    @pytest.mark.asyncio
    async def test_get_seller_stats_with_target_param(self, crm_client):
        """Stats de vendedor com parâmetro target retorna 200."""
        seller_id = _uid()
        seller_stats = _make_seller_stats(seller_id=seller_id)
        seller_stats.target = 200000.0
        seller_stats.target_percentage = 75.0
        with patch(PATCHER) as MockRepo, patch(SERVICE_PATCHER) as MockService:
            MockRepo.return_value.list = AsyncMock(return_value=([], 0))
            MockService.return_value.calculate_seller_stats = MagicMock(return_value=seller_stats)
            resp = await crm_client.get(f"/api/v1/crm/commissions/seller/{seller_id}/stats?target=200000")

        assert resp.status_code == 200


class TestCommissionGetById:
    """GET /api/v1/crm/commissions/{commission_id} → 200 / 404"""

    @pytest.mark.asyncio
    async def test_get_commission_by_id_returns_200(self, crm_client):
        """Buscar comissão existente retorna 200 com detalhe."""
        commission_id = _uid()
        commission = _make_commission(id=commission_id)
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.get_by_id = AsyncMock(return_value=commission)
            resp = await crm_client.get(f"/api/v1/crm/commissions/{commission_id}")

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == commission_id
        assert data["reference_number"] == "COM-2026-00001"

    @pytest.mark.asyncio
    async def test_get_commission_by_id_not_found_returns_404(self, crm_client):
        """Buscar comissão inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.get_by_id = AsyncMock(return_value=None)
            resp = await crm_client.get(f"/api/v1/crm/commissions/{_uid()}")

        assert resp.status_code == 404
        assert "não encontrada" in resp.json()["detail"]


class TestCommissionUpdate:
    """PUT /api/v1/crm/commissions/{commission_id} → 200 / 404"""

    @pytest.mark.asyncio
    async def test_update_commission_returns_200(self, crm_client):
        """Atualizar comissão existente retorna 200."""
        commission_id = _uid()
        commission = _make_commission(id=commission_id, notes="Observação atualizada")
        payload = {"notes": "Observação atualizada"}
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update = AsyncMock(return_value=commission)
            resp = await crm_client.put(f"/api/v1/crm/commissions/{commission_id}", json=payload)

        assert resp.status_code == 200
        assert resp.json()["notes"] == "Observação atualizada"

    @pytest.mark.asyncio
    async def test_update_commission_not_found_returns_404(self, crm_client):
        """Atualizar comissão inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update = AsyncMock(return_value=None)
            resp = await crm_client.put(
                f"/api/v1/crm/commissions/{_uid()}",
                json={"notes": "x"},
            )

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_commission_adjustments(self, crm_client):
        """Atualizar ajuste de comissão retorna 200 com valor atualizado."""
        commission_id = _uid()
        commission = _make_commission(id=commission_id, adjustments=200.0, final_commission=2700.0)
        payload = {"adjustments": 200.0, "notes": "Ajuste aprovado pelo gerente"}
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update = AsyncMock(return_value=commission)
            resp = await crm_client.put(f"/api/v1/crm/commissions/{commission_id}", json=payload)

        assert resp.status_code == 200
        assert resp.json()["adjustments"] == 200.0


class TestCommissionStatusUpdate:
    """PATCH /api/v1/crm/commissions/{commission_id}/status → 200 / 404"""

    @pytest.mark.asyncio
    async def test_update_status_to_approved_returns_200(self, crm_client):
        """Atualizar status para 'approved' retorna 200."""
        commission_id = _uid()
        commission = _make_commission(
            id=commission_id,
            status=CommissionStatus.APPROVED.value,
            is_approved=True,
            is_pending=False,
        )
        payload = {"status": "approved"}
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_status = AsyncMock(return_value=commission)
            resp = await crm_client.patch(
                f"/api/v1/crm/commissions/{commission_id}/status",
                json=payload,
            )

        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    @pytest.mark.asyncio
    async def test_update_status_to_cancelled_returns_200(self, crm_client):
        """Atualizar status para 'cancelled' retorna 200."""
        commission_id = _uid()
        commission = _make_commission(id=commission_id, status=CommissionStatus.CANCELLED.value)
        payload = {"status": "cancelled", "notes": "Motivo do cancelamento"}
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_status = AsyncMock(return_value=commission)
            resp = await crm_client.patch(
                f"/api/v1/crm/commissions/{commission_id}/status",
                json=payload,
            )

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_update_status_not_found_returns_404(self, crm_client):
        """Atualizar status de comissão inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_status = AsyncMock(return_value=None)
            resp = await crm_client.patch(
                f"/api/v1/crm/commissions/{_uid()}/status",
                json={"status": "approved"},
            )

        assert resp.status_code == 404


class TestCommissionApprove:
    """POST /api/v1/crm/commissions/{commission_id}/approve → 200 / 404"""

    @pytest.mark.asyncio
    async def test_approve_commission_returns_200(self, crm_client):
        """Aprovar comissão retorna 200 com status aprovado."""
        commission_id = _uid()
        commission = _make_commission(
            id=commission_id,
            status=CommissionStatus.APPROVED.value,
            is_approved=True,
            is_pending=False,
            approved_by_id="test-user-id",
        )
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_status = AsyncMock(return_value=commission)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/{commission_id}/approve",
                json={},
            )

        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    @pytest.mark.asyncio
    async def test_approve_commission_with_notes(self, crm_client):
        """Aprovar comissão com notas retorna 200."""
        commission_id = _uid()
        commission = _make_commission(id=commission_id, status=CommissionStatus.APPROVED.value)
        with patch(PATCHER) as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.update_status = AsyncMock(return_value=commission)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/{commission_id}/approve",
                json={"notes": "Aprovado pelo diretor comercial"},
            )

        assert resp.status_code == 200
        # Verifica que update_status foi chamado com status APPROVED e approved_by_id
        call_kwargs = mock_instance.update_status.call_args.kwargs
        assert call_kwargs["status"] == CommissionStatus.APPROVED
        assert call_kwargs["approved_by_id"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_approve_commission_not_found_returns_404(self, crm_client):
        """Aprovar comissão inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_status = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/{_uid()}/approve",
                json={},
            )

        assert resp.status_code == 404


class TestCommissionDelete:
    """DELETE /api/v1/crm/commissions/{commission_id} → 204 / 404"""

    @pytest.mark.asyncio
    async def test_delete_commission_returns_204(self, crm_client):
        """Deletar comissão existente retorna 204."""
        commission_id = _uid()
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.delete = AsyncMock(return_value=True)
            resp = await crm_client.delete(f"/api/v1/crm/commissions/{commission_id}")

        assert resp.status_code == 204
        assert resp.content == b""

    @pytest.mark.asyncio
    async def test_delete_commission_not_found_returns_404(self, crm_client):
        """Deletar comissão inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.delete = AsyncMock(return_value=False)
            resp = await crm_client.delete(f"/api/v1/crm/commissions/{_uid()}")

        assert resp.status_code == 404


# ===========================================================================
# TESTES — Payments
# ===========================================================================


class TestCommissionPayments:
    """POST /api/v1/crm/commissions/{commission_id}/payments → 201 / 400"""

    @pytest.mark.asyncio
    async def test_create_payment_returns_201(self, crm_client):
        """Registrar pagamento de comissão retorna 201."""
        commission_id = _uid()
        payment = _make_commission_payment(commission_id=commission_id)
        payload = {
            "commission_id": commission_id,
            "amount": 2500.0,
            "payment_method": "payroll",
            "payment_date": "2026-03-30",
        }
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.create_payment = AsyncMock(return_value=payment)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/{commission_id}/payments",
                json=payload,
            )

        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"] == 2500.0
        assert data["payment_method"] == "payroll"

    @pytest.mark.asyncio
    async def test_create_payment_mismatched_ids_returns_400(self, crm_client):
        """ID no path diferente do body retorna 400."""
        commission_id_path = _uid()
        commission_id_body = _uid()  # diferente do path
        payload = {
            "commission_id": commission_id_body,
            "amount": 2500.0,
            "payment_method": "payroll",
            "payment_date": "2026-03-30",
        }
        with patch(PATCHER):
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/{commission_id_path}/payments",
                json=payload,
            )

        assert resp.status_code == 400
        assert "não correspondem" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_payment_commission_not_found_returns_400(self, crm_client):
        """Comissão não encontrada ao registrar pagamento retorna 400."""
        commission_id = _uid()
        payload = {
            "commission_id": commission_id,
            "amount": 2500.0,
            "payment_method": "pix",
            "payment_date": "2026-03-30",
        }
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.create_payment = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/{commission_id}/payments",
                json=payload,
            )

        assert resp.status_code == 400


class TestCommissionPaymentConfirm:
    """POST /api/v1/crm/commissions/payments/{payment_id}/confirm → 200 / 404"""

    @pytest.mark.asyncio
    async def test_confirm_payment_returns_200(self, crm_client):
        """Confirmar pagamento retorna 200."""
        payment_id = _uid()
        payment = _make_commission_payment(id=payment_id, is_confirmed=True)
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.confirm_payment = AsyncMock(return_value=payment)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/payments/{payment_id}/confirm",
                json={},
            )

        assert resp.status_code == 200
        assert resp.json()["is_confirmed"] is True

    @pytest.mark.asyncio
    async def test_confirm_payment_not_found_returns_404(self, crm_client):
        """Confirmar pagamento inexistente retorna 404."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.confirm_payment = AsyncMock(return_value=None)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/payments/{_uid()}/confirm",
                json={},
            )

        assert resp.status_code == 404


# ===========================================================================
# TESTES — Rules Assign
# ===========================================================================


class TestCommissionRulesAssign:
    """POST /api/v1/crm/commissions/rules/assign → 201"""

    @pytest.mark.asyncio
    async def test_assign_rule_to_seller_returns_201(self, crm_client):
        """Associar regra a vendedor retorna 201."""
        seller_id = _uid()
        rule_id = _uid()
        seller_rule = _make_seller_commission_rule(seller_id=seller_id, rule_id=rule_id)
        payload = {
            "seller_id": seller_id,
            "rule_id": rule_id,
            "valid_from": "2026-01-01",
        }
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.assign_rule_to_seller = AsyncMock(return_value=seller_rule)
            resp = await crm_client.post("/api/v1/crm/commissions/rules/assign", json=payload)

        assert resp.status_code == 201
        data = resp.json()
        assert data["seller_id"] == seller_id
        assert data["rule_id"] == rule_id


# ===========================================================================
# TESTES — Commission Summaries
# ===========================================================================


class TestCommissionSummariesList:
    """GET /api/v1/crm/commissions/summaries → 200"""

    @pytest.mark.asyncio
    async def test_list_summaries_returns_200(self, crm_client):
        """Listar resumos mensais retorna lista correta."""
        seller_id = _uid()
        summaries = [_make_commission_summary(seller_id=seller_id) for _ in range(2)]
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list_summaries = AsyncMock(return_value=summaries)
            resp = await crm_client.get("/api/v1/crm/commissions/summaries")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_summaries_with_filters(self, crm_client):
        """Listar resumos com filtros year/month retorna 200."""
        summaries = [_make_commission_summary(year=2026, month=3)]
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list_summaries = AsyncMock(return_value=summaries)
            resp = await crm_client.get("/api/v1/crm/commissions/summaries?year=2026&month=3")

        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.asyncio
    async def test_list_summaries_empty_returns_200(self, crm_client):
        """Lista vazia retorna 200 com lista vazia."""
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.list_summaries = AsyncMock(return_value=[])
            resp = await crm_client.get("/api/v1/crm/commissions/summaries")

        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_summaries_with_seller_id_filter(self, crm_client):
        """Listar resumos filtrando por seller_id retorna 200."""
        seller_id = _uid()
        summary = _make_commission_summary(seller_id=seller_id)
        with patch(PATCHER) as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.list_summaries = AsyncMock(return_value=[summary])
            resp = await crm_client.get(f"/api/v1/crm/commissions/summaries?seller_id={seller_id}")

        assert resp.status_code == 200
        assert resp.json()[0]["seller_id"] == seller_id


class TestCommissionSummaryGetBySellerPeriod:
    """GET /api/v1/crm/commissions/summaries/{seller_id}/{year}/{month} → 200"""

    @pytest.mark.asyncio
    async def test_get_summary_returns_200(self, crm_client):
        """Buscar ou criar resumo mensal de vendedor retorna 200."""
        seller_id = _uid()
        summary = _make_commission_summary(seller_id=seller_id, year=2026, month=3)
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_summary = AsyncMock(return_value=summary)
            resp = await crm_client.get(f"/api/v1/crm/commissions/summaries/{seller_id}/2026/3")

        assert resp.status_code == 200
        data = resp.json()
        assert data["seller_id"] == seller_id
        assert data["year"] == 2026
        assert data["month"] == 3
        assert data["total_commissions"] == 7500.0

    @pytest.mark.asyncio
    async def test_get_summary_structure_complete(self, crm_client):
        """Estrutura do resumo contém todos os campos esperados."""
        seller_id = _uid()
        summary = _make_commission_summary(
            seller_id=seller_id,
            total_sales=150000.0,
            total_paid=2500.0,
            total_pending=5000.0,
        )
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.update_summary = AsyncMock(return_value=summary)
            resp = await crm_client.get(f"/api/v1/crm/commissions/summaries/{seller_id}/2026/3")

        assert resp.status_code == 200
        data = resp.json()
        assert "total_sales" in data
        assert "total_paid" in data
        assert "total_pending" in data
        assert "is_closed" in data
        assert data["is_closed"] is False


class TestCommissionSummaryClose:
    """POST /api/v1/crm/commissions/summaries/{seller_id}/{year}/{month}/close → 200 / 404"""

    @pytest.mark.asyncio
    async def test_close_summary_returns_200(self, crm_client):
        """Fechar resumo mensal retorna 200 com is_closed=True."""
        seller_id = _uid()
        summary = _make_commission_summary(seller_id=seller_id, is_closed=True)
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.close_summary = AsyncMock(return_value=summary)
            resp = await crm_client.post(f"/api/v1/crm/commissions/summaries/{seller_id}/2026/3/close")

        assert resp.status_code == 200
        assert resp.json()["is_closed"] is True

    @pytest.mark.asyncio
    async def test_close_summary_not_found_returns_404(self, crm_client):
        """Fechar resumo inexistente retorna 404."""
        seller_id = _uid()
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.close_summary = AsyncMock(return_value=None)
            resp = await crm_client.post(f"/api/v1/crm/commissions/summaries/{seller_id}/2026/3/close")

        assert resp.status_code == 404
        assert "não encontrado" in resp.json()["detail"]


# ===========================================================================
# TESTES — Casos de borda e validações
# ===========================================================================


class TestCommissionEdgeCases:
    """Casos de borda e validações de entrada."""

    @pytest.mark.asyncio
    async def test_create_commission_invalid_sale_value_returns_422(self, crm_client):
        """Criar comissão com sale_value <= 0 retorna 422."""
        payload = {
            "seller_id": _uid(),
            "sale_value": -100.0,  # inválido: deve ser > 0
        }
        with patch(PATCHER):
            resp = await crm_client.post("/api/v1/crm/commissions/", json=payload)

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_rule_missing_name_returns_422(self, crm_client):
        """Criar regra sem nome obrigatório retorna 422."""
        payload = {
            "commission_type": "percentage",
            "base_value": 5.0,
            "trigger": "on_first_payment",
            "trigger_delay_days": 0,
            # 'name' ausente
        }
        with patch(PATCHER):
            resp = await crm_client.post("/api/v1/crm/commissions/rules", json=payload)

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_list_commissions_page_pagination(self, crm_client):
        """Paginação com page=2 e page_size=10 retorna skip correto."""
        commissions = [_make_commission()]
        with patch(PATCHER) as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.list = AsyncMock(return_value=(commissions, 20))
            resp = await crm_client.get("/api/v1/crm/commissions?page=2&page_size=10")

        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total_pages"] == 2

    @pytest.mark.asyncio
    async def test_update_commission_status_invalid_value_returns_422(self, crm_client):
        """Status inválido na atualização retorna 422."""
        with patch(PATCHER):
            resp = await crm_client.patch(
                f"/api/v1/crm/commissions/{_uid()}/status",
                json={"status": "invalid_status_value"},
            )

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_without_required_fields_returns_422(self, crm_client):
        """Calcular comissão sem seller_id retorna 422."""
        payload = {
            # seller_id ausente
            "proposal_id": _uid(),
            "sale_value": 50000.0,
        }
        with patch(PATCHER):
            resp = await crm_client.post("/api/v1/crm/commissions/calculate", json=payload)

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_commission_response_contains_computed_fields(self, crm_client):
        """Resposta de comissão contém campos computados (is_pending, is_approved, etc)."""
        commission_id = _uid()
        commission = _make_commission(
            id=commission_id,
            is_pending=True,
            is_approved=False,
            is_paid=False,
            is_overdue=False,
            paid_amount=0.0,
            pending_amount=2500.0,
        )
        with patch(PATCHER) as MockRepo:
            MockRepo.return_value.get_by_id = AsyncMock(return_value=commission)
            resp = await crm_client.get(f"/api/v1/crm/commissions/{commission_id}")

        assert resp.status_code == 200
        data = resp.json()
        assert "is_pending" in data
        assert "is_approved" in data
        assert "is_paid" in data
        assert "is_overdue" in data
        assert "paid_amount" in data
        assert "pending_amount" in data
        assert data["is_pending"] is True
        assert data["paid_amount"] == 0.0

    @pytest.mark.asyncio
    async def test_commission_approve_sets_approved_by_id(self, crm_client):
        """Aprovação define approved_by_id como o usuário autenticado."""
        commission_id = _uid()
        commission = _make_commission(
            id=commission_id,
            status=CommissionStatus.APPROVED.value,
            approved_by_id="test-user-id",
        )
        with patch(PATCHER) as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.update_status = AsyncMock(return_value=commission)
            resp = await crm_client.post(
                f"/api/v1/crm/commissions/{commission_id}/approve",
                json={},
            )

        assert resp.status_code == 200
        call_kwargs = mock_instance.update_status.call_args.kwargs
        assert call_kwargs["approved_by_id"] == "test-user-id"
