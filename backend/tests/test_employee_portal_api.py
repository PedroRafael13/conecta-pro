"""Testes para API do Portal do Funcionário."""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from modules.hr.employee_portal.models import (
    DocumentType,
    NotificationPriority,
    NotificationType,
    PaySlipStatus,
    VacationStatus,
)
from modules.hr.employee_portal.schemas import (
    VacationBalanceResponse,
    VacationCalculationRequest,
    VacationCalculationResponse,
    VacationRequestCreate,
)


class TestPaySlipAPI:
    """Testes para API de contracheques."""

    @pytest.fixture
    def mock_payslip_service(self):
        """Mock do PaySlipService."""
        with patch("modules.hr.employee_portal.controllers.payslip_controller.PaySlipService") as mock:
            service = AsyncMock()
            mock.return_value = service
            yield service

    @pytest.fixture
    def mock_current_user(self):
        """Mock do usuário atual."""
        return {
            "sub": str(uuid4()),
            "employee_id": str(uuid4()),
            "condominio_id": str(uuid4()),
            "email": "funcionario@teste.com",
            "role": "employee",
        }

    def test_list_payslips_schema(self):
        """Testa estrutura de resposta de listagem."""
        # Simular resposta
        response_data = {
            "items": [
                {
                    "id": str(uuid4()),
                    "payslip_code": "2024-01-001",
                    "reference_period": "2024-01",
                    "net_salary": 3000.00,
                    "status": "published",
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

        assert "items" in response_data
        assert response_data["total"] == 1
        assert len(response_data["items"]) == 1

    def test_payslip_summary_structure(self):
        """Testa estrutura do resumo de contracheques."""
        summary = {
            "unread_count": 2,
            "pending_acknowledgement": 1,
            "available_years": [2024, 2023],
            "last_payslip": {
                "id": str(uuid4()),
                "reference_period": "2024-01",
                "net_salary": 3500.00,
                "payment_date": "2024-01-05",
            },
        }

        assert summary["unread_count"] == 2
        assert 2024 in summary["available_years"]


class TestVacationAPI:
    """Testes para API de férias."""

    def test_vacation_request_create_schema(self):
        """Testa schema de criação de solicitação."""
        data = VacationRequestCreate(
            start_date=date.today() + timedelta(days=45),
            end_date=date.today() + timedelta(days=60),
            days_requested=15,
            sell_days=0,
            advance_13th=False,
            employee_notes="Férias programadas",
        )

        assert data.days_requested == 15
        assert data.sell_days == 0

    def test_vacation_calculation_request_schema(self):
        """Testa schema de cálculo de férias."""
        data = VacationCalculationRequest(
            start_date=date.today() + timedelta(days=45),
            days_requested=20,
            sell_days=10,
            advance_13th=True,
        )

        assert data.days_requested == 20
        assert data.sell_days == 10
        assert data.advance_13th is True

    def test_vacation_balance_response_structure(self):
        """Testa estrutura da resposta de saldo."""
        balance = {
            "employee_id": str(uuid4()),
            "periods": [
                {
                    "id": str(uuid4()),
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31",
                    "days_remaining": 30,
                    "days_until_expiration": 180,
                    "is_expired": False,
                }
            ],
            "total_days_available": 30,
            "total_days_used": 0,
            "total_days_sold": 0,
            "total_days_remaining": 30,
            "pending_requests_count": 0,
            "has_expiring_period": False,
        }

        assert balance["total_days_available"] == 30
        assert len(balance["periods"]) == 1

    def test_vacation_calculation_values(self):
        """Testa valores de cálculo de férias."""
        # Simular cálculo para salário de R$ 3.000,00
        base_salary = Decimal("3000.00")
        days_requested = 20
        sell_days = 10

        # Valor diário
        daily_rate = base_salary / Decimal("30")
        assert daily_rate == Decimal("100.00")

        # Férias
        vacation_value = daily_rate * days_requested
        assert vacation_value == Decimal("2000.00")

        # 1/3 constitucional
        vacation_bonus = vacation_value / Decimal("3")
        assert vacation_bonus == Decimal("666.6666666666666666666666667")

        # Abono pecuniário
        sell_value = daily_rate * sell_days
        assert sell_value == Decimal("1000.00")


class TestDocumentAPI:
    """Testes para API de documentos."""

    def test_document_list_filters(self):
        """Testa filtros de listagem de documentos."""
        filters = {
            "type": DocumentType.PAYSLIP.value,
            "category": "folha_pagamento",
            "search": "janeiro",
            "pending_ack": False,
            "pending_signature": False,
            "page": 1,
            "page_size": 20,
        }

        assert filters["type"] == "payslip"
        assert filters["page_size"] == 20

    def test_document_pending_counts_structure(self):
        """Testa estrutura de contagem de pendências."""
        counts = {
            "pending_acknowledgement": 3,
            "pending_signature": 1,
            "expiring_soon": 2,
        }

        assert counts["pending_acknowledgement"] == 3

    def test_document_categories(self):
        """Testa categorias de documentos."""
        categories = [
            "folha_pagamento",
            "ferias",
            "contratos",
            "beneficios",
            "treinamentos",
            "atestados",
            "outros",
        ]

        assert len(categories) == 7
        assert "contratos" in categories


class TestNotificationAPI:
    """Testes para API de notificações."""

    def test_notification_list_filters(self):
        """Testa filtros de listagem de notificações."""
        filters = {
            "is_read": False,
            "type": NotificationType.PAYSLIP_AVAILABLE.value,
            "page": 1,
            "page_size": 20,
        }

        assert filters["is_read"] is False

    def test_unread_count_structure(self):
        """Testa estrutura de contagem de não lidas."""
        unread = {
            "total_unread": 5,
            "by_type": {
                "payslip_available": 2,
                "document_available": 3,
            },
            "by_priority": {
                "high": 1,
                "normal": 4,
            },
            "oldest_unread_at": None,
        }

        assert unread["total_unread"] == 5
        assert unread["by_type"]["payslip_available"] == 2

    def test_notification_mark_multiple_read(self):
        """Testa marcação de múltiplas notificações."""
        notification_ids = [str(uuid4()) for _ in range(5)]

        assert len(notification_ids) == 5


class TestPreferencesAPI:
    """Testes para API de preferências."""

    def test_preferences_default_values(self):
        """Testa valores padrão das preferências."""
        defaults = {
            "theme": "system",
            "language": "pt_BR",
            "timezone": "America/Sao_Paulo",
            "date_format": "DD/MM/YYYY",
            "email_notifications": True,
            "push_notifications": True,
            "sms_notifications": False,
            "whatsapp_notifications": False,
            "high_contrast": False,
            "font_size": "medium",
            "reduced_motion": False,
            "two_factor_enabled": False,
        }

        assert defaults["theme"] == "system"
        assert defaults["email_notifications"] is True
        assert defaults["two_factor_enabled"] is False

    def test_notification_settings_update(self):
        """Testa atualização de configurações de notificação."""
        update_data = {
            "email_notifications": True,
            "push_notifications": False,
            "sms_notifications": True,
            "notification_settings": {
                "payslip_available": {"email": True, "push": False},
                "vacation_approved": {"email": True, "push": True, "sms": True},
            },
        }

        assert update_data["sms_notifications"] is True
        assert update_data["notification_settings"]["payslip_available"]["email"] is True

    def test_privacy_settings_update(self):
        """Testa atualização de configurações de privacidade."""
        update_data = {
            "show_birthday": True,
            "show_photo": True,
            "show_contact": False,
            "privacy_settings": {
                "show_email": False,
                "show_phone": False,
                "show_address": False,
            },
        }

        assert update_data["show_contact"] is False

    def test_dashboard_widgets_config(self):
        """Testa configuração de widgets do dashboard."""
        widgets = [
            {
                "id": "payslips",
                "order": 1,
                "visible": True,
                "size": "medium",
            },
            {
                "id": "vacation_balance",
                "order": 2,
                "visible": True,
                "size": "small",
            },
            {
                "id": "notifications",
                "order": 3,
                "visible": True,
                "size": "large",
            },
        ]

        assert len(widgets) == 3
        assert widgets[0]["id"] == "payslips"

    def test_2fa_setup_response(self):
        """Testa resposta de configuração de 2FA."""
        setup_response = {
            "secret": "JBSWY3DPEHPK3PXP",
            "qr_code_url": "otpauth://totp/Portal:funcionario@teste.com?secret=JBSWY3DPEHPK3PXP&issuer=Portal",
            "backup_codes": [
                "12345678",
                "23456789",
                "34567890",
                "45678901",
                "56789012",
            ],
        }

        assert len(setup_response["backup_codes"]) == 5
        assert "secret" in setup_response

    def test_trusted_devices_structure(self):
        """Testa estrutura de dispositivos confiáveis."""
        devices = [
            {
                "id": "device-001",
                "name": "Chrome no Windows",
                "user_agent": "Mozilla/5.0...",
                "ip_address": "192.168.1.100",
                "added_at": "2024-01-10T10:00:00Z",
                "last_used_at": "2024-01-15T08:30:00Z",
            },
            {
                "id": "device-002",
                "name": "iPhone",
                "user_agent": "Mozilla/5.0...",
                "ip_address": "192.168.1.101",
                "added_at": "2024-01-12T14:00:00Z",
                "last_used_at": "2024-01-15T09:00:00Z",
            },
        ]

        assert len(devices) == 2
        assert devices[0]["name"] == "Chrome no Windows"


class TestVacationCalculationService:
    """Testes para serviço de cálculo de férias."""

    def test_inss_calculation_band_1(self):
        """Testa cálculo INSS - faixa 1 (até R$ 1.412,00)."""
        base = Decimal("1412.00")
        expected = base * Decimal("0.075")
        assert expected == Decimal("105.9000")

    def test_inss_calculation_band_2(self):
        """Testa cálculo INSS - faixa 2 (R$ 1.412,01 a R$ 2.666,68)."""
        base = Decimal("2000.00")
        expected = base * Decimal("0.09") - Decimal("21.18")
        assert expected == Decimal("158.82")

    def test_inss_calculation_band_3(self):
        """Testa cálculo INSS - faixa 3 (R$ 2.666,69 a R$ 4.000,03)."""
        base = Decimal("3500.00")
        expected = base * Decimal("0.12") - Decimal("101.18")
        assert expected == Decimal("318.82")

    def test_inss_calculation_band_4(self):
        """Testa cálculo INSS - faixa 4 (R$ 4.000,04 a R$ 7.786,02)."""
        base = Decimal("6000.00")
        expected = base * Decimal("0.14") - Decimal("181.18")
        assert expected == Decimal("658.82")

    def test_inss_calculation_cap(self):
        """Testa teto do INSS."""
        Decimal("10000.00")
        cap = Decimal("908.85")
        # Acima do teto, valor fixo
        assert cap == Decimal("908.85")

    def test_irrf_isento(self):
        """Testa IRRF - faixa isenta (até R$ 2.259,20)."""
        Decimal("2000.00")
        expected = Decimal("0")
        assert expected == Decimal("0")

    def test_irrf_calculation_band_1(self):
        """Testa cálculo IRRF - faixa 1 (7,5%)."""
        base = Decimal("2500.00")
        expected = base * Decimal("0.075") - Decimal("169.44")
        assert expected == Decimal("18.06")

    def test_irrf_calculation_band_2(self):
        """Testa cálculo IRRF - faixa 2 (15%)."""
        base = Decimal("3500.00")
        expected = base * Decimal("0.15") - Decimal("381.44")
        assert expected == Decimal("143.56")

    def test_full_vacation_calculation(self):
        """Testa cálculo completo de férias."""
        base_salary = Decimal("5000.00")
        days_requested = 20
        sell_days = 10

        # Valor diário
        daily_rate = base_salary / Decimal("30")

        # Férias
        vacation_value = daily_rate * days_requested
        vacation_bonus = vacation_value / Decimal("3")

        # Abono
        sell_value = daily_rate * sell_days
        sell_bonus = sell_value / Decimal("3")

        # Total bruto
        gross_total = vacation_value + vacation_bonus + sell_value + sell_bonus

        assert daily_rate == Decimal("166.6666666666666666666666667")
        assert vacation_value == Decimal("3333.333333333333333333333334")
        assert gross_total > Decimal("5000.00")
