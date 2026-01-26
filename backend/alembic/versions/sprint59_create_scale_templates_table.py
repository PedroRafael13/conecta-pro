"""Criar tabela scale_templates para templates de escalas.

Revision ID: sprint59_scale_templates
Revises: sprint58_ged
Create Date: 2026-01-26

Tabela criada:
- scale_templates (templates reutilizáveis de escalas)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# revision identifiers
revision = "sprint59_scale_templates"
down_revision = "sprint33_employees_operational"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabela scale_templates."""

    op.create_table(
        "scale_templates",
        # Identificação
        sa.Column(
            "id",
            UUID(as_uuid=False),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
        ),

        # Tenant (multi-tenancy)
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),

        # Informações do template
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),

        # Dados do template (estrutura da escala em JSON)
        sa.Column("template_data", JSONB(), nullable=False),

        # Controle de uso
        sa.Column("times_used", sa.Integer(), default=0, nullable=False),
        sa.Column("last_used", sa.DateTime(), nullable=True),

        # Auditoria
        sa.Column("created_by", UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),

        # Soft delete
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
    )

    # Índices para otimização de queries
    op.create_index(
        "idx_scale_templates_tenant_active",
        "scale_templates",
        ["tenant_id", "is_active"],
    )

    op.create_index(
        "idx_scale_templates_created_at",
        "scale_templates",
        ["created_at"],
    )

    op.create_index(
        "idx_scale_templates_times_used",
        "scale_templates",
        ["times_used"],
    )


def downgrade() -> None:
    """Remove tabela scale_templates."""

    # Remover índices
    op.drop_index("idx_scale_templates_times_used", table_name="scale_templates")
    op.drop_index("idx_scale_templates_created_at", table_name="scale_templates")
    op.drop_index("idx_scale_templates_tenant_active", table_name="scale_templates")

    # Remover tabela
    op.drop_table("scale_templates")
