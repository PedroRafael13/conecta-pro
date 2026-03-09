"""Fix financial module schema - add missing columns and rename mismatched columns

Revision ID: sprint60_fix_financial_schema
Revises: production_merge_20260209
Create Date: 2026-03-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'sprint60_fix_financial_schema'
down_revision = 'production_merge_20260209'
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================================
    # TABLE: suppliers
    # =========================================================================
    # Rename mismatched columns
    op.execute("ALTER TABLE suppliers RENAME COLUMN block_reason TO blocked_reason")
    op.execute("ALTER TABLE suppliers RENAME COLUMN block_date TO blocked_at")
    op.execute("ALTER TABLE suppliers RENAME COLUMN qualification_date TO qualified_at")

    # Add missing columns
    op.add_column('suppliers', sa.Column('code', sa.String(20), nullable=True))
    op.add_column('suppliers', sa.Column('whatsapp', sa.String(20), nullable=True))
    op.add_column('suppliers', sa.Column('contact_email', sa.String(150), nullable=True))
    op.add_column('suppliers', sa.Column('contact_phone', sa.String(20), nullable=True))
    op.add_column('suppliers', sa.Column('contact_position', sa.String(100), nullable=True))
    op.add_column('suppliers', sa.Column('address_country', sa.String(50), nullable=True, server_default='BR'))
    op.add_column('suppliers', sa.Column('payment_terms_days', sa.Integer(), nullable=True))
    op.add_column('suppliers', sa.Column('credit_limit', sa.Numeric(15, 2), nullable=True))
    op.add_column('suppliers', sa.Column('discount_percentage', sa.Numeric(5, 2), nullable=True))
    op.add_column('suppliers', sa.Column('default_payment_method_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('suppliers', sa.Column('rating', sa.Integer(), nullable=True))
    op.add_column('suppliers', sa.Column('rating_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('suppliers', sa.Column('documents', postgresql.JSONB(), nullable=True))

    # =========================================================================
    # TABLE: payable_accounts
    # =========================================================================
    # Rename mismatched columns
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN discount TO discount_value")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN paid_amount TO paid_value")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withholding_iss TO withhold_iss")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withholding_ir TO withhold_ir")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withholding_pis TO withhold_pis")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withholding_cofins TO withhold_cofins")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withholding_csll TO withhold_csll")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withholding_inss TO withhold_inss")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN installments TO total_installments")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN scheduled_date TO scheduled_payment_date")

    # Add missing columns
    op.add_column('payable_accounts', sa.Column('addition_value', sa.Numeric(15, 2), nullable=True, server_default='0'))
    op.add_column('payable_accounts', sa.Column('remaining_value', sa.Numeric(15, 2), nullable=True))
    op.add_column('payable_accounts', sa.Column('entry_date', sa.Date(), nullable=True))
    op.add_column('payable_accounts', sa.Column('payment_date', sa.Date(), nullable=True))
    op.add_column('payable_accounts', sa.Column('recurrence_end_date', sa.Date(), nullable=True))
    op.add_column('payable_accounts', sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('payable_accounts', sa.Column('approval_status', sa.String(20), nullable=True))
    op.add_column('payable_accounts', sa.Column('approval_notes', sa.Text(), nullable=True))
    op.add_column('payable_accounts', sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('payable_accounts', sa.Column('internal_notes', sa.Text(), nullable=True))
    op.add_column('payable_accounts', sa.Column('fiscal_document_type', sa.String(30), nullable=True))
    op.add_column('payable_accounts', sa.Column('fiscal_document_key', sa.String(50), nullable=True))
    op.add_column('payable_accounts', sa.Column('fiscal_document_url', sa.String(500), nullable=True))
    op.add_column('payable_accounts', sa.Column('contract_id', postgresql.UUID(as_uuid=True), nullable=True))

    # =========================================================================
    # TABLE: receivable_accounts
    # =========================================================================
    # Rename mismatched column
    op.execute("ALTER TABLE receivable_accounts RENAME COLUMN write_off_reason TO written_off_reason")

    # Add missing boolean flags
    op.add_column('receivable_accounts', sa.Column('boleto_generated', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('receivable_accounts', sa.Column('pix_generated', sa.Boolean(), nullable=True, server_default='false'))

    # =========================================================================
    # TABLE: cashflow_entries
    # =========================================================================
    # Rename mismatched columns
    op.execute("ALTER TABLE cashflow_entries RENAME COLUMN expected_date TO entry_date")
    op.execute("ALTER TABLE cashflow_entries RENAME COLUMN parent_entry_id TO recurrence_parent_id")

    # Add missing columns
    op.add_column('cashflow_entries', sa.Column('memo', sa.Text(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('difference', sa.Numeric(15, 2), nullable=True))
    op.add_column('cashflow_entries', sa.Column('competence_date', sa.Date(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('due_date', sa.Date(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('bank_transaction_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('is_transfer', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('cashflow_entries', sa.Column('transfer_to_account_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('transfer_entry_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('recurrence_day', sa.Integer(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('recurrence_start', sa.Date(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('recurrence_end', sa.Date(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('recurrence_count', sa.Integer(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('recurrence_index', sa.Integer(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('counterparty_type', sa.String(20), nullable=True))
    op.add_column('cashflow_entries', sa.Column('counterparty_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('counterparty_name', sa.String(150), nullable=True))
    op.add_column('cashflow_entries', sa.Column('cost_center_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('cost_center_name', sa.String(100), nullable=True))
    op.add_column('cashflow_entries', sa.Column('tags', postgresql.JSONB(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('is_essential', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('cashflow_entries', sa.Column('is_discretionary', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('cashflow_entries', sa.Column('is_budgeted', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('cashflow_entries', sa.Column('is_approved', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('cashflow_entries', sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('attachments', postgresql.JSONB(), nullable=True))
    op.add_column('cashflow_entries', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('payable_category_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('cashflow_entries', sa.Column('receivable_category_id', postgresql.UUID(as_uuid=True), nullable=True))

    # =========================================================================
    # TABLE: bank_accounts
    # =========================================================================
    # Rename mismatched columns
    op.execute("ALTER TABLE bank_accounts RENAME COLUMN initial_balance TO opening_balance")
    op.execute("ALTER TABLE bank_accounts RENAME COLUMN is_main TO is_main_account")

    # Add missing columns
    op.add_column('bank_accounts', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('bank_accounts', sa.Column('holder_name', sa.String(150), nullable=True))
    op.add_column('bank_accounts', sa.Column('holder_document', sa.String(20), nullable=True))
    op.add_column('bank_accounts', sa.Column('last_balance_update', sa.DateTime(timezone=True), nullable=True))
    op.add_column('bank_accounts', sa.Column('boleto_variation', sa.String(10), nullable=True))
    op.add_column('bank_accounts', sa.Column('boleto_assignor_code', sa.String(20), nullable=True))
    op.add_column('bank_accounts', sa.Column('integration_enabled', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('bank_accounts', sa.Column('integration_type', sa.String(30), nullable=True))
    op.add_column('bank_accounts', sa.Column('integration_config', postgresql.JSONB(), nullable=True))
    op.add_column('bank_accounts', sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('bank_accounts', sa.Column('last_sync_status', sa.String(20), nullable=True))
    op.add_column('bank_accounts', sa.Column('allow_negative_balance', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('bank_accounts', sa.Column('minimum_balance', sa.Numeric(15, 2), nullable=True, server_default='0'))
    op.add_column('bank_accounts', sa.Column('bank_manager_name', sa.String(100), nullable=True))
    op.add_column('bank_accounts', sa.Column('bank_manager_phone', sa.String(20), nullable=True))
    op.add_column('bank_accounts', sa.Column('bank_manager_email', sa.String(100), nullable=True))
    op.add_column('bank_accounts', sa.Column('opening_date', sa.Date(), nullable=True))
    op.add_column('bank_accounts', sa.Column('closing_date', sa.Date(), nullable=True))
    op.add_column('bank_accounts', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True))

    # =========================================================================
    # TABLE: customers
    # =========================================================================
    # Rename mismatched columns
    op.execute("ALTER TABLE customers RENAME COLUMN email_notifications TO notify_email")
    op.execute("ALTER TABLE customers RENAME COLUMN sms_notifications TO notify_sms")
    op.execute("ALTER TABLE customers RENAME COLUMN whatsapp_notifications TO notify_whatsapp")

    # Add missing address columns (plain, without billing_ prefix)
    op.add_column('customers', sa.Column('address_street', sa.String(200), nullable=True))
    op.add_column('customers', sa.Column('address_number', sa.String(20), nullable=True))
    op.add_column('customers', sa.Column('address_complement', sa.String(100), nullable=True))
    op.add_column('customers', sa.Column('address_neighborhood', sa.String(100), nullable=True))
    op.add_column('customers', sa.Column('address_city', sa.String(100), nullable=True))
    op.add_column('customers', sa.Column('address_state', sa.String(2), nullable=True))
    op.add_column('customers', sa.Column('address_zipcode', sa.String(10), nullable=True))
    op.add_column('customers', sa.Column('notify_push', sa.Boolean(), nullable=True, server_default='false'))

    # =========================================================================
    # TABLE: purchase_orders
    # =========================================================================
    op.add_column('purchase_orders', sa.Column('approval_notes', sa.Text(), nullable=True))
    op.add_column('purchase_orders', sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('purchase_orders', sa.Column('rejected_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('purchase_orders', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('purchase_orders', sa.Column('cancelled_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('purchase_orders', sa.Column('internal_notes', sa.Text(), nullable=True))
    op.add_column('purchase_orders', sa.Column('status_history', postgresql.JSONB(), nullable=True))

    # =========================================================================
    # TABLE: billing_rules
    # =========================================================================
    # Rename mismatched columns
    op.execute("ALTER TABLE billing_rules RENAME COLUMN calculation_type TO value_type")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN notify_days_before TO notify_before_days")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN notification_types TO notification_channels")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN apply_to_all_units TO apply_to_all")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN last_generation_date TO last_run_at")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN next_generation_date TO next_run_at")

    # Add missing columns
    op.add_column('billing_rules', sa.Column('reference_field', sa.String(50), nullable=True))
    op.add_column('billing_rules', sa.Column('apply_interest', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('billing_rules', sa.Column('apply_penalty', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('billing_rules', sa.Column('apply_discount', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('billing_rules', sa.Column('discount_rate', sa.Numeric(8, 4), nullable=True))
    op.add_column('billing_rules', sa.Column('discount_days', sa.Integer(), nullable=True))
    op.add_column('billing_rules', sa.Column('boleto_days_before', sa.Integer(), nullable=True))
    op.add_column('billing_rules', sa.Column('boleto_expiration_days', sa.Integer(), nullable=True))
    op.add_column('billing_rules', sa.Column('pix_expiration_hours', sa.Integer(), nullable=True))
    op.add_column('billing_rules', sa.Column('notifications_enabled', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('billing_rules', sa.Column('notify_after_days', postgresql.JSONB(), nullable=True))
    op.add_column('billing_rules', sa.Column('notification_time', sa.Time(), nullable=True))
    op.add_column('billing_rules', sa.Column('notification_templates', postgresql.JSONB(), nullable=True))
    op.add_column('billing_rules', sa.Column('unit_filter', postgresql.JSONB(), nullable=True))
    op.add_column('billing_rules', sa.Column('last_run_result', postgresql.JSONB(), nullable=True))
    op.add_column('billing_rules', sa.Column('total_collected', sa.Numeric(15, 2), nullable=True, server_default='0'))
    op.add_column('billing_rules', sa.Column('collection_rate', sa.Numeric(8, 4), nullable=True))
    op.add_column('billing_rules', sa.Column('ativo', sa.Boolean(), nullable=True, server_default='true'))


def downgrade():
    # Reverse all changes - suppliers
    op.execute("ALTER TABLE suppliers RENAME COLUMN blocked_reason TO block_reason")
    op.execute("ALTER TABLE suppliers RENAME COLUMN blocked_at TO block_date")
    op.execute("ALTER TABLE suppliers RENAME COLUMN qualified_at TO qualification_date")
    for col in ['code', 'whatsapp', 'contact_email', 'contact_phone', 'contact_position',
                'address_country', 'payment_terms_days', 'credit_limit', 'discount_percentage',
                'default_payment_method_id', 'rating', 'rating_count', 'documents']:
        op.drop_column('suppliers', col)

    # Reverse payable_accounts
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN discount_value TO discount")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN paid_value TO paid_amount")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withhold_iss TO withholding_iss")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withhold_ir TO withholding_ir")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withhold_pis TO withholding_pis")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withhold_cofins TO withholding_cofins")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withhold_csll TO withholding_csll")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN withhold_inss TO withholding_inss")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN total_installments TO installments")
    op.execute("ALTER TABLE payable_accounts RENAME COLUMN scheduled_payment_date TO scheduled_date")
    for col in ['addition_value', 'remaining_value', 'entry_date', 'payment_date', 'recurrence_end_date',
                'bank_account_id', 'approval_status', 'approval_notes', 'scheduled_at', 'internal_notes',
                'fiscal_document_type', 'fiscal_document_key', 'fiscal_document_url', 'contract_id']:
        op.drop_column('payable_accounts', col)

    # Reverse receivable_accounts
    op.execute("ALTER TABLE receivable_accounts RENAME COLUMN written_off_reason TO write_off_reason")
    op.drop_column('receivable_accounts', 'boleto_generated')
    op.drop_column('receivable_accounts', 'pix_generated')

    # Reverse cashflow_entries
    op.execute("ALTER TABLE cashflow_entries RENAME COLUMN entry_date TO expected_date")
    op.execute("ALTER TABLE cashflow_entries RENAME COLUMN recurrence_parent_id TO parent_entry_id")
    for col in ['memo', 'difference', 'competence_date', 'due_date', 'bank_transaction_id',
                'is_transfer', 'transfer_to_account_id', 'transfer_entry_id', 'recurrence_day',
                'recurrence_start', 'recurrence_end', 'recurrence_count', 'recurrence_index',
                'counterparty_type', 'counterparty_id', 'counterparty_name', 'cost_center_id',
                'cost_center_name', 'tags', 'is_essential', 'is_discretionary', 'is_budgeted',
                'is_approved', 'approved_by', 'approved_at', 'attachments', 'created_by',
                'payable_category_id', 'receivable_category_id']:
        op.drop_column('cashflow_entries', col)

    # Reverse bank_accounts
    op.execute("ALTER TABLE bank_accounts RENAME COLUMN opening_balance TO initial_balance")
    op.execute("ALTER TABLE bank_accounts RENAME COLUMN is_main_account TO is_main")
    for col in ['description', 'holder_name', 'holder_document', 'last_balance_update',
                'boleto_variation', 'boleto_assignor_code', 'integration_enabled', 'integration_type',
                'integration_config', 'last_sync_at', 'last_sync_status', 'allow_negative_balance',
                'minimum_balance', 'bank_manager_name', 'bank_manager_phone', 'bank_manager_email',
                'opening_date', 'closing_date', 'created_by']:
        op.drop_column('bank_accounts', col)

    # Reverse customers
    op.execute("ALTER TABLE customers RENAME COLUMN notify_email TO email_notifications")
    op.execute("ALTER TABLE customers RENAME COLUMN notify_sms TO sms_notifications")
    op.execute("ALTER TABLE customers RENAME COLUMN notify_whatsapp TO whatsapp_notifications")
    for col in ['address_street', 'address_number', 'address_complement', 'address_neighborhood',
                'address_city', 'address_state', 'address_zipcode', 'notify_push']:
        op.drop_column('customers', col)

    # Reverse purchase_orders
    for col in ['approval_notes', 'rejected_at', 'rejected_by', 'cancelled_at', 'cancelled_by',
                'internal_notes', 'status_history']:
        op.drop_column('purchase_orders', col)

    # Reverse billing_rules
    op.execute("ALTER TABLE billing_rules RENAME COLUMN value_type TO calculation_type")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN notify_before_days TO notify_days_before")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN notification_channels TO notification_types")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN apply_to_all TO apply_to_all_units")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN last_run_at TO last_generation_date")
    op.execute("ALTER TABLE billing_rules RENAME COLUMN next_run_at TO next_generation_date")
    for col in ['reference_field', 'apply_interest', 'apply_penalty', 'apply_discount', 'discount_rate',
                'discount_days', 'boleto_days_before', 'boleto_expiration_days', 'pix_expiration_hours',
                'notifications_enabled', 'notify_after_days', 'notification_time', 'notification_templates',
                'unit_filter', 'last_run_result', 'total_collected', 'collection_rate', 'ativo']:
        op.drop_column('billing_rules', col)
