"""
Sistema de Retry com Backoff Exponencial.

Implementa estratégias de retry configuráveis por serviço.
"""

import asyncio
import logging
import random  # noqa: S311
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps
from typing import TypeVar

from .error_classifier import ClassificadorErros, ErroIntegracao

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuração de retry por serviço."""

    max_tentativas: int
    base_delay: float  # segundos
    max_delay: float  # segundos
    jitter: float = 0.1  # percentual de variação aleatória


class RetryConfigs:
    """Configurações de retry por serviço."""

    _configs: dict[str, RetryConfig] = {
        # SEFAZ - NF-e, NFC-e
        "sefaz": RetryConfig(
            max_tentativas=3,
            base_delay=2.0,
            max_delay=60.0,
        ),
        "sefaz_am": RetryConfig(
            max_tentativas=3,
            base_delay=2.0,
            max_delay=60.0,
        ),
        # eSocial - Rate limit mais restritivo
        "esocial": RetryConfig(
            max_tentativas=5,
            base_delay=5.0,
            max_delay=120.0,
        ),
        # EFD-Reinf
        "efd_reinf": RetryConfig(
            max_tentativas=3,
            base_delay=3.0,
            max_delay=60.0,
        ),
        # FGTS Digital
        "fgts_digital": RetryConfig(
            max_tentativas=3,
            base_delay=3.0,
            max_delay=30.0,
        ),
        # DCTFWeb
        "dctfweb": RetryConfig(
            max_tentativas=3,
            base_delay=5.0,
            max_delay=60.0,
        ),
        # NFS-e Municipal
        "nfse": RetryConfig(
            max_tentativas=3,
            base_delay=2.0,
            max_delay=30.0,
        ),
        "nfse_manaus": RetryConfig(
            max_tentativas=3,
            base_delay=2.0,
            max_delay=30.0,
        ),
        # CT-e e MDF-e
        "cte": RetryConfig(
            max_tentativas=3,
            base_delay=2.0,
            max_delay=60.0,
        ),
        "mdfe": RetryConfig(
            max_tentativas=3,
            base_delay=2.0,
            max_delay=60.0,
        ),
        # Gov.br OAuth
        "govbr": RetryConfig(
            max_tentativas=3,
            base_delay=1.0,
            max_delay=10.0,
        ),
        # Simples Nacional
        "simples_nacional": RetryConfig(
            max_tentativas=3,
            base_delay=3.0,
            max_delay=30.0,
        ),
        # SPED
        "sped": RetryConfig(
            max_tentativas=2,
            base_delay=5.0,
            max_delay=30.0,
        ),
        # e-CAC
        "ecac": RetryConfig(
            max_tentativas=3,
            base_delay=5.0,
            max_delay=60.0,
        ),
        # Padrão
        "default": RetryConfig(
            max_tentativas=3,
            base_delay=1.0,
            max_delay=30.0,
        ),
    }

    @classmethod
    def get(cls, servico: str) -> RetryConfig:
        """Obtém configuração para o serviço."""
        return cls._configs.get(servico, cls._configs["default"])

    @classmethod
    def registrar(cls, servico: str, config: RetryConfig):
        """Registra configuração customizada."""
        cls._configs[servico] = config


async def retry_com_backoff[T](
    func: Callable[..., Awaitable[T]],
    *args,
    servico: str = "default",
    correlation_id: str | None = None,
    on_retry: Callable[[ErroIntegracao, int], Awaitable[None]] | None = None,
    **kwargs,
) -> T:
    """
    Executa função com retry e backoff exponencial.

    Fórmula: delay = min(base_delay * (2 ** tentativa) + jitter, max_delay)

    Args:
        func: Função assíncrona a executar
        servico: Nome do serviço para config de retry
        correlation_id: ID para rastreamento
        on_retry: Callback chamado em cada retry
        *args, **kwargs: Argumentos para a função

    Returns:
        Resultado da função

    Raises:
        Exception: Último erro se todas tentativas falharem
    """
    config = RetryConfigs.get(servico)
    max_tentativas = config.max_tentativas
    base_delay = config.base_delay
    max_delay = config.max_delay
    jitter_pct = config.jitter

    ultimo_erro: Exception | None = None
    erro_info: ErroIntegracao | None = None

    for tentativa in range(max_tentativas):
        try:
            return await func(*args, **kwargs)

        except Exception as e:
            ultimo_erro = e
            erro_info = ClassificadorErros.classificar(e, servico, tentativa, correlation_id)

            # Se não pode retentar, falha imediatamente
            if not erro_info.pode_retentar:
                logger.error(
                    f"[{servico}] Erro não recuperável (tentativa {tentativa + 1}): {e}",
                    extra={
                        "servico": servico,
                        "categoria": erro_info.categoria.value,
                        "correlation_id": correlation_id,
                    },
                )
                raise

            # Última tentativa, não espera
            if tentativa == max_tentativas - 1:
                break

            # Calcular delay com jitter
            delay = min(base_delay * (2**tentativa), max_delay)
            jitter = random.uniform(0, delay * jitter_pct)  # noqa: S311
            delay_total = delay + jitter

            logger.warning(
                f"[{servico}] Tentativa {tentativa + 1}/{max_tentativas} "
                f"falhou: {e}. Categoria: {erro_info.categoria.value}. "
                f"Aguardando {delay_total:.1f}s...",
                extra={
                    "servico": servico,
                    "tentativa": tentativa + 1,
                    "max_tentativas": max_tentativas,
                    "delay": delay_total,
                    "categoria": erro_info.categoria.value,
                    "correlation_id": correlation_id,
                },
            )

            # Callback de retry
            if on_retry:
                await on_retry(erro_info, tentativa + 1)

            await asyncio.sleep(delay_total)

    # Todas tentativas falharam
    logger.error(
        f"[{servico}] Todas as {max_tentativas} tentativas falharam. Último erro: {ultimo_erro}",
        extra={
            "servico": servico,
            "max_tentativas": max_tentativas,
            "categoria": erro_info.categoria.value if erro_info else "desconhecido",
            "correlation_id": correlation_id,
        },
    )
    raise ultimo_erro


def com_retry(servico: str = "default", on_retry: Callable[[ErroIntegracao, int], Awaitable[None]] | None = None):
    """
    Decorator para adicionar retry automático.

    Args:
        servico: Nome do serviço para configuração
        on_retry: Callback chamado em cada retry

    Example:
        @com_retry("sefaz")
        async def consultar_nfe(chave: str):
            ...
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Extrair correlation_id se passado
            correlation_id = kwargs.pop("correlation_id", None)

            return await retry_com_backoff(
                func, *args, servico=servico, correlation_id=correlation_id, on_retry=on_retry, **kwargs
            )

        return wrapper

    return decorator


