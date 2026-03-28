"""
Bartolo Controller - Endpoints do Assistente.

Expoe a API REST do Bartolo para integracao com o frontend.
"""

# pylint: disable=unused-argument,global-statement,invalid-name,line-too-long
# pylint: disable=redefined-outer-name

import logging
from typing import ClassVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from core.models import User
from modules.ai.bartolo.actions import ActionConfirmation, ActionExecutor
from modules.ai.bartolo.config.modules import MODULE_PROMPTS
from modules.ai.bartolo.services.bartolo_engine import BartoloEngine
from modules.ai.bartolo.services.learning_service import FeedbackType, LearningService

logger = logging.getLogger(__name__)

# Router
bartolo_router = APIRouter(prefix="/bartolo", tags=["Bartolo - Assistente Inteligente"])

# Instancias globais (em producao, usar injecao de dependencia)
_bartolo_engine: BartoloEngine | None = None
_learning_service: LearningService | None = None


def get_bartolo_engine() -> BartoloEngine:
    """Retorna instancia do BartoloEngine."""
    global _bartolo_engine
    if _bartolo_engine is None:
        _bartolo_engine = BartoloEngine()
    return _bartolo_engine


def get_learning_service() -> LearningService:
    """Retorna instancia do LearningService."""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService()
    return _learning_service


# ==========================================
# Schemas
# ==========================================


class SendMessageRequest(BaseModel):
    """Request para enviar mensagem."""

    VALID_MODULES: ClassVar[set[str]] = {
        "dashboard",
        "dp",
        "folha",
        "operacional",
        "ged",
        "rh",
        "sst",
        "financeiro",
        "comercial",
        "licitacoes",
    }

    message: str = Field(..., min_length=1, max_length=2000, description="Mensagem do usuario")
    session_id: str = Field(..., description="ID da sessao")
    module: str | None = Field(None, description="Modulo atual")
    metadata: dict | None = Field(None, description="Metadados adicionais")


class SendMessageResponse(BaseModel):
    """Response de mensagem."""

    message_id: str
    session_id: str
    response: str
    response_html: str | None = None
    intent: str | None = None
    confidence: float = 0.0
    suggestions: list = []
    actions: list = []
    wizard_response: dict | None = None
    data_results: dict | None = None
    action_preview: dict | None = None  # NOVO: Preview de ação executiva
    processing_time_ms: int = 0
    model_used: str = ""


class FeedbackRequest(BaseModel):
    """Request de feedback."""

    interaction_id: str = Field(..., description="ID da interacao")
    feedback_type: str = Field(..., description="Tipo de feedback: helpful, not_helpful, incorrect, etc")
    rating: int | None = Field(None, ge=1, le=5, description="Nota de 1 a 5")
    feedback_text: str | None = Field(None, max_length=500, description="Comentario")


class WizardStartRequest(BaseModel):
    """Request para iniciar wizard."""

    wizard_type: str = Field(..., description="Tipo do wizard")
    session_id: str = Field(..., description="ID da sessao")
    initial_data: dict | None = Field(None, description="Dados iniciais")


class WizardInputRequest(BaseModel):
    """Request de input no wizard."""

    session_id: str = Field(..., description="ID da sessao")
    user_input: str = Field(..., description="Entrada do usuario")


# ==========================================
# Endpoints - Chat Principal
# ==========================================


