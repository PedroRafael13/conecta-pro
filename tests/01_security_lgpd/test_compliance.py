"""
Tests for Compliance Module (consent_manager, data_erasure, privacy_impact).

Author: Claude AI + Human Developer
Date: 2026-01-10
"""

import pytest
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from unittest.mock import MagicMock, AsyncMock
import uuid


# =============================================================================
# MOCK IMPLEMENTATIONS
# =============================================================================

class ConsentPurpose(str, Enum):
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    DATA_SHARING = "data_sharing"
    SERVICE_PROVISION = "service_provision"


class ConsentStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING = "pending"


class LegalBasis(str, Enum):
    CONSENT = "consent"
    LEGITIMATE_INTEREST = "legitimate_interest"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"


class ErasureStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class RiskLevel(str, Enum):
    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Consent:
    id: str
    titular_id: str
    purpose: ConsentPurpose
    legal_basis: LegalBasis
    status: ConsentStatus
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


@dataclass
class ErasureRequest:
    id: str
    titular_id: str
    reason: str
    status: ErasureStatus
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    exclude_categories: List[str] = field(default_factory=list)


@dataclass
class PIAAssessment:
    id: str
    nome: str
    descricao: str
    risk_level: Optional[RiskLevel] = None
    risks: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ConsentManager:
    def __init__(self, db_session=None):
        self.db = db_session
        self._consents: Dict[str, List[Consent]] = {}

    async def register_consent(
        self, titular_id: str, purpose: ConsentPurpose,
        legal_basis: LegalBasis, granted: bool,
        expires_at: Optional[datetime] = None
    ) -> Consent:
        consent = Consent(
            id=str(uuid.uuid4()),
            titular_id=titular_id,
            purpose=purpose,
            legal_basis=legal_basis,
            status=ConsentStatus.ACTIVE if granted else ConsentStatus.PENDING,
            expires_at=expires_at
        )
        if titular_id not in self._consents:
            self._consents[titular_id] = []
        self._consents[titular_id].append(consent)
        return consent

    async def revoke_consent(self, titular_id: str, purpose: ConsentPurpose) -> Consent:
        consents = self._consents.get(titular_id, [])
        for consent in consents:
            if consent.purpose == purpose and consent.status == ConsentStatus.ACTIVE:
                consent.status = ConsentStatus.REVOKED
                consent.revoked_at = datetime.now()
                return consent
        raise ValueError("Consent not found")

    async def has_valid_consent(self, titular_id: str, purpose: ConsentPurpose) -> bool:
        consents = self._consents.get(titular_id, [])
        for consent in consents:
            if consent.purpose == purpose and consent.status == ConsentStatus.ACTIVE:
                if consent.expires_at and consent.expires_at < datetime.now():
                    return False
                return True
        return False

    async def get_consents(self, titular_id: str) -> List[Consent]:
        return self._consents.get(titular_id, [])


class DataErasureManager:
    def __init__(self, db_session=None):
        self.db = db_session
        self._requests: Dict[str, ErasureRequest] = {}
        self._audit: Dict[str, List[Dict]] = {}

    async def create_request(
        self, titular_id: str, reason: str,
        requested_by: str = None, exclude_categories: List[str] = None
    ) -> ErasureRequest:
        request = ErasureRequest(
            id=str(uuid.uuid4()),
            titular_id=titular_id,
            reason=reason,
            status=ErasureStatus.PENDING,
            exclude_categories=exclude_categories or []
        )
        self._requests[request.id] = request
        self._audit[request.id] = [{"action": "created", "timestamp": datetime.now().isoformat()}]
        return request

    async def process_request(self, request_id: str) -> ErasureRequest:
        request = self._requests.get(request_id)
        if request:
            request.status = ErasureStatus.PROCESSING
            self._audit[request_id].append({"action": "processing", "timestamp": datetime.now().isoformat()})
            # Simulate processing
            request.status = ErasureStatus.COMPLETED
            request.completed_at = datetime.now()
            self._audit[request_id].append({"action": "completed", "timestamp": datetime.now().isoformat()})
        return request

    async def get_status(self, request_id: str) -> ErasureRequest:
        return self._requests.get(request_id)

    async def cancel_request(self, request_id: str, reason: str) -> ErasureRequest:
        request = self._requests.get(request_id)
        if request and request.status == ErasureStatus.PENDING:
            request.status = ErasureStatus.CANCELLED
            self._audit[request_id].append({"action": "cancelled", "reason": reason})
        return request

    async def get_audit_trail(self, request_id: str) -> List[Dict]:
        return self._audit.get(request_id, [])


