"""slide extra fields and user list prefs

Revision ID: 0005_slide_extra_fields_and_user_list_prefs
Revises: 0004_case_slide_archive_fields
Create Date: 2026-02-04

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_slide_extra_fields_and_user_list_prefs"
down_revision = "0004_case_slide_archive_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("slides") as batch:
        batch.add_column(sa.Column("folder", sa.String(length=512), nullable=True))
        batch.add_column(sa.Column("ai_module", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("scan_magnification", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("ai_suggestion", sa.Text(), nullable=True))
        batch.add_column(sa.Column("processing_status", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("label_png_path", sa.String(length=1024), nullable=True))
        batch.add_column(sa.Column("slide_number", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("quality", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("clarity", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("review_result", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")))

    with op.batch_alter_table("slides") as batch:
        batch.alter_column("updated_at", server_default=None)

    op.create_table(
        "user_list_prefs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value_json", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_user_list_prefs_user_key", "user_list_prefs", ["user_id", "key"], unique=True)

    with op.batch_alter_table("user_list_prefs") as batch:
        batch.alter_column("updated_at", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_user_list_prefs_user_key", table_name="user_list_prefs")
    op.drop_table("user_list_prefs")

    with op.batch_alter_table("slides") as batch:
        batch.drop_column("updated_at")
        batch.drop_column("review_result")
        batch.drop_column("clarity")
        batch.drop_column("quality")
        batch.drop_column("slide_number")
        batch.drop_column("label_png_path")
        batch.drop_column("processing_status")
        batch.drop_column("ai_suggestion")
        batch.drop_column("scan_magnification")
        batch.drop_column("ai_module")
        batch.drop_column("folder")
