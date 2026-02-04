"""case/slide archive fields

Revision ID: 0004_case_slide_archive_fields
Revises: 0003_users_and_task_assignment
Create Date: 2026-02-04

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_case_slide_archive_fields"
down_revision = "0003_users_and_task_assignment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cases", sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("slides", sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    # drop defaults (keep NOT NULL)
    with op.batch_alter_table("cases") as batch:
        batch.alter_column("is_archived", server_default=None)
    with op.batch_alter_table("slides") as batch:
        batch.alter_column("is_archived", server_default=None)


def downgrade() -> None:
    op.drop_column("slides", "is_archived")
    op.drop_column("cases", "is_archived")
