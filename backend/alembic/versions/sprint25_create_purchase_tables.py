"""Sprint 25: Cria tabelas de Compras.

Revision ID: sprint25_purchase
Revises: c8f5a3b2d1e0_create_cashflow_tables
Create Date: 2024-12-31

Tabelas criadas:
- product_categories: Categorias de produtos
- products: Produtos/serviços
- purchase_requisitions: Requisições de compra
- purchase_requisition_items: Itens de requisição
- purchase_quotations: Cotações de fornecedores
- purchase_quotation_items: Itens de cotação
- purchase_orders: Ordens de compra
- purchase_order_items: Itens de ordem
- goods_receipts: Recebimentos de mercadorias
- goods_receipt_items: Itens de recebimento
- purchase_approvals: Aprovações de compra
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "sprint25_purchase"
down_revision = "c8f5a3b2d1e0_create_cashflow_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas de Compras."""

    # =========================================================================
    # Tabela: product_categories
    # Categorias de produtos/serviços
    # =========================================================================
    op.create_table(
        "product_categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Identificação
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo
        sa.Column(
            "category_type",
            sa.String(20),
            nullable=False,
            server_default="material",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="ativa",
        ),
        # Hierarquia
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("product_categories.id"),
            nullable=True,
        ),
        sa.Column("path", sa.String(500), nullable=True),
        sa.Column("depth", sa.Integer, server_default="0"),
        sa.Column("full_name", sa.String(500), nullable=True),
        # Configurações
        sa.Column("allow_purchase", sa.Boolean, server_default="true"),
        sa.Column("require_specification", sa.Boolean, server_default="false"),
        sa.Column("require_quotation", sa.Boolean, server_default="true"),
        sa.Column("minimum_quotations", sa.Integer, server_default="3"),
        # Contabilidade
        sa.Column("accounting_code", sa.String(20), nullable=True),
        sa.Column("cost_center_default", sa.String(50), nullable=True),
        # Exibição
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("display_order", sa.Integer, server_default="0"),
        # Flags
        sa.Column("is_system", sa.Boolean, server_default="false"),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_product_categories_code_condo",
        "product_categories",
        ["code", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_product_categories_parent", "product_categories", ["parent_id"])

    # =========================================================================
    # Tabela: products
    # Produtos e serviços para compra
    # =========================================================================
    op.create_table(
        "products",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("product_categories.id"),
            nullable=True,
            index=True,
        ),
        # Identificação
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("short_name", sa.String(50), nullable=True),
        # Tipo e unidade
        sa.Column(
            "product_type",
            sa.String(20),
            nullable=False,
            server_default="material",
        ),
        sa.Column("unit_of_measure", sa.String(10), server_default="un"),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="ativo",
        ),
        # Códigos
        sa.Column("barcode", sa.String(50), nullable=True),
        sa.Column("ncm", sa.String(10), nullable=True),
        sa.Column("manufacturer_code", sa.String(50), nullable=True),
        # Preços
        sa.Column("reference_price", sa.Numeric(15, 4), nullable=True),
        sa.Column("last_purchase_price", sa.Numeric(15, 4), nullable=True),
        sa.Column("average_price", sa.Numeric(15, 4), nullable=True),
        sa.Column("min_price", sa.Numeric(15, 4), nullable=True),
        sa.Column("max_price", sa.Numeric(15, 4), nullable=True),
        # Estoque
        sa.Column("track_stock", sa.Boolean, server_default="true"),
        sa.Column("current_stock", sa.Numeric(15, 4), server_default="0"),
        sa.Column("minimum_stock", sa.Numeric(15, 4), server_default="0"),
        sa.Column("maximum_stock", sa.Numeric(15, 4), nullable=True),
        sa.Column("reorder_point", sa.Numeric(15, 4), nullable=True),
        sa.Column("reorder_quantity", sa.Numeric(15, 4), nullable=True),
        # Lead time e fornecedor
        sa.Column("lead_time_days", sa.Integer, nullable=True),
        sa.Column("default_supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Fiscal
        sa.Column("origin", sa.String(1), server_default="0"),
        sa.Column("cfop_in", sa.String(10), nullable=True),
        sa.Column("cfop_out", sa.String(10), nullable=True),
        # Especificações
        sa.Column("specifications", postgresql.JSONB, nullable=True),
        # Fornecedores homologados
        sa.Column("approved_suppliers", postgresql.ARRAY(postgresql.UUID), nullable=True),
        # Histórico de preços
        sa.Column("price_history", postgresql.JSONB, server_default="[]"),
        # Bloqueio
        sa.Column("is_blocked", sa.Boolean, server_default="false"),
        sa.Column("block_reason", sa.Text, nullable=True),
        sa.Column("blocked_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("blocked_at", sa.DateTime(timezone=True), nullable=True),
        # Notas
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        # Imagem
        sa.Column("image_url", sa.String(500), nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_products_code_condo",
        "products",
        ["code", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_barcode", "products", ["barcode"])

    # =========================================================================
    # Tabela: purchase_requisitions
    # Requisições de compra
    # =========================================================================
    op.create_table(
        "purchase_requisitions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Número
        sa.Column("number", sa.String(20), nullable=False),
        # Descrição
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("justification", sa.Text, nullable=True),
        # Tipo e prioridade
        sa.Column(
            "requisition_type",
            sa.String(30),
            server_default="compra_normal",
        ),
        sa.Column(
            "priority",
            sa.String(20),
            server_default="normal",
        ),
        # Status
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="rascunho",
        ),
        # Datas
        sa.Column("requisition_date", sa.Date, nullable=False),
        sa.Column("required_date", sa.Date, nullable=True),
        # Departamento e centro de custo
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("cost_center", sa.String(50), nullable=True),
        sa.Column("project", sa.String(100), nullable=True),
        # Orçamento
        sa.Column("budget_available", sa.Numeric(15, 2), nullable=True),
        # Valores
        sa.Column("estimated_total", sa.Numeric(15, 2), server_default="0"),
        # Requisitante
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requester_name", sa.String(100), nullable=True),
        # Aprovação
        sa.Column("approval_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Rejeição
        sa.Column("rejection_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Cancelamento
        sa.Column("cancellation_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        # Cotação
        sa.Column("minimum_quotations", sa.Integer, server_default="3"),
        sa.Column("quotation_deadline", sa.Date, nullable=True),
        # Notas e anexos
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_purchase_requisitions_number_condo",
        "purchase_requisitions",
        ["number", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_purchase_requisitions_status", "purchase_requisitions", ["status"])
    op.create_index("ix_purchase_requisitions_requester", "purchase_requisitions", ["requester_id"])

    # =========================================================================
    # Tabela: purchase_requisition_items
    # Itens de requisição de compra
    # =========================================================================
    op.create_table(
        "purchase_requisition_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "requisition_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requisitions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=True,
        ),
        # Número do item
        sa.Column("item_number", sa.Integer, nullable=False),
        # Descrição
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("specifications", sa.Text, nullable=True),
        # Quantidade
        sa.Column("unit_of_measure", sa.String(10), server_default="un"),
        sa.Column("quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("quantity_approved", sa.Numeric(15, 4), nullable=True),
        sa.Column("quantity_quoted", sa.Numeric(15, 4), server_default="0"),
        sa.Column("quantity_ordered", sa.Numeric(15, 4), server_default="0"),
        # Preços
        sa.Column("estimated_price", sa.Numeric(15, 4), nullable=True),
        sa.Column("estimated_total", sa.Numeric(15, 2), nullable=True),
        # Urgência e datas
        sa.Column("is_urgent", sa.Boolean, server_default="false"),
        sa.Column("required_date", sa.Date, nullable=True),
        # Fornecedor sugerido
        sa.Column("suggested_supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("suggested_supplier_name", sa.String(200), nullable=True),
        # Notas
        sa.Column("notes", sa.Text, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.String(20),
            server_default="pendente",
        ),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # Tabela: purchase_quotations
    # Cotações de fornecedores
    # =========================================================================
    op.create_table(
        "purchase_quotations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "requisition_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requisitions.id"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id"),
            nullable=False,
            index=True,
        ),
        # Número
        sa.Column("number", sa.String(20), nullable=False),
        # Status
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="solicitada",
        ),
        # Datas
        sa.Column("quotation_date", sa.Date, nullable=False),
        sa.Column("valid_until", sa.Date, nullable=True),
        sa.Column("response_date", sa.DateTime(timezone=True), nullable=True),
        # Condições
        sa.Column("payment_condition", sa.String(20), nullable=True),
        sa.Column("payment_terms", sa.String(200), nullable=True),
        sa.Column("delivery_type", sa.String(20), nullable=True),
        sa.Column("delivery_days", sa.Integer, nullable=True),
        sa.Column("delivery_address", sa.Text, nullable=True),
        # Valores
        sa.Column("subtotal", sa.Numeric(15, 2), server_default="0"),
        sa.Column("discount_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("freight_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("insurance_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("other_costs", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total", sa.Numeric(15, 2), server_default="0"),
        # Impostos
        sa.Column("ipi_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("icms_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("pis_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("cofins_amount", sa.Numeric(15, 2), server_default="0"),
        # Scoring
        sa.Column("technical_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("commercial_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("delivery_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=True),
        # Seleção
        sa.Column("is_selected", sa.Boolean, server_default="false"),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("selected_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("selection_notes", sa.Text, nullable=True),
        # Rejeição
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Contato
        sa.Column("contact_name", sa.String(100), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        # Notas e anexos
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("supplier_notes", sa.Text, nullable=True),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_purchase_quotations_number_condo",
        "purchase_quotations",
        ["number", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_purchase_quotations_status", "purchase_quotations", ["status"])

    # =========================================================================
    # Tabela: purchase_quotation_items
    # Itens de cotação
    # =========================================================================
    op.create_table(
        "purchase_quotation_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "quotation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_quotations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "requisition_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requisition_items.id"),
            nullable=True,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=True,
        ),
        # Número do item
        sa.Column("item_number", sa.Integer, nullable=False),
        # Descrição
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("specifications", sa.Text, nullable=True),
        # Quantidade e preço
        sa.Column("unit_of_measure", sa.String(10), server_default="un"),
        sa.Column("quantity", sa.Numeric(15, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(15, 4), nullable=False),
        sa.Column("total", sa.Numeric(15, 2), nullable=False),
        # Impostos
        sa.Column("ipi_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("ipi_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("icms_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("icms_amount", sa.Numeric(15, 2), server_default="0"),
        # Código do fornecedor
        sa.Column("supplier_code", sa.String(50), nullable=True),
        # Entrega
        sa.Column("delivery_days", sa.Integer, nullable=True),
        sa.Column("available_quantity", sa.Numeric(15, 4), nullable=True),
        # Status
        sa.Column("is_available", sa.Boolean, server_default="true"),
        sa.Column("availability_notes", sa.String(200), nullable=True),
        # Notas
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # Tabela: purchase_orders
    # Ordens de compra
    # =========================================================================
    op.create_table(
        "purchase_orders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "quotation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_quotations.id"),
            nullable=True,
        ),
        sa.Column(
            "requisition_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requisitions.id"),
            nullable=True,
        ),
        # Número e revisão
        sa.Column("number", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer, server_default="1"),
        # Status e prioridade
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="rascunho",
        ),
        sa.Column("priority", sa.String(20), server_default="normal"),
        # Datas
        sa.Column("order_date", sa.Date, nullable=False),
        sa.Column("expected_delivery_date", sa.Date, nullable=True),
        sa.Column("actual_delivery_date", sa.Date, nullable=True),
        sa.Column("approval_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_date", sa.DateTime(timezone=True), nullable=True),
        # Condições de pagamento
        sa.Column("payment_condition", sa.String(20), nullable=True),
        sa.Column("payment_installments", sa.Integer, nullable=True),
        # Entrega
        sa.Column("delivery_type", sa.String(20), nullable=True),
        sa.Column("delivery_address", sa.Text, nullable=True),
        sa.Column("delivery_contact", sa.String(100), nullable=True),
        sa.Column("delivery_phone", sa.String(20), nullable=True),
        sa.Column("delivery_instructions", sa.Text, nullable=True),
        # Faturamento
        sa.Column("billing_address", sa.Text, nullable=True),
        sa.Column("billing_contact", sa.String(100), nullable=True),
        # Valores
        sa.Column("subtotal", sa.Numeric(15, 2), server_default="0"),
        sa.Column("discount_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("freight_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("insurance_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("other_costs", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total", sa.Numeric(15, 2), server_default="0"),
        # Impostos
        sa.Column("ipi_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("icms_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("icms_st_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("pis_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("cofins_amount", sa.Numeric(15, 2), server_default="0"),
        # Totais de recebimento/pagamento
        sa.Column("received_total", sa.Numeric(15, 2), server_default="0"),
        sa.Column("invoiced_total", sa.Numeric(15, 2), server_default="0"),
        sa.Column("paid_total", sa.Numeric(15, 2), server_default="0"),
        # Aprovação
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Observações do fornecedor
        sa.Column("supplier_notes", sa.Text, nullable=True),
        # Rejeição e cancelamento
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        # Conta a pagar vinculada
        sa.Column("payable_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Notas e anexos
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_purchase_orders_number_condo",
        "purchase_orders",
        ["number", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_purchase_orders_status", "purchase_orders", ["status"])
    op.create_index("ix_purchase_orders_delivery", "purchase_orders", ["expected_delivery_date"])

    # =========================================================================
    # Tabela: purchase_order_items
    # Itens de ordem de compra
    # =========================================================================
    op.create_table(
        "purchase_order_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_orders.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "quotation_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_quotation_items.id"),
            nullable=True,
        ),
        sa.Column(
            "requisition_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requisition_items.id"),
            nullable=True,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=True,
        ),
        # Número do item
        sa.Column("item_number", sa.Integer, nullable=False),
        # Descrição
        sa.Column("description", sa.String(500), nullable=False),
        # Quantidade e preço
        sa.Column("unit_of_measure", sa.String(10), server_default="un"),
        sa.Column("quantity_ordered", sa.Numeric(15, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(15, 4), nullable=False),
        sa.Column("discount_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("discount_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total", sa.Numeric(15, 2), nullable=False),
        # Impostos
        sa.Column("ipi_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("ipi_amount", sa.Numeric(15, 2), server_default="0"),
        sa.Column("icms_percentage", sa.Numeric(5, 2), server_default="0"),
        sa.Column("icms_amount", sa.Numeric(15, 2), server_default="0"),
        # Entrega
        sa.Column("expected_delivery_date", sa.Date, nullable=True),
        sa.Column("actual_delivery_date", sa.Date, nullable=True),
        # Rastreamento
        sa.Column("quantity_received", sa.Numeric(15, 4), server_default="0"),
        sa.Column("quantity_invoiced", sa.Numeric(15, 4), server_default="0"),
        sa.Column("quantity_returned", sa.Numeric(15, 4), server_default="0"),
        # Código do fornecedor
        sa.Column("supplier_code", sa.String(50), nullable=True),
        # Notas
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # Tabela: goods_receipts
    # Recebimentos de mercadorias
    # =========================================================================
    op.create_table(
        "goods_receipts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_orders.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id"),
            nullable=False,
        ),
        # Número
        sa.Column("number", sa.String(20), nullable=False),
        # Tipo e status
        sa.Column("receipt_type", sa.String(20), server_default="normal"),
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="pendente",
        ),
        # Datas
        sa.Column("receipt_date", sa.Date, nullable=False),
        sa.Column("expected_date", sa.Date, nullable=True),
        sa.Column("inspection_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_date", sa.DateTime(timezone=True), nullable=True),
        # Nota fiscal
        sa.Column("invoice_number", sa.String(50), nullable=True),
        sa.Column("invoice_series", sa.String(10), nullable=True),
        sa.Column("invoice_date", sa.Date, nullable=True),
        sa.Column("invoice_key", sa.String(50), nullable=True),
        sa.Column("invoice_total", sa.Numeric(15, 2), nullable=True),
        # Transportadora
        sa.Column("carrier", sa.String(200), nullable=True),
        sa.Column("carrier_cnpj", sa.String(18), nullable=True),
        sa.Column("vehicle_plate", sa.String(10), nullable=True),
        sa.Column("driver_name", sa.String(100), nullable=True),
        sa.Column("driver_document", sa.String(20), nullable=True),
        sa.Column("seal_number", sa.String(50), nullable=True),
        # Volumes e peso
        sa.Column("volumes", sa.Integer, nullable=True),
        sa.Column("gross_weight", sa.Numeric(15, 4), nullable=True),
        sa.Column("net_weight", sa.Numeric(15, 4), nullable=True),
        # Totais
        sa.Column("total_expected", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total_received", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total_accepted", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total_rejected", sa.Numeric(15, 2), server_default="0"),
        sa.Column("total_difference", sa.Numeric(15, 2), server_default="0"),
        # Inspeção
        sa.Column("inspection_result", sa.String(20), nullable=True),
        sa.Column("inspection_notes", sa.Text, nullable=True),
        sa.Column("inspected_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Divergência
        sa.Column("has_divergence", sa.Boolean, server_default="false"),
        sa.Column("divergence_type", sa.String(50), nullable=True),
        sa.Column("divergence_description", sa.Text, nullable=True),
        sa.Column("divergence_action", sa.String(50), nullable=True),
        # Aprovação
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Recebedor
        sa.Column("receiver_name", sa.String(100), nullable=True),
        sa.Column("receiver_document", sa.String(20), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        # Armazenamento
        sa.Column("storage_location", sa.String(100), nullable=True),
        sa.Column("storage_notes", sa.Text, nullable=True),
        # Notas e anexos
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_goods_receipts_number_condo",
        "goods_receipts",
        ["number", "condominio_id"],
        unique=True,
    )
    op.create_index("ix_goods_receipts_status", "goods_receipts", ["status"])

    # =========================================================================
    # Tabela: goods_receipt_items
    # Itens de recebimento
    # =========================================================================
    op.create_table(
        "goods_receipt_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "receipt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("goods_receipts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "order_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_order_items.id"),
            nullable=True,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=True,
        ),
        # Número do item
        sa.Column("item_number", sa.Integer, nullable=False),
        # Descrição
        sa.Column("description", sa.String(500), nullable=False),
        # Quantidade
        sa.Column("unit_of_measure", sa.String(10), server_default="un"),
        sa.Column("quantity_expected", sa.Numeric(15, 4), nullable=False),
        sa.Column("quantity_received", sa.Numeric(15, 4), server_default="0"),
        sa.Column("quantity_accepted", sa.Numeric(15, 4), server_default="0"),
        sa.Column("quantity_rejected", sa.Numeric(15, 4), server_default="0"),
        sa.Column("quantity_difference", sa.Numeric(15, 4), server_default="0"),
        # Preços e totais
        sa.Column("unit_price", sa.Numeric(15, 4), nullable=True),
        sa.Column("expected_total", sa.Numeric(15, 2), nullable=True),
        sa.Column("received_total", sa.Numeric(15, 2), nullable=True),
        sa.Column("accepted_total", sa.Numeric(15, 2), nullable=True),
        sa.Column("rejected_total", sa.Numeric(15, 2), nullable=True),
        # Lote e validade
        sa.Column("batch_number", sa.String(50), nullable=True),
        sa.Column("manufacturing_date", sa.Date, nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True),
        # Número de série
        sa.Column("serial_numbers", postgresql.ARRAY(sa.String), nullable=True),
        # Inspeção
        sa.Column("inspection_result", sa.String(20), nullable=True),
        sa.Column("inspection_notes", sa.Text, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Armazenamento
        sa.Column("storage_location", sa.String(100), nullable=True),
        sa.Column("storage_position", sa.String(50), nullable=True),
        # Notas
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    # =========================================================================
    # Tabela: purchase_approvals
    # Aprovações de compra (workflow multi-nível)
    # =========================================================================
    op.create_table(
        "purchase_approvals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Tipo e documento
        sa.Column("approval_type", sa.String(30), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_number", sa.String(50), nullable=True),
        # Nível e sequência
        sa.Column("approval_level", sa.String(30), nullable=False),
        sa.Column("sequence", sa.Integer, server_default="1"),
        # Status
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="pendente",
        ),
        # Valor do documento
        sa.Column("document_total", sa.Numeric(15, 2), nullable=True),
        # Aprovador
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("approver_role", sa.String(50), nullable=True),
        # Delegação
        sa.Column("original_approver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("delegated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("delegation_reason", sa.Text, nullable=True),
        sa.Column("delegated_at", sa.DateTime(timezone=True), nullable=True),
        # Datas
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_time_hours", sa.Numeric(10, 2), nullable=True),
        # Ação
        sa.Column("action", sa.String(30), nullable=True),
        sa.Column("comments", sa.Text, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Solicitação de informação
        sa.Column("info_requested", sa.Text, nullable=True),
        sa.Column("info_provided", sa.Text, nullable=True),
        # Notificação
        sa.Column("notification_sent", sa.Boolean, server_default="false"),
        sa.Column("reminder_count", sa.Integer, server_default="0"),
        # Histórico
        sa.Column("action_history", postgresql.JSONB, server_default="[]"),
        # Auditoria
        sa.Column("ativo", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_purchase_approvals_status", "purchase_approvals", ["status"])
    op.create_index(
        "ix_purchase_approvals_document",
        "purchase_approvals",
        ["approval_type", "document_id"],
    )
    op.create_index("ix_purchase_approvals_deadline", "purchase_approvals", ["deadline"])


def downgrade() -> None:
    """Remove tabelas de Compras."""
    op.drop_table("purchase_approvals")
    op.drop_table("goods_receipt_items")
    op.drop_table("goods_receipts")
    op.drop_table("purchase_order_items")
    op.drop_table("purchase_orders")
    op.drop_table("purchase_quotation_items")
    op.drop_table("purchase_quotations")
    op.drop_table("purchase_requisition_items")
    op.drop_table("purchase_requisitions")
    op.drop_table("products")
    op.drop_table("product_categories")
