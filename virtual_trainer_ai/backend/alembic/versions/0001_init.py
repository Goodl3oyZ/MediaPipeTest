"""initial tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "exercise_results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("score", sa.String(50)),
        sa.Column("feedback", sa.Text),
        sa.Column("input_video_key", sa.String(255)),
        sa.Column("output_video_key", sa.String(255)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "job_audit",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), server_default="queued"),
        sa.Column("input_key", sa.String(255), nullable=False),
        sa.Column("output_key", sa.String(255)),
        sa.Column("error", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("job_audit")
    op.drop_table("exercise_results")
    op.drop_table("users")
