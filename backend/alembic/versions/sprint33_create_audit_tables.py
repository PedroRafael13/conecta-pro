"""Sprint 33 - Create Audit Tables

Revision ID: sprint33_audit
Revises: sprint32_integrations
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sprint33_audit'
down_revision = 'sprint32_integrations'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==================== audit_logs ====================
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', sa.String(50), nullable=False, unique=True),
        sa.Column('correlation_id', sa.String(50), nullable=True),
        sa.Column('parent_event_id', sa.String(50), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('result', sa.String(20), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('user_name', sa.String(200), nullable=True),
        sa.Column('user_role', sa.String(100), nullable=True),
        sa.Column('impersonated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('entity_name', sa.String(300), nullable=True),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('changed_fields', postgresql.JSONB(), nullable=True),
        sa.Column('request_method', sa.String(10), nullable=True),
        sa.Column('request_path', sa.String(500), nullable=True),
        sa.Column('request_query', sa.Text(), nullable=True),
        sa.Column('request_body_hash', sa.String(64), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('device_fingerprint', sa.String(64), nullable=True),
        sa.Column('geo_country', sa.String(100), nullable=True),
        sa.Column('geo_region', sa.String(100), nullable=True),
        sa.Column('geo_city', sa.String(100), nullable=True),
        sa.Column('geo_coordinates', sa.String(50), nullable=True),
        sa.Column('service_name', sa.String(100), nullable=True),
        sa.Column('service_version', sa.String(20), nullable=True),
        sa.Column('environment', sa.String(50), nullable=True),
        sa.Column('server_hostname', sa.String(200), nullable=True),
        sa.Column('compliance_frameworks', postgresql.JSONB(), nullable=True),
        sa.Column('data_classification', sa.String(50), nullable=True),
        sa.Column('retention_days', sa.Integer(), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_pii', sa.Boolean(), nullable=False, default=False),
        sa.Column('triggered_alerts', postgresql.JSONB(), nullable=True),
        sa.Column('requires_review', sa.Boolean(), nullable=False, default=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=False, default=False),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_event_id', 'audit_logs', ['event_id'])
    op.create_index('ix_audit_logs_correlation_id', 'audit_logs', ['correlation_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_category', 'audit_logs', ['category'])
    op.create_index('ix_audit_logs_severity', 'audit_logs', ['severity'])
    op.create_index('ix_audit_logs_result', 'audit_logs', ['result'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_ip_address', 'audit_logs', ['ip_address'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_requires_review', 'audit_logs', ['requires_review'])
    op.create_index('ix_audit_logs_archived', 'audit_logs', ['archived'])
    op.create_index('ix_audit_logs_user_action_date', 'audit_logs', ['user_id', 'action', 'created_at'])

    # ==================== compliance_rules ====================
    op.create_table(
        'compliance_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('framework', sa.String(50), nullable=False),
        sa.Column('framework_reference', sa.String(100), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('requirement_text', sa.Text(), nullable=False),
        sa.Column('implementation_guidance', sa.Text(), nullable=True),
        sa.Column('evidence_required', postgresql.JSONB(), nullable=True),
        sa.Column('controls_required', postgresql.JSONB(), nullable=True),
        sa.Column('validation_query', sa.Text(), nullable=True),
        sa.Column('validation_script', sa.Text(), nullable=True),
        sa.Column('validation_endpoint', sa.String(500), nullable=True),
        sa.Column('validation_frequency_hours', sa.Integer(), nullable=True),
        sa.Column('auto_validate', sa.Boolean(), nullable=False, default=True),
        sa.Column('applies_to_entities', postgresql.JSONB(), nullable=True),
        sa.Column('applies_to_roles', postgresql.JSONB(), nullable=True),
        sa.Column('applies_to_modules', postgresql.JSONB(), nullable=True),
        sa.Column('excluded_entities', postgresql.JSONB(), nullable=True),
        sa.Column('penalty_description', sa.Text(), nullable=True),
        sa.Column('penalty_amount', sa.Integer(), nullable=True),
        sa.Column('penalty_currency', sa.String(3), nullable=True),
        sa.Column('legal_reference', sa.Text(), nullable=True),
        sa.Column('notify_on_violation', sa.Boolean(), nullable=False, default=True),
        sa.Column('notification_recipients', postgresql.JSONB(), nullable=True),
        sa.Column('escalation_path', postgresql.JSONB(), nullable=True),
        sa.Column('escalation_timeout_hours', sa.Integer(), nullable=True),
        sa.Column('remediation_steps', postgresql.JSONB(), nullable=True),
        sa.Column('remediation_deadline_days', sa.Integer(), nullable=True),
        sa.Column('auto_remediate', sa.Boolean(), nullable=False, default=False),
        sa.Column('remediation_script', sa.Text(), nullable=True),
        sa.Column('documentation_url', sa.String(500), nullable=True),
        sa.Column('training_url', sa.String(500), nullable=True),
        sa.Column('related_policies', postgresql.JSONB(), nullable=True),
        sa.Column('exceptions_allowed', sa.Boolean(), nullable=False, default=False),
        sa.Column('exception_approval_required', sa.Boolean(), nullable=False, default=True),
        sa.Column('exception_max_duration_days', sa.Integer(), nullable=True),
        sa.Column('total_checks', sa.Integer(), nullable=False, default=0),
        sa.Column('passed_checks', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_checks', sa.Integer(), nullable=False, default=0),
        sa.Column('last_check_at', sa.DateTime(), nullable=True),
        sa.Column('last_violation_at', sa.DateTime(), nullable=True),
        sa.Column('effective_from', sa.DateTime(), nullable=True),
        sa.Column('effective_until', sa.DateTime(), nullable=True),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('next_review_date', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_compliance_rules_code', 'compliance_rules', ['code'])
    op.create_index('ix_compliance_rules_framework', 'compliance_rules', ['framework'])
    op.create_index('ix_compliance_rules_category', 'compliance_rules', ['category'])
    op.create_index('ix_compliance_rules_status', 'compliance_rules', ['status'])
    op.create_index('ix_compliance_rules_severity', 'compliance_rules', ['severity'])
    op.create_index('ix_compliance_rules_ativo', 'compliance_rules', ['ativo'])
    op.create_index('ix_compliance_rules_framework_status', 'compliance_rules', ['framework', 'status'])

    # ==================== compliance_checks ====================
    op.create_table(
        'compliance_checks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('check_number', sa.String(50), nullable=False, unique=True),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('check_type', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('result', sa.String(30), nullable=True),
        sa.Column('scope_description', sa.Text(), nullable=True),
        sa.Column('entities_checked', sa.Integer(), nullable=True),
        sa.Column('entities_compliant', sa.Integer(), nullable=True),
        sa.Column('entities_non_compliant', sa.Integer(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('sample_percentage', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('executed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('executor_type', sa.String(50), nullable=True),
        sa.Column('evidence_collected', postgresql.JSONB(), nullable=True),
        sa.Column('evidence_files', postgresql.JSONB(), nullable=True),
        sa.Column('screenshots', postgresql.JSONB(), nullable=True),
        sa.Column('query_results', postgresql.JSONB(), nullable=True),
        sa.Column('violations', postgresql.JSONB(), nullable=True),
        sa.Column('violations_count', sa.Integer(), nullable=False, default=0),
        sa.Column('critical_violations', sa.Integer(), nullable=False, default=0),
        sa.Column('analysis_notes', sa.Text(), nullable=True),
        sa.Column('risk_assessment', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('impact_assessment', sa.Text(), nullable=True),
        sa.Column('remediation_required', sa.Boolean(), nullable=False, default=False),
        sa.Column('remediation_plan', postgresql.JSONB(), nullable=True),
        sa.Column('remediation_deadline', sa.DateTime(), nullable=True),
        sa.Column('remediation_status', sa.String(50), nullable=True),
        sa.Column('remediation_completed_at', sa.DateTime(), nullable=True),
        sa.Column('remediation_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('exception_granted', sa.Boolean(), nullable=False, default=False),
        sa.Column('exception_reason', sa.Text(), nullable=True),
        sa.Column('exception_approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('exception_expires_at', sa.DateTime(), nullable=True),
        sa.Column('requires_review', sa.Boolean(), nullable=False, default=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('review_decision', sa.String(50), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('notifications_sent', postgresql.JSONB(), nullable=True),
        sa.Column('escalated', sa.Boolean(), nullable=False, default=False),
        sa.Column('escalated_at', sa.DateTime(), nullable=True),
        sa.Column('escalated_to', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', postgresql.JSONB(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('next_check_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['rule_id'], ['compliance_rules.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_compliance_checks_rule_id', 'compliance_checks', ['rule_id'])
    op.create_index('ix_compliance_checks_check_number', 'compliance_checks', ['check_number'])
    op.create_index('ix_compliance_checks_batch_id', 'compliance_checks', ['batch_id'])
    op.create_index('ix_compliance_checks_status', 'compliance_checks', ['status'])
    op.create_index('ix_compliance_checks_result', 'compliance_checks', ['result'])
    op.create_index('ix_compliance_checks_check_type', 'compliance_checks', ['check_type'])
    op.create_index('ix_compliance_checks_created_at', 'compliance_checks', ['created_at'])
    op.create_index('ix_compliance_checks_requires_review', 'compliance_checks', ['requires_review'])
    op.create_index('ix_compliance_checks_remediation_required', 'compliance_checks', ['remediation_required'])
    op.create_index('ix_compliance_checks_ativo', 'compliance_checks', ['ativo'])
    op.create_index('ix_compliance_checks_rule_result', 'compliance_checks', ['rule_id', 'result'])

    # ==================== data_retention_policies ====================
    op.create_table(
        'data_retention_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('data_category', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('retention_period', sa.String(20), nullable=False),
        sa.Column('retention_days', sa.Integer(), nullable=True),
        sa.Column('grace_period_days', sa.Integer(), nullable=True),
        sa.Column('expiration_action', sa.String(20), nullable=False),
        sa.Column('secondary_action', sa.String(20), nullable=True),
        sa.Column('action_delay_days', sa.Integer(), nullable=True),
        sa.Column('entity_types', postgresql.JSONB(), nullable=True),
        sa.Column('table_names', postgresql.JSONB(), nullable=True),
        sa.Column('field_patterns', postgresql.JSONB(), nullable=True),
        sa.Column('excluded_entities', postgresql.JSONB(), nullable=True),
        sa.Column('condition_query', sa.Text(), nullable=True),
        sa.Column('condition_field', sa.String(100), nullable=True),
        sa.Column('condition_operator', sa.String(20), nullable=True),
        sa.Column('condition_value', sa.String(200), nullable=True),
        sa.Column('compliance_framework', sa.String(100), nullable=True),
        sa.Column('compliance_reference', sa.String(200), nullable=True),
        sa.Column('legal_basis', sa.Text(), nullable=True),
        sa.Column('legal_hold_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('anonymize_fields', postgresql.JSONB(), nullable=True),
        sa.Column('anonymization_method', sa.String(50), nullable=True),
        sa.Column('preserve_statistics', sa.Boolean(), nullable=False, default=False),
        sa.Column('archive_location', sa.String(500), nullable=True),
        sa.Column('archive_format', sa.String(50), nullable=True),
        sa.Column('archive_encrypted', sa.Boolean(), nullable=False, default=True),
        sa.Column('archive_compressed', sa.Boolean(), nullable=False, default=True),
        sa.Column('notify_before_days', sa.Integer(), nullable=True),
        sa.Column('notify_recipients', postgresql.JSONB(), nullable=True),
        sa.Column('notify_on_execution', sa.Boolean(), nullable=False, default=True),
        sa.Column('require_approval', sa.Boolean(), nullable=False, default=False),
        sa.Column('schedule_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('schedule_cron', sa.String(100), nullable=True),
        sa.Column('last_execution_at', sa.DateTime(), nullable=True),
        sa.Column('next_execution_at', sa.DateTime(), nullable=True),
        sa.Column('total_executions', sa.Integer(), nullable=False, default=0),
        sa.Column('records_processed', sa.Integer(), nullable=False, default=0),
        sa.Column('records_deleted', sa.Integer(), nullable=False, default=0),
        sa.Column('records_archived', sa.Integer(), nullable=False, default=0),
        sa.Column('records_anonymized', sa.Integer(), nullable=False, default=0),
        sa.Column('last_records_affected', sa.Integer(), nullable=True),
        sa.Column('storage_freed_bytes', sa.Integer(), nullable=False, default=0),
        sa.Column('last_error_at', sa.DateTime(), nullable=True),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.Column('consecutive_errors', sa.Integer(), nullable=False, default=0),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('effective_from', sa.DateTime(), nullable=True),
        sa.Column('effective_until', sa.DateTime(), nullable=True),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_retention_code', 'data_retention_policies', ['code'])
    op.create_index('ix_data_retention_data_category', 'data_retention_policies', ['data_category'])
    op.create_index('ix_data_retention_status', 'data_retention_policies', ['status'])
    op.create_index('ix_data_retention_retention_period', 'data_retention_policies', ['retention_period'])
    op.create_index('ix_data_retention_expiration_action', 'data_retention_policies', ['expiration_action'])
    op.create_index('ix_data_retention_next_execution_at', 'data_retention_policies', ['next_execution_at'])
    op.create_index('ix_data_retention_ativo', 'data_retention_policies', ['ativo'])

    # ==================== access_history ====================
    op.create_table(
        'access_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('request_id', sa.String(50), nullable=True),
        sa.Column('access_type', sa.String(30), nullable=False),
        sa.Column('result', sa.String(30), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('user_name', sa.String(200), nullable=True),
        sa.Column('user_role', sa.String(100), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('auth_method', sa.String(50), nullable=True),
        sa.Column('auth_provider', sa.String(100), nullable=True),
        sa.Column('mfa_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('mfa_method', sa.String(50), nullable=True),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resource_path', sa.String(500), nullable=True),
        sa.Column('http_method', sa.String(10), nullable=True),
        sa.Column('action', sa.String(100), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('ip_type', sa.String(20), nullable=True),
        sa.Column('ip_reputation', sa.String(50), nullable=True),
        sa.Column('proxy_detected', sa.Boolean(), nullable=False, default=False),
        sa.Column('vpn_detected', sa.Boolean(), nullable=False, default=False),
        sa.Column('tor_detected', sa.Boolean(), nullable=False, default=False),
        sa.Column('geo_country', sa.String(100), nullable=True),
        sa.Column('geo_country_code', sa.String(3), nullable=True),
        sa.Column('geo_region', sa.String(100), nullable=True),
        sa.Column('geo_city', sa.String(100), nullable=True),
        sa.Column('geo_latitude', sa.String(20), nullable=True),
        sa.Column('geo_longitude', sa.String(20), nullable=True),
        sa.Column('geo_timezone', sa.String(50), nullable=True),
        sa.Column('geo_isp', sa.String(200), nullable=True),
        sa.Column('device_type', sa.String(20), nullable=True),
        sa.Column('device_fingerprint', sa.String(64), nullable=True),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('device_name', sa.String(200), nullable=True),
        sa.Column('device_trusted', sa.Boolean(), nullable=False, default=False),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('browser_name', sa.String(100), nullable=True),
        sa.Column('browser_version', sa.String(50), nullable=True),
        sa.Column('os_name', sa.String(100), nullable=True),
        sa.Column('os_version', sa.String(50), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('risk_factors', postgresql.JSONB(), nullable=True),
        sa.Column('anomaly_detected', sa.Boolean(), nullable=False, default=False),
        sa.Column('anomaly_type', sa.String(100), nullable=True),
        sa.Column('failure_reason', sa.String(200), nullable=True),
        sa.Column('failure_code', sa.String(50), nullable=True),
        sa.Column('attempts_count', sa.Integer(), nullable=True),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('context', postgresql.JSONB(), nullable=True),
        sa.Column('headers', postgresql.JSONB(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('alert_triggered', sa.Boolean(), nullable=False, default=False),
        sa.Column('alert_ids', postgresql.JSONB(), nullable=True),
        sa.Column('requires_review', sa.Boolean(), nullable=False, default=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('accessed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_access_history_session_id', 'access_history', ['session_id'])
    op.create_index('ix_access_history_user_id', 'access_history', ['user_id'])
    op.create_index('ix_access_history_access_type', 'access_history', ['access_type'])
    op.create_index('ix_access_history_result', 'access_history', ['result'])
    op.create_index('ix_access_history_ip_address', 'access_history', ['ip_address'])
    op.create_index('ix_access_history_device_fingerprint', 'access_history', ['device_fingerprint'])
    op.create_index('ix_access_history_risk_level', 'access_history', ['risk_level'])
    op.create_index('ix_access_history_accessed_at', 'access_history', ['accessed_at'])
    op.create_index('ix_access_history_requires_review', 'access_history', ['requires_review'])
    op.create_index('ix_access_history_anomaly_detected', 'access_history', ['anomaly_detected'])
    op.create_index('ix_access_history_user_type_date', 'access_history', ['user_id', 'access_type', 'accessed_at'])
    op.create_index('ix_access_history_ip_date', 'access_history', ['ip_address', 'accessed_at'])


def downgrade() -> None:
    op.drop_table('access_history')
    op.drop_table('data_retention_policies')
    op.drop_table('compliance_checks')
    op.drop_table('compliance_rules')
    op.drop_table('audit_logs')
