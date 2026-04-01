"""
Classe base para sincronizadores de dados governamentais.

Fornece funcionalidades comuns:
- Logging estruturado
- Retry com backoff exponencial
- Controle de ultima sincronizacao
- Tratamento padronizado de erros
- Metricas de execucao
"""

import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class SyncResult:
    """Resultado de uma sincronizacao."""

    sucesso: bool
    registros_processados: int = 0
    registros_novos: int = 0
    registros_atualizados: int = 0
    registros_erro: int = 0
    mensagem: str = ""
    erros: list[dict[str, Any]] = field(default_factory=list)
    dados_extras: dict[str, Any] = field(default_factory=dict)
    duracao_segundos: float = 0
    ultimo_id_processado: str | None = None
    ultima_data_processada: datetime | None = None


@dataclass
class SyncConfig:
    """Configuracao de sincronizacao."""

    cnpj_empresa: str
    servico: str
    data_inicial: date | None = None
    data_final: date | None = None
    tipo_sync: str = "incremental"  # completa, incremental
    max_registros: int | None = None
    timeout_segundos: int = 300
    max_retries: int = 3
    parametros_extras: dict[str, Any] = field(default_factory=dict)


class SyncStatus(StrEnum):
    """Status de sincronizacao."""

    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


# =============================================================================
# CLASSE BASE
# =============================================================================


