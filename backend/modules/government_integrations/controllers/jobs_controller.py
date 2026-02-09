"""
Controller para gerenciamento de Jobs de Sincronizacao Governamental.

Endpoints:
- POST /jobs/registrar-todos - Registra todos os jobs para o tenant
- GET /jobs - Lista jobs do tenant
- GET /jobs/status - Status geral da sincronizacao
- POST /jobs/{tipo}/executar - Executa job imediatamente
- PATCH /jobs/{id} - Atualiza configuracao do job
- POST /jobs/{tipo}/pausar - Pausa job
- POST /jobs/{tipo}/retomar - Retoma job pausado
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db
from modules.government_integrations.jobs import (
    SYNC_JOBS_CONFIG,
    GovSyncJobManager,
    SyncJobType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Government Sync Jobs"])


# =========================================================================
# SCHEMAS
# =========================================================================


class JobRegistroResponse(BaseModel):
    """Resposta do registro de jobs."""

    sucesso: list[str]
    erros: list[dict]
    total: int


class JobInfo(BaseModel):
    """Informacoes de um job."""

    id: str
    nome: str
    tipo: str
    cron: str
    status: str
    ultima_execucao: str | None
    proxima_execucao: str | None
    total_execucoes: int = 0
    falhas: int = 0
    tags: list[str] = []


class JobListResponse(BaseModel):
    """Lista de jobs."""

    jobs: list[JobInfo]
    total: int


class JobStatusResponse(BaseModel):
    """Status da sincronizacao."""

    federal: list[dict]
    estadual: list[dict]
    municipal: list[dict]
    resumo: dict


class JobUpdateRequest(BaseModel):
    """Requisicao de atualizacao de job."""

    cron_expression: str | None = Field(None, description="Nova expressao cron")
    ativo: bool | None = Field(None, description="Ativar/desativar job")
    prioridade: int | None = Field(None, ge=1, le=10, description="Prioridade (1-10)")


class JobExecResponse(BaseModel):
    """Resposta de execucao de job."""

    sucesso: bool
    mensagem: str
    job_id: str | None = None


class JobConfigInfo(BaseModel):
    """Configuracao disponivel de job."""

    tipo: str
    nome: str
    descricao: str
    cron_padrao: str
    prioridade: int
    tags: list[str]


# =========================================================================
# ENDPOINTS
# =========================================================================


@router.get("/configuracoes", response_model=list[JobConfigInfo])
async def listar_configuracoes_disponiveis():
    """
    Lista todas as configuracoes de jobs disponiveis.

    Retorna os tipos de sincronizacao que podem ser configurados.
    """
    return [
        JobConfigInfo(
            tipo=config.job_type.value,
            nome=config.nome,
            descricao=config.descricao,
            cron_padrao=config.cron_expression,
            prioridade=config.prioridade,
            tags=config.tags,
        )
        for config in SYNC_JOBS_CONFIG.values()
    ]


@router.post("/registrar-todos", response_model=JobRegistroResponse)
async def registrar_todos_jobs(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db),
):
    """
    Registra todos os jobs de sincronizacao para o tenant.

    Cria as tarefas agendadas no scheduler para todos os servicos
    governamentais (NF-e, eSocial, FGTS, etc).
    """
    try:
        # Obter scheduler service
        from modules.scheduler.services.scheduler_service import SchedulerService

        scheduler = SchedulerService(db)
        manager = GovSyncJobManager(db, scheduler)

        resultado = manager.registrar_todos_jobs(tenant_id)

        return JobRegistroResponse(
            sucesso=resultado["sucesso"],
            erros=resultado["erros"],
            total=resultado["total"],
        )

    except Exception as e:
        logger.error(f"Erro registrando jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar jobs: {str(e)}",
        )


@router.get("", response_model=JobListResponse)
async def listar_jobs(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db),
):
    """
    Lista todos os jobs de sincronizacao do tenant.

    Retorna informacoes sobre status, ultima e proxima execucao.
    """
    try:
        from modules.scheduler.services.scheduler_service import SchedulerService

        scheduler = SchedulerService(db)
        manager = GovSyncJobManager(db, scheduler)

        jobs = manager.listar_jobs(tenant_id)

        return JobListResponse(
            jobs=[
                JobInfo(
                    id=job["id"],
                    nome=job["nome"],
                    tipo=_extrair_tipo_job(job),
                    cron=job["cron"],
                    status=job["status"],
                    ultima_execucao=job["ultima_execucao"],
                    proxima_execucao=job["proxima_execucao"],
                    total_execucoes=job.get("total_execucoes", 0),
                    falhas=job.get("falhas", 0),
                    tags=job.get("tags", []),
                )
                for job in jobs
            ],
            total=len(jobs),
        )

    except Exception as e:
        logger.error(f"Erro listando jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar jobs: {str(e)}",
        )


@router.get("/status", response_model=JobStatusResponse)
async def obter_status_sincronizacao(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db),
):
    """
    Obtem status geral da sincronizacao governamental.

    Agrupa jobs por categoria (federal, estadual, municipal) e
    retorna resumo com totais.
    """
    try:
        from modules.scheduler.services.scheduler_service import SchedulerService

        scheduler = SchedulerService(db)
        manager = GovSyncJobManager(db, scheduler)

        status_info = manager.obter_status_sincronizacao(tenant_id)

        return JobStatusResponse(
            federal=status_info["federal"],
            estadual=status_info["estadual"],
            municipal=status_info["municipal"],
            resumo=status_info["resumo"],
        )

    except Exception as e:
        logger.error(f"Erro obtendo status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}",
        )


@router.post("/{tipo}/executar", response_model=JobExecResponse)
async def executar_job_agora(
    tipo: SyncJobType,
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db),
):
    """
    Executa um job de sincronizacao imediatamente.

    Enfileira o job para execucao fora do agendamento normal.
    Util para sincronizacoes manuais ou testes.
    """
    try:
        from modules.scheduler.services.scheduler_service import SchedulerService

        scheduler = SchedulerService(db)
        manager = GovSyncJobManager(db, scheduler)

        resultado = manager.executar_job_agora(tenant_id, tipo)

        if not resultado["sucesso"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado["erro"],
            )

        return JobExecResponse(
            sucesso=True,
            mensagem=resultado["mensagem"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro executando job {tipo}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar job: {str(e)}",
        )


@router.patch("/{job_id}", response_model=JobExecResponse)
async def atualizar_job(
    job_id: UUID,
    dados: JobUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Atualiza configuracao de um job.

    Permite alterar expressao cron, status ativo/inativo e prioridade.
    """
    try:
        from modules.scheduler.services.scheduler_service import SchedulerService

        scheduler = SchedulerService(db)
        manager = GovSyncJobManager(db, scheduler)

        resultado = manager.atualizar_job(
            job_id=job_id,
            cron_expression=dados.cron_expression,
            ativo=dados.ativo,
            prioridade=dados.prioridade,
        )

        if not resultado["sucesso"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=resultado["erro"],
            )

        return JobExecResponse(
            sucesso=True,
            mensagem=resultado["mensagem"],
            job_id=str(job_id),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro atualizando job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar job: {str(e)}",
        )


