"""
Controller para Ordem de Servico.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.campo.models.ordem_servico import OrigemOS, PrioridadeOS, StatusOS, TipoOS
from modules.campo.schemas.ordem_servico import (
    OrdemServicoCreate,
    OrdemServicoListItem,
    OrdemServicoRead,
    OrdemServicoUpdate,
    OSAgendarRequest,
    OSAssinaturaRequest,
    OSAvaliacaoRequest,
    OSCancelarRequest,
    OSCheckinRequest,
    OSCheckoutRequest,
    OSConcluirRequest,
    OSDashboardStats,
    OSFiltro,
    OSFotoRequest,
    OSPaginatedResponse,
    OSReagendarRequest,
)
from modules.campo.services.ordem_servico_service import OrdemServicoService

router = APIRouter()


def get_service(db: AsyncSession = Depends(get_db)) -> OrdemServicoService:
    """Dependency para obter service."""
    return OrdemServicoService(db)


# =============================================================================
# CRUD
# =============================================================================


@router.post("/", response_model=OrdemServicoRead, status_code=status.HTTP_201_CREATED)
async def criar_os(
    data: OrdemServicoCreate,
    service: OrdemServicoService = Depends(get_service),
):
    """Cria uma nova Ordem de Servico."""
    os = await service.criar_os(data)
    return OrdemServicoRead.model_validate(os)


@router.get("/", response_model=OSPaginatedResponse)
async def listar_os(
    tipo: TipoOS | None = None,
    status_os: StatusOS | None = Query(None, alias="status"),
    prioridade: PrioridadeOS | None = None,
    origem: OrigemOS | None = None,
    cliente_id: UUID | None = None,
    tecnico_id: UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    cidade: str | None = None,
    estado: str | None = None,
    sla_vencido: bool | None = None,
    busca: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: OrdemServicoService = Depends(get_service),
):
    """Lista Ordens de Servico com filtros e paginacao."""
    filtro = OSFiltro(
        tipo=tipo,
        status=status_os,
        prioridade=prioridade,
        origem=origem,
        cliente_id=cliente_id,
        tecnico_id=tecnico_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        cidade=cidade,
        estado=estado,
        sla_vencido=sla_vencido,
        busca=busca,
    )
    return await service.listar_os(filtro, page, page_size)


@router.get("/atrasadas", response_model=list[OrdemServicoListItem])
async def listar_os_atrasadas(
    service: OrdemServicoService = Depends(get_service),
):
    """Lista OS com SLA vencido."""
    os_list = await service.listar_os_atrasadas()
    return [OrdemServicoListItem.model_validate(os) for os in os_list]


@router.get("/tecnico/{tecnico_id}", response_model=list[OrdemServicoListItem])
async def listar_os_tecnico(
    tecnico_id: UUID,
    data: date | None = None,
    apenas_abertas: bool = False,
    service: OrdemServicoService = Depends(get_service),
):
    """Lista OS de um tecnico."""
    os_list = await service.listar_os_tecnico(tecnico_id, data, apenas_abertas)
    return [OrdemServicoListItem.model_validate(os) for os in os_list]


@router.get("/cliente/{cliente_id}", response_model=list[OrdemServicoListItem])
async def listar_os_cliente(
    cliente_id: UUID,
    service: OrdemServicoService = Depends(get_service),
):
    """Lista OS de um cliente."""
    os_list = await service.listar_os_cliente(cliente_id)
    return [OrdemServicoListItem.model_validate(os) for os in os_list]


@router.get("/dashboard", response_model=OSDashboardStats)
async def obter_dashboard(
    cliente_id: UUID | None = None,
    tecnico_id: UUID | None = None,
    periodo_dias: int = Query(30, ge=1, le=365),
    service: OrdemServicoService = Depends(get_service),
):
    """Obtem estatisticas para dashboard."""
    return await service.obter_estatisticas(cliente_id, tecnico_id, periodo_dias)


@router.get("/{os_id}", response_model=OrdemServicoRead)
async def obter_os(
    os_id: UUID,
    service: OrdemServicoService = Depends(get_service),
):
    """Obtem detalhes de uma OS."""
    os = await service.obter_os(os_id)
    if not os:
        raise HTTPException(status_code=404, detail="OS nao encontrada")
    return OrdemServicoRead.model_validate(os)


@router.get("/numero/{numero}", response_model=OrdemServicoRead)
async def obter_os_por_numero(
    numero: str,
    service: OrdemServicoService = Depends(get_service),
):
    """Obtem OS por numero."""
    os = await service.obter_os_por_numero(numero)
    if not os:
        raise HTTPException(status_code=404, detail="OS nao encontrada")
    return OrdemServicoRead.model_validate(os)


@router.patch("/{os_id}", response_model=OrdemServicoRead)
async def atualizar_os(
    os_id: UUID,
    data: OrdemServicoUpdate,
    service: OrdemServicoService = Depends(get_service),
):
    """Atualiza uma OS."""
    os = await service.atualizar_os(os_id, data)
    if not os:
        raise HTTPException(status_code=404, detail="OS nao encontrada")
    return OrdemServicoRead.model_validate(os)


@router.delete("/{os_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_os(
    os_id: UUID,
    service: OrdemServicoService = Depends(get_service),
):
    """Exclui uma OS."""
    success = await service.excluir_os(os_id)
    if not success:
        raise HTTPException(status_code=404, detail="OS nao encontrada")


# =============================================================================
# ACOES DO FLUXO
# =============================================================================


@router.post("/{os_id}/agendar", response_model=OrdemServicoRead)
async def agendar_os(
    os_id: UUID,
    data: OSAgendarRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Agenda uma OS."""
    try:
        os = await service.agendar_os(
            os_id,
            data.data_agendada,
            data.horario_inicio_previsto,
            data.horario_fim_previsto,
            data.tecnico_id,
        )
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/iniciar-deslocamento", response_model=OrdemServicoRead)
async def iniciar_deslocamento(
    os_id: UUID,
    service: OrdemServicoService = Depends(get_service),
):
    """Marca inicio do deslocamento."""
    try:
        os = await service.iniciar_deslocamento(os_id)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/checkin", response_model=OrdemServicoRead)
