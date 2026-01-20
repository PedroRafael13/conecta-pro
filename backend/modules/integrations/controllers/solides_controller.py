"""
Controller REST para integração Sólides DP.
Sprint 33: Integration Framework

Endpoints para:
- Recebimento de webhooks do Sólides
- Configuração da integração
- Monitoramento e status
- Acionamento de sincronização
- Gerenciamento de conflitos
- Logs de sincronização
"""

import asyncio
import hashlib
import hmac
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.integrations.connectors.solides.conflict_resolver import (
    ConflictResolver,
    get_resolver_for_entity,
)
from modules.integrations.connectors.solides.connector import SolidesConnector
from modules.integrations.connectors.solides.models import (
    ConflictStatus,
    ConflictStrategy,
    SolidesEmployee,
    SolidesCredential,
    SolidesEntityMapping,
    SolidesIntegrationConfig,
    SolidesSyncConflict,
    SolidesSyncLog,
    SolidesSyncState,
    SyncStatus,
)
from modules.integrations.connectors.solides.sync_service import (
    SyncDirection,
    get_sync_service,
)
from modules.integrations.connectors.solides.tasks import (
    schedule_entity_sync,
    schedule_full_sync,
    schedule_incremental_sync,
)
from modules.integrations.connectors.solides.webhook_handler import SolidesWebhookHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/solides", tags=["Solides Integration"])


# ==================== FUNÇÕES UTILITÁRIAS ====================


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Valida assinatura HMAC SHA256 do webhook.

    Args:
        payload: Body raw da requisição em bytes
        signature: Assinatura recebida no header
        secret: Secret configurado para validação

    Returns:
        True se a assinatura for válida, False caso contrário

    Note:
        Usa hmac.compare_digest para prevenir timing attacks.
        Suporta assinaturas com ou sem prefixo 'sha256='.
    """
    if not secret:
        logger.warning("[Solides Webhook] Secret não configurado")
        return False

    if not signature:
        logger.warning("[Solides Webhook] Assinatura não fornecida")
        return False

    # Remove prefixo sha256= se presente
    if signature.startswith("sha256="):
        signature = signature[7:]

    # Calcula HMAC SHA256
    expected = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Comparação segura contra timing attacks
    return hmac.compare_digest(expected.lower(), signature.lower())


def get_webhook_secret() -> str:
    """
    Obtém o secret do webhook da variável de ambiente.

    Returns:
        String do secret ou string vazia se não configurado.
    """
    return os.getenv("SOLIDES_WEBHOOK_SECRET", "")


# ==================== SCHEMAS ====================


class SolidesConfigRequest(BaseModel):
    """Schema para configurar integração Sólides."""

    api_token: str = Field(
        ...,
        min_length=10,
        description="Token de API do Sólides (Basic Auth base64)"
    )
    sync_direction: str = Field(
        default="solides_to_conecta",
        description="Direção da sincronização: solides_to_conecta, conecta_to_solides, bidirectional"
    )
    conflict_strategy: str = Field(
        default="most_recent",
        description="Estratégia de conflito: solides_wins, conecta_wins, most_recent, manual"
    )
    enabled_entities: List[str] = Field(
        default=["colaboradores", "departamentos", "cargos", "ocorrencias", "absenteismos"],
        description="Entidades habilitadas para sincronização"
    )
    incremental_sync_interval_minutes: int = Field(
        default=15,
        ge=5,
        le=60,
        description="Intervalo em minutos para sincronização incremental"
    )
    auto_create_departments: bool = Field(
        default=True,
        description="Criar departamentos automaticamente se não existirem"
    )
    auto_create_positions: bool = Field(
        default=True,
        description="Criar cargos automaticamente se não existirem"
    )
    webhook_enabled: bool = Field(
        default=True,
        description="Habilitar recebimento de webhooks"
    )


class SolidesConfigResponse(BaseModel):
    """Resposta com configuração atual da integração."""

    is_enabled: bool
    is_connected: bool
    sync_direction: Optional[str] = None
    conflict_strategy: Optional[str] = None
    enabled_entities: List[str] = Field(default_factory=list)
    last_health_check_at: Optional[datetime] = None
    last_health_check_status: Optional[bool] = None


class SyncTriggerRequest(BaseModel):
    """Request para disparar sincronização manual."""

    entity_types: Optional[List[str]] = Field(
        default=None,
        description="Tipos de entidade a sincronizar (None = todas habilitadas)"
    )
    full_sync: bool = Field(
        default=False,
        description="Se True, executa sincronização completa"
    )
    force: bool = Field(
        default=False,
        description="Se True, ignora verificações de intervalo mínimo"
    )


class SyncTriggerResponse(BaseModel):
    """Resposta do disparo de sincronização."""

    success: bool
    message: str
    task_id: Optional[str] = None
    sync_type: str
    entity_types: Optional[List[str]] = None


class SyncStatusResponse(BaseModel):
    """Status atual da sincronização."""

    connected: bool
    api_latency_ms: Optional[int] = None
    entities: Dict[str, Any] = Field(default_factory=dict)
    pending_conflicts: int = 0
    last_full_sync_at: Optional[datetime] = None
    last_incremental_sync_at: Optional[datetime] = None
    webhook_enabled: bool = False


class ConflictResponse(BaseModel):
    """Conflito de sincronização."""

    id: str
    entity_type: str
    entity_id: str
    solides_id: str
    status: str
    changed_fields: List[str] = Field(default_factory=list)
    detected_at: datetime
    solides_data: Dict[str, Any]
    conecta_data: Dict[str, Any]


class ConflictResolutionRequest(BaseModel):
    """Request para resolver conflito manualmente."""

    strategy: str = Field(
        ...,
        description="Estratégia: solides_wins, conecta_wins, most_recent, manual"
    )
    resolution_notes: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Notas sobre a resolução"
    )
    manual_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dados para resolução manual (quando strategy=manual)"
    )


class SyncLogResponse(BaseModel):
    """Log de sincronização."""

    id: str
    sync_type: str
    entity_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_processed: int = 0
    created_count: int = 0
    updated_count: int = 0
    error_count: int = 0


class WebhookResponse(BaseModel):
    """Resposta do endpoint de webhook."""

    status: str
    message: Optional[str] = None
    webhook_id: Optional[str] = None
    event_type: Optional[str] = None


class IntegrationStatusResponse(BaseModel):
    """Status completo da integração."""

    healthy: bool
    connected: bool
    latency_ms: Optional[int] = None
    message: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    pending_items: int = 0


class SolidesEmployeeResponse(BaseModel):
    """Schema de resposta para colaborador do Sólides."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    solides_id: str
    nome: str
    email: Optional[str] = None
    cpf: Optional[str] = None
    matricula: Optional[str] = None
    cargo_nome: Optional[str] = None
    departamento_nome: Optional[str] = None
    situacao: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    data_admissao: Optional[datetime] = None
    foto_url: Optional[str] = None


