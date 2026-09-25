"""Add uppercase application status enum labels

Revision ID: 004_enum_labels
Revises: 003_workflow_ext
Create Date: 2026-09-12

"""
from alembic import op


revision = "004_enum_labels"
down_revision = "003_workflow_ext"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'INTERVIEWER_HOLD'")
        op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'DEPARTMENT_INTERVIEW_HOLD'")
        op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'OFFER_NOT_AGREED'")


def downgrade():
    pass
