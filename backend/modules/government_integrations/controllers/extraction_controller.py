"""
Controller de Extração de Dados Governamentais.

Endpoints para iniciar e gerenciar extrações.
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from ..extractors.orchestrator import (
    ConfiguracaoExtracao,
    TipoServico,
    get_orchestrator,
)
from ..jobs.sync_tasks import (
    sincronizar_esocial,
    sincronizar_fgts,
    sincronizar_nfe,
    sincronizar_nfse,
    sincronizar_rfb,
    sincronizar_todos,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extracao", tags=["Extração Governamental"])


# ============================================================================
# Schemas
# ============================================================================


class IniciarExtracaoRequest(BaseModel):
    """Requisição para iniciar extração."""

    servicos: list[str] | None = Field(
        None, description="Serviços a sincronizar. Se vazio, sincroniza todos.", example=["sefaz_nfe", "esocial"]
    )
    cnpjs: list[str] | None = Field(
        None, description="CNPJs específicos. Se vazio, usa todos do tenant.", example=["12345678000100"]
    )
    ufs: list[str] | None = Field(None, description="UFs para consulta SEFAZ", example=["AM", "SP"])
    data_inicio: datetime | None = Field(None, description="Data inicial do período")
    data_fim: datetime | None = Field(None, description="Data final do período")
    dias: int = Field(30, ge=1, le=365, description="Dias para trás (se data_inicio não informada)")
    modo_incremental: bool = Field(True, description="Se True, busca apenas novos documentos")
    executar_async: bool = Field(True, description="Se True, executa em background via Celery")

    @field_validator("servicos")
    @classmethod
    def validar_servicos(cls, v):
        if v:
            validos = [t.value for t in TipoServico]
            for s in v:
                if s not in validos:
                    raise ValueError(f"Serviço inválido: {s}. Válidos: {validos}")
        return v


class ExtracaoResponse(BaseModel):
    """Resposta de extração."""

    id: str
    status: str
    servicos: list[str]
    iniciado_em: datetime
    modo: str
    mensagem: str


class StatusExtracaoResponse(BaseModel):
    """Status de uma extração em andamento."""

    id: str
    status: str
    progresso: float
    documentos_processados: int
    documentos_novos: int
    documentos_erro: int
    servicos_concluidos: list[str]
    servicos_pendentes: list[str]
    erros: list[str]
    iniciado_em: datetime
    estimativa_conclusao: datetime | None = None


class HistoricoExtracaoResponse(BaseModel):
    """Histórico de extrações."""

    id: str
    tenant_id: str
    servicos: list[str]
    status: str
    documentos_processados: int
    documentos_novos: int
    documentos_erro: int
    iniciado_em: datetime
    finalizado_em: datetime | None
    duracao_segundos: float | None
    usuario_id: str | None


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/iniciar", response_model=ExtracaoResponse)
async def iniciar_extracao(
    tenant_id: str,
    request: IniciarExtracaoRequest,
    background_tasks: BackgroundTasks,
):
    """
    Inicia extração de dados governamentais.

    Pode ser executada de forma síncrona (aguarda conclusão) ou
    assíncrona (retorna imediatamente e processa em background).
    """
    logger.info(f"Iniciando extração para tenant {tenant_id}")

    try:
        tid = UUID(tenant_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de tenant inválido")

    # Determinar período
    data_fim = request.data_fim or datetime.utcnow()
    data_inicio = request.data_inicio or (data_fim - timedelta(days=request.dias))

    # Mapear serviços
    if request.servicos:
        servicos = [TipoServico(s) for s in request.servicos]
    else:
        servicos = list(TipoServico)

    if request.executar_async:
        # Executar via Celery
        task_ids = []

        if not request.servicos or "sefaz_nfe" in (request.servicos or []):
            task = sincronizar_nfe.delay(tenant_id, request.cnpjs, request.ufs, request.dias)
            task_ids.append(("sefaz_nfe", task.id))

        if not request.servicos or "esocial" in (request.servicos or []):
            task = sincronizar_esocial.delay(tenant_id, request.cnpjs)
            task_ids.append(("esocial", task.id))

        if not request.servicos or "fgts_digital" in (request.servicos or []):
            task = sincronizar_fgts.delay(tenant_id, request.cnpjs)
            task_ids.append(("fgts_digital", task.id))

        if not request.servicos or "nfse_manaus" in (request.servicos or []):
            task = sincronizar_nfse.delay(tenant_id, request.cnpjs, request.dias)
            task_ids.append(("nfse_manaus", task.id))

        if not request.servicos or "receita_federal" in (request.servicos or []):
            if request.cnpjs:
                task = sincronizar_rfb.delay(tenant_id, request.cnpjs)
                task_ids.append(("receita_federal", task.id))

        # Usar o primeiro task_id como referência
        extracao_id = task_ids[0][1] if task_ids else "none"

        return ExtracaoResponse(
            id=extracao_id,
            status="enfileirada",
            servicos=[t[0] for t in task_ids],
            iniciado_em=datetime.utcnow(),
            modo="async",
            mensagem=f"Extração enfileirada. {len(task_ids)} tarefas criadas.",
        )

    else:
        # Executar síncrono
        config = ConfiguracaoExtracao(
            servicos=servicos,
            data_inicio=data_inicio,
            data_fim=data_fim,
            cnpjs=request.cnpjs,
            ufs=request.ufs,
            modo_incremental=request.modo_incremental,
        )

        orchestrator = get_orchestrator()
        resultado = await orchestrator.iniciar_extracao(tid, config)

        return ExtracaoResponse(
            id=resultado.id,
            status=resultado.status,
            servicos=[s.value for s in servicos],
            iniciado_em=resultado.inicio,
            modo="sync",
            mensagem=f"Extração concluída. {resultado.documentos_novos} novos documentos.",
        )


@router.get("/status/{extracao_id}", response_model=StatusExtracaoResponse)
async def obter_status_extracao(extracao_id: str):
    """
    Obtém status de uma extração em andamento.
    """
    # Em produção, consultar status da task Celery e/ou banco
    # from celery.result import AsyncResult
    # result = AsyncResult(extracao_id)

    return StatusExtracaoResponse(
        id=extracao_id,
        status="em_andamento",
        progresso=0.0,
        documentos_processados=0,
        documentos_novos=0,
        documentos_erro=0,
        servicos_concluidos=[],
        servicos_pendentes=[],
        erros=[],
        iniciado_em=datetime.utcnow(),
    )


@router.get("/historico", response_model=list[HistoricoExtracaoResponse])
async def listar_historico_extracoes(
    tenant_id: str,
    limite: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Lista histórico de extrações do tenant.
    """
    # Em produção, buscar do banco
    # SELECT * FROM extracoes WHERE tenant_id = ... ORDER BY ...

    return []


