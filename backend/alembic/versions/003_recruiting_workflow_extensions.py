"""Recruiting workflow extensions

Revision ID: 003_workflow_ext
Revises: 002_add_v2_models
Create Date: 2026-08-31

"""
from alembic import op
import sqlalchemy as sa


revision = "003_workflow_ext"
down_revision = "002_add_v2_models"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'INTERVIEWER_HOLD'")
        op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'DEPARTMENT_INTERVIEW_HOLD'")
        op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'OFFER_NOT_AGREED'")
        op.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS is_third_party_headhunter_enabled BOOLEAN DEFAULT FALSE")
        op.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS interview_flow_config TEXT")
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_jobs_is_third_party_headhunter_enabled "
            "ON jobs (is_third_party_headhunter_enabled)"
        )

        op.execute("ALTER TABLE applications ADD COLUMN IF NOT EXISTS rejection_reason TEXT")
        op.execute("ALTER TABLE applications ADD COLUMN IF NOT EXISTS interviewer_evaluation TEXT")
        op.execute("ALTER TABLE applications ADD COLUMN IF NOT EXISTS offer_details TEXT")
        op.execute("ALTER TABLE applications ADD COLUMN IF NOT EXISTS onboarding_attachments TEXT")

        op.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_templates (
                id VARCHAR NOT NULL PRIMARY KEY,
                name VARCHAR NOT NULL,
                audience VARCHAR NOT NULL,
                interview_type VARCHAR NOT NULL,
                subject VARCHAR NOT NULL,
                body TEXT NOT NULL,
                is_active BOOLEAN,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
            """
        )
        op.execute("CREATE INDEX IF NOT EXISTS ix_notification_templates_id ON notification_templates (id)")
        op.execute("CREATE INDEX IF NOT EXISTS ix_notification_templates_audience ON notification_templates (audience)")
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_notification_templates_interview_type "
            "ON notification_templates (interview_type)"
        )
        op.execute("CREATE INDEX IF NOT EXISTS ix_notification_templates_is_active ON notification_templates (is_active)")

        op.execute(
            """
            CREATE TABLE IF NOT EXISTS mailbox_configs (
                id VARCHAR NOT NULL PRIMARY KEY,
                provider VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                auth_code VARCHAR NOT NULL,
                is_active BOOLEAN,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
            """
        )
        op.execute("CREATE INDEX IF NOT EXISTS ix_mailbox_configs_id ON mailbox_configs (id)")
        op.execute("CREATE INDEX IF NOT EXISTS ix_mailbox_configs_is_active ON mailbox_configs (is_active)")

        op.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_logs (
                id VARCHAR NOT NULL PRIMARY KEY,
                candidate_email VARCHAR,
                interviewer_email VARCHAR,
                candidate_template_id VARCHAR,
                interviewer_template_id VARCHAR,
                interview_type VARCHAR,
                status VARCHAR NOT NULL,
                error_message TEXT,
                sent_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
            """
        )
        op.execute("CREATE INDEX IF NOT EXISTS ix_notification_logs_id ON notification_logs (id)")

        op.execute(
            """
            CREATE TABLE IF NOT EXISTS headhunter_recommendations (
                id VARCHAR NOT NULL PRIMARY KEY,
                job_id VARCHAR NOT NULL REFERENCES jobs(id),
                candidate_name VARCHAR NOT NULL,
                phone VARCHAR,
                email VARCHAR,
                resume_url VARCHAR,
                headhunter_name VARCHAR,
                notes TEXT,
                status VARCHAR NOT NULL,
                hr_feedback TEXT,
                reviewed_by VARCHAR REFERENCES users(id),
                reviewed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
            """
        )
        op.execute("CREATE INDEX IF NOT EXISTS ix_headhunter_recommendations_id ON headhunter_recommendations (id)")
        op.execute("CREATE INDEX IF NOT EXISTS ix_headhunter_recommendations_job_id ON headhunter_recommendations (job_id)")
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_headhunter_recommendations_candidate_name "
            "ON headhunter_recommendations (candidate_name)"
        )
        op.execute("CREATE INDEX IF NOT EXISTS ix_headhunter_recommendations_status ON headhunter_recommendations (status)")
        return

    op.add_column("jobs", sa.Column("is_third_party_headhunter_enabled", sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column("jobs", sa.Column("interview_flow_config", sa.Text(), nullable=True))
    op.create_index(op.f("ix_jobs_is_third_party_headhunter_enabled"), "jobs", ["is_third_party_headhunter_enabled"], unique=False)

    op.add_column("applications", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.add_column("applications", sa.Column("interviewer_evaluation", sa.Text(), nullable=True))
    op.add_column("applications", sa.Column("offer_details", sa.Text(), nullable=True))
    op.add_column("applications", sa.Column("onboarding_attachments", sa.Text(), nullable=True))

    op.create_table(
        "notification_templates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("audience", sa.String(), nullable=False),
        sa.Column("interview_type", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_templates_id"), "notification_templates", ["id"], unique=False)
    op.create_index(op.f("ix_notification_templates_audience"), "notification_templates", ["audience"], unique=False)
    op.create_index(op.f("ix_notification_templates_interview_type"), "notification_templates", ["interview_type"], unique=False)
    op.create_index(op.f("ix_notification_templates_is_active"), "notification_templates", ["is_active"], unique=False)

    op.create_table(
        "mailbox_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("auth_code", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mailbox_configs_id"), "mailbox_configs", ["id"], unique=False)
    op.create_index(op.f("ix_mailbox_configs_is_active"), "mailbox_configs", ["is_active"], unique=False)

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("candidate_email", sa.String(), nullable=True),
        sa.Column("interviewer_email", sa.String(), nullable=True),
        sa.Column("candidate_template_id", sa.String(), nullable=True),
        sa.Column("interviewer_template_id", sa.String(), nullable=True),
        sa.Column("interview_type", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_logs_id"), "notification_logs", ["id"], unique=False)

    op.create_table(
        "headhunter_recommendations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("candidate_name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("resume_url", sa.String(), nullable=True),
        sa.Column("headhunter_name", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("hr_feedback", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_headhunter_recommendations_id"), "headhunter_recommendations", ["id"], unique=False)
    op.create_index(op.f("ix_headhunter_recommendations_job_id"), "headhunter_recommendations", ["job_id"], unique=False)
    op.create_index(op.f("ix_headhunter_recommendations_candidate_name"), "headhunter_recommendations", ["candidate_name"], unique=False)
    op.create_index(op.f("ix_headhunter_recommendations_status"), "headhunter_recommendations", ["status"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_headhunter_recommendations_status"), table_name="headhunter_recommendations")
    op.drop_index(op.f("ix_headhunter_recommendations_candidate_name"), table_name="headhunter_recommendations")
    op.drop_index(op.f("ix_headhunter_recommendations_job_id"), table_name="headhunter_recommendations")
    op.drop_index(op.f("ix_headhunter_recommendations_id"), table_name="headhunter_recommendations")
    op.drop_table("headhunter_recommendations")

    op.drop_index(op.f("ix_notification_logs_id"), table_name="notification_logs")
    op.drop_table("notification_logs")

    op.drop_index(op.f("ix_mailbox_configs_is_active"), table_name="mailbox_configs")
    op.drop_index(op.f("ix_mailbox_configs_id"), table_name="mailbox_configs")
    op.drop_table("mailbox_configs")

    op.drop_index(op.f("ix_notification_templates_is_active"), table_name="notification_templates")
    op.drop_index(op.f("ix_notification_templates_interview_type"), table_name="notification_templates")
    op.drop_index(op.f("ix_notification_templates_audience"), table_name="notification_templates")
    op.drop_index(op.f("ix_notification_templates_id"), table_name="notification_templates")
    op.drop_table("notification_templates")

    op.drop_column("applications", "onboarding_attachments")
    op.drop_column("applications", "offer_details")
    op.drop_column("applications", "interviewer_evaluation")
    op.drop_column("applications", "rejection_reason")

    op.drop_index(op.f("ix_jobs_is_third_party_headhunter_enabled"), table_name="jobs")
    op.drop_column("jobs", "interview_flow_config")
    op.drop_column("jobs", "is_third_party_headhunter_enabled")
