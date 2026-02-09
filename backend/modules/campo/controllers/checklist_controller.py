"""
Controller para Checklist.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.campo.models.checklist import TipoServico
from modules.campo.schemas.checklist import (
    ChecklistComItens,
    ChecklistConcluirRequest,
    ChecklistIniciarRequest,
    ChecklistItemCreate,
    ChecklistItemRead,
    ChecklistItemUpdate,
    ChecklistPreenchidoCompleto,
    ChecklistPreenchidoRead,
    ChecklistResponderRequest,
    ChecklistTemplateCreate,
    ChecklistTemplateListItem,
    ChecklistTemplateRead,
    ChecklistTemplateUpdate,
    ReordenarItensRequest,
    TemplateFiltro,
    TemplatePaginatedResponse,
    ValidacaoResult,
)
from modules.campo.services.checklist_service import ChecklistService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_db)) -> ChecklistService:
    """Dependency para obter service."""
    return ChecklistService(db)


# =============================================================================
# TEMPLATE
# =============================================================================


@router.post("/templates", response_model=ChecklistTemplateRead, status_code=status.HTTP_201_CREATED)
async def criar_template(
    data: ChecklistTemplateCreate,
    service: ChecklistService = Depends(get_service),
):
    """Cria um novo template de checklist."""
    template = await service.criar_template(data)
    return ChecklistTemplateRead.model_validate(template)


@router.get("/templates", response_model=TemplatePaginatedResponse)
async def listar_templates(
    tipo_servico: TipoServico | None = None,
    categoria_equipamento: str | None = None,
    is_obrigatorio: bool | None = None,
    is_ativo: bool | None = True,
    busca: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: ChecklistService = Depends(get_service),
):
    """Lista templates com filtros e paginacao."""
    filtro = TemplateFiltro(
        tipo_servico=tipo_servico,
        categoria_equipamento=categoria_equipamento,
        is_obrigatorio=is_obrigatorio,
        is_ativo=is_ativo,
        busca=busca,
    )
    return await service.listar_templates(filtro, page, page_size)


@router.get("/templates/tipo/{tipo_servico}", response_model=list[ChecklistTemplateListItem])
async def listar_templates_por_tipo(
    tipo_servico: TipoServico,
    service: ChecklistService = Depends(get_service),
):
    """Lista templates ativos para um tipo de servico."""
    templates = await service.listar_templates_por_tipo(tipo_servico)
    return [ChecklistTemplateListItem.model_validate(t) for t in templates]


@router.get("/templates/{template_id}", response_model=ChecklistComItens)
async def obter_template(
    template_id: UUID,
    service: ChecklistService = Depends(get_service),
):
    """Obtem template com seus itens."""
    result = await service.obter_template(template_id)
    if not result:
        raise HTTPException(status_code=404, detail="Template nao encontrado")
    return result


@router.patch("/templates/{template_id}", response_model=ChecklistTemplateRead)
async def atualizar_template(
    template_id: UUID,
    data: ChecklistTemplateUpdate,
    service: ChecklistService = Depends(get_service),
):
    """Atualiza um template."""
    template = await service.atualizar_template(template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template nao encontrado")
    return ChecklistTemplateRead.model_validate(template)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_template(
    template_id: UUID,
    service: ChecklistService = Depends(get_service),
):
    """Exclui um template (soft delete)."""
    success = await service.excluir_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template nao encontrado")


@router.post("/templates/{template_id}/clonar", response_model=ChecklistTemplateRead)
async def clonar_template(
    template_id: UUID,
    novo_nome: str = Query(..., min_length=3),
    service: ChecklistService = Depends(get_service),
):
    """Clona um template existente."""
    template = await service.clonar_template(template_id, novo_nome)
    if not template:
        raise HTTPException(status_code=404, detail="Template nao encontrado")
    return ChecklistTemplateRead.model_validate(template)


# =============================================================================
# ITENS
# =============================================================================


@router.post("/itens", response_model=ChecklistItemRead, status_code=status.HTTP_201_CREATED)
async def adicionar_item(
    data: ChecklistItemCreate,
    service: ChecklistService = Depends(get_service),
):
    """Adiciona item a um template."""
    item = await service.adicionar_item(data)
    return ChecklistItemRead.model_validate(item)


@router.get("/itens/{item_id}", response_model=ChecklistItemRead)
async def obter_item(
    item_id: UUID,
    service: ChecklistService = Depends(get_service),
):
    """Obtem item por ID."""
    item = await service.obter_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return ChecklistItemRead.model_validate(item)


@router.patch("/itens/{item_id}", response_model=ChecklistItemRead)
async def atualizar_item(
    item_id: UUID,
    data: ChecklistItemUpdate,
    service: ChecklistService = Depends(get_service),
):
    """Atualiza um item."""
    item = await service.atualizar_item(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return ChecklistItemRead.model_validate(item)


@router.delete("/itens/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_item(
    item_id: UUID,
    service: ChecklistService = Depends(get_service),
):
    """Exclui um item (soft delete)."""
    success = await service.excluir_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item nao encontrado")


@router.get("/templates/{template_id}/itens", response_model=list[ChecklistItemRead])
async def listar_itens_template(
    template_id: UUID,
    service: ChecklistService = Depends(get_service),
):
    """Lista itens de um template."""
    itens = await service.listar_itens_template(template_id)
    return [ChecklistItemRead.model_validate(item) for item in itens]


@router.post("/templates/{template_id}/reordenar", status_code=status.HTTP_200_OK)
async def reordenar_itens(
    template_id: UUID,
    data: ReordenarItensRequest,
    service: ChecklistService = Depends(get_service),
):
    """Reordena itens de um template."""
    success = await service.reordenar_itens(template_id, data.nova_ordem)
    if not success:
        raise HTTPException(status_code=400, detail="Erro ao reordenar itens")
    return {"message": "Itens reordenados com sucesso"}


# =============================================================================
# PREENCHIMENTO
# =============================================================================


@router.post(
    "/os/{ordem_servico_id}/iniciar", response_model=ChecklistPreenchidoRead, status_code=status.HTTP_201_CREATED
)
async def iniciar_checklist(
    ordem_servico_id: UUID,
    data: ChecklistIniciarRequest,
    service: ChecklistService = Depends(get_service),
):
    """Inicia preenchimento de checklist para uma OS."""
    try:
        preenchido = await service.iniciar_checklist(
            ordem_servico_id,
            data.template_id,
        )
        return ChecklistPreenchidoRead.model_validate(preenchido)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/os/{ordem_servico_id}/responder", response_model=ValidacaoResult)
async def responder_item(
    ordem_servico_id: UUID,
    data: ChecklistResponderRequest,
    service: ChecklistService = Depends(get_service),
):
    """Responde um item do checklist."""
    try:
        _, validacao = await service.responder_item(
            ordem_servico_id,
            data.item_id,
            data.valor,
            foto_url=data.foto_url,
            fotos_urls=data.fotos_urls,
            assinatura_url=data.assinatura_url,
            latitude=data.latitude,
            longitude=data.longitude,
            observacao=data.observacao,
        )
        return validacao
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/os/{ordem_servico_id}/concluir", response_model=ChecklistPreenchidoRead)
async def concluir_checklist(
    ordem_servico_id: UUID,
    data: ChecklistConcluirRequest,
    service: ChecklistService = Depends(get_service),
):
    """Conclui preenchimento do checklist."""
    try:
        preenchido = await service.concluir_checklist(
            ordem_servico_id,
            data.observacoes_finais,
        )
        return ChecklistPreenchidoRead.model_validate(preenchido)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/os/{ordem_servico_id}", response_model=ChecklistPreenchidoCompleto)
async def obter_checklist_os(
    ordem_servico_id: UUID,
    service: ChecklistService = Depends(get_service),
):
    """Obtem checklist completo de uma OS."""
    result = await service.obter_checklist_completo(ordem_servico_id)
    if not result:
        raise HTTPException(status_code=404, detail="Checklist nao encontrado para esta OS")
    return result


@router.get("/os/{ordem_servico_id}/progresso", response_model=ChecklistPreenchidoRead)
async def obter_progresso_checklist(
    ordem_servico_id: UUID,
    service: ChecklistService = Depends(get_service),
):
    """Obtem progresso do checklist de uma OS."""
    result = await service.obter_progresso_checklist(ordem_servico_id)
    if not result:
        raise HTTPException(status_code=404, detail="Checklist nao encontrado para esta OS")
    return result
