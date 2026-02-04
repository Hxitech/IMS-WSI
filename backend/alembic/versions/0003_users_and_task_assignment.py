"""users and task assignment

Revision ID: 0003_users_and_task_assignment
Revises: 0002_slide_ingest_meta
Create Date: 2026-02-04

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_users_and_task_assignment"
down_revision = "0002_slide_ingest_meta"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.Enum("admin", "doctor", "tech", name="userrole"), nullable=False, server_default="tech"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.add_column("tasks", sa.Column("assignee_id", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("assigned_at", sa.DateTime(), nullable=True))
    op.add_column(
        "tasks",
        sa.Column(
            "assign_strategy",
            sa.Enum("manual", "by_count", "by_time", name="taskassignstrategy"),
            nullable=False,
            server_default="manual",
        ),
    )
    op.create_foreign_key(
        "fk_tasks_assignee_id_users",
        "tasks",
        "users",
        ["assignee_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tasks_assignee_id_users", "tasks", type_="foreignkey")
    op.drop_column("tasks", "assign_strategy")
    op.drop_column("tasks", "assigned_at")
    op.drop_column("tasks", "assignee_id")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS taskassignstrategy")
    op.execute("DROP TYPE IF EXISTS userrole")
