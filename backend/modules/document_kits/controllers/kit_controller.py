"""Controller de Kits Documentais - Versão Async com Autenticação."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import CurrentUserId
from modules.document_kits.models.document_kit import (
    KitType,
    KitStatus,
    AssignmentStatus,
    ItemStatusEnum,
    EntityType,
)
from modules.document_kits.schemas.kit_schemas import (
    DocumentKitCreate,
    DocumentKitUpdate,
    DocumentKitResponse,
    DocumentKitListResponse,
    DocumentKitItemCreate,
    DocumentKitItemUpdate,
    DocumentKitItemResponse,
    DocumentKitAssignmentCreate,
    DocumentKitAssignmentUpdate,
    DocumentKitAssignmentResponse,
    DocumentKitItemStatusResponse,
    KitStatsResponse,
    KitSuggestionResponse,
)
from modules.document_kits.services.kit_service import DocumentKitService
from modules.document_kits.services.kit_ai_service import DocumentKitAIService
from modules.document_kits.services.kit_operational_service import KitOperationalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document-kits", tags=["Document Kits"])


async def get_service(db: AsyncSession = Depends(get_db)) -> DocumentKitService:
    """Retorna instancia do service."""
    return DocumentKitService(db)


async def get_ai_service(db: AsyncSession = Depends(get_db)) -> DocumentKitAIService:
    """Retorna instancia do AI service."""
    return DocumentKitAIService(db)


async def get_operational_service(db: AsyncSession = Depends(get_db)) -> KitOperationalService:
    """Retorna instancia do Operational service."""
    return KitOperationalService(db)


# === Kit Endpoints ===


@router.post("/", response_model=DocumentKitResponse, status_code=status.HTTP_201_CREATED)
async def create_kit(
    data: DocumentKitCreate,
    user_id: CurrentUserId,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Cria um novo kit documental."""
    try:
        kit = await service.create_kit(data, UUID(user_id))
        logger.info("Kit criado por %s: %s", user_id, kit.id)
        return DocumentKitResponse.model_validate(kit)
    except Exception as e:
        logger.error("Erro ao criar kit: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/", response_model=DocumentKitListResponse)
