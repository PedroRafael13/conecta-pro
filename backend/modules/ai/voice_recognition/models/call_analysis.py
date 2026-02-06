"""
Call Analysis Model - Sprint 52.

Model for analyzing phone calls and voice interactions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from core.models.base import Base


class CallAnalysisStatusEnum(str, Enum):
    """Call analysis status."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    REVIEWED = "reviewed"


class CallTypeEnum(str, Enum):
    """Type of call."""
    SUPPORT = "support"
    SALES = "sales"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    FOLLOW_UP = "follow_up"
    SCHEDULING = "scheduling"
    EMERGENCY = "emergency"
    INTERCOM = "intercom"
    IVR = "ivr"
    VOICEMAIL = "voicemail"
    INTERNAL = "internal"
    OTHER = "other"


class CallSentimentEnum(str, Enum):
    """Overall call sentiment."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"


class CallAnalysis(Base):
    """Call analysis model for phone call insights."""

    __tablename__ = "ai_call_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recording_id = Column(UUID(as_uuid=True), ForeignKey("ai_voice_recordings.id"), nullable=False, index=True)
    transcription_id = Column(UUID(as_uuid=True), ForeignKey("ai_transcriptions.id"), nullable=True)

    # Status
    status = Column(String(30), default=CallAnalysisStatusEnum.PENDING.value, index=True)

    # Call classification
    call_type = Column(String(30), nullable=True, index=True)
    call_type_confidence = Column(Float, nullable=True)
    call_categories = Column(ARRAY(String), default=list)

    # Participants
    agent_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    agent_name = Column(String(100), nullable=True)
    customer_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    customer_name = Column(String(100), nullable=True)
    participant_count = Column(Integer, default=2)

    # Duration metrics
    total_duration_seconds = Column(Float, nullable=True)
    agent_talk_time = Column(Float, nullable=True)  # seconds
    customer_talk_time = Column(Float, nullable=True)
    silence_time = Column(Float, nullable=True)
    hold_time = Column(Float, nullable=True)
    talk_ratio = Column(Float, nullable=True)  # agent/customer

    # Sentiment analysis
    overall_sentiment = Column(String(20), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    sentiment_timeline = Column(JSONB, default=list)  # [{time, sentiment, score}]
    agent_sentiment = Column(Float, nullable=True)
    customer_sentiment = Column(Float, nullable=True)

    # Emotion detection
    emotions_detected = Column(JSONB, default=dict)  # {emotion: count/score}
    dominant_emotion = Column(String(30), nullable=True)
    emotion_timeline = Column(JSONB, default=list)

    # Key topics/intents
    topics = Column(ARRAY(String), default=list)
    primary_topic = Column(String(100), nullable=True)
    intents = Column(JSONB, default=list)  # [{intent, confidence, params}]
    keywords = Column(ARRAY(String), default=list)
    entities = Column(JSONB, default=list)  # [{type, value, count}]

    # Issues and complaints
    issues_identified = Column(JSONB, default=list)  # [{issue, severity, resolved}]
    complaint_detected = Column(Boolean, default=False)
    escalation_needed = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)

    # Resolution
    resolution_status = Column(String(30), nullable=True)  # resolved, unresolved, pending
    resolution_summary = Column(Text, nullable=True)
    action_items = Column(JSONB, default=list)  # [{action, assignee, due}]
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)

    # Quality metrics
    quality_score = Column(Float, nullable=True)  # 0-100
    quality_breakdown = Column(JSONB, default=dict)  # {metric: score}

    # Agent performance
    agent_score = Column(Float, nullable=True)  # 0-100
    agent_metrics = Column(JSONB, default=dict)
    # greeting, professionalism, knowledge, empathy, resolution, closing

    # Customer satisfaction
    csat_predicted = Column(Float, nullable=True)  # 1-5
    nps_predicted = Column(Float, nullable=True)  # -100 to 100
    effort_score = Column(Float, nullable=True)  # Customer effort

    # Compliance
    compliance_score = Column(Float, nullable=True)
    compliance_issues = Column(JSONB, default=list)
    required_disclosures = Column(JSONB, default=dict)  # {disclosure: mentioned}
    pii_detected = Column(JSONB, default=list)  # Personal info detected

    # Summary
    summary = Column(Text, nullable=True)
    key_points = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)

    # Alerts generated
    alerts = Column(JSONB, default=list)  # [{type, severity, message}]

    # Processing
    processing_time_ms = Column(Integer, nullable=True)
    analyzed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Review
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    review_corrections = Column(JSONB, default=dict)

    # Metadata
    extra_metadata = Column(JSONB, default=dict)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid4()

    def set_analyzing(self) -> None:
        """Mark as analyzing."""
        self.status = CallAnalysisStatusEnum.ANALYZING.value
        self.updated_at = datetime.utcnow()

    def set_completed(self, processing_time_ms: int) -> None:
        """Mark as completed."""
        self.status = CallAnalysisStatusEnum.COMPLETED.value
        self.processing_time_ms = processing_time_ms
        self.analyzed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def set_failed(self, error: str) -> None:
        """Mark as failed."""
        self.status = CallAnalysisStatusEnum.FAILED.value
        self.error_message = error
        self.updated_at = datetime.utcnow()

    def add_issue(self, issue: str, severity: str, resolved: bool = False) -> None:
        """Add an identified issue."""
        if not self.issues_identified:
            self.issues_identified = []
        self.issues_identified.append({
            "issue": issue,
            "severity": severity,
            "resolved": resolved,
            "identified_at": datetime.utcnow().isoformat(),
        })
        self.updated_at = datetime.utcnow()

    def add_action_item(self, action: str, assignee: Optional[str] = None, due: Optional[datetime] = None) -> None:
        """Add an action item."""
        if not self.action_items:
            self.action_items = []
        self.action_items.append({
            "action": action,
            "assignee": assignee,
            "due": due.isoformat() if due else None,
            "status": "pending",
        })
        self.follow_up_required = True
        self.updated_at = datetime.utcnow()

    def add_alert(self, alert_type: str, severity: str, message: str) -> None:
        """Add an alert."""
        if not self.alerts:
            self.alerts = []
        self.alerts.append({
            "type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.updated_at = datetime.utcnow()

    def calculate_talk_ratio(self) -> None:
        """Calculate talk time ratio."""
        if self.agent_talk_time and self.customer_talk_time:
            if self.customer_talk_time > 0:
                self.talk_ratio = self.agent_talk_time / self.customer_talk_time
            else:
                self.talk_ratio = float('inf')
        self.updated_at = datetime.utcnow()

    def needs_escalation(self) -> bool:
        """Check if call needs escalation."""
        if self.escalation_needed:
            return True
        if self.complaint_detected:
            return True
        if self.sentiment_score is not None and self.sentiment_score < -0.5:
            return True
        if self.quality_score is not None and self.quality_score < 50:
            return True
        return False

    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quality metrics summary."""
        return {
            "quality_score": self.quality_score,
            "agent_score": self.agent_score,
            "csat_predicted": self.csat_predicted,
            "nps_predicted": self.nps_predicted,
            "compliance_score": self.compliance_score,
            "issues_count": len(self.issues_identified or []),
            "alerts_count": len(self.alerts or []),
        }

    def get_sentiment_summary(self) -> Dict[str, Any]:
        """Get sentiment analysis summary."""
        return {
            "overall": self.overall_sentiment,
            "score": self.sentiment_score,
            "agent": self.agent_sentiment,
            "customer": self.customer_sentiment,
            "dominant_emotion": self.dominant_emotion,
            "emotions": self.emotions_detected,
        }

    def __repr__(self) -> str:
        return f"<CallAnalysis {self.id} type={self.call_type} status={self.status}>"