class SolidesEmployeeListResponse(BaseModel):
    """Schema para listagem paginada de colaboradores do Sólides."""

    items: List[SolidesEmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== ENDPOINT DE WEBHOOK (PÚBLICO) ====================


@router.get(
    "/employees",
    response_model=SolidesEmployeeListResponse,
    summary="Listar colaboradores sincronizados",
    description="Lista colaboradores sincronizados do Sólides com filtros e paginação.",
)
async def list_solides_employees(
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(20, ge=1, le=200, description="Itens por página"),
    search: Optional[str] = Query(None, description="Buscar por nome, email ou matricula"),
    situacao: Optional[str] = Query(None, description="Filtrar por situacao"),
    include_inactive: bool = Query(False, description="Incluir registros inativos"),
) -> SolidesEmployeeListResponse:
    """
    Lista colaboradores sincronizados do Sólides.
    """
    filters = []
    condominio_id = getattr(current_user, "condominio_id", None)
    if condominio_id:
        filters.append(SolidesEmployee.condominio_id == condominio_id)

    if not include_inactive:
        filters.append(SolidesEmployee.is_active.is_(True))

    if situacao:
        filters.append(SolidesEmployee.situacao == situacao)

    if search:
        like_term = f"%{search}%"
        filters.append(
            or_(
                SolidesEmployee.nome.ilike(like_term),
                SolidesEmployee.email.ilike(like_term),
                SolidesEmployee.matricula.ilike(like_term),
            )
        )

    total_result = await db.execute(
        select(func.count()).select_from(SolidesEmployee).where(*filters)
    )
    total = total_result.scalar_one() or 0
    total_pages = (total + page_size - 1) // page_size

    items_result = await db.execute(
        select(SolidesEmployee)
        .where(*filters)
        .order_by(SolidesEmployee.nome.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = items_result.scalars().all()

    return SolidesEmployeeListResponse(
        items=[SolidesEmployeeResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Receber webhook do Sólides",
    description="""
    Endpoint para receber webhooks do Sólides DP.

    **Eventos suportados:**
    - `novo_colaborador` / `employee.created`: Novo colaborador cadastrado
    - `edicao_colaborador` / `employee.updated`: Colaborador atualizado
    - `demissao_colaborador` / `employee.terminated`: Colaborador demitido
    - `nova_ocorrencia`: Nova ocorrência registrada
    - `novo_absenteismo`: Novo absenteísmo registrado
    - `nova_resposta_pesquisa`: Resposta em pesquisa
    - `novo_curriculo`: Novo currículo recebido
    - `nova_inscricao`: Nova inscrição em vaga
    - `mudanca_etapa`: Mudança de etapa em processo seletivo

    **Validação de assinatura:**
    - Header `X-Solides-Signature` ou `X-Webhook-Signature`
    - HMAC SHA256 com secret configurado em `SOLIDES_WEBHOOK_SECRET`
    - Formato: `sha256=<hash>` ou apenas `<hash>`

    **Retorno rápido:**
    - Sempre retorna 200 OK rapidamente
    - Processamento ocorre de forma assíncrona via fila
    """,
    responses={
        200: {"description": "Webhook recebido com sucesso"},
        400: {"description": "Payload inválido"},
        401: {"description": "Assinatura inválida"},
        500: {"description": "Erro interno no processamento"},
    }
)
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_solides_signature: Optional[str] = Header(
        default=None,
        alias="X-Solides-Signature",
        description="Assinatura HMAC SHA256 do payload"
    ),
    x_webhook_signature: Optional[str] = Header(
        default=None,
        alias="X-Webhook-Signature",
        description="Assinatura alternativa HMAC SHA256"
    ),
    x_request_id: Optional[str] = Header(
        default=None,
        alias="X-Request-ID",
        description="ID único da requisição para rastreamento"
    )
) -> WebhookResponse:
    """
    Endpoint para receber webhooks do Sólides DP.

    O processamento é feito de forma assíncrona para garantir
    resposta rápida ao Sólides (evita timeout/retry desnecessário).
    """
    # Ler body raw para validação de assinatura
    try:
        body = await request.body()
    except Exception as e:
        logger.error(f"[Solides Webhook] Erro ao ler body: {e}")
        return WebhookResponse(
            status="error",
            message="Erro ao ler requisição"
        )

    # Validar assinatura HMAC
    webhook_secret = get_webhook_secret()
    signature = x_solides_signature or x_webhook_signature

    if webhook_secret:
        if not signature:
            logger.warning(
                f"[Solides Webhook] Requisição sem assinatura "
                f"(request_id={x_request_id}, ip={request.client.host if request.client else 'unknown'})"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Assinatura do webhook não fornecida"
            )

        if not verify_webhook_signature(body, signature, webhook_secret):
            logger.warning(
                f"[Solides Webhook] Assinatura inválida "
                f"(request_id={x_request_id}, ip={request.client.host if request.client else 'unknown'})"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Assinatura do webhook inválida"
            )

        logger.debug(f"[Solides Webhook] Assinatura validada com sucesso")
    else:
        logger.warning(
            "[Solides Webhook] SOLIDES_WEBHOOK_SECRET não configurado - "
            "validação de assinatura desabilitada"
        )

    # Parse do payload JSON
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"[Solides Webhook] JSON inválido: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload JSON inválido"
        )

    # Extrair tipo de evento (suporta diferentes formatos)
    event_type = (
        payload.get("event") or
        payload.get("type") or
        payload.get("event_type") or
        "unknown"
    )

    # Headers para logging/rastreamento
    headers = {
        "X-Solides-Signature": x_solides_signature or "",
        "X-Webhook-Signature": x_webhook_signature or "",
        "X-Request-ID": x_request_id or "",
        "Content-Type": request.headers.get("Content-Type", ""),
        "User-Agent": request.headers.get("User-Agent", ""),
    }

    # IP de origem
    client_ip = None
    if request.client:
        client_ip = request.client.host
    # Verificar headers de proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()

    logger.info(
        f"[Solides Webhook] Recebido evento '{event_type}' "
        f"(request_id={x_request_id}, ip={client_ip})"
    )

    # Processar via handler
    try:
        handler = SolidesWebhookHandler(db, async_processing=True)

        result = await handler.handle_webhook(
            event_type=event_type,
            payload=payload,
            headers=headers,
            raw_body=body,
            request_id=x_request_id,
            ip_address=client_ip
        )

        return WebhookResponse(
            status=result.get("status", "received"),
            message=result.get("message"),
            webhook_id=result.get("webhook_id"),
            event_type=event_type
        )

    except Exception as e:
        logger.error(
            f"[Solides Webhook] Erro no processamento: {e}",
            exc_info=True
        )
        # Retorna 200 mesmo em erro para evitar retry do Sólides
        # O erro foi logado para investigação
        return WebhookResponse(
            status="error",
            message="Erro interno - evento será reprocessado",
            event_type=event_type
        )


# ==================== ENDPOINT DE STATUS (PÚBLICO PARA HEALTH CHECK) ====================


@router.get(
    "/status",
    response_model=SyncStatusResponse,
    summary="Status da integração Sólides",
    description="Retorna status atual da integração e última sincronização."
)
async def get_integration_status(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> SyncStatusResponse:
    """
    Retorna status atual da integração Sólides.

    Inclui:
    - Status de conexão com a API
    - Latência da API
    - Status por entidade
    - Conflitos pendentes
    - Data da última sincronização
    """
    condominio_id = current_user.condominio_id

    try:
        # Buscar configuração
        config = db.query(SolidesIntegrationConfig).filter(
            SolidesIntegrationConfig.condominio_id == condominio_id
        ).first()

        if not config or not config.is_enabled:
            return SyncStatusResponse(
                connected=False,
                api_latency_ms=None,
                entities={},
                pending_conflicts=0,
                last_full_sync_at=None,
                last_incremental_sync_at=None,
                webhook_enabled=False
            )

        # Obter status via sync_service
        sync_service = get_sync_service(db, condominio_id)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            status_data = loop.run_until_complete(sync_service.get_sync_status())
        finally:
            loop.close()

        # Buscar última sync completa
        last_full = db.query(SolidesSyncState).filter(
            SolidesSyncState.condominio_id == condominio_id,
            SolidesSyncState.last_full_sync_at.isnot(None)
        ).order_by(SolidesSyncState.last_full_sync_at.desc()).first()

        # Buscar última sync incremental
        last_incremental = db.query(SolidesSyncState).filter(
            SolidesSyncState.condominio_id == condominio_id,
            SolidesSyncState.last_sync_at.isnot(None)
        ).order_by(SolidesSyncState.last_sync_at.desc()).first()

        return SyncStatusResponse(
            connected=status_data.get("connected", False),
            api_latency_ms=status_data.get("api_latency_ms"),
            entities=status_data.get("entities", {}),
            pending_conflicts=status_data.get("pending_conflicts", 0),
            last_full_sync_at=last_full.last_full_sync_at if last_full else None,
            last_incremental_sync_at=last_incremental.last_sync_at if last_incremental else None,
            webhook_enabled=config.webhook_enabled if config else False
        )

    except Exception as e:
        logger.error(f"[Solides] Erro ao obter status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status da integração: {str(e)}"
        )


# ==================== ENDPOINTS DE SINCRONIZAÇÃO ====================


@router.post(
    "/sync/trigger",
    response_model=SyncTriggerResponse,
    summary="Disparar sincronização manual",
    description="""
    Dispara sincronização manual com o Sólides.

    **Tipos de sincronização:**
    - `full_sync=true`: Sincronização completa de todas as entidades
    - `full_sync=false`: Sincronização incremental (apenas alterações)

    **Entidades suportadas:**
    - colaboradores
    - departamentos
    - cargos
    - ocorrencias
    - absenteismos
    """
)
async def trigger_sync(
    request: SyncTriggerRequest = Body(default=SyncTriggerRequest()),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> SyncTriggerResponse:
    """
    Dispara sincronização manual com o Sólides.

    Args:
        request: Parâmetros da sincronização
        db: Sessão do banco de dados
        current_user: Usuário autenticado

    Returns:
        Resposta com ID da task agendada
    """
    condominio_id = str(current_user.condominio_id)

    # Verificar se integração está habilitada
    config = db.query(SolidesIntegrationConfig).filter(
        SolidesIntegrationConfig.condominio_id == current_user.condominio_id
    ).first()

    if not config or not config.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integração Sólides não está habilitada"
        )

    try:
        if request.full_sync:
            # Sincronização completa
            task = schedule_full_sync(condominio_id)
            sync_type = "full"
            message = "Sincronização completa agendada"
        else:
            # Sincronização incremental
            task = schedule_incremental_sync(condominio_id)
            sync_type = "incremental"
            message = "Sincronização incremental agendada"

        logger.info(
            f"[Solides] Sincronização {sync_type} agendada "
            f"(condominio={condominio_id}, task_id={task.id}, user={current_user.id})"
        )

        return SyncTriggerResponse(
            success=True,
            message=message,
            task_id=str(task.id),
            sync_type=sync_type,
            entity_types=request.entity_types
        )

    except Exception as e:
        logger.error(f"[Solides] Erro ao agendar sincronização: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao agendar sincronização: {str(e)}"
        )


@router.post(
    "/sync/full",
    response_model=SyncTriggerResponse,
    summary="Disparar sincronização completa",
    description="Dispara sincronização completa de todas as entidades."
)
async def trigger_full_sync(
    request: SyncTriggerRequest = Body(default=SyncTriggerRequest()),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> SyncTriggerResponse:
    """Dispara sincronização completa."""
    condominio_id = str(current_user.condominio_id)

    task = schedule_full_sync(condominio_id)

    logger.info(
        f"[Solides] Sincronização completa agendada "
        f"(condominio={condominio_id}, task_id={task.id})"
    )

    return SyncTriggerResponse(
        success=True,
        message="Sincronização completa agendada",
        task_id=str(task.id),
        sync_type="full"
    )


@router.post(
    "/sync/incremental",
    response_model=SyncTriggerResponse,
    summary="Disparar sincronização incremental",
    description="Dispara sincronização incremental (apenas alterações)."
)
async def trigger_incremental_sync(
    request: SyncTriggerRequest = Body(default=SyncTriggerRequest()),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> SyncTriggerResponse:
    """Dispara sincronização incremental."""
    condominio_id = str(current_user.condominio_id)

    task = schedule_incremental_sync(condominio_id)

    logger.info(
        f"[Solides] Sincronização incremental agendada "
        f"(condominio={condominio_id}, task_id={task.id})"
    )

    return SyncTriggerResponse(
        success=True,
        message="Sincronização incremental agendada",
        task_id=str(task.id),
        sync_type="incremental"
    )


@router.post(
    "/sync/entity/{entity_type}/{solides_id}",
    response_model=SyncTriggerResponse,
    summary="Sincronizar entidade específica",
    description="Sincroniza uma entidade específica pelo ID do Sólides."
)
async def sync_single_entity(
    entity_type: str,
    solides_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> SyncTriggerResponse:
    """Sincroniza uma entidade específica."""
    condominio_id = str(current_user.condominio_id)

    # Validar tipo de entidade
    valid_types = ["colaboradores", "departamentos", "cargos", "ocorrencias", "absenteismos"]
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de entidade inválido. Válidos: {', '.join(valid_types)}"
        )

    task = schedule_entity_sync(condominio_id, entity_type, solides_id)

    logger.info(
        f"[Solides] Sincronização de entidade agendada "
        f"(entity={entity_type}/{solides_id}, condominio={condominio_id})"
    )

    return SyncTriggerResponse(
        success=True,
        message=f"Sincronização de {entity_type}/{solides_id} agendada",
        task_id=str(task.id),
        sync_type="entity",
        entity_types=[entity_type]
    )


# ==================== ENDPOINTS DE LOGS ====================


@router.get(
    "/logs",
    response_model=List[SyncLogResponse],
    summary="Listar logs de sincronização",
    description="Retorna histórico de logs de sincronização."
)
async def get_sync_logs(
    since: Optional[datetime] = Query(
        default=None,
        description="Filtrar logs a partir desta data"
    ),
    entity_type: Optional[str] = Query(
        default=None,
        description="Filtrar por tipo de entidade"
    ),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filtrar por status: pending, processing, completed, failed"
    ),
    limit: int = Query(
        default=100,
        le=200,
        description="Limite de registros"
    ),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> List[SyncLogResponse]:
    """Retorna logs de sincronização com filtros."""
    query = db.query(SolidesSyncLog).filter(
        SolidesSyncLog.condominio_id == current_user.condominio_id
    )

    if since:
        query = query.filter(SolidesSyncLog.started_at >= since)

    if entity_type:
        query = query.filter(SolidesSyncLog.entity_type == entity_type)

    if status_filter:
        try:
            query = query.filter(SolidesSyncLog.status == SyncStatus(status_filter))
        except ValueError:
            pass  # Ignora filtro inválido

    logs = query.order_by(
        SolidesSyncLog.started_at.desc()
    ).limit(limit).all()

    return [
        SyncLogResponse(
            id=str(log.id),
            sync_type=log.sync_type or "unknown",
            entity_type=log.entity_type or "unknown",
            status=log.status.value if log.status else "unknown",
            started_at=log.started_at,
            completed_at=log.completed_at,
            duration_seconds=log.duration_seconds,
            total_processed=log.total_processed or 0,
            created_count=log.created_count or 0,
            updated_count=log.updated_count or 0,
            error_count=log.error_count or 0
        )
        for log in logs
    ]


@router.get(
    "/logs/{log_id}",
    summary="Detalhes de log de sincronização",
    description="Retorna detalhes completos de um log específico."
)
async def get_sync_log_detail(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """Retorna detalhes de um log de sincronização."""
    try:
        log_uuid = UUID(log_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de log inválido"
        )

    log = db.query(SolidesSyncLog).filter(
        SolidesSyncLog.id == log_uuid,
        SolidesSyncLog.condominio_id == current_user.condominio_id
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log não encontrado"
        )

    return {
        "id": str(log.id),
        "sync_type": log.sync_type,
        "entity_type": log.entity_type,
        "direction": log.direction.value if log.direction else None,
        "status": log.status.value if log.status else None,
        "started_at": log.started_at,
        "completed_at": log.completed_at,
        "duration_seconds": log.duration_seconds,
        "total_processed": log.total_processed,
        "created_count": log.created_count,
        "updated_count": log.updated_count,
        "deleted_count": log.deleted_count,
        "skipped_count": log.skipped_count,
        "error_count": log.error_count,
        "conflict_count": log.conflict_count,
        "errors": log.errors,
        "triggered_by": str(log.triggered_by) if log.triggered_by else None,
        "trigger_info": log.trigger_info,
    }


# ==================== ENDPOINTS DE CONFIGURAÇÃO ====================


@router.get(
    "/config",
    response_model=SolidesConfigResponse,
    summary="Obter configuração",
    description="Retorna configuração atual da integração Sólides."
)
async def get_config(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> SolidesConfigResponse:
    """Retorna configuração atual da integração."""
    config = db.query(SolidesIntegrationConfig).filter(
        SolidesIntegrationConfig.condominio_id == current_user.condominio_id
    ).first()

    if not config:
        return SolidesConfigResponse(
            is_enabled=False,
            is_connected=False,
            sync_direction=None,
            conflict_strategy=None,
            enabled_entities=[],
            last_health_check_at=None,
            last_health_check_status=None
        )

    return SolidesConfigResponse(
        is_enabled=config.is_enabled,
        is_connected=config.is_connected,
        sync_direction=config.sync_direction.value if config.sync_direction else None,
        conflict_strategy=config.conflict_strategy.value if config.conflict_strategy else None,
        enabled_entities=config.enabled_entities or [],
        last_health_check_at=config.last_health_check_at,
        last_health_check_status=config.last_health_check_status
    )


@router.post(
    "/config",
    summary="Configurar integração",
    description="Configura ou atualiza integração com Sólides."
)
async def configure_integration(
    config_data: SolidesConfigRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """Configura integração com Sólides."""
    condominio_id = current_user.condominio_id

    # Validar token com health check
    try:
        connector = SolidesConnector(credentials={"api_token": config_data.api_token})

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async with connector:
                health = loop.run_until_complete(connector.health_check())
        finally:
            loop.close()

        if not health.healthy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token inválido ou API indisponível: {health.message}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Solides] Erro ao validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar token: {str(e)}"
        )

    # Salvar/atualizar credencial
    credential = db.query(SolidesCredential).filter(
        SolidesCredential.condominio_id == condominio_id
    ).first()

    if credential:
        credential.api_token_encrypted = config_data.api_token  # TODO: encrypt
        credential.last_validated_at = datetime.utcnow()
        credential.is_valid = True
        credential.updated_by = current_user.id
    else:
        credential = SolidesCredential(
            condominio_id=condominio_id,
            api_token_encrypted=config_data.api_token,  # TODO: encrypt
            last_validated_at=datetime.utcnow(),
            is_valid=True,
            created_by=current_user.id
        )
        db.add(credential)

    # Salvar/atualizar config
    config = db.query(SolidesIntegrationConfig).filter(
        SolidesIntegrationConfig.condominio_id == condominio_id
    ).first()

    if config:
        config.is_enabled = True
        config.is_connected = True
        config.sync_direction = SyncDirection(config_data.sync_direction)
        config.conflict_strategy = ConflictStrategy(config_data.conflict_strategy)
        config.enabled_entities = config_data.enabled_entities
        config.incremental_sync_interval_minutes = config_data.incremental_sync_interval_minutes
        config.auto_create_departments = config_data.auto_create_departments
        config.auto_create_positions = config_data.auto_create_positions
        config.webhook_enabled = config_data.webhook_enabled
        config.last_health_check_at = datetime.utcnow()
        config.last_health_check_status = True
    else:
        config = SolidesIntegrationConfig(
            condominio_id=condominio_id,
            is_enabled=True,
            is_connected=True,
            sync_direction=SyncDirection(config_data.sync_direction),
            conflict_strategy=ConflictStrategy(config_data.conflict_strategy),
            enabled_entities=config_data.enabled_entities,
            incremental_sync_interval_minutes=config_data.incremental_sync_interval_minutes,
            auto_create_departments=config_data.auto_create_departments,
            auto_create_positions=config_data.auto_create_positions,
            webhook_enabled=config_data.webhook_enabled,
            last_health_check_at=datetime.utcnow(),
            last_health_check_status=True
        )
        db.add(config)

    db.commit()

    logger.info(
        f"[Solides] Integração configurada "
        f"(condominio={condominio_id}, user={current_user.id})"
    )

    return {"success": True, "message": "Integração configurada com sucesso"}


@router.delete(
    "/config",
    summary="Desabilitar integração",
    description="Desabilita a integração com Sólides."
)
async def disable_integration(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """Desabilita integração com Sólides."""
    config = db.query(SolidesIntegrationConfig).filter(
        SolidesIntegrationConfig.condominio_id == current_user.condominio_id
    ).first()

    if config:
        config.is_enabled = False
        config.is_connected = False
        db.commit()

        logger.info(
            f"[Solides] Integração desabilitada "
            f"(condominio={current_user.condominio_id}, user={current_user.id})"
        )

    return {"success": True, "message": "Integração desabilitada"}


# ==================== ENDPOINTS DE CONFLITOS ====================


@router.get(
    "/conflicts",
    response_model=List[ConflictResponse],
    summary="Listar conflitos",
    description="Lista conflitos de sincronização pendentes de resolução."
)
async def list_conflicts(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filtrar por status: pending, resolved, ignored"
    ),
    entity_type: Optional[str] = Query(
        default=None,
        description="Filtrar por tipo de entidade"
    ),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> List[ConflictResponse]:
    """Lista conflitos de sincronização."""
    query = db.query(SolidesSyncConflict).filter(
        SolidesSyncConflict.condominio_id == current_user.condominio_id
    )

    if status_filter:
        try:
            query = query.filter(SolidesSyncConflict.status == ConflictStatus(status_filter))
        except ValueError:
            pass
    else:
        # Por padrão, só pendentes
        query = query.filter(SolidesSyncConflict.status == ConflictStatus.PENDING)

    if entity_type:
        query = query.filter(SolidesSyncConflict.entity_type == entity_type)

    conflicts = query.order_by(
        SolidesSyncConflict.detected_at.desc()
    ).offset(offset).limit(limit).all()

    return [
        ConflictResponse(
            id=str(c.id),
            entity_type=c.entity_type,
            entity_id=c.entity_id,
            solides_id=c.solides_id,
            status=c.status.value,
            changed_fields=c.changed_fields or [],
            detected_at=c.detected_at,
            solides_data=c.solides_data or {},
            conecta_data=c.conecta_data or {}
        )
        for c in conflicts
    ]


@router.post(
    "/conflicts/{conflict_id}/resolve",
    summary="Resolver conflito",
    description="Resolve um conflito de sincronização."
)
async def resolve_conflict(
    conflict_id: str,
    resolution: ConflictResolutionRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """Resolve conflito de sincronização."""
    try:
        conflict_uuid = UUID(conflict_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de conflito inválido"
        )

    conflict = db.query(SolidesSyncConflict).filter(
        SolidesSyncConflict.id == conflict_uuid,
        SolidesSyncConflict.condominio_id == current_user.condominio_id
    ).first()

    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conflito não encontrado"
        )

    if conflict.status != ConflictStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conflito já foi resolvido"
        )

    # Validar estratégia
    try:
        strategy = ConflictStrategy(resolution.strategy)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estratégia inválida. Válidas: solides_wins, conecta_wins, most_recent, manual"
        )

    # Resolver
    resolver = get_resolver_for_entity(conflict.entity_type)
    resolved_data, updated_conflict = resolver.resolve_conflict_record(
        db=db,
        conflict=conflict,
        strategy=strategy,
        resolved_by=current_user.id,
        resolution_notes=resolution.resolution_notes
    )

    logger.info(
        f"[Solides] Conflito resolvido "
        f"(conflict_id={conflict_id}, strategy={resolution.strategy}, user={current_user.id})"
    )

    return {
        "success": True,
        "message": "Conflito resolvido",
        "strategy_used": resolution.strategy,
        "resolved_data": resolved_data
    }


@router.post(
    "/conflicts/{conflict_id}/ignore",
    summary="Ignorar conflito",
    description="Marca um conflito como ignorado."
)
async def ignore_conflict(
    conflict_id: str,
    notes: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> Dict[str, Any]:
    """Ignora conflito de sincronização."""
    try:
        conflict_uuid = UUID(conflict_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de conflito inválido"
        )

    conflict = db.query(SolidesSyncConflict).filter(
        SolidesSyncConflict.id == conflict_uuid,
        SolidesSyncConflict.condominio_id == current_user.condominio_id
    ).first()

    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conflito não encontrado"
        )

    resolver = ConflictResolver()
    resolver.ignore_conflict(db, conflict, current_user.id, notes)

    logger.info(
        f"[Solides] Conflito ignorado "
        f"(conflict_id={conflict_id}, user={current_user.id})"
    )

    return {"success": True, "message": "Conflito ignorado"}


# ==================== ENDPOINT DE HEALTH CHECK ====================


@router.get(
    "/health",
    response_model=IntegrationStatusResponse,
    summary="Health check",
    description="Verifica saúde da conexão com Sólides."
)
async def health_check(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
) -> IntegrationStatusResponse:
    """Verifica saúde da integração com Sólides."""
    try:
        # Verificar se está configurado
        config = db.query(SolidesIntegrationConfig).filter(
            SolidesIntegrationConfig.condominio_id == current_user.condominio_id
        ).first()

        if not config or not config.is_enabled:
            return IntegrationStatusResponse(
                healthy=False,
                connected=False,
                message="Integração não configurada ou desabilitada"
            )

        # Testar conexão
        sync_service = get_sync_service(db, current_user.condominio_id)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            status_data = loop.run_until_complete(sync_service.get_sync_status())
        finally:
            loop.close()

        # Contar itens pendentes
        pending = db.query(SolidesSyncConflict).filter(
            SolidesSyncConflict.condominio_id == current_user.condominio_id,
            SolidesSyncConflict.status == ConflictStatus.PENDING
        ).count()

        # Última sync
        last_sync = db.query(SolidesSyncLog).filter(
            SolidesSyncLog.condominio_id == current_user.condominio_id,
            SolidesSyncLog.status == SyncStatus.COMPLETED
        ).order_by(SolidesSyncLog.completed_at.desc()).first()

        return IntegrationStatusResponse(
            healthy=status_data.get("connected", False),
            connected=status_data.get("connected", False),
            latency_ms=status_data.get("api_latency_ms"),
            message=status_data.get("api_message", "OK"),
            last_sync_at=last_sync.completed_at if last_sync else None,
            pending_items=pending
        )

    except Exception as e:
        logger.error(f"[Solides] Erro no health check: {e}", exc_info=True)
        return IntegrationStatusResponse(
            healthy=False,
            connected=False,
            message=str(e)
        )