async def list_kits(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    tipo: Optional[KitType] = None,
    kit_status: Optional[KitStatus] = Query(None, alias="status"),
    is_template: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitListResponse:
    """Lista kits documentais."""
    kits = await service.list_kits(
        condominio_id=condominio_id,
        tipo=tipo,
        status=kit_status,
        is_template=is_template,
        search=search,
        skip=skip,
        limit=limit,
    )
    total = await service.count_kits(condominio_id, tipo, kit_status)
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return DocumentKitListResponse(
        items=[DocumentKitResponse.model_validate(k) for k in kits],
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=pages,
    )


@router.get("/stats", response_model=KitStatsResponse)
async def get_stats(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> KitStatsResponse:
    """Retorna estatisticas de kits."""
    stats = await service.get_stats(condominio_id)
    return KitStatsResponse(**stats)


@router.get("/templates", response_model=List[DocumentKitResponse])
async def list_templates(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    tipo: Optional[KitType] = None,
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitResponse]:
    """Lista templates de kits."""
    kits = await service.list_kits(
        condominio_id=condominio_id,
        tipo=tipo,
        status=KitStatus.ATIVO,
        is_template=True,
    )
    return [DocumentKitResponse.model_validate(k) for k in kits]


@router.get("/{kit_id}", response_model=DocumentKitResponse)
async def get_kit(
    kit_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Busca kit por ID."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    return DocumentKitResponse.model_validate(kit)


@router.put("/{kit_id}", response_model=DocumentKitResponse)
async def update_kit(
    kit_id: UUID,
    data: DocumentKitUpdate,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Atualiza kit."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = await service.update_kit(kit, data, UUID(user_id))
    return DocumentKitResponse.model_validate(kit)


@router.delete("/{kit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kit(
    kit_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> None:
    """Remove kit."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    await service.delete_kit(kit)


@router.post("/{kit_id}/activate", response_model=DocumentKitResponse)
async def activate_kit(
    kit_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Ativa kit."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = await service.activate_kit(kit)
    return DocumentKitResponse.model_validate(kit)


@router.post("/{kit_id}/deactivate", response_model=DocumentKitResponse)
async def deactivate_kit(
    kit_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Desativa kit."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = await service.deactivate_kit(kit)
    return DocumentKitResponse.model_validate(kit)


@router.post("/{kit_id}/archive", response_model=DocumentKitResponse)
async def archive_kit(
    kit_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Arquiva kit."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = await service.archive_kit(kit)
    return DocumentKitResponse.model_validate(kit)


@router.post("/{kit_id}/duplicate", response_model=DocumentKitResponse)
async def duplicate_kit(
    kit_id: UUID,
    new_codigo: str = Query(..., min_length=1),
    new_nome: str = Query(..., min_length=1),
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Duplica kit."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    new_kit = await service.duplicate_kit(kit, new_codigo, new_nome, UUID(user_id))
    return DocumentKitResponse.model_validate(new_kit)


# === Kit Item Endpoints ===


@router.post(
    "/{kit_id}/items",
    response_model=DocumentKitItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_item(
    kit_id: UUID,
    data: DocumentKitItemCreate,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemResponse:
    """Adiciona item ao kit."""
    kit = await service.get_kit(kit_id, condominio_id)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    item = await service.add_item(kit, data)
    return DocumentKitItemResponse.model_validate(item)


@router.get("/{kit_id}/items", response_model=List[DocumentKitItemResponse])
async def list_items(
    kit_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    only_active: bool = True,
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitItemResponse]:
    """Lista itens de um kit."""
    items = await service.list_kit_items(kit_id, condominio_id, only_active)
    return [DocumentKitItemResponse.model_validate(i) for i in items]


@router.get("/items/{item_id}", response_model=DocumentKitItemResponse)
async def get_item(
    item_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemResponse:
    """Busca item por ID."""
    item = await service.get_item(item_id, condominio_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return DocumentKitItemResponse.model_validate(item)


@router.put("/items/{item_id}", response_model=DocumentKitItemResponse)
async def update_item(
    item_id: UUID,
    data: DocumentKitItemUpdate,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemResponse:
    """Atualiza item."""
    item = await service.get_item(item_id, condominio_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    item = await service.update_item(item, data)
    return DocumentKitItemResponse.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> None:
    """Remove item."""
    item = await service.get_item(item_id, condominio_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    await service.delete_item(item)


@router.post("/{kit_id}/items/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_items(
    kit_id: UUID,
    item_orders: List[dict],
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> None:
    """Reordena itens do kit."""
    await service.reorder_items(kit_id, condominio_id, item_orders)


# === Assignment Endpoints ===


@router.post(
    "/assignments",
    response_model=DocumentKitAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_kit(
    data: DocumentKitAssignmentCreate,
    user_id: CurrentUserId,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Atribui kit a uma entidade."""
    try:
        assignment = await service.assign_kit(data, UUID(user_id))
        return DocumentKitAssignmentResponse.model_validate(assignment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/assignments", response_model=List[DocumentKitAssignmentResponse])
async def list_assignments(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    kit_id: Optional[UUID] = None,
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[UUID] = None,
    assignment_status: Optional[AssignmentStatus] = Query(None, alias="status"),
    vencidos: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitAssignmentResponse]:
    """Lista atribuicoes."""
    assignments = await service.list_assignments(
        condominio_id=condominio_id,
        kit_id=kit_id,
        entity_type=entity_type,
        entity_id=entity_id,
        status=assignment_status,
        vencidos=vencidos,
        skip=skip,
        limit=limit,
    )
    return [DocumentKitAssignmentResponse.model_validate(a) for a in assignments]


@router.get("/assignments/pending", response_model=List[DocumentKitAssignmentResponse])
async def list_pending_assignments(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitAssignmentResponse]:
    """Lista atribuicoes pendentes."""
    assignments = await service.list_assignments(
        condominio_id=condominio_id,
        status=AssignmentStatus.PENDENTE,
    )
    return [DocumentKitAssignmentResponse.model_validate(a) for a in assignments]


@router.get("/assignments/overdue", response_model=List[DocumentKitAssignmentResponse])
async def list_overdue_assignments(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitAssignmentResponse]:
    """Lista atribuicoes vencidas."""
    assignments = await service.list_assignments(
        condominio_id=condominio_id,
        vencidos=True,
    )
    return [DocumentKitAssignmentResponse.model_validate(a) for a in assignments]


@router.get("/assignments/{assignment_id}", response_model=DocumentKitAssignmentResponse)
async def get_assignment(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Busca atribuicao por ID."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.put("/assignments/{assignment_id}", response_model=DocumentKitAssignmentResponse)
async def update_assignment(
    assignment_id: UUID,
    data: DocumentKitAssignmentUpdate,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Atualiza atribuicao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = await service.update_assignment(assignment, data)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/start", response_model=DocumentKitAssignmentResponse)
async def start_assignment(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Inicia atribuicao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = await service.start_assignment(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/approve", response_model=DocumentKitAssignmentResponse)
async def approve_assignment(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Aprova atribuicao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = await service.approve_assignment(assignment, UUID(user_id))
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/reject", response_model=DocumentKitAssignmentResponse)
async def reject_assignment(
    assignment_id: UUID,
    motivo: str = Query(..., min_length=1),
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Reprova atribuicao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = await service.reject_assignment(assignment, motivo)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/complete", response_model=DocumentKitAssignmentResponse)
async def complete_assignment(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Completa atribuicao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = await service.complete_assignment(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/cancel", response_model=DocumentKitAssignmentResponse)
async def cancel_assignment(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Cancela atribuicao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = await service.cancel_assignment(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/notify", response_model=DocumentKitAssignmentResponse)
async def notify_assignment(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Envia notificacao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = await service.send_notification(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


# === Item Status Endpoints ===


@router.get(
    "/assignments/{assignment_id}/statuses",
    response_model=List[DocumentKitItemStatusResponse],
)
async def list_item_statuses(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    item_status: Optional[ItemStatusEnum] = Query(None, alias="status"),
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitItemStatusResponse]:
    """Lista status de itens de uma atribuicao."""
    statuses = await service.list_assignment_statuses(
        assignment_id, condominio_id, item_status
    )
    return [DocumentKitItemStatusResponse.model_validate(s) for s in statuses]


@router.get("/item-statuses/{status_id}", response_model=DocumentKitItemStatusResponse)
async def get_item_status(
    status_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Busca status de item."""
    item_status = await service.get_item_status(status_id, condominio_id)
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post("/item-statuses/{status_id}/submit", response_model=DocumentKitItemStatusResponse)
async def submit_document(
    status_id: UUID,
    arquivo_url: str = Query(...),
    arquivo_nome: str = Query(...),
    arquivo_tamanho: int = Query(..., ge=0),
    arquivo_tipo: str = Query(...),
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Submete documento."""
    item_status = await service.get_item_status(status_id, condominio_id)
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = await service.submit_document(
        item_status, arquivo_url, arquivo_nome, arquivo_tamanho, arquivo_tipo, UUID(user_id)
    )
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post("/item-statuses/{status_id}/approve", response_model=DocumentKitItemStatusResponse)
async def approve_document(
    status_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    observacoes: Optional[str] = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Aprova documento."""
    item_status = await service.get_item_status(status_id, condominio_id)
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = await service.approve_document(item_status, UUID(user_id), observacoes)
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post("/item-statuses/{status_id}/reject", response_model=DocumentKitItemStatusResponse)
async def reject_document(
    status_id: UUID,
    motivo: str = Query(..., min_length=1),
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Reprova documento."""
    item_status = await service.get_item_status(status_id, condominio_id)
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = await service.reject_document(item_status, motivo)
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post(
    "/item-statuses/{status_id}/not-applicable",
    response_model=DocumentKitItemStatusResponse,
)
async def mark_not_applicable(
    status_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    motivo: Optional[str] = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Marca item como nao aplicavel."""
    item_status = await service.get_item_status(status_id, condominio_id)
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = await service.mark_not_applicable(item_status, motivo or "")
    return DocumentKitItemStatusResponse.model_validate(item_status)


# === AI Endpoints ===


@router.get("/ai/suggest", response_model=List[KitSuggestionResponse])
async def suggest_kits(
    entity_type: EntityType,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    cargo: Optional[str] = None,
    departamento: Optional[str] = None,
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> List[KitSuggestionResponse]:
    """Sugere kits para uma entidade."""
    entity_data = {
        "cargo": cargo or "",
        "departamento": departamento or "",
    }
    suggestions = await ai_service.suggest_kits_for_entity(
        condominio_id, entity_type, entity_data
    )
    return [KitSuggestionResponse(**s) for s in suggestions]


@router.get("/ai/compliance/{entity_type}/{entity_id}")
async def analyze_compliance(
    entity_type: EntityType,
    entity_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> dict:
    """Analisa conformidade de uma entidade."""
    return await ai_service.analyze_compliance_risk(
        condominio_id, entity_type, entity_id
    )


@router.get("/ai/predict/{assignment_id}")
async def predict_completion(
    assignment_id: UUID,
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    service: DocumentKitService = Depends(get_service),
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> dict:
    """Preve data de conclusao."""
    assignment = await service.get_assignment(assignment_id, condominio_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    return await ai_service.predict_completion_date(assignment)


@router.get("/ai/priorities", response_model=List[dict])
async def get_priorities(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    limit: int = Query(10, ge=1, le=50),
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> List[dict]:
    """Retorna atribuicoes prioritarias."""
    return await ai_service.get_priority_assignments(condominio_id, limit)


@router.get("/ai/usage")
async def analyze_usage(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> dict:
    """Analisa uso dos kits."""
    return await ai_service.analyze_kit_usage(condominio_id)


@router.get("/ai/expiring", response_model=List[dict])
async def get_expiring_documents(
    condominio_id: UUID = Query(..., description="ID do condominio"),
    user_id: CurrentUserId = None,
    days_ahead: int = Query(30, ge=1, le=365),
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> List[dict]:
    """Lista documentos proximos do vencimento."""
    return await ai_service.get_expiring_documents(condominio_id, days_ahead)


# === Operational Integration Endpoints ===


@router.get("/operational/employees", response_model=List[dict])
async def get_employees_by_condominium(
    condominium_id: str,
    user_id: CurrentUserId = None,
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    include_inactive: bool = Query(False, description="Incluir funcionarios inativos"),
    op_service: KitOperationalService = Depends(get_operational_service),
) -> List[dict]:
    """Busca todos os colaboradores alocados em um condominio no periodo."""
    try:
        from datetime import date

        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None

        employees_data = await op_service.get_employees_by_condominium(
            condominium_id=condominium_id,
            start_date=start,
            end_date=end,
            include_inactive=include_inactive,
        )

        result = [emp.to_dict() for emp in employees_data]

        logger.info(
            "Fetched %d employees for condominium %s",
            len(result),
            condominium_id,
        )

        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error fetching employees: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/operational/employees/month", response_model=List[dict])
async def get_employees_by_month(
    condominium_id: str,
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Ano (ex: 2026)"),
    user_id: CurrentUserId = None,
    include_inactive: bool = Query(False, description="Incluir funcionarios inativos"),
    op_service: KitOperationalService = Depends(get_operational_service),
) -> List[dict]:
    """Busca colaboradores de um condominio em um mes especifico."""
    try:
        employees_data = await op_service.get_employees_by_month(
            condominium_id=condominium_id,
            month=month,
            year=year,
            include_inactive=include_inactive,
        )

        result = [emp.to_dict() for emp in employees_data]

        logger.info(
            "Fetched %d employees for condominium %s (month: %02d/%d)",
            len(result),
            condominium_id,
            month,
            year,
        )

        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error fetching employees by month: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/operational/condominiums", response_model=List[dict])
async def get_condominiums_with_employees(
    user_id: CurrentUserId = None,
    op_service: KitOperationalService = Depends(get_operational_service),
) -> List[dict]:
    """Busca TODOS os condominios que possuem funcionarios alocados atualmente."""
    try:
        result = await op_service.get_condominiums_with_employees()

        logger.info("Fetched %d condominiums with active employees", len(result))

        return result

    except Exception as e:
        logger.error("Error fetching condominiums: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/operational/validate", response_model=dict)
async def validate_condominium_has_employees(
    condominium_id: str,
    user_id: CurrentUserId = None,
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, ge=2020, le=2100, description="Ano"),
    op_service: KitOperationalService = Depends(get_operational_service),
) -> dict:
    """Valida se um condominio possui funcionarios no periodo."""
    try:
        result = await op_service.validate_condominium_has_employees(
            condominium_id=condominium_id,
            month=month,
            year=year,
        )

        logger.info(
            "Validation for condominium %s: %s employees",
            condominium_id,
            result["employee_count"],
        )

        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error validating condominium: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
