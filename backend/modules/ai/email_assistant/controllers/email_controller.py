"""
Email Controller - Sprint 54.

Endpoints REST para o assistente de email com IA.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import logging

from core.database import get_async_session
from core.auth.dependencies import CurrentActiveUser

from modules.ai.email_assistant.schemas import (
    EmailCreate,
    EmailUpdate,
    EmailResponse,
    EmailListResponse,
    EmailClassificationResult,
    EmailAnalysisRequest,
    EmailResponseCreate,
    EmailResponseOut,
    GenerateReplyRequest,
    GenerateReplyResponse,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    EmailRuleCreate,
    EmailRuleUpdate,
    EmailRuleResponse,
    EmailAssistantDashboard,
    EmailStatusEnum,
    EmailCategoryEnum,
    EmailPriorityEnum,
)
from modules.ai.email_assistant.repositories import EmailRepository
from modules.ai.email_assistant.services import EmailClassifier, EmailResponder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-assistant", tags=["AI Email Assistant"])

# Services
_classifier = EmailClassifier()
_responder = EmailResponder()


def get_repository(
    session: AsyncSession = Depends(get_async_session),
) -> EmailRepository:
    """Obtem instancia do repositorio."""
    return EmailRepository(session)


# =============================================================================
# Email Endpoints
# =============================================================================


@router.post(
    "/emails",
    response_model=EmailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar email",
)
async def create_email(
    data: EmailCreate,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cria e processa novo email."""
    try:
        # Verifica se email ja existe
        existing = await repo.get_email_by_message_id(data.message_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email com este message_id ja existe",
            )

        # Classifica o email
        classification = _classifier.classify(
            subject=data.subject,
            body=data.body_text or "",
            from_address=data.from_address,
            headers=data.headers,
        )

        # Prepara dados
        email_data = data.model_dump()
        email_data["body_preview"] = (data.body_text or "")[:500]
        email_data["has_attachments"] = len(data.attachments) > 0
        email_data["attachment_count"] = len(data.attachments)

        # Adiciona classificacao
        email_data.update({
            "status": "classified",
            "category": classification["category"],
            "category_confidence": classification["category_confidence"],
            "priority": classification["priority"],
            "priority_score": classification["priority_score"],
            "priority_factors": classification["priority_factors"],
            "sentiment": classification["sentiment"],
            "sentiment_score": classification["sentiment_score"],
            "emotions": classification["emotions"],
            "intent": classification["intent"],
            "intent_confidence": classification["intent_confidence"],
            "keywords": classification["keywords"],
            "entities": classification["entities"],
            "topics": classification["topics"],
            "action_items": classification["action_items"],
            "questions": classification["questions"],
            "is_spam": classification["is_spam"],
            "spam_score": classification["spam_score"],
            "is_phishing": classification["is_phishing"],
            "phishing_indicators": classification["phishing_indicators"],
            "security_score": classification["security_score"],
            "processing_time_ms": classification["processing_time_ms"],
            "processed_at": datetime.utcnow(),
        })

        email = await repo.create_email(email_data)
        logger.info(f"Email criado: {email.id}")
        return email

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar email",
        )


@router.get(
    "/emails",
    response_model=List[EmailListResponse],
    summary="Listar emails",
)
async def list_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[EmailStatusEnum] = None,
    category: Optional[EmailCategoryEnum] = None,
    priority: Optional[EmailPriorityEnum] = None,
    is_spam: Optional[bool] = None,
    condominio_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    search: Optional[str] = None,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista emails com filtros."""
    emails, _ = await repo.list_emails(
        skip=skip,
        limit=limit,
        status=status,
        category=category,
        priority=priority,
        is_spam=is_spam,
        condominio_id=condominio_id,
        assigned_to=assigned_to,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    return emails


@router.get(
    "/emails/{email_id}",
    response_model=EmailResponse,
    summary="Obter email",
)
async def get_email(
    email_id: UUID,
    include_responses: bool = False,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem email por ID."""
    email = await repo.get_email_by_id(email_id, include_responses)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )
    return email


