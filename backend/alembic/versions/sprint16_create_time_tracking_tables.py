"""Sprint 16: Create time tracking tables (Ponto Eletrônico).

Revision ID: sprint16_time_tracking
Revises: sprint15_recruitment
Create Date: 2024-12-31

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint16_time_tracking"
down_revision: str | None = "sprint15_recruitment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabelas do módulo de Ponto Eletrônico."""

    # Tabela de Jornadas de Trabalho (WorkSchedule)
    op.create_table(
        "work_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo e status
        sa.Column("schedule_type", sa.String(50), nullable=False, server_default="CLT_44H"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ativo"),
        # Vínculo
        sa.Column("employee_id", sa.String(50), nullable=True, index=True),
        sa.Column("employee_name", sa.String(200), nullable=True),
        sa.Column("department_id", sa.String(50), nullable=True, index=True),
        sa.Column("department_name", sa.String(100), nullable=True),
        # Horários semanais (JSONB)
        sa.Column("weekly_schedule", JSONB, nullable=True),
        # Configurações de horas
        sa.Column("weekly_hours", sa.Integer, nullable=False, server_default="2640"),
        sa.Column("daily_hours", sa.Integer, nullable=False, server_default="528"),
        sa.Column("break_duration_minutes", sa.Integer, nullable=False, server_default="60"),
        # Tolerâncias
        sa.Column("tolerance_late_minutes", sa.Integer, nullable=False, server_default="5"),
        sa.Column("tolerance_early_minutes", sa.Integer, nullable=False, server_default="5"),
        sa.Column("tolerance_overtime_minutes", sa.Integer, nullable=False, server_default="10"),
        # Banco de horas
        sa.Column("has_time_bank", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("time_bank_balance_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("time_bank_expiration_months", sa.Integer, nullable=True, server_default="6"),
        # Configurações de intervalo
        sa.Column("flexible_break", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("min_break_minutes", sa.Integer, nullable=False, server_default="60"),
        sa.Column("max_break_minutes", sa.Integer, nullable=True),
        # Noturno
        sa.Column("has_night_shift", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("night_shift_start", sa.Time, nullable=True),
        sa.Column("night_shift_end", sa.Time, nullable=True),
        # Localização
        sa.Column("allowed_locations", JSONB, nullable=True),
        sa.Column("geolocation_required", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("geolocation_radius_meters", sa.Integer, nullable=True, server_default="100"),
        # Template
        sa.Column("is_template", sa.Boolean, nullable=False, server_default="false"),
        # Vigência
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        # Condomínio
        sa.Column("condominium_id", sa.String(50), nullable=True, index=True),
        sa.Column("condominium_name", sa.String(200), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by_id", sa.String(50), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Tabela de Registros de Ponto (TimeEntry)
    op.create_table(
        "time_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False, index=True),
        # Funcionário
        sa.Column("employee_id", sa.String(50), nullable=False, index=True),
        sa.Column("employee_name", sa.String(200), nullable=False),
        sa.Column("employee_registration", sa.String(50), nullable=True),
        sa.Column("employee_pis", sa.String(15), nullable=True),
        sa.Column("department_id", sa.String(50), nullable=True, index=True),
        sa.Column("department_name", sa.String(100), nullable=True),
        # Registro
        sa.Column("entry_date", sa.Date, nullable=False, index=True),
        sa.Column("entry_time", sa.Time, nullable=False),
        sa.Column("entry_type", sa.String(30), nullable=False),
        sa.Column("registration_method", sa.String(30), nullable=False, server_default="app"),
        # Status
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        # Horário esperado
        sa.Column("expected_time", sa.Time, nullable=True),
        sa.Column("difference_minutes", sa.Integer, nullable=True, server_default="0"),
        sa.Column("is_late", sa.Boolean, nullable=False, server_default="false"),
        # Localização
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("location_accuracy", sa.Float, nullable=True),
        sa.Column("location_address", sa.String(500), nullable=True),
        # Dispositivo
        sa.Column("device_id", sa.String(100), nullable=True),
        sa.Column("device_name", sa.String(200), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        # Biometria
        sa.Column("biometric_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("biometric_score", sa.Float, nullable=True),
        sa.Column("facial_image_url", sa.String(500), nullable=True),
        # Anomalias
        sa.Column("anomaly_type", sa.String(30), nullable=True),
        sa.Column("anomaly_description", sa.String(500), nullable=True),
        sa.Column("anomaly_resolved", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("anomaly_resolution", sa.Text, nullable=True),
        # Ajuste manual
        sa.Column("is_manual_entry", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("original_time", sa.Time, nullable=True),
        sa.Column("adjustment_reason", sa.Text, nullable=True),
        sa.Column("adjusted_by_id", sa.String(50), nullable=True),
        sa.Column("adjusted_by_name", sa.String(200), nullable=True),
        sa.Column("adjusted_at", sa.DateTime, nullable=True),
        # Aprovação
        sa.Column("requires_approval", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("approved_by_id", sa.String(50), nullable=True),
        sa.Column("approved_by_name", sa.String(200), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Noturno
        sa.Column("is_night_entry", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("night_hours_minutes", sa.Integer, nullable=False, server_default="0"),
        # Jornada
        sa.Column("work_schedule_id", sa.String(50), nullable=True),
        # REP
        sa.Column("rep_nsr", sa.String(50), nullable=True),
        # Condomínio
        sa.Column("condominium_id", sa.String(50), nullable=True, index=True),
        sa.Column("condominium_name", sa.String(200), nullable=True),
        # Observações
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by_id", sa.String(50), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Índices compostos para time_entries
    op.create_index("ix_time_entries_employee_date", "time_entries", ["employee_id", "entry_date"])

    # Tabela de Horas Extras (Overtime)
    op.create_table(
        "overtime_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False, index=True),
        # Funcionário
        sa.Column("employee_id", sa.String(50), nullable=False, index=True),
        sa.Column("employee_name", sa.String(200), nullable=False),
        sa.Column("employee_registration", sa.String(50), nullable=True),
        sa.Column("department_id", sa.String(50), nullable=True, index=True),
        sa.Column("department_name", sa.String(100), nullable=True),
        # Data e horários
        sa.Column("overtime_date", sa.Date, nullable=False, index=True),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=False),
        sa.Column("total_minutes", sa.Integer, nullable=False),
        # Tipo
        sa.Column("overtime_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        # Percentuais
        sa.Column("overtime_50_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("overtime_100_minutes", sa.Integer, nullable=False, server_default="0"),
        # Noturno
        sa.Column("night_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("night_bonus_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        # Motivo
        sa.Column("reason", sa.String(30), nullable=True),
        sa.Column("reason_description", sa.Text, nullable=True),
        # Valores
        sa.Column("hourly_rate", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("calculated_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        # Pré-aprovação
        sa.Column("requires_pre_approval", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("pre_approved_by_id", sa.String(50), nullable=True),
        sa.Column("pre_approved_by_name", sa.String(200), nullable=True),
        sa.Column("pre_approved_at", sa.DateTime, nullable=True),
        # Aprovação
        sa.Column("approved_by_id", sa.String(50), nullable=True),
        sa.Column("approved_by_name", sa.String(200), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Rejeição
        sa.Column("rejected_by_id", sa.String(50), nullable=True),
        sa.Column("rejected_by_name", sa.String(200), nullable=True),
        sa.Column("rejected_at", sa.DateTime, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Compensação
        sa.Column("compensation_type", sa.String(20), nullable=True),
        sa.Column("is_compensated", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("compensation_date", sa.Date, nullable=True),
        sa.Column("compensation_minutes", sa.Integer, nullable=True),
        # Banco de horas
        sa.Column("time_bank_minutes", sa.Integer, nullable=True),
        # Pagamento
        sa.Column("is_paid", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("payment_date", sa.Date, nullable=True),
        sa.Column("payroll_reference", sa.String(100), nullable=True),
        # Vínculo
        sa.Column("time_entry_ids", JSONB, nullable=True),
        sa.Column("time_sheet_id", sa.String(50), nullable=True),
        # Condomínio
        sa.Column("condominium_id", sa.String(50), nullable=True, index=True),
        sa.Column("condominium_name", sa.String(200), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by_id", sa.String(50), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Tabela de Justificativas (TimeJustification)
    op.create_table(
        "time_justifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False, index=True),
        # Funcionário
        sa.Column("employee_id", sa.String(50), nullable=False, index=True),
        sa.Column("employee_name", sa.String(200), nullable=False),
        sa.Column("employee_registration", sa.String(50), nullable=True),
        sa.Column("department_id", sa.String(50), nullable=True, index=True),
        sa.Column("department_name", sa.String(100), nullable=True),
        # Tipo e categoria
        sa.Column("justification_type", sa.String(50), nullable=False),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="rascunho"),
        # Título e descrição
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("detailed_reason", sa.Text, nullable=True),
        # Período
        sa.Column("start_date", sa.Date, nullable=False, index=True),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("start_time", sa.Time, nullable=True),
        sa.Column("end_time", sa.Time, nullable=True),
        sa.Column("is_full_day", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("days_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("hours_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("minutes_justified", sa.Integer, nullable=False, server_default="0"),
        # Anexos
        sa.Column("has_attachments", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("attachments", JSONB, nullable=True),
        # Informações médicas
        sa.Column("cid_code", sa.String(10), nullable=True),
        sa.Column("cid_description", sa.String(200), nullable=True),
        sa.Column("medical_certificate_number", sa.String(50), nullable=True),
        sa.Column("doctor_name", sa.String(200), nullable=True),
        sa.Column("doctor_crm", sa.String(20), nullable=True),
        sa.Column("clinic_name", sa.String(200), nullable=True),
        # Registros vinculados
        sa.Column("time_entry_ids", JSONB, nullable=True),
        # Jornada
        sa.Column("work_schedule_id", sa.String(50), nullable=True),
        # Análise
        sa.Column("analyzed_by_id", sa.String(50), nullable=True),
        sa.Column("analyzed_by_name", sa.String(200), nullable=True),
        sa.Column("analyzed_at", sa.DateTime, nullable=True),
        # Aprovação
        sa.Column("requires_approval", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("approved_by_id", sa.String(50), nullable=True),
        sa.Column("approved_by_name", sa.String(200), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Níveis de aprovação
        sa.Column("approval_level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("max_approval_level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("approval_history", JSONB, nullable=True),
        # Rejeição
        sa.Column("rejected_by_id", sa.String(50), nullable=True),
        sa.Column("rejected_by_name", sa.String(200), nullable=True),
        sa.Column("rejected_at", sa.DateTime, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Aprovação parcial
        sa.Column("partial_approved_days", sa.Integer, nullable=True),
        sa.Column("partial_approved_minutes", sa.Integer, nullable=True),
        # Impacto
        sa.Column("grants_paid_leave", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("affects_dsr", sa.Boolean, nullable=False, server_default="true"),
        # Prazo
        sa.Column("deadline_for_submission", sa.DateTime, nullable=True),
        sa.Column("is_late_submission", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("late_submission_days", sa.Integer, nullable=False, server_default="0"),
        # Verificação RH
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("verified_by_id", sa.String(50), nullable=True),
        sa.Column("verified_by_name", sa.String(200), nullable=True),
        sa.Column("verified_at", sa.DateTime, nullable=True),
        # Submissão
        sa.Column("submitted_at", sa.DateTime, nullable=True),
        # Condomínio
        sa.Column("condominium_id", sa.String(50), nullable=True, index=True),
        sa.Column("condominium_name", sa.String(200), nullable=True),
        # Observações
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by_id", sa.String(50), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Tabela de Folha de Ponto (TimeSheet)
    op.create_table(
        "time_sheets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False, index=True),
        # Referência
        sa.Column("reference_month", sa.Integer, nullable=False),
        sa.Column("reference_year", sa.Integer, nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        # Funcionário
        sa.Column("employee_id", sa.String(50), nullable=False, index=True),
        sa.Column("employee_name", sa.String(200), nullable=False),
        sa.Column("employee_registration", sa.String(50), nullable=True),
        sa.Column("employee_cpf", sa.String(14), nullable=True),
        sa.Column("employee_pis", sa.String(15), nullable=True),
        sa.Column("department_id", sa.String(50), nullable=True, index=True),
        sa.Column("department_name", sa.String(100), nullable=True),
        sa.Column("position_name", sa.String(100), nullable=True),
        # Status
        sa.Column("status", sa.String(20), nullable=False, server_default="aberto"),
        # Jornada
        sa.Column("work_schedule_id", sa.String(50), nullable=True),
        sa.Column("work_schedule_name", sa.String(200), nullable=True),
        sa.Column("weekly_hours_expected", sa.Integer, nullable=False, server_default="2640"),
        # Dias
        sa.Column("total_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("work_days_expected", sa.Integer, nullable=False, server_default="0"),
        sa.Column("work_days_worked", sa.Integer, nullable=False, server_default="0"),
        sa.Column("absent_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("justified_absent_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("unjustified_absent_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("vacation_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("holiday_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("leave_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("medical_leave_days", sa.Integer, nullable=False, server_default="0"),
        # Horas (em minutos)
        sa.Column("hours_expected_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("hours_worked_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("hours_balance_minutes", sa.Integer, nullable=False, server_default="0"),
        # Horas extras
        sa.Column("overtime_50_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("overtime_100_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("overtime_total_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("overtime_approved_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("overtime_pending_minutes", sa.Integer, nullable=False, server_default="0"),
        # Noturno
        sa.Column("night_hours_minutes", sa.Integer, nullable=False, server_default="0"),
        # Atrasos
        sa.Column("late_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("early_departure_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("late_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("early_departure_count", sa.Integer, nullable=False, server_default="0"),
        # Intervalos
        sa.Column("break_expected_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("break_actual_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("break_irregular_count", sa.Integer, nullable=False, server_default="0"),
        # Banco de horas
        sa.Column("time_bank_previous_balance", sa.Integer, nullable=False, server_default="0"),
        sa.Column("time_bank_credits", sa.Integer, nullable=False, server_default="0"),
        sa.Column("time_bank_debits", sa.Integer, nullable=False, server_default="0"),
        sa.Column("time_bank_current_balance", sa.Integer, nullable=False, server_default="0"),
        sa.Column("time_bank_expiring_minutes", sa.Integer, nullable=False, server_default="0"),
        # DSR
        sa.Column("dsr_entitled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("dsr_lost_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("dsr_lost_reason", sa.Text, nullable=True),
        # Valores
        sa.Column("hourly_rate", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("overtime_50_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("overtime_100_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("night_additional_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_additional_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_deduction_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        # Ocorrências
        sa.Column("total_entries", sa.Integer, nullable=False, server_default="0"),
        sa.Column("anomaly_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("anomaly_resolved_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("justification_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("justification_approved_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("justification_pending_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("manual_entries_count", sa.Integer, nullable=False, server_default="0"),
        # Resumo diário
        sa.Column("daily_summary", JSONB, nullable=True),
        sa.Column("has_pending_issues", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("pending_issues", JSONB, nullable=True),
        # Revisão
        sa.Column("reviewed_by_id", sa.String(50), nullable=True),
        sa.Column("reviewed_by_name", sa.String(200), nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        # Aprovação funcionário
        sa.Column("approved_by_employee", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("employee_approved_at", sa.DateTime, nullable=True),
        # Aprovação gestor
        sa.Column("approved_by_manager", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("manager_id", sa.String(50), nullable=True),
        sa.Column("manager_name", sa.String(200), nullable=True),
        sa.Column("manager_approved_at", sa.DateTime, nullable=True),
        # Aprovação RH
        sa.Column("approved_by_hr", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("hr_approver_id", sa.String(50), nullable=True),
        sa.Column("hr_approver_name", sa.String(200), nullable=True),
        sa.Column("hr_approved_at", sa.DateTime, nullable=True),
        # Fechamento
        sa.Column("closed_at", sa.DateTime, nullable=True),
        sa.Column("closed_by_id", sa.String(50), nullable=True),
        sa.Column("closed_by_name", sa.String(200), nullable=True),
        # Folha de pagamento
        sa.Column("sent_to_payroll_at", sa.DateTime, nullable=True),
        sa.Column("payroll_reference", sa.String(100), nullable=True),
        sa.Column("payroll_batch_id", sa.String(50), nullable=True),
        # Condomínio
        sa.Column("condominium_id", sa.String(50), nullable=True, index=True),
        sa.Column("condominium_name", sa.String(200), nullable=True),
        # Observações
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("internal_notes", sa.Text, nullable=True),
        # Cálculo
        sa.Column("last_calculated_at", sa.DateTime, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by_id", sa.String(50), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )

    # Índice único para folha de ponto por funcionário/mês
    op.create_index(
        "ix_time_sheets_employee_period",
        "time_sheets",
        ["employee_id", "reference_month", "reference_year"],
        unique=True,
    )


def downgrade() -> None:
    """Remove tabelas do módulo de Ponto Eletrônico."""
    op.drop_index("ix_time_sheets_employee_period", table_name="time_sheets")
    op.drop_table("time_sheets")
    op.drop_table("time_justifications")
    op.drop_table("overtime_records")
    op.drop_index("ix_time_entries_employee_date", table_name="time_entries")
    op.drop_table("time_entries")
    op.drop_table("work_schedules")
