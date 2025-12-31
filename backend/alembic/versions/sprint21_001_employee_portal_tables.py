"""Sprint 21 - Portal do Funcionário: tabelas base.

Revision ID: sprint21_001
Revises: sprint20_003
Create Date: 2025-01-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'sprint21_001'
down_revision: Union[str, None] = 'sprint20_003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create employee portal tables."""

    # ============================================================
    # CONTRACHEQUES (PaySlip)
    # ============================================================
    op.create_table(
        'hr_payslips',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Identificação
        sa.Column('payslip_code', sa.String(50), nullable=False),
        sa.Column('payslip_type', sa.String(30), nullable=False, server_default='monthly'),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),

        # Período
        sa.Column('reference_year', sa.Integer, nullable=False),
        sa.Column('reference_month', sa.Integer, nullable=False),
        sa.Column('reference_period', sa.String(7), nullable=False),  # YYYY-MM
        sa.Column('payment_date', sa.Date, nullable=True),
        sa.Column('competence_start', sa.Date, nullable=True),
        sa.Column('competence_end', sa.Date, nullable=True),

        # Valores
        sa.Column('base_salary', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_earnings', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_deductions', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('net_salary', sa.Numeric(12, 2), nullable=False, server_default='0'),

        # Detalhes (JSONB)
        sa.Column('earnings', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('deductions', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('informative', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('bank_info', postgresql.JSONB, nullable=True),

        # Bases de cálculo
        sa.Column('inss_base', sa.Numeric(12, 2), nullable=True),
        sa.Column('inss_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('irrf_base', sa.Numeric(12, 2), nullable=True),
        sa.Column('irrf_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('fgts_base', sa.Numeric(12, 2), nullable=True),
        sa.Column('fgts_value', sa.Numeric(12, 2), nullable=True),

        # Visualização
        sa.Column('first_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('view_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('download_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_download_at', sa.DateTime(timezone=True), nullable=True),

        # Ciência
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by_ip', sa.String(50), nullable=True),

        # Contestação
        sa.Column('contested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('contest_reason', sa.Text, nullable=True),
        sa.Column('contest_resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('contest_resolution', sa.Text, nullable=True),

        # PDF
        sa.Column('pdf_path', sa.String(500), nullable=True),
        sa.Column('pdf_generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pdf_hash', sa.String(64), nullable=True),

        # Publicação
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Integração
        sa.Column('external_id', sa.String(100), nullable=True),
        sa.Column('source_system', sa.String(50), nullable=True),
        sa.Column('import_batch_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Auditoria
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index('ix_hr_payslips_employee', 'hr_payslips', ['employee_id'])
    op.create_index('ix_hr_payslips_condominio', 'hr_payslips', ['condominio_id'])
    op.create_index('ix_hr_payslips_period', 'hr_payslips', ['reference_year', 'reference_month'])
    op.create_index('ix_hr_payslips_status', 'hr_payslips', ['status'])
    op.create_unique_constraint('uq_hr_payslips_code', 'hr_payslips', ['condominio_id', 'payslip_code'])

    # ============================================================
    # PERÍODOS AQUISITIVOS DE FÉRIAS
    # ============================================================
    op.create_table(
        'hr_vacation_periods',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Período aquisitivo
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('period_number', sa.Integer, nullable=False),

        # Direito
        sa.Column('days_entitled', sa.Integer, nullable=False, server_default='30'),
        sa.Column('absences_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('days_lost', sa.Integer, nullable=False, server_default='0'),

        # Uso
        sa.Column('days_used', sa.Integer, nullable=False, server_default='0'),
        sa.Column('days_sold', sa.Integer, nullable=False, server_default='0'),
        sa.Column('days_remaining', sa.Integer, nullable=False, server_default='30'),

        # Limite concessivo
        sa.Column('limit_date', sa.Date, nullable=False),
        sa.Column('is_expired', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('is_fully_used', sa.Boolean, nullable=False, server_default='false'),

        # Auditoria
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index('ix_hr_vacation_periods_employee', 'hr_vacation_periods', ['employee_id'])
    op.create_index('ix_hr_vacation_periods_dates', 'hr_vacation_periods', ['start_date', 'end_date'])

    # ============================================================
    # SOLICITAÇÕES DE FÉRIAS
    # ============================================================
    op.create_table(
        'hr_vacation_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('request_code', sa.String(50), nullable=False),

        # Datas
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('return_date', sa.Date, nullable=False),

        # Dias
        sa.Column('days_requested', sa.Integer, nullable=False),
        sa.Column('sell_days', sa.Integer, nullable=False, server_default='0'),
        sa.Column('advance_13th', sa.Boolean, nullable=False, server_default='false'),

        # Valores calculados
        sa.Column('gross_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('net_value', sa.Numeric(12, 2), nullable=True),
        sa.Column('calculation_details', postgresql.JSONB, nullable=True),

        # Aprovação
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('manager_approved', sa.Boolean, nullable=True),
        sa.Column('manager_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('manager_approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('manager_notes', sa.Text, nullable=True),

        sa.Column('hr_approved', sa.Boolean, nullable=True),
        sa.Column('hr_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hr_approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('hr_notes', sa.Text, nullable=True),

        # Rejeição
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Cancelamento
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text, nullable=True),

        # Interrupção
        sa.Column('interrupted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interruption_reason', sa.Text, nullable=True),
        sa.Column('actual_end_date', sa.Date, nullable=True),

        # Observações
        sa.Column('employee_notes', sa.Text, nullable=True),
        sa.Column('internal_notes', sa.Text, nullable=True),

        # Auditoria
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index('ix_hr_vacation_requests_employee', 'hr_vacation_requests', ['employee_id'])
    op.create_index('ix_hr_vacation_requests_status', 'hr_vacation_requests', ['status'])
    op.create_index('ix_hr_vacation_requests_dates', 'hr_vacation_requests', ['start_date', 'end_date'])
    op.create_unique_constraint('uq_hr_vacation_requests_code', 'hr_vacation_requests', ['condominio_id', 'request_code'])
    op.create_foreign_key('fk_vacation_request_period', 'hr_vacation_requests', 'hr_vacation_periods', ['period_id'], ['id'])

    # ============================================================
    # DOCUMENTOS DO FUNCIONÁRIO
    # ============================================================
    op.create_table(
        'hr_employee_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Identificação
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),

        # Arquivo
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_name', sa.String(200), nullable=True),
        sa.Column('file_size', sa.BigInteger, nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('file_hash', sa.String(64), nullable=True),

        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('is_published', sa.Boolean, nullable=False, server_default='false'),

        # Validade
        sa.Column('valid_from', sa.Date, nullable=True),
        sa.Column('valid_until', sa.Date, nullable=True),
        sa.Column('is_expired', sa.Boolean, nullable=False, server_default='false'),

        # Ciência
        sa.Column('requires_acknowledgement', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by_ip', sa.String(50), nullable=True),
        sa.Column('acknowledged_device', sa.String(500), nullable=True),

        # Assinatura
        sa.Column('requires_signature', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('signed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('signature_hash', sa.String(256), nullable=True),
        sa.Column('signature_certificate', sa.Text, nullable=True),

        # Visualização
        sa.Column('view_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('first_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('download_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_download_at', sa.DateTime(timezone=True), nullable=True),

        # Publicação
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Arquivamento
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Referência
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Metadados
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=True),

        # Auditoria
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index('ix_hr_employee_documents_employee', 'hr_employee_documents', ['employee_id'])
    op.create_index('ix_hr_employee_documents_type', 'hr_employee_documents', ['document_type'])
    op.create_index('ix_hr_employee_documents_status', 'hr_employee_documents', ['status'])

    # ============================================================
    # NOTIFICAÇÕES DO PORTAL
    # ============================================================
    op.create_table(
        'hr_employee_notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('condominio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Tipo e prioridade
        sa.Column('notification_type', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, server_default='normal'),

        # Conteúdo
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('short_message', sa.String(200), nullable=True),

        # Visual
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),

        # Ação
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('action_label', sa.String(100), nullable=True),

        # Referência
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Canais
        sa.Column('channels', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('delivery_status', postgresql.JSONB, nullable=False, server_default='{}'),

        # Status
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_dismissed', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),

        # Expiração
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_expired', sa.Boolean, nullable=False, server_default='false'),

        # Extra
        sa.Column('extra_data', postgresql.JSONB, nullable=False, server_default='{}'),

        # Auditoria
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index('ix_hr_employee_notifications_employee', 'hr_employee_notifications', ['employee_id'])
    op.create_index('ix_hr_employee_notifications_type', 'hr_employee_notifications', ['notification_type'])
    op.create_index('ix_hr_employee_notifications_read', 'hr_employee_notifications', ['is_read'])
    op.create_index('ix_hr_employee_notifications_created', 'hr_employee_notifications', ['created_at'])

    # ============================================================
    # PREFERÊNCIAS DO FUNCIONÁRIO
    # ============================================================
    op.create_table(
        'hr_employee_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),

        # Aparência
        sa.Column('theme', sa.String(20), nullable=False, server_default='system'),
        sa.Column('language', sa.String(10), nullable=False, server_default='pt_BR'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='America/Sao_Paulo'),
        sa.Column('date_format', sa.String(20), nullable=False, server_default='DD/MM/YYYY'),

        # Notificações
        sa.Column('email_notifications', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('push_notifications', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('sms_notifications', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('whatsapp_notifications', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('notification_settings', postgresql.JSONB, nullable=False, server_default='{}'),

        # Privacidade
        sa.Column('show_birthday', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('show_photo', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('show_contact', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('privacy_settings', postgresql.JSONB, nullable=False, server_default='{}'),

        # Dashboard
        sa.Column('dashboard_widgets', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('default_page', sa.String(50), nullable=False, server_default='dashboard'),

        # Acessibilidade
        sa.Column('high_contrast', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('font_size', sa.String(10), nullable=False, server_default='medium'),
        sa.Column('reduced_motion', sa.Boolean, nullable=False, server_default='false'),

        # 2FA
        sa.Column('two_factor_enabled', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('two_factor_secret', sa.String(100), nullable=True),
        sa.Column('two_factor_backup_codes', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('two_factor_verified_at', sa.DateTime(timezone=True), nullable=True),

        # Dispositivos
        sa.Column('trusted_devices', postgresql.JSONB, nullable=False, server_default='[]'),

        # Auditoria
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_index('ix_hr_employee_preferences_employee', 'hr_employee_preferences', ['employee_id'])


def downgrade() -> None:
    """Drop employee portal tables."""
    op.drop_table('hr_employee_preferences')
    op.drop_table('hr_employee_notifications')
    op.drop_table('hr_employee_documents')
    op.drop_table('hr_vacation_requests')
    op.drop_table('hr_vacation_periods')
    op.drop_table('hr_payslips')