@router.patch(
    "/emails/{email_id}",
    response_model=EmailResponse,
    summary="Atualizar email",
)
async def update_email(
    email_id: UUID,
    data: EmailUpdate,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Atualiza email."""
    update_data = data.model_dump(exclude_unset=True)
    email = await repo.update_email(email_id, update_data)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )
    return email


@router.post(
    "/emails/{email_id}/assign",
    response_model=EmailResponse,
    summary="Atribuir email",
)
async def assign_email(
    email_id: UUID,
    user_id: Optional[UUID] = None,
    team: Optional[str] = None,
    reason: Optional[str] = None,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Atribui email a usuario ou equipe."""
    email = await repo.assign_email(email_id, user_id, team, reason)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )
    return email


@router.post(
    "/emails/{email_id}/mark-spam",
    response_model=EmailResponse,
    summary="Marcar como spam",
)
async def mark_as_spam(
    email_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Marca email como spam."""
    email = await repo.mark_as_spam(email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )
    return email


@router.post(
    "/emails/{email_id}/mark-phishing",
    response_model=EmailResponse,
    summary="Marcar como phishing",
)
async def mark_as_phishing(
    email_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Marca email como phishing."""
    email = await repo.mark_as_phishing(email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )
    return email


@router.post(
    "/emails/{email_id}/archive",
    response_model=EmailResponse,
    summary="Arquivar email",
)
async def archive_email(
    email_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Arquiva email."""
    email = await repo.archive_email(email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )
    return email


@router.delete(
    "/emails/{email_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar email",
)
async def delete_email(
    email_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Deleta email (soft delete)."""
    success = await repo.delete_email(email_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )


# =============================================================================
# Classification Endpoints
# =============================================================================


@router.post(
    "/analyze",
    response_model=EmailClassificationResult,
    summary="Analisar email",
)
async def analyze_email(
    data: EmailAnalysisRequest,
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Analisa email sem persistir."""
    result = _classifier.classify(
        subject=data.subject,
        body=data.body,
        from_address=data.from_address,
        headers=data.headers,
    )
    return EmailClassificationResult(**result)


@router.post(
    "/emails/{email_id}/reclassify",
    response_model=EmailResponse,
    summary="Reclassificar email",
)
async def reclassify_email(
    email_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Reclassifica email existente."""
    email = await repo.get_email_by_id(email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )

    classification = _classifier.classify(
        subject=email.subject,
        body=email.body_text or "",
        from_address=email.from_address,
        headers=email.headers or {},
    )

    updated = await repo.update_email_classification(email_id, classification)
    return updated


# =============================================================================
# Response Generation Endpoints
# =============================================================================


@router.post(
    "/generate-reply",
    response_model=GenerateReplyResponse,
    summary="Gerar resposta",
)
async def generate_reply(
    data: GenerateReplyRequest,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Gera resposta automatica para email."""
    email = await repo.get_email_by_id(data.email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )

    email_data = {
        "subject": email.subject,
        "body_text": email.body_text,
        "from_address": email.from_address,
        "from_name": email.from_name,
    }

    classification = {
        "category": email.category.value if email.category else "other",
        "category_confidence": email.category_confidence,
        "intent": email.intent,
        "sentiment": email.sentiment.value if email.sentiment else "neutral",
        "action_items": email.action_items or [],
    }

    result = _responder.generate_reply(
        email_data=email_data,
        classification=classification,
        tone=data.tone,
        max_length=data.max_length,
        include_greeting=data.include_greeting,
        include_signature=data.include_signature,
        context=data.context,
    )

    return GenerateReplyResponse(**result)


@router.post(
    "/responses",
    response_model=EmailResponseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar resposta",
)
async def create_response(
    data: EmailResponseCreate,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cria resposta de email."""
    email = await repo.get_email_by_id(data.email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )

    response_data = data.model_dump()
    response = await repo.create_response(response_data)
    return response


@router.get(
    "/emails/{email_id}/responses",
    response_model=List[EmailResponseOut],
    summary="Listar respostas",
)
async def list_responses(
    email_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista respostas de um email."""
    responses = await repo.list_responses_by_email(email_id)
    return responses


@router.post(
    "/responses/{response_id}/send",
    response_model=EmailResponseOut,
    summary="Enviar resposta",
)
async def send_response(
    response_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Marca resposta como enviada."""
    response = await repo.mark_response_sent(response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resposta nao encontrada",
        )
    return response


# =============================================================================
# Template Endpoints
# =============================================================================


@router.post(
    "/templates",
    response_model=EmailTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar template",
)
async def create_template(
    data: EmailTemplateCreate,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cria template de email."""
    existing = await repo.get_template_by_code(data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Template com este codigo ja existe",
        )

    template_data = data.model_dump()
    template = await repo.create_template(template_data)
    return template


@router.get(
    "/templates",
    response_model=List[EmailTemplateResponse],
    summary="Listar templates",
)
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[EmailCategoryEnum] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista templates."""
    templates, _ = await repo.list_templates(
        skip=skip,
        limit=limit,
        category=category,
        is_active=is_active,
        search=search,
    )
    return templates


@router.get(
    "/templates/{template_id}",
    response_model=EmailTemplateResponse,
    summary="Obter template",
)
async def get_template(
    template_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem template por ID."""
    template = await repo.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado",
        )
    return template


@router.patch(
    "/templates/{template_id}",
    response_model=EmailTemplateResponse,
    summary="Atualizar template",
)
async def update_template(
    template_id: UUID,
    data: EmailTemplateUpdate,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Atualiza template."""
    update_data = data.model_dump(exclude_unset=True)
    template = await repo.update_template(template_id, update_data)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado",
        )
    return template


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar template",
)
async def delete_template(
    template_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Deleta template."""
    success = await repo.delete_template(template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado",
        )


# =============================================================================
# Rule Endpoints
# =============================================================================


@router.post(
    "/rules",
    response_model=EmailRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar regra",
)
async def create_rule(
    data: EmailRuleCreate,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cria regra de processamento."""
    rule_data = data.model_dump()
    rule = await repo.create_rule(rule_data)
    return rule


@router.get(
    "/rules",
    response_model=List[EmailRuleResponse],
    summary="Listar regras",
)
async def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    condominio_id: Optional[UUID] = None,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista regras."""
    rules, _ = await repo.list_rules(
        skip=skip,
        limit=limit,
        is_active=is_active,
        condominio_id=condominio_id,
    )
    return rules


@router.get(
    "/rules/{rule_id}",
    response_model=EmailRuleResponse,
    summary="Obter regra",
)
async def get_rule(
    rule_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem regra por ID."""
    rule = await repo.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada",
        )
    return rule


@router.patch(
    "/rules/{rule_id}",
    response_model=EmailRuleResponse,
    summary="Atualizar regra",
)
async def update_rule(
    rule_id: UUID,
    data: EmailRuleUpdate,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Atualiza regra."""
    update_data = data.model_dump(exclude_unset=True)
    rule = await repo.update_rule(rule_id, update_data)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada",
        )
    return rule


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar regra",
)
async def delete_rule(
    rule_id: UUID,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Deleta regra."""
    success = await repo.delete_rule(rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra nao encontrada",
        )


# =============================================================================
# Dashboard Endpoint
# =============================================================================


@router.get(
    "/dashboard",
    response_model=EmailAssistantDashboard,
    summary="Dashboard do assistente",
)
async def get_dashboard(
    condominio_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    repo: EmailRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem dashboard do assistente de email."""
    stats = await repo.get_email_stats(
        condominio_id=condominio_id,
        from_date=from_date,
        to_date=to_date,
    )

    trend = await repo.get_email_trend(days=30, condominio_id=condominio_id)
    top_templates = await repo.get_top_templates(limit=5)

    return EmailAssistantDashboard(
        total_emails=stats["total_emails"],
        total_processed=stats["total_processed"],
        total_unprocessed=stats["total_unprocessed"],
        total_spam=stats["total_spam"],
        total_phishing=stats["total_phishing"],
        emails_by_status=stats["emails_by_status"],
        emails_by_category=stats["emails_by_category"],
        emails_by_priority=stats["emails_by_priority"],
        avg_processing_time_ms=stats["avg_processing_time_ms"],
        avg_response_time_minutes=0.0,  # TODO: calcular
        auto_reply_rate=0.0,  # TODO: calcular
        classification_accuracy=0.0,  # TODO: calcular
        sentiment_distribution=stats["sentiment_distribution"],
        top_templates=top_templates,
        emails_trend=trend,
        response_time_trend=[],  # TODO: implementar
    )
