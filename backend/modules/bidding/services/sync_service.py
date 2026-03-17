"""
Service de Sincronizacao — Licitacoes
======================================
Gerencia sincronizacao de dados com portais de licitacao,
controlando jobs de sync, status e historico.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class SyncJobStatus:
    """Status possiveis de um job de sincronizacao."""

    PENDENTE = "pendente"
    EXECUTANDO = "executando"
    CONCLUIDO = "concluido"
    ERRO = "erro"
    CANCELADO = "cancelado"


class SyncFilters:
    """Filtros para listagem de jobs de sincronizacao."""

    def __init__(
        self,
        portal: str | None = None,
        status: str | None = None,
        data_inicial: str | None = None,
        data_final: str | None = None,
        page: int = 1,
        size: int = 20,
    ):
        self.portal = portal
        self.status = status
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.page = page
        self.size = size


# Portais disponiveis para sincronizacao
AVAILABLE_PORTALS = {
    "pncp": {
        "nome": "Portal Nacional de Contratacoes Publicas",
        "tipo": "federal",
        "url": "https://pncp.gov.br",
    },
    "comprasnet": {
        "nome": "ComprasNet / Compras.gov.br",
        "tipo": "federal",
        "url": "https://www.gov.br/compras",
    },
    "licitacoes_e": {
        "nome": "Licitacoes-e (Banco do Brasil)",
        "tipo": "banco",
        "url": "https://www.licitacoes-e.com.br",
    },
    "ecompras_am": {
        "nome": "e-Compras Amazonas",
        "tipo": "estadual",
        "url": "https://www.e-compras.am.gov.br",
    },
    "bll": {
        "nome": "BLL Compras",
        "tipo": "privado",
        "url": "https://bllcompras.com",
    },
}


class SyncService:
    """Service para operacoes de sincronizacao com portais de licitacao."""

    def __init__(self, db=None):
        """
        Inicializa o service.

        Args:
            db: Sessao de banco de dados (opcional)
        """
        self.db = db
        self._jobs: dict[str, dict[str, Any]] = {}

    async def sync_portal(self, portal_name: str, force: bool = False) -> dict[str, Any]:
        """
        Inicia sincronizacao com um portal.

        Args:
            portal_name: Nome do portal (pncp, comprasnet, licitacoes_e, ecompras_am, bll)
            force: Forcar sync mesmo se existir job recente

        Returns:
            Dados do job de sincronizacao criado

        Raises:
            ValueError: Se portal invalido
        """
        if portal_name not in AVAILABLE_PORTALS:
            raise ValueError(f"Portal invalido: {portal_name}. Disponiveis: {list(AVAILABLE_PORTALS.keys())}")

        # Verificar se ja existe job executando para este portal
        if not force:
            for job in self._jobs.values():
                if job["portal"] == portal_name and job["status"] == SyncJobStatus.EXECUTANDO:
                    logger.warning("Ja existe sincronizacao em andamento para portal %s", portal_name)
                    return job

        job_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        portal_info = AVAILABLE_PORTALS[portal_name]

        sync_job = {
            "id": job_id,
            "portal": portal_name,
            "portal_nome": portal_info["nome"],
            "portal_tipo": portal_info["tipo"],
            "status": SyncJobStatus.EXECUTANDO,
            "registros_encontrados": 0,
            "registros_novos": 0,
            "registros_atualizados": 0,
            "erros": [],
            "iniciado_em": now,
            "concluido_em": None,
            "duracao_ms": None,
        }

        self._jobs[job_id] = sync_job
        logger.info("Sincronizacao iniciada: job=%s, portal=%s", job_id, portal_name)

        # TODO: Disparar task Celery para sincronizacao real
        # from modules.bidding.tasks import sync_portal_task
        # sync_portal_task.delay(job_id, portal_name)

        return sync_job

    async def get_sync_status(self, job_id: str) -> dict[str, Any] | None:
        """
        Consulta status de um job de sincronizacao.

        Args:
            job_id: ID do job

        Returns:
            Dados do job com status atualizado ou None
        """
        job = self._jobs.get(job_id)
        if not job:
            logger.warning("Job de sincronizacao nao encontrado: %s", job_id)
            return None
        return job

    async def list_sync_jobs(self, filters: SyncFilters | None = None) -> list[dict[str, Any]]:
        """
        Lista jobs de sincronizacao com filtros.

        Args:
            filters: Filtros opcionais (portal, status, datas, paginacao)

        Returns:
            Lista de jobs de sincronizacao
        """
        results = list(self._jobs.values())

        if filters:
            if filters.portal:
                results = [j for j in results if j.get("portal") == filters.portal]
            if filters.status:
                results = [j for j in results if j.get("status") == filters.status]

            # Paginacao
            start = (filters.page - 1) * filters.size
            end = start + filters.size
            results = results[start:end]

        # Ordenar por data de inicio (mais recente primeiro)
        results.sort(key=lambda x: x.get("iniciado_em", ""), reverse=True)
        return results

    async def get_last_sync(self, portal: str) -> dict[str, Any] | None:
        """
        Retorna o ultimo job de sincronizacao de um portal.

        Args:
            portal: Nome do portal

        Returns:
            Ultimo job de sincronizacao ou None
        """
        if portal not in AVAILABLE_PORTALS:
            raise ValueError(f"Portal invalido: {portal}")

        portal_jobs = [j for j in self._jobs.values() if j.get("portal") == portal]
        if not portal_jobs:
            logger.info("Nenhuma sincronizacao encontrada para portal %s", portal)
            return None

        portal_jobs.sort(key=lambda x: x.get("iniciado_em", ""), reverse=True)
        return portal_jobs[0]

    async def complete_sync_job(
        self,
        job_id: str,
        registros_encontrados: int = 0,
        registros_novos: int = 0,
        registros_atualizados: int = 0,
        erros: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """
        Finaliza um job de sincronizacao com os resultados.

        Args:
            job_id: ID do job
            registros_encontrados: Total de registros encontrados no portal
            registros_novos: Registros novos inseridos
            registros_atualizados: Registros existentes atualizados
            erros: Lista de erros durante a sincronizacao

        Returns:
            Job atualizado ou None
        """
        job = self._jobs.get(job_id)
        if not job:
            return None

        now = datetime.utcnow().isoformat()
        inicio = datetime.fromisoformat(job["iniciado_em"])
        duracao = (datetime.utcnow() - inicio).total_seconds() * 1000

        job["status"] = SyncJobStatus.CONCLUIDO if not erros else SyncJobStatus.ERRO
        job["registros_encontrados"] = registros_encontrados
        job["registros_novos"] = registros_novos
        job["registros_atualizados"] = registros_atualizados
        job["erros"] = erros or []
        job["concluido_em"] = now
        job["duracao_ms"] = round(duracao)

        logger.info(
            "Sincronizacao concluida: job=%s, encontrados=%d, novos=%d, atualizados=%d",
            job_id,
            registros_encontrados,
            registros_novos,
            registros_atualizados,
        )
        return job