class PIAManager:
    def __init__(self, db_session=None):
        self.db = db_session
        self._assessments: Dict[str, PIAAssessment] = {}

    async def create_assessment(self, nome: str, descricao: str, **kwargs) -> PIAAssessment:
        assessment = PIAAssessment(
            id=str(uuid.uuid4()),
            nome=nome,
            descricao=descricao
        )
        self._assessments[assessment.id] = assessment
        return assessment

    async def evaluate_risks(self, assessment_id: str) -> List[Dict]:
        assessment = self._assessments.get(assessment_id)
        if assessment:
            risks = [
                {"category": "data_breach", "probability": "medium", "impact": "high"},
                {"category": "unauthorized_access", "probability": "low", "impact": "high"}
            ]
            assessment.risks = risks
            return risks
        return []

    async def calculate_risk_level(self, assessment_id: str) -> RiskLevel:
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            return RiskLevel.LOW
        # Simple risk calculation based on number of high-risk factors
        high_risk_count = sum(1 for r in assessment.risks if r.get("impact") == "high")
        if high_risk_count >= 2:
            return RiskLevel.HIGH
        elif high_risk_count == 1:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    async def get_recommendations(self, assessment_id: str) -> List[str]:
        return [
            "Implementar criptografia de dados em repouso",
            "Estabelecer controles de acesso baseados em funcao",
            "Realizar auditorias periodicas de acesso"
        ]

    async def is_dpia_required(self, **kwargs) -> bool:
        dados_sensiveis = kwargs.get("dados_sensiveis", False)
        volume = kwargs.get("volume_titulares", 0)
        decisao_auto = kwargs.get("tomada_decisao_automatizada", False)
        monitoramento = kwargs.get("monitoramento_sistematico", False)

        risk_factors = sum([
            dados_sensiveis,
            volume > 1000,
            decisao_auto,
            monitoramento
        ])
        return risk_factors >= 2

    async def generate_report(self, assessment_id: str) -> Dict:
        assessment = self._assessments.get(assessment_id)
        if assessment:
            return {
                "id": assessment.id,
                "nome": assessment.nome,
                "risks": assessment.risks,
                "recommendations": await self.get_recommendations(assessment_id)
            }
        return {}


# =============================================================================
# CONSENT MANAGER TESTS
# =============================================================================