@router.post("/cancelar/{extracao_id}")
async def cancelar_extracao(extracao_id: str):
    """
    Cancela uma extração em andamento.
    """
    # Em produção, revogar task Celery
    # from celery.result import AsyncResult
    # AsyncResult(extracao_id).revoke(terminate=True)

    return {"id": extracao_id, "status": "cancelada", "mensagem": "Solicitação de cancelamento enviada"}


# ============================================================================
# Endpoints de Sincronização Rápida
# ============================================================================


@router.post("/sync/nfe")
async def sincronizar_nfe_rapido(
    tenant_id: str,
    cnpjs: list[str] | None = None,
    ufs: list[str] | None = None,
    dias: int = Query(30, ge=1, le=365),
):
    """
    Sincroniza NF-e de forma rápida (background).
    """
    task = sincronizar_nfe.delay(tenant_id, cnpjs, ufs, dias)

    return {
        "task_id": task.id,
        "servico": "sefaz_nfe",
        "status": "enfileirada",
        "mensagem": "Sincronização de NF-e iniciada",
    }


@router.post("/sync/esocial")
async def sincronizar_esocial_rapido(
    tenant_id: str,
    cnpjs: list[str] | None = None,
    competencia: str | None = None,
):
    """
    Sincroniza eSocial de forma rápida (background).
    """
    task = sincronizar_esocial.delay(tenant_id, cnpjs, competencia)

    return {
        "task_id": task.id,
        "servico": "esocial",
        "status": "enfileirada",
        "mensagem": "Sincronização do eSocial iniciada",
    }


@router.post("/sync/fgts")
async def sincronizar_fgts_rapido(
    tenant_id: str,
    cnpjs: list[str] | None = None,
    competencias: list[str] | None = None,
):
    """
    Sincroniza FGTS Digital de forma rápida (background).
    """
    task = sincronizar_fgts.delay(tenant_id, cnpjs, competencias)

    return {
        "task_id": task.id,
        "servico": "fgts_digital",
        "status": "enfileirada",
        "mensagem": "Sincronização do FGTS Digital iniciada",
    }


@router.post("/sync/nfse")
async def sincronizar_nfse_rapido(
    tenant_id: str,
    cnpjs: list[str] | None = None,
    dias: int = Query(30, ge=1, le=365),
):
    """
    Sincroniza NFS-e de forma rápida (background).
    """
    task = sincronizar_nfse.delay(tenant_id, cnpjs, dias)

    return {
        "task_id": task.id,
        "servico": "nfse_manaus",
        "status": "enfileirada",
        "mensagem": "Sincronização de NFS-e iniciada",
    }


@router.post("/sync/rfb")
async def sincronizar_rfb_rapido(
    tenant_id: str,
    cnpjs: list[str],
):
    """
    Sincroniza dados da Receita Federal (background).
    """
    if not cnpjs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe ao menos um CNPJ")

    task = sincronizar_rfb.delay(tenant_id, cnpjs)

    return {
        "task_id": task.id,
        "servico": "receita_federal",
        "status": "enfileirada",
        "mensagem": "Sincronização da Receita Federal iniciada",
    }


@router.post("/sync/todos")
async def sincronizar_todos_rapido(
    tenant_id: str,
    cnpjs: list[str] | None = None,
    servicos: list[str] | None = None,
):
    """
    Sincroniza todos os serviços governamentais (background).
    """
    task = sincronizar_todos.delay(tenant_id, cnpjs, servicos)

    return {
        "task_id": task.id,
        "servico": "todos",
        "status": "enfileirada",
        "mensagem": "Sincronização completa iniciada",
    }
