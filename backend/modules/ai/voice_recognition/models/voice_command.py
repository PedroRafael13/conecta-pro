"""
Voice Command Model - Sprint 52.

Models for voice command recognition and execution.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models.base import Base


class VoiceCommandStatusEnum(StrEnum):
    """Voice command execution status."""

    PENDING = "pending"
    RECOGNIZED = "recognized"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    AMBIGUOUS = "ambiguous"


class CommandCategoryEnum(StrEnum):
    """Voice command category."""

    NAVIGATION = "navigation"
    SEARCH = "search"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    REPORT = "report"
    NOTIFICATION = "notification"
    SETTINGS = "settings"
    HELP = "help"
    SYSTEM = "system"
    CUSTOM = "custom"


class CommandDefinition(Base):
    """Command definition for voice command registry."""

    __tablename__ = "ai_command_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Null = global

    # Command info
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(30), default=CommandCategoryEnum.CUSTOM.value)

    # Recognition patterns
    phrases = Column(ARRAY(String), nullable=False)  # Trigger phrases
    synonyms = Column(JSONB, default=dict)  # Word synonyms
    regex_patterns = Column(ARRAY(String), default=list)

    # Parameters
    parameters = Column(JSONB, default=list)  # [{name, type, required, prompt}]
    required_params = Column(ARRAY(String), default=list)
    optional_params = Column(ARRAY(String), default=list)

    # Action
    action_type = Column(String(50), nullable=False)  # api_call, workflow, function
    action_config = Column(JSONB, nullable=False)  # {endpoint, method, params}

    # Response templates
    success_response = Column(Text, nullable=True)
    error_response = Column(Text, nullable=True)
    confirmation_prompt = Column(Text, nullable=True)

    # Settings
    requires_confirmation = Column(Boolean, default=False)
    is_dangerous = Column(Boolean, default=False)
    min_confidence = Column(Float, default=0.7)
    priority = Column(Integer, default=50)  # Higher = checked first

    # Permissions
    allowed_roles = Column(ARRAY(String), default=list)
    denied_roles = Column(ARRAY(String), default=list)

    # Stats
    total_uses = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    avg_confidence = Column(Float, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Built-in commands

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid4()

    def matches_phrase(self, text: str) -> tuple[bool, float]:
        """Check if text matches any command phrase."""
        text_lower = text.lower().strip()

        for phrase in self.phrases:
            phrase_lower = phrase.lower().strip()
            if phrase_lower in text_lower or text_lower in phrase_lower:
                # Calculate similarity
                from difflib import SequenceMatcher

                similarity = SequenceMatcher(None, text_lower, phrase_lower).ratio()
                return True, similarity

        return False, 0.0

    def record_use(self, success: bool, confidence: float) -> None:
        """Record command usage."""
        self.total_uses += 1
        if self.avg_confidence:
            self.avg_confidence = (self.avg_confidence + confidence) / 2
        else:
            self.avg_confidence = confidence

        if self.success_rate is None:
            self.success_rate = 1.0 if success else 0.0
        else:
            # Moving average
            self.success_rate = (self.success_rate * 0.9) + (0.1 if success else 0.0)

        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<CommandDefinition {self.code} category={self.category}>"


class VoiceCommand(Base):
    """Voice command execution log."""

    __tablename__ = "ai_voice_commands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Source
    recording_id = Column(UUID(as_uuid=True), ForeignKey("ai_voice_recordings.id"), nullable=True)
    transcription_id = Column(UUID(as_uuid=True), ForeignKey("ai_transcriptions.id"), nullable=True)

    # Input
    raw_text = Column(Text, nullable=False)  # Original spoken text
    normalized_text = Column(Text, nullable=True)  # Cleaned text

    # Recognition
    command_id = Column(UUID(as_uuid=True), ForeignKey("ai_command_definitions.id"), nullable=True)
    command_code = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    alternatives = Column(JSONB, default=list)  # Other possible commands

    # Parameters extracted
    parameters = Column(JSONB, default=dict)
    missing_params = Column(ARRAY(String), default=list)

    # Status
    status = Column(String(30), default=VoiceCommandStatusEnum.PENDING.value, index=True)

    # Execution
    executed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    action_result = Column(JSONB, nullable=True)
    response_text = Column(Text, nullable=True)  # Spoken response

    # Errors
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)

    # Confirmation
    requires_confirmation = Column(Boolean, default=False)
    confirmed = Column(Boolean, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    # Context
    session_id = Column(String(100), nullable=True)
    context = Column(JSONB, default=dict)  # Current app context

    # Feedback
    user_feedback = Column(String(20), nullable=True)  # correct, incorrect, partial
    feedback_text = Column(Text, nullable=True)

    # Metadata
    device_type = Column(String(50), nullable=True)
    app_version = Column(String(20), nullable=True)
    extra_metadata = Column(JSONB, default=dict)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid4()

    def set_recognized(
        self,
        command_id: str,
        command_code: str,
        confidence: float,
        parameters: dict[str, Any],
    ) -> None:
        """Set command as recognized."""
        self.command_id = command_id
        self.command_code = command_code
        self.confidence = confidence
        self.parameters = parameters
        self.status = VoiceCommandStatusEnum.RECOGNIZED.value
        self.updated_at = datetime.utcnow()

    def set_executing(self) -> None:
        """Set command as executing."""
        self.status = VoiceCommandStatusEnum.EXECUTING.value
        self.updated_at = datetime.utcnow()

    def set_completed(self, result: dict, response: str, execution_time_ms: int) -> None:
        """Set command as completed."""
        self.status = VoiceCommandStatusEnum.COMPLETED.value
        self.action_result = result
        self.response_text = response
        self.execution_time_ms = execution_time_ms
        self.executed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def set_failed(self, error: str, error_code: str | None = None) -> None:
        """Set command as failed."""
        self.status = VoiceCommandStatusEnum.FAILED.value
        self.error_message = error
        self.error_code = error_code
        self.updated_at = datetime.utcnow()

    def set_ambiguous(self, alternatives: list[dict]) -> None:
        """Set command as ambiguous with alternatives."""
        self.status = VoiceCommandStatusEnum.AMBIGUOUS.value
        self.alternatives = alternatives
        self.updated_at = datetime.utcnow()

    def confirm(self) -> None:
        """Confirm command execution."""
        self.confirmed = True
        self.confirmed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel command."""
        self.status = VoiceCommandStatusEnum.CANCELLED.value
        self.confirmed = False
        self.updated_at = datetime.utcnow()

    def add_feedback(self, feedback: str, text: str | None = None) -> None:
        """Add user feedback."""
        self.user_feedback = feedback
        self.feedback_text = text
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<VoiceCommand {self.id} code={self.command_code} status={self.status}>"
