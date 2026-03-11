"""Add financial_contract_costs table for contract costing (Phase 3).

Revision ID: sprint66_add_contract_costs
Revises: sprint65_fix_charts_of_accounts
Create Date: 2026-03-09

"""

from alembic import op

revision = "sprint66_add_contract_costs"
down_revision = "sprint65_fix_charts_of_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure enum type exists (idempotent)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'servicetype') THEN
                CREATE TYPE servicetype AS ENUM (
                    'portaria',
                    'limpeza',
                    'jardinagem',
                    'seguranca_eletronica',
                    'portaria_remota'
                );
            END IF;
        END$$
        """
    )

    # Create table using raw SQL to avoid SQLAlchemy re-creating the enum type
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS financial_contract_costs (
            id              UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            contract_id     VARCHAR(255) NOT NULL,
            contract_name   VARCHAR(255) NOT NULL,
            service_type    servicetype NOT NULL,
            reference_month DATE NOT NULL,

            -- Mão de obra
            labor_base          NUMERIC(12,2) DEFAULT 0,
            labor_overtime_50   NUMERIC(12,2) DEFAULT 0,
            labor_overtime_100  NUMERIC(12,2) DEFAULT 0,
            labor_night_add     NUMERIC(12,2) DEFAULT 0,
            labor_charges       NUMERIC(12,2) DEFAULT 0,
            labor_provisions    NUMERIC(12,2) DEFAULT 0,

            -- Benefícios
            benefit_vt     NUMERIC(12,2) DEFAULT 0,
            benefit_vr     NUMERIC(12,2) DEFAULT 0,
            benefit_va     NUMERIC(12,2) DEFAULT 0,
            benefit_health NUMERIC(12,2) DEFAULT 0,
            benefit_other  NUMERIC(12,2) DEFAULT 0,

            -- Materiais/Insumos
            materials_uniforms    NUMERIC(12,2) DEFAULT 0,
            materials_supplies    NUMERIC(12,2) DEFAULT 0,
            materials_equipment   NUMERIC(12,2) DEFAULT 0,
            materials_maintenance NUMERIC(12,2) DEFAULT 0,

            -- Conectividade/Tecnologia
            tech_connectivity NUMERIC(12,2) DEFAULT 0,
            tech_monitoring   NUMERIC(12,2) DEFAULT 0,
            tech_software     NUMERIC(12,2) DEFAULT 0,

            -- Rateios administrativos
            overhead_supervision NUMERIC(12,2) DEFAULT 0,
            overhead_admin       NUMERIC(12,2) DEFAULT 0,
            overhead_commercial  NUMERIC(12,2) DEFAULT 0,

            -- Métricas calculadas
            total_cost       NUMERIC(12,2) DEFAULT 0,
            contract_revenue NUMERIC(12,2) DEFAULT 0,
            gross_margin     NUMERIC(5,2)  DEFAULT 0,

            -- Métricas específicas por tipo
            qty_workers  INTEGER DEFAULT 0,
            area_m2      NUMERIC(10,2) DEFAULT 0,
            qty_units    INTEGER DEFAULT 0,
            qty_cameras  INTEGER DEFAULT 0,

            -- Auditoria
            notes      VARCHAR(500),
            created_at DATE DEFAULT CURRENT_DATE
        )
        """
    )

    # Indexes (IF NOT EXISTS to be idempotent)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_financial_contract_costs_contract_id ON financial_contract_costs (contract_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_financial_contract_costs_reference_month "
        "ON financial_contract_costs (reference_month)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_financial_contract_costs_contract_month "
        "ON financial_contract_costs (contract_id, reference_month)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_financial_contract_costs_service_month "
        "ON financial_contract_costs (service_type, reference_month)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS financial_contract_costs")
    op.execute("DROP TYPE IF EXISTS servicetype")