@router.post("/{tipo}/pausar", response_model=JobExecResponse)
async def pausar_job(
    tipo: SyncJobType,
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db),
):
    """
    Pausa um job de sincronizacao.

    O job nao sera executado ate ser retomado.
    """
    try:
        from modules.scheduler.services.scheduler_service import SchedulerService

        scheduler = SchedulerService(db)
        manager = GovSyncJobManager(db, scheduler)

        # Buscar job
        job_id = manager._buscar_job_existente(tenant_id, tipo)
        if not job_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {tipo.value} nao encontrado",
            )

        resultado = manager.atualizar_job(job_id, ativo=False)

        return JobExecResponse(
            sucesso=resultado["sucesso"],
            mensagem=f"Job {tipo.value} pausado",
            job_id=str(job_id),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro pausando job {tipo}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao pausar job: {str(e)}",
        )


@router.post("/{tipo}/retomar", response_model=JobExecResponse)
async def retomar_job(
    tipo: SyncJobType,
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db),
):
    """
    Retoma um job de sincronizacao pausado.
    """
    try:
        from modules.scheduler.services.scheduler_service import SchedulerService

        scheduler = SchedulerService(db)
        manager = GovSyncJobManager(db, scheduler)

        # Buscar job
        job_id = manager._buscar_job_existente(tenant_id, tipo)
        if not job_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {tipo.value} nao encontrado",
            )

        resultado = manager.atualizar_job(job_id, ativo=True)

        return JobExecResponse(
            sucesso=resultado["sucesso"],
            mensagem=f"Job {tipo.value} retomado",
            job_id=str(job_id),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro retomando job {tipo}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao retomar job: {str(e)}",
        )


# =========================================================================
# HELPERS
# =========================================================================


def _extrair_tipo_job(job: dict) -> str:
    """Extrai tipo do job a partir das tags ou nome."""
    nome = job.get("nome", "").lower()

    for job_type in SyncJobType:
        if job_type.value in nome or job_type.value.replace("_", " ") in nome:
            return job_type.value

    return "desconhecido"
