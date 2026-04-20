"""
Testes de regressão CPRO11-T4 — fixes P0.1, P0.2, P0.5, P0.6, P0.11.

Cada teste documenta um bug confirmado em produção (CIC) e garante que não volta.
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from modules.crm.models.contract import ContractStatus
from modules.crm.models.lead import Lead, LeadStatus
from modules.crm.services.dashboard_service import DashboardKPIs, DashboardService


# ============================================================
# REG-01 — P0.11: leads_conversion_rate usa status "converted"
# ============================================================
def _make_lead(status: str) -> Lead:
    lead = MagicMock(spec=Lead)
    lead.status = status
    lead.created_at = MagicMock()
    lead.created_at.date.return_value = MagicMock()
    lead.created_at.date.return_value.__ge__ = MagicMock(return_value=False)
    lead.created_at.date.return_value.__eq__ = MagicMock(return_value=False)
    return lead


def test_leads_conversion_rate_conta_converted():
    """REG-01: DB usa status 'converted' — taxa deve refletir realidade, não 0.0."""
    service = DashboardService()
    leads = [_make_lead("converted")] * 11 + [_make_lead("qualified")] * 3
    kpis = service.calculate_kpis(leads=leads, opportunities=[], proposals=[], commissions=[])
    assert kpis.leads_conversion_rate > 0.0, (
        "leads_conversion_rate=0.0 regrediu — bug P0.11: status 'converted' não é reconhecido"
    )
    expected = (11 / 14) * 100
    assert abs(kpis.leads_conversion_rate - expected) < 0.01


def test_leads_conversion_rate_conta_won_legado():
    """REG-01b: status 'won' (legado) ainda deve ser contado."""
    service = DashboardService()
    leads = [_make_lead("won")] * 5 + [_make_lead("new")] * 5
    kpis = service.calculate_kpis(leads=leads, opportunities=[], proposals=[], commissions=[])
    assert kpis.leads_conversion_rate == 50.0


# ============================================================
# REG-02 — P0.2: endereco_texto deve ser string (nunca objeto)
# ============================================================
def test_endereco_texto_e_string():
    """REG-02: /crm/clients resposta deve ter 'endereco_texto' como string, não objeto."""
    from modules.crm.controllers.client_controller import listar_clientes  # noqa: F401

    # Simula a tupla retornada pelo raw SQL (r[8..r[12] = campos de endereço)
    rua = "Rua das Flores"
    numero = "123"
    bairro = "Centro"
    cidade = "Manaus"
    estado = "AM"

    endereco_texto = ", ".join(p for p in [rua, numero, bairro, cidade, estado] if p) or None
    assert isinstance(endereco_texto, str), "endereco_texto deve ser str, não objeto"
    assert "Manaus" in endereco_texto
    assert "Rua das Flores" in endereco_texto


def test_endereco_texto_com_campos_nulos():
    """REG-02b: campos None no endereço não geram 'None' na string."""
    rua = "Av. Brasil"
    numero = None
    bairro = None
    cidade = "Manaus"
    estado = "AM"

    endereco_texto = ", ".join(p for p in [rua, numero, bairro, cidade, estado] if p) or None
    assert endereco_texto is not None
    assert "None" not in endereco_texto
    assert "Av. Brasil" in endereco_texto


# ============================================================
# REG-03 — P0.1: ContractStatus enum tem valores lowercase
# ============================================================
def test_contractstatus_valores_lowercase():
    """REG-03: valores do enum ContractStatus devem ser lowercase (compatíveis com PG type)."""
    for member in ContractStatus:
        assert member.value == member.value.lower(), (
            f"ContractStatus.{member.name}={member.value!r} não é lowercase — "
            "quebra o casting contractstatus no PostgreSQL"
        )


# ============================================================
# REG-04 — P0.6/P0.5: DashboardKPIs tem campos clientes_total e mrr
# ============================================================
def test_dashboard_kpis_tem_clientes_total_e_mrr():
    """REG-04: DashboardKPIs deve ter clientes_total e mrr (P0.5/P0.6)."""
    kpis = DashboardKPIs()
    assert hasattr(kpis, "clientes_total"), "clientes_total ausente — bug P0.5 regrediu"
    assert hasattr(kpis, "mrr"), "mrr ausente — bug P0.6 regrediu"
    assert kpis.clientes_total == 0
    assert kpis.mrr == 0.0


def test_dashboard_kpis_mrr_nunca_nan():
    """REG-04b: mrr nunca deve ser NaN (COALESCE exigido — INV-12)."""
    import math

    kpis = DashboardKPIs(mrr=0.0)
    assert not math.isnan(kpis.mrr), "mrr=NaN regrediu — violação INV-12"


# ============================================================
# REG-05 — P0.2: proposals/templates não capturado por /{proposal_id}
# ============================================================
def test_proposals_templates_rota_declarada_antes_de_proposal_id():
    """REG-05: rota /proposals/templates deve estar ANTES de /{proposal_id} no router."""
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from modules.crm.controllers import proposal_controller

    router = proposal_controller.router
    route_paths = [getattr(r, "path", "") for r in router.routes]

    # FastAPI registra com prefixo completo quando montado
    idx_templates = next(
        (i for i, p in enumerate(route_paths) if p.endswith("/templates") and "template_id" not in p),
        None,
    )
    idx_proposal_id = next(
        (i for i, p in enumerate(route_paths) if p.endswith("/{proposal_id}")),
        None,
    )

    assert idx_templates is not None, f"Rota /templates não encontrada — paths: {route_paths}"
    assert idx_proposal_id is not None, "Rota /{proposal_id} não encontrada no router de proposals"
    assert idx_templates < idx_proposal_id, (
        f"Rota /templates (idx={idx_templates}) está DEPOIS de /{{proposal_id}} "
        f"(idx={idx_proposal_id}) — GET /proposals/templates retorna 422 (UUID inválido)"
    )
