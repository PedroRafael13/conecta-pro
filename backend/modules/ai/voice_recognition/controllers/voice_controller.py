"""
Voice Recognition Controller - Sprint 52.

REST API endpoints for voice recognition.
"""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from core.database.session import get_db
from core.auth.dependencies import get_current_user, CurrentActiveUser
from modules.ai.voice_recognition.schemas import (
    VoiceRecordingCreate,
    VoiceRecordingUpdate,
    VoiceRecordingResponse,
    VoiceRecordingUpload,
    TranscriptionCreate,
    TranscriptionResponse,
    TranscribeRequest,
    CommandDefinitionCreate,
    CommandDefinitionUpdate,
    CommandDefinitionResponse,
    VoiceCommandCreate,
    VoiceCommandResponse,
    CommandExecuteRequest,
    CommandExecuteResponse,
    CallAnalysisCreate,
    CallAnalysisResponse,
    CallAnalysisSummary,
    AnalyzeCallRequest,
    VoiceRecognitionDashboard,
)
from modules.ai.voice_recognition.repositories import VoiceRecognitionRepository
from modules.ai.voice_recognition.services import (
    SpeechRecognizer,
    VoiceCommandProcessor,
    CallAnalyzer,
)

voice_router = APIRouter(prefix="/voice", tags=["Voice Recognition"])


# ============== Voice Recording Endpoints ==============

