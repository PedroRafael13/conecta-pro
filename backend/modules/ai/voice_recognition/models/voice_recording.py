"""
Voice Recording Model - Sprint 52.

Model for storing audio recordings for speech recognition.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models.base import Base


class VoiceRecordingStatusEnum(StrEnum):
    """Voice recording status."""

    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBED = "transcribed"
    ANALYZED = "analyzed"
    FAILED = "failed"
    ARCHIVED = "archived"


class VoiceRecordingSourceEnum(StrEnum):
    """Voice recording source."""

    PHONE_CALL = "phone_call"
    VOICEMAIL = "voicemail"
    MEETING = "meeting"
    DICTATION = "dictation"
    INTERCOM = "intercom"
    MOBILE_APP = "mobile_app"
    WEB_APP = "web_app"
    IVR = "ivr"
    SUPPORT_TICKET = "support_ticket"
    OTHER = "other"


class AudioFormatEnum(StrEnum):
    """Audio format types."""

    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"
    WEBM = "webm"
    AAC = "aac"
    WMA = "wma"
    AMR = "amr"
    OTHER = "other"


class VoiceRecording(Base):
    """Voice recording model for audio storage and processing."""

    __tablename__ = "ai_voice_recordings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Recording info
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(50), default=VoiceRecordingSourceEnum.OTHER.value)
    status = Column(String(30), default=VoiceRecordingStatusEnum.PENDING.value, index=True)

    # File info
    file_path = Column(String(500), nullable=True)
    file_url = Column(String(1000), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    audio_format = Column(String(20), default=AudioFormatEnum.WAV.value)
    mime_type = Column(String(100), nullable=True)
    checksum = Column(String(64), nullable=True)

    # Audio properties
    duration_seconds = Column(Float, nullable=True)
    sample_rate = Column(Integer, nullable=True)  # Hz
    channels = Column(Integer, default=1)  # 1=mono, 2=stereo
    bit_depth = Column(Integer, nullable=True)  # 8, 16, 24, 32
    bitrate = Column(Integer, nullable=True)  # kbps

    # Language
    language = Column(String(10), default="pt-BR")
    detected_language = Column(String(10), nullable=True)
    language_confidence = Column(Float, nullable=True)

    # Speakers
    speaker_count = Column(Integer, nullable=True)
    speakers = Column(JSONB, default=list)  # [{id, name, segments}]

    # Audio quality
    quality_score = Column(Float, nullable=True)  # 0-1
    noise_level = Column(Float, nullable=True)  # dB
    signal_to_noise = Column(Float, nullable=True)  # dB
    quality_issues = Column(ARRAY(String), default=list)

    # Call info (if phone call)
    caller_phone = Column(String(20), nullable=True)
    callee_phone = Column(String(20), nullable=True)
    call_direction = Column(String(10), nullable=True)  # inbound, outbound
    call_start_at = Column(DateTime, nullable=True)
    call_end_at = Column(DateTime, nullable=True)

    # Related entities
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    contact_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    ticket_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    meeting_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Processing
    processed_at = Column(DateTime, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Metadata
    extra_metadata = Column(JSONB, default=dict)
    tags = Column(ARRAY(String), default=list)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid4()

    def mark_uploaded(self, file_path: str, file_size: int) -> None:
        """Mark recording as uploaded."""
        self.file_path = file_path
        self.file_size_bytes = file_size
        self.status = VoiceRecordingStatusEnum.UPLOADED.value
        self.updated_at = datetime.utcnow()

    def mark_processing(self) -> None:
        """Mark recording as being processed."""
        self.status = VoiceRecordingStatusEnum.PROCESSING.value
        self.updated_at = datetime.utcnow()

    def mark_transcribed(self, processing_time_ms: int) -> None:
        """Mark recording as transcribed."""
        self.status = VoiceRecordingStatusEnum.TRANSCRIBED.value
        self.processed_at = datetime.utcnow()
        self.processing_time_ms = processing_time_ms
        self.updated_at = datetime.utcnow()

    def mark_analyzed(self) -> None:
        """Mark recording as fully analyzed."""
        self.status = VoiceRecordingStatusEnum.ANALYZED.value
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark recording as failed."""
        self.status = VoiceRecordingStatusEnum.FAILED.value
        self.error_message = error
        self.retry_count += 1
        self.updated_at = datetime.utcnow()

    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if recording can be retried."""
        return self.retry_count < max_retries

    def get_audio_info(self) -> dict[str, Any]:
        """Get audio technical info."""
        return {
            "format": self.audio_format,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "bitrate": self.bitrate,
            "file_size_bytes": self.file_size_bytes,
        }

    def get_quality_info(self) -> dict[str, Any]:
        """Get audio quality info."""
        return {
            "quality_score": self.quality_score,
            "noise_level": self.noise_level,
            "signal_to_noise": self.signal_to_noise,
            "issues": self.quality_issues or [],
        }

    def __repr__(self) -> str:
        return f"<VoiceRecording {self.id} source={self.source} status={self.status}>"
