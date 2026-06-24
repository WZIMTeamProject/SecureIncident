"""add_profile_fields_to_users

Revision ID: 9ca2bc071d3d
Revises: 8557b1f01d8a
Create Date: 2026-06-14 14:29:39.502963

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9ca2bc071d3d"
down_revision: str | None = "8557b1f01d8a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def downgrade() -> None:
    op.drop_column("users", "profile_picture_url")
    op.drop_column("users", "bio")


def upgrade() -> None:
    op.add_column("users", sa.Column("bio", sa.String(length=1000), nullable=True))
    op.add_column(
        "users", sa.Column("profile_picture_url", sa.String(length=500), nullable=True)
    )
