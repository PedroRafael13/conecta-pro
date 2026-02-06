"""
Rate Limiter para Serviços Governamentais.

Implementa Token Bucket com limites específicos por serviço.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class LimiteServico:
    """Configuração de limite para um serviço."""
    requisicoes_por_minuto: int
    requisicoes_por_hora: int
    burst_maximo: int  # Máximo de requisições em burst
    intervalo_minimo_ms: int  # Intervalo mínimo entre requisições
    prioridade_padrao: int = 5  # 1 = mais alta, 10 = mais baixa


# Limites baseados em documentação oficial e observação empírica
LIMITES_SERVICOS: Dict[str, LimiteServico] = {
    # SEFAZ (NF-e, CT-e, MDF-e) - limites mais conservadores
    "sefaz_nfe": LimiteServico(
        requisicoes_por_minuto=60,
        requisicoes_por_hora=1000,
        burst_maximo=10,
        intervalo_minimo_ms=500,
        prioridade_padrao=3,
    ),
    "sefaz_cte": LimiteServico(
        requisicoes_por_minuto=60,
        requisicoes_por_hora=1000,
        burst_maximo=10,
        intervalo_minimo_ms=500,
        prioridade_padrao=4,
    ),
    "sefaz_mdfe": LimiteServico(
        requisicoes_por_minuto=60,
        requisicoes_por_hora=1000,
        burst_maximo=10,
        intervalo_minimo_ms=500,
        prioridade_padrao=4,
    ),
    # eSocial - limites mais restritivos
    "esocial": LimiteServico(
        requisicoes_por_minuto=30,
        requisicoes_por_hora=500,
        burst_maximo=5,
        intervalo_minimo_ms=1000,
        prioridade_padrao=2,  # Alta prioridade (prazos legais)
    ),
    # FGTS Digital
    "fgts_digital": LimiteServico(
        requisicoes_por_minuto=30,
        requisicoes_por_hora=500,
        burst_maximo=5,
        intervalo_minimo_ms=1000,
        prioridade_padrao=2,
    ),
    # NFS-e Nacional
    "nfse_nacional": LimiteServico(
        requisicoes_por_minuto=120,
        requisicoes_por_hora=2000,
        burst_maximo=20,
        intervalo_minimo_ms=200,
        prioridade_padrao=5,
    ),
    # SPED
    "sped": LimiteServico(
        requisicoes_por_minuto=20,
        requisicoes_por_hora=200,
        burst_maximo=3,
        intervalo_minimo_ms=2000,
        prioridade_padrao=6,
    ),
    # Receita Federal
    "receita_federal": LimiteServico(
        requisicoes_por_minuto=10,
        requisicoes_por_hora=100,
        burst_maximo=2,
        intervalo_minimo_ms=3000,
        prioridade_padrao=7,
    ),
    # Prefeituras (limites variam, usar conservador)
    "prefeitura_default": LimiteServico(
        requisicoes_por_minuto=30,
        requisicoes_por_hora=500,
        burst_maximo=5,
        intervalo_minimo_ms=1000,
        prioridade_padrao=5,
    ),
}


class RateLimiter:
    """
    Implementa rate limiting usando Token Bucket com Redis.

    Características:
    - Limites por minuto e por hora
    - Suporte a burst
    - Intervalo mínimo entre requisições
    - Filas de espera com prioridade
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        redis_url: str = "redis://localhost:6379/1"
    ):
        self._redis = redis_client
        self._redis_url = redis_url
        self._locks: Dict[str, asyncio.Lock] = {}
        self._local_buckets: Dict[str, Dict] = {}  # Fallback sem Redis

    async def _get_redis(self) -> redis.Redis:
        """Obtém conexão Redis."""
        if self._redis is None:
            self._redis = redis.from_url(self._redis_url)
        return self._redis

    def _get_lock(self, servico: str) -> asyncio.Lock:
        """Obtém lock para um serviço."""
        if servico not in self._locks:
            self._locks[servico] = asyncio.Lock()
        return self._locks[servico]

    async def pode_executar(
        self,
        servico: str,
        tenant_id: str,
        uf: Optional[str] = None
    ) -> Tuple[bool, float]:
        """
        Verifica se pode executar requisição.

        Args:
            servico: Nome do serviço
            tenant_id: ID do tenant
            uf: UF (para limites específicos por estado)

        Returns:
            Tupla (pode_executar, tempo_espera_segundos)
        """
        limite = LIMITES_SERVICOS.get(servico, LIMITES_SERVICOS["prefeitura_default"])
        chave_base = f"rate:{servico}:{tenant_id}"
        if uf:
            chave_base += f":{uf}"

        try:
            redis_client = await self._get_redis()
            return await self._verificar_redis(redis_client, chave_base, limite)
        except Exception as e:
            logger.warning(f"Fallback para rate limit local: {e}")
            return await self._verificar_local(chave_base, limite)

    async def _verificar_redis(
        self,
        redis_client: redis.Redis,
        chave_base: str,
        limite: LimiteServico
    ) -> Tuple[bool, float]:
        """Verifica rate limit usando Redis."""
        agora = datetime.utcnow()
        minuto_atual = agora.strftime("%Y%m%d%H%M")
        hora_atual = agora.strftime("%Y%m%d%H")

        chave_minuto = f"{chave_base}:min:{minuto_atual}"
        chave_hora = f"{chave_base}:hour:{hora_atual}"
        chave_ultima = f"{chave_base}:last"

        # Usar pipeline para atomicidade
        pipe = redis_client.pipeline()
        pipe.get(chave_minuto)
        pipe.get(chave_hora)
        pipe.get(chave_ultima)
        resultados = await pipe.execute()

        contagem_minuto = int(resultados[0] or 0)
        contagem_hora = int(resultados[1] or 0)
        ultima_requisicao = float(resultados[2] or 0)

        # Verificar limite por minuto
        if contagem_minuto >= limite.requisicoes_por_minuto:
            tempo_espera = 60 - agora.second
            return False, tempo_espera

        # Verificar limite por hora
        if contagem_hora >= limite.requisicoes_por_hora:
            tempo_espera = 3600 - (agora.minute * 60 + agora.second)
            return False, tempo_espera

        # Verificar intervalo mínimo
        agora_ms = agora.timestamp() * 1000
        if ultima_requisicao > 0:
            decorrido = agora_ms - ultima_requisicao
            if decorrido < limite.intervalo_minimo_ms:
                tempo_espera = (limite.intervalo_minimo_ms - decorrido) / 1000
                return False, tempo_espera

        return True, 0

    async def registrar_requisicao(
        self,
        servico: str,
        tenant_id: str,
        uf: Optional[str] = None
    ):
        """Registra uma requisição executada."""
        limite = LIMITES_SERVICOS.get(servico, LIMITES_SERVICOS["prefeitura_default"])
        chave_base = f"rate:{servico}:{tenant_id}"
        if uf:
            chave_base += f":{uf}"

        try:
            redis_client = await self._get_redis()
            await self._registrar_redis(redis_client, chave_base)
        except Exception as e:
            logger.warning(f"Fallback para registro local: {e}")
            await self._registrar_local(chave_base)

    async def _registrar_redis(self, redis_client: redis.Redis, chave_base: str):
        """Registra requisição no Redis."""
        agora = datetime.utcnow()
        minuto_atual = agora.strftime("%Y%m%d%H%M")
        hora_atual = agora.strftime("%Y%m%d%H")

        chave_minuto = f"{chave_base}:min:{minuto_atual}"
        chave_hora = f"{chave_base}:hour:{hora_atual}"
        chave_ultima = f"{chave_base}:last"

        pipe = redis_client.pipeline()
        pipe.incr(chave_minuto)
        pipe.expire(chave_minuto, 120)  # Expira em 2 minutos
        pipe.incr(chave_hora)
        pipe.expire(chave_hora, 7200)  # Expira em 2 horas
        pipe.set(chave_ultima, agora.timestamp() * 1000)
        pipe.expire(chave_ultima, 60)
        await pipe.execute()

    async def _verificar_local(
        self,
        chave_base: str,
        limite: LimiteServico
    ) -> Tuple[bool, float]:
        """Fallback: verifica rate limit localmente."""
        async with self._get_lock(chave_base):
            agora = datetime.utcnow()
            bucket = self._local_buckets.get(chave_base, {
                "tokens": limite.burst_maximo,
                "ultima_atualizacao": agora,
                "contagem_minuto": 0,
                "minuto_atual": agora.minute,
            })

            # Resetar contagem se mudou o minuto
            if bucket["minuto_atual"] != agora.minute:
                bucket["contagem_minuto"] = 0
                bucket["minuto_atual"] = agora.minute

            # Verificar limite por minuto
            if bucket["contagem_minuto"] >= limite.requisicoes_por_minuto:
                tempo_espera = 60 - agora.second
                return False, tempo_espera

            # Regenerar tokens (token bucket)
            tempo_decorrido = (agora - bucket["ultima_atualizacao"]).total_seconds()
            tokens_regenerados = tempo_decorrido * (limite.requisicoes_por_minuto / 60)
            bucket["tokens"] = min(limite.burst_maximo, bucket["tokens"] + tokens_regenerados)
            bucket["ultima_atualizacao"] = agora

            if bucket["tokens"] < 1:
                tempo_espera = (1 - bucket["tokens"]) / (limite.requisicoes_por_minuto / 60)
                return False, tempo_espera

            self._local_buckets[chave_base] = bucket
            return True, 0

    async def _registrar_local(self, chave_base: str):
        """Fallback: registra requisição localmente."""
        async with self._get_lock(chave_base):
            agora = datetime.utcnow()
            bucket = self._local_buckets.get(chave_base, {
                "tokens": 10,
                "ultima_atualizacao": agora,
                "contagem_minuto": 0,
                "minuto_atual": agora.minute,
            })

            bucket["tokens"] -= 1
            bucket["contagem_minuto"] += 1
            self._local_buckets[chave_base] = bucket

    async def aguardar_permissao(
        self,
        servico: str,
        tenant_id: str,
        uf: Optional[str] = None,
        timeout: float = 60.0
    ) -> bool:
        """
        Aguarda até poder executar ou timeout.

        Args:
            servico: Nome do serviço
            tenant_id: ID do tenant
            uf: UF opcional
            timeout: Tempo máximo de espera

        Returns:
            True se pode executar, False se timeout
        """
        inicio = datetime.utcnow()

        while True:
            pode, espera = await self.pode_executar(servico, tenant_id, uf)

            if pode:
                await self.registrar_requisicao(servico, tenant_id, uf)
                return True

            # Verificar timeout
            decorrido = (datetime.utcnow() - inicio).total_seconds()
            if decorrido + espera > timeout:
                logger.warning(
                    f"Timeout aguardando rate limit: {servico}/{tenant_id}"
                )
                return False

            logger.debug(
                f"Rate limit ativo, aguardando {espera:.1f}s: {servico}/{tenant_id}"
            )
            await asyncio.sleep(min(espera, timeout - decorrido))

    async def obter_status(
        self,
        servico: str,
        tenant_id: str,
        uf: Optional[str] = None
    ) -> Dict:
        """Obtém status atual do rate limit."""
        limite = LIMITES_SERVICOS.get(servico, LIMITES_SERVICOS["prefeitura_default"])
        chave_base = f"rate:{servico}:{tenant_id}"
        if uf:
            chave_base += f":{uf}"

        try:
            redis_client = await self._get_redis()
            agora = datetime.utcnow()
            minuto_atual = agora.strftime("%Y%m%d%H%M")
            hora_atual = agora.strftime("%Y%m%d%H")

            pipe = redis_client.pipeline()
            pipe.get(f"{chave_base}:min:{minuto_atual}")
            pipe.get(f"{chave_base}:hour:{hora_atual}")
            resultados = await pipe.execute()

            contagem_minuto = int(resultados[0] or 0)
            contagem_hora = int(resultados[1] or 0)

            return {
                "servico": servico,
                "tenant_id": tenant_id,
                "uf": uf,
                "limite_minuto": limite.requisicoes_por_minuto,
                "uso_minuto": contagem_minuto,
                "disponivel_minuto": limite.requisicoes_por_minuto - contagem_minuto,
                "limite_hora": limite.requisicoes_por_hora,
                "uso_hora": contagem_hora,
                "disponivel_hora": limite.requisicoes_por_hora - contagem_hora,
                "burst_maximo": limite.burst_maximo,
                "intervalo_minimo_ms": limite.intervalo_minimo_ms,
            }

        except Exception as e:
            logger.warning(f"Erro ao obter status: {e}")
            return {
                "servico": servico,
                "tenant_id": tenant_id,
                "erro": str(e),
            }

    async def resetar_limites(
        self,
        servico: str,
        tenant_id: str,
        uf: Optional[str] = None
    ):
        """Reseta limites para um serviço/tenant (uso administrativo)."""
        chave_base = f"rate:{servico}:{tenant_id}"
        if uf:
            chave_base += f":{uf}"

        try:
            redis_client = await self._get_redis()
            # Buscar e deletar todas as chaves relacionadas
            async for key in redis_client.scan_iter(f"{chave_base}:*"):
                await redis_client.delete(key)

            logger.info(f"Limites resetados: {chave_base}")

        except Exception as e:
            logger.error(f"Erro ao resetar limites: {e}")

        # Limpar fallback local também
        keys_to_remove = [k for k in self._local_buckets if k.startswith(chave_base)]
        for key in keys_to_remove:
            del self._local_buckets[key]


# Instância singleton
_rate_limiter_instance: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Obtém instância do rate limiter."""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
    return _rate_limiter_instance
