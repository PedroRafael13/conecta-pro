"""
Module: Government Sync Jobs
Description: Tarefas agendadas para sincronizacao automatica com servicos governamentais.

Periodicidades configuradas:
- NF-e/NFC-e: A cada 30 minutos
- CT-e/MDF-e: A cada 30 minutos
- eSocial: Diariamente as 06:00
- FGTS Digital: Diariamente as 07:00
- DCTFWeb: Diariamente as 08:00
- EFD-Reinf: Diariamente as 08:30
- SPED Fiscal: Semanalmente (Segunda 03:00)
- SPED Contabil: Mensalmente (Dia 5 as 03:00)
- NFS-e Manaus: A cada 60 minutos
- Receita Federal (CNPJ): Semanalmente

Author: Claude AI + Human Developer
Date: 2026-01-16
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SyncJobType(str, Enum):
    """Tipos de jobs de sincronizacao."""
    NFE_EMITIDAS = "nfe_emitidas"
    NFE_DESTINADAS = "nfe_destinadas"
    CTE = "cte"
    MDFE = "mdfe"
    ESOCIAL = "esocial"
    FGTS_DIGITAL = "fgts_digital"
    DCTFWEB = "dctfweb"
    EFD_REINF = "efd_reinf"
    SPED_FISCAL = "sped_fiscal"
    SPED_CONTABIL = "sped_contabil"
    NFSE_MANAUS = "nfse_manaus"
    NFSE_NACIONAL = "nfse_nacional"
    RECEITA_FEDERAL = "receita_federal"
    SIMPLES_NACIONAL = "simples_nacional"


class SyncJobConfig:
    """Configuracao de um job de sincronizacao."""

    def __init__(
        self,
        job_type: SyncJobType,
        nome: str,
        descricao: str,
        cron_expression: str,
        handler: str,
        handler_module: str,
        prioridade: int = 5,
        timeout_seconds: int = 3600,
        max_retries: int = 3,
        ativo: bool = True,
        tags: Optional[List[str]] = None,
    ):
        self.job_type = job_type
        self.nome = nome
        self.descricao = descricao
        self.cron_expression = cron_expression
        self.handler = handler
        self.handler_module = handler_module
        self.prioridade = prioridade
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.ativo = ativo
        self.tags = tags or []


# Configuracoes padrao dos jobs
SYNC_JOBS_CONFIG: Dict[SyncJobType, SyncJobConfig] = {
    # =========================================================================
    # DOCUMENTOS FISCAIS ESTADUAIS (Alta Frequencia)
    # =========================================================================
    SyncJobType.NFE_EMITIDAS: SyncJobConfig(
        job_type=SyncJobType.NFE_EMITIDAS,
        nome="Sync NF-e Emitidas",
        descricao="Sincroniza NF-e emitidas pela empresa com SEFAZ",
        cron_expression="*/30 * * * *",  # A cada 30 minutos
        handler="sync_nfe_emitidas",
        handler_module="modules.government_integrations.jobs.handlers.nfe_handler",
        prioridade=8,
        timeout_seconds=1800,
        tags=["fiscal", "nfe", "estadual"],
    ),
    SyncJobType.NFE_DESTINADAS: SyncJobConfig(
        job_type=SyncJobType.NFE_DESTINADAS,
        nome="Sync NF-e Destinadas",
        descricao="Sincroniza NF-e destinadas a empresa via DF-e Nacional",
        cron_expression="0 */2 * * *",  # A cada 2 horas
        handler="sync_nfe_destinadas",
        handler_module="modules.government_integrations.jobs.handlers.nfe_handler",
        prioridade=7,
        timeout_seconds=3600,
        tags=["fiscal", "nfe", "dfe", "compras"],
    ),
    SyncJobType.CTE: SyncJobConfig(
        job_type=SyncJobType.CTE,
        nome="Sync CT-e",
        descricao="Sincroniza Conhecimentos de Transporte",
        cron_expression="*/30 * * * *",  # A cada 30 minutos
        handler="sync_cte",
        handler_module="modules.government_integrations.jobs.handlers.cte_handler",
        prioridade=7,
        timeout_seconds=1800,
        tags=["fiscal", "cte", "transporte"],
    ),
    SyncJobType.MDFE: SyncJobConfig(
        job_type=SyncJobType.MDFE,
        nome="Sync MDF-e",
        descricao="Sincroniza Manifestos de Documentos Fiscais",
        cron_expression="*/30 * * * *",  # A cada 30 minutos
        handler="sync_mdfe",
        handler_module="modules.government_integrations.jobs.handlers.mdfe_handler",
        prioridade=7,
        timeout_seconds=1800,
        tags=["fiscal", "mdfe", "transporte"],
    ),

    # =========================================================================
    # OBRIGACOES FEDERAIS (Diarias)
    # =========================================================================
    SyncJobType.ESOCIAL: SyncJobConfig(
        job_type=SyncJobType.ESOCIAL,
        nome="Sync eSocial",
        descricao="Sincroniza eventos do eSocial (status e recibos)",
        cron_expression="0 6 * * *",  # Diariamente as 06:00
        handler="sync_esocial",
        handler_module="modules.government_integrations.jobs.handlers.esocial_handler",
        prioridade=9,
        timeout_seconds=7200,
        max_retries=5,
        tags=["trabalhista", "esocial", "federal"],
    ),
    SyncJobType.FGTS_DIGITAL: SyncJobConfig(
        job_type=SyncJobType.FGTS_DIGITAL,
        nome="Sync FGTS Digital",
        descricao="Sincroniza guias e extratos do FGTS Digital",
        cron_expression="0 7 * * *",  # Diariamente as 07:00
        handler="sync_fgts_digital",
        handler_module="modules.government_integrations.jobs.handlers.fgts_handler",
        prioridade=8,
        timeout_seconds=3600,
        tags=["trabalhista", "fgts", "federal"],
    ),
    SyncJobType.DCTFWEB: SyncJobConfig(
        job_type=SyncJobType.DCTFWEB,
        nome="Sync DCTFWeb",
        descricao="Sincroniza declaracoes e debitos da DCTFWeb",
        cron_expression="0 8 * * *",  # Diariamente as 08:00
        handler="sync_dctfweb",
        handler_module="modules.government_integrations.jobs.handlers.dctfweb_handler",
        prioridade=8,
        timeout_seconds=3600,
        tags=["fiscal", "dctfweb", "federal"],
    ),
    SyncJobType.EFD_REINF: SyncJobConfig(
        job_type=SyncJobType.EFD_REINF,
        nome="Sync EFD-Reinf",
        descricao="Sincroniza eventos e totalizadores do EFD-Reinf",
        cron_expression="30 8 * * *",  # Diariamente as 08:30
        handler="sync_efd_reinf",
        handler_module="modules.government_integrations.jobs.handlers.reinf_handler",
        prioridade=8,
        timeout_seconds=3600,
        tags=["fiscal", "reinf", "federal"],
    ),

    # =========================================================================
    # SPED (Semanal/Mensal)
    # =========================================================================
    SyncJobType.SPED_FISCAL: SyncJobConfig(
        job_type=SyncJobType.SPED_FISCAL,
        nome="Sync SPED Fiscal",
        descricao="Sincroniza escrituracoes e apuracoes SPED ICMS/IPI",
        cron_expression="0 3 * * 1",  # Segunda-feira as 03:00
        handler="sync_sped_fiscal",
        handler_module="modules.government_integrations.jobs.handlers.sped_handler",
        prioridade=6,
        timeout_seconds=7200,
        tags=["contabil", "sped", "icms", "ipi"],
    ),
    SyncJobType.SPED_CONTABIL: SyncJobConfig(
        job_type=SyncJobType.SPED_CONTABIL,
        nome="Sync SPED Contabil",
        descricao="Sincroniza escrituracoes contabeis (ECD)",
        cron_expression="0 3 5 * *",  # Dia 5 de cada mes as 03:00
        handler="sync_sped_contabil",
        handler_module="modules.government_integrations.jobs.handlers.sped_handler",
        prioridade=5,
        timeout_seconds=7200,
        tags=["contabil", "sped", "ecd"],
    ),

    # =========================================================================
    # NFS-e MUNICIPAL
    # =========================================================================
    SyncJobType.NFSE_MANAUS: SyncJobConfig(
        job_type=SyncJobType.NFSE_MANAUS,
        nome="Sync NFS-e Manaus",
        descricao="Sincroniza NFS-e emitidas em Manaus",
        cron_expression="0 * * * *",  # A cada hora
        handler="sync_nfse_manaus",
        handler_module="modules.government_integrations.jobs.handlers.nfse_handler",
        prioridade=7,
        timeout_seconds=1800,
        tags=["fiscal", "nfse", "municipal", "manaus"],
    ),
    SyncJobType.NFSE_NACIONAL: SyncJobConfig(
        job_type=SyncJobType.NFSE_NACIONAL,
        nome="Sync NFS-e Nacional",
        descricao="Sincroniza NFS-e do Padrao Nacional",
        cron_expression="0 * * * *",  # A cada hora
        handler="sync_nfse_nacional",
        handler_module="modules.government_integrations.jobs.handlers.nfse_handler",
        prioridade=7,
        timeout_seconds=1800,
        tags=["fiscal", "nfse", "nacional"],
    ),

    # =========================================================================
    # RECEITA FEDERAL
    # =========================================================================
    SyncJobType.RECEITA_FEDERAL: SyncJobConfig(
        job_type=SyncJobType.RECEITA_FEDERAL,
        nome="Sync Receita Federal",
        descricao="Atualiza situacao cadastral e certidoes",
        cron_expression="0 4 * * 0",  # Domingo as 04:00
        handler="sync_receita_federal",
        handler_module="modules.government_integrations.jobs.handlers.receita_handler",
        prioridade=5,
        timeout_seconds=3600,
        tags=["fiscal", "receita", "certidoes"],
    ),
    SyncJobType.SIMPLES_NACIONAL: SyncJobConfig(
        job_type=SyncJobType.SIMPLES_NACIONAL,
        nome="Sync Simples Nacional",
        descricao="Sincroniza situacao e extratos do Simples Nacional",
        cron_expression="0 5 1 * *",  # Dia 1 de cada mes as 05:00
        handler="sync_simples_nacional",
        handler_module="modules.government_integrations.jobs.handlers.simples_handler",
        prioridade=6,
        timeout_seconds=3600,
        tags=["fiscal", "simples", "federal"],
    ),
}


class GovSyncJobManager:
    """Gerenciador de jobs de sincronizacao governamental."""

    def __init__(self, db: Session, scheduler_service=None):
        """
        Inicializa o gerenciador.

        Args:
            db: Sessao do banco de dados
            scheduler_service: Servico de agendamento (opcional)
        """
        self.db = db
        self.scheduler_service = scheduler_service

    def registrar_todos_jobs(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """
        Registra todos os jobs de sincronizacao para um tenant.

        Args:
            tenant_id: ID do tenant

        Returns:
            Dict com resultado do registro
        """
        resultados = {
            "sucesso": [],
            "erros": [],
            "total": len(SYNC_JOBS_CONFIG),
        }

        for job_type, config in SYNC_JOBS_CONFIG.items():
            try:
                resultado = self.registrar_job(tenant_id, config)
                if resultado.get("sucesso"):
                    resultados["sucesso"].append(config.nome)
                else:
                    resultados["erros"].append({
                        "job": config.nome,
                        "erro": resultado.get("erro"),
                    })
            except Exception as e:
                logger.error(f"Erro registrando job {config.nome}: {e}")
                resultados["erros"].append({
                    "job": config.nome,
                    "erro": str(e),
                })

        logger.info(
            f"Jobs registrados: {len(resultados['sucesso'])}/{resultados['total']} "
            f"para tenant {tenant_id}"
        )

        return resultados

    def registrar_job(
        self,
        tenant_id: uuid.UUID,
        config: SyncJobConfig,
    ) -> Dict[str, Any]:
        """
        Registra um job individual no scheduler.

        Args:
            tenant_id: ID do tenant
            config: Configuracao do job

        Returns:
            Dict com resultado
        """
        if not self.scheduler_service:
            return {
                "sucesso": False,
                "erro": "Scheduler service nao configurado",
            }

        try:
            # Verificar se job ja existe
            existing = self._buscar_job_existente(tenant_id, config.job_type)
            if existing:
                logger.info(f"Job {config.nome} ja existe para tenant {tenant_id}")
                return {
                    "sucesso": True,
                    "job_id": str(existing),
                    "mensagem": "Job ja existente",
                }

            # Criar novo job
            from modules.scheduler.models.scheduled_task import TaskType, TaskCategory

            task = self.scheduler_service.create_task(
                tenant_id=tenant_id,
                name=config.nome,
                handler=config.handler,
                task_type=TaskType.CRON,
                category=TaskCategory.INTEGRATION,
                cron_expression=config.cron_expression,
                handler_module=config.handler_module,
                handler_kwargs={
                    "job_type": config.job_type.value,
                    "tenant_id": str(tenant_id),
                },
                timeout_seconds=config.timeout_seconds,
                max_retries=config.max_retries,
                priority=config.prioridade,
                queue_name="gov_sync",
                tags=config.tags,
            )

            # Ativar job
            if config.ativo:
                self.scheduler_service.activate_task(task.id)

            logger.info(f"Job {config.nome} registrado: {task.id}")

            return {
                "sucesso": True,
                "job_id": str(task.id),
                "mensagem": "Job criado com sucesso",
            }

        except Exception as e:
            logger.error(f"Erro criando job {config.nome}: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
            }

    def _buscar_job_existente(
        self,
        tenant_id: uuid.UUID,
        job_type: SyncJobType,
    ) -> Optional[uuid.UUID]:
        """Verifica se job ja existe."""
        try:
            from modules.scheduler.models.scheduled_task import ScheduledTask

            task = self.db.query(ScheduledTask).filter(
                ScheduledTask.tenant_id == tenant_id,
                ScheduledTask.handler_kwargs.contains({"job_type": job_type.value}),
            ).first()

            return task.id if task else None
        except Exception:
            return None

    def atualizar_job(
        self,
        job_id: uuid.UUID,
        cron_expression: Optional[str] = None,
        ativo: Optional[bool] = None,
        prioridade: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Atualiza configuracao de um job.

        Args:
            job_id: ID do job
            cron_expression: Nova expressao cron
            ativo: Status ativo/inativo
            prioridade: Nova prioridade

        Returns:
            Dict com resultado
        """
        if not self.scheduler_service:
            return {"sucesso": False, "erro": "Scheduler nao configurado"}

        try:
            updates = {}
            if cron_expression:
                updates["cron_expression"] = cron_expression
            if prioridade is not None:
                updates["priority"] = prioridade

            if updates:
                self.scheduler_service.update_task(job_id, **updates)

            if ativo is not None:
                if ativo:
                    self.scheduler_service.activate_task(job_id)
                else:
                    self.scheduler_service.deactivate_task(job_id)

            return {"sucesso": True, "mensagem": "Job atualizado"}

        except Exception as e:
            logger.error(f"Erro atualizando job {job_id}: {e}")
            return {"sucesso": False, "erro": str(e)}

    def listar_jobs(self, tenant_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Lista todos os jobs de sincronizacao do tenant.

        Args:
            tenant_id: ID do tenant

        Returns:
            Lista de jobs com status
        """
        try:
            from modules.scheduler.models.scheduled_task import ScheduledTask

            tasks = self.db.query(ScheduledTask).filter(
                ScheduledTask.tenant_id == tenant_id,
                ScheduledTask.queue_name == "gov_sync",
            ).all()

            return [
                {
                    "id": str(task.id),
                    "nome": task.name,
                    "cron": task.cron_expression,
                    "status": task.status.value,
                    "ultima_execucao": task.last_run_at.isoformat() if task.last_run_at else None,
                    "proxima_execucao": task.next_run_at.isoformat() if task.next_run_at else None,
                    "total_execucoes": task.run_count,
                    "falhas": task.failure_count,
                    "tags": task.tags,
                }
                for task in tasks
            ]

        except Exception as e:
            logger.error(f"Erro listando jobs: {e}")
            return []

    def executar_job_agora(
        self,
        tenant_id: uuid.UUID,
        job_type: SyncJobType,
    ) -> Dict[str, Any]:
        """
        Executa um job imediatamente (fora do agendamento).

        Args:
            tenant_id: ID do tenant
            job_type: Tipo do job

        Returns:
            Dict com resultado
        """
        if not self.scheduler_service:
            return {"sucesso": False, "erro": "Scheduler nao configurado"}

        try:
            job_id = self._buscar_job_existente(tenant_id, job_type)
            if not job_id:
                return {"sucesso": False, "erro": "Job nao encontrado"}

            # Enfileirar execucao imediata
            self.scheduler_service.queue_task_now(job_id)

            return {
                "sucesso": True,
                "mensagem": f"Job {job_type.value} enfileirado para execucao imediata",
            }

        except Exception as e:
            logger.error(f"Erro executando job {job_type}: {e}")
            return {"sucesso": False, "erro": str(e)}

    def obter_status_sincronizacao(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """
        Obtem status geral da sincronizacao governamental.

        Args:
            tenant_id: ID do tenant

        Returns:
            Dict com status de todos os servicos
        """
        jobs = self.listar_jobs(tenant_id)

        # Agrupar por categoria
        status = {
            "federal": [],
            "estadual": [],
            "municipal": [],
            "resumo": {
                "total_jobs": len(jobs),
                "ativos": 0,
                "com_erro": 0,
                "ultima_sync": None,
            },
        }

        for job in jobs:
            tags = job.get("tags", [])

            # Classificar por nivel
            if "federal" in tags:
                categoria = "federal"
            elif "estadual" in tags or "transporte" in tags:
                categoria = "estadual"
            elif "municipal" in tags:
                categoria = "municipal"
            else:
                categoria = "federal"  # default

            status[categoria].append({
                "nome": job["nome"],
                "status": job["status"],
                "ultima_execucao": job["ultima_execucao"],
                "proxima_execucao": job["proxima_execucao"],
            })

            # Atualizar resumo
            if job["status"] == "active":
                status["resumo"]["ativos"] += 1
            if job["falhas"] > 0:
                status["resumo"]["com_erro"] += 1

            # Ultima sync global
            if job["ultima_execucao"]:
                if (
                    status["resumo"]["ultima_sync"] is None or
                    job["ultima_execucao"] > status["resumo"]["ultima_sync"]
                ):
                    status["resumo"]["ultima_sync"] = job["ultima_execucao"]

        return status


# =========================================================================
# HANDLERS DOS JOBS (Funcoes que serao executadas pelo scheduler)
# =========================================================================

async def executar_sync_job(
    db: Session,
    job_type: str,
    tenant_id: str,
    **kwargs,
) -> Dict[str, Any]:
    """
    Handler generico para execucao de jobs de sincronizacao.

    Este handler e chamado pelo scheduler e delega para o SyncManager.

    Args:
        db: Sessao do banco
        job_type: Tipo do job
        tenant_id: ID do tenant
        **kwargs: Argumentos adicionais

    Returns:
        Dict com resultado da sincronizacao
    """
    from ..sync.sync_manager import SyncManager

    logger.info(f"[GovSync] Iniciando job {job_type} para tenant {tenant_id}")

    try:
        # Mapear job_type para servico do SyncManager
        servico_map = {
            "nfe_emitidas": "sefaz_nfe",
            "nfe_destinadas": "sefaz_nfe",
            "cte": "sefaz_cte",
            "mdfe": "sefaz_mdfe",
            "esocial": "esocial",
            "fgts_digital": "fgts_digital",
            "dctfweb": "dctfweb",
            "efd_reinf": "efd_reinf",
            "sped_fiscal": "sped_fiscal",
            "sped_contabil": "sped_contabil",
            "nfse_manaus": "nfse_manaus",
            "nfse_nacional": "nfse_nacional",
            "receita_federal": "receita_federal",
            "simples_nacional": "simples_nacional",
        }

        servico = servico_map.get(job_type)
        if not servico:
            return {
                "sucesso": False,
                "erro": f"Tipo de job desconhecido: {job_type}",
            }

        # Obter CNPJ do tenant
        cnpj = await _obter_cnpj_tenant(db, tenant_id)
        if not cnpj:
            return {
                "sucesso": False,
                "erro": "CNPJ do tenant nao encontrado",
            }

        # Executar sincronizacao
        sync_manager = SyncManager(db)
        resultado = await sync_manager.executar_sync(
            servico=servico,
            cnpj=cnpj,
            dias_retroativos=kwargs.get("dias_retroativos", 7),
        )

        logger.info(
            f"[GovSync] Job {job_type} concluido - "
            f"Sucesso: {resultado.get('sucesso')}, "
            f"Registros: {resultado.get('total_registros', 0)}"
        )

        return resultado

    except Exception as e:
        logger.error(f"[GovSync] Erro no job {job_type}: {e}")
        return {
            "sucesso": False,
            "erro": str(e),
        }


async def _obter_cnpj_tenant(db: Session, tenant_id: str) -> Optional[str]:
    """Obtem CNPJ do tenant."""
    try:
        from modules.core.models.tenant import Tenant

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        return tenant.cnpj if tenant else None
    except Exception:
        # Fallback para credenciais configuradas
        try:
            from modules.government_integrations.core.certificate_manager import CertificateStore

            store = CertificateStore(db)
            certs = store.listar_certificados_ativos()
            if certs:
                return certs[0].get("cnpj")
        except Exception:
            pass
    return None
