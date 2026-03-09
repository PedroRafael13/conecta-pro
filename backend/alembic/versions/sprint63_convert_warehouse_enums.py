"""Convert warehouse enum columns to VARCHAR to match model String types.

Revision ID: sprint63_convert_warehouse_enums
Revises: sprint62_fix_inventory_schema
Create Date: 2026-03-08

"""

from alembic import op

revision = "sprint63_convert_warehouse_enums"
down_revision = "sprint62_fix_inventory_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert PostgreSQL enum columns to VARCHAR so model String types work
    op.execute(
        "ALTER TABLE fin_warehouses "
        "ALTER COLUMN warehouse_type TYPE VARCHAR(20) USING warehouse_type::text"
    )
    op.execute(
        "ALTER TABLE fin_warehouses "
        "ALTER COLUMN status TYPE VARCHAR(20) USING status::text"
    )
    op.execute(
        "ALTER TABLE fin_warehouses "
        "ALTER COLUMN storage_type TYPE VARCHAR(20) USING storage_type::text"
    )

    # Also check fin_stock_items for enum columns
    # Get column types first - do ALTER IF the column is an enum type
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'fin_stock_items'
                AND column_name = 'status'
                AND udt_name NOT IN ('varchar', 'text', 'character varying')
            ) THEN
                ALTER TABLE fin_stock_items ALTER COLUMN status TYPE VARCHAR(20) USING status::text;
            END IF;
        END$$
    """)


def downgrade() -> None:
    pass
