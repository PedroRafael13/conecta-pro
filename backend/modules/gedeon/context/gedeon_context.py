"""
GedeonContext — Memória viva do GEDEON por cliente/competência.
Armazenado no Redis com TTL de 90 dias.
Construído continuamente à medida que eventos chegam.
Usado para pré-preencher o checklist de montagem de kit.
"""

import json
import logging
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# TTL do contexto no Redis: 90 dias
CONTEXT_TTL = 60 * 60 * 24 * 90


class GedeonContext:
    """
    Contexto acumulado do GEDEON para um cliente+competência.
    Estrutura:
    {
      "cliente_id": "uuid",
      "competencia": "2026-04",
      "score_prontidao": 0-100,
      "movimentacao_pessoal": [...],
      "ocorrencias": [...],
      "certidoes": {"status": "ok|alerta|critico"},
      "documentos_gerados": {...},
      "pendencias": [...],
      "ultima_atualizacao": "iso-datetime"
    }
    """

    def __init__(self) -> None:
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        if self._redis is None:
            try:
                from core.config import settings

                redis_url = settings.redis_url
            except Exception:
                redis_url = "redis://localhost:6379/1"
            self._redis = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

    def _key(self, cliente_id: str, competencia: str) -> str:
        return f"gedeon:ctx:{cliente_id}:{competencia}"

    async def get(
        self,
        cliente_id: str,
        competencia: str,
    ) -> dict[str, Any]:
        """Recuperar contexto do Redis."""
        await self.connect()
        try:
            raw = await self._redis.get(self._key(cliente_id, competencia))
            if raw:
                return json.loads(raw)
        except Exception as e:
            logger.warning("Erro ao ler contexto: %s", e)
        return self._contexto_vazio(cliente_id, competencia)

    async def update(
        self,
        cliente_id: str,
        competencia: str,
        campo: str,
        valor: Any,
    ) -> None:
        """Atualizar um campo do contexto."""
        await self.connect()
        try:
            ctx = await self.get(cliente_id, competencia)
            ctx[campo] = valor
            ctx["ultima_atualizacao"] = datetime.utcnow().isoformat()
            ctx["score_prontidao"] = self._calcular_score(ctx)
            await self._redis.setex(
                self._key(cliente_id, competencia),
                CONTEXT_TTL,
                json.dumps(ctx, ensure_ascii=False),
            )
        except Exception as e:
            logger.warning("Erro ao atualizar contexto: %s", e)

    async def append_evento(
        self,
        cliente_id: str,
        competencia: str,
        lista: str,
        item: dict,
    ) -> None:
        """Adicionar item a uma lista do contexto."""
        await self.connect()
        try:
            ctx = await self.get(cliente_id, competencia)
            if lista not in ctx:
                ctx[lista] = []
            # Evitar duplicatas pelo event_id
            event_id = item.get("event_id", "")
            if event_id and any(x.get("event_id") == event_id for x in ctx[lista]):
                return  # Já processado (idempotência)
            ctx[lista].append(item)
            ctx["ultima_atualizacao"] = datetime.utcnow().isoformat()
            ctx["score_prontidao"] = self._calcular_score(ctx)
            await self._redis.setex(
                self._key(cliente_id, competencia),
                CONTEXT_TTL,
                json.dumps(ctx, ensure_ascii=False),
            )
        except Exception as e:
            logger.warning("Erro ao append contexto: %s", e)

    def _calcular_score(self, ctx: dict) -> int:
        """
        Score de prontidão 0-100 para montagem do kit.
        Baseado em: certidões, documentos, pendências.
        """
        score = 100
        # Certidões críticas: -20 cada
        certidoes = ctx.get("certidoes", {})
        if certidoes.get("critico", 0) > 0:
            score -= 20 * certidoes["critico"]
        # Pendências: -10 cada
        pendencias = ctx.get("pendencias", [])
        score -= 10 * len(pendencias)
        return max(0, min(100, score))

    def _contexto_vazio(
        self,
        cliente_id: str,
        competencia: str,
    ) -> dict:
        return {
            "cliente_id": cliente_id,
            "competencia": competencia,
            "score_prontidao": 100,
            "movimentacao_pessoal": [],
            "ocorrencias": [],
            "certidoes": {"ok": 0, "alerta": 0, "critico": 0},
            "documentos_gerados": {},
            "pendencias": [],
            "tipo_kit": None,
            "ultima_atualizacao": None,
        }

    async def get_all_clients_context(
        self,
        competencia: str,
    ) -> list[dict]:
        """Recuperar contexto de todos os clientes."""
        await self.connect()
        try:
            keys = await self._redis.keys(f"gedeon:ctx:*:{competencia}")
            contexts = []
            for key in keys:
                raw = await self._redis.get(key)
                if raw:
                    contexts.append(json.loads(raw))
            return sorted(contexts, key=lambda x: x.get("score_prontidao", 100))
        except Exception as e:
            logger.warning("Erro ao listar contextos: %s", e)
            return []

    async def get_keys_for_competencia(
        self,
        competencia: str,
    ) -> list[str]:
        """Retorna lista de client_ids com contexto ativo."""
        await self.connect()
        try:
            keys = await self._redis.keys(f"gedeon:ctx:*:{competencia}")
            result = []
            for key in keys:
                parts = key.split(":")
                if len(parts) >= 4:
                    result.append(parts[2])
            return result
        except Exception as e:
            logger.warning("Erro ao listar keys: %s", e)
            return []


# Singleton global
gedeon_context = GedeonContext()