@bartolo_router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    engine: BartoloEngine = Depends(get_bartolo_engine),
    learning: LearningService = Depends(get_learning_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Envia mensagem para o Bartolo e recebe resposta.

    O Bartolo processa a mensagem considerando:
    - Perfil e permissoes do usuario (via JWT)
    - Modulo atual do sistema
    - Historico da conversa
    - Dados do sistema quando relevante
    """
    # Validar modulo se informado
    if request.module and request.module not in SendMessageRequest.VALID_MODULES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Modulo invalido: '{request.module}'. "
            f"Modulos permitidos: {', '.join(sorted(SendMessageRequest.VALID_MODULES))}",
        )

    try:
        # Usa o UUID do usuario autenticado via JWT
        user_id_str = str(current_user.id)

        response = await engine.process_message(
            user_id=user_id_str,
            session_id=request.session_id,
            message=request.message,
            module=request.module,
            metadata=request.metadata,
            db=db,
        )

        # Registra interacao para aprendizado
        await learning.record_interaction(
            user_id=user_id_str,
            session_id=request.session_id,
            message=request.message,
            response=response.response,
            intent=response.intent,
            module=request.module,
            processing_time_ms=response.processing_time_ms,
        )

        return SendMessageResponse(
            message_id=str(response.message_id),
            session_id=response.session_id,
            response=response.response,
            response_html=response.response_html,
            intent=response.intent,
            confidence=response.confidence,
            suggestions=response.suggestions,
            actions=response.actions,
            wizard_response=response.wizard_response,
            data_results=response.data_results,
            action_preview=response.action_preview.dict() if response.action_preview else None,  # NOVO
            processing_time_ms=response.processing_time_ms,
            model_used=response.model_used,
        )

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao processar mensagem")


@bartolo_router.post("/confirm-action", response_model=SendMessageResponse)
async def confirm_action(
    confirmation: ActionConfirmation,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirma e executa uma ação proposta pelo Bartolo.

    Após o Bartolo detectar uma ação e mostrar o preview,
    o usuário pode confirmar ou cancelar através deste endpoint.
    """
    try:
        # Sobrescreve user_id da confirmação com o usuário autenticado via JWT
        confirmation.user_id = str(current_user.id)

        action_executor = ActionExecutor(db)
        result = await action_executor.execute_action(confirmation)

        # Formatar resposta baseada no resultado
        if result.success:
            response_text = f"✅ {result.message}\n\n"
            if result.details:
                response_text += "**Detalhes:**\n"
                for key, value in result.details.items():
                    # Formatar key de snake_case para Title Case
                    key_formatted = key.replace("_", " ").title()
                    response_text += f"- **{key_formatted}:** {value}\n"
        else:
            response_text = f"❌ {result.message}\n\n"
            if result.error_message:
                response_text += f"**Erro:** {result.error_message}\n"

        return SendMessageResponse(
            message_id=result.action_id,
            session_id=confirmation.action_id,
            response=response_text,
            processing_time_ms=int(result.duration_seconds * 1000) if result.duration_seconds else 0,
            model_used="action_executor",
        )

    except ValueError as e:
        logger.error(f"Erro de validação ao confirmar ação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao confirmar ação: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao executar ação")


@bartolo_router.post("/send/stream")
async def send_message_stream(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Envia mensagem com resposta em streaming.

    Retorna a resposta progressivamente enquanto e gerada.
    Util para respostas longas.
    """
    user_id_str = str(current_user.id)

    async def generate():
        async for chunk in engine.process_message_stream(
            user_id=user_id_str,
            session_id=request.session_id,
            message=request.message,
            module=request.module,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@bartolo_router.get("/greeting")
async def get_greeting(
    session_id: str = Query("default", description="ID da sessao"),
    current_user: User = Depends(get_current_user),
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Retorna saudacao personalizada do Bartolo.

    Usa nome real do usuario do JWT (nao UUID).
    """
    # Usar nome real do JWT em vez de depender do profile_service
    user_name = getattr(current_user, "name", "") or getattr(current_user, "full_name", "")
    if not user_name:
        user_name = getattr(current_user, "email", "").split("@")[0]
    primeiro_nome = user_name.split()[0] if user_name else "Jordan"

    from modules.ai.bartolo.config.identity import get_greeting as _get_greeting

    greeting = _get_greeting(primeiro_nome, True)
    return {"greeting": greeting}


# ==========================================
# Endpoints - Feedback
# ==========================================


@bartolo_router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    learning: LearningService = Depends(get_learning_service),
):
    """
    Registra feedback sobre uma resposta do Bartolo.

    O feedback e usado para melhorar respostas futuras.
    """
    try:
        feedback_type = FeedbackType(request.feedback_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de feedback invalido. Use: {[f.value for f in FeedbackType]}",
        )

    success = await learning.record_feedback(
        interaction_id=UUID(request.interaction_id),
        feedback_type=feedback_type,
        rating=request.rating,
        feedback_text=request.feedback_text,
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interacao nao encontrada")

    return {"success": True, "message": "Feedback registrado com sucesso"}


# ==========================================
# Endpoints - Wizards
# ==========================================


@bartolo_router.get("/wizards")
async def list_wizards(
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Lista wizards disponiveis.

    Wizards sao assistentes guiados para tarefas complexas.
    """
    wizards = await engine.get_available_wizards()
    return {"wizards": wizards}


@bartolo_router.post("/wizard/start")
async def start_wizard(
    request: WizardStartRequest,
    current_user: User = Depends(get_current_user),
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Inicia um wizard de assistencia guiada.

    Wizards disponiveis:
    - proposta_comercial: Monta proposta comercial passo a passo
    - admissao_funcionario: Guia processo de admissao
    """
    user_id_str = str(current_user.id)
    response = engine.wizard_manager.start_wizard(
        wizard_type=request.wizard_type,
        user_id=user_id_str,
        session_id=request.session_id,
        initial_data=request.initial_data,
    )

    return {
        "wizard_id": str(response.wizard_id),
        "step_id": response.step_id,
        "step_number": response.step_number,
        "total_steps": response.total_steps,
        "state": response.state.value,
        "message": response.message,
        "question": response.question,
        "options": response.options,
        "help_text": response.help_text,
        "progress_percent": response.progress_percent,
    }


@bartolo_router.post("/wizard/input")
async def wizard_input(
    request: WizardInputRequest,
    current_user: User = Depends(get_current_user),
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Processa entrada do usuario no wizard ativo.
    """
    user_id_str = str(current_user.id)
    response = engine.wizard_manager.process_input(
        user_id=user_id_str,
        session_id=request.session_id,
        user_input=request.user_input,
    )

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum wizard ativo para esta sessao")

    return {
        "wizard_id": str(response.wizard_id),
        "step_id": response.step_id,
        "step_number": response.step_number,
        "total_steps": response.total_steps,
        "state": response.state.value,
        "message": response.message,
        "question": response.question,
        "options": response.options,
        "help_text": response.help_text,
        "collected_data": response.collected_data,
        "progress_percent": response.progress_percent,
        "can_go_back": response.can_go_back,
    }


@bartolo_router.get("/wizard/status")
async def wizard_status(
    session_id: str = Query(..., description="ID da sessao"),
    current_user: User = Depends(get_current_user),
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Retorna status do wizard ativo.
    """
    user_id_str = str(current_user.id)
    status = engine.wizard_manager.get_wizard_status(user_id_str, session_id)

    if not status:
        return {"active": False}

    return {"active": True, **status}


@bartolo_router.post("/wizard/cancel")
async def cancel_wizard(
    session_id: str = Query(..., description="ID da sessao"),
    current_user: User = Depends(get_current_user),
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Cancela wizard ativo.
    """
    user_id_str = str(current_user.id)
    response = engine.wizard_manager.cancel_wizard(user_id_str, session_id)

    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum wizard ativo")

    return {"success": True, "message": response.message}


# ==========================================
# Endpoints - Modulos
# ==========================================


@bartolo_router.get("/modules")
async def list_modules(
    engine: BartoloEngine = Depends(get_bartolo_engine),
):
    """
    Lista modulos disponiveis com suas capacidades.
    """
    modules = await engine.get_available_modules()
    return {"modules": modules, "total": len(modules)}


@bartolo_router.get("/modules/{module_id}")
async def get_module_info(module_id: str):
    """
    Retorna informacoes detalhadas de um modulo.
    """
    if module_id not in MODULE_PROMPTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Modulo '{module_id}' nao encontrado")

    config = MODULE_PROMPTS[module_id]
    return {
        "id": module_id,
        "name": config.get("name"),
        "description": config.get("description"),
        "category": config.get("category", "").value if config.get("category") else None,
        "capabilities": config.get("capabilities", []),
        "wizards": config.get("wizards", []),
    }


# ==========================================
# Endpoints - Estatisticas
# ==========================================


@bartolo_router.get("/stats")
async def get_stats(
    engine: BartoloEngine = Depends(get_bartolo_engine),
    learning: LearningService = Depends(get_learning_service),
):
    """
    Retorna estatisticas do Bartolo.
    """
    engine_stats = engine.get_stats()
    learning_stats = learning.get_stats()

    return {
        "bartolo": engine_stats,
        "learning": learning_stats,
    }


@bartolo_router.get("/health")
async def health_check():
    """
    Health check do Bartolo.
    """
    return {
        "status": "healthy",
        "name": "Bartolo",
        "version": "1.0",
        "message": "Ola! Sou o Bartolo, o assistente inteligente do Conecta PRO. Estou pronto para ajudar!",
    }


# ==========================================
# Endpoints - Aprendizado
# ==========================================


@bartolo_router.get("/learning/stats")
async def get_learning_stats(
    current_user: User = Depends(get_current_user),
    learning: LearningService = Depends(get_learning_service),
):
    """
    Retorna estatisticas de aprendizado.
    """
    return learning.get_stats()


@bartolo_router.get("/learning/patterns")
async def get_learned_patterns(
    current_user: User = Depends(get_current_user),
    pattern_type: str | None = Query(None, description="Filtrar por tipo"),
    min_usage: int = Query(3, description="Uso minimo"),
    min_success_rate: float = Query(0.7, description="Taxa de sucesso minima"),
    learning: LearningService = Depends(get_learning_service),
):
    """
    Retorna padroes aprendidos.
    """
    patterns = await learning.get_successful_patterns(
        pattern_type=pattern_type,
        min_usage=min_usage,
        min_success_rate=min_success_rate,
    )

    return {
        "patterns": [
            {
                "id": str(p.id),
                "type": p.pattern_type,
                "trigger": p.trigger,
                "usage_count": p.usage_count,
                "success_rate": round(p.success_rate * 100, 1),
            }
            for p in patterns
        ],
        "total": len(patterns),
    }
