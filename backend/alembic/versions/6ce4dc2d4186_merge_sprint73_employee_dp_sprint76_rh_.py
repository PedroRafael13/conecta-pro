"""merge sprint73_employee_dp + sprint76_rh_structs into single head

Revision ID: 6ce4dc2d4186
Revises: sprint73_employee_dp, sprint76_rh_structs
Create Date: 2026-03-20 02:23:26.575813

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "6ce4dc2d4186"
down_revision: str | None = ("sprint73_employee_dp", "sprint76_rh_structs")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
