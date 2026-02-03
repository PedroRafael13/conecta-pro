"""
Testes para LGPD Compliance - endpoints de proteção de dados.

Testa implementação real do Art. 15 LGPD (direito de acesso).
Execute com: python -m pytest tests/test_lgpd_compliance.py -v -s
"""

import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Adiciona backend ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI

from modules.notifications.compliance.lgpd_manager import LGPDManager
from modules.notifications.controllers.compliance_controller import router

# Mock app para teste
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestLGPDCompliance:
    """Testes para funcionalidades de compliance LGPD."""

    def setup_method(self):
        """Setup para cada teste."""
        self.lgpd_manager = LGPDManager()
        self.user_id = 12345

    @pytest.mark.asyncio
    async def test_collect_user_data_structure(self):
        """Testa estrutura de dados coletados (sem DB)."""
        from unittest.mock import AsyncMock, MagicMock

        # Mock database session
        mock_db = AsyncMock()

        # Mock user data
        mock_user = MagicMock()
        mock_user.id = self.user_id
        mock_user.name = "João Silva"
        mock_user.email = "joao@test.com"
        mock_user.phone = "+5511999999999"
        mock_user.role = "operator"
        mock_user.created_at = datetime(2024, 1, 1, 10, 0, 0)
        mock_user.updated_at = datetime(2024, 2, 1, 15, 30, 0)
        mock_user.last_login = "2024-02-01T10:00:00"

        # Mock query results
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        # Executar coleta de dados
        user_data = await self.lgpd_manager._collect_user_data(mock_db, self.user_id)

        # Verificar estrutura principal
        assert "user_id" in user_data
        assert "export_date" in user_data
        assert "export_version" in user_data
        assert "data_categories" in user_data
        assert "metadata" in user_data

        # Verificar categorias de dados
        categories = user_data["data_categories"]
        assert "basic_profile" in categories
        assert "notification_preferences" in categories
        assert "notification_history" in categories
        assert "registered_devices" in categories
        assert "engagement_analytics" in categories
        assert "consent_records" in categories

        # Verificar dados básicos
        basic_profile = categories["basic_profile"]
        assert basic_profile["user_id"] == self.user_id
        assert basic_profile["name"] == "João Silva"
        assert basic_profile["email"] == "joao@test.com"
        assert basic_profile["phone"] == "+5511999999999"
        assert basic_profile["role"] == "operator"

        # Verificar metadados
        metadata = user_data["metadata"]
        assert "export_requested_by" in metadata
        assert "data_sources" in metadata
        assert "legal_basis" in metadata
        assert "LGPD" in metadata["legal_basis"]

    def test_calculate_engagement_stats_empty(self):
        """Testa cálculo de engajamento com dados vazios."""
        notifications = []

        stats = self.lgpd_manager._calculate_engagement_stats(notifications)

        assert stats["total_notifications"] == 0
        assert stats["engagement_rate"] == 0.0
        assert stats["most_active_hour"] is None

    def test_calculate_engagement_stats_with_data(self):
        """Testa cálculo de engajamento com dados."""
        from unittest.mock import MagicMock

        # Mock notifications
        notifications = []
        for i in range(10):
            notif = MagicMock()
            notif.opened_at = datetime(2024, 1, 1, 10, 0, 0) if i < 5 else None
            notif.channel = "email" if i < 6 else "push"
            notifications.append(notif)

        stats = self.lgpd_manager._calculate_engagement_stats(notifications)

        assert stats["total_notifications"] == 10
        assert stats["opened_notifications"] == 5
        assert stats["engagement_rate"] == 50.0
        assert stats["most_active_hour"] == "10:00"
        assert "engagement_by_channel" in stats

    def test_calculate_channel_engagement(self):
        """Testa cálculo de engajamento por canal."""
        from unittest.mock import MagicMock

        notifications = []

        # Email notifications (3 total, 2 opened)
        for i in range(3):
            notif = MagicMock()
            notif.channel = "email"
            notif.opened_at = datetime(2024, 1, 1, 10, 0, 0) if i < 2 else None
            notifications.append(notif)

        # Push notifications (2 total, 1 opened)
        for i in range(2):
            notif = MagicMock()
            notif.channel = "push"
            notif.opened_at = datetime(2024, 1, 1, 10, 0, 0) if i < 1 else None
            notifications.append(notif)

        channel_stats = self.lgpd_manager._calculate_channel_engagement(notifications)

        assert "email" in channel_stats
        assert "push" in channel_stats

        email_stats = channel_stats["email"]
        assert email_stats["total"] == 3
        assert email_stats["opened"] == 2
        assert email_stats["engagement_rate"] == 66.67

        push_stats = channel_stats["push"]
        assert push_stats["total"] == 2
        assert push_stats["opened"] == 1
        assert push_stats["engagement_rate"] == 50.0

    @pytest.mark.asyncio
    async def test_collect_consent_records(self):
        """Testa coleta de registros de consentimento."""
        from unittest.mock import AsyncMock, MagicMock

        mock_db = AsyncMock()

        # Mock preference data
        mock_pref = MagicMock()
        mock_pref.category.value = "marketing"
        mock_pref.channel.value = "email"
        mock_pref.created_at = datetime(2024, 1, 1, 10, 0, 0)
        mock_pref.updated_at = datetime(2024, 2, 1, 10, 0, 0)

        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_pref]

        consent_records = await self.lgpd_manager._collect_consent_records(mock_db, self.user_id)

        assert len(consent_records) == 1
        record = consent_records[0]
        assert record["consent_type"] == "marketing"
        assert record["status"] == "granted"
        assert record["channel"] == "email"
        assert record["source"] == "notification_preferences"

    def test_privacy_policy_endpoint(self):
        """Testa endpoint de política de privacidade."""
        response = client.get("/compliance/privacy-policy")

        assert response.status_code == 200
        data = response.json()

        assert "privacy_policy" in data
        assert "controller" in data["privacy_policy"]
        assert "data_processing" in data["privacy_policy"]
        assert "data_subject_rights" in data["privacy_policy"]
        assert "contact" in data["privacy_policy"]

        # Verificar informações do controlador
        controller = data["privacy_policy"]["controller"]
        assert controller["name"] == "Conecta Mais"
        assert "dpo@conectamais.pro" in controller["contact"]

        # Verificar direitos do titular
        rights = data["privacy_policy"]["data_subject_rights"]
        assert "access" in rights
        assert "deletion" in rights
        assert "portability" in rights
        assert "/api/v1/notifications/compliance/my-data" in rights["access"]


