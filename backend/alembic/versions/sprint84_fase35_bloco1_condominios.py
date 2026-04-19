"""fase_3_5_bloco1: condominios ALTER + employee_alocacoes + kit_documental_templates + kits_gerados

Revision ID: sprint84_fase35_bloco1_condominios
Revises: 9d91ef5c61f6
Create Date: 2026-04-18

GEDEON Fase 3.5 BLOCO 1 — Fundação estrutural.

condominios já existe (referenciada por empresas, payable_installments, bank_reconciliations).
Estratégia: ALTER TABLE (preserva FKs existentes).
- Deleta 1 mock row (a1b2c3d4-...)
- ADD nome_normalizado, tipo_servico, tem_folha_clt, client_id
- CREATE employee_alocacoes, kit_documental_templates, kits_gerados
- ADD 3 colunas em onvio_documents: doc_scope, condominio_id, referente_a_employee_id
"""

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision = "sprint84_bloco1_condominios"
down_revision = "9d91ef5c61f6"
branch_labels = None
depends_on = None


MOCK_COND_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def upgrade() -> None:
    # 1. ALTER condominios — add missing columns first (nullable so existing row is safe)
    op.add_column(
        "condominios",
        sa.Column("nome_normalizado", sa.String(100), nullable=True),
    )
    op.add_column(
        "condominios",
        sa.Column("tipo_servico", sa.String(50), nullable=True),
    )
    op.add_column(
        "condominios",
        sa.Column(
            "tem_folha_clt",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "condominios",
        sa.Column("client_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_condominios_client_id",
        "condominios",
        "clients",
        ["client_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # 1b. Update mock row → becomes ESCRITÓRIO (preserves FK refs from empresas/payable)
    # empresas.condominio_id is NOT NULL so can't delete; repurpose the mock UUID instead
    op.execute(
        text(
            "UPDATE condominios SET "
            "nome='ESCRITÓRIO', nome_normalizado='escritorio', "
            "tipo_servico='administrativo', tem_folha_clt=true, "
            "cnpj='35.710.481/0001-03', ativo=true "
            "WHERE id = :id"
        ).bindparams(id=MOCK_COND_ID)
    )
    op.create_index("ix_condominios_nome_normalizado", "condominios", ["nome_normalizado"])
    op.create_index("ix_condominios_tipo_servico", "condominios", ["tipo_servico"])
    op.create_index("ix_condominios_client_id", "condominios", ["client_id"])
    op.create_unique_constraint("uq_condominios_nome_normalizado", "condominios", ["nome_normalizado"])

    # 2. employee_alocacoes
    op.create_table(
        "employee_alocacoes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "employee_id",
            UUID(as_uuid=True),
            sa.ForeignKey("employees.id"),
            nullable=False,
        ),
        sa.Column(
            "condominio_id",
            UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=False,
        ),
        sa.Column("funcao", sa.String(100), nullable=False),
        sa.Column("data_inicio", sa.Date(), nullable=False),
        sa.Column("data_fim", sa.Date(), nullable=True),
        sa.Column(
            "ativo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_employee_alocacoes_employee", "employee_alocacoes", ["employee_id"])
    op.create_index("ix_employee_alocacoes_condominio", "employee_alocacoes", ["condominio_id"])
    op.create_index("ix_employee_alocacoes_ativo", "employee_alocacoes", ["ativo"])

    # 3. kit_documental_templates
    op.create_table(
        "kit_documental_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo_servico", sa.String(50), nullable=False),
        sa.Column("tipo_documento", sa.String(100), nullable=False),
        sa.Column("escopo", sa.String(50), nullable=False),
        sa.Column(
            "obrigatorio",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("periodicidade", sa.String(20), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_unique_constraint(
        "uq_kit_template",
        "kit_documental_templates",
        ["tipo_servico", "tipo_documento", "escopo"],
    )

    # 4. kits_gerados
    op.create_table(
        "kits_gerados",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "condominio_id",
            UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=False,
        ),
        sa.Column("mes_ref", sa.String(7), nullable=False),
        sa.Column(
            "gerado_em",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("gerado_por_user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("arquivo_zip_path", sa.Text(), nullable=True),
        sa.Column("docs_incluidos", JSONB(), nullable=True),
        sa.Column("total_docs_esperados", sa.Integer(), nullable=True),
        sa.Column("total_docs_incluidos", sa.Integer(), nullable=True),
    )
    op.create_index("ix_kits_condominio_mes", "kits_gerados", ["condominio_id", "mes_ref"])

    # 5. onvio_documents — add 3 columns
    op.add_column("onvio_documents", sa.Column("doc_scope", sa.String(50), nullable=True))
    op.add_column(
        "onvio_documents",
        sa.Column(
            "condominio_id",
            UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=True,
        ),
    )
    op.add_column(
        "onvio_documents",
        sa.Column(
            "referente_a_employee_id",
            UUID(as_uuid=True),
            sa.ForeignKey("employees.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_onvio_doc_scope", "onvio_documents", ["doc_scope"])
    op.create_index("ix_onvio_condominio", "onvio_documents", ["condominio_id"])


def downgrade() -> None:
    # 5. onvio_documents
    op.drop_index("ix_onvio_condominio", table_name="onvio_documents")
    op.drop_index("ix_onvio_doc_scope", table_name="onvio_documents")
    op.drop_column("onvio_documents", "referente_a_employee_id")
    op.drop_column("onvio_documents", "condominio_id")
    op.drop_column("onvio_documents", "doc_scope")

    # 4. kits_gerados
    op.drop_index("ix_kits_condominio_mes", table_name="kits_gerados")
    op.drop_table("kits_gerados")

    # 3. kit_documental_templates
    op.drop_constraint("uq_kit_template", "kit_documental_templates", type_="unique")
    op.drop_table("kit_documental_templates")

    # 2. employee_alocacoes
    op.drop_index("ix_employee_alocacoes_ativo", table_name="employee_alocacoes")
    op.drop_index("ix_employee_alocacoes_condominio", table_name="employee_alocacoes")
    op.drop_index("ix_employee_alocacoes_employee", table_name="employee_alocacoes")
    op.drop_table("employee_alocacoes")

    # 1. condominios — remove added columns
    op.drop_constraint("uq_condominios_nome_normalizado", "condominios", type_="unique")
    op.drop_index("ix_condominios_client_id", table_name="condominios")
    op.drop_index("ix_condominios_tipo_servico", table_name="condominios")
    op.drop_index("ix_condominios_nome_normalizado", table_name="condominios")
    op.drop_constraint("fk_condominios_client_id", "condominios", type_="foreignkey")
    op.drop_column("condominios", "client_id")
    op.drop_column("condominios", "tem_folha_clt")
    op.drop_column("condominios", "tipo_servico")
    op.drop_column("condominios", "nome_normalizado")
