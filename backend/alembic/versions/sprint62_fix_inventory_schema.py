"""Fix inventory schema - add missing columns to fin_warehouses and related tables.

Revision ID: sprint62_fix_inventory_schema
Revises: sprint61_add_supplier_cnae
Create Date: 2026-03-08

"""

from alembic import op

revision = "sprint62_fix_inventory_schema"
down_revision = "sprint61_add_supplier_cnae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # fin_warehouses: add missing columns
    cols = [
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS short_name VARCHAR(30)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS manager_name VARCHAR(100)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS manager_email VARCHAR(200)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS manager_phone VARCHAR(20)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS storage_area_m2 NUMERIC(10,2)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS total_positions VARCHAR(10) DEFAULT '0'",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS occupied_positions VARCHAR(10) DEFAULT '0'",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS current_weight_kg NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS addressing_format VARCHAR(50)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS current_temperature NUMERIC(5,2)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS last_temperature_check TIMESTAMP",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS has_alarm BOOLEAN DEFAULT FALSE",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS has_fire_system BOOLEAN DEFAULT FALSE",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS access_control_type VARCHAR(50)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS opening_time VARCHAR(5)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS closing_time VARCHAR(5)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS works_24h BOOLEAN DEFAULT FALSE",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS monthly_cost NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS cost_per_m2 NUMERIC(10,2)",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS total_items VARCHAR(10) DEFAULT '0'",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS total_quantity NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS total_value NUMERIC(15,2) DEFAULT 0",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS last_movement_at TIMESTAMP",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS last_inventory_at TIMESTAMP",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS allows_negative_stock BOOLEAN DEFAULT FALSE",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS fifo_enabled BOOLEAN DEFAULT TRUE",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS auto_reorder BOOLEAN DEFAULT FALSE",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS blocked_reason TEXT",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS blocked_at TIMESTAMP",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS blocked_by UUID",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS internal_notes TEXT",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS extra_data JSONB DEFAULT '{}'",
        "ALTER TABLE fin_warehouses ADD COLUMN IF NOT EXISTS ativo BOOLEAN DEFAULT TRUE NOT NULL",
    ]
    for col in cols:
        op.execute(col)

    # fin_stock_items: check for missing columns
    stock_item_cols = [
        "ALTER TABLE fin_stock_items ADD COLUMN IF NOT EXISTS ativo BOOLEAN DEFAULT TRUE NOT NULL",
        "ALTER TABLE fin_stock_items ADD COLUMN IF NOT EXISTS extra_data JSONB DEFAULT '{}'",
    ]
    for col in stock_item_cols:
        op.execute(col)


def downgrade() -> None:
    pass
