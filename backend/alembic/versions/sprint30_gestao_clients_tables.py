"""Sprint 30 GESTAO: Create clients module tables

Revision ID: sprint30_gestao_clients
Revises: sprint32_create_diarists_tables
Create Date: 2026-01-01

Sprint 30 - Cadastro de Clientes/Condomínios
Módulo central para cadastro de clientes que serão gerenciados no ERP
e integrados com Guardian/Plus.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'sprint30_gestao_clients'
down_revision: Union[str, None] = 'sprint32_create_diarists_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create clients module tables."""

    # ========================================
    # ENUMS
    # ========================================

    # Client enums
    client_type_enum = postgresql.ENUM(
        'pf', 'pj', 'condominium', 'holding', 'franchise',
        'government', 'other',
        name='client_type_enum',
        create_type=False
    )

    client_status_enum = postgresql.ENUM(
        'prospect', 'active', 'suspended', 'blocked',
        'cancelled', 'defaulter', 'churned',
        name='client_status_enum',
        create_type=False
    )

    client_segment_enum = postgresql.ENUM(
        'small', 'medium', 'large', 'enterprise',
        'vip', 'strategic',
        name='client_segment_enum',
        create_type=False
    )

    document_type_enum = postgresql.ENUM(
        'cpf', 'cnpj', 'passport', 'rg', 'other',
        name='document_type_enum',
        create_type=False
    )

    # Condominium enums
    condominium_type_enum = postgresql.ENUM(
        'residential', 'commercial', 'mixed', 'industrial',
        'horizontal', 'gated_community', 'shopping',
        name='condominium_type_enum',
        create_type=False
    )

    condominium_status_enum = postgresql.ENUM(
        'prospect', 'implantation', 'active', 'suspended', 'cancelled',
        name='condominium_status_enum',
        create_type=False
    )

    administration_type_enum = postgresql.ENUM(
        'self_managed', 'administrator', 'property_manager', 'hybrid',
        name='administration_type_enum',
        create_type=False
    )

    # Unit enums
    unit_type_enum = postgresql.ENUM(
        'apartment', 'house', 'store', 'office', 'warehouse',
        'parking', 'storage', 'penthouse', 'duplex', 'triplex',
        'garden', 'rooftop', 'common_area', 'commercial',
        name='unit_type_enum',
        create_type=False
    )

    unit_status_enum = postgresql.ENUM(
        'available', 'occupied', 'vacant', 'renovation',
        'blocked', 'reserved', 'defaulter',
        name='unit_status_enum',
        create_type=False
    )

    # Contract enums
    contract_service_type_enum = postgresql.ENUM(
        'portaria_remota', 'controle_acesso', 'cftv', 'alarme',
        'cerca_eletrica', 'monitoramento_24h', 'app_morador',
        'assembleia_virtual', 'manutencao', 'limpeza', 'jardinagem',
        'administracao', 'consultoria', 'integracao', 'suporte',
        name='contract_service_type_enum',
        create_type=False
    )

    service_status_enum = postgresql.ENUM(
        'pending', 'implantation', 'active', 'suspended',
        'cancelled', 'finished',
        name='service_status_enum',
        create_type=False
    )

    # Integration enums
    integration_type_enum = postgresql.ENUM(
        'guardian', 'plus', 'erp_external', 'banking',
        'nfe', 'whatsapp', 'email', 'sms', 'webhook',
        name='integration_type_enum',
        create_type=False
    )

    sync_status_enum = postgresql.ENUM(
        'pending', 'syncing', 'synced', 'error', 'disabled',
        name='sync_status_enum',
        create_type=False
    )

    sync_direction_enum = postgresql.ENUM(
        'push', 'pull', 'bidirectional',
        name='sync_direction_enum',
        create_type=False
    )

    # Create all enums
    op.execute("CREATE TYPE client_type_enum AS ENUM ('pf', 'pj', 'condominium', 'holding', 'franchise', 'government', 'other')")
    op.execute("CREATE TYPE client_status_enum AS ENUM ('prospect', 'active', 'suspended', 'blocked', 'cancelled', 'defaulter', 'churned')")
    op.execute("CREATE TYPE client_segment_enum AS ENUM ('small', 'medium', 'large', 'enterprise', 'vip', 'strategic')")
    op.execute("CREATE TYPE document_type_enum AS ENUM ('cpf', 'cnpj', 'passport', 'rg', 'other')")
    op.execute("CREATE TYPE condominium_type_enum AS ENUM ('residential', 'commercial', 'mixed', 'industrial', 'horizontal', 'gated_community', 'shopping')")
    op.execute("CREATE TYPE condominium_status_enum AS ENUM ('prospect', 'implantation', 'active', 'suspended', 'cancelled')")
    op.execute("CREATE TYPE administration_type_enum AS ENUM ('self_managed', 'administrator', 'property_manager', 'hybrid')")
    op.execute("CREATE TYPE unit_type_enum AS ENUM ('apartment', 'house', 'store', 'office', 'warehouse', 'parking', 'storage', 'penthouse', 'duplex', 'triplex', 'garden', 'rooftop', 'common_area', 'commercial')")
    op.execute("CREATE TYPE unit_status_enum AS ENUM ('available', 'occupied', 'vacant', 'renovation', 'blocked', 'reserved', 'defaulter')")
    op.execute("CREATE TYPE contract_service_type_enum AS ENUM ('portaria_remota', 'controle_acesso', 'cftv', 'alarme', 'cerca_eletrica', 'monitoramento_24h', 'app_morador', 'assembleia_virtual', 'manutencao', 'limpeza', 'jardinagem', 'administracao', 'consultoria', 'integracao', 'suporte')")
    op.execute("CREATE TYPE service_status_enum AS ENUM ('pending', 'implantation', 'active', 'suspended', 'cancelled', 'finished')")
    op.execute("CREATE TYPE integration_type_enum AS ENUM ('guardian', 'plus', 'erp_external', 'banking', 'nfe', 'whatsapp', 'email', 'sms', 'webhook')")
    op.execute("CREATE TYPE sync_status_enum AS ENUM ('pending', 'syncing', 'synced', 'error', 'disabled')")
    op.execute("CREATE TYPE sync_direction_enum AS ENUM ('push', 'pull', 'bidirectional')")

    # ========================================
    # TABLE: clients
    # ========================================
    op.create_table(
        'clients',
        # Primary key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # Client code and identification
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('trading_name', sa.String(200), nullable=True),
        sa.Column('client_type', client_type_enum, nullable=False),

        # Documents
        sa.Column('document_type', document_type_enum, nullable=False),
        sa.Column('document_number', sa.String(20), nullable=False),
        sa.Column('state_registration', sa.String(30), nullable=True),
        sa.Column('municipal_registration', sa.String(30), nullable=True),

        # Contact
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('whatsapp', sa.String(20), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),

        # Address
        sa.Column('address_street', sa.String(255), nullable=True),
        sa.Column('address_number', sa.String(20), nullable=True),
        sa.Column('address_complement', sa.String(100), nullable=True),
        sa.Column('address_neighborhood', sa.String(100), nullable=True),
        sa.Column('address_city', sa.String(100), nullable=True),
        sa.Column('address_state', sa.String(2), nullable=True),
        sa.Column('address_zipcode', sa.String(10), nullable=True),
        sa.Column('address_country', sa.String(50), nullable=True, default='Brasil'),

        # Billing address
        sa.Column('billing_address_street', sa.String(255), nullable=True),
        sa.Column('billing_address_number', sa.String(20), nullable=True),
        sa.Column('billing_address_complement', sa.String(100), nullable=True),
        sa.Column('billing_address_neighborhood', sa.String(100), nullable=True),
        sa.Column('billing_address_city', sa.String(100), nullable=True),
        sa.Column('billing_address_state', sa.String(2), nullable=True),
        sa.Column('billing_address_zipcode', sa.String(10), nullable=True),

        # Financial contact
        sa.Column('financial_contact_name', sa.String(200), nullable=True),
        sa.Column('financial_contact_email', sa.String(255), nullable=True),
        sa.Column('financial_contact_phone', sa.String(20), nullable=True),

        # Technical contact
        sa.Column('technical_contact_name', sa.String(200), nullable=True),
        sa.Column('technical_contact_email', sa.String(255), nullable=True),
        sa.Column('technical_contact_phone', sa.String(20), nullable=True),

        # Status and segment
        sa.Column('status', client_status_enum, nullable=False, default='prospect'),
        sa.Column('segment', client_segment_enum, nullable=True),

        # Dates
        sa.Column('contract_start_date', sa.Date, nullable=True),
        sa.Column('contract_end_date', sa.Date, nullable=True),
        sa.Column('first_billing_date', sa.Date, nullable=True),
        sa.Column('last_billing_date', sa.Date, nullable=True),

        # Financial
        sa.Column('credit_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('payment_terms', sa.Integer, nullable=True, default=30),
        sa.Column('billing_day', sa.Integer, nullable=True, default=10),
        sa.Column('total_revenue', sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column('total_debt', sa.Numeric(15, 2), nullable=True, default=0),

        # Metrics
        sa.Column('health_score', sa.Float, nullable=True),
        sa.Column('satisfaction_score', sa.Float, nullable=True),
        sa.Column('engagement_score', sa.Float, nullable=True),

        # Integration flags
        sa.Column('guardian_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('plus_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('guardian_client_id', sa.String(50), nullable=True),
        sa.Column('plus_client_id', sa.String(50), nullable=True),

        # Metadata
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('tags', postgresql.JSONB, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),

        # FKs
        sa.Column('account_manager_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sales_rep_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Audit
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Indexes for clients
    op.create_index('ix_clients_code', 'clients', ['code'])
    op.create_index('ix_clients_name', 'clients', ['name'])
    op.create_index('ix_clients_document_number', 'clients', ['document_number'])
    op.create_index('ix_clients_email', 'clients', ['email'])
    op.create_index('ix_clients_status', 'clients', ['status'])
    op.create_index('ix_clients_client_type', 'clients', ['client_type'])
    op.create_index('ix_clients_segment', 'clients', ['segment'])
    op.create_index('ix_clients_guardian_enabled', 'clients', ['guardian_enabled'])
    op.create_index('ix_clients_plus_enabled', 'clients', ['plus_enabled'])
    op.create_index('ix_clients_ativo', 'clients', ['ativo'])
    op.create_index('ix_clients_created_at', 'clients', ['created_at'])

    # ========================================
    # TABLE: condominiums
    # ========================================
    op.create_table(
        'condominiums',
        # Primary key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # FK to client
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False),

        # Identification
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('trading_name', sa.String(200), nullable=True),
        sa.Column('cnpj', sa.String(18), nullable=True),

        # Type and status
        sa.Column('condominium_type', condominium_type_enum, nullable=False),
        sa.Column('status', condominium_status_enum, nullable=False, default='prospect'),
        sa.Column('administration_type', administration_type_enum, nullable=True),

        # Address
        sa.Column('address_street', sa.String(255), nullable=True),
        sa.Column('address_number', sa.String(20), nullable=True),
        sa.Column('address_complement', sa.String(100), nullable=True),
        sa.Column('address_neighborhood', sa.String(100), nullable=True),
        sa.Column('address_city', sa.String(100), nullable=True),
        sa.Column('address_state', sa.String(2), nullable=True),
        sa.Column('address_zipcode', sa.String(10), nullable=True),
        sa.Column('latitude', sa.Float, nullable=True),
        sa.Column('longitude', sa.Float, nullable=True),

        # Physical characteristics
        sa.Column('total_units', sa.Integer, nullable=True, default=0),
        sa.Column('total_towers', sa.Integer, nullable=True, default=1),
        sa.Column('total_floors', sa.Integer, nullable=True, default=1),
        sa.Column('total_parking_spaces', sa.Integer, nullable=True, default=0),
        sa.Column('total_common_areas', sa.Integer, nullable=True, default=0),
        sa.Column('built_area', sa.Float, nullable=True),
        sa.Column('total_area', sa.Float, nullable=True),
        sa.Column('construction_year', sa.Integer, nullable=True),

        # Amenities
        sa.Column('has_pool', sa.Boolean, nullable=False, default=False),
        sa.Column('has_gym', sa.Boolean, nullable=False, default=False),
        sa.Column('has_party_room', sa.Boolean, nullable=False, default=False),
        sa.Column('has_playground', sa.Boolean, nullable=False, default=False),
        sa.Column('has_sports_court', sa.Boolean, nullable=False, default=False),
        sa.Column('has_sauna', sa.Boolean, nullable=False, default=False),
        sa.Column('has_barbecue', sa.Boolean, nullable=False, default=False),
        sa.Column('has_garden', sa.Boolean, nullable=False, default=False),
        sa.Column('amenities', postgresql.JSONB, nullable=True),

        # Security features
        sa.Column('has_cctv', sa.Boolean, nullable=False, default=False),
        sa.Column('has_access_control', sa.Boolean, nullable=False, default=False),
        sa.Column('has_intercom', sa.Boolean, nullable=False, default=False),
        sa.Column('has_24h_security', sa.Boolean, nullable=False, default=False),
        sa.Column('has_electric_fence', sa.Boolean, nullable=False, default=False),
        sa.Column('has_alarm', sa.Boolean, nullable=False, default=False),
        sa.Column('total_cameras', sa.Integer, nullable=True, default=0),
        sa.Column('total_access_points', sa.Integer, nullable=True, default=0),

        # Syndic information
        sa.Column('syndic_name', sa.String(200), nullable=True),
        sa.Column('syndic_email', sa.String(255), nullable=True),
        sa.Column('syndic_phone', sa.String(20), nullable=True),
        sa.Column('syndic_cpf', sa.String(14), nullable=True),
        sa.Column('syndic_mandate_start', sa.Date, nullable=True),
        sa.Column('syndic_mandate_end', sa.Date, nullable=True),

        # Administrator information
        sa.Column('administrator_name', sa.String(200), nullable=True),
        sa.Column('administrator_cnpj', sa.String(18), nullable=True),
        sa.Column('administrator_email', sa.String(255), nullable=True),
        sa.Column('administrator_phone', sa.String(20), nullable=True),

        # Dates
        sa.Column('implantation_start_date', sa.Date, nullable=True),
        sa.Column('implantation_end_date', sa.Date, nullable=True),
        sa.Column('activation_date', sa.Date, nullable=True),

        # Metadata
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('tags', postgresql.JSONB, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),

        # Audit
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Indexes for condominiums
    op.create_index('ix_condominiums_client_id', 'condominiums', ['client_id'])
    op.create_index('ix_condominiums_code', 'condominiums', ['code'])
    op.create_index('ix_condominiums_name', 'condominiums', ['name'])
    op.create_index('ix_condominiums_cnpj', 'condominiums', ['cnpj'])
    op.create_index('ix_condominiums_status', 'condominiums', ['status'])
    op.create_index('ix_condominiums_type', 'condominiums', ['condominium_type'])
    op.create_index('ix_condominiums_city_state', 'condominiums', ['address_city', 'address_state'])
    op.create_index('ix_condominiums_ativo', 'condominiums', ['ativo'])

    # ========================================
    # TABLE: units
    # ========================================
    op.create_table(
        'units',
        # Primary key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # FK to condominium
        sa.Column('condominium_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('condominiums.id', ondelete='CASCADE'), nullable=False),

        # Identification
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('unit_number', sa.String(20), nullable=False),
        sa.Column('block', sa.String(50), nullable=True),
        sa.Column('tower', sa.String(50), nullable=True),
        sa.Column('floor', sa.Integer, nullable=True),

        # Type and status
        sa.Column('unit_type', unit_type_enum, nullable=False),
        sa.Column('status', unit_status_enum, nullable=False, default='available'),

        # Physical characteristics
        sa.Column('private_area', sa.Float, nullable=True),
        sa.Column('total_area', sa.Float, nullable=True),
        sa.Column('bedrooms', sa.Integer, nullable=True),
        sa.Column('bathrooms', sa.Integer, nullable=True),
        sa.Column('parking_spaces', sa.Integer, nullable=True),

        # Owner information
        sa.Column('owner_name', sa.String(200), nullable=True),
        sa.Column('owner_document', sa.String(20), nullable=True),
        sa.Column('owner_email', sa.String(255), nullable=True),
        sa.Column('owner_phone', sa.String(20), nullable=True),
        sa.Column('owner_mobile', sa.String(20), nullable=True),

        # Resident information
        sa.Column('resident_name', sa.String(200), nullable=True),
        sa.Column('resident_document', sa.String(20), nullable=True),
        sa.Column('resident_email', sa.String(255), nullable=True),
        sa.Column('resident_phone', sa.String(20), nullable=True),
        sa.Column('resident_mobile', sa.String(20), nullable=True),
        sa.Column('resident_type', sa.String(20), nullable=True),  # owner, tenant, relative

        # Financial
        sa.Column('condominium_fee', sa.Numeric(10, 2), nullable=True),
        sa.Column('extra_fee', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_defaulter', sa.Boolean, nullable=False, default=False),
        sa.Column('debt_amount', sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column('last_payment_date', sa.Date, nullable=True),

        # Access credentials
        sa.Column('access_card', sa.String(50), nullable=True),
        sa.Column('access_tag', sa.String(50), nullable=True),
        sa.Column('biometric_registered', sa.Boolean, nullable=False, default=False),
        sa.Column('facial_registered', sa.Boolean, nullable=False, default=False),
        sa.Column('app_registered', sa.Boolean, nullable=False, default=False),

        # Vehicles
        sa.Column('vehicles', postgresql.JSONB, nullable=True),

        # Emergency contact
        sa.Column('emergency_contact_name', sa.String(200), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(20), nullable=True),
        sa.Column('emergency_contact_relationship', sa.String(50), nullable=True),

        # Metadata
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('tags', postgresql.JSONB, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),

        # Audit
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Unique constraint
        sa.UniqueConstraint('condominium_id', 'code', name='uq_units_condominium_code'),
    )

    # Indexes for units
    op.create_index('ix_units_condominium_id', 'units', ['condominium_id'])
    op.create_index('ix_units_code', 'units', ['code'])
    op.create_index('ix_units_unit_number', 'units', ['unit_number'])
    op.create_index('ix_units_block', 'units', ['block'])
    op.create_index('ix_units_tower', 'units', ['tower'])
    op.create_index('ix_units_status', 'units', ['status'])
    op.create_index('ix_units_unit_type', 'units', ['unit_type'])
    op.create_index('ix_units_owner_document', 'units', ['owner_document'])
    op.create_index('ix_units_resident_document', 'units', ['resident_document'])
    op.create_index('ix_units_is_defaulter', 'units', ['is_defaulter'])
    op.create_index('ix_units_ativo', 'units', ['ativo'])

    # ========================================
    # TABLE: client_contracts
    # ========================================
    op.create_table(
        'client_contracts',
        # Primary key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # FK to client
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False),

        # Optional FK to condominium
        sa.Column('condominium_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('condominiums.id', ondelete='SET NULL'), nullable=True),

        # Contract identification
        sa.Column('contract_number', sa.String(50), nullable=False, unique=True),
        sa.Column('service_type', contract_service_type_enum, nullable=False),
        sa.Column('status', service_status_enum, nullable=False, default='pending'),

        # Description
        sa.Column('description', sa.Text, nullable=True),

        # Dates
        sa.Column('start_date', sa.Date, nullable=True),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('implantation_start_date', sa.Date, nullable=True),
        sa.Column('implantation_end_date', sa.Date, nullable=True),
        sa.Column('activation_date', sa.Date, nullable=True),
        sa.Column('cancellation_date', sa.Date, nullable=True),

        # Financial
        sa.Column('monthly_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('implantation_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('discount_percentage', sa.Float, nullable=True),
        sa.Column('billing_day', sa.Integer, nullable=True, default=10),

        # SLA configuration
        sa.Column('sla_response_time', sa.Integer, nullable=True),  # minutes
        sa.Column('sla_resolution_time', sa.Integer, nullable=True),  # hours
        sa.Column('sla_availability', sa.Float, nullable=True, default=99.9),
        sa.Column('sla_config', postgresql.JSONB, nullable=True),

        # Renewal
        sa.Column('auto_renewal', sa.Boolean, nullable=False, default=True),
        sa.Column('renewal_period_months', sa.Integer, nullable=True, default=12),
        sa.Column('notice_period_days', sa.Integer, nullable=True, default=30),

        # Metadata
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),

        # Audit
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Indexes for client_contracts
    op.create_index('ix_client_contracts_client_id', 'client_contracts', ['client_id'])
    op.create_index('ix_client_contracts_condominium_id', 'client_contracts', ['condominium_id'])
    op.create_index('ix_client_contracts_contract_number', 'client_contracts', ['contract_number'])
    op.create_index('ix_client_contracts_service_type', 'client_contracts', ['service_type'])
    op.create_index('ix_client_contracts_status', 'client_contracts', ['status'])
    op.create_index('ix_client_contracts_start_date', 'client_contracts', ['start_date'])
    op.create_index('ix_client_contracts_end_date', 'client_contracts', ['end_date'])
    op.create_index('ix_client_contracts_ativo', 'client_contracts', ['ativo'])

    # ========================================
    # TABLE: integration_settings
    # ========================================
    op.create_table(
        'integration_settings',
        # Primary key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),

        # FK to client
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False),

        # Optional FK to condominium
        sa.Column('condominium_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('condominiums.id', ondelete='SET NULL'), nullable=True),

        # Integration identification
        sa.Column('integration_type', integration_type_enum, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),

        # Status
        sa.Column('enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('sync_status', sync_status_enum, nullable=False, default='pending'),
        sa.Column('sync_direction', sync_direction_enum, nullable=False, default='bidirectional'),

        # API configuration
        sa.Column('api_url', sa.String(500), nullable=True),
        sa.Column('api_key', sa.String(255), nullable=True),
        sa.Column('api_secret', sa.String(255), nullable=True),
        sa.Column('api_token', sa.Text, nullable=True),
        sa.Column('api_version', sa.String(20), nullable=True),

        # Authentication
        sa.Column('auth_type', sa.String(50), nullable=True),  # api_key, oauth2, basic, jwt
        sa.Column('auth_config', postgresql.JSONB, nullable=True),

        # Webhook configuration
        sa.Column('webhook_url', sa.String(500), nullable=True),
        sa.Column('webhook_secret', sa.String(255), nullable=True),
        sa.Column('webhook_events', postgresql.ARRAY(sa.String), nullable=True),

        # Sync configuration
        sa.Column('sync_interval_minutes', sa.Integer, nullable=True, default=60),
        sa.Column('last_sync_at', sa.DateTime, nullable=True),
        sa.Column('next_sync_at', sa.DateTime, nullable=True),
        sa.Column('last_sync_status', sa.String(50), nullable=True),
        sa.Column('last_sync_message', sa.Text, nullable=True),
        sa.Column('sync_config', postgresql.JSONB, nullable=True),

        # External IDs
        sa.Column('external_client_id', sa.String(100), nullable=True),
        sa.Column('external_config', postgresql.JSONB, nullable=True),

        # Metadata
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),

        # Audit
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Unique constraint
        sa.UniqueConstraint('client_id', 'integration_type', 'condominium_id', name='uq_integration_client_type_condo'),
    )

    # Indexes for integration_settings
    op.create_index('ix_integration_settings_client_id', 'integration_settings', ['client_id'])
    op.create_index('ix_integration_settings_condominium_id', 'integration_settings', ['condominium_id'])
    op.create_index('ix_integration_settings_type', 'integration_settings', ['integration_type'])
    op.create_index('ix_integration_settings_enabled', 'integration_settings', ['enabled'])
    op.create_index('ix_integration_settings_sync_status', 'integration_settings', ['sync_status'])
    op.create_index('ix_integration_settings_ativo', 'integration_settings', ['ativo'])


def downgrade() -> None:
    """Drop clients module tables."""

    # Drop tables in reverse order (respecting FKs)
    op.drop_table('integration_settings')
    op.drop_table('client_contracts')
    op.drop_table('units')
    op.drop_table('condominiums')
    op.drop_table('clients')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS sync_direction_enum")
    op.execute("DROP TYPE IF EXISTS sync_status_enum")
    op.execute("DROP TYPE IF EXISTS integration_type_enum")
    op.execute("DROP TYPE IF EXISTS service_status_enum")
    op.execute("DROP TYPE IF EXISTS contract_service_type_enum")
    op.execute("DROP TYPE IF EXISTS unit_status_enum")
    op.execute("DROP TYPE IF EXISTS unit_type_enum")
    op.execute("DROP TYPE IF EXISTS administration_type_enum")
    op.execute("DROP TYPE IF EXISTS condominium_status_enum")
    op.execute("DROP TYPE IF EXISTS condominium_type_enum")
    op.execute("DROP TYPE IF EXISTS document_type_enum")
    op.execute("DROP TYPE IF EXISTS client_segment_enum")
    op.execute("DROP TYPE IF EXISTS client_status_enum")
    op.execute("DROP TYPE IF EXISTS client_type_enum")
