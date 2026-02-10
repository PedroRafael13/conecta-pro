"""Testes unitários para Models do módulo de Ponto Eletrônico."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.hr.time_tracking.models import (
    AnomalyType,
    CompensationType,
    DayOfWeek,
    EntryStatus,
    EntryType,
    JustificationCategory,
    JustificationStatus,
    JustificationType,
    Overtime,
    OvertimeReason,
    OvertimeStatus,
    OvertimeType,
    RegistrationMethod,
    ScheduleStatus,
    ScheduleType,
    TimeEntry,
    TimeJustification,
    TimeSheet,
    TimeSheetStatus,
    WorkSchedule,
)


class TestTimeEntryModel:
    """Testes para TimeEntry."""

    def test_create_time_entry(self):
        """Testa criação de registro de ponto."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(8, 0),
            entry_type=EntryType.ENTRADA,
            registration_method=RegistrationMethod.APP_MOBILE,
        )

        assert entry.employee_id == "emp-001"
        assert entry.entry_type == EntryType.ENTRADA

    def test_calculate_difference_late(self):
        """Testa cálculo de atraso."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(8, 30),
            entry_type=EntryType.ENTRADA,
            expected_time=time(8, 0),
            tolerance_minutes=10,
        )

        entry.calculate_difference()

        assert entry.difference_minutes == 30
        assert entry.is_late is True

    def test_calculate_difference_early(self):
        """Testa cálculo de chegada adiantada."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(7, 45),
            entry_type=EntryType.ENTRADA,
            expected_time=time(8, 0),
            tolerance_minutes=10,
        )

        entry.calculate_difference()

        assert entry.difference_minutes == -15
        assert entry.is_late is False

    def test_detect_anomaly_duplicate(self):
        """Testa detecção de anomalia de duplicata."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(8, 0),
            entry_type=EntryType.ENTRADA,
        )

        # Simula detecção manual
        entry.anomaly_type = AnomalyType.MULTIPLAS_MARCACOES
        entry.anomaly_description = "Registro duplicado detectado"

        assert entry.anomaly_type == AnomalyType.MULTIPLAS_MARCACOES
        assert entry.has_anomaly is True

    def test_mark_as_manual(self):
        """Testa marcação como ajuste manual."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(8, 0),
            entry_type=EntryType.ENTRADA,
        )

        entry.mark_as_manual(
            adjusted_by_id="rh-001",
            adjusted_by_name="Maria RH",
            reason="Correção de horário",
        )

        assert entry.is_manual_entry is True
        assert entry.adjusted_by_id == "rh-001"
        assert entry.requires_approval is True

    def test_approve_entry(self):
        """Testa aprovação de registro."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(8, 0),
            entry_type=EntryType.ENTRADA,
            requires_approval=True,
        )

        entry.approve(
            approved_by_id="gestor-001",
            approved_by_name="Pedro Gestor",
        )

        assert entry.status == EntryStatus.CONFIRMADO
        assert entry.approved_by_id == "gestor-001"

    def test_calculate_night_hours(self):
        """Testa cálculo de horas noturnas."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(23, 0),
            entry_type=EntryType.ENTRADA,
        )

        entry.calculate_night_hours()

        assert entry.is_night_shift is True


class TestWorkScheduleModel:
    """Testes para WorkSchedule."""

    def test_create_schedule_clt44h(self):
        """Testa criação de jornada CLT 44h."""
        schedule = WorkSchedule(
            name="Comercial Padrão",
            schedule_type=ScheduleType.CLT_44H,
            weekly_hours_minutes=2640,  # 44h em minutos
        )

        assert schedule.schedule_type == ScheduleType.CLT_44H
        assert schedule.weekly_hours_minutes == 2640

    def test_is_work_day(self):
        """Testa verificação de dia útil."""
        schedule = WorkSchedule(
            name="Comercial",
            schedule_type=ScheduleType.CLT_44H,
            daily_schedule={
                "segunda": {"entry": "08:00", "exit": "17:48"},
                "terca": {"entry": "08:00", "exit": "17:48"},
                "quarta": {"entry": "08:00", "exit": "17:48"},
                "quinta": {"entry": "08:00", "exit": "17:48"},
                "sexta": {"entry": "08:00", "exit": "17:48"},
            },
            work_days=["segunda", "terca", "quarta", "quinta", "sexta"],
        )

        # Segunda-feira = dia útil
        monday = date(2024, 12, 30)
        assert schedule.is_work_day(monday) is True

        # Domingo = folga
        sunday = date(2024, 12, 29)
        assert schedule.is_work_day(sunday) is False

    def test_schedule_12x36(self):
        """Testa jornada 12x36."""
        schedule = WorkSchedule(
            name="12x36",
            schedule_type=ScheduleType.ESCALA_12X36,
            weekly_hours_minutes=2160,  # 36h em minutos
        )

        assert schedule.schedule_type == ScheduleType.ESCALA_12X36

    def test_validate_clt_rules(self):
        """Testa validação de regras CLT."""
        schedule = WorkSchedule(
            name="Comercial",
            schedule_type=ScheduleType.CLT_44H,
            weekly_hours_minutes=2640,
            daily_hours_minutes=528,  # 8h48min
            max_daily_hours_minutes=528,
            min_rest_between_shifts_hours=11,
            break_duration_minutes=60,
        )

        violations = schedule.validate_clt_rules()

        # Jornada válida não deve ter violações
        assert len(violations) == 0

    def test_time_bank(self):
        """Testa banco de horas."""
        schedule = WorkSchedule(
            name="Com Banco de Horas",
            schedule_type=ScheduleType.CLT_44H,
            use_time_bank=True,
            time_bank_balance_minutes=0,
            time_bank_max_positive_hours=120,
            time_bank_max_negative_hours=40,
        )

        # Adiciona crédito
        schedule.update_time_bank(60)
        assert schedule.time_bank_balance_minutes == 60

        # Adiciona débito
        schedule.update_time_bank(-30)
        assert schedule.time_bank_balance_minutes == 30


