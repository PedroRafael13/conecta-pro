"""sprint85_bloco_a_modelo_canonico_gedeon_32_templates

Revision ID: 5ec309bea85c
Revises: cpro11_001_contractstatus_enum
Create Date: 2026-04-21 23:51:31.156674

GEDEON BLOCO A — Modelo Canônico (planilha GEDEON_Arquitetura_Modulos_032026.xlsx)

Alterações:
  1. kit_documental_templates: ADD COLUMNS (num, modulo, slug, status_origem)
     DROP old unique (tipo_servico, tipo_documento, escopo)
     ADD unique on slug
     tipo_servico → nullable (backward compat)
  2. CREATE TABLE kit_template_presenca (32 × 10 = 320 rows)
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "5ec309bea85c"  # pragma: allowlist secret
down_revision: str | None = "cpro11_001_contractstatus_enum"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Tornar tipo_servico nullable (backward compat)
    op.alter_column("kit_documental_templates", "tipo_servico", nullable=True)

    # 2. DROP old unique constraint (tipo_servico, tipo_documento, escopo)
    op.drop_constraint("uq_kit_template", "kit_documental_templates", type_="unique")

    # 3. ADD new columns
    op.add_column("kit_documental_templates", sa.Column("num", sa.Integer(), nullable=True))
    op.add_column("kit_documental_templates", sa.Column("modulo", sa.String(4), nullable=True))
    op.add_column("kit_documental_templates", sa.Column("slug", sa.String(64), nullable=True))
    op.add_column("kit_documental_templates", sa.Column("status_origem", sa.String(32), nullable=True))

    # 4. ADD unique on slug (after seed will be NOT NULL — set nullable=True for seed then tighten)
    op.create_unique_constraint("uq_kit_template_slug", "kit_documental_templates", ["slug"])

    # 5. CREATE TABLE kit_template_presenca
    op.create_table(
        "kit_template_presenca",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("presenca", sa.String(16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["template_id"], ["kit_documental_templates.id"], name="fk_presenca_template"),
        sa.ForeignKeyConstraint(["condominio_id"], ["condominios.id"], name="fk_presenca_condominio"),
        sa.UniqueConstraint("template_id", "condominio_id", name="uq_template_condominio"),
    )
    op.create_index("ix_presenca_template", "kit_template_presenca", ["template_id"])
    op.create_index("ix_presenca_condominio", "kit_template_presenca", ["condominio_id"])


def downgrade() -> None:
    op.drop_index("ix_presenca_condominio", table_name="kit_template_presenca")
    op.drop_index("ix_presenca_template", table_name="kit_template_presenca")
    op.drop_table("kit_template_presenca")

    op.drop_constraint("uq_kit_template_slug", "kit_documental_templates", type_="unique")
    op.drop_column("kit_documental_templates", "status_origem")
    op.drop_column("kit_documental_templates", "slug")
    op.drop_column("kit_documental_templates", "modulo")
    op.drop_column("kit_documental_templates", "num")

    op.create_unique_constraint(
        "uq_kit_template", "kit_documental_templates", ["tipo_servico", "tipo_documento", "escopo"]
    )
    op.alter_column("kit_documental_templates", "tipo_servico", nullable=False)