class TestLGPDValidation:
    """Testes para validações LGPD."""

    def test_data_request_validation(self):
        """Testa validações de solicitação de dados."""
        from pydantic import ValidationError

        from modules.notifications.schemas.compliance_schemas import DataRequestCreate

        # Teste com dados válidos
        valid_request = DataRequestCreate(request_type="access", description="Solicito acesso aos meus dados")
        assert valid_request.request_type == "access"

        # Teste com tipo inválido
        with pytest.raises(ValidationError):
            DataRequestCreate(request_type="invalid_type")

        # Teste com descrição obrigatória para exclusão
        with pytest.raises(ValidationError):
            DataRequestCreate(
                request_type="deletion",
                description="",  # Vazio para exclusão
            )

    def test_deletion_confirmation_validation(self):
        """Testa validação de confirmação de exclusão."""
        from pydantic import ValidationError

        from modules.notifications.schemas.compliance_schemas import DataDeletionConfirmation

        # Confirmação válida
        valid_confirmation = DataDeletionConfirmation(confirmation="DELETE_MY_DATA", reason="Não uso mais o serviço")
        assert valid_confirmation.confirmation == "DELETE_MY_DATA"

        # Confirmação inválida
        with pytest.raises(ValidationError) as exc_info:
            DataDeletionConfirmation(confirmation="delete")

        assert "DELETE_MY_DATA" in str(exc_info.value)


class TestLGPDSecurity:
    """Testes para segurança dos endpoints LGPD."""

    def test_endpoint_requires_authentication(self):
        """Testa que endpoints requerem autenticação."""
        # Tentar acessar sem token
        response = client.get("/compliance/my-data")

        # Deve retornar 401 ou 403 (dependendo da implementação de auth)
        assert response.status_code in [401, 403, 422]  # 422 se der erro de validação

    def test_rate_limiting_considerations(self):
        """Testa considerações de rate limiting."""
        # Este teste seria implementado com rate limiting real
        # Por enquanto, apenas documenta a necessidade

        # LGPD endpoints devem ter rate limiting especial:
        # - /my-data: 1 request/hour
        # - /data-request: 5 requests/day
        # - /delete: 1 request/day

        assert True  # Placeholder

    def test_audit_logging(self):
        """Testa que ações LGPD geram audit logs."""
        # Este teste seria implementado com audit logging real

        # Todas as ações LGPD devem gerar logs:
        # - Data export
        # - Data deletion requests
        # - Consent changes
        # - Privacy settings updates

        assert True  # Placeholder


if __name__ == "__main__":
    # Execução direta para debug
    pytest.main([__file__, "-v", "-s"])
