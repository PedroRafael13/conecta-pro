"""
AI Voice Recognition Schemas - Sprint 52.
"""

from modules.ai.voice_recognition.schemas.voice_schemas import (
    # Voice Recording
    VoiceRecordingCreate,
    VoiceRecordingUpdate,
    VoiceRecordingResponse,
    VoiceRecordingUpload,
    # Transcription
    TranscriptionCreate,
    TranscriptionResponse,
    TranscriptionSegmentResponse,
    TranscribeRequest,
    # Voice Command
    CommandDefinitionCreate,
    CommandDefinitionUpdate,
    CommandDefinitionResponse,
    VoiceCommandCreate,
    VoiceCommandResponse,
    CommandExecuteRequest,
    CommandExecuteResponse,
    # Call Analysis
    CallAnalysisCreate,
    CallAnalysisResponse,
    CallAnalysisSummary,
    AnalyzeCallRequest,
    # Dashboard
    VoiceRecognitionDashboard,
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
