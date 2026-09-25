"""Add organization fields and employee-department association to users.

Revision ID: 005_user_organization_fields
Revises: 004_enum_labels
"""

from alembic import op
import sqlalchemy as sa


revision = "005_user_organization_fields"
down_revision = "004_enum_labels"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    # The Department ORM model predates Alembic coverage, so make the table
    # available for databases initialized only through migrations as well.
    if "departments" not in tables:
        op.create_table(
            "departments",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("code", sa.String(), nullable=True),
            sa.Column("parent_id", sa.String(), nullable=True),
            sa.Column("level", sa.Integer(), nullable=True, server_default="1"),
            sa.Column("path", sa.String(), nullable=True),
            sa.Column("manager_id", sa.String(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
            sa.Column("employee_count", sa.Integer(), nullable=True, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["parent_id"], ["departments.id"]),
            sa.ForeignKeyConstraint(["manager_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_departments_id", "departments", ["id"])
        op.create_index("ix_departments_name", "departments", ["name"])
        op.create_index("ix_departments_code", "departments", ["code"], unique=True)
        op.create_index("ix_departments_parent_id", "departments", ["parent_id"])
        op.create_index("ix_departments_manager_id", "departments", ["manager_id"])
        op.create_index("ix_departments_is_active", "departments", ["is_active"])

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "department_id" not in user_columns:
        op.add_column("users", sa.Column("department_id", sa.String(), nullable=True))
        op.create_foreign_key("fk_users_department_id", "users", "departments", ["department_id"], ["id"])
        op.create_index("ix_users_department_id", "users", ["department_id"])
    if "title" not in user_columns:
        op.add_column("users", sa.Column("title", sa.String(), nullable=True))
    if "manager_id" not in user_columns:
        op.add_column("users", sa.Column("manager_id", sa.String(), nullable=True))
        op.create_foreign_key("fk_users_manager_id", "users", "users", ["manager_id"], ["id"])
        op.create_index("ix_users_manager_id", "users", ["manager_id"])
    if "employee_no" not in user_columns:
        op.add_column("users", sa.Column("employee_no", sa.String(), nullable=True))
        op.create_index("ix_users_employee_no", "users", ["employee_no"], unique=True)
    if "status" not in user_columns:
        op.add_column("users", sa.Column("status", sa.String(), nullable=True, server_default="active"))
        op.create_index("ix_users_status", "users", ["status"])


def downgrade():
    op.drop_index("ix_users_status", table_name="users")
    op.drop_column("users", "status")
    op.drop_index("ix_users_employee_no", table_name="users")
    op.drop_column("users", "employee_no")
    op.drop_index("ix_users_manager_id", table_name="users")
    op.drop_constraint("fk_users_manager_id", "users", type_="foreignkey")
    op.drop_column("users", "manager_id")
    op.drop_column("users", "title")
    op.drop_index("ix_users_department_id", table_name="users")
    op.drop_constraint("fk_users_department_id", "users", type_="foreignkey")
    op.drop_column("users", "department_id")
