"""Fix fin_charts_of_accounts: add missing columns and convert enum types.

Revision ID: sprint65_fix_charts_of_accounts
Revises: sprint64_convert_financial_enums
Create Date: 2026-03-09

"""

from alembic import op

revision = "sprint65_fix_charts_of_accounts"
down_revision = "sprint64_convert_financial_enums"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to fin_charts_of_accounts
    cols = [
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS version_date TIMESTAMPTZ",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS max_levels INTEGER DEFAULT 5",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS account_mask VARCHAR(50) DEFAULT '9.9.99.999.9999'",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS separator VARCHAR(1) DEFAULT '.'",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS sped_layout_code VARCHAR(10)",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS sped_version VARCHAR(20)",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS external_code VARCHAR(50)",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE",
        "ALTER TABLE fin_charts_of_accounts ADD COLUMN IF NOT EXISTS allow_modifications BOOLEAN DEFAULT TRUE",
    ]
    for col in cols:
        op.execute(col)

    # Convert enum columns to VARCHAR
    for col in ["chart_type", "status", "standard"]:
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'fin_charts_of_accounts'
                    AND column_name = '{col}'
                    AND udt_name NOT IN ('varchar', 'text', 'character varying', 'bpchar')
                ) THEN
                    ALTER TABLE fin_charts_of_accounts
                    ALTER COLUMN {col} TYPE VARCHAR(30) USING {col}::text;
                END IF;
            END$$
        """)


def downgrade() -> None:
    pass
