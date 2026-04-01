"""
Voice Recognition Repository - Sprint 52.

Repository for voice recognition data access.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from modules.ai.voice_recognition.models import (
    CallAnalysis,
    CallAnalysisStatusEnum,
    CommandDefinition,
    Transcription,
    TranscriptionStatusEnum,
    VoiceCommand,
    VoiceCommandStatusEnum,
    VoiceRecording,
)


class VoiceRecognitionRepository:
    """Repository for voice recognition operations."""

    def __init__(self, db: Session):
        self.db = db

    # ============== Voice Recording ==============

    def create_recording(self, data: dict[str, Any]) -> VoiceRecording:
        """Create a voice recording."""
        recording = VoiceRecording(**data)
        self.db.add(recording)
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def get_recording(self, recording_id: UUID) -> VoiceRecording | None:
        """Get recording by ID."""
        return self.db.query(VoiceRecording).filter(VoiceRecording.id == recording_id).first()

    def get_recordings(
        self,
        tenant_id: UUID,
        status: str | None = None,
        source: str | None = None,
        user_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[VoiceRecording], int]:
        """Get recordings with filters."""
        query = self.db.query(VoiceRecording).filter(VoiceRecording.tenant_id == tenant_id)

        if status:
            query = query.filter(VoiceRecording.status == status)
        if source:
            query = query.filter(VoiceRecording.source == source)
        if user_id:
            query = query.filter(VoiceRecording.user_id == user_id)

        total = query.count()
        recordings = query.order_by(desc(VoiceRecording.created_at)).offset(skip).limit(limit).all()

        return recordings, total

    def update_recording(self, recording_id: UUID, data: dict[str, Any]) -> VoiceRecording | None:
        """Update recording."""
        recording = self.get_recording(recording_id)
        if recording:
            for key, value in data.items():
                if hasattr(recording, key):
                    setattr(recording, key, value)
            recording.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(recording)
        return recording

    def delete_recording(self, recording_id: UUID) -> bool:
        """Delete recording."""
        recording = self.get_recording(recording_id)
        if recording:
            self.db.delete(recording)
            self.db.commit()
            return True
        return False

    # ============== Transcription ==============

    def create_transcription(self, data: dict[str, Any]) -> Transcription:
        """Create a transcription."""
        transcription = Transcription(**data)
        self.db.add(transcription)
        self.db.commit()
        self.db.refresh(transcription)
        return transcription

    def get_transcription(self, transcription_id: UUID) -> Transcription | None:
        """Get transcription by ID."""
        return self.db.query(Transcription).filter(Transcription.id == transcription_id).first()

    def get_transcription_by_recording(self, recording_id: UUID) -> Transcription | None:
        """Get transcription for a recording."""
        return (
            self.db.query(Transcription)
            .filter(Transcription.recording_id == recording_id)
            .order_by(desc(Transcription.created_at))
            .first()
        )

    def get_transcriptions(
        self,
        tenant_id: UUID,
        status: str | None = None,
        provider: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Transcription], int]:
        """Get transcriptions with filters."""
        query = self.db.query(Transcription).filter(Transcription.tenant_id == tenant_id)

        if status:
            query = query.filter(Transcription.status == status)
        if provider:
            query = query.filter(Transcription.provider == provider)

        total = query.count()
        transcriptions = query.order_by(desc(Transcription.created_at)).offset(skip).limit(limit).all()

        return transcriptions, total

    def update_transcription(self, transcription_id: UUID, data: dict[str, Any]) -> Transcription | None:
        """Update transcription."""
        transcription = self.get_transcription(transcription_id)
        if transcription:
            for key, value in data.items():
                if hasattr(transcription, key):
                    setattr(transcription, key, value)
            transcription.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(transcription)
        return transcription

    # ============== Command Definition ==============

    def create_command_definition(self, data: dict[str, Any]) -> CommandDefinition:
        """Create a command definition."""
        definition = CommandDefinition(**data)
        self.db.add(definition)
        self.db.commit()
        self.db.refresh(definition)
        return definition

    def get_command_definition(self, definition_id: UUID) -> CommandDefinition | None:
        """Get command definition by ID."""
        return self.db.query(CommandDefinition).filter(CommandDefinition.id == definition_id).first()

    def get_command_by_code(self, code: str) -> CommandDefinition | None:
        """Get command definition by code."""
        return self.db.query(CommandDefinition).filter(CommandDefinition.code == code).first()

    def get_command_definitions(
        self,
        tenant_id: UUID | None = None,
        category: str | None = None,
        is_active: bool = True,
    ) -> list[CommandDefinition]:
        """Get command definitions."""
        query = self.db.query(CommandDefinition).filter(CommandDefinition.is_active == is_active)

        if tenant_id:
            query = query.filter(
                or_(
                    CommandDefinition.tenant_id == tenant_id,
                    CommandDefinition.tenant_id.is_(None),
                )
            )
        else:
            query = query.filter(CommandDefinition.tenant_id.is_(None))

        if category:
            query = query.filter(CommandDefinition.category == category)

        return query.order_by(desc(CommandDefinition.priority)).all()

    def update_command_definition(self, definition_id: UUID, data: dict[str, Any]) -> CommandDefinition | None:
        """Update command definition."""
        definition = self.get_command_definition(definition_id)
        if definition:
            for key, value in data.items():
                if hasattr(definition, key):
                    setattr(definition, key, value)
            definition.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(definition)
        return definition

    # ============== Voice Command ==============

    def create_voice_command(self, data: dict[str, Any]) -> VoiceCommand:
        """Create a voice command log."""
        command = VoiceCommand(**data)
        self.db.add(command)
        self.db.commit()
        self.db.refresh(command)
        return command

    def get_voice_command(self, command_id: UUID) -> VoiceCommand | None:
        """Get voice command by ID."""
        return self.db.query(VoiceCommand).filter(VoiceCommand.id == command_id).first()

    def get_voice_commands(
        self,
        tenant_id: UUID,
        user_id: UUID | None = None,
        status: str | None = None,
        command_code: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[VoiceCommand], int]:
        """Get voice commands with filters."""
        query = self.db.query(VoiceCommand).filter(VoiceCommand.tenant_id == tenant_id)

        if user_id:
            query = query.filter(VoiceCommand.user_id == user_id)
        if status:
            query = query.filter(VoiceCommand.status == status)
        if command_code:
            query = query.filter(VoiceCommand.command_code == command_code)

        total = query.count()
        commands = query.order_by(desc(VoiceCommand.created_at)).offset(skip).limit(limit).all()

        return commands, total

    def update_voice_command(self, command_id: UUID, data: dict[str, Any]) -> VoiceCommand | None:
        """Update voice command."""
        command = self.get_voice_command(command_id)
        if command:
            for key, value in data.items():
                if hasattr(command, key):
                    setattr(command, key, value)
            command.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(command)
        return command

    # ============== Call Analysis ==============

    def create_call_analysis(self, data: dict[str, Any]) -> CallAnalysis:
        """Create a call analysis."""
        analysis = CallAnalysis(**data)
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_call_analysis(self, analysis_id: UUID) -> CallAnalysis | None:
        """Get call analysis by ID."""
        return self.db.query(CallAnalysis).filter(CallAnalysis.id == analysis_id).first()

    def get_call_analysis_by_recording(self, recording_id: UUID) -> CallAnalysis | None:
        """Get call analysis for a recording."""
        return (
            self.db.query(CallAnalysis)
            .filter(CallAnalysis.recording_id == recording_id)
            .order_by(desc(CallAnalysis.created_at))
            .first()
        )

    def get_call_analyses(
        self,
        tenant_id: UUID,
        status: str | None = None,
        call_type: str | None = None,
        sentiment: str | None = None,
        escalation_needed: bool | None = None,
        agent_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CallAnalysis], int]:
        """Get call analyses with filters."""
        query = self.db.query(CallAnalysis).filter(CallAnalysis.tenant_id == tenant_id)

        if status:
            query = query.filter(CallAnalysis.status == status)
        if call_type:
            query = query.filter(CallAnalysis.call_type == call_type)
        if sentiment:
            query = query.filter(CallAnalysis.overall_sentiment == sentiment)
        if escalation_needed is not None:
            query = query.filter(CallAnalysis.escalation_needed == escalation_needed)
        if agent_id:
            query = query.filter(CallAnalysis.agent_id == agent_id)

        total = query.count()
        analyses = query.order_by(desc(CallAnalysis.created_at)).offset(skip).limit(limit).all()

        return analyses, total

    def update_call_analysis(self, analysis_id: UUID, data: dict[str, Any]) -> CallAnalysis | None:
        """Update call analysis."""
        analysis = self.get_call_analysis(analysis_id)
        if analysis:
            for key, value in data.items():
                if hasattr(analysis, key):
                    setattr(analysis, key, value)
            analysis.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(analysis)
        return analysis

    # ============== Statistics ==============

    def get_dashboard_stats(self, tenant_id: UUID) -> dict[str, Any]:
        """Get dashboard statistics."""
        # Recordings stats
        total_recordings = (
            self.db.query(func.count(VoiceRecording.id)).filter(VoiceRecording.tenant_id == tenant_id).scalar() or 0
        )

        # Transcriptions stats
        total_transcriptions = (
            self.db.query(func.count(Transcription.id)).filter(Transcription.tenant_id == tenant_id).scalar() or 0
        )

        avg_confidence = (
            self.db.query(func.avg(Transcription.confidence_score))
            .filter(
                Transcription.tenant_id == tenant_id,
                Transcription.status == TranscriptionStatusEnum.COMPLETED.value,
            )
            .scalar()
        )

        # Commands stats
        total_commands = (
            self.db.query(func.count(VoiceCommand.id)).filter(VoiceCommand.tenant_id == tenant_id).scalar() or 0
        )

        successful_commands = (
            self.db.query(func.count(VoiceCommand.id))
            .filter(
                VoiceCommand.tenant_id == tenant_id,
                VoiceCommand.status == VoiceCommandStatusEnum.COMPLETED.value,
            )
            .scalar()
            or 0
        )

        # Call analysis stats
        total_calls = (
            self.db.query(func.count(CallAnalysis.id)).filter(CallAnalysis.tenant_id == tenant_id).scalar() or 0
        )

        avg_quality = (
            self.db.query(func.avg(CallAnalysis.quality_score))
            .filter(
                CallAnalysis.tenant_id == tenant_id,
                CallAnalysis.status == CallAnalysisStatusEnum.COMPLETED.value,
            )
            .scalar()
        )

        avg_csat = (
            self.db.query(func.avg(CallAnalysis.csat_predicted))
            .filter(
                CallAnalysis.tenant_id == tenant_id,
                CallAnalysis.status == CallAnalysisStatusEnum.COMPLETED.value,
            )
            .scalar()
        )

        escalations = (
            self.db.query(func.count(CallAnalysis.id))
            .filter(
                CallAnalysis.tenant_id == tenant_id,
                CallAnalysis.escalation_needed,
            )
            .scalar()
            or 0
        )

        # Group by stats
        recordings_by_source = dict(
            self.db.query(VoiceRecording.source, func.count(VoiceRecording.id))
            .filter(VoiceRecording.tenant_id == tenant_id)
            .group_by(VoiceRecording.source)
            .all()
        )

        recordings_by_status = dict(
            self.db.query(VoiceRecording.status, func.count(VoiceRecording.id))
            .filter(VoiceRecording.tenant_id == tenant_id)
            .group_by(VoiceRecording.status)
            .all()
        )

        calls_by_type = dict(
            self.db.query(CallAnalysis.call_type, func.count(CallAnalysis.id))
            .filter(
                CallAnalysis.tenant_id == tenant_id,
                CallAnalysis.call_type.isnot(None),
            )
            .group_by(CallAnalysis.call_type)
            .all()
        )

        calls_by_sentiment = dict(
            self.db.query(CallAnalysis.overall_sentiment, func.count(CallAnalysis.id))
            .filter(
                CallAnalysis.tenant_id == tenant_id,
                CallAnalysis.overall_sentiment.isnot(None),
            )
            .group_by(CallAnalysis.overall_sentiment)
            .all()
        )

        return {
            "total_recordings": total_recordings,
            "total_transcriptions": total_transcriptions,
            "total_commands": total_commands,
            "total_calls_analyzed": total_calls,
            "avg_transcription_confidence": round(avg_confidence, 2) if avg_confidence else None,
            "avg_call_quality_score": round(avg_quality, 1) if avg_quality else None,
            "avg_csat_predicted": round(avg_csat, 1) if avg_csat else None,
            "recordings_by_source": recordings_by_source,
            "recordings_by_status": recordings_by_status,
            "calls_by_type": calls_by_type,
            "calls_by_sentiment": calls_by_sentiment,
            "command_success_rate": round(successful_commands / total_commands * 100, 1)
            if total_commands > 0
            else None,
            "escalation_rate": round(escalations / total_calls * 100, 1) if total_calls > 0 else None,
        }
