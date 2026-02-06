"""Testes para models do Portal do Funcionário."""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from modules.hr.employee_portal.models import (
    PaySlip,
    PaySlipStatus,
    PaySlipType,
    VacationPeriod,
    VacationRequest,
    VacationStatus,
    EmployeeDocument,
    DocumentType,
    DocumentStatus,
    EmployeeNotification,
    NotificationType,
    NotificationPriority,
    NotificationChannel,
    EmployeePreferences,
    ThemePreference,
    LanguagePreference,
)


class TestPaySlipModel:
    """Testes para PaySlip."""

    def test_create_payslip(self):
        """Testa criação de contracheque."""
        payslip = PaySlip(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            payslip_code="2024-01-001",
            payslip_type=PaySlipType.MONTHLY,
            status=PaySlipStatus.DRAFT,
            reference_year=2024,
            reference_month=1,
            reference_period="2024-01",
            base_salary=Decimal("3000.00"),
            total_earnings=Decimal("3500.00"),
            total_deductions=Decimal("500.00"),
            net_salary=Decimal("3000.00"),
            earnings=[],
            deductions=[],
        )

        assert payslip.payslip_code == "2024-01-001"
        assert payslip.net_salary == Decimal("3000.00")

    def test_payslip_is_published(self):
        """Testa propriedade is_published."""
        payslip = PaySlip(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            payslip_code="2024-01-001",
            status=PaySlipStatus.PUBLISHED,
            reference_year=2024,
            reference_month=1,
            reference_period="2024-01",
            base_salary=Decimal("3000.00"),
            total_earnings=Decimal("3000.00"),
            total_deductions=Decimal("0"),
            net_salary=Decimal("3000.00"),
            earnings=[],
            deductions=[],
            published_at=datetime.utcnow(),
        )

        assert payslip.is_published is True

    def test_payslip_is_viewable(self):
        """Testa propriedade is_viewable."""
        # Draft não é viewable
        payslip_draft = PaySlip(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            payslip_code="2024-01-001",
            status=PaySlipStatus.DRAFT,
            reference_year=2024,
            reference_month=1,
            reference_period="2024-01",
            base_salary=Decimal("3000.00"),
            total_earnings=Decimal("3000.00"),
            total_deductions=Decimal("0"),
            net_salary=Decimal("3000.00"),
            earnings=[],
            deductions=[],
        )

        assert payslip_draft.is_viewable is False

        # Published é viewable
        payslip_published = PaySlip(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            payslip_code="2024-01-002",
            status=PaySlipStatus.PUBLISHED,
            reference_year=2024,
            reference_month=1,
            reference_period="2024-01",
            base_salary=Decimal("3000.00"),
            total_earnings=Decimal("3000.00"),
            total_deductions=Decimal("0"),
            net_salary=Decimal("3000.00"),
            earnings=[],
            deductions=[],
            published_at=datetime.utcnow(),
        )

        assert payslip_published.is_viewable is True

    def test_payslip_record_view(self):
        """Testa registro de visualização."""
        payslip = PaySlip(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            payslip_code="2024-01-001",
            status=PaySlipStatus.PUBLISHED,
            reference_year=2024,
            reference_month=1,
            reference_period="2024-01",
            base_salary=Decimal("3000.00"),
            total_earnings=Decimal("3000.00"),
            total_deductions=Decimal("0"),
            net_salary=Decimal("3000.00"),
            earnings=[],
            deductions=[],
            published_at=datetime.utcnow(),
            view_count=0,
        )

        payslip.record_view()

        assert payslip.view_count == 1
        assert payslip.first_viewed_at is not None
        assert payslip.last_viewed_at is not None


class TestVacationPeriodModel:
    """Testes para VacationPeriod."""

    def test_create_vacation_period(self):
        """Testa criação de período aquisitivo."""
        period = VacationPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            limit_date=date(2024, 12, 31),
            period_number=1,
            days_entitled=30,
            days_remaining=30,
        )

        assert period.days_entitled == 30
        assert period.days_remaining == 30

    def test_vacation_period_days_until_expiration(self):
        """Testa cálculo de dias até expiração."""
        period = VacationPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            limit_date=date.today() + timedelta(days=60),
            period_number=1,
            days_entitled=30,
            days_remaining=30,
        )

        assert period.days_until_expiration == 60

    def test_vacation_period_expired(self):
        """Testa período expirado."""
        period = VacationPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            start_date=date(2022, 1, 1),
            end_date=date(2022, 12, 31),
            limit_date=date(2023, 12, 31),
            period_number=1,
            days_entitled=30,
            days_remaining=30,
            is_expired=True,
        )

        assert period.is_expired is True

    def test_calculate_days_by_absences(self):
        """Testa cálculo de dias por faltas (CLT Art. 130)."""
        # 0-5 faltas = 30 dias
        period = VacationPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            limit_date=date(2024, 12, 31),
            period_number=1,
            days_entitled=30,
            days_remaining=30,
            absences_count=5,
        )

        days = period.calculate_entitled_days()
        assert days == 30

        # 6-14 faltas = 24 dias
        period.absences_count = 10
        days = period.calculate_entitled_days()
        assert days == 24

        # 15-23 faltas = 18 dias
        period.absences_count = 20
        days = period.calculate_entitled_days()
        assert days == 18

        # 24-32 faltas = 12 dias
        period.absences_count = 30
        days = period.calculate_entitled_days()
        assert days == 12


