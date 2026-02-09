"""
Voice Recognition Schemas - Sprint 52.

Pydantic schemas for voice recognition API.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# ============== Voice Recording Schemas ==============


class VoiceRecordingCreate(BaseModel):
    """Schema for creating a voice recording."""

    title: str | None = Field(None, max_length=255)
    description: str | None = None
    source: str = Field(default="other")
    language: str = Field(default="pt-BR")
    caller_phone: str | None = Field(None, max_length=20)
    callee_phone: str | None = Field(None, max_length=20)
    call_direction: str | None = None
    user_id: UUID | None = None
    contact_id: UUID | None = None
    ticket_id: UUID | None = None
    meeting_id: UUID | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source")
    @classmethod
    def validate_source(cls, v):
        valid = [
            "phone_call",
            "voicemail",
            "meeting",
            "dictation",
            "intercom",
            "mobile_app",
            "web_app",
            "ivr",
            "support_ticket",
            "other",
        ]
        if v not in valid:
            raise ValueError(f"Source must be one of: {valid}")
        return v


class VoiceRecordingUpdate(BaseModel):
    """Schema for updating a voice recording."""

    title: str | None = Field(None, max_length=255)
    description: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class VoiceRecordingUpload(BaseModel):
    """Schema for uploading audio file info."""

    file_name: str
    file_size_bytes: int
    audio_format: str
    mime_type: str | None = None
    duration_seconds: float | None = None
    sample_rate: int | None = None
    channels: int | None = 1

    @field_validator("audio_format")
    @classmethod
    def validate_format(cls, v):
        valid = ["wav", "mp3", "ogg", "flac", "m4a", "webm", "aac", "wma", "amr", "other"]
        if v.lower() not in valid:
            raise ValueError(f"Audio format must be one of: {valid}")
        return v.lower()


class VoiceRecordingResponse(BaseModel):
    """Schema for voice recording response."""

    id: UUID
    tenant_id: UUID
    title: str | None
    description: str | None
    source: str
    status: str
    file_name: str | None
    file_size_bytes: int | None
    audio_format: str
    duration_seconds: float | None
    language: str
    detected_language: str | None
    speaker_count: int | None
    quality_score: float | None
    caller_phone: str | None
    callee_phone: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


# ============== Transcription Schemas ==============


class TranscribeRequest(BaseModel):
    """Schema for transcription request."""

    recording_id: UUID
    provider: str = Field(default="whisper")
    language: str = Field(default="pt-BR")
    enable_speaker_labels: bool = Field(default=True)
    enable_punctuation: bool = Field(default=True)
    options: dict[str, Any] = Field(default_factory=dict)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        valid = [
            "google_speech",
            "aws_transcribe",
            "azure_speech",
            "whisper",
            "deepgram",
            "assemblyai",
            "vosk",
            "local",
        ]
        if v not in valid:
            raise ValueError(f"Provider must be one of: {valid}")
        return v


class TranscriptionCreate(BaseModel):
    """Schema for creating transcription record."""

    recording_id: UUID
    provider: str = "whisper"
    language: str = "pt-BR"


class TranscriptionSegmentResponse(BaseModel):
    """Schema for transcription segment."""

    segment_index: int
    text: str
    start_time: float
    end_time: float
    duration: float | None
    speaker_id: str | None
    speaker_name: str | None
    confidence: float | None
    sentiment: str | None
    keywords: list[str]

    class Config:
        from_attributes = True


class TranscriptionResponse(BaseModel):
    """Schema for transcription response."""

    id: UUID
    tenant_id: UUID
    recording_id: UUID
    status: str
    provider: str
    text: str | None
    text_formatted: str | None
    word_count: int | None
    segment_count: int | None
    confidence_score: float | None
    language: str
    detected_language: str | None
    speaker_count: int | None
    speakers: list[dict]
    duration_seconds: float | None
    words_per_minute: float | None
    processing_time_ms: int | None
    has_corrections: bool
    error_message: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


# ============== Voice Command Schemas ==============


class CommandDefinitionCreate(BaseModel):
    """Schema for creating command definition."""

    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    category: str = Field(default="custom")
    phrases: list[str] = Field(..., min_items=1)
    synonyms: dict[str, list[str]] = Field(default_factory=dict)
    parameters: list[dict] = Field(default_factory=list)
    action_type: str
    action_config: dict[str, Any]
    success_response: str | None = None
    error_response: str | None = None
    confirmation_prompt: str | None = None
    requires_confirmation: bool = False
    is_dangerous: bool = False
    min_confidence: float = Field(default=0.7, ge=0, le=1)
    priority: int = Field(default=50, ge=0, le=100)
    allowed_roles: list[str] = Field(default_factory=list)

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, v):
        valid = ["api_call", "workflow", "function", "navigate", "query", "custom"]
        if v not in valid:
            raise ValueError(f"Action type must be one of: {valid}")
        return v


class CommandDefinitionUpdate(BaseModel):
    """Schema for updating command definition."""

    name: str | None = Field(None, max_length=100)
    description: str | None = None
    phrases: list[str] | None = None
    synonyms: dict[str, list[str]] | None = None
    parameters: list[dict] | None = None
    action_config: dict[str, Any] | None = None
    success_response: str | None = None
    error_response: str | None = None
    requires_confirmation: bool | None = None
    min_confidence: float | None = Field(None, ge=0, le=1)
    priority: int | None = Field(None, ge=0, le=100)
    is_active: bool | None = None


class CommandDefinitionResponse(BaseModel):
    """Schema for command definition response."""

    id: UUID
    tenant_id: UUID | None
    name: str
    code: str
    description: str | None
    category: str
    phrases: list[str]
    parameters: list[dict]
    action_type: str
    requires_confirmation: bool
    is_dangerous: bool
    min_confidence: float
    priority: int
    total_uses: int
    success_rate: float | None
    is_active: bool
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceCommandCreate(BaseModel):
    """Schema for creating voice command."""

    raw_text: str = Field(..., min_length=1)
    recording_id: UUID | None = None
    transcription_id: UUID | None = None
    session_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    device_type: str | None = None


class CommandExecuteRequest(BaseModel):
    """Schema for executing a voice command."""

    text: str = Field(..., min_length=1)
    session_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    auto_confirm: bool = False


class CommandExecuteResponse(BaseModel):
    """Schema for command execution response."""

    command_id: UUID
    recognized: bool
    command_code: str | None
    confidence: float | None
    status: str
    requires_confirmation: bool
    confirmation_prompt: str | None
    response_text: str | None
    result: dict | None
    alternatives: list[dict]
    missing_params: list[str]
    error_message: str | None


class VoiceCommandResponse(BaseModel):
    """Schema for voice command response."""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    raw_text: str
    command_code: str | None
    confidence: float | None
    status: str
    parameters: dict
    response_text: str | None
    action_result: dict | None
    execution_time_ms: int | None
    requires_confirmation: bool
    confirmed: bool | None
    user_feedback: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Call Analysis Schemas ==============


class AnalyzeCallRequest(BaseModel):
    """Schema for call analysis request."""

    recording_id: UUID
    transcription_id: UUID | None = None
    agent_id: UUID | None = None
    customer_id: UUID | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class CallAnalysisCreate(BaseModel):
    """Schema for creating call analysis."""

    recording_id: UUID
    transcription_id: UUID | None = None
    agent_id: UUID | None = None
    agent_name: str | None = None
    customer_id: UUID | None = None
    customer_name: str | None = None


class CallAnalysisSummary(BaseModel):
    """Schema for call analysis summary."""

    id: UUID
    recording_id: UUID
    status: str
    call_type: str | None
    overall_sentiment: str | None
    sentiment_score: float | None
    quality_score: float | None
    csat_predicted: float | None
    complaint_detected: bool
    escalation_needed: bool
    resolution_status: str | None
    summary: str | None
    key_points: list[str]
    issues_count: int
    action_items_count: int
    analyzed_at: datetime | None

    class Config:
        from_attributes = True


class CallAnalysisResponse(BaseModel):
    """Schema for full call analysis response."""

    id: UUID
    tenant_id: UUID
    recording_id: UUID
    transcription_id: UUID | None
    status: str
    call_type: str | None
    call_type_confidence: float | None
    call_categories: list[str]
    agent_id: UUID | None
    agent_name: str | None
    customer_id: UUID | None
    customer_name: str | None
    total_duration_seconds: float | None
    agent_talk_time: float | None
    customer_talk_time: float | None
    talk_ratio: float | None
    overall_sentiment: str | None
    sentiment_score: float | None
    agent_sentiment: float | None
    customer_sentiment: float | None
    emotions_detected: dict
    dominant_emotion: str | None
    topics: list[str]
    primary_topic: str | None
    keywords: list[str]
    issues_identified: list[dict]
    complaint_detected: bool
    escalation_needed: bool
    escalation_reason: str | None
    resolution_status: str | None
    resolution_summary: str | None
    action_items: list[dict]
    follow_up_required: bool
    quality_score: float | None
    quality_breakdown: dict
    agent_score: float | None
    agent_metrics: dict
    csat_predicted: float | None
    nps_predicted: float | None
    compliance_score: float | None
    compliance_issues: list[dict]
    summary: str | None
    key_points: list[str]
    recommendations: list[str]
    alerts: list[dict]
    processing_time_ms: int | None
    analyzed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Dashboard Schemas ==============


class VoiceRecognitionDashboard(BaseModel):
    """Schema for voice recognition dashboard."""

    total_recordings: int
    total_transcriptions: int
    total_commands: int
    total_calls_analyzed: int
    avg_transcription_confidence: float | None
    avg_call_quality_score: float | None
    avg_csat_predicted: float | None
    recordings_by_source: dict[str, int]
    recordings_by_status: dict[str, int]
    calls_by_type: dict[str, int]
    calls_by_sentiment: dict[str, int]
    commands_by_category: dict[str, int]
    command_success_rate: float | None
    escalation_rate: float | None
    top_topics: list[dict]
    top_commands: list[dict]
    recent_alerts: list[dict]
