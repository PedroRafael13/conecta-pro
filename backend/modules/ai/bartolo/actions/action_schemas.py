"""
Schemas Pydantic para o sistema de ações executivas do Bartolo.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .action_types import ActionType, ActionCategory, ActionStatus


class ActionRequest(BaseModel):
    """Request de ação detectada na mensagem do usuário."""
    action_type: ActionType
    category: ActionCategory
    parameters: Dict[str, Any]
    detected_from_message: str
    confidence: float = Field(ge=0.0, le=1.0)
    user_id: str
    session_id: str


class ActionPreview(BaseModel):
    """Preview de uma ação para confirmação do usuário."""
    action_id: str
    action_type: ActionType
    title: str
    description: str
    affected_entities: List[Dict[str, Any]]
    changes_summary: List[str]
    warnings: List[str] = Field(default_factory=list)
    required_permission: str
    user_has_permission: bool
    parameters: Dict[str, Any]
    can_be_undone: bool
    requires_confirmation: bool = Field(default=True)


class ActionConfirmation(BaseModel):
    """Confirmação do usuário para executar uma ação."""
    action_id: str
    confirmed: bool
    user_notes: Optional[str] = None
    user_id: str
    confirmed_at: datetime


class ActionResult(BaseModel):
    """Resultado da execução de uma ação."""
    action_id: str
    action_type: ActionType
    status: ActionStatus
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    affected_entities: List[Dict[str, Any]] = Field(default_factory=list)
    audit_log_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
