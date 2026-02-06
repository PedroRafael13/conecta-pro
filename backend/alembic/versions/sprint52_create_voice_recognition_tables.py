"""Sprint 52: Create voice recognition tables.

Revision ID: sprint52_voice
Revises: sprint51_lpr
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers
revision = 'sprint52_voice'
down_revision = 'sprint49_meeting_assist'
branch_labels = None
depends_on = None


def create_enum_safe(name: str, values: list):
    """Cria enum de forma segura (ignora se já existir)."""
    values_str = ", ".join([f"'{v}'" for v in values])
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({values_str});
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)


def upgrade() -> None:
    # Create enums (safe)
    create_enum_safe("voice_recording_status", [
        "pending", "uploading", "uploaded", "processing",
        "transcribed", "analyzed", "failed", "archived"
    ])

    create_enum_safe("voice_recording_source", [
        "phone_call", "voicemail", "meeting", "dictation", "intercom",
        "mobile_app", "web_app", "ivr", "support_ticket", "other"
    ])

    create_enum_safe("audio_format", [
        "wav", "mp3", "ogg", "flac", "m4a", "webm", "aac", "wma", "amr", "other"
    ])

    create_enum_safe("transcription_status", [
        "pending", "processing", "completed", "partial",
        "failed", "reviewed", "corrected"
    ])

    create_enum_safe("transcription_provider", [
        "google_speech", "aws_transcribe", "azure_speech", "whisper",
        "deepgram", "assemblyai", "vosk", "local"
    ])

    create_enum_safe("voice_command_status", [
        "pending", "recognized", "executing", "completed",
        "failed", "cancelled", "requires_confirmation", "ambiguous"
    ])

    create_enum_safe("command_category", [
        "navigation", "search", "create", "update", "delete",
        "query", "report", "notification", "settings", "help", "system", "custom"
    ])

    create_enum_safe("call_analysis_status", [
        "pending", "analyzing", "completed", "partial", "failed", "reviewed"
    ])

    create_enum_safe("call_type", [
        "support", "sales", "complaint", "inquiry", "follow_up",
        "scheduling", "emergency", "intercom", "ivr", "voicemail", "internal", "other"
    ])

    create_enum_safe("call_sentiment", [
        "very_positive", "positive", "neutral", "negative", "very_negative", "mixed"
    ])

    # Create ai_voice_recordings table
    op.create_table(
        'ai_voice_recordings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('source', sa.String(50), nullable=False, server_default='other'),
        sa.Column('status', sa.String(30), nullable=False, server_default='pending', index=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_url', sa.String(1000), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_size_bytes', sa.Integer, nullable=True),
        sa.Column('audio_format', sa.String(20), nullable=False, server_default='wav'),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('checksum', sa.String(64), nullable=True),
        sa.Column('duration_seconds', sa.Float, nullable=True),
        sa.Column('sample_rate', sa.Integer, nullable=True),
        sa.Column('channels', sa.Integer, nullable=False, server_default='1'),
        sa.Column('bit_depth', sa.Integer, nullable=True),
        sa.Column('bitrate', sa.Integer, nullable=True),
        sa.Column('language', sa.String(10), nullable=False, server_default='pt-BR'),
        sa.Column('detected_language', sa.String(10), nullable=True),
        sa.Column('language_confidence', sa.Float, nullable=True),
        sa.Column('speaker_count', sa.Integer, nullable=True),
        sa.Column('speakers', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('noise_level', sa.Float, nullable=True),
        sa.Column('signal_to_noise', sa.Float, nullable=True),
        sa.Column('quality_issues', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('caller_phone', sa.String(20), nullable=True),
        sa.Column('callee_phone', sa.String(20), nullable=True),
        sa.Column('call_direction', sa.String(10), nullable=True),
        sa.Column('call_start_at', sa.DateTime, nullable=True),
        sa.Column('call_end_at', sa.DateTime, nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('processed_at', sa.DateTime, nullable=True),
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create ai_transcriptions table
    op.create_table(
        'ai_transcriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('recording_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_voice_recordings.id'), nullable=False, index=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='pending', index=True),
        sa.Column('provider', sa.String(50), nullable=False, server_default='whisper'),
        sa.Column('text', sa.Text, nullable=True),
        sa.Column('text_formatted', sa.Text, nullable=True),
        sa.Column('text_cleaned', sa.Text, nullable=True),
        sa.Column('words', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('word_count', sa.Integer, nullable=True),
        sa.Column('unique_words', sa.Integer, nullable=True),
        sa.Column('segments', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('segment_count', sa.Integer, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('confidence_min', sa.Float, nullable=True),
        sa.Column('confidence_max', sa.Float, nullable=True),
        sa.Column('low_confidence_words', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('language', sa.String(10), nullable=False, server_default='pt-BR'),
        sa.Column('detected_language', sa.String(10), nullable=True),
        sa.Column('language_confidence', sa.Float, nullable=True),
        sa.Column('speaker_labels', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('speaker_count', sa.Integer, nullable=True),
        sa.Column('speakers', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('duration_seconds', sa.Float, nullable=True),
        sa.Column('words_per_minute', sa.Float, nullable=True),
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('options_used', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('has_corrections', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('corrections', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('corrected_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('corrected_at', sa.DateTime, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create ai_transcription_segments table
    op.create_table(
        'ai_transcription_segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('transcription_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_transcriptions.id'), nullable=False, index=True),
        sa.Column('segment_index', sa.Integer, nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('start_time', sa.Float, nullable=False),
        sa.Column('end_time', sa.Float, nullable=False),
        sa.Column('duration', sa.Float, nullable=True),
        sa.Column('speaker_id', sa.String(50), nullable=True),
        sa.Column('speaker_name', sa.String(100), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('words', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('word_count', sa.Integer, nullable=True),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('sentiment_score', sa.Float, nullable=True),
        sa.Column('keywords', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('entities', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('is_question', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('is_command', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('contains_action_item', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Create ai_command_definitions table
    op.create_table(
        'ai_command_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, index=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(30), nullable=False, server_default='custom'),
        sa.Column('phrases', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('synonyms', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('regex_patterns', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('parameters', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('required_params', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('optional_params', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('action_config', postgresql.JSONB, nullable=False),
        sa.Column('success_response', sa.Text, nullable=True),
        sa.Column('error_response', sa.Text, nullable=True),
        sa.Column('confirmation_prompt', sa.Text, nullable=True),
        sa.Column('requires_confirmation', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('is_dangerous', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('min_confidence', sa.Float, nullable=False, server_default='0.7'),
        sa.Column('priority', sa.Integer, nullable=False, server_default='50'),
        sa.Column('allowed_roles', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('denied_roles', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('total_uses', sa.Integer, nullable=False, server_default='0'),
        sa.Column('success_rate', sa.Float, nullable=True),
        sa.Column('avg_confidence', sa.Float, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_system', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create ai_voice_commands table
    op.create_table(
        'ai_voice_commands',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('recording_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_voice_recordings.id'), nullable=True),
        sa.Column('transcription_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_transcriptions.id'), nullable=True),
        sa.Column('raw_text', sa.Text, nullable=False),
        sa.Column('normalized_text', sa.Text, nullable=True),
        sa.Column('command_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_command_definitions.id'), nullable=True),
        sa.Column('command_code', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('alternatives', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('parameters', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('missing_params', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(30), nullable=False, server_default='pending', index=True),
        sa.Column('executed_at', sa.DateTime, nullable=True),
        sa.Column('execution_time_ms', sa.Integer, nullable=True),
        sa.Column('action_result', postgresql.JSONB, nullable=True),
        sa.Column('response_text', sa.Text, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('requires_confirmation', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('confirmed', sa.Boolean, nullable=True),
        sa.Column('confirmed_at', sa.DateTime, nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('context', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('user_feedback', sa.String(20), nullable=True),
        sa.Column('feedback_text', sa.Text, nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('app_version', sa.String(20), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create ai_call_analyses table
    op.create_table(
        'ai_call_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('recording_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_voice_recordings.id'), nullable=False, index=True),
        sa.Column('transcription_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_transcriptions.id'), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='pending', index=True),
        sa.Column('call_type', sa.String(30), nullable=True, index=True),
        sa.Column('call_type_confidence', sa.Float, nullable=True),
        sa.Column('call_categories', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('agent_name', sa.String(100), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('customer_name', sa.String(100), nullable=True),
        sa.Column('participant_count', sa.Integer, nullable=False, server_default='2'),
        sa.Column('total_duration_seconds', sa.Float, nullable=True),
        sa.Column('agent_talk_time', sa.Float, nullable=True),
        sa.Column('customer_talk_time', sa.Float, nullable=True),
        sa.Column('silence_time', sa.Float, nullable=True),
        sa.Column('hold_time', sa.Float, nullable=True),
        sa.Column('talk_ratio', sa.Float, nullable=True),
        sa.Column('overall_sentiment', sa.String(20), nullable=True),
        sa.Column('sentiment_score', sa.Float, nullable=True),
        sa.Column('sentiment_timeline', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('agent_sentiment', sa.Float, nullable=True),
        sa.Column('customer_sentiment', sa.Float, nullable=True),
        sa.Column('emotions_detected', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('dominant_emotion', sa.String(30), nullable=True),
        sa.Column('emotion_timeline', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('topics', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('primary_topic', sa.String(100), nullable=True),
        sa.Column('intents', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('keywords', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('entities', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('issues_identified', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('complaint_detected', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('escalation_needed', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('escalation_reason', sa.Text, nullable=True),
        sa.Column('resolution_status', sa.String(30), nullable=True),
        sa.Column('resolution_summary', sa.Text, nullable=True),
        sa.Column('action_items', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('follow_up_required', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('follow_up_date', sa.DateTime, nullable=True),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('quality_breakdown', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('agent_score', sa.Float, nullable=True),
        sa.Column('agent_metrics', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('csat_predicted', sa.Float, nullable=True),
        sa.Column('nps_predicted', sa.Float, nullable=True),
        sa.Column('effort_score', sa.Float, nullable=True),
        sa.Column('compliance_score', sa.Float, nullable=True),
        sa.Column('compliance_issues', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('required_disclosures', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('pii_detected', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('key_points', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('recommendations', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('alerts', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('analyzed_at', sa.DateTime, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime, nullable=True),
        sa.Column('review_notes', sa.Text, nullable=True),
        sa.Column('review_corrections', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create indexes
    op.create_index('ix_ai_voice_recordings_source_status', 'ai_voice_recordings', ['source', 'status'])
    op.create_index('ix_ai_transcriptions_status_provider', 'ai_transcriptions', ['status', 'provider'])
    op.create_index('ix_ai_call_analyses_type_sentiment', 'ai_call_analyses', ['call_type', 'overall_sentiment'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('ai_call_analyses')
    op.drop_table('ai_voice_commands')
    op.drop_table('ai_command_definitions')
    op.drop_table('ai_transcription_segments')
    op.drop_table('ai_transcriptions')
    op.drop_table('ai_voice_recordings')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS call_sentiment')
    op.execute('DROP TYPE IF EXISTS call_type')
    op.execute('DROP TYPE IF EXISTS call_analysis_status')
    op.execute('DROP TYPE IF EXISTS command_category')
    op.execute('DROP TYPE IF EXISTS voice_command_status')
    op.execute('DROP TYPE IF EXISTS transcription_provider')
    op.execute('DROP TYPE IF EXISTS transcription_status')
    op.execute('DROP TYPE IF EXISTS audio_format')
    op.execute('DROP TYPE IF EXISTS voice_recording_source')
    op.execute('DROP TYPE IF EXISTS voice_recording_status')
