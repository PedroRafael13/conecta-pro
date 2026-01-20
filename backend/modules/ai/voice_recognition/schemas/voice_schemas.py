"""
Voice Recognition Schemas - Sprint 52.

Pydantic schemas for voice recognition API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


# ============== Voice Recording Schemas ==============

class VoiceRecordingCreate(BaseModel):
    """Schema for creating a voice recording."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    source: str = Field(default="other")
    language: str = Field(default="pt-BR")
    caller_phone: Optional[str] = Field(None, max_length=20)
    callee_phone: Optional[str] = Field(None, max_length=20)
    call_direction: Optional[str] = None
    user_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    ticket_id: Optional[UUID] = None
    meeting_id: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("source")
    def validate_source(cls, v):
        valid = ["phone_call", "voicemail", "meeting", "dictation", "intercom",
                 "mobile_app", "web_app", "ivr", "support_ticket", "other"]
        if v not in valid:
            raise ValueError(f"Source must be one of: {valid}")
        return v


class VoiceRecordingUpdate(BaseModel):
    """Schema for updating a voice recording."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class VoiceRecordingUpload(BaseModel):
    """Schema for uploading audio file info."""
    file_name: str
    file_size_bytes: int
    audio_format: str
    mime_type: Optional[str] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = 1

    @validator("audio_format")
    def validate_format(cls, v):
        valid = ["wav", "mp3", "ogg", "flac", "m4a", "webm", "aac", "wma", "amr", "other"]
        if v.lower() not in valid:
            raise ValueError(f"Audio format must be one of: {valid}")
        return v.lower()


class VoiceRecordingResponse(BaseModel):
    """Schema for voice recording response."""
    id: UUID
    tenant_id: UUID
    title: Optional[str]
    description: Optional[str]
    source: str
    status: str
    file_name: Optional[str]
    file_size_bytes: Optional[int]
    audio_format: str
    duration_seconds: Optional[float]
    language: str
    detected_language: Optional[str]
    speaker_count: Optional[int]
    quality_score: Optional[float]
    caller_phone: Optional[str]
    callee_phone: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: Optional[datetime]

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
    options: Dict[str, Any] = Field(default_factory=dict)

    @validator("provider")
    def validate_provider(cls, v):
        valid = ["google_speech", "aws_transcribe", "azure_speech", "whisper",
                 "deepgram", "assemblyai", "vosk", "local"]
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
    duration: Optional[float]
    speaker_id: Optional[str]
    speaker_name: Optional[str]
    confidence: Optional[float]
    sentiment: Optional[str]
    keywords: List[str]

    class Config:
        from_attributes = True


class TranscriptionResponse(BaseModel):
    """Schema for transcription response."""
    id: UUID
    tenant_id: UUID
    recording_id: UUID
    status: str
    provider: str
    text: Optional[str]
    text_formatted: Optional[str]
    word_count: Optional[int]
    segment_count: Optional[int]
    confidence_score: Optional[float]
    language: str
    detected_language: Optional[str]
    speaker_count: Optional[int]
    speakers: List[Dict]
    duration_seconds: Optional[float]
    words_per_minute: Optional[float]
    processing_time_ms: Optional[int]
    has_corrections: bool
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============== Voice Command Schemas ==============

class CommandDefinitionCreate(BaseModel):
    """Schema for creating command definition."""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    category: str = Field(default="custom")
    phrases: List[str] = Field(..., min_items=1)
    synonyms: Dict[str, List[str]] = Field(default_factory=dict)
    parameters: List[Dict] = Field(default_factory=list)
    action_type: str
    action_config: Dict[str, Any]
    success_response: Optional[str] = None
    error_response: Optional[str] = None
    confirmation_prompt: Optional[str] = None
    requires_confirmation: bool = False
    is_dangerous: bool = False
    min_confidence: float = Field(default=0.7, ge=0, le=1)
    priority: int = Field(default=50, ge=0, le=100)
    allowed_roles: List[str] = Field(default_factory=list)

    @validator("action_type")
    def validate_action_type(cls, v):
        valid = ["api_call", "workflow", "function", "navigate", "query", "custom"]
        if v not in valid:
            raise ValueError(f"Action type must be one of: {valid}")
        return v


class CommandDefinitionUpdate(BaseModel):
    """Schema for updating command definition."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    phrases: Optional[List[str]] = None
    synonyms: Optional[Dict[str, List[str]]] = None
    parameters: Optional[List[Dict]] = None
    action_config: Optional[Dict[str, Any]] = None
    success_response: Optional[str] = None
    error_response: Optional[str] = None
    requires_confirmation: Optional[bool] = None
    min_confidence: Optional[float] = Field(None, ge=0, le=1)
    priority: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class CommandDefinitionResponse(BaseModel):
    """Schema for command definition response."""
    id: UUID
    tenant_id: Optional[UUID]
    name: str
    code: str
    description: Optional[str]
    category: str
    phrases: List[str]
    parameters: List[Dict]
    action_type: str
    requires_confirmation: bool
    is_dangerous: bool
    min_confidence: float
    priority: int
    total_uses: int
    success_rate: Optional[float]
    is_active: bool
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceCommandCreate(BaseModel):
    """Schema for creating voice command."""
    raw_text: str = Field(..., min_length=1)
    recording_id: Optional[UUID] = None
    transcription_id: Optional[UUID] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    device_type: Optional[str] = None


