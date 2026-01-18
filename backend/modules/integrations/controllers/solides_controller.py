"""
Controller REST para integração Sólides.
Sprint 33: Integration Framework

Endpoints para configuração, monitoramento e acionamento de sincronização.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.integrations.connectors.solides.connector import SolidesConnector
from modules.integrations.connectors.solides.sync_service import (
    get_sync_service,
    SyncDirection,
)
from modules.integrations.connectors.solides.webhook_handler import SolidesWebhookHandler
from modules.integrations.connectors.solides.models import (
    SolidesIntegrationConfig,
    SolidesSyncState,
    SolidesSyncLog,
    SolidesSyncConflict,
    SolidesEntityMapping,
    SolidesCredential,
    ConflictStatus,
    ConflictStrategy,
    SyncStatus,
)
from modules.integrations.connectors.solides.conflict_resolver import (
    ConflictResolver,
    get_resolver_for_entity,
)
from modules.integrations.connectors.solides.tasks import (
    schedule_full_sync,
    schedule_incremental_sync,
    schedule_entity_sync,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/solides", tags=["Sólides Integration"])


# ==================== SCHEMAS ====================

class SolidesConfigRequest(BaseModel):
    """Schema para configurar integração."""
    api_token: str = Field(..., min_length=10, description="Token de API do Sólides")
    sync_direction: str = Field(default="solides_to_conecta")
    conflict_strategy: str = Field(default="most_recent")
    enabled_entities: List[str] = Field(
        default=["colaboradores", "departamentos", "cargos", "ocorrencias", "absenteismos"]
    )
    incremental_sync_interval_minutes: int = Field(default=15, ge=5, le=60)
    auto_create_departments: bool = True
    auto_create_positions: bool = True
    webhook_enabled: bool = True


class SolidesConfigResponse(BaseModel):
    """Resposta de configuração."""
    is_enabled: bool
    is_connected: bool
    sync_direction: Optional[str]
    conflict_strategy: Optional[str]
    enabled_entities: List[str]
    last_health_check_at: Optional[datetime]
    last_health_check_status: Optional[bool]


class SyncTriggerRequest(BaseModel):
    """Request para disparar sincronização."""
    entity_types: Optional[List[str]] = None
    full_sync: bool = False


class SyncStatusResponse(BaseModel):
    """Status da sincronização."""
    connected: bool
    api_latency_ms: Optional[int]
    entities: dict
    pending_conflicts: int
    last_full_sync_at: Optional[datetime]
    last_incremental_sync_at: Optional[datetime]


class ConflictResponse(BaseModel):
    """Conflito de sincronização."""
    id: str
    entity_type: str
    entity_id: str
    solides_id: str
    status: str
    changed_fields: List[str]
    detected_at: datetime
    solides_data: dict
    conecta_data: dict


class ConflictResolutionRequest(BaseModel):
    """Request para resolver conflito."""
    strategy: str = Field(..., description="solides_wins, conecta_wins, most_recent, manual")
    resolution_notes: Optional[str] = None


class SyncLogResponse(BaseModel):
    """Log de sincronização."""
    id: str
    sync_type: str
    entity_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    total_processed: int
    created_count: int
    updated_count: int
    error_count: int


# ==================== ENDPOINTS DE CONFIGURAÇÃO ====================

@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna status atual da integração e última sincronização.
    """
    condominio_id = current_user.condominio_id

    try:
        sync_service = get_sync_service(db, condominio_id)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            status = loop.run_until_complete(sync_service.get_sync_status())
        finally:
            loop.close()

        # Buscar última sync
        last_full = db.query(SolidesSyncState).filter(
            SolidesSyncState.condominio_id == condominio_id,
            SolidesSyncState.last_full_sync_at.isnot(None)
        ).order_by(SolidesSyncState.last_full_sync_at.desc()).first()

        last_incremental = db.query(SolidesSyncState).filter(
            SolidesSyncState.condominio_id == condominio_id,
            SolidesSyncState.last_sync_at.isnot(None)
        ).order_by(SolidesSyncState.last_sync_at.desc()).first()

        return {
            "connected": status.get("connected", False),
            "api_latency_ms": status.get("api_latency_ms"),
            "entities": status.get("entities", {}),
            "pending_conflicts": status.get("pending_conflicts", 0),
            "last_full_sync_at": last_full.last_full_sync_at if last_full else None,
            "last_incremental_sync_at": last_incremental.last_sync_at if last_incremental else None,
        }

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}"
        )


