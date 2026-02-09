"""Testes do LGPD Compliance Manager - Sprint 03."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from modules.notifications.compliance.lgpd_manager import (
    ComplianceAuditLog,
    ConsentRecord,
    ConsentStatus,
    ConsentType,
    DataProcessingRequest,
    DataRequestType,
    LGPDComplianceManager,
    RequestStatus,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_db():
    """Mock da sessão do banco."""
    return AsyncMock()


@pytest.fixture
def compliance_manager():
    """Instância do LGPDComplianceManager."""
    return LGPDComplianceManager()


# ============================================================================
# Tests - Consent Management
# ============================================================================


class TestConsentManagement:
    """Testes de gestão de consentimento."""

    @pytest.mark.asyncio
    async def test_record_consent_granted(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa registro de consentimento concedido."""
        consent = await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito receber comunicações de marketing.",
            version="1.0",
            ip_address="192.168.1.1",
        )

        assert isinstance(consent, ConsentRecord)
        assert consent.user_id == 1
        assert consent.consent_type == ConsentType.MARKETING
        assert consent.status == ConsentStatus.GRANTED
        assert consent.granted_at is not None
        assert consent.expires_at is not None

    @pytest.mark.asyncio
    async def test_record_consent_denied(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa registro de consentimento negado."""
        consent = await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.THIRD_PARTY,
            granted=False,
            consent_text="Não desejo compartilhar dados com terceiros.",
            version="1.0",
        )

        assert consent.status == ConsentStatus.DENIED
        assert consent.granted_at is None

    @pytest.mark.asyncio
    async def test_withdraw_consent(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa retirada de consentimento."""
        # Primeiro, conceder consentimento
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.NEWSLETTER,
            granted=True,
            consent_text="Aceito newsletter.",
            version="1.0",
        )

        # Depois, retirar
        withdrawn = await compliance_manager.withdraw_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.NEWSLETTER,
            reason="Não desejo mais receber.",
        )

        assert withdrawn.status == ConsentStatus.WITHDRAWN
        assert withdrawn.withdrawn_at is not None

    @pytest.mark.asyncio
    async def test_check_consent_active(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa verificação de consentimento ativo."""
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito marketing.",
            version="1.0",
        )

        has_consent = await compliance_manager.check_consent(
            mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
        )

        assert has_consent is True

    @pytest.mark.asyncio
    async def test_check_consent_withdrawn(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa verificação de consentimento retirado."""
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito marketing.",
            version="1.0",
        )

        await compliance_manager.withdraw_consent(
            mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
        )

        has_consent = await compliance_manager.check_consent(
            mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
        )

        assert has_consent is False

    @pytest.mark.asyncio
    async def test_check_consent_nonexistent(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa verificação de consentimento inexistente."""
        has_consent = await compliance_manager.check_consent(
            mock_db,
            user_id=999,
            consent_type=ConsentType.MARKETING,
        )

        assert has_consent is False

    @pytest.mark.asyncio
    async def test_get_user_consents(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa obtenção de todos os consentimentos de um usuário."""
        # Registrar múltiplos consentimentos
        for consent_type in [ConsentType.MARKETING, ConsentType.NEWSLETTER]:
            await compliance_manager.record_consent(
                db=mock_db,
                user_id=1,
                consent_type=consent_type,
                granted=True,
                consent_text="Aceito.",
                version="1.0",
            )

        consents = await compliance_manager.get_user_consents(mock_db, user_id=1)

        assert len(consents) == 2


# ============================================================================
# Tests - Data Requests (DSAR)
# ============================================================================


class TestDataRequests:
    """Testes de solicitações de dados (DSAR)."""

    @pytest.mark.asyncio
    async def test_create_access_request(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa criação de solicitação de acesso."""
        request = await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.ACCESS,
            requester_email="user@example.com",
        )

        assert isinstance(request, DataProcessingRequest)
        assert request.user_id == 1
        assert request.request_type == DataRequestType.ACCESS
        assert request.status == RequestStatus.PENDING
        assert request.deadline is not None
        assert request.verification_token is not None

    @pytest.mark.asyncio
    async def test_create_deletion_request(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa criação de solicitação de exclusão."""
        request = await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.DELETION,
            requester_email="user@example.com",
        )

        assert request.request_type == DataRequestType.DELETION
        # Verificar prazo (15 dias para exclusão)
        expected_deadline = datetime.utcnow() + timedelta(days=compliance_manager.DELETION_REQUEST_DEADLINE_DAYS)
        assert request.deadline.date() == expected_deadline.date()

    @pytest.mark.asyncio
    async def test_verify_data_request(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa verificação de solicitação."""
        request = await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.ACCESS,
            requester_email="user@example.com",
        )

        # Verificar com token correto
        verified = await compliance_manager.verify_data_request(
            mock_db,
            request.id,
            request.verification_token,
        )

        assert verified is True

    @pytest.mark.asyncio
    async def test_verify_wrong_token(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa verificação com token incorreto."""
        request = await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.ACCESS,
            requester_email="user@example.com",
        )

        verified = await compliance_manager.verify_data_request(
            mock_db,
            request.id,
            "wrong_token",
        )

        assert verified is False

    @pytest.mark.asyncio
    async def test_process_access_request(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa processamento de solicitação de acesso."""
        request = await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.ACCESS,
            requester_email="user@example.com",
        )

        # Verificar primeiro
        await compliance_manager.verify_data_request(
            mock_db,
            request.id,
            request.verification_token,
        )

        # Processar
        result = await compliance_manager.process_access_request(mock_db, request.id)

        assert result.request_id == request.id
        assert result.export_format == "json"
        assert len(result.data_categories) > 0
        assert result.checksum is not None

    @pytest.mark.asyncio
    async def test_process_deletion_request(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa processamento de solicitação de exclusão."""
        # Criar consentimento
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito.",
            version="1.0",
        )

        # Criar solicitação de exclusão
        request = await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.DELETION,
            requester_email="user@example.com",
        )

        # Verificar
        await compliance_manager.verify_data_request(
            mock_db,
            request.id,
            request.verification_token,
        )

        # Processar
        success = await compliance_manager.process_deletion_request(mock_db, request.id)

        assert success is True

        # Verificar que consentimentos foram retirados
        consents = await compliance_manager.get_user_consents(mock_db, user_id=1)
        for consent in consents:
            assert consent.status == ConsentStatus.WITHDRAWN

    @pytest.mark.asyncio
    async def test_process_unverified_request(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa processamento de solicitação não verificada."""
        request = await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.ACCESS,
            requester_email="user@example.com",
        )

        with pytest.raises(ValueError, match="not verified"):
            await compliance_manager.process_access_request(mock_db, request.id)


# ============================================================================
# Tests - Notification Send Permission
# ============================================================================


class TestNotificationPermission:
    """Testes de permissão para envio de notificações."""

    @pytest.mark.asyncio
    async def test_can_send_system_notification(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa que notificações de sistema não precisam de consentimento."""
        can_send, reason = await compliance_manager.can_send_notification(
            mock_db,
            user_id=1,
            notification_type="system",
        )

        assert can_send is True
        assert "System" in reason

    @pytest.mark.asyncio
    async def test_can_send_transaction_notification(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa que notificações transacionais não precisam de consentimento."""
        can_send, reason = await compliance_manager.can_send_notification(
            mock_db,
            user_id=1,
            notification_type="transaction",
        )

        assert can_send is True

    @pytest.mark.asyncio
    async def test_cannot_send_marketing_without_consent(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa que marketing precisa de consentimento."""
        can_send, reason = await compliance_manager.can_send_notification(
            mock_db,
            user_id=1,
            notification_type="marketing",
        )

        assert can_send is False
        assert "consent" in reason.lower()

    @pytest.mark.asyncio
    async def test_can_send_marketing_with_consent(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa que marketing pode ser enviado com consentimento."""
        # Registrar consentimento
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito marketing.",
            version="1.0",
        )

        can_send, reason = await compliance_manager.can_send_notification(
            mock_db,
            user_id=1,
            notification_type="marketing",
        )

        assert can_send is True
        assert "verified" in reason.lower()


# ============================================================================
# Tests - Audit Logging
# ============================================================================


class TestAuditLogging:
    """Testes de logs de auditoria."""

    @pytest.mark.asyncio
    async def test_consent_creates_audit_log(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa que consentimento cria log de auditoria."""
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito.",
            version="1.0",
        )

        logs = await compliance_manager.get_audit_logs(
            mock_db,
            user_id=1,
            action="consent_recorded",
        )

        assert len(logs) > 0
        assert logs[0].action == "consent_recorded"
        assert logs[0].user_id == 1

    @pytest.mark.asyncio
    async def test_data_request_creates_audit_log(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa que solicitação de dados cria log."""
        await compliance_manager.create_data_request(
            db=mock_db,
            user_id=1,
            request_type=DataRequestType.ACCESS,
            requester_email="user@example.com",
        )

        logs = await compliance_manager.get_audit_logs(
            mock_db,
            action="data_request_created",
        )

        assert len(logs) > 0
        assert logs[0].action == "data_request_created"

    @pytest.mark.asyncio
    async def test_filter_audit_logs_by_date(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa filtro de logs por data."""
        # Criar alguns eventos
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito.",
            version="1.0",
        )

        now = datetime.utcnow()
        logs = await compliance_manager.get_audit_logs(
            mock_db,
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1),
        )

        assert all(now - timedelta(hours=1) <= log.timestamp <= now + timedelta(hours=1) for log in logs)


# ============================================================================
# Tests - Compliance Reports
# ============================================================================


class TestComplianceReports:
    """Testes de relatórios de compliance."""

    @pytest.mark.asyncio
    async def test_generate_compliance_report(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa geração de relatório de compliance."""
        # Criar alguns eventos
        await compliance_manager.record_consent(
            db=mock_db,
            user_id=1,
            consent_type=ConsentType.MARKETING,
            granted=True,
            consent_text="Aceito.",
            version="1.0",
        )

        await compliance_manager.create_data_request(
            db=mock_db,
            user_id=2,
            request_type=DataRequestType.ACCESS,
            requester_email="user@example.com",
        )

        report = await compliance_manager.generate_compliance_report(
            mock_db,
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=1),
        )

        assert "period" in report
        assert "summary" in report
        assert "action_breakdown" in report
        assert "consent_stats" in report


# ============================================================================
# Tests - Edge Cases
# ============================================================================


class TestEdgeCases:
    """Testes de casos extremos."""

    @pytest.mark.asyncio
    async def test_multiple_consent_types(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa múltiplos tipos de consentimento para mesmo usuário."""
        for consent_type in ConsentType:
            await compliance_manager.record_consent(
                db=mock_db,
                user_id=1,
                consent_type=consent_type,
                granted=True,
                consent_text=f"Aceito {consent_type.value}.",
                version="1.0",
            )

        consents = await compliance_manager.get_user_consents(mock_db, user_id=1)
        assert len(consents) == len(ConsentType)

    @pytest.mark.asyncio
    async def test_withdraw_nonexistent_consent(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa retirada de consentimento inexistente."""
        with pytest.raises(ValueError, match="not found"):
            await compliance_manager.withdraw_consent(
                mock_db,
                user_id=999,
                consent_type=ConsentType.MARKETING,
            )

    @pytest.mark.asyncio
    async def test_verify_nonexistent_request(
        self,
        mock_db,
        compliance_manager,
    ):
        """Testa verificação de solicitação inexistente."""
        fake_id = uuid4()
        verified = await compliance_manager.verify_data_request(
            mock_db,
            fake_id,
            "any_token",
        )

        assert verified is False
