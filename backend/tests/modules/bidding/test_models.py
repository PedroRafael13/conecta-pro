"""
Tests for bidding model creation and basic validation.

These tests verify model instantiation and field defaults without
requiring a live database — they test the Python/SQLAlchemy layer only.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

# ══════════════════════════════════════════════════════════════
# Helper: mock Base to avoid needing real DB metadata
# ══════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def _patch_base():
    """
    Patches core.models.Base so that model classes can be imported
    without requiring a real database engine or metadata.
    We only need to verify field defaults and properties.
    """
    # No-op: models use declarative_base which works without connection
    yield


# ══════════════════════════════════════════════════════════════
# 1. Tender Model
# ══════════════════════════════════════════════════════════════


class TestTenderModel:
    """Tests for Tender model — edital de licitacao."""

    def test_tender_creation(self):
        """Verifies Tender model can be instantiated with required fields."""
        from modules.bidding.models.tender import BiddingModality, Tender, TenderStatus

        tender = Tender()
        tender.id = uuid.uuid4()
        tender.numero = "PE-001"
        tender.ano = 2026
        tender.objeto = "Contratacao de servicos de vigilancia patrimonial para a UFAM"
        tender.modalidade = BiddingModality.PREGAO_ELETRONICO.value
        tender.status = TenderStatus.PUBLISHED.value
        tender.orgao_nome = "UFAM"
        tender.orgao_cnpj = "04.378.626/0001-97"
        tender.uf = "AM"

        assert tender.numero == "PE-001"
        assert tender.ano == 2026
        assert tender.status == "published"
        assert tender.modalidade == "pregao_eletronico"

    def test_tender_status_enum(self):
        """Verifies TenderStatus enum has all expected statuses."""
        from modules.bidding.models.tender import TenderStatus

        expected = {
            "draft",
            "published",
            "open",
            "suspended",
            "canceled",
            "under_analysis",
            "adjudicated",
            "homologated",
            "deserted",
            "failed",
            "completed",
        }
        actual = {s.value for s in TenderStatus}
        assert actual == expected

    def test_bidding_modality_enum(self):
        """Verifies BiddingModality enum includes key modalities."""
        from modules.bidding.models.tender import BiddingModality

        assert BiddingModality.PREGAO_ELETRONICO.value == "pregao_eletronico"
        assert BiddingModality.CONCORRENCIA.value == "concorrencia"
        assert BiddingModality.DISPENSA.value == "dispensa"


# ══════════════════════════════════════════════════════════════
# 2. Proposal Model
# ══════════════════════════════════════════════════════════════


class TestProposalModel:
    """Tests for BiddingProposal model — proposta de licitacao."""

    def test_proposal_creation_with_tender(self):
        """Verifies BiddingProposal can be linked to a Tender via tender_id."""
        from modules.bidding.models.proposal import BiddingProposal, ProposalStatus

        tender_id = uuid.uuid4()

        proposal = BiddingProposal()
        proposal.id = uuid.uuid4()
        proposal.tender_id = tender_id
        proposal.numero = "PROP-001"
        proposal.versao = 1
        proposal.valor_total = Decimal("1500000.00")
        proposal.status = ProposalStatus.DRAFT.value

        assert proposal.tender_id == tender_id
        assert proposal.numero == "PROP-001"
        assert proposal.valor_total == Decimal("1500000.00")
        assert proposal.status == "draft"

    def test_proposal_status_enum(self):
        """Verifies ProposalStatus has all expected statuses."""
        from modules.bidding.models.proposal import ProposalStatus

        expected = {
            "draft",
            "ready",
            "submitted",
            "under_analysis",
            "classified",
            "disqualified",
            "winner",
            "second_place",
            "negotiating",
            "canceled",
        }
        actual = {s.value for s in ProposalStatus}
        assert actual == expected


# ══════════════════════════════════════════════════════════════
# 3. PublicContract Model
# ══════════════════════════════════════════════════════════════


class TestPublicContractModel:
    """Tests for PublicContract model — contrato publico."""

    def test_public_contract_creation(self):
        """Verifies PublicContract can be instantiated with all key fields."""
        from modules.bidding.models.public_contract import ContractStatus, PublicContract

        contract = PublicContract()
        contract.id = uuid.uuid4()
        contract.numero_contrato = "CT-001"
        contract.ano_contrato = 2026
        contract.objeto = "Vigilancia patrimonial"
        contract.orgao_cnpj = "04.378.626/0001-97"
        contract.orgao_nome = "UFAM"
        contract.orgao_uf = "AM"
        contract.valor_contrato = Decimal("1500000.00")
        contract.status = ContractStatus.ACTIVE.value

        assert contract.numero_contrato == "CT-001"
        assert contract.valor_contrato == Decimal("1500000.00")
        assert contract.status == "active"
        assert contract.orgao_uf == "AM"

    def test_contract_status_enum(self):
        """Verifies ContractStatus has all expected statuses."""
        from modules.bidding.models.public_contract import ContractStatus

        expected = {
            "draft",
            "pending_signature",
            "active",
            "suspended",
            "terminated",
            "completed",
            "expired",
        }
        actual = {s.value for s in ContractStatus}
        assert actual == expected

    def test_guarantee_type_enum(self):
        """Verifies GuaranteeType has all expected types."""
        from modules.bidding.models.public_contract import GuaranteeType

        assert GuaranteeType.SEGURO_GARANTIA.value == "seguro_garantia"
        assert GuaranteeType.FIANCA_BANCARIA.value == "fianca_bancaria"


# ══════════════════════════════════════════════════════════════
# 4. Measurement Model
# ══════════════════════════════════════════════════════════════


class TestMeasurementModel:
    """Tests for Measurement model — medicao de contrato."""

    def test_measurement_creation(self):
        """Verifies Measurement can be instantiated with required fields."""
        from modules.bidding.models.measurement import Measurement, MeasurementStatus, MeasurementType

        contract_id = uuid.uuid4()

        measurement = Measurement()
        measurement.id = uuid.uuid4()
        measurement.contrato_id = contract_id
        measurement.numero_medicao = 1
        measurement.competencia = "2026-03"
        measurement.tipo = MeasurementType.MENSAL.value
        measurement.periodo_inicio = date(2026, 3, 1)
        measurement.periodo_fim = date(2026, 3, 31)
        measurement.valor_bruto = Decimal("125000.00")
        measurement.valor_liquido = Decimal("120000.00")
        measurement.status = MeasurementStatus.DRAFT.value

        assert measurement.contrato_id == contract_id
        assert measurement.numero_medicao == 1
        assert measurement.competencia == "2026-03"
        assert measurement.valor_bruto == Decimal("125000.00")
        assert measurement.tipo == "mensal"

    def test_measurement_status_enum(self):
        """Verifies MeasurementStatus has all expected statuses."""
        from modules.bidding.models.measurement import MeasurementStatus

        expected = {
            "draft",
            "submitted",
            "under_review",
            "approved",
            "rejected",
            "partially_approved",
            "paid",
            "canceled",
        }
        actual = {s.value for s in MeasurementStatus}
        assert actual == expected

    def test_measurement_type_enum(self):
        """Verifies MeasurementType has all expected types."""
        from modules.bidding.models.measurement import MeasurementType

        assert MeasurementType.MENSAL.value == "mensal"
        assert MeasurementType.FINAL.value == "final"
        assert MeasurementType.REAJUSTE.value == "reajuste"


# ══════════════════════════════════════════════════════════════
# 5. Certificate Model
# ══════════════════════════════════════════════════════════════


class TestCertificateModel:
    """Tests for Certificate model — certidao para licitacao."""

    def test_certificate_creation(self):
        """Verifies Certificate model enums are correctly defined."""
        from modules.bidding.models.certificate import CertificateStatus, CertificateType

        assert CertificateType.CND_FEDERAL.value == "cnd_federal"
        assert CertificateType.CRF_FGTS.value == "crf_fgts"
        assert CertificateType.CND_TRABALHISTA.value == "cnd_trabalhista"

        assert CertificateStatus.VALID.value == "valid"
        assert CertificateStatus.EXPIRED.value == "expired"
        assert CertificateStatus.EXPIRING.value == "expiring"

    def test_certificate_source_enum(self):
        """Verifies CertificateSource has all expected sources."""
        from modules.bidding.models.certificate import CertificateSource

        assert CertificateSource.MANUAL.value == "manual"
        assert CertificateSource.API_RECEITA.value == "api_receita"
        assert CertificateSource.WEB_SCRAPING.value == "web_scraping"


# ══════════════════════════════════════════════════════════════
# 6. Opportunity Model
# ══════════════════════════════════════════════════════════════


class TestOpportunityModel:
    """Tests for BiddingOpportunity model — oportunidade de licitacao."""

    def test_opportunity_creation(self):
        """Verifies BiddingOpportunity can be instantiated with basic fields."""
        from modules.bidding.models.opportunity import BiddingOpportunity

        opp = BiddingOpportunity()
        opp.id = uuid.uuid4()
        opp.portal = "pncp"
        opp.portal_id = "PNCP-2026-001"
        opp.objeto = "Contratacao de vigilancia patrimonial armada e desarmada"
        opp.valor_estimado = Decimal("500000.00")
        opp.modalidade = "pregao_eletronico"
        opp.orgao_nome = "UFAM"
        opp.orgao_cnpj = "04.378.626/0001-97"
        opp.uf = "AM"
        opp.status = "nova"
        opp.relevancia_score = 85.0

        assert opp.portal == "pncp"
        assert opp.objeto == "Contratacao de vigilancia patrimonial armada e desarmada"
        assert opp.valor_estimado == Decimal("500000.00")
        assert opp.relevancia_score == 85.0
        assert opp.status == "nova"

    def test_opportunity_repr(self):
        """Verifies BiddingOpportunity __repr__ includes portal and status."""
        from modules.bidding.models.opportunity import BiddingOpportunity

        opp = BiddingOpportunity()
        opp.portal = "comprasnet"
        opp.portal_id = "CN-001"
        opp.status = "analisada"
        opp.objeto = "Teste"  # Required field

        repr_str = repr(opp)
        assert "comprasnet" in repr_str
        assert "analisada" in repr_str
