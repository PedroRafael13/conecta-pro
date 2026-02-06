"""Sprint 49: Create meeting assistant tables

Revision ID: sprint49_meeting_assist
Revises: sprint48_data_quality
Create Date: 2026-01-06

Cria tabelas para o módulo AI Meeting/Task Assistant:
- ai_meetings: Reuniões
- ai_meeting_participants: Participantes das reuniões
- ai_meeting_notes: Notas das reuniões
- ai_meeting_summaries: Resumos gerados por IA
- ai_tasks: Tarefas
- ai_task_dependencies: Dependências entre tarefas
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers
revision = 'sprint49_meeting_assist'
down_revision = 'sprint48_data_quality'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============== ENUMS ==============

    # Meeting Status Enum
    meeting_status_enum = postgresql.ENUM(
        'SCHEDULED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED',
        'CANCELLED', 'RESCHEDULED', 'NO_SHOW',
        name='meetingstatus_enum',
        create_type=False
    )

    # Meeting Type Enum
    meeting_type_enum = postgresql.ENUM(
        'INTERNAL', 'EXTERNAL', 'ONE_ON_ONE', 'TEAM', 'ALL_HANDS',
        'INTERVIEW', 'CLIENT', 'BOARD', 'STANDUP', 'RETROSPECTIVE',
        'PLANNING', 'REVIEW', 'TRAINING', 'WORKSHOP', 'WEBINAR', 'OTHER',
        name='meetingtype_enum',
        create_type=False
    )

    # Participant Status Enum
    participant_status_enum = postgresql.ENUM(
        'PENDING', 'ACCEPTED', 'DECLINED', 'TENTATIVE', 'NO_RESPONSE',
        name='participantstatus_enum',
        create_type=False
    )

    # Participant Role Enum
    participant_role_enum = postgresql.ENUM(
        'ORGANIZER', 'REQUIRED', 'OPTIONAL', 'PRESENTER', 'NOTE_TAKER', 'OBSERVER',
        name='participantrole_enum',
        create_type=False
    )

    # Recurrence Type Enum
    recurrence_type_enum = postgresql.ENUM(
        'NONE', 'DAILY', 'WEEKLY', 'BIWEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY', 'CUSTOM',
        name='recurrencetype_enum',
        create_type=False
    )

    # Task Status Enum
    task_status_enum = postgresql.ENUM(
        'BACKLOG', 'TODO', 'IN_PROGRESS', 'IN_REVIEW', 'BLOCKED',
        'COMPLETED', 'CANCELLED', 'ON_HOLD',
        name='taskstatus_enum',
        create_type=False
    )

    # Task Priority Enum
    task_priority_enum = postgresql.ENUM(
        'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE',
        name='taskpriority_enum',
        create_type=False
    )

    # Task Type Enum
    task_type_enum = postgresql.ENUM(
        'TASK', 'BUG', 'FEATURE', 'IMPROVEMENT', 'STORY', 'EPIC',
        'SUBTASK', 'MAINTENANCE', 'DOCUMENTATION', 'RESEARCH',
        'MEETING_ACTION', 'FOLLOW_UP',
        name='tasktype_enum',
        create_type=False
    )

    # Dependency Type Enum
    dependency_type_enum = postgresql.ENUM(
        'BLOCKS', 'BLOCKED_BY', 'RELATES_TO', 'DUPLICATES', 'PARENT_OF', 'CHILD_OF',
        name='dependencytype_enum',
        create_type=False
    )

    # Create all enums
    meeting_status_enum.create(op.get_bind(), checkfirst=True)
    meeting_type_enum.create(op.get_bind(), checkfirst=True)
    participant_status_enum.create(op.get_bind(), checkfirst=True)
    participant_role_enum.create(op.get_bind(), checkfirst=True)
    recurrence_type_enum.create(op.get_bind(), checkfirst=True)
    task_status_enum.create(op.get_bind(), checkfirst=True)
    task_priority_enum.create(op.get_bind(), checkfirst=True)
    task_type_enum.create(op.get_bind(), checkfirst=True)
    dependency_type_enum.create(op.get_bind(), checkfirst=True)

    # ============== TABLES ==============

    # 1. ai_meetings
    op.create_table(
        'ai_meetings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('meeting_code', sa.String(50), nullable=False, unique=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('meeting_type', postgresql.ENUM(
            'INTERNAL', 'EXTERNAL', 'ONE_ON_ONE', 'TEAM', 'ALL_HANDS',
            'INTERVIEW', 'CLIENT', 'BOARD', 'STANDUP', 'RETROSPECTIVE',
            'PLANNING', 'REVIEW', 'TRAINING', 'WORKSHOP', 'WEBINAR', 'OTHER',
            name='meetingtype_enum', create_type=False
        ), nullable=False, server_default='INTERNAL'),
        sa.Column('status', postgresql.ENUM(
            'SCHEDULED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED',
            'CANCELLED', 'RESCHEDULED', 'NO_SHOW',
            name='meetingstatus_enum', create_type=False
        ), nullable=False, server_default='SCHEDULED'),
        sa.Column('scheduled_start', sa.DateTime, nullable=False),
        sa.Column('scheduled_end', sa.DateTime, nullable=False),
        sa.Column('actual_start', sa.DateTime),
        sa.Column('actual_end', sa.DateTime),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('timezone', sa.String(50), server_default='America/Sao_Paulo'),
        sa.Column('location', sa.String(500)),
        sa.Column('is_virtual', sa.Boolean, server_default='true'),
        sa.Column('virtual_link', sa.String(1000)),
        sa.Column('virtual_platform', sa.String(100)),
        sa.Column('room_id', sa.String(100)),
        sa.Column('is_recurring', sa.Boolean, server_default='false'),
        sa.Column('recurrence_type', postgresql.ENUM(
            'NONE', 'DAILY', 'WEEKLY', 'BIWEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY', 'CUSTOM',
            name='recurrencetype_enum', create_type=False
        ), server_default='NONE'),
        sa.Column('recurrence_pattern', postgresql.JSONB, server_default='{}'),
        sa.Column('recurrence_end_date', sa.DateTime),
        sa.Column('parent_meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_meetings.id')),
        sa.Column('occurrence_number', sa.Integer),
        sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organizer_name', sa.String(200)),
        sa.Column('organizer_email', sa.String(200)),
        sa.Column('department', sa.String(100)),
        sa.Column('project_id', postgresql.UUID(as_uuid=True)),
        sa.Column('agenda', postgresql.JSONB, server_default='[]'),
        sa.Column('objectives', postgresql.JSONB, server_default='[]'),
        sa.Column('preparation_notes', sa.Text),
        sa.Column('attachments', postgresql.JSONB, server_default='[]'),
        sa.Column('meeting_notes', sa.Text),
        sa.Column('action_items', postgresql.JSONB, server_default='[]'),
        sa.Column('decisions', postgresql.JSONB, server_default='[]'),
        sa.Column('ai_suggested', sa.Boolean, server_default='false'),
        sa.Column('ai_suggestion_reason', sa.Text),
        sa.Column('auto_schedule_enabled', sa.Boolean, server_default='false'),
        sa.Column('smart_reminder_sent', sa.Boolean, server_default='false'),
        sa.Column('sentiment_score', sa.Float),
        sa.Column('effectiveness_score', sa.Float),
        sa.Column('reminder_minutes', postgresql.ARRAY(sa.Integer), server_default='{15,60,1440}'),
        sa.Column('notifications_sent', postgresql.JSONB, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('category', sa.String(100)),
        sa.Column('priority', sa.Integer, server_default='50'),
        sa.Column('external_calendar_id', sa.String(200)),
        sa.Column('sync_status', sa.String(50)),
        sa.Column('last_synced_at', sa.DateTime),
        sa.Column('extra_metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('ativo', sa.Boolean, server_default='true'),
    )

    op.create_index('ix_meetings_organizer_id', 'ai_meetings', ['organizer_id'])
    op.create_index('ix_meetings_scheduled_start', 'ai_meetings', ['scheduled_start'])
    op.create_index('ix_meetings_status', 'ai_meetings', ['status'])

    # 2. ai_meeting_participants
    op.create_table(
        'ai_meeting_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_meetings.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(200), nullable=False),
        sa.Column('phone', sa.String(50)),
        sa.Column('department', sa.String(100)),
        sa.Column('company', sa.String(200)),
        sa.Column('role', postgresql.ENUM(
            'ORGANIZER', 'REQUIRED', 'OPTIONAL', 'PRESENTER', 'NOTE_TAKER', 'OBSERVER',
            name='participantrole_enum', create_type=False
        ), nullable=False, server_default='REQUIRED'),
        sa.Column('status', postgresql.ENUM(
            'PENDING', 'ACCEPTED', 'DECLINED', 'TENTATIVE', 'NO_RESPONSE',
            name='participantstatus_enum', create_type=False
        ), nullable=False, server_default='PENDING'),
        sa.Column('response_date', sa.DateTime),
        sa.Column('response_note', sa.Text),
        sa.Column('attended', sa.Boolean),
        sa.Column('joined_at', sa.DateTime),
        sa.Column('left_at', sa.DateTime),
        sa.Column('attendance_duration_minutes', sa.Integer),
        sa.Column('invitation_sent', sa.Boolean, server_default='false'),
        sa.Column('invitation_sent_at', sa.DateTime),
        sa.Column('reminder_sent', sa.Boolean, server_default='false'),
        sa.Column('reminder_sent_at', sa.DateTime),
        sa.Column('preferred_notification_method', sa.String(50)),
        sa.Column('calendar_synced', sa.Boolean, server_default='false'),
        sa.Column('extra_metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
    )

    op.create_index('ix_participants_meeting_id', 'ai_meeting_participants', ['meeting_id'])
    op.create_index('ix_participants_user_id', 'ai_meeting_participants', ['user_id'])

    # 3. ai_meeting_notes
    op.create_table(
        'ai_meeting_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_meetings.id'), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_name', sa.String(200)),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('content_type', sa.String(50), server_default='text'),
        sa.Column('is_private', sa.Boolean, server_default='false'),
        sa.Column('note_type', sa.String(50)),
        sa.Column('agenda_item_index', sa.Integer),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
    )

    op.create_index('ix_meeting_notes_meeting_id', 'ai_meeting_notes', ['meeting_id'])

    # 4. ai_meeting_summaries
    op.create_table(
        'ai_meeting_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_meetings.id'), nullable=False),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('key_points', postgresql.JSONB, server_default='[]'),
        sa.Column('action_items', postgresql.JSONB, server_default='[]'),
        sa.Column('decisions', postgresql.JSONB, server_default='[]'),
        sa.Column('next_steps', postgresql.JSONB, server_default='[]'),
        sa.Column('topics_discussed', postgresql.JSONB, server_default='[]'),
        sa.Column('participant_contributions', postgresql.JSONB, server_default='{}'),
        sa.Column('sentiment_analysis', postgresql.JSONB, server_default='{}'),
        sa.Column('keywords', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('ai_model', sa.String(100)),
        sa.Column('ai_confidence', sa.Float),
        sa.Column('generation_time_seconds', sa.Float),
        sa.Column('is_reviewed', sa.Boolean, server_default='false'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True)),
        sa.Column('reviewed_at', sa.DateTime),
        sa.Column('is_published', sa.Boolean, server_default='false'),
        sa.Column('published_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
    )

    op.create_index('ix_meeting_summaries_meeting_id', 'ai_meeting_summaries', ['meeting_id'])

    # 5. ai_tasks
    op.create_table(
        'ai_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_code', sa.String(50), nullable=False, unique=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('task_type', postgresql.ENUM(
            'TASK', 'BUG', 'FEATURE', 'IMPROVEMENT', 'STORY', 'EPIC',
            'SUBTASK', 'MAINTENANCE', 'DOCUMENTATION', 'RESEARCH',
            'MEETING_ACTION', 'FOLLOW_UP',
            name='tasktype_enum', create_type=False
        ), nullable=False, server_default='TASK'),
        sa.Column('status', postgresql.ENUM(
            'BACKLOG', 'TODO', 'IN_PROGRESS', 'IN_REVIEW', 'BLOCKED',
            'COMPLETED', 'CANCELLED', 'ON_HOLD',
            name='taskstatus_enum', create_type=False
        ), nullable=False, server_default='TODO'),
        sa.Column('priority', postgresql.ENUM(
            'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE',
            name='taskpriority_enum', create_type=False
        ), nullable=False, server_default='MEDIUM'),
        sa.Column('ai_priority_score', sa.Float),
        sa.Column('ai_priority_factors', postgresql.JSONB, server_default='{}'),
        sa.Column('ai_suggested_priority', postgresql.ENUM(
            'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE',
            name='taskpriority_enum', create_type=False
        )),
        sa.Column('priority_last_calculated', sa.DateTime),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True)),
        sa.Column('assignee_name', sa.String(200)),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True)),
        sa.Column('reporter_name', sa.String(200)),
        sa.Column('watchers', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('due_date', sa.DateTime),
        sa.Column('start_date', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('ai_suggested_due_date', sa.DateTime),
        sa.Column('estimated_hours', sa.Float),
        sa.Column('actual_hours', sa.Float),
        sa.Column('remaining_hours', sa.Float),
        sa.Column('ai_estimated_hours', sa.Float),
        sa.Column('story_points', sa.Integer),
        sa.Column('project_id', postgresql.UUID(as_uuid=True)),
        sa.Column('project_name', sa.String(200)),
        sa.Column('sprint_id', postgresql.UUID(as_uuid=True)),
        sa.Column('sprint_name', sa.String(100)),
        sa.Column('epic_id', postgresql.UUID(as_uuid=True)),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_tasks.id')),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_meetings.id')),
        sa.Column('meeting_action_index', sa.Integer),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('labels', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('category', sa.String(100)),
        sa.Column('department', sa.String(100)),
        sa.Column('progress_percentage', sa.Float, server_default='0'),
        sa.Column('checklist', postgresql.JSONB, server_default='[]'),
        sa.Column('checklist_completed', sa.Integer, server_default='0'),
        sa.Column('checklist_total', sa.Integer, server_default='0'),
        sa.Column('is_blocked', sa.Boolean, server_default='false'),
        sa.Column('blocked_reason', sa.Text),
        sa.Column('blocked_since', sa.DateTime),
        sa.Column('context', sa.Text),
        sa.Column('acceptance_criteria', postgresql.JSONB, server_default='[]'),
        sa.Column('attachments', postgresql.JSONB, server_default='[]'),
        sa.Column('links', postgresql.JSONB, server_default='[]'),
        sa.Column('comments_count', sa.Integer, server_default='0'),
        sa.Column('last_comment_at', sa.DateTime),
        sa.Column('activity_log', postgresql.JSONB, server_default='[]'),
        sa.Column('ai_generated', sa.Boolean, server_default='false'),
        sa.Column('ai_generation_source', sa.String(100)),
        sa.Column('ai_suggestions', postgresql.JSONB, server_default='[]'),
        sa.Column('smart_notifications_enabled', sa.Boolean, server_default='true'),
        sa.Column('is_recurring', sa.Boolean, server_default='false'),
        sa.Column('recurrence_pattern', postgresql.JSONB, server_default='{}'),
        sa.Column('recurrence_end_date', sa.DateTime),
        sa.Column('parent_recurring_task_id', postgresql.UUID(as_uuid=True)),
        sa.Column('cycle_time_hours', sa.Float),
        sa.Column('lead_time_hours', sa.Float),
        sa.Column('time_in_status', postgresql.JSONB, server_default='{}'),
        sa.Column('external_id', sa.String(200)),
        sa.Column('external_url', sa.String(1000)),
        sa.Column('extra_metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('ativo', sa.Boolean, server_default='true'),
    )

    op.create_index('ix_tasks_assignee_id', 'ai_tasks', ['assignee_id'])
    op.create_index('ix_tasks_status', 'ai_tasks', ['status'])
    op.create_index('ix_tasks_priority', 'ai_tasks', ['priority'])
    op.create_index('ix_tasks_due_date', 'ai_tasks', ['due_date'])
    op.create_index('ix_tasks_meeting_id', 'ai_tasks', ['meeting_id'])
    op.create_index('ix_tasks_project_id', 'ai_tasks', ['project_id'])

    # 6. ai_task_dependencies
    op.create_table(
        'ai_task_dependencies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_tasks.id'), nullable=False),
        sa.Column('related_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_tasks.id'), nullable=False),
        sa.Column('dependency_type', postgresql.ENUM(
            'BLOCKS', 'BLOCKED_BY', 'RELATES_TO', 'DUPLICATES', 'PARENT_OF', 'CHILD_OF',
            name='dependencytype_enum', create_type=False
        ), nullable=False, server_default='RELATES_TO'),
        sa.Column('description', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
    )

    op.create_index('ix_task_dependencies_task_id', 'ai_task_dependencies', ['task_id'])
    op.create_index('ix_task_dependencies_related', 'ai_task_dependencies', ['related_task_id'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('ai_task_dependencies')
    op.drop_table('ai_tasks')
    op.drop_table('ai_meeting_summaries')
    op.drop_table('ai_meeting_notes')
    op.drop_table('ai_meeting_participants')
    op.drop_table('ai_meetings')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS dependencytype_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS tasktype_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS taskpriority_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS taskstatus_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS recurrencetype_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS participantrole_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS participantstatus_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS meetingtype_enum CASCADE')
    op.execute('DROP TYPE IF EXISTS meetingstatus_enum CASCADE')