class CommandExecuteRequest(BaseModel):
    """Schema for executing a voice command."""
    text: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    auto_confirm: bool = False


class CommandExecuteResponse(BaseModel):
    """Schema for command execution response."""
    command_id: UUID
    recognized: bool
    command_code: Optional[str]
    confidence: Optional[float]
    status: str
    requires_confirmation: bool
    confirmation_prompt: Optional[str]
    response_text: Optional[str]
    result: Optional[Dict]
    alternatives: List[Dict]
    missing_params: List[str]
    error_message: Optional[str]


class VoiceCommandResponse(BaseModel):
    """Schema for voice command response."""
    id: UUID
    tenant_id: UUID
    user_id: UUID
    raw_text: str
    command_code: Optional[str]
    confidence: Optional[float]
    status: str
    parameters: Dict
    response_text: Optional[str]
    action_result: Optional[Dict]
    execution_time_ms: Optional[int]
    requires_confirmation: bool
    confirmed: Optional[bool]
    user_feedback: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Call Analysis Schemas ==============

class AnalyzeCallRequest(BaseModel):
    """Schema for call analysis request."""
    recording_id: UUID
    transcription_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    options: Dict[str, Any] = Field(default_factory=dict)


class CallAnalysisCreate(BaseModel):
    """Schema for creating call analysis."""
    recording_id: UUID
    transcription_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    agent_name: Optional[str] = None
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None


class CallAnalysisSummary(BaseModel):
    """Schema for call analysis summary."""
    id: UUID
    recording_id: UUID
    status: str
    call_type: Optional[str]
    overall_sentiment: Optional[str]
    sentiment_score: Optional[float]
    quality_score: Optional[float]
    csat_predicted: Optional[float]
    complaint_detected: bool
    escalation_needed: bool
    resolution_status: Optional[str]
    summary: Optional[str]
    key_points: List[str]
    issues_count: int
    action_items_count: int
    analyzed_at: Optional[datetime]

    class Config:
        from_attributes = True


class CallAnalysisResponse(BaseModel):
    """Schema for full call analysis response."""
    id: UUID
    tenant_id: UUID
    recording_id: UUID
    transcription_id: Optional[UUID]
    status: str
    call_type: Optional[str]
    call_type_confidence: Optional[float]
    call_categories: List[str]
    agent_id: Optional[UUID]
    agent_name: Optional[str]
    customer_id: Optional[UUID]
    customer_name: Optional[str]
    total_duration_seconds: Optional[float]
    agent_talk_time: Optional[float]
    customer_talk_time: Optional[float]
    talk_ratio: Optional[float]
    overall_sentiment: Optional[str]
    sentiment_score: Optional[float]
    agent_sentiment: Optional[float]
    customer_sentiment: Optional[float]
    emotions_detected: Dict
    dominant_emotion: Optional[str]
    topics: List[str]
    primary_topic: Optional[str]
    keywords: List[str]
    issues_identified: List[Dict]
    complaint_detected: bool
    escalation_needed: bool
    escalation_reason: Optional[str]
    resolution_status: Optional[str]
    resolution_summary: Optional[str]
    action_items: List[Dict]
    follow_up_required: bool
    quality_score: Optional[float]
    quality_breakdown: Dict
    agent_score: Optional[float]
    agent_metrics: Dict
    csat_predicted: Optional[float]
    nps_predicted: Optional[float]
    compliance_score: Optional[float]
    compliance_issues: List[Dict]
    summary: Optional[str]
    key_points: List[str]
    recommendations: List[str]
    alerts: List[Dict]
    processing_time_ms: Optional[int]
    analyzed_at: Optional[datetime]
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
    avg_transcription_confidence: Optional[float]
    avg_call_quality_score: Optional[float]
    avg_csat_predicted: Optional[float]
    recordings_by_source: Dict[str, int]
    recordings_by_status: Dict[str, int]
    calls_by_type: Dict[str, int]
    calls_by_sentiment: Dict[str, int]
    commands_by_category: Dict[str, int]
    command_success_rate: Optional[float]
    escalation_rate: Optional[float]
    top_topics: List[Dict]
    top_commands: List[Dict]
    recent_alerts: List[Dict]
