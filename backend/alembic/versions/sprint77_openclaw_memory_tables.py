"""openclaw agent memory — patterns + knowledge_base + intervention learning fields

Revision ID: sprint77_openclaw_memory
Revises: 6ce4dc2d4186
Create Date: 2026-03-20
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint77_openclaw_memory"
down_revision = "sprint77_openclaw_interventions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Campos de aprendizado na tabela existente
    op.add_column("openclaw_interventions", sa.Column("root_cause", sa.Text(), nullable=True))
    op.add_column("openclaw_interventions", sa.Column("learned_pattern", sa.Text(), nullable=True))
    op.add_column("openclaw_interventions", sa.Column("prevention_action", sa.Text(), nullable=True))
    op.add_column("openclaw_interventions", sa.Column("used_cached_solution", sa.Boolean(), server_default="false"))

    # Tabela de padroes aprendidos
    op.create_table(
        "openclaw_patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pattern_name", sa.String(200), nullable=False, unique=True),
        sa.Column("alert_name", sa.String(200), nullable=False, index=True),
        sa.Column("trigger_conditions", postgresql.JSONB(), nullable=True),
        sa.Column("frequency", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("auto_action", postgresql.JSONB(), nullable=True),
        sa.Column("diagnosis_template", sa.Text(), nullable=True),
        sa.Column("avg_resolve_time_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
    )

    # Tabela de knowledge base
    op.create_table(
        "openclaw_knowledge_base",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("component", sa.String(200), nullable=False, unique=True),
        sa.Column("known_issues", postgresql.JSONB(), nullable=True),
        sa.Column("dependencies", postgresql.JSONB(), nullable=True),
        sa.Column("peak_hours", postgresql.JSONB(), nullable=True),
        sa.Column("criticality_level", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("runbook", postgresql.JSONB(), nullable=True),
        sa.Column("last_incident_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
    )


def downgrade() -> None:
    op.drop_table("openclaw_knowledge_base")
    op.drop_table("openclaw_patterns")
    op.drop_column("openclaw_interventions", "used_cached_solution")
    op.drop_column("openclaw_interventions", "prevention_action")
    op.drop_column("openclaw_interventions", "learned_pattern")
    op.drop_column("openclaw_interventions", "root_cause")
