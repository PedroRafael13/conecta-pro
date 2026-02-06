"""Testes unitários para Models do módulo de Ponto Eletrônico."""

import pytest
from datetime import date, time, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from modules.hr.time_tracking.models import (
    TimeEntry,
    WorkSchedule,
    Overtime,
    TimeJustification,
    TimeSheet,
    EntryType,
    EntryStatus,
    RegistrationMethod,
    AnomalyType,
    ScheduleType,
    ScheduleStatus,
    DayOfWeek,
    OvertimeType,
    OvertimeStatus,
    OvertimeReason,
    CompensationType,
    JustificationType,
    JustificationStatus,
    JustificationCategory,
    TimeSheetStatus,
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
            registration_method=RegistrationMethod.APP,
        )

        assert entry.employee_id == "emp-001"
        assert entry.entry_type == EntryType.ENTRADA
        assert entry.status == EntryStatus.PENDENTE

    def test_calculate_difference_late(self):
        """Testa cálculo de atraso."""
        entry = TimeEntry(
            employee_id="emp-001",
            employee_name="João Silva",
            entry_date=date.today(),
            entry_time=time(8, 30),
            entry_type=EntryType.ENTRADA,
            expected_time=time(8, 0),
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
        entry.anomaly_type = AnomalyType.REGISTRO_DUPLICADO
        entry.anomaly_description = "Registro duplicado detectado"

        assert entry.anomaly_type == AnomalyType.REGISTRO_DUPLICADO
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

        assert entry.status == EntryStatus.APROVADO
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

        assert entry.is_night_entry is True


class TestWorkScheduleModel:
    """Testes para WorkSchedule."""

    def test_create_schedule_clt44h(self):
        """Testa criação de jornada CLT 44h."""
        schedule = WorkSchedule(
            name="Comercial Padrão",
            schedule_type=ScheduleType.CLT_44H,
            weekly_hours=2640,  # 44h em minutos
        )

        assert schedule.schedule_type == ScheduleType.CLT_44H
        assert schedule.weekly_hours == 2640

    def test_is_work_day(self):
        """Testa verificação de dia útil."""
        schedule = WorkSchedule(
            name="Comercial",
            schedule_type=ScheduleType.CLT_44H,
            weekly_schedule={
                "monday": {"start": "08:00", "end": "17:48"},
                "tuesday": {"start": "08:00", "end": "17:48"},
                "wednesday": {"start": "08:00", "end": "17:48"},
                "thursday": {"start": "08:00", "end": "17:48"},
                "friday": {"start": "08:00", "end": "17:48"},
            },
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
            weekly_hours=2160,  # 36h em minutos
        )

        assert schedule.schedule_type == ScheduleType.ESCALA_12X36

    def test_validate_clt_rules(self):
        """Testa validação de regras CLT."""
        schedule = WorkSchedule(
            name="Comercial",
            schedule_type=ScheduleType.CLT_44H,
            weekly_hours=2640,
            daily_hours=528,  # 8h48min
        )

        violations = schedule.validate_clt_rules()

        # Jornada válida não deve ter violações
        assert len(violations) == 0

    def test_time_bank(self):
        """Testa banco de horas."""
        schedule = WorkSchedule(
            name="Com Banco de Horas",
            schedule_type=ScheduleType.CLT_44H,
            has_time_bank=True,
            time_bank_balance_minutes=0,
        )

        # Adiciona crédito
        schedule.update_time_bank(60, "credit")
        assert schedule.time_bank_balance_minutes == 60

        # Adiciona débito
        schedule.update_time_bank(30, "debit")
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
            total_minutes=120,
            overtime_type=OvertimeType.HORA_EXTRA_50,
        )

        assert overtime.overtime_type == OvertimeType.HORA_EXTRA_50
        assert overtime.total_minutes == 120
        assert overtime.total_hours == 2.0

    def test_pre_approve_overtime(self):
        """Testa pré-aprovação de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            total_minutes=120,
            overtime_type=OvertimeType.HORA_EXTRA_50,
            requires_pre_approval=True,
        )

        overtime.pre_approve(
            approved_by_id="gestor-001",
            approved_by_name="Pedro Gestor",
        )

        assert overtime.status == OvertimeStatus.PRE_APROVADO

    def test_approve_overtime(self):
        """Testa aprovação de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            total_minutes=120,
            overtime_type=OvertimeType.HORA_EXTRA_50,
        )

        overtime.approve(
            approved_by_id="rh-001",
            approved_by_name="Maria RH",
            compensation_type=CompensationType.PAGAMENTO,
        )

        assert overtime.status == OvertimeStatus.APROVADO
        assert overtime.compensation_type == CompensationType.PAGAMENTO

    def test_calculate_overtime_value(self):
        """Testa cálculo de valor de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            total_minutes=120,
            overtime_type=OvertimeType.HORA_EXTRA_50,
            hourly_rate=Decimal("20.00"),
            overtime_50_minutes=120,
        )

        # 2h * R$20 * 1.5 = R$60
        expected_value = Decimal("60.00")
        assert overtime.calculated_value == expected_value

    def test_compensate_overtime(self):
        """Testa compensação de hora extra."""
        overtime = Overtime(
            employee_id="emp-001",
            employee_name="João Silva",
            overtime_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
            total_minutes=120,
            overtime_type=OvertimeType.HORA_EXTRA_50,
            status=OvertimeStatus.APROVADO,
            compensation_type=CompensationType.BANCO_HORAS,
        )

        overtime.compensate(
            compensation_date=date.today() + timedelta(days=7),
            compensation_minutes=120,
        )

        assert overtime.is_compensated is True


class TestTimeJustificationModel:
    """Testes para TimeJustification."""

    def test_create_medical_leave(self):
        """Testa criação de atestado médico."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.ATESTADO_MEDICO,
            title="Atestado médico - Gripe",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
        )

        assert justification.justification_type == JustificationType.ATESTADO_MEDICO
        assert justification.category == JustificationCategory.MEDICA
        assert justification.requires_medical_docs is True

    def test_submit_justification(self):
        """Testa submissão de justificativa."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.PROBLEMA_TRANSPORTE,
            title="Atraso por problema no metrô",
            start_date=date.today(),
            end_date=date.today(),
        )

        justification.submit()

        assert justification.status == JustificationStatus.SUBMETIDO
        assert justification.submitted_at is not None

    def test_approve_justification(self):
        """Testa aprovação de justificativa."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.PROBLEMA_TRANSPORTE,
            title="Atraso por problema no metrô",
            start_date=date.today(),
            end_date=date.today(),
            status=JustificationStatus.SUBMETIDO,
        )

        justification.approve(
            approved_by_id="gestor-001",
            approved_by_name="Pedro Gestor",
        )

        assert justification.status == JustificationStatus.APROVADO
        assert justification.is_approved is True

    def test_reject_justification(self):
        """Testa rejeição de justificativa."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.MOTIVO_PESSOAL,
            title="Assunto pessoal",
            start_date=date.today(),
            end_date=date.today(),
            status=JustificationStatus.SUBMETIDO,
        )

        justification.reject(
            rejected_by_id="gestor-001",
            rejected_by_name="Pedro Gestor",
            reason="Justificativa insuficiente",
        )

        assert justification.status == JustificationStatus.REJEITADO
        assert justification.rejection_reason == "Justificativa insuficiente"

    def test_add_attachment(self):
        """Testa adição de anexo."""
        justification = TimeJustification(
            employee_id="emp-001",
            employee_name="João Silva",
            justification_type=JustificationType.ATESTADO_MEDICO,
            title="Atestado médico",
            start_date=date.today(),
            end_date=date.today(),
        )

        attachment = {
            "name": "atestado.pdf",
            "url": "/uploads/atestado.pdf",
            "type": "application/pdf",
            "size": 1024,
        }

        justification.add_attachment(attachment)

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
        )

        assert sheet.can_close is True


class TestEnums:
    """Testes para Enums."""

    def test_entry_types(self):
        """Testa tipos de entrada."""
        assert EntryType.ENTRADA.value == "entrada"
        assert EntryType.SAIDA.value == "saida"
        assert EntryType.SAIDA_INTERVALO.value == "saida_intervalo"
        assert EntryType.RETORNO_INTERVALO.value == "retorno_intervalo"

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
        assert JustificationType.ATESTADO_MEDICO.value == "atestado_medico"
        assert JustificationType.FERIAS.value == "ferias"
        assert JustificationType.LICENCA_MATERNIDADE.value == "licenca_maternidade"