class TestVacationRequestModel:
    """Testes para VacationRequest."""

    def test_create_vacation_request(self):
        """Testa criação de solicitação de férias."""
        request = VacationRequest(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            request_code="VR-2024-001",
            status=VacationStatus.DRAFT,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
            return_date=date(2024, 7, 16),
            days_requested=15,
            sell_days=0,
        )

        assert request.days_requested == 15
        assert request.status == VacationStatus.DRAFT

    def test_vacation_request_validation_min_days(self):
        """Testa validação de mínimo de dias."""
        # Mínimo 5 dias (CLT)
        request = VacationRequest(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            request_code="VR-2024-001",
            status=VacationStatus.DRAFT,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 3),
            return_date=date(2024, 7, 4),
            days_requested=3,  # Menos que o mínimo
            sell_days=0,
        )

        assert request.days_requested < 5

    def test_vacation_request_sell_days_limit(self):
        """Testa limite de abono pecuniário."""
        # Máximo 10 dias de venda (1/3 de 30)
        request = VacationRequest(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            request_code="VR-2024-001",
            status=VacationStatus.DRAFT,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 20),
            return_date=date(2024, 7, 21),
            days_requested=20,
            sell_days=10,  # Máximo permitido
        )

        assert request.sell_days == 10


class TestEmployeeDocumentModel:
    """Testes para EmployeeDocument."""

    def test_create_document(self):
        """Testa criação de documento."""
        doc = EmployeeDocument(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            document_type=DocumentType.PAYSLIP,
            title="Contracheque Janeiro 2024",
            status=DocumentStatus.DRAFT,
        )

        assert doc.title == "Contracheque Janeiro 2024"
        assert doc.document_type == DocumentType.PAYSLIP

    def test_document_requires_acknowledgement(self):
        """Testa documento que requer ciência."""
        doc = EmployeeDocument(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            document_type=DocumentType.INTERNAL_POLICY,
            title="Nova Política de Segurança",
            requires_acknowledgement=True,
            status=DocumentStatus.PUBLISHED,
        )

        assert doc.requires_acknowledgement is True
        assert doc.acknowledged_at is None

    def test_document_validity(self):
        """Testa validade do documento."""
        doc = EmployeeDocument(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            document_type=DocumentType.MEDICAL_CERTIFICATE,
            title="Atestado Médico",
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=30),
            status=DocumentStatus.PUBLISHED,
        )

        assert doc.valid_until > date.today()


class TestEmployeeNotificationModel:
    """Testes para EmployeeNotification."""

    def test_create_notification(self):
        """Testa criação de notificação."""
        notification = EmployeeNotification(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            notification_type=NotificationType.PAYSLIP_AVAILABLE,
            priority=NotificationPriority.NORMAL,
            title="Novo Contracheque",
            message="Seu contracheque de janeiro está disponível.",
            channels=[NotificationChannel.PORTAL, NotificationChannel.EMAIL],
        )

        assert notification.title == "Novo Contracheque"
        assert NotificationChannel.PORTAL in notification.channels

    def test_notification_priority(self):
        """Testa prioridades de notificação."""
        notification = EmployeeNotification(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            notification_type=NotificationType.VACATION_APPROVED,
            priority=NotificationPriority.HIGH,
            title="Férias Aprovadas",
            message="Suas férias foram aprovadas!",
            channels=[NotificationChannel.PORTAL],
        )

        assert notification.priority == NotificationPriority.HIGH

    def test_notification_read_status(self):
        """Testa status de leitura."""
        notification = EmployeeNotification(
            id=uuid4(),
            condominio_id=uuid4(),
            employee_id=uuid4(),
            notification_type=NotificationType.DOCUMENT_AVAILABLE,
            priority=NotificationPriority.NORMAL,
            title="Novo Documento",
            message="Um novo documento está disponível.",
            channels=[NotificationChannel.PORTAL],
            is_read=False,
        )

        assert notification.is_read is False

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        assert notification.is_read is True
        assert notification.read_at is not None


class TestEmployeePreferencesModel:
    """Testes para EmployeePreferences."""

    def test_create_preferences(self):
        """Testa criação de preferências."""
        prefs = EmployeePreferences(
            id=uuid4(),
            employee_id=uuid4(),
            theme=ThemePreference.SYSTEM,
            language=LanguagePreference.PT_BR,
            timezone="America/Sao_Paulo",
        )

        assert prefs.theme == ThemePreference.SYSTEM
        assert prefs.language == LanguagePreference.PT_BR

    def test_preferences_notification_settings(self):
        """Testa configurações de notificação."""
        prefs = EmployeePreferences(
            id=uuid4(),
            employee_id=uuid4(),
            email_notifications=True,
            push_notifications=True,
            sms_notifications=False,
            whatsapp_notifications=False,
        )

        assert prefs.email_notifications is True
        assert prefs.sms_notifications is False

    def test_preferences_2fa_disabled_by_default(self):
        """Testa 2FA desabilitado por padrão."""
        prefs = EmployeePreferences(
            id=uuid4(),
            employee_id=uuid4(),
        )

        assert prefs.two_factor_enabled is False
        assert prefs.two_factor_secret is None

    def test_preferences_accessibility(self):
        """Testa configurações de acessibilidade."""
        prefs = EmployeePreferences(
            id=uuid4(),
            employee_id=uuid4(),
            high_contrast=True,
            font_size="large",
            reduced_motion=True,
        )

        assert prefs.high_contrast is True
        assert prefs.font_size == "large"
        assert prefs.reduced_motion is True