@router.get("/config", response_model=SolidesConfigResponse)
async def get_config(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna configuração atual da integração.
    """
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


@router.post("/config")
async def configure_integration(
    config_data: SolidesConfigRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Configura integração com Sólides.
    """
    condominio_id = current_user.condominio_id

    # Validar token
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

    logger.info(f"[Solides] Integração configurada para condomínio {condominio_id}")

    return {"success": True, "message": "Integração configurada com sucesso"}


@router.delete("/config")
async def disable_integration(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Desabilita integração com Sólides.
    """
    config = db.query(SolidesIntegrationConfig).filter(
        SolidesIntegrationConfig.condominio_id == current_user.condominio_id
    ).first()

    if config:
        config.is_enabled = False
        config.is_connected = False
        db.commit()

    return {"success": True, "message": "Integração desabilitada"}


# ==================== ENDPOINTS DE SINCRONIZAÇÃO ====================

@router.post("/sync/full")
async def trigger_full_sync(
    request: SyncTriggerRequest = Body(default=SyncTriggerRequest()),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dispara sincronização completa.
    """
    condominio_id = str(current_user.condominio_id)

    task = schedule_full_sync(condominio_id)

    return {
        "success": True,
        "message": "Sincronização completa agendada",
        "task_id": task.id
    }


@router.post("/sync/incremental")
async def trigger_incremental_sync(
    request: SyncTriggerRequest = Body(default=SyncTriggerRequest()),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Dispara sincronização incremental.
    """
    condominio_id = str(current_user.condominio_id)

    task = schedule_incremental_sync(condominio_id)

    return {
        "success": True,
        "message": "Sincronização incremental agendada",
        "task_id": task.id
    }


@router.post("/sync/entity/{entity_type}/{solides_id}")
async def sync_single_entity(
    entity_type: str,
    solides_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Sincroniza uma entidade específica.
    """
    condominio_id = str(current_user.condominio_id)

    task = schedule_entity_sync(condominio_id, entity_type, solides_id)

    return {
        "success": True,
        "message": f"Sincronização de {entity_type}/{solides_id} agendada",
        "task_id": task.id
    }


# ==================== ENDPOINTS DE CONFLITOS ====================

@router.get("/conflicts", response_model=List[ConflictResponse])
async def list_conflicts(
    status_filter: Optional[str] = Query(None, alias="status"),
    entity_type: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lista conflitos pendentes de resolução.
    """
    query = db.query(SolidesSyncConflict).filter(
        SolidesSyncConflict.condominio_id == current_user.condominio_id
    )

    if status_filter:
        query = query.filter(SolidesSyncConflict.status == ConflictStatus(status_filter))
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
            solides_data=c.solides_data,
            conecta_data=c.conecta_data
        )
        for c in conflicts
    ]


@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    conflict_id: str,
    resolution: ConflictResolutionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Resolve conflito manualmente.
    """
    conflict = db.query(SolidesSyncConflict).filter(
        SolidesSyncConflict.id == UUID(conflict_id),
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

    # Resolver
    resolver = get_resolver_for_entity(conflict.entity_type)
    resolved_data, updated_conflict = resolver.resolve_conflict_record(
        db=db,
        conflict=conflict,
        strategy=ConflictStrategy(resolution.strategy),
        resolved_by=current_user.id,
        resolution_notes=resolution.resolution_notes
    )

    # TODO: Aplicar resolved_data à entidade real

    return {
        "success": True,
        "message": "Conflito resolvido",
        "strategy_used": resolution.strategy,
        "resolved_data": resolved_data
    }


@router.post("/conflicts/{conflict_id}/ignore")
async def ignore_conflict(
    conflict_id: str,
    notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Ignora conflito.
    """
    conflict = db.query(SolidesSyncConflict).filter(
        SolidesSyncConflict.id == UUID(conflict_id),
        SolidesSyncConflict.condominio_id == current_user.condominio_id
    ).first()

    if not conflict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conflito não encontrado"
        )

    resolver = ConflictResolver()
    resolver.ignore_conflict(db, conflict, current_user.id, notes)

    return {"success": True, "message": "Conflito ignorado"}


# ==================== ENDPOINT DE WEBHOOK ====================

@router.post("/webhook")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint para receber webhooks do Sólides.
    """
    # Ler body
    body = await request.body()

    try:
        payload = await request.json()
    except:
        return Response(
            content="Invalid JSON",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Extrair tipo de evento
    event_type = payload.get("event", payload.get("type", "unknown"))

    # Headers relevantes
    headers = {
        "X-Solides-Signature": request.headers.get("X-Solides-Signature", ""),
        "X-Webhook-Signature": request.headers.get("X-Webhook-Signature", ""),
        "X-Request-ID": request.headers.get("X-Request-ID", ""),
    }

    # Processar
    handler = SolidesWebhookHandler(db, async_processing=True)

    result = await handler.handle_webhook(
        event_type=event_type,
        payload=payload,
        headers=headers,
        raw_body=body,
        request_id=headers.get("X-Request-ID"),
        ip_address=request.client.host if request.client else None
    )

    # Responder 200 imediatamente (processamento assíncrono)
    return JSONResponse(
        content=result,
        status_code=status.HTTP_200_OK
    )


# ==================== ENDPOINTS DE LOGS ====================

@router.get("/logs", response_model=List[SyncLogResponse])
async def get_sync_logs(
    since: Optional[datetime] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna logs de sincronização.
    """
    query = db.query(SolidesSyncLog).filter(
        SolidesSyncLog.condominio_id == current_user.condominio_id
    )

    if since:
        query = query.filter(SolidesSyncLog.started_at >= since)

    logs = query.order_by(
        SolidesSyncLog.started_at.desc()
    ).limit(limit).all()

    return [
        SyncLogResponse(
            id=str(log.id),
            sync_type=log.sync_type,
            entity_type=log.entity_type,
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


@router.get("/logs/{log_id}")
async def get_sync_log_detail(
    log_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna detalhes de um log de sincronização.
    """
    log = db.query(SolidesSyncLog).filter(
        SolidesSyncLog.id == UUID(log_id),
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
        "triggered_by": log.triggered_by,
        "trigger_info": log.trigger_info,
    }


# ==================== ENDPOINT DE HEALTH CHECK ====================

@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Verifica saúde da conexão com Sólides.
    """
    try:
        sync_service = get_sync_service(db, current_user.condominio_id)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            status_data = loop.run_until_complete(sync_service.get_sync_status())
        finally:
            loop.close()

        return {
            "healthy": status_data.get("connected", False),
            "latency_ms": status_data.get("api_latency_ms"),
            "message": status_data.get("api_message"),
        }

    except Exception as e:
        return {
            "healthy": False,
            "message": str(e)
        }
