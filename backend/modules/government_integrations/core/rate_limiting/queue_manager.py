"""
Gerenciador de Filas para Integrações Governamentais.

Integra Celery com rate limiting e gerenciamento de prioridades.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import redis.asyncio as redis
from celery import Celery
from celery.result import AsyncResult

from .celery_config import TaskPriority, criar_celery_app
from .rate_limiter import LIMITES_SERVICOS, RateLimiter, get_rate_limiter

logger = logging.getLogger(__name__)


class StatusFila(Enum):
    """Status de uma fila."""

    ATIVA = "ativa"
    PAUSADA = "pausada"
    DEGRADADA = "degradada"
    INDISPONIVEL = "indisponivel"


@dataclass
class TaskInfo:
    """Informações de uma task na fila."""

    task_id: str
    servico: str
    tenant_id: str
    prioridade: int
    payload: dict[str, Any]
    criada_em: datetime
    status: str
    resultado: Any | None = None
    erro: str | None = None


class GerenciadorFilas:
    """
    Gerencia filas Celery com rate limiting integrado.

    Responsabilidades:
    - Enfileirar tasks respeitando rate limits
    - Gerenciar prioridades
    - Monitorar status das filas
    - Pausar/retomar filas
    """

    def __init__(
        self,
        celery_app: Celery | None = None,
        rate_limiter: RateLimiter | None = None,
        redis_url: str = "redis://localhost:6379/0",
    ):
        self.celery = celery_app or criar_celery_app()
        self.rate_limiter = rate_limiter or get_rate_limiter()
        self._redis_url = redis_url
        self._redis: redis.Redis | None = None
        self._filas_pausadas: dict[str, bool] = {}

    async def _get_redis(self) -> redis.Redis:
        """Obtém conexão Redis."""
        if self._redis is None:
            self._redis = redis.from_url(self._redis_url)
        return self._redis

    async def enfileirar(
        self,
        task_name: str,
        servico: str,
        tenant_id: str,
        payload: dict[str, Any],
        prioridade: TaskPriority = TaskPriority.NORMAL,
        uf: str | None = None,
        aguardar_rate_limit: bool = True,
        timeout_rate_limit: float = 60.0,
    ) -> str | None:
        """
        Enfileira task respeitando rate limits.

        Args:
            task_name: Nome completo da task Celery
            servico: Serviço governamental (sefaz_nfe, esocial, etc)
            tenant_id: ID do tenant
            payload: Dados da task
            prioridade: Prioridade da task
            uf: UF para rate limit específico
            aguardar_rate_limit: Se True, aguarda rate limit liberar
            timeout_rate_limit: Timeout para aguardar rate limit

        Returns:
            task_id se enfileirada, None se bloqueada
        """
        # Verificar se fila está pausada
        fila = self._obter_fila_para_servico(servico)
        if self._filas_pausadas.get(fila, False):
            logger.warning(f"Fila {fila} está pausada, task não enfileirada")
            return None

        # Verificar/aguardar rate limit
        if aguardar_rate_limit:
            pode_executar = await self.rate_limiter.aguardar_permissao(servico, tenant_id, uf, timeout_rate_limit)
            if not pode_executar:
                logger.warning(f"Rate limit timeout para {servico}/{tenant_id}, task não enfileirada")
                return None
        else:
            pode, espera = await self.rate_limiter.pode_executar(servico, tenant_id, uf)
            if not pode:
                logger.info(f"Rate limit ativo para {servico}/{tenant_id}, aguardar {espera:.1f}s")
                return None

        # Enfileirar task
        try:
            result = self.celery.send_task(
                task_name,
                kwargs=payload,
                queue=fila,
                priority=prioridade.value,
            )

            # Registrar na fila de monitoramento
            await self._registrar_task(result.id, servico, tenant_id, prioridade, payload)

            logger.info(f"Task enfileirada: {result.id} ({task_name}) em {fila} com prioridade {prioridade.name}")

            return result.id

        except Exception as e:
            logger.error(f"Erro ao enfileirar task: {e}")
            return None

    async def enfileirar_batch(
        self,
        task_name: str,
        servico: str,
        tenant_id: str,
        payloads: list[dict[str, Any]],
        prioridade: TaskPriority = TaskPriority.BAIXA,
        uf: str | None = None,
        intervalo_ms: int = 0,
    ) -> list[str]:
        """
        Enfileira múltiplas tasks respeitando rate limits.

        Args:
            task_name: Nome da task
            servico: Serviço governamental
            tenant_id: ID do tenant
            payloads: Lista de payloads
            prioridade: Prioridade das tasks
            uf: UF para rate limit
            intervalo_ms: Intervalo entre enfileiramentos

        Returns:
            Lista de task_ids enfileirados
        """
        task_ids = []
        limite = LIMITES_SERVICOS.get(servico)
        intervalo = intervalo_ms / 1000 if intervalo_ms else ((limite.intervalo_minimo_ms / 1000) if limite else 0.5)

        for i, payload in enumerate(payloads):
            task_id = await self.enfileirar(
                task_name=task_name,
                servico=servico,
                tenant_id=tenant_id,
                payload=payload,
                prioridade=prioridade,
                uf=uf,
                aguardar_rate_limit=True,
            )

            if task_id:
                task_ids.append(task_id)

            # Intervalo entre enfileiramentos para não sobrecarregar
            if i < len(payloads) - 1 and intervalo > 0:
                await asyncio.sleep(intervalo)

        logger.info(f"Batch enfileirado: {len(task_ids)}/{len(payloads)} tasks para {servico}")

        return task_ids

    def _obter_fila_para_servico(self, servico: str) -> str:
        """Mapeia serviço para nome da fila."""
        mapeamento = {
            "sefaz_nfe": "gov.sefaz.nfe",
            "sefaz_cte": "gov.sefaz.cte",
            "sefaz_mdfe": "gov.sefaz.mdfe",
            "esocial": "gov.esocial",
            "fgts_digital": "gov.fgts",
            "nfse_nacional": "gov.nfse",
            "sped": "gov.sped",
        }
        return mapeamento.get(servico, "gov.batch")

    async def _registrar_task(
        self, task_id: str, servico: str, tenant_id: str, prioridade: TaskPriority, payload: dict
    ):
        """Registra task no Redis para monitoramento."""
        try:
            redis_client = await self._get_redis()
            chave = f"task:{task_id}"

            dados = {
                "task_id": task_id,
                "servico": servico,
                "tenant_id": tenant_id,
                "prioridade": prioridade.value,
                "criada_em": datetime.utcnow().isoformat(),
                "status": "pending",
            }

            await redis_client.hset(chave, mapping=dados)
            await redis_client.expire(chave, 86400)  # 24 horas

            # Adicionar à lista do tenant
            await redis_client.lpush(f"tenant:{tenant_id}:tasks", task_id)
            await redis_client.ltrim(
                f"tenant:{tenant_id}:tasks",
                0,
                999,  # Manter últimas 1000
            )

        except Exception as e:
            logger.warning(f"Erro ao registrar task no Redis: {e}")

    async def obter_status_task(self, task_id: str) -> TaskInfo | None:
        """Obtém status de uma task."""
        try:
            # Status do Celery
            result = AsyncResult(task_id, app=self.celery)

            # Dados do Redis
            redis_client = await self._get_redis()
            dados = await redis_client.hgetall(f"task:{task_id}")

            if not dados:
                return None

            # Decodificar bytes do Redis
            dados = {k.decode(): v.decode() for k, v in dados.items()}

            return TaskInfo(
                task_id=task_id,
                servico=dados.get("servico", ""),
                tenant_id=dados.get("tenant_id", ""),
                prioridade=int(dados.get("prioridade", 5)),
                payload={},  # Não armazenamos payload completo
                criada_em=datetime.fromisoformat(dados["criada_em"]),
                status=result.status,
                resultado=result.result if result.successful() else None,
                erro=str(result.result) if result.failed() else None,
            )

        except Exception as e:
            logger.error(f"Erro ao obter status da task: {e}")
            return None

    async def obter_tasks_tenant(self, tenant_id: str, limite: int = 50) -> list[TaskInfo]:
        """Obtém tasks recentes de um tenant."""
        try:
            redis_client = await self._get_redis()
            task_ids = await redis_client.lrange(f"tenant:{tenant_id}:tasks", 0, limite - 1)

            tasks = []
            for task_id in task_ids:
                task_id = task_id.decode() if isinstance(task_id, bytes) else task_id
                info = await self.obter_status_task(task_id)
                if info:
                    tasks.append(info)

            return tasks

        except Exception as e:
            logger.error(f"Erro ao obter tasks do tenant: {e}")
            return []

    async def pausar_fila(self, fila: str, motivo: str = ""):
        """Pausa uma fila."""
        self._filas_pausadas[fila] = True
        logger.warning(f"Fila {fila} pausada: {motivo}")

        try:
            redis_client = await self._get_redis()
            await redis_client.hset(
                "filas:status",
                fila,
                json.dumps(
                    {
                        "pausada": True,
                        "motivo": motivo,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
            )
        except Exception as e:
            logger.warning(f"Erro ao registrar pausa no Redis: {e}")

    async def retomar_fila(self, fila: str):
        """Retoma uma fila pausada."""
        self._filas_pausadas[fila] = False
        logger.info(f"Fila {fila} retomada")

        try:
            redis_client = await self._get_redis()
            await redis_client.hdel("filas:status", fila)
        except Exception as e:
            logger.warning(f"Erro ao registrar retomada no Redis: {e}")

    async def obter_status_filas(self) -> dict[str, dict]:
        """Obtém status de todas as filas."""
        filas = [
            "gov.esocial",
            "gov.fgts",
            "gov.sefaz.nfe",
            "gov.sefaz.cte",
            "gov.sefaz.mdfe",
            "gov.nfse",
            "gov.sped",
            "gov.batch",
        ]

        status = {}

        try:
            # Usar inspect do Celery
            inspect = self.celery.control.inspect()
            active = inspect.active() or {}
            reserved = inspect.reserved() or {}
            inspect.scheduled() or {}

            for fila in filas:
                # Contar tasks
                tasks_ativas = sum(
                    len([t for t in tasks if t.get("delivery_info", {}).get("routing_key") == fila.replace("gov.", "")])
                    for tasks in active.values()
                )
                tasks_reservadas = sum(
                    len([t for t in tasks if t.get("delivery_info", {}).get("routing_key") == fila.replace("gov.", "")])
                    for tasks in reserved.values()
                )

                pausada = self._filas_pausadas.get(fila, False)

                status[fila] = {
                    "status": StatusFila.PAUSADA.value if pausada else StatusFila.ATIVA.value,
                    "tasks_ativas": tasks_ativas,
                    "tasks_reservadas": tasks_reservadas,
                    "pausada": pausada,
                }

        except Exception as e:
            logger.warning(f"Erro ao obter status das filas: {e}")
            for fila in filas:
                status[fila] = {
                    "status": StatusFila.INDISPONIVEL.value,
                    "erro": str(e),
                }

        return status

    async def obter_metricas(self) -> dict[str, Any]:
        """Obtém métricas gerais do sistema de filas."""
        try:
            redis_client = await self._get_redis()

            # Rate limits por serviço
            rate_limits = {}
            for servico in LIMITES_SERVICOS.keys():
                # Obter contagens agregadas (simplificado)
                chaves_minuto = []
                async for key in redis_client.scan_iter(f"rate:{servico}:*:min:*"):
                    chaves_minuto.append(key)

                rate_limits[servico] = {
                    "tenants_ativos": len({k.decode().split(":")[2] for k in chaves_minuto}) if chaves_minuto else 0,
                }

            # Status das filas
            status_filas = await self.obter_status_filas()

            # Totais
            total_ativas = sum(f.get("tasks_ativas", 0) for f in status_filas.values())
            total_reservadas = sum(f.get("tasks_reservadas", 0) for f in status_filas.values())

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "filas": status_filas,
                "rate_limits": rate_limits,
                "totais": {
                    "tasks_ativas": total_ativas,
                    "tasks_reservadas": total_reservadas,
                    "filas_pausadas": sum(1 for f in status_filas.values() if f.get("pausada", False)),
                },
            }

        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return {"erro": str(e)}

    async def cancelar_task(self, task_id: str, tenant_id: str) -> bool:
        """Cancela uma task pendente."""
        try:
            # Verificar se pertence ao tenant
            info = await self.obter_status_task(task_id)
            if not info or info.tenant_id != tenant_id:
                logger.warning(f"Task {task_id} não encontrada ou não pertence ao tenant")
                return False

            # Revogar no Celery
            self.celery.control.revoke(task_id, terminate=True)

            # Atualizar status
            redis_client = await self._get_redis()
            await redis_client.hset(f"task:{task_id}", "status", "cancelled")

            logger.info(f"Task {task_id} cancelada")
            return True

        except Exception as e:
            logger.error(f"Erro ao cancelar task: {e}")
            return False


# Instância singleton
_queue_manager_instance: GerenciadorFilas | None = None


def get_queue_manager() -> GerenciadorFilas:
    """Obtém instância do gerenciador de filas."""
    global _queue_manager_instance
    if _queue_manager_instance is None:
        _queue_manager_instance = GerenciadorFilas()
    return _queue_manager_instance
