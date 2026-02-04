"""slide ingest metadata

Revision ID: 0002_slide_ingest_meta
Revises: 0001_init
Create Date: 2026-02-04

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_slide_ingest_meta"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("slides", sa.Column("filename", sa.String(length=512), nullable=True))
    op.add_column("slides", sa.Column("storage_path", sa.String(length=1024), nullable=True))
    op.add_column("slides", sa.Column("ingested_ok", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("slides", sa.Column("level_count", sa.Integer(), nullable=True))
    op.add_column("slides", sa.Column("width", sa.Integer(), nullable=True))
    op.add_column("slides", sa.Column("height", sa.Integer(), nullable=True))
    op.add_column("slides", sa.Column("mpp_x", sa.Float(), nullable=True))
    op.add_column("slides", sa.Column("mpp_y", sa.Float(), nullable=True))
    op.add_column("slides", sa.Column("thumb_path", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("slides", "thumb_path")
    op.drop_column("slides", "mpp_y")
    op.drop_column("slides", "mpp_x")
    op.drop_column("slides", "height")
    op.drop_column("slides", "width")
    op.drop_column("slides", "level_count")
    op.drop_column("slides", "ingested_ok")
    op.drop_column("slides", "storage_path")
    op.drop_column("slides", "filename")
