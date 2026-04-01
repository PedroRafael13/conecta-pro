"""
Gerenciador Central de Sincronizacao.

Coordena todas as sincronizacoes de dados governamentais:
- Agendamento automatico
- Execucao manual
- Monitoramento de status
- Notificacoes
"""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any

from .base_sync import SyncConfig, SyncResult, SyncStatus

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS E DATACLASSES
# =============================================================================


class ServicoGov(StrEnum):
    """Servicos governamentais disponiveis."""

    # Federais
    ESOCIAL = "esocial"
    RECEITA_FEDERAL = "receita_federal"
    ECAC = "ecac"
    FGTS_DIGITAL = "fgts_digital"
    SIMPLES_NACIONAL = "simples_nacional"
    EFD_REINF = "efd_reinf"
    DCTFWEB = "dctfweb"
    NFSE_NACIONAL = "nfse_nacional"

    # Estaduais
    SEFAZ_NFE = "sefaz_nfe"
    SEFAZ_CTE = "sefaz_cte"
    SEFAZ_MDFE = "sefaz_mdfe"
    SPED_FISCAL = "sped_fiscal"
    SPED_CONTABIL = "sped_contabil"

    # Municipais
    NFSE_MANAUS = "nfse_manaus"


@dataclass
class SyncJob:
    """Job de sincronizacao."""

    id: str
    cnpj: str
    servico: ServicoGov
    config: SyncConfig
    status: SyncStatus = SyncStatus.IDLE
    resultado: SyncResult | None = None
    inicio: datetime | None = None
    fim: datetime | None = None
    erro: str | None = None


@dataclass
class SyncSchedule:
    """Agendamento de sincronizacao."""

    servico: ServicoGov
    intervalo_minutos: int = 60
    horario_preferencial: str | None = None  # HH:MM
    dias_semana: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])
    ativo: bool = True
    ultima_execucao: datetime | None = None
    proxima_execucao: datetime | None = None


# =============================================================================
# SYNC MANAGER
# =============================================================================