class RetryContext:
    """
    Context manager para retry com estado.

    Example:
        async with RetryContext("sefaz", max_tentativas=3) as ctx:
            while ctx.deve_tentar():
                try:
                    resultado = await operacao()
                    break
                except Exception as e:
                    await ctx.registrar_erro(e)
    """

    def __init__(self, servico: str, max_tentativas: int | None = None, correlation_id: str | None = None):
        config = RetryConfigs.get(servico)
        self.servico = servico
        self.max_tentativas = max_tentativas or config.max_tentativas
        self.base_delay = config.base_delay
        self.max_delay = config.max_delay
        self.jitter = config.jitter
        self.correlation_id = correlation_id

        self._tentativa_atual = 0
        self._ultimo_erro: ErroIntegracao | None = None
        self._sucesso = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def deve_tentar(self) -> bool:
        """Verifica se deve fazer mais uma tentativa."""
        if self._sucesso:
            return False
        if self._tentativa_atual >= self.max_tentativas:
            return False
        if self._ultimo_erro and not self._ultimo_erro.pode_retentar:
            return False
        return True

    async def registrar_erro(self, erro: Exception):
        """Registra erro e aguarda antes do próximo retry."""
        self._tentativa_atual += 1
        self._ultimo_erro = ClassificadorErros.classificar(
            erro, self.servico, self._tentativa_atual, self.correlation_id
        )

        if not self.deve_tentar():
            raise erro

        # Calcular e aguardar delay
        delay = min(self.base_delay * (2 ** (self._tentativa_atual - 1)), self.max_delay)
        jitter = random.uniform(0, delay * self.jitter)  # noqa: S311

        logger.warning(
            f"[{self.servico}] Tentativa {self._tentativa_atual}/{self.max_tentativas} "
            f"falhou. Aguardando {delay + jitter:.1f}s..."
        )

        await asyncio.sleep(delay + jitter)

    def marcar_sucesso(self):
        """Marca operação como bem-sucedida."""
        self._sucesso = True

    @property
    def tentativas(self) -> int:
        """Retorna número de tentativas realizadas."""
        return self._tentativa_atual

    @property
    def ultimo_erro(self) -> ErroIntegracao | None:
        """Retorna último erro registrado."""
        return self._ultimo_erro
