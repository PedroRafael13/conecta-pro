"""Sprint 14 - Proposals CPQ Premium

Adiciona campos e tabelas para:
- Integração com assinatura digital (DocuSign, ClickSign, etc)
- Simulações de preços
- Wizard de criação em etapas
- Aprovação multinível

Revision ID: sprint14_cpq
Revises: sprint07_workflow_engine
Create Date: 2026-01-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint14_cpq"
down_revision: str | None = "sprint07_workflow"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica migração."""

    # 1. Tabela de simulações de preço
    op.create_table(
        "pricing_simulations",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("proposal_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        # Input
        sa.Column("base_salary", sa.Numeric(15, 2), nullable=False),
        sa.Column("headcount", sa.Integer(), nullable=False),
        sa.Column("contract_months", sa.Integer(), nullable=False),
        sa.Column("service_type", sa.String(50), nullable=False),
        sa.Column("client_state", sa.String(2), nullable=False),
        sa.Column("margin_target", sa.Numeric(5, 2), nullable=False),
        sa.Column("benefits_value", sa.Numeric(15, 2), server_default="0"),
        sa.Column("equipment_value", sa.Numeric(15, 2), server_default="0"),
        # Calculated
        sa.Column("base_cost", sa.Numeric(15, 2), nullable=False),
        sa.Column("cct_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("cct_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("labor_cost", sa.Numeric(15, 2), nullable=False),
        sa.Column("benefits_cost", sa.Numeric(15, 2), nullable=False),
        sa.Column("equipment_cost", sa.Numeric(15, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(15, 2), nullable=False),
        sa.Column("tax_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("tax_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("margin_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("margin_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(15, 2), nullable=False),
        sa.Column("total_monthly", sa.Numeric(15, 2), nullable=False),
        sa.Column("total_contract", sa.Numeric(15, 2), nullable=False),
        # Metadata
        sa.Column("scenario_name", sa.String(100), nullable=True),
        sa.Column("is_selected", sa.Boolean(), server_default="false"),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["proposals.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_pricing_simulations_proposal_id",
        "pricing_simulations",
        ["proposal_id"],
    )
    op.create_index(
        "ix_pricing_simulations_tenant_id",
        "pricing_simulations",
        ["tenant_id"],
    )

    # 2. Tabela de assinaturas de proposta
    op.create_table(
        "proposal_signatures",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("proposal_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        # Provedor
        sa.Column("provider", sa.String(30), nullable=False),  # internal, docusign, clicksign
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("signing_url", sa.Text(), nullable=True),
        sa.Column("callback_url", sa.Text(), nullable=True),
        # Status
        sa.Column("status", sa.String(30), nullable=False),  # pending, sent, signed, etc
        sa.Column("requested_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("viewed_at", sa.DateTime(), nullable=True),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("refused_at", sa.DateTime(), nullable=True),
        sa.Column("expired_at", sa.DateTime(), nullable=True),
        # Signatario
        sa.Column("signer_name", sa.String(255), nullable=False),
        sa.Column("signer_email", sa.String(255), nullable=False),
        sa.Column("signer_cpf", sa.String(14), nullable=True),
        sa.Column("signer_phone", sa.String(20), nullable=True),
        sa.Column("signer_role", sa.String(50), server_default="cliente"),
        sa.Column("signer_order", sa.Integer(), server_default="1"),
        # Documento assinado
        sa.Column("signed_document_url", sa.Text(), nullable=True),
        sa.Column("signature_hash", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        # Controle
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("refusal_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["proposals.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_proposal_signatures_proposal_id",
        "proposal_signatures",
        ["proposal_id"],
    )
    op.create_index(
        "ix_proposal_signatures_external_id",
        "proposal_signatures",
        ["external_id"],
    )
    op.create_index(
        "ix_proposal_signatures_status",
        "proposal_signatures",
        ["status"],
    )

    # 3. Tabela de níveis de aprovação
    op.create_table(
        "proposal_approval_levels",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # Critérios
        sa.Column("min_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("max_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("min_discount_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_discount_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("proposal_types", postgresql.ARRAY(sa.String()), nullable=True),
        # Aprovadores
        sa.Column("required_role", sa.String(50), nullable=False),
        sa.Column("approver_ids", postgresql.ARRAY(postgresql.UUID()), nullable=True),
        sa.Column("require_all", sa.Boolean(), server_default="false"),
        # Ordem
        sa.Column("level_order", sa.Integer(), nullable=False),
        sa.Column("is_final", sa.Boolean(), server_default="false"),
        # Controle
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_proposal_approval_levels_tenant_id",
        "proposal_approval_levels",
        ["tenant_id"],
    )
    op.create_index(
        "ix_proposal_approval_levels_level_order",
        "proposal_approval_levels",
        ["level_order"],
    )

    # 4. Tabela de etapas do wizard
    op.create_table(
        "proposal_wizard_states",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("proposal_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", sa.String(100), nullable=True),
        # Estado
        sa.Column("current_step", sa.Integer(), server_default="1"),
        sa.Column("total_steps", sa.Integer(), server_default="5"),
        sa.Column("step_data", postgresql.JSONB(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), server_default="false"),
        # Etapas: 1-Cliente, 2-Serviços, 3-Precificação, 4-Condições, 5-Revisão
        sa.Column("step1_completed", sa.Boolean(), server_default="false"),
        sa.Column("step2_completed", sa.Boolean(), server_default="false"),
        sa.Column("step3_completed", sa.Boolean(), server_default="false"),
        sa.Column("step4_completed", sa.Boolean(), server_default="false"),
        sa.Column("step5_completed", sa.Boolean(), server_default="false"),
        # Timestamps
        sa.Column("started_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["proposals.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_proposal_wizard_states_user_id",
        "proposal_wizard_states",
        ["user_id"],
    )

    # 5. Adicionar colunas na tabela proposals
    op.add_column(
        "proposals",
        sa.Column("signature_provider", sa.String(30), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("signature_external_id", sa.String(255), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("signature_status", sa.String(30), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("signed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("signed_document_url", sa.Text(), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("approval_level_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("current_approval_level", sa.Integer(), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("pricing_simulation_id", postgresql.UUID(as_uuid=False), nullable=True),
    )

    # 6. Adicionar colunas de CCT detalhado
    op.add_column(
        "proposals",
        sa.Column("cct_breakdown", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("tax_breakdown", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "proposals",
        sa.Column("margin_percent", sa.Numeric(5, 2), nullable=True),
    )

    # 7. Criar índices adicionais
    op.create_index(
        "ix_proposals_signature_status",
        "proposals",
        ["signature_status"],
    )
    op.create_index(
        "ix_proposals_approval_level_id",
        "proposals",
        ["approval_level_id"],
    )


def downgrade() -> None:
    """Reverte migração."""

    # Remover índices
    op.drop_index("ix_proposals_approval_level_id", table_name="proposals")
    op.drop_index("ix_proposals_signature_status", table_name="proposals")

    # Remover colunas de proposals
    op.drop_column("proposals", "margin_percent")
    op.drop_column("proposals", "tax_breakdown")
    op.drop_column("proposals", "cct_breakdown")
    op.drop_column("proposals", "pricing_simulation_id")
    op.drop_column("proposals", "current_approval_level")
    op.drop_column("proposals", "approval_level_id")
    op.drop_column("proposals", "signed_document_url")
    op.drop_column("proposals", "signed_at")
    op.drop_column("proposals", "signature_status")
    op.drop_column("proposals", "signature_external_id")
    op.drop_column("proposals", "signature_provider")

    # Remover tabelas
    op.drop_table("proposal_wizard_states")
    op.drop_table("proposal_approval_levels")
    op.drop_table("proposal_signatures")
    op.drop_table("pricing_simulations")
