"""Add platform administrator role."""

from alembic import op


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL stores UserRole as a native enum. SQLite (used by some local
    # demos) has no native enum and needs no schema change for this value.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'platform_admin'")


def downgrade():
    # PostgreSQL does not support removing a value from an enum safely.
    pass
