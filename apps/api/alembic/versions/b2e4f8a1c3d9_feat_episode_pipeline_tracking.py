"""feat: episode pipeline tracking columns

Revision ID: b2e4f8a1c3d9
Revises: 453f61afe613
Create Date: 2026-04-22 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b2e4f8a1c3d9"
down_revision: str | None = "453f61afe613"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "episodes",
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "episodes",
        sa.Column(
            "published_urls",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "episodes",
        sa.Column(
            "pipeline_progress",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )
    op.create_index("ix_episodes_celery_task_id", "episodes", ["celery_task_id"])


def downgrade() -> None:
    op.drop_index("ix_episodes_celery_task_id", table_name="episodes")
    op.drop_column("episodes", "pipeline_progress")
    op.drop_column("episodes", "published_urls")
    op.drop_column("episodes", "celery_task_id")