class BaseSynchronizer(ABC):
    """
    Classe base abstrata para sincronizadores de dados governamentais.

    Cada servico (eSocial, SEFAZ, etc) deve herdar desta classe e implementar
    os metodos abstratos.
    """

    # Nome do servico (deve ser sobrescrito)
    SERVICO_NOME: str = "base"

    # Intervalo padrao entre sincronizacoes (em minutos)
    INTERVALO_PADRAO: int = 60

    # Dias retroativos padrao para sincronizacao incremental
    DIAS_RETROATIVOS_PADRAO: int = 30

    def __init__(
        self,
        db_session,
        certificate_manager=None,
        govbr_service=None,
    ):
        """
        Inicializa o sincronizador.

        Args:
            db_session: Sessao do banco de dados
            certificate_manager: Gerenciador de certificados (opcional)
            govbr_service: Service Gov.br para autenticacao (opcional)
        """
        self.db = db_session
        self.certificate_manager = certificate_manager
        self.govbr_service = govbr_service
        self._status = SyncStatus.IDLE
        self._cancel_requested = False
        self._current_sync_id: str | None = None

    @property
    def status(self) -> SyncStatus:
        """Retorna status atual da sincronizacao."""
        return self._status

    def cancelar(self):
        """Solicita cancelamento da sincronizacao em andamento."""
        self._cancel_requested = True
        logger.info(f"[{self.SERVICO_NOME}] Cancelamento solicitado")

    # =========================================================================
    # METODOS ABSTRATOS (devem ser implementados)
    # =========================================================================

    @abstractmethod
    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Extrai dados do servico governamental.

        Deve ser implementado por cada sincronizador especifico.
        Retorna um generator que yield cada registro extraido.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados de cada registro extraido
        """
        pass

    @abstractmethod
    async def _processar_registro(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """
        Processa um registro extraido (salva/atualiza no banco).

        Args:
            registro: Dados do registro
            config: Configuracao da sincronizacao

        Returns:
            True se processou com sucesso, False caso contrario
        """
        pass

    @abstractmethod
    def _obter_ultima_sincronizacao(
        self,
        cnpj: str,
    ) -> datetime | None:
        """
        Obtem data/hora da ultima sincronizacao bem sucedida.

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Data/hora da ultima sincronizacao ou None
        """
        pass

    # =========================================================================
    # METODOS PRINCIPAIS
    # =========================================================================

    async def sincronizar(
        self,
        config: SyncConfig,
    ) -> SyncResult:
        """
        Executa sincronizacao completa.

        Args:
            config: Configuracao da sincronizacao

        Returns:
            SyncResult com resultado da sincronizacao
        """
        self._status = SyncStatus.RUNNING
        self._cancel_requested = False
        self._current_sync_id = str(uuid4())

        inicio = datetime.utcnow()
        result = SyncResult(sucesso=False)

        logger.info(
            f"[{self.SERVICO_NOME}] Iniciando sincronizacao - CNPJ: {config.cnpj_empresa}, Tipo: {config.tipo_sync}"
        )

        try:
            # Validar pre-requisitos
            await self._validar_prerequisitos(config)

            # Ajustar datas para sincronizacao incremental
            if config.tipo_sync == "incremental" and not config.data_inicial:
                ultima_sync = self._obter_ultima_sincronizacao(config.cnpj_empresa)
                if ultima_sync:
                    config.data_inicial = ultima_sync.date()
                else:
                    config.data_inicial = date.today() - timedelta(days=self.DIAS_RETROATIVOS_PADRAO)

            if not config.data_final:
                config.data_final = date.today()

            # Registrar inicio no banco
            await self._registrar_inicio_sync(config)

            # Extrair e processar dados
            async for registro in self._extrair_dados(config):
                if self._cancel_requested:
                    logger.warning(f"[{self.SERVICO_NOME}] Sincronizacao cancelada")
                    result.mensagem = "Sincronizacao cancelada pelo usuario"
                    break

                result.registros_processados += 1

                try:
                    is_novo = await self._processar_registro(registro, config)
                    if is_novo:
                        result.registros_novos += 1
                    else:
                        result.registros_atualizados += 1

                    # Atualizar marcadores
                    if "id" in registro:
                        result.ultimo_id_processado = str(registro["id"])
                    if "data" in registro:
                        result.ultima_data_processada = registro["data"]

                except Exception as e:
                    result.registros_erro += 1
                    result.erros.append(
                        {
                            "registro": str(registro.get("id", "unknown")),
                            "erro": str(e),
                            "traceback": traceback.format_exc(),
                        }
                    )
                    logger.error(f"[{self.SERVICO_NOME}] Erro processando registro: {e}")

                # Commit parcial a cada 100 registros
                if result.registros_processados % 100 == 0:
                    await self._commit_parcial()

            # Commit final
            await self._commit_final()

            # Definir sucesso
            if result.registros_erro == 0:
                result.sucesso = True
                self._status = SyncStatus.SUCCESS
                result.mensagem = (
                    f"Sincronizacao concluida: {result.registros_processados} registros "
                    f"({result.registros_novos} novos, {result.registros_atualizados} atualizados)"
                )
            elif result.registros_processados > result.registros_erro:
                result.sucesso = True
                self._status = SyncStatus.PARTIAL
                result.mensagem = (
                    f"Sincronizacao parcial: {result.registros_erro} erros de {result.registros_processados} registros"
                )
            else:
                self._status = SyncStatus.ERROR
                result.mensagem = f"Sincronizacao falhou: {result.registros_erro} erros"

        except Exception as e:
            self._status = SyncStatus.ERROR
            result.mensagem = f"Erro na sincronizacao: {str(e)}"
            result.erros.append({"tipo": "erro_geral", "erro": str(e), "traceback": traceback.format_exc()})
            logger.exception(f"[{self.SERVICO_NOME}] Erro na sincronizacao")

        finally:
            # Calcular duracao
            fim = datetime.utcnow()
            result.duracao_segundos = (fim - inicio).total_seconds()

            # Registrar fim no banco
            await self._registrar_fim_sync(result)

            logger.info(
                f"[{self.SERVICO_NOME}] Sincronizacao finalizada - "
                f"Status: {self._status.value}, Duracao: {result.duracao_segundos:.2f}s"
            )

        return result

    # =========================================================================
    # METODOS DE SUPORTE
    # =========================================================================

    async def _validar_prerequisitos(self, config: SyncConfig):
        """Valida pre-requisitos para sincronizacao."""
        # Verificar certificado se necessario
        if self.certificate_manager:
            if not self.certificate_manager.is_valid():
                raise ValueError("Certificado digital invalido ou expirado")

        # Verificar CNPJ
        if not config.cnpj_empresa or len(config.cnpj_empresa) != 14:
            raise ValueError("CNPJ invalido")

    @abstractmethod
    async def _registrar_inicio_sync(self, config: SyncConfig):
        """Registra inicio da sincronizacao no banco."""
        ...

    @abstractmethod
    async def _registrar_fim_sync(self, result: SyncResult):
        """Registra fim da sincronizacao no banco."""
        ...

    async def _commit_parcial(self):
        """Faz commit parcial durante processamento."""
        try:
            if hasattr(self.db, "commit"):
                await self.db.commit()
        except Exception as e:
            logger.warning(f"[{self.SERVICO_NOME}] Erro no commit parcial: {e}")

    async def _commit_final(self):
        """Faz commit final apos processamento."""
        try:
            if hasattr(self.db, "commit"):
                await self.db.commit()
        except Exception as e:
            logger.error(f"[{self.SERVICO_NOME}] Erro no commit final: {e}")
            raise

    # =========================================================================
    # UTILITARIOS
    # =========================================================================

    async def _request_com_retry(
        self,
        func,
        *args,
        max_retries: int = 3,
        base_delay: float = 1.0,
        **kwargs,
    ) -> Any:
        """
        Executa funcao com retry e backoff exponencial.

        Args:
            func: Funcao a executar
            max_retries: Numero maximo de tentativas
            base_delay: Delay base em segundos

        Returns:
            Resultado da funcao
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                last_error = e
                delay = base_delay * (2**attempt)

                logger.warning(
                    f"[{self.SERVICO_NOME}] Tentativa {attempt + 1}/{max_retries} falhou: {e}. Aguardando {delay}s..."
                )

                await asyncio.sleep(delay)

        raise last_error

    def _normalizar_cnpj(self, cnpj: str) -> str:
        """Remove formatacao do CNPJ."""
        import re

        return re.sub(r"[^0-9]", "", cnpj)

    def _normalizar_cpf(self, cpf: str) -> str:
        """Remove formatacao do CPF."""
        import re

        return re.sub(r"[^0-9]", "", cpf)

    def _parse_data(self, data_str: str) -> date | None:
        """Converte string para date."""
        if not data_str:
            return None

        formatos = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%SZ",
        ]

        for fmt in formatos:
            try:
                return datetime.strptime(data_str[: len(fmt)], fmt).date()
            except ValueError:
                continue

        return None

    def _parse_decimal(self, valor: Any) -> float | None:
        """Converte valor para decimal."""
        if valor is None:
            return None

        if isinstance(valor, (int, float)):
            return float(valor)

        if isinstance(valor, str):
            valor = valor.replace(",", ".").strip()
            try:
                return float(valor)
            except ValueError:
                return None

        return None


# =============================================================================
# DECORATORS
# =============================================================================


def retry_on_error(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator para retry com backoff exponencial."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    delay = base_delay * (2**attempt)
                    logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou: {e}. Aguardando {delay}s...")
                    await asyncio.sleep(delay)
            raise last_error

        return wrapper

    return decorator


def log_execution(func):
    """Decorator para logging de execucao."""

    async def wrapper(*args, **kwargs):
        logger.info(f"Iniciando {func.__name__}")
        inicio = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            duracao = (datetime.utcnow() - inicio).total_seconds()
            logger.info(f"Finalizado {func.__name__} em {duracao:.2f}s")
            return result
        except Exception as e:
            duracao = (datetime.utcnow() - inicio).total_seconds()
            logger.error(f"Erro em {func.__name__} apos {duracao:.2f}s: {e}")
            raise

    return wrapper