@voice_router.post("/recordings", response_model=VoiceRecordingResponse, status_code=status.HTTP_201_CREATED)
async def create_recording(
    data: VoiceRecordingCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Create a new voice recording record."""
    repo = VoiceRecognitionRepository(db)
    recording_data = data.model_dump()
    recording_data["tenant_id"] = current_user.tenant_id
    recording_data["created_by"] = current_user.id
    recording = repo.create_recording(recording_data)
    return recording


@voice_router.get("/recordings", response_model=List[VoiceRecordingResponse])
async def list_recordings(
    source: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentActiveUser = None,
    db: Session = Depends(get_db),
):
    """List voice recordings."""
    repo = VoiceRecognitionRepository(db)
    recordings, _ = repo.get_recordings(
        tenant_id=current_user.tenant_id,
        source=source,
        status=status,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return recordings


@voice_router.get("/recordings/{recording_id}", response_model=VoiceRecordingResponse)
async def get_recording(
    recording_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Get a voice recording by ID."""
    repo = VoiceRecognitionRepository(db)
    recording = repo.get_recording(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@voice_router.patch("/recordings/{recording_id}", response_model=VoiceRecordingResponse)
async def update_recording(
    recording_id: UUID,
    data: VoiceRecordingUpdate,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Update a voice recording."""
    repo = VoiceRecognitionRepository(db)
    recording = repo.update_recording(recording_id, data.model_dump(exclude_unset=True))
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@voice_router.delete("/recordings/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recording(
    recording_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Delete a voice recording."""
    repo = VoiceRecognitionRepository(db)
    if not repo.delete_recording(recording_id):
        raise HTTPException(status_code=404, detail="Recording not found")


# ============== Transcription Endpoints ==============

@voice_router.post("/transcriptions", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_transcription(
    data: TranscriptionCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Create a transcription record."""
    repo = VoiceRecognitionRepository(db)
    transcription_data = data.model_dump()
    transcription_data["tenant_id"] = current_user.tenant_id
    transcription = repo.create_transcription(transcription_data)
    return transcription


@voice_router.post("/transcriptions/transcribe", response_model=TranscriptionResponse)
async def transcribe_recording(
    request: TranscribeRequest,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Transcribe a voice recording."""
    repo = VoiceRecognitionRepository(db)

    # Get recording
    recording = repo.get_recording(request.recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Create transcription record
    transcription = repo.create_transcription({
        "tenant_id": current_user.tenant_id,
        "recording_id": request.recording_id,
        "provider": request.provider,
        "language": request.language,
        "speaker_labels": request.enable_speaker_labels,
    })

    # Simulate transcription (in production, use actual audio data)
    recognizer = SpeechRecognizer(default_provider=request.provider)
    result = recognizer.transcribe(
        audio_data=b"sample_audio",  # Would use actual audio file
        language=request.language,
        provider=request.provider,
        enable_speaker_labels=request.enable_speaker_labels,
        enable_punctuation=request.enable_punctuation,
        options=request.options,
    )

    # Update transcription with results
    transcription = repo.update_transcription(transcription.id, {
        "status": result["status"],
        "text": result["text"],
        "text_formatted": result["text_formatted"],
        "words": result["words"],
        "segments": result["segments"],
        "word_count": result["word_count"],
        "confidence_score": result["confidence_score"],
        "detected_language": result["detected_language"],
        "speaker_count": result["speaker_count"],
        "speakers": result["speakers"],
        "duration_seconds": result["duration_seconds"],
        "processing_time_ms": result["processing_time_ms"],
    })

    # Update recording status
    repo.update_recording(request.recording_id, {
        "status": "transcribed",
        "duration_seconds": result["duration_seconds"],
    })

    return transcription


@voice_router.get("/transcriptions", response_model=List[TranscriptionResponse])
async def list_transcriptions(
    status: Optional[str] = None,
    provider: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentActiveUser = None,
    db: Session = Depends(get_db),
):
    """List transcriptions."""
    repo = VoiceRecognitionRepository(db)
    transcriptions, _ = repo.get_transcriptions(
        tenant_id=current_user.tenant_id,
        status=status,
        provider=provider,
        skip=skip,
        limit=limit,
    )
    return transcriptions


@voice_router.get("/transcriptions/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription(
    transcription_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Get a transcription by ID."""
    repo = VoiceRecognitionRepository(db)
    transcription = repo.get_transcription(transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return transcription


@voice_router.get("/recordings/{recording_id}/transcription", response_model=TranscriptionResponse)
async def get_recording_transcription(
    recording_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Get transcription for a recording."""
    repo = VoiceRecognitionRepository(db)
    transcription = repo.get_transcription_by_recording(recording_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return transcription


# ============== Voice Command Endpoints ==============

@voice_router.post("/commands/definitions", response_model=CommandDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_command_definition(
    data: CommandDefinitionCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Create a command definition."""
    repo = VoiceRecognitionRepository(db)

    # Check if code already exists
    existing = repo.get_command_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="Command code already exists")

    definition_data = data.model_dump()
    definition_data["tenant_id"] = current_user.tenant_id
    definition_data["created_by"] = current_user.id
    definition = repo.create_command_definition(definition_data)
    return definition


@voice_router.get("/commands/definitions", response_model=List[CommandDefinitionResponse])
async def list_command_definitions(
    category: Optional[str] = None,
    is_active: bool = True,
    current_user: CurrentActiveUser = None,
    db: Session = Depends(get_db),
):
    """List command definitions."""
    repo = VoiceRecognitionRepository(db)
    definitions = repo.get_command_definitions(
        tenant_id=current_user.tenant_id,
        category=category,
        is_active=is_active,
    )
    return definitions


@voice_router.get("/commands/definitions/{definition_id}", response_model=CommandDefinitionResponse)
async def get_command_definition(
    definition_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Get a command definition by ID."""
    repo = VoiceRecognitionRepository(db)
    definition = repo.get_command_definition(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="Command definition not found")
    return definition


@voice_router.patch("/commands/definitions/{definition_id}", response_model=CommandDefinitionResponse)
async def update_command_definition(
    definition_id: UUID,
    data: CommandDefinitionUpdate,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Update a command definition."""
    repo = VoiceRecognitionRepository(db)
    definition = repo.update_command_definition(definition_id, data.model_dump(exclude_unset=True))
    if not definition:
        raise HTTPException(status_code=404, detail="Command definition not found")
    return definition


@voice_router.post("/commands/execute", response_model=CommandExecuteResponse)
async def execute_voice_command(
    request: CommandExecuteRequest,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Execute a voice command."""
    repo = VoiceRecognitionRepository(db)
    processor = VoiceCommandProcessor()

    # Process command
    result = processor.process_command(
        text=request.text,
        context=request.context,
        user_id=current_user.id,
    )

    # Create command log
    command = repo.create_voice_command({
        "tenant_id": current_user.tenant_id,
        "user_id": current_user.id,
        "raw_text": request.text,
        "normalized_text": request.text.lower().strip(),
        "command_code": result.get("command_code"),
        "confidence": result.get("confidence"),
        "status": result.get("status"),
        "parameters": result.get("parameters", {}),
        "alternatives": result.get("alternatives", []),
        "requires_confirmation": result.get("requires_confirmation", False),
        "session_id": request.session_id,
        "context": request.context,
    })

    # Execute if ready and auto_confirm
    if result.get("status") == "ready" and (request.auto_confirm or not result.get("requires_confirmation")):
        exec_result = processor.execute_command(
            command_code=result["command_code"],
            parameters=result.get("parameters", {}),
            context=request.context,
        )

        # Update command log
        repo.update_voice_command(command.id, {
            "status": "completed" if exec_result.get("success") else "failed",
            "action_result": exec_result.get("result"),
            "response_text": exec_result.get("response_text"),
            "execution_time_ms": exec_result.get("execution_time_ms"),
            "error_message": exec_result.get("error") if not exec_result.get("success") else None,
        })

        result["result"] = exec_result.get("result")
        result["response_text"] = exec_result.get("response_text")

    return CommandExecuteResponse(
        command_id=command.id,
        recognized=result.get("recognized", False),
        command_code=result.get("command_code"),
        confidence=result.get("confidence"),
        status=result.get("status", "not_recognized"),
        requires_confirmation=result.get("requires_confirmation", False),
        confirmation_prompt=None,
        response_text=result.get("response_text"),
        result=result.get("result"),
        alternatives=result.get("alternatives", []),
        missing_params=result.get("missing_params", []),
        error_message=None,
    )


@voice_router.get("/commands", response_model=List[VoiceCommandResponse])
async def list_voice_commands(
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    command_code: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentActiveUser = None,
    db: Session = Depends(get_db),
):
    """List voice command logs."""
    repo = VoiceRecognitionRepository(db)
    commands, _ = repo.get_voice_commands(
        tenant_id=current_user.tenant_id,
        user_id=user_id,
        status=status,
        command_code=command_code,
        skip=skip,
        limit=limit,
    )
    return commands


@voice_router.post("/commands/{command_id}/feedback")
async def add_command_feedback(
    command_id: UUID,
    feedback: str,
    feedback_text: Optional[str] = None,
    current_user: CurrentActiveUser = None,
    db: Session = Depends(get_db),
):
    """Add feedback to a voice command."""
    repo = VoiceRecognitionRepository(db)
    command = repo.update_voice_command(command_id, {
        "user_feedback": feedback,
        "feedback_text": feedback_text,
    })
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return {"status": "ok", "message": "Feedback recorded"}


# ============== Call Analysis Endpoints ==============

@voice_router.post("/calls/analyze", response_model=CallAnalysisResponse)
async def analyze_call(
    request: AnalyzeCallRequest,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Analyze a phone call recording."""
    repo = VoiceRecognitionRepository(db)

    # Get recording
    recording = repo.get_recording(request.recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Get transcription if available
    transcription = None
    if request.transcription_id:
        transcription = repo.get_transcription(request.transcription_id)
    else:
        transcription = repo.get_transcription_by_recording(request.recording_id)

    if not transcription:
        raise HTTPException(status_code=400, detail="Transcription required for analysis")

    # Create analysis record
    analysis = repo.create_call_analysis({
        "tenant_id": current_user.tenant_id,
        "recording_id": request.recording_id,
        "transcription_id": transcription.id,
        "agent_id": request.agent_id,
        "customer_id": request.customer_id,
        "status": "analyzing",
    })

    # Perform analysis
    analyzer = CallAnalyzer()
    result = analyzer.analyze_call(
        transcription_text=transcription.text or "",
        segments=transcription.segments or [],
        duration_seconds=recording.duration_seconds,
        metadata=request.options,
    )

    # Update analysis with results
    analysis = repo.update_call_analysis(analysis.id, result)

    # Update recording status
    repo.update_recording(request.recording_id, {"status": "analyzed"})

    return analysis


@voice_router.get("/calls/analyses", response_model=List[CallAnalysisSummary])
async def list_call_analyses(
    status: Optional[str] = None,
    call_type: Optional[str] = None,
    sentiment: Optional[str] = None,
    escalation_needed: Optional[bool] = None,
    agent_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentActiveUser = None,
    db: Session = Depends(get_db),
):
    """List call analyses."""
    repo = VoiceRecognitionRepository(db)
    analyses, _ = repo.get_call_analyses(
        tenant_id=current_user.tenant_id,
        status=status,
        call_type=call_type,
        sentiment=sentiment,
        escalation_needed=escalation_needed,
        agent_id=agent_id,
        skip=skip,
        limit=limit,
    )

    return [
        CallAnalysisSummary(
            id=a.id,
            recording_id=a.recording_id,
            status=a.status,
            call_type=a.call_type,
            overall_sentiment=a.overall_sentiment,
            sentiment_score=a.sentiment_score,
            quality_score=a.quality_score,
            csat_predicted=a.csat_predicted,
            complaint_detected=a.complaint_detected,
            escalation_needed=a.escalation_needed,
            resolution_status=a.resolution_status,
            summary=a.summary,
            key_points=a.key_points or [],
            issues_count=len(a.issues_identified or []),
            action_items_count=len(a.action_items or []),
            analyzed_at=a.analyzed_at,
        )
        for a in analyses
    ]


@voice_router.get("/calls/analyses/{analysis_id}", response_model=CallAnalysisResponse)
async def get_call_analysis(
    analysis_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Get a call analysis by ID."""
    repo = VoiceRecognitionRepository(db)
    analysis = repo.get_call_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@voice_router.get("/recordings/{recording_id}/analysis", response_model=CallAnalysisResponse)
async def get_recording_analysis(
    recording_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Get call analysis for a recording."""
    repo = VoiceRecognitionRepository(db)
    analysis = repo.get_call_analysis_by_recording(recording_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


# ============== Dashboard ==============

@voice_router.get("/dashboard", response_model=VoiceRecognitionDashboard)
async def get_dashboard(
    current_user: CurrentActiveUser = ...,  # Required
    db: Session = Depends(get_db),
):
    """Get voice recognition dashboard statistics."""
    repo = VoiceRecognitionRepository(db)
    stats = repo.get_dashboard_stats(current_user.tenant_id)

    return VoiceRecognitionDashboard(
        total_recordings=stats["total_recordings"],
        total_transcriptions=stats["total_transcriptions"],
        total_commands=stats["total_commands"],
        total_calls_analyzed=stats["total_calls_analyzed"],
        avg_transcription_confidence=stats["avg_transcription_confidence"],
        avg_call_quality_score=stats["avg_call_quality_score"],
        avg_csat_predicted=stats["avg_csat_predicted"],
        recordings_by_source=stats["recordings_by_source"],
        recordings_by_status=stats["recordings_by_status"],
        calls_by_type=stats["calls_by_type"],
        calls_by_sentiment=stats["calls_by_sentiment"],
        commands_by_category={},
        command_success_rate=stats["command_success_rate"],
        escalation_rate=stats["escalation_rate"],
        top_topics=[],
        top_commands=[],
        recent_alerts=[],
    )


# ============== Utilities ==============

@voice_router.get("/providers")
async def list_providers(
    current_user: CurrentActiveUser = ...,  # Required
):
    """List available transcription providers."""
    recognizer = SpeechRecognizer()
    return recognizer.list_providers()


@voice_router.post("/analyze-quality")
async def analyze_audio_quality(
    current_user: CurrentActiveUser = ...,  # Required
):
    """Analyze audio quality for transcription."""
    recognizer = SpeechRecognizer()
    # In production, would use actual uploaded audio
    result = recognizer.analyze_audio_quality(b"sample_audio")
    return result