class TestOvertimeModel:
    """Testes para Overtime."""

    def test_create_overtime_50(self):
        """Testa criação de hora extra 50%."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            duration_minutes=120,
            net_duration_minutes=120,
            break_minutes=0,
            overtime_type=OvertimeType.HORA_EXTRA_50,
        )

        assert overtime.overtime_type == OvertimeType.HORA_EXTRA_50
        assert overtime.duration_minutes == 120
        assert overtime.duration_hours == 2.0

    def test_pre_approve_overtime(self):
        """Testa pré-aprovação de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            duration_minutes=120,
            net_duration_minutes=120,
            break_minutes=0,
            overtime_type=OvertimeType.HORA_EXTRA_50,
        )

        overtime.pre_approve(
            approved_by_id="gestor-001",
            approved_by_name="Pedro Gestor",
        )

        assert overtime.is_pre_approved is True

    def test_approve_overtime(self):
        """Testa aprovação de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            duration_minutes=120,
            net_duration_minutes=120,
            break_minutes=0,
            overtime_type=OvertimeType.HORA_EXTRA_50,
        )

        overtime.approve(
            approved_by_id="rh-001",
            approved_by_name="Maria RH",
        )

        assert overtime.status == OvertimeStatus.APROVADA
        assert overtime.approved_by_id == "rh-001"

    def test_calculate_overtime_value(self):
        """Testa cálculo de valor de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            duration_minutes=120,
            net_duration_minutes=120,
            break_minutes=0,
            night_minutes=0,
            overtime_type=OvertimeType.HORA_EXTRA_50,
            hourly_rate=Decimal("20.00"),
        )

        assert overtime.total_value is not None

    def test_compensate_overtime(self):
        """Testa compensação de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            duration_minutes=120,
            net_duration_minutes=120,
            break_minutes=0,
            night_minutes=0,
            compensated_minutes=0,
            remaining_minutes=120,
            overtime_type=OvertimeType.HORA_EXTRA_50,
            status=OvertimeStatus.APROVADA,
            compensation_type=CompensationType.FOLGA,
        )

        overtime.compensate(
            compensation_type=CompensationType.FOLGA,
            compensation_date=date.today() + timedelta(days=7),
            minutes=120,
        )

        assert overtime.is_compensated is True


class TestTimeJustificationModel:
    """Testes para TimeJustification."""

    def test_create_medical_leave(self):
        """Testa criação de atestado médico."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.LICENCA_MEDICA,
            title="Atestado médico - Gripe",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
        )

        assert justification.justification_type == JustificationType.LICENCA_MEDICA
        assert justification.category == JustificationCategory.SAUDE
        assert justification.requires_medical_docs is True

    def test_submit_justification(self):
        """Testa submissão de justificativa."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.TRANSPORTE,
            title="Atraso por problema no metrô",
            start_date=date.today(),
            end_date=date.today(),
        )

        justification.submit()

        assert justification.status == JustificationStatus.PENDENTE
        assert justification.submitted_at is not None

    def test_approve_justification(self):
        """Testa aprovação de justificativa."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.TRANSPORTE,
            title="Atraso por problema no metrô",
            start_date=date.today(),
            end_date=date.today(),
            status=JustificationStatus.PENDENTE,
        )

        justification.approve(
            approved_by_id="gestor-001",
            approved_by_name="Pedro Gestor",
        )

        assert justification.status == JustificationStatus.APROVADA
        assert justification.is_approved is True

    def test_reject_justification(self):
        """Testa rejeição de justificativa."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.OUTRO,
            title="Assunto pessoal",
            start_date=date.today(),
            end_date=date.today(),
            status=JustificationStatus.PENDENTE,
        )

        justification.reject(
            rejected_by_id="gestor-001",
            rejected_by_name="Pedro Gestor",
            reason="Justificativa insuficiente",
        )

        assert justification.status == JustificationStatus.REJEITADA
        assert justification.rejection_reason == "Justificativa insuficiente"

    def test_add_attachment(self):
        """Testa adição de anexo."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.LICENCA_MEDICA,
            title="Atestado médico",
            start_date=date.today(),
            end_date=date.today(),
        )

        justification.add_attachment(
            name="atestado.pdf",
            url="/uploads/atestado.pdf",
            file_type="application/pdf",
            size=1024,
        )

        assert justification.has_attachments is True
        assert len(justification.attachments) == 1


