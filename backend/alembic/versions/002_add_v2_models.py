"""Add V2 models - Application, InterviewerScreening, Assessment

Revision ID: 002_add_v2_models
Revises: 001_initial_migration
Create Date: 2026-05-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_v2_models'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # 创建ApplicationStatus枚举类型
    application_status = postgresql.ENUM(
        'new', 'hr_screening', 'hr_rejected',
        'hr_interview_scheduled', 'hr_interviewing', 'hr_interview_completed', 'hr_interview_rejected',
        'sent_to_interviewer', 'interviewer_rejected',
        'interview_intention_communication', 'candidate_declined_interview',
        'interview_time_confirming',
        'department_interview_scheduled', 'department_interviewing', 'department_interview_completed', 'department_interview_rejected',
        'assessment_invited', 'assessment_in_progress', 'assessment_completed', 'assessment_failed',
        'hr_reinterview_scheduled', 'hr_reinterviewing', 'hr_reinterview_completed', 'hr_reinterview_rejected',
        'final_interview_scheduled', 'final_interviewing', 'final_interview_completed', 'final_interview_rejected',
        'salary_negotiation', 'salary_rejected', 'verbal_offer_accepted',
        'offer_approval', 'offer_approval_rejected', 'offer_pending', 'offer_sent', 'offer_rejected', 'offer_accepted',
        'pending_onboard', 'onboard_cancelled', 'onboarded',
        'candidate_withdrawn',
        name='applicationstatus'
    )
    application_status.create(op.get_bind(), checkfirst=True)

    # 创建InterviewType枚举类型
    interview_type = postgresql.ENUM(
        'hr_initial', 'department', 'hr_reinterview', 'final',
        name='interviewtype'
    )
    interview_type.create(op.get_bind(), checkfirst=True)

    # 创建InterviewStatus枚举类型
    interview_status = postgresql.ENUM(
        'scheduled', 'confirmed', 'declined', 'cancelled', 'rescheduled', 'in_progress', 'completed', 'no_show',
        name='interviewstatus'
    )
    interview_status.create(op.get_bind(), checkfirst=True)

    # 创建InterviewResult枚举类型
    interview_result = postgresql.ENUM(
        'pending', 'pass', 'fail', 'hold',
        name='interviewresult'
    )
    interview_result.create(op.get_bind(), checkfirst=True)

    # 创建AssessmentStatus枚举类型
    assessment_status = postgresql.ENUM(
        'invited', 'in_progress', 'completed', 'failed', 'expired',
        name='assessmentstatus'
    )
    assessment_status.create(op.get_bind(), checkfirst=True)

    # 创建applications表
    op.create_table(
        'applications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('new', 'hr_screening', 'hr_rejected', 'hr_interview_scheduled', 'hr_interviewing', 'hr_interview_completed', 'hr_interview_rejected', 'sent_to_interviewer', 'interviewer_rejected', 'interview_intention_communication', 'candidate_declined_interview', 'interview_time_confirming', 'department_interview_scheduled', 'department_interviewing', 'department_interview_completed', 'department_interview_rejected', 'assessment_invited', 'assessment_in_progress', 'assessment_completed', 'assessment_failed', 'hr_reinterview_scheduled', 'hr_reinterviewing', 'hr_reinterview_completed', 'hr_reinterview_rejected', 'final_interview_scheduled', 'final_interviewing', 'final_interview_completed', 'final_interview_rejected', 'salary_negotiation', 'salary_rejected', 'verbal_offer_accepted', 'offer_approval', 'offer_approval_rejected', 'offer_pending', 'offer_sent', 'offer_rejected', 'offer_accepted', 'pending_onboard', 'onboard_cancelled', 'onboarded', 'candidate_withdrawn', name='applicationstatus'), nullable=False),
        sa.Column('resume_url', sa.String(), nullable=True),
        sa.Column('resume_parsed_data', sa.Text(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('hr_id', sa.String(), nullable=True),
        sa.Column('recruiter_id', sa.String(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=True, default=False),
        sa.Column('locked_by', sa.String(), nullable=True),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_count', sa.Integer(), nullable=True, default=1),
        sa.Column('intention_contact_method', sa.String(), nullable=True),
        sa.Column('intention_contact_result', sa.String(), nullable=True),
        sa.Column('intention_contact_notes', sa.Text(), nullable=True),
        sa.Column('intention_contacted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('intention_contacted_by', sa.String(), nullable=True),
        sa.Column('interview_notification_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interview_confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interview_confirmation_token', sa.String(), nullable=True),
        sa.Column('interview_flow_config', sa.Text(), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('hr_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_status_change_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['hr_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['recruiter_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['locked_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['intention_contacted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    op.create_index(op.f('ix_applications_candidate_id'), 'applications', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_applications_job_id'), 'applications', ['job_id'], unique=False)
    op.create_index(op.f('ix_applications_status'), 'applications', ['status'], unique=False)
    op.create_index(op.f('ix_applications_hr_id'), 'applications', ['hr_id'], unique=False)
    op.create_index(op.f('ix_applications_is_locked'), 'applications', ['is_locked'], unique=False)

    # 创建application_status_history表
    op.create_table(
        'application_status_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('application_id', sa.String(), nullable=False),
        sa.Column('from_status', sa.Enum('new', 'hr_screening', 'hr_rejected', 'hr_interview_scheduled', 'hr_interviewing', 'hr_interview_completed', 'hr_interview_rejected', 'sent_to_interviewer', 'interviewer_rejected', 'interview_intention_communication', 'candidate_declined_interview', 'interview_time_confirming', 'department_interview_scheduled', 'department_interviewing', 'department_interview_completed', 'department_interview_rejected', 'assessment_invited', 'assessment_in_progress', 'assessment_completed', 'assessment_failed', 'hr_reinterview_scheduled', 'hr_reinterviewing', 'hr_reinterview_completed', 'hr_reinterview_rejected', 'final_interview_scheduled', 'final_interviewing', 'final_interview_completed', 'final_interview_rejected', 'salary_negotiation', 'salary_rejected', 'verbal_offer_accepted', 'offer_approval', 'offer_approval_rejected', 'offer_pending', 'offer_sent', 'offer_rejected', 'offer_accepted', 'pending_onboard', 'onboard_cancelled', 'onboarded', 'candidate_withdrawn', name='applicationstatus'), nullable=True),
        sa.Column('to_status', sa.Enum('new', 'hr_screening', 'hr_rejected', 'hr_interview_scheduled', 'hr_interviewing', 'hr_interview_completed', 'hr_interview_rejected', 'sent_to_interviewer', 'interviewer_rejected', 'interview_intention_communication', 'candidate_declined_interview', 'interview_time_confirming', 'department_interview_scheduled', 'department_interviewing', 'department_interview_completed', 'department_interview_rejected', 'assessment_invited', 'assessment_in_progress', 'assessment_completed', 'assessment_failed', 'hr_reinterview_scheduled', 'hr_reinterviewing', 'hr_reinterview_completed', 'hr_reinterview_rejected', 'final_interview_scheduled', 'final_interviewing', 'final_interview_completed', 'final_interview_rejected', 'salary_negotiation', 'salary_rejected', 'verbal_offer_accepted', 'offer_approval', 'offer_approval_rejected', 'offer_pending', 'offer_sent', 'offer_rejected', 'offer_accepted', 'pending_onboard', 'onboard_cancelled', 'onboarded', 'candidate_withdrawn', name='applicationstatus'), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('operator_id', sa.String(), nullable=True),
        sa.Column('operator_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_status_history_id'), 'application_status_history', ['id'], unique=False)
    op.create_index(op.f('ix_application_status_history_application_id'), 'application_status_history', ['application_id'], unique=False)

    # 创建interviewer_screenings表
    op.create_table(
        'interviewer_screenings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('application_id', sa.String(), nullable=False),
        sa.Column('interviewer_id', sa.String(), nullable=False),
        sa.Column('interviewer_name', sa.String(), nullable=True),
        sa.Column('result', sa.String(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['interviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviewer_screenings_id'), 'interviewer_screenings', ['id'], unique=False)
    op.create_index(op.f('ix_interviewer_screenings_application_id'), 'interviewer_screenings', ['application_id'], unique=False)
    op.create_index(op.f('ix_interviewer_screenings_interviewer_id'), 'interviewer_screenings', ['interviewer_id'], unique=False)

    # 创建assessments表
    op.create_table(
        'assessments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('application_id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=True),
        sa.Column('assessment_type', sa.String(), nullable=True),
        sa.Column('assessment_url', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('invited', 'in_progress', 'completed', 'failed', 'expired', name='assessmentstatus'), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('result_data', sa.Text(), nullable=True),
        sa.Column('report_url', sa.Text(), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessments_id'), 'assessments', ['id'], unique=False)
    op.create_index(op.f('ix_assessments_application_id'), 'assessments', ['application_id'], unique=False)
    op.create_index(op.f('ix_assessments_candidate_id'), 'assessments', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_assessments_status'), 'assessments', ['status'], unique=False)

    # 更新interviews表，添加新字段
    op.add_column('interviews', sa.Column('application_id', sa.String(), nullable=True))
    op.add_column('interviews', sa.Column('interview_type', sa.Enum('hr_initial', 'department', 'hr_reinterview', 'final', name='interviewtype'), nullable=True))
    op.add_column('interviews', sa.Column('title', sa.String(), nullable=True))
    op.add_column('interviews', sa.Column('interviewer_name', sa.String(), nullable=True))
    op.add_column('interviews', sa.Column('scorecard_template_id', sa.String(), nullable=True))
    op.add_column('interviews', sa.Column('duration', sa.Integer(), nullable=True))
    op.add_column('interviews', sa.Column('location', sa.String(), nullable=True))
    op.add_column('interviews', sa.Column('meeting_link', sa.String(), nullable=True))
    op.add_column('interviews', sa.Column('score', sa.Integer(), nullable=True))
    op.add_column('interviews', sa.Column('evaluation_data', sa.Text(), nullable=True))
    op.add_column('interviews', sa.Column('notification_sent_to_candidate', sa.Boolean(), nullable=True, default=False))
    op.add_column('interviews', sa.Column('notification_sent_to_interviewer', sa.Boolean(), nullable=True, default=False))
    op.add_column('interviews', sa.Column('candidate_confirmed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('interviews', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    # 更新interviews表的status和result字段类型
    op.alter_column('interviews', 'status',
                    existing_type=sa.String(),
                    type_=sa.Enum('scheduled', 'confirmed', 'declined', 'cancelled', 'rescheduled', 'in_progress', 'completed', 'no_show', name='interviewstatus'),
                    existing_nullable=False)
    op.alter_column('interviews', 'result',
                    existing_type=sa.String(),
                    type_=sa.Enum('pending', 'pass', 'fail', 'hold', name='interviewresult'),
                    existing_nullable=True)

    # 添加外键
    op.create_foreign_key('fk_interviews_application', 'interviews', 'applications', ['application_id'], ['id'])
    op.create_foreign_key('fk_interviews_scorecard_template', 'interviews', 'scorecard_templates', ['scorecard_template_id'], ['id'])

    # 创建索引
    op.create_index(op.f('ix_interviews_application_id'), 'interviews', ['application_id'], unique=False)
    op.create_index(op.f('ix_interviews_interview_type'), 'interviews', ['interview_type'], unique=False)


def downgrade():
    # 删除索引
    op.drop_index(op.f('ix_interviews_interview_type'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_application_id'), table_name='interviews')

    # 删除外键
    op.drop_constraint('fk_interviews_scorecard_template', 'interviews', type_='foreignkey')
    op.drop_constraint('fk_interviews_application', 'interviews', type_='foreignkey')

    # 删除interviews表的新字段
    op.drop_column('interviews', 'completed_at')
    op.drop_column('interviews', 'candidate_confirmed_at')
    op.drop_column('interviews', 'notification_sent_to_interviewer')
    op.drop_column('interviews', 'notification_sent_to_candidate')
    op.drop_column('interviews', 'evaluation_data')
    op.drop_column('interviews', 'score')
    op.drop_column('interviews', 'meeting_link')
    op.drop_column('interviews', 'location')
    op.drop_column('interviews', 'duration')
    op.drop_column('interviews', 'scorecard_template_id')
    op.drop_column('interviews', 'interviewer_name')
    op.drop_column('interviews', 'title')
    op.drop_column('interviews', 'interview_type')
    op.drop_column('interviews', 'application_id')

    # 恢复interviews表的status和result字段类型
    op.alter_column('interviews', 'status',
                    existing_type=sa.Enum('scheduled', 'confirmed', 'declined', 'cancelled', 'rescheduled', 'in_progress', 'completed', 'no_show', name='interviewstatus'),
                    type_=sa.String(),
                    existing_nullable=False)
    op.alter_column('interviews', 'result',
                    existing_type=sa.Enum('pending', 'pass', 'fail', 'hold', name='interviewresult'),
                    type_=sa.String(),
                    existing_nullable=True)

    # 删除表
    op.drop_index(op.f('ix_assessments_status'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_candidate_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_application_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_id'), table_name='assessments')
    op.drop_table('assessments')

    op.drop_index(op.f('ix_interviewer_screenings_interviewer_id'), table_name='interviewer_screenings')
    op.drop_index(op.f('ix_interviewer_screenings_application_id'), table_name='interviewer_screenings')
    op.drop_index(op.f('ix_interviewer_screenings_id'), table_name='interviewer_screenings')
    op.drop_table('interviewer_screenings')

    op.drop_index(op.f('ix_application_status_history_application_id'), table_name='application_status_history')
    op.drop_index(op.f('ix_application_status_history_id'), table_name='application_status_history')
    op.drop_table('application_status_history')

    op.drop_index(op.f('ix_applications_is_locked'), table_name='applications')
    op.drop_index(op.f('ix_applications_hr_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_status'), table_name='applications')
    op.drop_index(op.f('ix_applications_job_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_candidate_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    op.drop_table('applications')

    # 删除枚举类型
    sa.Enum(name='assessmentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='interviewresult').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='interviewstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='interviewtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='applicationstatus').drop(op.get_bind(), checkfirst=True)