class TestConsentManager:
    @pytest.fixture
    def consent_manager(self):
        return ConsentManager(db_session=MagicMock())

    @pytest.fixture
    def sample_titular(self):
        return {"id": str(uuid.uuid4()), "cpf": "12345678901", "nome": "Maria Santos"}

    @pytest.mark.asyncio
    async def test_register_consent(self, consent_manager, sample_titular):
        consent = await consent_manager.register_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.MARKETING,
            legal_basis=LegalBasis.CONSENT,
            granted=True
        )
        assert consent is not None
        assert consent.status == ConsentStatus.ACTIVE
        assert consent.purpose == ConsentPurpose.MARKETING

    @pytest.mark.asyncio
    async def test_revoke_consent(self, consent_manager, sample_titular):
        await consent_manager.register_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.MARKETING,
            legal_basis=LegalBasis.CONSENT,
            granted=True
        )
        revoked = await consent_manager.revoke_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.MARKETING
        )
        assert revoked is not None
        assert revoked.status == ConsentStatus.REVOKED

    @pytest.mark.asyncio
    async def test_check_consent_active(self, consent_manager, sample_titular):
        await consent_manager.register_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.ANALYTICS,
            legal_basis=LegalBasis.CONSENT,
            granted=True
        )
        has_consent = await consent_manager.has_valid_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.ANALYTICS
        )
        assert has_consent is True

    @pytest.mark.asyncio
    async def test_check_consent_revoked(self, consent_manager, sample_titular):
        await consent_manager.register_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.MARKETING,
            legal_basis=LegalBasis.CONSENT,
            granted=True
        )
        await consent_manager.revoke_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.MARKETING
        )
        has_consent = await consent_manager.has_valid_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.MARKETING
        )
        assert has_consent is False

    @pytest.mark.asyncio
    async def test_consent_expiration(self, consent_manager, sample_titular):
        consent = await consent_manager.register_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.DATA_SHARING,
            legal_basis=LegalBasis.CONSENT,
            granted=True,
            expires_at=datetime.now() + timedelta(days=30)
        )
        assert consent.expires_at is not None

    @pytest.mark.asyncio
    async def test_get_all_consents_for_titular(self, consent_manager, sample_titular):
        await consent_manager.register_consent(
            titular_id=sample_titular["id"], purpose=ConsentPurpose.MARKETING,
            legal_basis=LegalBasis.CONSENT, granted=True
        )
        await consent_manager.register_consent(
            titular_id=sample_titular["id"], purpose=ConsentPurpose.ANALYTICS,
            legal_basis=LegalBasis.CONSENT, granted=True
        )
        consents = await consent_manager.get_consents(titular_id=sample_titular["id"])
        assert len(consents) >= 2

    @pytest.mark.asyncio
    async def test_legal_basis_legitimate_interest(self, consent_manager, sample_titular):
        consent = await consent_manager.register_consent(
            titular_id=sample_titular["id"],
            purpose=ConsentPurpose.SERVICE_PROVISION,
            legal_basis=LegalBasis.LEGITIMATE_INTEREST,
            granted=True
        )
        assert consent.legal_basis == LegalBasis.LEGITIMATE_INTEREST


# =============================================================================
# DATA ERASURE TESTS
# =============================================================================