class TestTimeSheetModel:
    """Testes para TimeSheet."""

    def test_create_time_sheet(self):
        """Testa criação de folha de ponto."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
            status=TimeSheetStatus.ABERTO,
        )

        assert sheet.reference_month == 12
        assert sheet.reference_year == 2024
        assert sheet.status == TimeSheetStatus.ABERTO
        assert sheet.period_display == "Dezembro/2024"

    def test_calculate_totals(self):
        """Testa cálculo de totais."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
            hours_worked_minutes=10560,  # 176h
            hours_expected_minutes=10560,
            overtime_50_minutes=120,
            overtime_100_minutes=60,
            time_bank_previous_balance=0,
            time_bank_credits=0,
            time_bank_debits=0,
            anomaly_count=0,
            anomaly_resolved_count=0,
            justification_pending_count=0,
            overtime_pending_minutes=0,
            late_minutes=0,
            early_departure_minutes=0,
            unjustified_absent_days=0,
        )

        sheet.calculate_totals()

        assert sheet.hours_worked == 176.0
        assert sheet.overtime_total_minutes == 180

    def test_employee_approve(self):
        """Testa aprovação do funcionário."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
        )

        sheet.employee_approve()

        assert sheet.approved_by_employee is True
        assert sheet.employee_approved_at is not None

    def test_manager_approve(self):
        """Testa aprovação do gestor."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
            approved_by_employee=True,
        )

        sheet.manager_approve(
            manager_id="gestor-001",
            manager_name="Pedro Gestor",
        )

        assert sheet.approved_by_manager is True
        assert sheet.manager_id == "gestor-001"

    def test_close_sheet(self):
        """Testa fechamento de folha."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
            approved_by_employee=True,
            approved_by_manager=True,
            approved_by_hr=True,
        )

        sheet.close(
            closed_by_id="rh-001",
            closed_by_name="Maria RH",
        )

        assert sheet.status == TimeSheetStatus.FECHADO
        assert sheet.closed_at is not None

    def test_send_to_payroll(self):
        """Testa envio para folha de pagamento."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
            status=TimeSheetStatus.FECHADO,
        )

        sheet.send_to_payroll(
            payroll_reference="FP-2024-12-001",
        )

        assert sheet.status == TimeSheetStatus.ENVIADO_FOLHA
        assert sheet.payroll_reference == "FP-2024-12-001"

    def test_fully_approved(self):
        """Testa verificação de aprovação completa."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
            approved_by_employee=True,
            approved_by_manager=True,
            approved_by_hr=True,
        )

        assert sheet.is_fully_approved is True

    def test_can_close(self):
        """Testa verificação se pode fechar."""
        sheet = TimeSheet(
            employee_id="emp-001",
            employee_name="João Silva",
            reference_month=12,
            reference_year=2024,
            approved_by_employee=True,
            approved_by_manager=True,
            approved_by_hr=True,
            has_pending_issues=False,
            status=TimeSheetStatus.APROVADO,
        )

        assert sheet.can_close is True


class TestEnums:
    """Testes para Enums."""

    def test_entry_types(self):
        """Testa tipos de entrada."""
        assert EntryType.ENTRADA.value == "entrada"
        assert EntryType.SAIDA.value == "saida"
        assert EntryType.INICIO_INTERVALO.value == "inicio_intervalo"
        assert EntryType.FIM_INTERVALO.value == "fim_intervalo"

    def test_schedule_types(self):
        """Testa tipos de jornada."""
        assert ScheduleType.CLT_44H.value == "clt_44h"
        assert ScheduleType.ESCALA_12X36.value == "escala_12x36"
        assert ScheduleType.ESCALA_6X1.value == "escala_6x1"

    def test_overtime_types(self):
        """Testa tipos de hora extra."""
        assert OvertimeType.HORA_EXTRA_50.value == "hora_extra_50"
        assert OvertimeType.HORA_EXTRA_100.value == "hora_extra_100"

    def test_justification_types(self):
        """Testa tipos de justificativa."""
        assert JustificationType.LICENCA_MEDICA.value == "licenca_medica"
        assert JustificationType.FALTA.value == "falta"
        assert JustificationType.LICENCA_MATERNIDADE.value == "licenca_maternidade"
