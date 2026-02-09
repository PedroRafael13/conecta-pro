"""
AI Voice Recognition Schemas - Sprint 52.
"""

from modules.ai.voice_recognition.schemas.voice_schemas import (
    AnalyzeCallRequest,
    # Call Analysis
    CallAnalysisCreate,
    CallAnalysisResponse,
    CallAnalysisSummary,
    # Voice Command
    CommandDefinitionCreate,
    CommandDefinitionResponse,
    CommandDefinitionUpdate,
    CommandExecuteRequest,
    CommandExecuteResponse,
    TranscribeRequest,
    # Transcription
    TranscriptionCreate,
    TranscriptionResponse,
    TranscriptionSegmentResponse,
    VoiceCommandCreate,
    VoiceCommandResponse,
    # Dashboard
    VoiceRecognitionDashboard,
    # Voice Recording
    VoiceRecordingCreate,
    VoiceRecordingResponse,
    VoiceRecordingUpdate,
    VoiceRecordingUpload,
)

__all__ = [
    # Voice Recording
    "VoiceRecordingCreate",
    "VoiceRecordingUpdate",
    "VoiceRecordingResponse",
    "VoiceRecordingUpload",
    # Transcription
    "TranscriptionCreate",
    "TranscriptionResponse",
    "TranscriptionSegmentResponse",
    "TranscribeRequest",
    # Voice Command
    "CommandDefinitionCreate",
    "CommandDefinitionUpdate",
    "CommandDefinitionResponse",
    "VoiceCommandCreate",
    "VoiceCommandResponse",
    "CommandExecuteRequest",
    "CommandExecuteResponse",
    # Call Analysis
    "CallAnalysisCreate",
    "CallAnalysisResponse",
    "CallAnalysisSummary",
    "AnalyzeCallRequest",
    # Dashboard
    "VoiceRecognitionDashboard",
]