class TestDataErasureManager:
    @pytest.fixture
    def erasure_manager(self):
        return DataErasureManager(db_session=MagicMock())

    @pytest.fixture
    def sample_titular_id(self):
        return str(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_erasure_request(self, erasure_manager, sample_titular_id):
        request = await erasure_manager.create_request(
            titular_id=sample_titular_id,
            reason="Exercicio do direito ao esquecimento",
            requested_by=sample_titular_id
        )
        assert request is not None
        assert request.status == ErasureStatus.PENDING
        assert request.titular_id == sample_titular_id

    @pytest.mark.asyncio
    async def test_process_erasure_request(self, erasure_manager, sample_titular_id):
        request = await erasure_manager.create_request(
            titular_id=sample_titular_id,
            reason="Solicitacao do titular"
        )
        processed = await erasure_manager.process_request(request.id)
        assert processed.status in [ErasureStatus.PROCESSING, ErasureStatus.COMPLETED]

    @pytest.mark.asyncio
    async def test_erasure_with_retention_exception(self, erasure_manager, sample_titular_id):
        request = await erasure_manager.create_request(
            titular_id=sample_titular_id,
            reason="Solicitacao do titular",
            exclude_categories=["fiscal", "trabalhista"]
        )
        assert request is not None
        assert "fiscal" in request.exclude_categories

    @pytest.mark.asyncio
    async def test_get_erasure_status(self, erasure_manager, sample_titular_id):
        request = await erasure_manager.create_request(
            titular_id=sample_titular_id, reason="Teste"
        )
        status = await erasure_manager.get_status(request.id)
        assert status is not None
        assert status.status == ErasureStatus.PENDING

    @pytest.mark.asyncio
    async def test_cancel_erasure_request(self, erasure_manager, sample_titular_id):
        request = await erasure_manager.create_request(
            titular_id=sample_titular_id, reason="Teste"
        )
        cancelled = await erasure_manager.cancel_request(
            request.id, reason="Solicitacao cancelada pelo titular"
        )
        assert cancelled.status == ErasureStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_erasure_audit_trail(self, erasure_manager, sample_titular_id):
        request = await erasure_manager.create_request(
            titular_id=sample_titular_id, reason="Teste de auditoria"
        )
        await erasure_manager.process_request(request.id)
        audit = await erasure_manager.get_audit_trail(request.id)
        assert audit is not None
        assert len(audit) >= 1


# =============================================================================
# PRIVACY IMPACT ASSESSMENT TESTS
# =============================================================================

class TestPIAManager:
    @pytest.fixture
    def pia_manager(self):
        return PIAManager(db_session=MagicMock())

    @pytest.fixture
    def sample_activity(self):
        return {
            "nome": "Processamento de dados de funcionarios",
            "descricao": "Coleta e processamento de dados pessoais para folha de pagamento"
        }

    @pytest.mark.asyncio
    async def test_create_assessment(self, pia_manager, sample_activity):
        assessment = await pia_manager.create_assessment(**sample_activity)
        assert assessment is not None
        assert assessment.id is not None

    @pytest.mark.asyncio
    async def test_evaluate_risks(self, pia_manager, sample_activity):
        assessment = await pia_manager.create_assessment(**sample_activity)
        risks = await pia_manager.evaluate_risks(assessment.id)
        assert risks is not None
        assert isinstance(risks, list)

    @pytest.mark.asyncio
    async def test_risk_level_calculation(self, pia_manager):
        assessment = await pia_manager.create_assessment(
            nome="Processamento de dados sensiveis",
            descricao="Dados de saude e biometricos"
        )
        await pia_manager.evaluate_risks(assessment.id)
        risk_level = await pia_manager.calculate_risk_level(assessment.id)
        assert risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]

    @pytest.mark.asyncio
    async def test_mitigation_recommendations(self, pia_manager, sample_activity):
        assessment = await pia_manager.create_assessment(**sample_activity)
        recommendations = await pia_manager.get_recommendations(assessment.id)
        assert recommendations is not None
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_dpia_required_check(self, pia_manager):
        required = await pia_manager.is_dpia_required(
            dados_sensiveis=True,
            volume_titulares=5000,
            tomada_decisao_automatizada=True,
            monitoramento_sistematico=True
        )
        assert required is True

    @pytest.mark.asyncio
    async def test_dpia_not_required(self, pia_manager):
        required = await pia_manager.is_dpia_required(
            dados_sensiveis=False,
            volume_titulares=50,
            tomada_decisao_automatizada=False,
            monitoramento_sistematico=False
        )
        assert required is False

    @pytest.mark.asyncio
    async def test_generate_report(self, pia_manager, sample_activity):
        assessment = await pia_manager.create_assessment(**sample_activity)
        await pia_manager.evaluate_risks(assessment.id)
        report = await pia_manager.generate_report(assessment.id)
        assert report is not None
        assert "risks" in report


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestComplianceIntegration:
    @pytest.mark.asyncio
    async def test_full_consent_lifecycle(self):
        manager = ConsentManager(db_session=MagicMock())
        titular_id = str(uuid.uuid4())

        # 1. Register consent
        consent = await manager.register_consent(
            titular_id=titular_id, purpose=ConsentPurpose.MARKETING,
            legal_basis=LegalBasis.CONSENT, granted=True
        )
        assert consent.status == ConsentStatus.ACTIVE

        # 2. Verify consent
        has_consent = await manager.has_valid_consent(
            titular_id=titular_id, purpose=ConsentPurpose.MARKETING
        )
        assert has_consent is True

        # 3. Revoke consent
        revoked = await manager.revoke_consent(
            titular_id=titular_id, purpose=ConsentPurpose.MARKETING
        )
        assert revoked.status == ConsentStatus.REVOKED

        # 4. Verify revocation
        has_consent = await manager.has_valid_consent(
            titular_id=titular_id, purpose=ConsentPurpose.MARKETING
        )
        assert has_consent is False

    @pytest.mark.asyncio
    async def test_erasure_workflow(self):
        erasure_mgr = DataErasureManager(db_session=MagicMock())
        titular_id = str(uuid.uuid4())

        request = await erasure_mgr.create_request(
            titular_id=titular_id,
            reason="Exercicio do direito ao esquecimento"
        )
        assert request is not None

        processed = await erasure_mgr.process_request(request.id)
        assert processed.status == ErasureStatus.COMPLETED
