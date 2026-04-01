"""
Comutador de Endpoints.

Gerencia troca automática entre endpoints principal e contingência.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .uf_matrix import (
    MatrizContingencia,
)

logger = logging.getLogger(__name__)


class StatusEndpoint(Enum):
    """Status de um endpoint."""

    DISPONIVEL = "disponivel"
    INDISPONIVEL = "indisponivel"
    DEGRADADO = "degradado"  # Lento mas funcionando
    DESCONHECIDO = "desconhecido"


@dataclass
class EstadoEndpoint:
    """Estado de um endpoint."""

    status: StatusEndpoint = StatusEndpoint.DESCONHECIDO
    ultima_verificacao: datetime | None = None
    falhas_consecutivas: int = 0
    tempo_medio_resposta: float = 0.0
    ultima_falha: datetime | None = None
    motivo_falha: str | None = None


@dataclass
class ConfiguracaoComutacao:
    """Configuração do comutador de endpoints."""

    # Número de falhas para marcar como indisponível
    falhas_para_indisponivel: int = 3
    # Tempo para considerar endpoint recuperado (minutos)
    tempo_recuperacao: int = 5
    # Tempo máximo de resposta antes de considerar degradado (ms)
    limite_degradacao_ms: float = 5000.0
    # Intervalo de verificação automática (segundos)
    intervalo_verificacao: int = 60


class ComutadorEndpoints:
    """Gerencia comutação entre endpoints principal e contingência."""

    def __init__(self, config: ConfiguracaoComutacao | None = None):
        self.config = config or ConfiguracaoComutacao()
        self._estados: dict[str, EstadoEndpoint] = {}
        self._usando_contingencia: dict[str, bool] = {}
        self._lock = asyncio.Lock()

    def _gerar_chave(self, uf: str, tipo_doc: str) -> str:
        """Gera chave única para UF + tipo de documento."""
        return f"{uf.upper()}:{tipo_doc.lower()}"

    async def obter_endpoint(self, uf: str, tipo_documento: str, servico: str) -> tuple[str, bool]:
        """
        Obtém endpoint ativo para UF e tipo de documento.

        Args:
            uf: Sigla da UF
            tipo_documento: Tipo (nfe, cte, mdfe)
            servico: Nome do serviço (NfeStatusServico, etc)

        Returns:
            Tupla (url, usando_contingencia)
        """
        chave = self._gerar_chave(uf, tipo_documento)

        # Obter configuração
        if tipo_documento.lower() == "nfe":
            config = MatrizContingencia.obter_config_nfe(uf)
        elif tipo_documento.lower() == "cte":
            config = MatrizContingencia.obter_config_cte(uf)
        elif tipo_documento.lower() == "mdfe":
            config = MatrizContingencia.obter_config_mdfe(uf)
        else:
            raise ValueError(f"Tipo de documento não suportado: {tipo_documento}")

        # Verificar se deve usar contingência
        async with self._lock:
            usando_contingencia = self._usando_contingencia.get(chave, False)
            estado = self._estados.get(chave, EstadoEndpoint())

            # Verificar se pode voltar ao principal
            if usando_contingencia and estado.ultima_falha:
                tempo_desde_falha = datetime.utcnow() - estado.ultima_falha
                if tempo_desde_falha > timedelta(minutes=self.config.tempo_recuperacao):
                    # Tentar voltar ao principal
                    self._usando_contingencia[chave] = False
                    usando_contingencia = False
                    logger.info(f"Tentando retornar ao endpoint principal: {chave}")

        # Resolver URL
        if usando_contingencia and config.contingencia:
            url_base = config.contingencia.url
            logger.debug(f"Usando contingência para {chave}")
        else:
            url_base = config.principal.url

        # Resolver URL se for identificador
        url = MatrizContingencia.resolver_url(url_base, servico)

        return url, usando_contingencia

    async def registrar_sucesso(self, uf: str, tipo_documento: str, tempo_resposta_ms: float):
        """
        Registra sucesso de requisição.

        Args:
            uf: Sigla da UF
            tipo_documento: Tipo do documento
            tempo_resposta_ms: Tempo de resposta em ms
        """
        chave = self._gerar_chave(uf, tipo_documento)

        async with self._lock:
            estado = self._estados.get(chave, EstadoEndpoint())

            # Atualizar estado
            estado.status = StatusEndpoint.DISPONIVEL
            estado.ultima_verificacao = datetime.utcnow()
            estado.falhas_consecutivas = 0

            # Média móvel do tempo de resposta
            if estado.tempo_medio_resposta == 0:
                estado.tempo_medio_resposta = tempo_resposta_ms
            else:
                estado.tempo_medio_resposta = estado.tempo_medio_resposta * 0.7 + tempo_resposta_ms * 0.3

            # Verificar degradação
            if tempo_resposta_ms > self.config.limite_degradacao_ms:
                estado.status = StatusEndpoint.DEGRADADO

            self._estados[chave] = estado

            # Se estava em contingência e principal voltou, registrar
            if self._usando_contingencia.get(chave, False):
                logger.info(f"Endpoint principal restaurado: {chave} (tempo: {tempo_resposta_ms:.0f}ms)")
                self._usando_contingencia[chave] = False

    async def registrar_falha(self, uf: str, tipo_documento: str, motivo: str) -> bool:
        """
        Registra falha de requisição.

        Args:
            uf: Sigla da UF
            tipo_documento: Tipo do documento
            motivo: Motivo da falha

        Returns:
            True se deve usar contingência
        """
        chave = self._gerar_chave(uf, tipo_documento)

        async with self._lock:
            estado = self._estados.get(chave, EstadoEndpoint())

            # Atualizar estado
            estado.falhas_consecutivas += 1
            estado.ultima_verificacao = datetime.utcnow()
            estado.ultima_falha = datetime.utcnow()
            estado.motivo_falha = motivo

            # Verificar se deve marcar como indisponível
            if estado.falhas_consecutivas >= self.config.falhas_para_indisponivel:
                estado.status = StatusEndpoint.INDISPONIVEL

                # Ativar contingência se disponível
                config = MatrizContingencia.obter_config_nfe(uf)
                if config.contingencia and not self._usando_contingencia.get(chave, False):
                    self._usando_contingencia[chave] = True
                    logger.warning(
                        f"Ativando contingência para {chave}: {motivo}. Falhas: {estado.falhas_consecutivas}"
                    )

            self._estados[chave] = estado

            return self._usando_contingencia.get(chave, False)

    async def forcar_contingencia(self, uf: str, tipo_documento: str, motivo: str = "Forçado manualmente"):
        """Força uso de contingência para UF."""
        chave = self._gerar_chave(uf, tipo_documento)

        async with self._lock:
            self._usando_contingencia[chave] = True
            estado = self._estados.get(chave, EstadoEndpoint())
            estado.status = StatusEndpoint.INDISPONIVEL
            estado.motivo_falha = motivo
            estado.ultima_falha = datetime.utcnow()
            self._estados[chave] = estado

        logger.warning(f"Contingência forçada para {chave}: {motivo}")

    async def desativar_contingencia(self, uf: str, tipo_documento: str):
        """Desativa contingência e volta ao principal."""
        chave = self._gerar_chave(uf, tipo_documento)

        async with self._lock:
            self._usando_contingencia[chave] = False
            estado = self._estados.get(chave, EstadoEndpoint())
            estado.status = StatusEndpoint.DESCONHECIDO
            estado.falhas_consecutivas = 0
            self._estados[chave] = estado

        logger.info(f"Contingência desativada para {chave}")

    def obter_status(self, uf: str, tipo_documento: str) -> dict:
        """Obtém status atual do endpoint."""
        chave = self._gerar_chave(uf, tipo_documento)
        estado = self._estados.get(chave, EstadoEndpoint())

        return {
            "uf": uf,
            "tipo_documento": tipo_documento,
            "status": estado.status.value,
            "usando_contingencia": self._usando_contingencia.get(chave, False),
            "falhas_consecutivas": estado.falhas_consecutivas,
            "tempo_medio_resposta_ms": estado.tempo_medio_resposta,
            "ultima_verificacao": estado.ultima_verificacao.isoformat() if estado.ultima_verificacao else None,
            "ultima_falha": estado.ultima_falha.isoformat() if estado.ultima_falha else None,
            "motivo_falha": estado.motivo_falha,
        }

    def obter_todos_status(self) -> dict[str, dict]:
        """Obtém status de todos os endpoints monitorados."""
        resultado = {}
        for chave, estado in self._estados.items():
            resultado[chave] = {
                "status": estado.status.value,
                "usando_contingencia": self._usando_contingencia.get(chave, False),
                "falhas_consecutivas": estado.falhas_consecutivas,
                "tempo_medio_resposta_ms": estado.tempo_medio_resposta,
            }
        return resultado

    async def resetar_estado(self, uf: str, tipo_documento: str):
        """Reseta estado de um endpoint."""
        chave = self._gerar_chave(uf, tipo_documento)

        async with self._lock:
            if chave in self._estados:
                del self._estados[chave]
            if chave in self._usando_contingencia:
                del self._usando_contingencia[chave]

        logger.info(f"Estado resetado para {chave}")


# Instância singleton
_comutador_instance: ComutadorEndpoints | None = None


def get_comutador() -> ComutadorEndpoints:
    """Obtém instância do comutador."""
    global _comutador_instance
    if _comutador_instance is None:
        _comutador_instance = ComutadorEndpoints()
    return _comutador_instance
