"""Sprint 44: Create contract analysis tables

Revision ID: sprint44_contract_analysis
Revises: sprint43_inventory_forecast
Create Date: 2025-01-05

Tabelas para analise de contratos com IA:
- contract_analyses: Analises de contratos
- contract_extracted_clauses: Clausulas extraidas
- contract_alerts: Alertas de contratos
"""

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM


# revision identifiers
revision = 'sprint44_contract_analysis'
down_revision = 'sprint43_inventory_forecast'
branch_labels = None
depends_on = None


def create_enum_safe(name: str, values: list):
    """Cria enum de forma segura (ignora se já existir)."""
    values_str = ", ".join([f"'{v}'" for v in values])
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({values_str});
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)


def upgrade() -> None:
    """Criar tabelas de analise de contratos."""

    # Enum types (safe creation)
    create_enum_safe("analysis_status", ["pending", "processing", "completed", "failed", "requires_review"])
    create_enum_safe("contract_type", ["service", "sales", "lease", "employment", "nda", "sla",
                                        "partnership", "franchise", "license", "supply", "consulting", "other"])
    create_enum_safe("risk_level", ["low", "medium", "high", "critical"])
    create_enum_safe("clause_type", ["object", "payment", "termination", "penalty", "warranty",
                                      "confidentiality", "non_compete", "exclusivity", "force_majeure",
                                      "liability", "indemnity", "jurisdiction", "renewal", "adjustment",
                                      "sla", "insurance", "audit", "data_protection", "ip_rights",
                                      "dispute_resolution", "notification", "assignment", "governing_law", "other"])
    create_enum_safe("clause_importance", ["low", "medium", "high", "critical"])
    create_enum_safe("alert_type", ["expiry", "renewal", "adjustment", "risk", "compliance",
                                     "review", "payment", "deadline", "sla_breach", "warranty",
                                     "audit", "custom"])
    create_enum_safe("alert_status", ["pending", "acknowledged", "in_progress", "resolved", "dismissed", "escalated"])
    create_enum_safe("alert_priority", ["low", "medium", "high", "urgent", "critical"])

    # Tabela: contract_analyses
    op.create_table(
        'contract_analyses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),

        # Contrato
        sa.Column('contract_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('contract_number', sa.String(100)),
        sa.Column('document_id', UUID(as_uuid=True)),
        sa.Column('file_name', sa.String(500)),

        # Status
        sa.Column('status', ENUM('pending', 'processing', 'completed', 'failed', 'requires_review',
                  name='analysis_status', create_type=False), server_default='pending', nullable=False, index=True),
        sa.Column('contract_type', ENUM('service', 'sales', 'lease', 'employment', 'nda', 'sla',
                  'partnership', 'franchise', 'license', 'supply', 'consulting', 'other',
                  name='contract_type', create_type=False), server_default='other'),

        # Partes
        sa.Column('contractor_name', sa.String(300)),
        sa.Column('contractor_document', sa.String(20)),
        sa.Column('contractor_type', sa.String(20)),
        sa.Column('contracted_name', sa.String(300)),
        sa.Column('contracted_document', sa.String(20)),
        sa.Column('contracted_type', sa.String(20)),

        # Datas
        sa.Column('signature_date', sa.Date),
        sa.Column('start_date', sa.Date, index=True),
        sa.Column('end_date', sa.Date, index=True),
        sa.Column('renewal_date', sa.Date),
        sa.Column('adjustment_date', sa.Date),

        # Valores
        sa.Column('total_value', sa.Numeric(18, 2)),
        sa.Column('monthly_value', sa.Numeric(18, 2)),
        sa.Column('currency', sa.String(3), server_default='BRL'),
        sa.Column('payment_terms', sa.Text),
        sa.Column('adjustment_index', sa.String(50)),

        # Risco
        sa.Column('risk_level', ENUM('low', 'medium', 'high', 'critical',
                  name='risk_level', create_type=False), server_default='low'),
        sa.Column('risk_score', sa.Float, server_default='0'),
        sa.Column('risk_factors', JSONB, server_default='[]'),

        # Conformidade
        sa.Column('compliance_score', sa.Float, server_default='0'),
        sa.Column('compliance_issues', JSONB, server_default='[]'),
        sa.Column('missing_clauses', JSONB, server_default='[]'),

        # Clausulas
        sa.Column('total_clauses', sa.Integer, server_default='0'),
        sa.Column('extracted_clauses', sa.Integer, server_default='0'),
        sa.Column('risky_clauses', sa.Integer, server_default='0'),

        # Flags
        sa.Column('has_auto_renewal', sa.Boolean, server_default='false'),
        sa.Column('has_penalty_clause', sa.Boolean, server_default='false'),
        sa.Column('has_confidentiality', sa.Boolean, server_default='false'),
        sa.Column('has_sla', sa.Boolean, server_default='false'),
        sa.Column('has_exclusivity', sa.Boolean, server_default='false'),
        sa.Column('requires_review', sa.Boolean, server_default='false'),

        # Prazos
        sa.Column('notice_period_days', sa.Integer),
        sa.Column('grace_period_days', sa.Integer),
        sa.Column('warranty_period_days', sa.Integer),

        # Texto
        sa.Column('original_text', sa.Text),
        sa.Column('summary', sa.Text),
        sa.Column('key_terms', JSONB, server_default='[]'),
        sa.Column('obligations', JSONB, server_default='[]'),

        # Processamento
        sa.Column('processing_time_ms', sa.Integer),
        sa.Column('confidence_score', sa.Float),
        sa.Column('model_version', sa.String(50)),
        sa.Column('error_message', sa.Text),

        # Metadados
        sa.Column('analyzed_by', UUID(as_uuid=True)),
        sa.Column('reviewed_by', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('reviewed_at', sa.DateTime),

        # Notas
        sa.Column('notes', sa.Text),
        sa.Column('review_notes', sa.Text),

        # Flags
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
    )

    # Indices
    op.create_index(
        'ix_analyses_contract_status',
        'contract_analyses',
        ['contract_id', 'status']
    )
    op.create_index(
        'ix_analyses_dates',
        'contract_analyses',
        ['start_date', 'end_date']
    )
    op.create_index(
        'ix_analyses_risk',
        'contract_analyses',
        ['risk_level', 'risk_score']
    )

    # Tabela: contract_extracted_clauses
    op.create_table(
        'contract_extracted_clauses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),

        # Relacionamento
        sa.Column('analysis_id', UUID(as_uuid=True),
                  sa.ForeignKey('contract_analyses.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('contract_id', UUID(as_uuid=True), nullable=False, index=True),

        # Identificacao
        sa.Column('clause_number', sa.String(20)),
        sa.Column('clause_type', ENUM('object', 'payment', 'termination', 'penalty', 'warranty',
                  'confidentiality', 'non_compete', 'exclusivity', 'force_majeure',
                  'liability', 'indemnity', 'jurisdiction', 'renewal', 'adjustment',
                  'sla', 'insurance', 'audit', 'data_protection', 'ip_rights',
                  'dispute_resolution', 'notification', 'assignment', 'governing_law', 'other',
                  name='clause_type', create_type=False), server_default='other', nullable=False),
        sa.Column('importance', ENUM('low', 'medium', 'high', 'critical',
                  name='clause_importance', create_type=False), server_default='medium'),

        # Texto
        sa.Column('title', sa.String(500)),
        sa.Column('original_text', sa.Text, nullable=False),
        sa.Column('normalized_text', sa.Text),
        sa.Column('summary', sa.Text),

        # Posicao
        sa.Column('start_position', sa.Integer),
        sa.Column('end_position', sa.Integer),
        sa.Column('page_number', sa.Integer),
        sa.Column('section', sa.String(100)),

        # Entidades
        sa.Column('entities', JSONB, server_default='[]'),
        sa.Column('dates_mentioned', JSONB, server_default='[]'),
        sa.Column('values_mentioned', JSONB, server_default='[]'),
        sa.Column('parties_mentioned', JSONB, server_default='[]'),

        # Analise
        sa.Column('is_risky', sa.Boolean, server_default='false'),
        sa.Column('risk_score', sa.Float, server_default='0'),
        sa.Column('risk_reasons', JSONB, server_default='[]'),
        sa.Column('keywords', JSONB, server_default='[]'),
        sa.Column('obligations', JSONB, server_default='[]'),
        sa.Column('conditions', JSONB, server_default='[]'),
        sa.Column('deadlines', JSONB, server_default='[]'),

        # Confianca
        sa.Column('classification_confidence', sa.Float, server_default='0'),
        sa.Column('extraction_confidence', sa.Float, server_default='0'),

        # Metadados
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

        # Flags
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('needs_review', sa.Boolean, server_default='false'),
        sa.Column('reviewed', sa.Boolean, server_default='false'),

        # Notas
        sa.Column('notes', sa.Text),
    )

    # Indices
    op.create_index(
        'ix_clauses_analysis_type',
        'contract_extracted_clauses',
        ['analysis_id', 'clause_type']
    )
    op.create_index(
        'ix_clauses_risky',
        'contract_extracted_clauses',
        ['is_risky', 'risk_score']
    )

    # Tabela: contract_alerts
    op.create_table(
        'contract_alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),

        # Relacionamentos
        sa.Column('analysis_id', UUID(as_uuid=True),
                  sa.ForeignKey('contract_analyses.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('contract_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('contract_number', sa.String(100)),

        # Tipo e prioridade
        sa.Column('alert_type', ENUM('expiry', 'renewal', 'adjustment', 'risk', 'compliance',
                  'review', 'payment', 'deadline', 'sla_breach', 'warranty',
                  'audit', 'custom', name='alert_type', create_type=False),
                  nullable=False, index=True),
        sa.Column('status', ENUM('pending', 'acknowledged', 'in_progress', 'resolved',
                  'dismissed', 'escalated', name='alert_status', create_type=False),
                  server_default='pending', nullable=False, index=True),
        sa.Column('priority', ENUM('low', 'medium', 'high', 'urgent', 'critical',
                  name='alert_priority', create_type=False),
                  server_default='medium', nullable=False, index=True),

        # Conteudo
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('recommendation', sa.Text),

        # Datas
        sa.Column('trigger_date', sa.Date, nullable=False, index=True),
        sa.Column('due_date', sa.Date),
        sa.Column('reference_date', sa.Date),
        sa.Column('days_before', sa.Integer),
        sa.Column('days_remaining', sa.Integer),

        # Resolucao
        sa.Column('acknowledged_by', UUID(as_uuid=True)),
        sa.Column('acknowledged_at', sa.DateTime),
        sa.Column('resolved_by', UUID(as_uuid=True)),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('resolution_notes', sa.Text),
        sa.Column('resolution_action', sa.String(100)),

        # Adiamento
        sa.Column('is_snoozed', sa.Boolean, server_default='false'),
        sa.Column('snooze_until', sa.DateTime),
        sa.Column('snooze_count', sa.Integer, server_default='0'),

        # Escalonamento
        sa.Column('escalation_level', sa.Integer, server_default='0'),
        sa.Column('escalated_to', UUID(as_uuid=True)),
        sa.Column('escalated_at', sa.DateTime),

        # Confianca
        sa.Column('confidence', sa.Float, server_default='0'),

        # Metadados
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

        # Flags
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('is_automated', sa.Boolean, server_default='true'),
        sa.Column('requires_action', sa.Boolean, server_default='true'),

        # Notificacoes
        sa.Column('notification_sent', sa.Boolean, server_default='false'),
        sa.Column('notification_sent_at', sa.DateTime),
        sa.Column('notification_channels', JSONB, server_default='[]'),

        # Notas
        sa.Column('notes', sa.Text),
    )

    # Indices
    op.create_index(
        'ix_alerts_contract_status',
        'contract_alerts',
        ['contract_id', 'status']
    )
    op.create_index(
        'ix_alerts_priority_due',
        'contract_alerts',
        ['priority', 'due_date']
    )
    op.create_index(
        'ix_alerts_trigger',
        'contract_alerts',
        ['trigger_date', 'is_active']
    )


def downgrade() -> None:
    """Remover tabelas de analise de contratos."""

    # Remover tabelas
    op.drop_table('contract_alerts')
    op.drop_table('contract_extracted_clauses')
    op.drop_table('contract_analyses')

    # Remover enums
    op.execute('DROP TYPE IF EXISTS analysis_status')
    op.execute('DROP TYPE IF EXISTS contract_type')
    op.execute('DROP TYPE IF EXISTS risk_level')
    op.execute('DROP TYPE IF EXISTS clause_type')
    op.execute('DROP TYPE IF EXISTS clause_importance')
    op.execute('DROP TYPE IF EXISTS alert_type')
    op.execute('DROP TYPE IF EXISTS alert_status')
    op.execute('DROP TYPE IF EXISTS alert_priority')
