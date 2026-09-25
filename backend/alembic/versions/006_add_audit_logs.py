"""Add system audit logs."""

from alembic import op
import sqlalchemy as sa


revision = "006_add_audit_logs"
down_revision = "005_user_organization_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("request_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("user_email", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("resource_type", sa.String(), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, column in (
        ("id", "id"),
        ("request_id", "request_id"),
        ("user_id", "user_id"),
        ("user_email", "user_email"),
        ("action", "action"),
        ("resource_type", "resource_type"),
        ("resource_id", "resource_id"),
        ("created_at", "created_at"),
    ):
        op.create_index(f"ix_audit_logs_{name}", "audit_logs", [column])


def downgrade():
    for name in ("id", "request_id", "user_id", "user_email", "action", "resource_type", "resource_id", "created_at"):
        op.drop_index(f"ix_audit_logs_{name}", table_name="audit_logs")
    op.drop_table("audit_logs")
