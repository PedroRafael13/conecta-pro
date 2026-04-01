"""
AI Voice Recognition Module - Sprint 52.

Sistema de reconhecimento de voz para transcrição, comandos e análise de chamadas.

Funcionalidades:
- Gravação e armazenamento de áudio
- Transcrição speech-to-text (multi-provider)
- Comandos de voz com processamento NLP
- Análise de chamadas telefônicas
- Detecção de sentimento e emoções
- Métricas de qualidade de atendimento
"""

from modules.ai.voice_recognition.controllers import voice_router
from modules.ai.voice_recognition.models import (
    AudioFormatEnum,
    CallAnalysis,
    CallAnalysisStatusEnum,
    CallSentimentEnum,
    CallTypeEnum,
    CommandCategoryEnum,
    CommandDefinition,
    Transcription,
    TranscriptionProviderEnum,
    TranscriptionSegment,
    TranscriptionStatusEnum,
    VoiceCommand,
    VoiceCommandStatusEnum,
    VoiceRecording,
    VoiceRecordingSourceEnum,
    VoiceRecordingStatusEnum,
)
from modules.ai.voice_recognition.repositories import VoiceRecognitionRepository
from modules.ai.voice_recognition.schemas import (
    AnalyzeCallRequest,
    CallAnalysisCreate,
    CallAnalysisResponse,
    CommandDefinitionCreate,
    CommandDefinitionResponse,
    CommandExecuteRequest,
    CommandExecuteResponse,
    TranscribeRequest,
    TranscriptionCreate,
    TranscriptionResponse,
    VoiceCommandCreate,
    VoiceCommandResponse,
    VoiceRecognitionDashboard,
    VoiceRecordingCreate,
    VoiceRecordingResponse,
    VoiceRecordingUpdate,
)
from modules.ai.voice_recognition.services import (
    CallAnalyzer,
    SpeechRecognizer,
    VoiceCommandProcessor,
)

__all__ = [
    # Models
    "VoiceRecording",
    "VoiceRecordingStatusEnum",
    "VoiceRecordingSourceEnum",
    "AudioFormatEnum",
    "Transcription",
    "TranscriptionSegment",
    "TranscriptionStatusEnum",
    "TranscriptionProviderEnum",
    "VoiceCommand",
    "CommandDefinition",
    "VoiceCommandStatusEnum",
    "CommandCategoryEnum",
    "CallAnalysis",
    "CallAnalysisStatusEnum",
    "CallTypeEnum",
    "CallSentimentEnum",
    # Schemas
    "VoiceRecordingCreate",
    "VoiceRecordingUpdate",
    "VoiceRecordingResponse",
    "TranscriptionCreate",
    "TranscriptionResponse",
    "TranscribeRequest",
    "CommandDefinitionCreate",
    "CommandDefinitionResponse",
    "VoiceCommandCreate",
    "VoiceCommandResponse",
    "CommandExecuteRequest",
    "CommandExecuteResponse",
    "CallAnalysisCreate",
    "CallAnalysisResponse",
    "AnalyzeCallRequest",
    "VoiceRecognitionDashboard",
    # Repository
    "VoiceRecognitionRepository",
    # Services
    "SpeechRecognizer",
    "VoiceCommandProcessor",
    "CallAnalyzer",
    # Router
    "voice_router",
]
