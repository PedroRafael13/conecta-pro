"""
Transcription Model - Sprint 52.

Models for speech-to-text transcription results.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models.base import Base


class TranscriptionStatusEnum(StrEnum):
    """Transcription status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    REVIEWED = "reviewed"
    CORRECTED = "corrected"


class TranscriptionProviderEnum(StrEnum):
    """Transcription provider."""

    GOOGLE_SPEECH = "google_speech"
    AWS_TRANSCRIBE = "aws_transcribe"
    AZURE_SPEECH = "azure_speech"
    WHISPER = "whisper"
    DEEPGRAM = "deepgram"
    ASSEMBLYAI = "assemblyai"
    VOSK = "vosk"
    LOCAL = "local"


class Transcription(Base):
    """Transcription model for speech-to-text results."""

    __tablename__ = "ai_transcriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recording_id = Column(UUID(as_uuid=True), ForeignKey("ai_voice_recordings.id"), nullable=False, index=True)

    # Status
    status = Column(String(30), default=TranscriptionStatusEnum.PENDING.value, index=True)
    provider = Column(String(50), default=TranscriptionProviderEnum.WHISPER.value)

    # Transcription content
    text = Column(Text, nullable=True)  # Full text
    text_formatted = Column(Text, nullable=True)  # With punctuation/formatting
    text_cleaned = Column(Text, nullable=True)  # Normalized

    # Word-level data
    words = Column(JSONB, default=list)  # [{word, start, end, confidence}]
    word_count = Column(Integer, nullable=True)
    unique_words = Column(Integer, nullable=True)

    # Segments/paragraphs
    segments = Column(JSONB, default=list)  # [{start, end, text, speaker}]
    segment_count = Column(Integer, nullable=True)

    # Confidence
    confidence_score = Column(Float, nullable=True)  # 0-1 overall
    confidence_min = Column(Float, nullable=True)
    confidence_max = Column(Float, nullable=True)
    low_confidence_words = Column(JSONB, default=list)  # Words below threshold

    # Language
    language = Column(String(10), default="pt-BR")
    detected_language = Column(String(10), nullable=True)
    language_confidence = Column(Float, nullable=True)

    # Speaker diarization
    speaker_labels = Column(Boolean, default=False)
    speaker_count = Column(Integer, nullable=True)
    speakers = Column(JSONB, default=list)  # [{id, name, speaking_time}]

    # Timestamps
    duration_seconds = Column(Float, nullable=True)
    words_per_minute = Column(Float, nullable=True)

    # Processing info
    processing_time_ms = Column(Integer, nullable=True)
    model_version = Column(String(50), nullable=True)
    options_used = Column(JSONB, default=dict)

    # Corrections
    has_corrections = Column(Boolean, default=False)
    corrections = Column(JSONB, default=list)  # [{original, corrected, position}]
    corrected_by = Column(UUID(as_uuid=True), nullable=True)
    corrected_at = Column(DateTime, nullable=True)

    # Error info
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)

    # Metadata
    extra_metadata = Column(JSONB, default=dict)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid4()

    def set_result(
        self,
        text: str,
        confidence: float,
        words: list[dict],
        segments: list[dict],
        processing_time_ms: int,
    ) -> None:
        """Set transcription result."""
        self.text = text
        self.confidence_score = confidence
        self.words = words
        self.segments = segments
        self.word_count = len(words) if words else len(text.split())
        self.segment_count = len(segments)
        self.processing_time_ms = processing_time_ms
        self.status = TranscriptionStatusEnum.COMPLETED.value
        self.updated_at = datetime.utcnow()

        # Calculate WPM
        if self.duration_seconds and self.duration_seconds > 0:
            self.words_per_minute = (self.word_count / self.duration_seconds) * 60

    def mark_failed(self, error: str, error_code: str | None = None) -> None:
        """Mark transcription as failed."""
        self.status = TranscriptionStatusEnum.FAILED.value
        self.error_message = error
        self.error_code = error_code
        self.updated_at = datetime.utcnow()

    def add_correction(self, original: str, corrected: str, position: int) -> None:
        """Add a correction to the transcription."""
        if not self.corrections:
            self.corrections = []
        self.corrections.append(
            {
                "original": original,
                "corrected": corrected,
                "position": position,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.has_corrections = True
        self.updated_at = datetime.utcnow()

    def get_speaker_text(self, speaker_id: str) -> str:
        """Get text spoken by a specific speaker."""
        if not self.segments:
            return ""
        return " ".join(seg.get("text", "") for seg in self.segments if seg.get("speaker") == speaker_id)

    def get_segment_at_time(self, time_seconds: float) -> dict | None:
        """Get segment at a specific time."""
        if not self.segments:
            return None
        for segment in self.segments:
            if segment.get("start", 0) <= time_seconds <= segment.get("end", 0):
                return segment
        return None

    def get_quality_metrics(self) -> dict[str, Any]:
        """Get transcription quality metrics."""
        return {
            "confidence_score": self.confidence_score,
            "confidence_min": self.confidence_min,
            "confidence_max": self.confidence_max,
            "low_confidence_count": len(self.low_confidence_words or []),
            "has_corrections": self.has_corrections,
            "corrections_count": len(self.corrections or []),
        }

    def __repr__(self) -> str:
        return f"<Transcription {self.id} status={self.status} confidence={self.confidence_score}>"


class TranscriptionSegment(Base):
    """Individual transcription segment for detailed analysis."""

    __tablename__ = "ai_transcription_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    transcription_id = Column(UUID(as_uuid=True), ForeignKey("ai_transcriptions.id"), nullable=False, index=True)

    # Segment info
    segment_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

    # Timing
    start_time = Column(Float, nullable=False)  # seconds
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=True)

    # Speaker
    speaker_id = Column(String(50), nullable=True)
    speaker_name = Column(String(100), nullable=True)

    # Confidence
    confidence = Column(Float, nullable=True)

    # Words in segment
    words = Column(JSONB, default=list)
    word_count = Column(Integer, nullable=True)

    # Analysis
    sentiment = Column(String(20), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    keywords = Column(ARRAY(String), default=list)
    entities = Column(JSONB, default=list)

    # Flags
    is_question = Column(Boolean, default=False)
    is_command = Column(Boolean, default=False)
    contains_action_item = Column(Boolean, default=False)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid4()
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time

    def __repr__(self) -> str:
        return f"<TranscriptionSegment {self.id} idx={self.segment_index}>"
