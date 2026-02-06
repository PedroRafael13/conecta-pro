"""Sprint 45 - Create fraud detection tables

Revision ID: sprint45_fraud_detection
Revises: sprint44_contract_analysis
Create Date: 2025-01-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers, used by Alembic.
revision: str = 'sprint45_fraud_detection'
down_revision: Union[str, None] = 'sprint44_contract_analysis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar ENUMs
    fraud_category_enum = postgresql.ENUM(
        'financial', 'identity', 'access', 'document', 'contract', 'billing',
        'procurement', 'employee', 'vendor', 'cyber', 'account_takeover',
        'payment', 'other',
        name='fraudcategory',
        create_type=False
    )
    fraud_category_enum.create(op.get_bind(), checkfirst=True)

    alert_severity_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='alertseverity',
        create_type=False
    )
    alert_severity_enum.create(op.get_bind(), checkfirst=True)

    alert_status_enum = postgresql.ENUM(
        'pending', 'investigating', 'confirmed', 'false_positive',
        'resolved', 'escalated', 'closed',
        name='alertstatus',
        create_type=False
    )
    alert_status_enum.create(op.get_bind(), checkfirst=True)

    rule_type_enum = postgresql.ENUM(
        'threshold', 'velocity', 'pattern', 'blacklist', 'whitelist',
        'behavioral', 'statistical', 'ml_based', 'composite', 'time_based',
        'geo_based', 'device_based', 'network_based',
        name='ruletype',
        create_type=False
    )
    rule_type_enum.create(op.get_bind(), checkfirst=True)

    rule_operator_enum = postgresql.ENUM(
        'equals', 'not_equals', 'greater_than', 'less_than',
        'greater_than_or_equal', 'less_than_or_equal', 'contains',
        'not_contains', 'starts_with', 'ends_with', 'in_list',
        'not_in_list', 'matches_regex', 'between', 'is_null',
        'is_not_null', 'is_empty',
        name='ruleoperator',
        create_type=False
    )
    rule_operator_enum.create(op.get_bind(), checkfirst=True)

    rule_action_enum = postgresql.ENUM(
        'alert', 'block', 'challenge', 'flag', 'review', 'notify',
        'limit', 'suspend', 'escalate', 'log',
        name='ruleaction',
        create_type=False
    )
    rule_action_enum.create(op.get_bind(), checkfirst=True)

    pattern_type_enum = postgresql.ENUM(
        'split_transaction', 'velocity_abuse', 'account_takeover',
        'credential_stuffing', 'synthetic_identity', 'first_party_fraud',
        'friendly_fraud', 'return_fraud', 'promo_abuse', 'loyalty_fraud',
        'card_testing', 'card_not_present', 'counterfeit_card',
        'lost_stolen_card', 'application_fraud', 'bust_out',
        'money_laundering', 'structuring', 'layering', 'phantom_vendor',
        'invoice_fraud', 'payroll_fraud', 'expense_fraud', 'kickback',
        'bid_rigging', 'ghost_employee', 'time_theft', 'asset_misappropriation',
        'data_theft', 'phishing', 'social_engineering', 'insider_threat',
        name='patterntype',
        create_type=False
    )
    pattern_type_enum.create(op.get_bind(), checkfirst=True)

    pattern_status_enum = postgresql.ENUM(
        'draft', 'active', 'inactive', 'testing', 'deprecated',
        name='patternstatus',
        create_type=False
    )
    pattern_status_enum.create(op.get_bind(), checkfirst=True)

    entity_type_enum = postgresql.ENUM(
        'usuario', 'morador', 'visitante', 'prestador', 'funcionario',
        'fornecedor', 'condominio', 'unidade', 'conta', 'dispositivo',
        'ip_address', 'email', 'telefone', 'documento',
        name='entitytype',
        create_type=False
    )
    entity_type_enum.create(op.get_bind(), checkfirst=True)

    risk_level_enum = postgresql.ENUM(
        'minimal', 'low', 'medium', 'high', 'critical', 'blocked',
        name='risklevel',
        create_type=False
    )
    risk_level_enum.create(op.get_bind(), checkfirst=True)

    # Criar tabela fraud_rules
    op.create_table(
        'fraud_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('rule_type', rule_type_enum, nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('subcategory', sa.String(50)),
        sa.Column('default_severity', sa.String(20), default='medium'),
        sa.Column('risk_weight', sa.Float, default=1.0),
        sa.Column('conditions', postgresql.JSONB, default=[]),
        sa.Column('threshold_value', sa.Float),
        sa.Column('threshold_count', sa.Integer),
        sa.Column('threshold_period_minutes', sa.Integer),
        sa.Column('velocity_count', sa.Integer),
        sa.Column('velocity_period_minutes', sa.Integer),
        sa.Column('velocity_field', sa.String(100)),
        sa.Column('primary_action', rule_action_enum, default='alert'),
        sa.Column('secondary_actions', postgresql.JSONB, default=[]),
        sa.Column('notify_channels', postgresql.JSONB, default=[]),
        sa.Column('applies_to_entities', postgresql.JSONB, default=[]),
        sa.Column('applies_to_transactions', postgresql.JSONB, default=[]),
        sa.Column('total_triggers', sa.Integer, default=0),
        sa.Column('true_positives', sa.Integer, default=0),
        sa.Column('false_positives', sa.Integer, default=0),
        sa.Column('last_triggered_at', sa.DateTime),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_system', sa.Boolean, default=False),
        sa.Column('is_test_mode', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
    )

    op.create_index('ix_fraud_rules_code', 'fraud_rules', ['code'])
    op.create_index('ix_fraud_rules_rule_type', 'fraud_rules', ['rule_type'])
    op.create_index('ix_fraud_rules_category', 'fraud_rules', ['category'])
    op.create_index('ix_fraud_rules_is_active', 'fraud_rules', ['is_active'])

    # Criar tabela fraud_patterns
    op.create_table(
        'fraud_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('pattern_type', pattern_type_enum, nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('subcategory', sa.String(50)),
        sa.Column('status', pattern_status_enum, default='draft'),
        sa.Column('severity', sa.String(20), default='medium'),
        sa.Column('risk_score', sa.Float, default=50.0),
        sa.Column('pattern_definition', postgresql.JSONB, default={}),
        sa.Column('features', postgresql.JSONB, default=[]),
        sa.Column('indicators', postgresql.JSONB, default=[]),
        sa.Column('detection_threshold', sa.Float, default=0.7),
        sa.Column('confidence_threshold', sa.Float, default=0.8),
        sa.Column('ml_model_path', sa.String(500)),
        sa.Column('ml_model_version', sa.String(50)),
        sa.Column('ml_last_trained_at', sa.DateTime),
        sa.Column('total_detections', sa.Integer, default=0),
        sa.Column('confirmed_cases', sa.Integer, default=0),
        sa.Column('false_positives', sa.Integer, default=0),
        sa.Column('last_detected_at', sa.DateTime),
        sa.Column('prevention_tips', postgresql.JSONB, default=[]),
        sa.Column('recommended_actions', postgresql.JSONB, default=[]),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_ml_based', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
    )

    op.create_index('ix_fraud_patterns_code', 'fraud_patterns', ['code'])
    op.create_index('ix_fraud_patterns_pattern_type', 'fraud_patterns', ['pattern_type'])
    op.create_index('ix_fraud_patterns_category', 'fraud_patterns', ['category'])
    op.create_index('ix_fraud_patterns_status', 'fraud_patterns', ['status'])
    op.create_index('ix_fraud_patterns_is_active', 'fraud_patterns', ['is_active'])

    # Criar tabela risk_profiles
    op.create_table(
        'risk_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('entity_type', entity_type_enum, nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_identifier', sa.String(255)),
        sa.Column('entity_name', sa.String(255)),
        sa.Column('risk_level', risk_level_enum, default='low'),
        sa.Column('risk_score', sa.Float, default=0),
        sa.Column('risk_score_change', sa.Float, default=0),
        sa.Column('behavior_score', sa.Float, default=0),
        sa.Column('transaction_score', sa.Float, default=0),
        sa.Column('velocity_score', sa.Float, default=0),
        sa.Column('identity_score', sa.Float, default=0),
        sa.Column('network_score', sa.Float, default=0),
        sa.Column('historical_score', sa.Float, default=0),
        sa.Column('risk_factors', postgresql.JSONB, default=[]),
        sa.Column('trust_indicators', postgresql.JSONB, default=[]),
        sa.Column('known_ips', postgresql.JSONB, default=[]),
        sa.Column('known_devices', postgresql.JSONB, default=[]),
        sa.Column('known_locations', postgresql.JSONB, default=[]),
        sa.Column('typical_hours', postgresql.JSONB, default=[]),
        sa.Column('total_alerts', sa.Integer, default=0),
        sa.Column('confirmed_frauds', sa.Integer, default=0),
        sa.Column('false_positives', sa.Integer, default=0),
        sa.Column('total_transactions', sa.Integer, default=0),
        sa.Column('total_transaction_value', sa.Float, default=0),
        sa.Column('avg_transaction_value', sa.Float, default=0),
        sa.Column('max_transaction_value', sa.Float),
        sa.Column('transaction_limit_daily', sa.Float),
        sa.Column('transaction_limit_monthly', sa.Float),
        sa.Column('transactions_today', sa.Integer, default=0),
        sa.Column('transactions_this_month', sa.Integer, default=0),
        sa.Column('logins_today', sa.Integer, default=0),
        sa.Column('last_login_at', sa.DateTime),
        sa.Column('last_login_ip', sa.String(45)),
        sa.Column('last_transaction_at', sa.DateTime),
        sa.Column('is_blocked', sa.Boolean, default=False),
        sa.Column('blocked_at', sa.DateTime),
        sa.Column('blocked_reason', sa.String(500)),
        sa.Column('is_whitelisted', sa.Boolean, default=False),
        sa.Column('whitelisted_at', sa.DateTime),
        sa.Column('is_watchlisted', sa.Boolean, default=False),
        sa.Column('watchlisted_at', sa.DateTime),
        sa.Column('watchlist_reason', sa.String(500)),
        sa.Column('verification_level', sa.Integer, default=0),
        sa.Column('identity_verified', sa.Boolean, default=False),
        sa.Column('identity_verified_at', sa.DateTime),
        sa.Column('notes', sa.Text),
        sa.Column('last_calculated_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )

    op.create_index(
        'ix_risk_profiles_entity',
        'risk_profiles',
        ['entity_type', 'entity_id'],
        unique=True
    )
    op.create_index('ix_risk_profiles_risk_level', 'risk_profiles', ['risk_level'])
    op.create_index('ix_risk_profiles_risk_score', 'risk_profiles', ['risk_score'])
    op.create_index('ix_risk_profiles_is_blocked', 'risk_profiles', ['is_blocked'])
    op.create_index('ix_risk_profiles_is_watchlisted', 'risk_profiles', ['is_watchlisted'])

    # Criar tabela fraud_alerts
    op.create_table(
        'fraud_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('alert_number', sa.String(20), unique=True, nullable=False),
        sa.Column('category', fraud_category_enum, nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('severity', alert_severity_enum, nullable=False),
        sa.Column('status', alert_status_enum, default='pending'),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('summary', sa.Text),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_name', sa.String(255)),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True)),
        sa.Column('transaction_type', sa.String(50)),
        sa.Column('transaction_value', sa.Float),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fraud_rules.id')),
        sa.Column('pattern_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fraud_patterns.id')),
        sa.Column('risk_score', sa.Float, default=0),
        sa.Column('confidence_score', sa.Float),
        sa.Column('evidence', postgresql.JSONB, default=[]),
        sa.Column('indicators', postgresql.JSONB, default=[]),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('device_id', sa.String(255)),
        sa.Column('location', sa.String(255)),
        sa.Column('geo_coordinates', postgresql.JSONB),
        sa.Column('user_agent', sa.Text),
        sa.Column('potential_loss', sa.Float),
        sa.Column('actual_loss', sa.Float),
        sa.Column('recovered_amount', sa.Float),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True)),
        sa.Column('assigned_at', sa.DateTime),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('resolution_type', sa.String(50)),
        sa.Column('resolution_notes', sa.Text),
        sa.Column('confirmed_by', postgresql.UUID(as_uuid=True)),
        sa.Column('confirmed_at', sa.DateTime),
        sa.Column('is_escalated', sa.Boolean, default=False),
        sa.Column('escalated_to', postgresql.UUID(as_uuid=True)),
        sa.Column('escalated_at', sa.DateTime),
        sa.Column('escalation_level', sa.Integer, default=0),
        sa.Column('sla_deadline', sa.DateTime),
        sa.Column('investigation_notes', sa.Text),
        sa.Column('actions_log', postgresql.JSONB, default=[]),
        sa.Column('tags', postgresql.JSONB, default=[]),
        sa.Column('feedback_status', sa.String(20)),
        sa.Column('feedback_notes', sa.Text),
        sa.Column('feedback_at', sa.DateTime),
        sa.Column('related_alerts', postgresql.JSONB, default=[]),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('requires_immediate_action', sa.Boolean, default=False),
        sa.Column('detected_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )

    op.create_index('ix_fraud_alerts_alert_number', 'fraud_alerts', ['alert_number'])
    op.create_index('ix_fraud_alerts_category', 'fraud_alerts', ['category'])
    op.create_index('ix_fraud_alerts_severity', 'fraud_alerts', ['severity'])
    op.create_index('ix_fraud_alerts_status', 'fraud_alerts', ['status'])
    op.create_index('ix_fraud_alerts_entity', 'fraud_alerts', ['entity_type', 'entity_id'])
    op.create_index('ix_fraud_alerts_created_at', 'fraud_alerts', ['created_at'])
    op.create_index('ix_fraud_alerts_assigned_to', 'fraud_alerts', ['assigned_to'])
    op.create_index('ix_fraud_alerts_rule_id', 'fraud_alerts', ['rule_id'])
    op.create_index('ix_fraud_alerts_pattern_id', 'fraud_alerts', ['pattern_id'])


def downgrade() -> None:
    # Remover tabelas
    op.drop_table('fraud_alerts')
    op.drop_table('risk_profiles')
    op.drop_table('fraud_patterns')
    op.drop_table('fraud_rules')

    # Remover ENUMs
    op.execute('DROP TYPE IF EXISTS risklevel')
    op.execute('DROP TYPE IF EXISTS entitytype')
    op.execute('DROP TYPE IF EXISTS patternstatus')
    op.execute('DROP TYPE IF EXISTS patterntype')
    op.execute('DROP TYPE IF EXISTS ruleaction')
    op.execute('DROP TYPE IF EXISTS ruleoperator')
    op.execute('DROP TYPE IF EXISTS ruletype')
    op.execute('DROP TYPE IF EXISTS alertstatus')
    op.execute('DROP TYPE IF EXISTS alertseverity')
    op.execute('DROP TYPE IF EXISTS fraudcategory')
