"""Create inventory tables for Sprint 26 - Estoque module.

Revision ID: sprint26_inventory
Revises: sprint25_create_purchase_tables
Create Date: 2024-12-31

Tables:
- fin_warehouses: Armazéns e depósitos
- fin_stock_items: Itens de estoque
- fin_stock_movements: Movimentações de estoque
- fin_stock_inventories: Inventários físicos
- fin_stock_inventory_items: Itens do inventário
- fin_stock_reservations: Reservas de estoque
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint26_inventory"
down_revision: Union[str, None] = "sprint25_create_purchase_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create inventory tables."""
    # ==========================================================================
    # ENUMS
    # ==========================================================================

    # Warehouse enums
    warehouse_type_enum = postgresql.ENUM(
        "CENTRAL",
        "REGIONAL",
        "TRANSIT",
        "RESERVED",
        "QUARANTINE",
        "RETURN",
        "VIRTUAL",
        "CONSIGNMENT",
        name="warehousetype",
        create_type=False,
    )
    warehouse_type_enum.create(op.get_bind(), checkfirst=True)

    warehouse_status_enum = postgresql.ENUM(
        "ACTIVE",
        "INACTIVE",
        "MAINTENANCE",
        "BLOCKED",
        "CLOSED",
        name="warehousestatus",
        create_type=False,
    )
    warehouse_status_enum.create(op.get_bind(), checkfirst=True)

    storage_type_enum = postgresql.ENUM(
        "GENERAL",
        "REFRIGERATED",
        "FROZEN",
        "HAZARDOUS",
        "HIGH_VALUE",
        "BULK",
        name="storagetype",
        create_type=False,
    )
    storage_type_enum.create(op.get_bind(), checkfirst=True)

    # Stock Item enums
    stock_item_status_enum = postgresql.ENUM(
        "AVAILABLE",
        "RESERVED",
        "BLOCKED",
        "QUARANTINE",
        "EXPIRED",
        "DAMAGED",
        "IN_TRANSIT",
        name="stockitemstatus",
        create_type=False,
    )
    stock_item_status_enum.create(op.get_bind(), checkfirst=True)

    costing_method_enum = postgresql.ENUM(
        "FIFO",
        "LIFO",
        "AVERAGE",
        "SPECIFIC",
        "STANDARD",
        name="costingmethod",
        create_type=False,
    )
    costing_method_enum.create(op.get_bind(), checkfirst=True)

    # Movement enums
    movement_type_enum = postgresql.ENUM(
        "ENTRY",
        "EXIT",
        "TRANSFER_OUT",
        "TRANSFER_IN",
        "ADJUSTMENT_PLUS",
        "ADJUSTMENT_MINUS",
        "RETURN_SUPPLIER",
        "RETURN_CUSTOMER",
        "PRODUCTION_IN",
        "PRODUCTION_OUT",
        "SCRAP",
        name="movementtype",
        create_type=False,
    )
    movement_type_enum.create(op.get_bind(), checkfirst=True)

    movement_reason_enum = postgresql.ENUM(
        "PURCHASE",
        "SALE",
        "TRANSFER",
        "INVENTORY_ADJUSTMENT",
        "PRODUCTION_CONSUMPTION",
        "PRODUCTION_OUTPUT",
        "RETURN_FROM_CUSTOMER",
        "RETURN_TO_SUPPLIER",
        "DAMAGED",
        "EXPIRED",
        "THEFT",
        "LOSS",
        "DONATION",
        "SAMPLE",
        "QUALITY_CONTROL",
        "REWORK",
        "SCRAP",
        "INITIAL_BALANCE",
        "CORRECTION",
        "OTHER",
        name="movementreason",
        create_type=False,
    )
    movement_reason_enum.create(op.get_bind(), checkfirst=True)

    movement_status_enum = postgresql.ENUM(
        "DRAFT",
        "PENDING",
        "CONFIRMED",
        "COMPLETED",
        "CANCELLED",
        "REVERSED",
        name="movementstatus",
        create_type=False,
    )
    movement_status_enum.create(op.get_bind(), checkfirst=True)

    # Inventory enums
    inventory_type_enum = postgresql.ENUM(
        "FULL",
        "PARTIAL",
        "CYCLIC",
        "BLIND",
        "ABC",
        "PERPETUAL",
        name="inventorytype",
        create_type=False,
    )
    inventory_type_enum.create(op.get_bind(), checkfirst=True)

    inventory_status_enum = postgresql.ENUM(
        "DRAFT",
        "SCHEDULED",
        "IN_PROGRESS",
        "COUNTING",
        "REVIEW",
        "ADJUSTMENT",
        "COMPLETED",
        "CANCELLED",
        "CLOSED",
        name="inventorystatus",
        create_type=False,
    )
    inventory_status_enum.create(op.get_bind(), checkfirst=True)

    inventory_item_status_enum = postgresql.ENUM(
        "PENDING",
        "COUNTED",
        "RECOUNTED",
        "DIVERGENT",
        "ADJUSTED",
        "APPROVED",
        name="inventoryitemstatus",
        create_type=False,
    )
    inventory_item_status_enum.create(op.get_bind(), checkfirst=True)

    # Reservation enums
    reservation_type_enum = postgresql.ENUM(
        "SALE",
        "PRODUCTION",
        "TRANSFER",
        "PROJECT",
        "SERVICE",
        "CONSIGNMENT",
        "SAMPLE",
        "OTHER",
        name="reservationtype",
        create_type=False,
    )
    reservation_type_enum.create(op.get_bind(), checkfirst=True)

    reservation_status_enum = postgresql.ENUM(
        "PENDING",
        "CONFIRMED",
        "PARTIAL",
        "CONSUMED",
        "RELEASED",
        "EXPIRED",
        name="reservationstatus",
        create_type=False,
    )
    reservation_status_enum.create(op.get_bind(), checkfirst=True)

    reservation_priority_enum = postgresql.ENUM(
        "LOW",
        "NORMAL",
        "HIGH",
        "URGENT",
        "CRITICAL",
        name="reservationpriority",
        create_type=False,
    )
    reservation_priority_enum.create(op.get_bind(), checkfirst=True)

    # ==========================================================================
    # TABLE: fin_warehouses
    # ==========================================================================
    op.create_table(
        "fin_warehouses",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Type and Status
        sa.Column(
            "warehouse_type",
            warehouse_type_enum,
            server_default="CENTRAL",
            nullable=False,
        ),
        sa.Column(
            "status",
            warehouse_status_enum,
            server_default="ACTIVE",
            nullable=False,
        ),
        sa.Column(
            "storage_type",
            storage_type_enum,
            server_default="GENERAL",
            nullable=False,
        ),
        # Hierarchy
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Location
        sa.Column("address", sa.String(200), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("zip_code", sa.String(10), nullable=True),
        sa.Column("country", sa.String(50), server_default="Brasil", nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        # Contact
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        # Capacity
        sa.Column("total_area_m2", sa.Numeric(12, 2), nullable=True),
        sa.Column("usable_area_m2", sa.Numeric(12, 2), nullable=True),
        sa.Column("max_weight_kg", sa.Numeric(15, 2), nullable=True),
        sa.Column("max_volume_m3", sa.Numeric(12, 2), nullable=True),
        sa.Column("current_occupancy_percent", sa.Numeric(5, 2), nullable=True),
        # Addressing
        sa.Column("has_addressing", sa.Boolean, server_default="false", nullable=False),
        sa.Column("addressing_levels", sa.Integer, nullable=True),
        sa.Column("address_format", sa.String(100), nullable=True),
        # Temperature Control
        sa.Column("temperature_controlled", sa.Boolean, server_default="false", nullable=False),
        sa.Column("min_temperature", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_temperature", sa.Numeric(5, 2), nullable=True),
        sa.Column("humidity_controlled", sa.Boolean, server_default="false", nullable=False),
        sa.Column("min_humidity", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_humidity", sa.Numeric(5, 2), nullable=True),
        # Security
        sa.Column("has_security", sa.Boolean, server_default="false", nullable=False),
        sa.Column("security_level", sa.String(20), nullable=True),
        sa.Column("has_cctv", sa.Boolean, server_default="false", nullable=False),
        sa.Column("has_access_control", sa.Boolean, server_default="false", nullable=False),
        # Operation
        sa.Column("operating_hours", sa.String(100), nullable=True),
        sa.Column("working_days", sa.String(50), nullable=True),
        sa.Column("cost_center", sa.String(50), nullable=True),
        # Integration
        sa.Column("external_code", sa.String(50), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Flags
        sa.Column("is_default", sa.Boolean, server_default="false", nullable=False),
        sa.Column("allow_negative_stock", sa.Boolean, server_default="false", nullable=False),
        sa.Column("require_batch", sa.Boolean, server_default="false", nullable=False),
        sa.Column("require_serial", sa.Boolean, server_default="false", nullable=False),
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["fin_warehouses.id"],
            name="fk_warehouse_parent",
        ),
    )

    # Indexes for fin_warehouses
    op.create_index("ix_fin_warehouses_condominio", "fin_warehouses", ["condominio_id"])
    op.create_index("ix_fin_warehouses_code", "fin_warehouses", ["code"])
    op.create_index("ix_fin_warehouses_name", "fin_warehouses", ["name"])
    op.create_index("ix_fin_warehouses_type", "fin_warehouses", ["warehouse_type"])
    op.create_index("ix_fin_warehouses_status", "fin_warehouses", ["status"])
    op.create_index("ix_fin_warehouses_parent", "fin_warehouses", ["parent_id"])
    op.create_index("ix_fin_warehouses_active", "fin_warehouses", ["active"])
    op.create_unique_constraint(
        "uq_fin_warehouses_code_condo",
        "fin_warehouses",
        ["condominio_id", "code"],
    )

    # ==========================================================================
    # TABLE: fin_stock_items
    # ==========================================================================
    op.create_table(
        "fin_stock_items",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # References
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("batch_number", sa.String(50), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("location_code", sa.String(50), nullable=True),
        # Status
        sa.Column(
            "status",
            stock_item_status_enum,
            server_default="AVAILABLE",
            nullable=False,
        ),
        # Quantities
        sa.Column("quantity_on_hand", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("quantity_reserved", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("quantity_committed", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("quantity_on_order", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("quantity_in_transit", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("quantity_available", sa.Numeric(15, 4), server_default="0", nullable=False),
        # Unit
        sa.Column("unit_of_measure", sa.String(20), nullable=False),
        sa.Column("conversion_factor", sa.Numeric(12, 6), server_default="1", nullable=False),
        # Costs
        sa.Column("unit_cost", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("total_cost", sa.Numeric(18, 4), server_default="0", nullable=False),
        sa.Column("average_cost", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("last_purchase_cost", sa.Numeric(15, 4), nullable=True),
        sa.Column("standard_cost", sa.Numeric(15, 4), nullable=True),
        sa.Column("replacement_cost", sa.Numeric(15, 4), nullable=True),
        # Costing
        sa.Column(
            "costing_method",
            costing_method_enum,
            server_default="AVERAGE",
            nullable=False,
        ),
        # Stock Levels
        sa.Column("minimum_stock", sa.Numeric(15, 4), nullable=True),
        sa.Column("maximum_stock", sa.Numeric(15, 4), nullable=True),
        sa.Column("reorder_point", sa.Numeric(15, 4), nullable=True),
        sa.Column("reorder_quantity", sa.Numeric(15, 4), nullable=True),
        sa.Column("safety_stock", sa.Numeric(15, 4), nullable=True),
        # Dates
        sa.Column("manufacturing_date", sa.Date, nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True),
        sa.Column("last_movement_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_count_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_purchase_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sale_date", sa.DateTime(timezone=True), nullable=True),
        # Analytics
        sa.Column("abc_class", sa.String(1), nullable=True),
        sa.Column("xyz_class", sa.String(1), nullable=True),
        sa.Column("turnover_rate", sa.Numeric(10, 4), nullable=True),
        sa.Column("days_of_stock", sa.Integer, nullable=True),
        # Attributes
        sa.Column("weight_kg", sa.Numeric(12, 4), nullable=True),
        sa.Column("volume_m3", sa.Numeric(12, 6), nullable=True),
        sa.Column("custom_attributes", postgresql.JSONB, nullable=True),
        # Flags
        sa.Column("is_blocked", sa.Boolean, server_default="false", nullable=False),
        sa.Column("block_reason", sa.String(200), nullable=True),
        sa.Column("requires_inspection", sa.Boolean, server_default="false", nullable=False),
        sa.Column("inspection_status", sa.String(20), nullable=True),
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["fin_warehouses.id"],
            name="fk_stock_item_warehouse",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["fin_products.id"],
            name="fk_stock_item_product",
        ),
    )

    # Indexes for fin_stock_items
    op.create_index("ix_fin_stock_items_condominio", "fin_stock_items", ["condominio_id"])
    op.create_index("ix_fin_stock_items_product", "fin_stock_items", ["product_id"])
    op.create_index("ix_fin_stock_items_warehouse", "fin_stock_items", ["warehouse_id"])
    op.create_index("ix_fin_stock_items_batch", "fin_stock_items", ["batch_number"])
    op.create_index("ix_fin_stock_items_serial", "fin_stock_items", ["serial_number"])
    op.create_index("ix_fin_stock_items_location", "fin_stock_items", ["location_code"])
    op.create_index("ix_fin_stock_items_status", "fin_stock_items", ["status"])
    op.create_index("ix_fin_stock_items_expiry", "fin_stock_items", ["expiry_date"])
    op.create_index("ix_fin_stock_items_abc", "fin_stock_items", ["abc_class"])
    op.create_index("ix_fin_stock_items_active", "fin_stock_items", ["active"])
    op.create_unique_constraint(
        "uq_fin_stock_items_product_warehouse_batch",
        "fin_stock_items",
        ["condominio_id", "product_id", "warehouse_id", "batch_number"],
    )

    # ==========================================================================
    # TABLE: fin_stock_movements
    # ==========================================================================
    op.create_table(
        "fin_stock_movements",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("movement_number", sa.String(30), nullable=False),
        # References
        sa.Column("stock_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Transfer (optional)
        sa.Column("destination_warehouse_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("destination_stock_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Type and Status
        sa.Column("movement_type", movement_type_enum, nullable=False),
        sa.Column("movement_reason", movement_reason_enum, nullable=False),
        sa.Column(
            "status",
            movement_status_enum,
            server_default="DRAFT",
            nullable=False,
        ),
        # Quantities
        sa.Column("quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("unit_of_measure", sa.String(20), nullable=False),
        sa.Column("quantity_base", sa.Numeric(15, 4), nullable=False),
        # Costs
        sa.Column("unit_cost", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("total_cost", sa.Numeric(18, 4), server_default="0", nullable=False),
        # Balance
        sa.Column("balance_before", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("balance_after", sa.Numeric(15, 4), server_default="0", nullable=False),
        # Batch/Serial
        sa.Column("batch_number", sa.String(50), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("location_code", sa.String(50), nullable=True),
        # Dates
        sa.Column("movement_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        # Source Document
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_number", sa.String(50), nullable=True),
        # Reversal
        sa.Column("is_reversal", sa.Boolean, server_default="false", nullable=False),
        sa.Column("reversed_movement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reversal_movement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reversal_reason", sa.String(200), nullable=True),
        # Approval
        sa.Column("requires_approval", sa.Boolean, server_default="false", nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Notes
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["stock_item_id"],
            ["fin_stock_items.id"],
            name="fk_movement_stock_item",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["fin_products.id"],
            name="fk_movement_product",
        ),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["fin_warehouses.id"],
            name="fk_movement_warehouse",
        ),
        sa.ForeignKeyConstraint(
            ["destination_warehouse_id"],
            ["fin_warehouses.id"],
            name="fk_movement_dest_warehouse",
        ),
        sa.ForeignKeyConstraint(
            ["destination_stock_item_id"],
            ["fin_stock_items.id"],
            name="fk_movement_dest_stock_item",
        ),
        sa.ForeignKeyConstraint(
            ["reversed_movement_id"],
            ["fin_stock_movements.id"],
            name="fk_movement_reversed",
        ),
        sa.ForeignKeyConstraint(
            ["reversal_movement_id"],
            ["fin_stock_movements.id"],
            name="fk_movement_reversal",
        ),
    )

    # Indexes for fin_stock_movements
    op.create_index("ix_fin_stock_movements_condominio", "fin_stock_movements", ["condominio_id"])
    op.create_index("ix_fin_stock_movements_number", "fin_stock_movements", ["movement_number"])
    op.create_index("ix_fin_stock_movements_stock_item", "fin_stock_movements", ["stock_item_id"])
    op.create_index("ix_fin_stock_movements_product", "fin_stock_movements", ["product_id"])
    op.create_index("ix_fin_stock_movements_warehouse", "fin_stock_movements", ["warehouse_id"])
    op.create_index("ix_fin_stock_movements_type", "fin_stock_movements", ["movement_type"])
    op.create_index("ix_fin_stock_movements_status", "fin_stock_movements", ["status"])
    op.create_index("ix_fin_stock_movements_date", "fin_stock_movements", ["movement_date"])
    op.create_index(
        "ix_fin_stock_movements_source", "fin_stock_movements", ["source_type", "source_id"]
    )
    op.create_unique_constraint(
        "uq_fin_stock_movements_number_condo",
        "fin_stock_movements",
        ["condominio_id", "movement_number"],
    )

    # ==========================================================================
    # TABLE: fin_stock_inventories
    # ==========================================================================
    op.create_table(
        "fin_stock_inventories",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("inventory_number", sa.String(30), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # References
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Type and Status
        sa.Column(
            "inventory_type",
            inventory_type_enum,
            server_default="FULL",
            nullable=False,
        ),
        sa.Column(
            "status",
            inventory_status_enum,
            server_default="DRAFT",
            nullable=False,
        ),
        # Scope
        sa.Column("scope_filter", postgresql.JSONB, nullable=True),
        sa.Column(
            "product_categories", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True
        ),
        sa.Column("abc_classes", postgresql.ARRAY(sa.String(1)), nullable=True),
        sa.Column("locations", postgresql.ARRAY(sa.String(50)), nullable=True),
        # Dates
        sa.Column("scheduled_date", sa.Date, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        # Reference Date
        sa.Column("reference_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cutoff_date", sa.DateTime(timezone=True), nullable=True),
        # Settings
        sa.Column("freeze_stock", sa.Boolean, server_default="false", nullable=False),
        sa.Column("blind_count", sa.Boolean, server_default="false", nullable=False),
        sa.Column("allow_recount", sa.Boolean, server_default="true", nullable=False),
        sa.Column("require_double_count", sa.Boolean, server_default="false", nullable=False),
        sa.Column("tolerance_percent", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("tolerance_value", sa.Numeric(15, 2), server_default="0", nullable=False),
        # Stats
        sa.Column("total_items", sa.Integer, server_default="0", nullable=False),
        sa.Column("counted_items", sa.Integer, server_default="0", nullable=False),
        sa.Column("divergent_items", sa.Integer, server_default="0", nullable=False),
        sa.Column("adjusted_items", sa.Integer, server_default="0", nullable=False),
        sa.Column("total_system_value", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_counted_value", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_divergence_value", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("accuracy_percent", sa.Numeric(5, 2), nullable=True),
        # Team
        sa.Column("supervisor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("team_members", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        # Approval
        sa.Column("requires_approval", sa.Boolean, server_default="true", nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["fin_warehouses.id"],
            name="fk_inventory_warehouse",
        ),
    )

    # Indexes for fin_stock_inventories
    op.create_index(
        "ix_fin_stock_inventories_condominio", "fin_stock_inventories", ["condominio_id"]
    )
    op.create_index(
        "ix_fin_stock_inventories_number", "fin_stock_inventories", ["inventory_number"]
    )
    op.create_index("ix_fin_stock_inventories_warehouse", "fin_stock_inventories", ["warehouse_id"])
    op.create_index("ix_fin_stock_inventories_type", "fin_stock_inventories", ["inventory_type"])
    op.create_index("ix_fin_stock_inventories_status", "fin_stock_inventories", ["status"])
    op.create_index(
        "ix_fin_stock_inventories_scheduled", "fin_stock_inventories", ["scheduled_date"]
    )
    op.create_unique_constraint(
        "uq_fin_stock_inventories_number_condo",
        "fin_stock_inventories",
        ["condominio_id", "inventory_number"],
    )

    # ==========================================================================
    # TABLE: fin_stock_inventory_items
    # ==========================================================================
    op.create_table(
        "fin_stock_inventory_items",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # References
        sa.Column("inventory_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stock_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Status
        sa.Column(
            "status",
            inventory_item_status_enum,
            server_default="PENDING",
            nullable=False,
        ),
        # Location
        sa.Column("location_code", sa.String(50), nullable=True),
        sa.Column("batch_number", sa.String(50), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        # System Quantities
        sa.Column("system_quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("system_value", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(15, 4), nullable=False),
        # Counted Quantities
        sa.Column("counted_quantity", sa.Numeric(15, 4), nullable=True),
        sa.Column("counted_value", sa.Numeric(18, 4), nullable=True),
        sa.Column("second_count_quantity", sa.Numeric(15, 4), nullable=True),
        # Divergence
        sa.Column("quantity_difference", sa.Numeric(15, 4), nullable=True),
        sa.Column("value_difference", sa.Numeric(18, 4), nullable=True),
        sa.Column("difference_percent", sa.Numeric(10, 4), nullable=True),
        sa.Column("is_within_tolerance", sa.Boolean, nullable=True),
        # Adjustment
        sa.Column("adjusted_quantity", sa.Numeric(15, 4), nullable=True),
        sa.Column("adjustment_movement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("adjustment_reason", sa.String(200), nullable=True),
        # Counting Info
        sa.Column("counted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("counted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("second_counted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("second_counted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("count_device", sa.String(50), nullable=True),
        # Approval
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["fin_stock_inventories.id"],
            name="fk_inv_item_inventory",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["stock_item_id"],
            ["fin_stock_items.id"],
            name="fk_inv_item_stock_item",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["fin_products.id"],
            name="fk_inv_item_product",
        ),
        sa.ForeignKeyConstraint(
            ["adjustment_movement_id"],
            ["fin_stock_movements.id"],
            name="fk_inv_item_adjustment",
        ),
    )

    # Indexes for fin_stock_inventory_items
    op.create_index(
        "ix_fin_stock_inv_items_inventory", "fin_stock_inventory_items", ["inventory_id"]
    )
    op.create_index(
        "ix_fin_stock_inv_items_stock_item", "fin_stock_inventory_items", ["stock_item_id"]
    )
    op.create_index("ix_fin_stock_inv_items_product", "fin_stock_inventory_items", ["product_id"])
    op.create_index("ix_fin_stock_inv_items_status", "fin_stock_inventory_items", ["status"])
    op.create_index(
        "ix_fin_stock_inv_items_location", "fin_stock_inventory_items", ["location_code"]
    )
    op.create_unique_constraint(
        "uq_fin_stock_inv_items_inv_stock",
        "fin_stock_inventory_items",
        ["inventory_id", "stock_item_id"],
    )

    # ==========================================================================
    # TABLE: fin_stock_reservations
    # ==========================================================================
    op.create_table(
        "fin_stock_reservations",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("reservation_number", sa.String(30), nullable=False),
        # References
        sa.Column("stock_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Type and Status
        sa.Column(
            "reservation_type",
            reservation_type_enum,
            server_default="SALE",
            nullable=False,
        ),
        sa.Column(
            "status",
            reservation_status_enum,
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column(
            "priority",
            reservation_priority_enum,
            server_default="NORMAL",
            nullable=False,
        ),
        # Quantities
        sa.Column("quantity_reserved", sa.Numeric(15, 4), nullable=False),
        sa.Column("quantity_released", sa.Numeric(15, 4), server_default="0", nullable=False),
        sa.Column("quantity_remaining", sa.Numeric(15, 4), nullable=False),
        sa.Column("unit_of_measure", sa.String(20), nullable=False),
        # Dates
        sa.Column("reservation_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        # Source Document
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_number", sa.String(50), nullable=True),
        sa.Column("source_line", sa.Integer, nullable=True),
        # Requestor
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("cost_center", sa.String(50), nullable=True),
        # Auto-release
        sa.Column("auto_release", sa.Boolean, server_default="false", nullable=False),
        sa.Column("auto_release_hours", sa.Integer, nullable=True),
        # Flags
        sa.Column("is_hard_reservation", sa.Boolean, server_default="false", nullable=False),
        sa.Column("allow_partial_release", sa.Boolean, server_default="true", nullable=False),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["stock_item_id"],
            ["fin_stock_items.id"],
            name="fk_reservation_stock_item",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["fin_products.id"],
            name="fk_reservation_product",
        ),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["fin_warehouses.id"],
            name="fk_reservation_warehouse",
        ),
    )

    # Indexes for fin_stock_reservations
    op.create_index(
        "ix_fin_stock_reservations_condominio", "fin_stock_reservations", ["condominio_id"]
    )
    op.create_index(
        "ix_fin_stock_reservations_number", "fin_stock_reservations", ["reservation_number"]
    )
    op.create_index(
        "ix_fin_stock_reservations_stock_item", "fin_stock_reservations", ["stock_item_id"]
    )
    op.create_index("ix_fin_stock_reservations_product", "fin_stock_reservations", ["product_id"])
    op.create_index(
        "ix_fin_stock_reservations_warehouse", "fin_stock_reservations", ["warehouse_id"]
    )
    op.create_index(
        "ix_fin_stock_reservations_type", "fin_stock_reservations", ["reservation_type"]
    )
    op.create_index("ix_fin_stock_reservations_status", "fin_stock_reservations", ["status"])
    op.create_index("ix_fin_stock_reservations_priority", "fin_stock_reservations", ["priority"])
    op.create_index("ix_fin_stock_reservations_expiry", "fin_stock_reservations", ["expiry_date"])
    op.create_index(
        "ix_fin_stock_reservations_source", "fin_stock_reservations", ["source_type", "source_id"]
    )
    op.create_unique_constraint(
        "uq_fin_stock_reservations_number_condo",
        "fin_stock_reservations",
        ["condominio_id", "reservation_number"],
    )


def downgrade() -> None:
    """Drop inventory tables."""
    # Drop tables in reverse order
    op.drop_table("fin_stock_reservations")
    op.drop_table("fin_stock_inventory_items")
    op.drop_table("fin_stock_inventories")
    op.drop_table("fin_stock_movements")
    op.drop_table("fin_stock_items")
    op.drop_table("fin_warehouses")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS reservationpriority")
    op.execute("DROP TYPE IF EXISTS reservationstatus")
    op.execute("DROP TYPE IF EXISTS reservationtype")
    op.execute("DROP TYPE IF EXISTS inventoryitemstatus")
    op.execute("DROP TYPE IF EXISTS inventorystatus")
    op.execute("DROP TYPE IF EXISTS inventorytype")
    op.execute("DROP TYPE IF EXISTS movementstatus")
    op.execute("DROP TYPE IF EXISTS movementreason")
    op.execute("DROP TYPE IF EXISTS movementtype")
    op.execute("DROP TYPE IF EXISTS costingmethod")
    op.execute("DROP TYPE IF EXISTS stockitemstatus")
    op.execute("DROP TYPE IF EXISTS storagetype")
    op.execute("DROP TYPE IF EXISTS warehousestatus")
    op.execute("DROP TYPE IF EXISTS warehousetype")
