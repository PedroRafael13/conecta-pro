"""Controller de Kits Documentais."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document-kits", tags=["Document Kits"])

CONDOMINIO_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
USER_ID = "b2c3d4e5-f6a7-8901-bcde-f12345678901"


def get_service(db: Session = Depends(get_db)) -> DocumentKitService:
    """Retorna instancia do service."""
    return DocumentKitService(db)


def get_ai_service(db: Session = Depends(get_db)) -> DocumentKitAIService:
    """Retorna instancia do AI service."""
    return DocumentKitAIService(db)


# === Kit Endpoints ===


@router.post("/", response_model=DocumentKitResponse, status_code=status.HTTP_201_CREATED)
def create_kit(
    data: DocumentKitCreate,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Cria um novo kit documental."""
    try:
        kit = service.create_kit(data, UUID(USER_ID))
        logger.info("Kit criado: %s", kit.id)
        return DocumentKitResponse.model_validate(kit)
    except Exception as e:
        logger.error("Erro ao criar kit: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/", response_model=DocumentKitListResponse)
def list_kits(
    tipo: Optional[KitType] = None,
    kit_status: Optional[KitStatus] = Query(None, alias="status"),
    is_template: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitListResponse:
    """Lista kits documentais."""
    kits = service.list_kits(
        condominio_id=UUID(CONDOMINIO_ID),
        tipo=tipo,
        status=kit_status,
        is_template=is_template,
        search=search,
        skip=skip,
        limit=limit,
    )
    total = service.repository.count_kits(UUID(CONDOMINIO_ID), tipo, kit_status)
    pages = (total + limit - 1) // limit if limit > 0 else 0

    return DocumentKitListResponse(
        items=[DocumentKitResponse.model_validate(k) for k in kits],
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        pages=pages,
    )


@router.get("/stats", response_model=KitStatsResponse)
def get_stats(
    service: DocumentKitService = Depends(get_service),
) -> KitStatsResponse:
    """Retorna estatisticas de kits."""
    stats = service.get_stats(UUID(CONDOMINIO_ID))
    return KitStatsResponse(**stats)


@router.get("/templates", response_model=List[DocumentKitResponse])
def list_templates(
    tipo: Optional[KitType] = None,
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitResponse]:
    """Lista templates de kits."""
    kits = service.list_kits(
        condominio_id=UUID(CONDOMINIO_ID),
        tipo=tipo,
        status=KitStatus.ATIVO,
        is_template=True,
    )
    return [DocumentKitResponse.model_validate(k) for k in kits]


@router.get("/{kit_id}", response_model=DocumentKitResponse)
def get_kit(
    kit_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Busca kit por ID."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    return DocumentKitResponse.model_validate(kit)


@router.put("/{kit_id}", response_model=DocumentKitResponse)
def update_kit(
    kit_id: UUID,
    data: DocumentKitUpdate,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Atualiza kit."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = service.update_kit(kit, data, UUID(USER_ID))
    return DocumentKitResponse.model_validate(kit)


@router.delete("/{kit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kit(
    kit_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> None:
    """Remove kit."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    service.delete_kit(kit)


@router.post("/{kit_id}/activate", response_model=DocumentKitResponse)
def activate_kit(
    kit_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Ativa kit."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = service.activate_kit(kit)
    return DocumentKitResponse.model_validate(kit)


@router.post("/{kit_id}/deactivate", response_model=DocumentKitResponse)
def deactivate_kit(
    kit_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Desativa kit."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = service.deactivate_kit(kit)
    return DocumentKitResponse.model_validate(kit)


@router.post("/{kit_id}/archive", response_model=DocumentKitResponse)
def archive_kit(
    kit_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Arquiva kit."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    kit = service.archive_kit(kit)
    return DocumentKitResponse.model_validate(kit)


@router.post("/{kit_id}/duplicate", response_model=DocumentKitResponse)
def duplicate_kit(
    kit_id: UUID,
    new_codigo: str = Query(..., min_length=1),
    new_nome: str = Query(..., min_length=1),
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitResponse:
    """Duplica kit."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    new_kit = service.duplicate_kit(kit, new_codigo, new_nome, UUID(USER_ID))
    return DocumentKitResponse.model_validate(new_kit)


# === Kit Item Endpoints ===


@router.post(
    "/{kit_id}/items",
    response_model=DocumentKitItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_item(
    kit_id: UUID,
    data: DocumentKitItemCreate,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemResponse:
    """Adiciona item ao kit."""
    kit = service.get_kit(kit_id, UUID(CONDOMINIO_ID))
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")
    item = service.add_item(kit, data)
    return DocumentKitItemResponse.model_validate(item)


@router.get("/{kit_id}/items", response_model=List[DocumentKitItemResponse])
def list_items(
    kit_id: UUID,
    only_active: bool = True,
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitItemResponse]:
    """Lista itens de um kit."""
    items = service.list_kit_items(kit_id, UUID(CONDOMINIO_ID), only_active)
    return [DocumentKitItemResponse.model_validate(i) for i in items]


@router.get("/items/{item_id}", response_model=DocumentKitItemResponse)
def get_item(
    item_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemResponse:
    """Busca item por ID."""
    item = service.get_item(item_id, UUID(CONDOMINIO_ID))
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return DocumentKitItemResponse.model_validate(item)


@router.put("/items/{item_id}", response_model=DocumentKitItemResponse)
def update_item(
    item_id: UUID,
    data: DocumentKitItemUpdate,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemResponse:
    """Atualiza item."""
    item = service.get_item(item_id, UUID(CONDOMINIO_ID))
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    item = service.update_item(item, data)
    return DocumentKitItemResponse.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> None:
    """Remove item."""
    item = service.get_item(item_id, UUID(CONDOMINIO_ID))
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    service.delete_item(item)


@router.post("/{kit_id}/items/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_items(
    kit_id: UUID,
    item_orders: List[dict],
    service: DocumentKitService = Depends(get_service),
) -> None:
    """Reordena itens do kit."""
    service.reorder_items(kit_id, UUID(CONDOMINIO_ID), item_orders)


# === Assignment Endpoints ===


@router.post(
    "/assignments",
    response_model=DocumentKitAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_kit(
    data: DocumentKitAssignmentCreate,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Atribui kit a uma entidade."""
    try:
        assignment = service.assign_kit(data, UUID(USER_ID))
        return DocumentKitAssignmentResponse.model_validate(assignment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/assignments", response_model=List[DocumentKitAssignmentResponse])
def list_assignments(
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
    assignments = service.list_assignments(
        condominio_id=UUID(CONDOMINIO_ID),
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
def list_pending_assignments(
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitAssignmentResponse]:
    """Lista atribuicoes pendentes."""
    assignments = service.list_assignments(
        condominio_id=UUID(CONDOMINIO_ID),
        status=AssignmentStatus.PENDENTE,
    )
    return [DocumentKitAssignmentResponse.model_validate(a) for a in assignments]


@router.get("/assignments/overdue", response_model=List[DocumentKitAssignmentResponse])
def list_overdue_assignments(
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitAssignmentResponse]:
    """Lista atribuicoes vencidas."""
    assignments = service.list_assignments(
        condominio_id=UUID(CONDOMINIO_ID),
        vencidos=True,
    )
    return [DocumentKitAssignmentResponse.model_validate(a) for a in assignments]


@router.get("/assignments/{assignment_id}", response_model=DocumentKitAssignmentResponse)
def get_assignment(
    assignment_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Busca atribuicao por ID."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.put("/assignments/{assignment_id}", response_model=DocumentKitAssignmentResponse)
def update_assignment(
    assignment_id: UUID,
    data: DocumentKitAssignmentUpdate,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Atualiza atribuicao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = service.update_assignment(assignment, data)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/start", response_model=DocumentKitAssignmentResponse)
def start_assignment(
    assignment_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Inicia atribuicao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = service.start_assignment(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/approve", response_model=DocumentKitAssignmentResponse)
def approve_assignment(
    assignment_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Aprova atribuicao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = service.approve_assignment(assignment, UUID(USER_ID))
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/reject", response_model=DocumentKitAssignmentResponse)
def reject_assignment(
    assignment_id: UUID,
    motivo: str = Query(..., min_length=1),
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Reprova atribuicao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = service.reject_assignment(assignment, motivo)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/complete", response_model=DocumentKitAssignmentResponse)
def complete_assignment(
    assignment_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Completa atribuicao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = service.complete_assignment(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/cancel", response_model=DocumentKitAssignmentResponse)
def cancel_assignment(
    assignment_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Cancela atribuicao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = service.cancel_assignment(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


@router.post("/assignments/{assignment_id}/notify", response_model=DocumentKitAssignmentResponse)
def notify_assignment(
    assignment_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitAssignmentResponse:
    """Envia notificacao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    assignment = service.send_notification(assignment)
    return DocumentKitAssignmentResponse.model_validate(assignment)


# === Item Status Endpoints ===


@router.get(
    "/assignments/{assignment_id}/statuses",
    response_model=List[DocumentKitItemStatusResponse],
)
def list_item_statuses(
    assignment_id: UUID,
    item_status: Optional[ItemStatusEnum] = Query(None, alias="status"),
    service: DocumentKitService = Depends(get_service),
) -> List[DocumentKitItemStatusResponse]:
    """Lista status de itens de uma atribuicao."""
    statuses = service.list_assignment_statuses(
        assignment_id, UUID(CONDOMINIO_ID), item_status
    )
    return [DocumentKitItemStatusResponse.model_validate(s) for s in statuses]


@router.get("/item-statuses/{status_id}", response_model=DocumentKitItemStatusResponse)
def get_item_status(
    status_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Busca status de item."""
    item_status = service.get_item_status(status_id, UUID(CONDOMINIO_ID))
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post("/item-statuses/{status_id}/submit", response_model=DocumentKitItemStatusResponse)
def submit_document(
    status_id: UUID,
    arquivo_url: str = Query(...),
    arquivo_nome: str = Query(...),
    arquivo_tamanho: int = Query(..., ge=0),
    arquivo_tipo: str = Query(...),
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Submete documento."""
    item_status = service.get_item_status(status_id, UUID(CONDOMINIO_ID))
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = service.submit_document(
        item_status, arquivo_url, arquivo_nome, arquivo_tamanho, arquivo_tipo, UUID(USER_ID)
    )
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post("/item-statuses/{status_id}/analyze", response_model=DocumentKitItemStatusResponse)
def analyze_document(
    status_id: UUID,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Marca documento como em analise."""
    item_status = service.get_item_status(status_id, UUID(CONDOMINIO_ID))
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = service.analyze_document(item_status)
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post("/item-statuses/{status_id}/approve", response_model=DocumentKitItemStatusResponse)
def approve_document(
    status_id: UUID,
    observacoes: Optional[str] = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Aprova documento."""
    item_status = service.get_item_status(status_id, UUID(CONDOMINIO_ID))
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = service.approve_document(item_status, UUID(USER_ID), observacoes)
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post("/item-statuses/{status_id}/reject", response_model=DocumentKitItemStatusResponse)
def reject_document(
    status_id: UUID,
    motivo: str = Query(..., min_length=1),
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Reprova documento."""
    item_status = service.get_item_status(status_id, UUID(CONDOMINIO_ID))
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = service.reject_document(item_status, UUID(USER_ID), motivo)
    return DocumentKitItemStatusResponse.model_validate(item_status)


@router.post(
    "/item-statuses/{status_id}/not-applicable",
    response_model=DocumentKitItemStatusResponse,
)
def mark_not_applicable(
    status_id: UUID,
    motivo: Optional[str] = None,
    service: DocumentKitService = Depends(get_service),
) -> DocumentKitItemStatusResponse:
    """Marca item como nao aplicavel."""
    item_status = service.get_item_status(status_id, UUID(CONDOMINIO_ID))
    if not item_status:
        raise HTTPException(status_code=404, detail="Status nao encontrado")
    item_status = service.mark_not_applicable(item_status, motivo)
    return DocumentKitItemStatusResponse.model_validate(item_status)


# === AI Endpoints ===


@router.get("/ai/suggest", response_model=List[KitSuggestionResponse])
def suggest_kits(
    entity_type: EntityType,
    cargo: Optional[str] = None,
    departamento: Optional[str] = None,
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> List[KitSuggestionResponse]:
    """Sugere kits para uma entidade."""
    entity_data = {
        "cargo": cargo or "",
        "departamento": departamento or "",
    }
    suggestions = ai_service.suggest_kits_for_entity(
        UUID(CONDOMINIO_ID), entity_type, entity_data
    )
    return [KitSuggestionResponse(**s) for s in suggestions]


@router.get("/ai/compliance/{entity_type}/{entity_id}")
def analyze_compliance(
    entity_type: EntityType,
    entity_id: UUID,
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> dict:
    """Analisa conformidade de uma entidade."""
    return ai_service.analyze_compliance_risk(
        UUID(CONDOMINIO_ID), entity_type, entity_id
    )


@router.get("/ai/predict/{assignment_id}")
def predict_completion(
    assignment_id: UUID,
    service: DocumentKitService = Depends(get_service),
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> dict:
    """Preve data de conclusao."""
    assignment = service.get_assignment(assignment_id, UUID(CONDOMINIO_ID))
    if not assignment:
        raise HTTPException(status_code=404, detail="Atribuicao nao encontrada")
    return ai_service.predict_completion_date(assignment)


@router.get("/ai/priorities", response_model=List[dict])
def get_priorities(
    limit: int = Query(10, ge=1, le=50),
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> List[dict]:
    """Retorna atribuicoes prioritarias."""
    return ai_service.get_priority_assignments(UUID(CONDOMINIO_ID), limit)


@router.get("/ai/usage")
def analyze_usage(
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> dict:
    """Analisa uso dos kits."""
    return ai_service.analyze_kit_usage(UUID(CONDOMINIO_ID))


@router.get("/ai/expiring", response_model=List[dict])
def get_expiring_documents(
    days_ahead: int = Query(30, ge=1, le=365),
    ai_service: DocumentKitAIService = Depends(get_ai_service),
) -> List[dict]:
    """Lista documentos proximos do vencimento."""
    return ai_service.get_expiring_documents(UUID(CONDOMINIO_ID), days_ahead)
