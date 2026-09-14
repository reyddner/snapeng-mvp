"""Add temporary public memorial drafts.

Revision ID: 002_memorial_drafts
Revises: 001_initial
"""

from alembic import op
import sqlalchemy as sa


revision = "002_memorial_drafts"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "memorial_drafts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("draft_id", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_memorial_drafts_id"), "memorial_drafts", ["id"], unique=False)
    op.create_index(op.f("ix_memorial_drafts_draft_id"), "memorial_drafts", ["draft_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_memorial_drafts_draft_id"), table_name="memorial_drafts")
    op.drop_index(op.f("ix_memorial_drafts_id"), table_name="memorial_drafts")
    op.drop_table("memorial_drafts")