class SyncManager:
    """
    Gerenciador central de sincronizacoes.

    Responsavel por:
    - Registrar e gerenciar sincronizadores
    - Executar sincronizacoes manuais e agendadas
    - Monitorar status das sincronizacoes
    - Enviar notificacoes
    """

    def __init__(
        self,
        db_session,
        certificate_manager=None,
        max_workers: int = 4,
    ):
        """
        Inicializa o gerenciador.

        Args:
            db_session: Sessao do banco de dados
            certificate_manager: Gerenciador de certificados
            max_workers: Numero maximo de workers paralelos
        """
        self.db = db_session
        self.certificate_manager = certificate_manager
        self.max_workers = max_workers

        # Sincronizadores registrados
        self._synchronizers: dict[ServicoGov, Any] = {}

        # Jobs em execucao
        self._jobs: dict[str, SyncJob] = {}
        self._jobs_lock = threading.Lock()

        # Agendamentos
        self._schedules: dict[str, dict[ServicoGov, SyncSchedule]] = {}

        # Thread pool para execucao paralela
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        # Flag de execucao do scheduler
        self._scheduler_running = False
        self._scheduler_task = None

        # Inicializar sincronizadores
        self._init_synchronizers()

    def _init_synchronizers(self):
        """Inicializa os sincronizadores disponiveis."""
        try:
            # eSocial
            from .federal.esocial_sync import ESocialSynchronizer

            self._synchronizers[ServicoGov.ESOCIAL] = ESocialSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # Receita Federal
            from .federal.receita_sync import ReceitaFederalSynchronizer

            self._synchronizers[ServicoGov.RECEITA_FEDERAL] = ReceitaFederalSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # NF-e/SEFAZ
            from .estadual.nfe_sync import NFeSynchronizer

            self._synchronizers[ServicoGov.SEFAZ_NFE] = NFeSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # NFS-e Manaus
            from .municipal.nfse_manaus_sync import NFSeManausSynchronizer

            self._synchronizers[ServicoGov.NFSE_MANAUS] = NFSeManausSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # FGTS Digital
            from .federal.fgts_digital_sync import FGTSDigitalSynchronizer

            self._synchronizers[ServicoGov.FGTS_DIGITAL] = FGTSDigitalSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # EFD-Reinf
            from .federal.efd_reinf_sync import EFDReinfSynchronizer

            self._synchronizers[ServicoGov.EFD_REINF] = EFDReinfSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # DCTFWeb
            from .federal.dctfweb_sync import DCTFWebSynchronizer

            self._synchronizers[ServicoGov.DCTFWEB] = DCTFWebSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # CT-e
            from .estadual.cte_sync import CTeSynchronizer

            self._synchronizers[ServicoGov.SEFAZ_CTE] = CTeSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # MDF-e
            from .estadual.mdfe_sync import MDFeSynchronizer

            self._synchronizers[ServicoGov.SEFAZ_MDFE] = MDFeSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # SPED Fiscal
            from .estadual.sped_fiscal_sync import SPEDFiscalSynchronizer

            self._synchronizers[ServicoGov.SPED_FISCAL] = SPEDFiscalSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # SPED Contabil
            from .federal.sped_contabil_sync import SPEDContabilSynchronizer

            self._synchronizers[ServicoGov.SPED_CONTABIL] = SPEDContabilSynchronizer(
                self.db,
                self.certificate_manager,
            )

            # NFS-e Nacional
            from .municipal.nfse_nacional_sync import NFSeNacionalSynchronizer

            self._synchronizers[ServicoGov.NFSE_NACIONAL] = NFSeNacionalSynchronizer(
                self.db,
                self.certificate_manager,
            )

            logger.info(f"[SyncManager] Inicializado com {len(self._synchronizers)} sincronizadores")

        except Exception as e:
            logger.error(f"[SyncManager] Erro inicializando sincronizadores: {e}")

    # =========================================================================
    # EXECUCAO DE SINCRONIZACOES
    # =========================================================================

    async def sincronizar(
        self,
        cnpj: str,
        servico: ServicoGov,
        tipo_sync: str = "incremental",
        data_inicial: date | None = None,
        data_final: date | None = None,
        **kwargs,
    ) -> SyncResult:
        """
        Executa sincronizacao de um servico.

        Args:
            cnpj: CNPJ da empresa
            servico: Servico a sincronizar
            tipo_sync: Tipo de sincronizacao (incremental/completa)
            data_inicial: Data inicial (opcional)
            data_final: Data final (opcional)

        Returns:
            SyncResult com resultado
        """
        # Verificar se sincronizador existe
        synchronizer = self._synchronizers.get(servico)
        if not synchronizer:
            return SyncResult(
                sucesso=False,
                mensagem=f"Sincronizador nao disponivel: {servico.value}",
            )

        # Criar configuracao
        config = SyncConfig(
            cnpj_empresa=cnpj,
            servico=servico.value,
            tipo_sync=tipo_sync,
            data_inicial=data_inicial,
            data_final=data_final,
            parametros_extras=kwargs,
        )

        # Criar job
        job_id = f"{cnpj}_{servico.value}_{datetime.utcnow().timestamp()}"
        job = SyncJob(
            id=job_id,
            cnpj=cnpj,
            servico=servico,
            config=config,
            status=SyncStatus.RUNNING,
            inicio=datetime.utcnow(),
        )

        with self._jobs_lock:
            self._jobs[job_id] = job

        try:
            # Executar sincronizacao
            logger.info(f"[SyncManager] Iniciando {servico.value} para {cnpj}")
            resultado = await synchronizer.sincronizar(config)

            job.resultado = resultado
            job.status = SyncStatus.SUCCESS if resultado.sucesso else SyncStatus.ERROR
            job.fim = datetime.utcnow()

            # Atualizar agendamento
            self._atualizar_ultima_execucao(cnpj, servico)

            return resultado

        except Exception as e:
            logger.exception(f"[SyncManager] Erro em {servico.value}")
            job.status = SyncStatus.ERROR
            job.erro = str(e)
            job.fim = datetime.utcnow()

            return SyncResult(
                sucesso=False,
                mensagem=f"Erro na sincronizacao: {str(e)}",
            )

    async def sincronizar_todos(
        self,
        cnpj: str,
        servicos: list[ServicoGov] | None = None,
        paralelo: bool = True,
    ) -> dict[ServicoGov, SyncResult]:
        """
        Sincroniza multiplos servicos.

        Args:
            cnpj: CNPJ da empresa
            servicos: Lista de servicos (ou todos se None)
            paralelo: Executar em paralelo

        Returns:
            Dict com resultados por servico
        """
        if servicos is None:
            servicos = list(self._synchronizers.keys())

        resultados = {}

        if paralelo:
            # Executar em paralelo
            tasks = [self.sincronizar(cnpj, servico) for servico in servicos]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for servico, result in zip(servicos, results, strict=False):
                if isinstance(result, Exception):
                    resultados[servico] = SyncResult(
                        sucesso=False,
                        mensagem=str(result),
                    )
                else:
                    resultados[servico] = result
        else:
            # Executar sequencialmente
            for servico in servicos:
                resultados[servico] = await self.sincronizar(cnpj, servico)

        return resultados

    # =========================================================================
    # AGENDAMENTO
    # =========================================================================

    def configurar_agendamento(
        self,
        cnpj: str,
        servico: ServicoGov,
        intervalo_minutos: int = 60,
        horario_preferencial: str | None = None,
        dias_semana: list[int] | None = None,
        ativo: bool = True,
    ):
        """
        Configura agendamento de sincronizacao.

        Args:
            cnpj: CNPJ da empresa
            servico: Servico a agendar
            intervalo_minutos: Intervalo entre sincronizacoes
            horario_preferencial: Horario preferencial (HH:MM)
            dias_semana: Dias da semana (0=segunda, 6=domingo)
            ativo: Se o agendamento esta ativo
        """
        if cnpj not in self._schedules:
            self._schedules[cnpj] = {}

        schedule = SyncSchedule(
            servico=servico,
            intervalo_minutos=intervalo_minutos,
            horario_preferencial=horario_preferencial,
            dias_semana=dias_semana or [0, 1, 2, 3, 4, 5, 6],
            ativo=ativo,
        )

        # Calcular proxima execucao
        schedule.proxima_execucao = self._calcular_proxima_execucao(schedule)

        self._schedules[cnpj][servico] = schedule

        logger.info(
            f"[SyncManager] Agendamento configurado: {servico.value} para {cnpj} a cada {intervalo_minutos} minutos"
        )

    def _calcular_proxima_execucao(self, schedule: SyncSchedule) -> datetime:
        """Calcula proxima execucao do agendamento."""
        agora = datetime.utcnow()

        if schedule.horario_preferencial:
            hora, minuto = map(int, schedule.horario_preferencial.split(":"))
            proxima = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)

            if proxima <= agora:
                proxima += timedelta(days=1)

            # Ajustar para dia da semana permitido
            while proxima.weekday() not in schedule.dias_semana:
                proxima += timedelta(days=1)

        else:
            if schedule.ultima_execucao:
                proxima = schedule.ultima_execucao + timedelta(minutes=schedule.intervalo_minutos)
            else:
                proxima = agora + timedelta(minutes=schedule.intervalo_minutos)

        return proxima

    def _atualizar_ultima_execucao(self, cnpj: str, servico: ServicoGov):
        """Atualiza ultima execucao do agendamento."""
        if cnpj in self._schedules and servico in self._schedules[cnpj]:
            schedule = self._schedules[cnpj][servico]
            schedule.ultima_execucao = datetime.utcnow()
            schedule.proxima_execucao = self._calcular_proxima_execucao(schedule)

    async def _scheduler_loop(self):
        """Loop do scheduler."""
        logger.info("[SyncManager] Scheduler iniciado")

        while self._scheduler_running:
            try:
                agora = datetime.utcnow()

                # Verificar todos os agendamentos
                for cnpj, servicos in self._schedules.items():
                    for servico, schedule in servicos.items():
                        if not schedule.ativo:
                            continue

                        if schedule.proxima_execucao and schedule.proxima_execucao <= agora:
                            # Executar sincronizacao em background
                            asyncio.create_task(self.sincronizar(cnpj, servico))

                # Aguardar 60 segundos
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"[SyncManager] Erro no scheduler: {e}")
                await asyncio.sleep(60)

        logger.info("[SyncManager] Scheduler parado")

    def iniciar_scheduler(self):
        """Inicia o scheduler de sincronizacoes."""
        if self._scheduler_running:
            return

        self._scheduler_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("[SyncManager] Scheduler iniciado")

    def parar_scheduler(self):
        """Para o scheduler."""
        self._scheduler_running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
        logger.info("[SyncManager] Scheduler parado")

    # =========================================================================
    # MONITORAMENTO
    # =========================================================================

    def obter_status(self, cnpj: str) -> dict[str, Any]:
        """
        Obtem status de todas as sincronizacoes de uma empresa.

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dict com status por servico
        """
        status = {}

        for servico in ServicoGov:
            servico_status = {
                "disponivel": servico in self._synchronizers,
                "agendamento_ativo": False,
                "ultima_sincronizacao": None,
                "proxima_sincronizacao": None,
                "status_ultima": None,
            }

            # Verificar agendamento
            if cnpj in self._schedules and servico in self._schedules[cnpj]:
                schedule = self._schedules[cnpj][servico]
                servico_status.update(
                    {
                        "agendamento_ativo": schedule.ativo,
                        "intervalo_minutos": schedule.intervalo_minutos,
                        "ultima_sincronizacao": schedule.ultima_execucao.isoformat()
                        if schedule.ultima_execucao
                        else None,
                        "proxima_sincronizacao": schedule.proxima_execucao.isoformat()
                        if schedule.proxima_execucao
                        else None,
                    }
                )

            # Verificar jobs recentes
            with self._jobs_lock:
                jobs_servico = [j for j in self._jobs.values() if j.cnpj == cnpj and j.servico == servico]
                if jobs_servico:
                    ultimo_job = max(jobs_servico, key=lambda j: j.inicio or datetime.min)
                    servico_status.update(
                        {
                            "status_ultima": ultimo_job.status.value,
                            "ultima_sincronizacao": ultimo_job.fim.isoformat() if ultimo_job.fim else None,
                        }
                    )

            status[servico.value] = servico_status

        return status

    def obter_jobs_ativos(self, cnpj: str | None = None) -> list[dict[str, Any]]:
        """Obtem jobs em execucao."""
        with self._jobs_lock:
            jobs = list(self._jobs.values())

        if cnpj:
            jobs = [j for j in jobs if j.cnpj == cnpj]

        jobs = [j for j in jobs if j.status == SyncStatus.RUNNING]

        return [
            {
                "id": j.id,
                "cnpj": j.cnpj,
                "servico": j.servico.value,
                "status": j.status.value,
                "inicio": j.inicio.isoformat() if j.inicio else None,
            }
            for j in jobs
        ]

    def obter_historico(
        self,
        cnpj: str,
        servico: ServicoGov | None = None,
        limite: int = 10,
    ) -> list[dict[str, Any]]:
        """Obtem historico de sincronizacoes."""
        from .models.sync_models import SyncLog

        query = self.db.query(SyncLog).filter(SyncLog.cnpj_empresa == cnpj)

        if servico:
            query = query.filter(SyncLog.servico == servico.value)

        logs = query.order_by(SyncLog.inicio_execucao.desc()).limit(limite).all()

        return [
            {
                "id": str(log.id),
                "servico": log.servico,
                "tipo": log.tipo_sync.value if log.tipo_sync else None,
                "status": log.status.value if log.status else None,
                "inicio": log.inicio_execucao.isoformat() if log.inicio_execucao else None,
                "fim": log.fim_execucao.isoformat() if log.fim_execucao else None,
                "duracao_segundos": log.duracao_segundos,
                "registros_processados": log.registros_processados,
                "registros_novos": log.registros_novos,
                "registros_erro": log.registros_erro,
                "mensagem_erro": log.mensagem_erro,
            }
            for log in logs
        ]

    # =========================================================================
    # CONFIGURACAO
    # =========================================================================

    def configurar_empresa(
        self,
        cnpj: str,
        _certificado_id: str | None = None,
        servicos_habilitados: list[ServicoGov] | None = None,
        agendamentos: dict[ServicoGov, int] | None = None,
    ):
        """
        Configura sincronizacao completa para uma empresa.

        Args:
            cnpj: CNPJ da empresa
            certificado_id: ID do certificado digital
            servicos_habilitados: Lista de servicos a habilitar
            agendamentos: Dict de servico -> intervalo em minutos
        """
        if servicos_habilitados is None:
            servicos_habilitados = list(self._synchronizers.keys())

        if agendamentos is None:
            agendamentos = {
                ServicoGov.ESOCIAL: 60,
                ServicoGov.SEFAZ_NFE: 30,
                ServicoGov.RECEITA_FEDERAL: 1440,  # 24h
            }

        # Configurar agendamentos
        for servico, intervalo in agendamentos.items():
            if servico in servicos_habilitados:
                self.configurar_agendamento(
                    cnpj=cnpj,
                    servico=servico,
                    intervalo_minutos=intervalo,
                    ativo=True,
                )

        logger.info(f"[SyncManager] Empresa {cnpj} configurada com {len(servicos_habilitados)} servicos")


# =============================================================================
# INSTANCIA GLOBAL
# =============================================================================

_sync_manager: SyncManager | None = None


def get_sync_manager() -> SyncManager:
    """Retorna instancia global do SyncManager."""
    global _sync_manager
    if _sync_manager is None:
        raise RuntimeError("SyncManager nao inicializado. Chame init_sync_manager primeiro.")
    return _sync_manager


def init_sync_manager(
    db_session,
    certificate_manager=None,
    max_workers: int = 4,
) -> SyncManager:
    """Inicializa e retorna o SyncManager global."""
    global _sync_manager
    _sync_manager = SyncManager(
        db_session=db_session,
        certificate_manager=certificate_manager,
        max_workers=max_workers,
    )
    return _sync_manager