async def fazer_checkin(
    os_id: UUID,
    data: OSCheckinRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Registra check-in no local."""
    try:
        os = await service.fazer_checkin(os_id, data.latitude, data.longitude)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/checkout", response_model=OrdemServicoRead)
async def fazer_checkout(
    os_id: UUID,
    data: OSCheckoutRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Registra check-out do local."""
    try:
        os = await service.fazer_checkout(os_id, data.latitude, data.longitude)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/pausar", response_model=OrdemServicoRead)
async def pausar_os(
    os_id: UUID,
    motivo: str | None = None,
    service: OrdemServicoService = Depends(get_service),
):
    """Pausa uma OS em andamento."""
    try:
        os = await service.pausar_os(os_id, motivo)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/retomar", response_model=OrdemServicoRead)
async def retomar_os(
    os_id: UUID,
    service: OrdemServicoService = Depends(get_service),
):
    """Retoma uma OS pausada."""
    try:
        os = await service.retomar_os(os_id)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/concluir", response_model=OrdemServicoRead)
async def concluir_os(
    os_id: UUID,
    data: OSConcluirRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Conclui uma OS."""
    try:
        os = await service.concluir_os(os_id, data.solucao_aplicada)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/cancelar", response_model=OrdemServicoRead)
async def cancelar_os(
    os_id: UUID,
    data: OSCancelarRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Cancela uma OS."""
    try:
        cancelado_por = None
        os = await service.cancelar_os(os_id, data.motivo, cancelado_por)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/reagendar", response_model=OrdemServicoRead)
async def reagendar_os(
    os_id: UUID,
    data: OSReagendarRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Reagenda uma OS."""
    try:
        os = await service.reagendar_os(os_id, data.nova_data, data.motivo)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# AVALIACAO E ASSINATURA
# =============================================================================


@router.post("/{os_id}/avaliacao", response_model=OrdemServicoRead)
async def registrar_avaliacao(
    os_id: UUID,
    data: OSAvaliacaoRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Registra avaliacao do cliente."""
    try:
        os = await service.registrar_avaliacao(os_id, data.nota, data.comentario)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{os_id}/assinatura", response_model=OrdemServicoRead)
async def registrar_assinatura(
    os_id: UUID,
    data: OSAssinaturaRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Registra assinatura do cliente."""
    os = await service.registrar_assinatura(os_id, data.url, data.nome, data.documento)
    if not os:
        raise HTTPException(status_code=404, detail="OS nao encontrada")
    return OrdemServicoRead.model_validate(os)


@router.post("/{os_id}/foto", response_model=OrdemServicoRead)
async def adicionar_foto(
    os_id: UUID,
    data: OSFotoRequest,
    service: OrdemServicoService = Depends(get_service),
):
    """Adiciona foto a OS."""
    try:
        os = await service.adicionar_foto(os_id, data.tipo, data.url, data.descricao)
        if not os:
            raise HTTPException(status_code=404, detail="OS nao encontrada")
        return OrdemServicoRead.model_validate(os)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
