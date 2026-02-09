"""Merge all 12 migration heads into single head for production

Revision ID: production_merge_20260209
Revises: bidding_001, perf001_gin_indexes_jsonb, sprint05_marketplace, sprint24_receivable_p2, sprint30_gestao_clients, sprint33_workflow, sprint36_fix_float_numeric, sprint55_workflow_optimizer, sprint56_gov_sync, sprint57_disciplinary, sprint58_ged, sprint59_scale_templates
Create Date: 2026-02-09 18:30:09.830556

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "production_merge_20260209"
down_revision: str | None = (
    "bidding_001",
    "perf001_gin_indexes_jsonb",
    "sprint05_marketplace",
    "sprint24_receivable_p2",
    "sprint30_gestao_clients",
    "sprint33_workflow",
    "sprint36_fix_float_numeric",
    "sprint55_workflow_optimizer",
    "sprint56_gov_sync",
    "sprint57_disciplinary",
    "sprint58_ged",
    "sprint59_scale_templates",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
