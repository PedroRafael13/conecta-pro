"""
THEMIS — Agente de Assinaturas do GEDEON
"Nenhuma assinatura esquecida"

Responsabilidades:
- Monitorar documentos pendentes de assinatura (ged_kit_documents)
- Calcular tempo médio de assinatura por kit/cliente
- Predizer atrasos com base no histórico
- Disparar eventos GED_ASSINATURA_PENDENTE via ConectaEventBus
- Priorizar fila de assinaturas por urgência (normal/alto/critico)

Tabelas: ged_kit_documents, ged_document_kits
"""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Horas limite antes de considerar atrasado
HORAS_ALERTA = 48
HORAS_CRITICO = 72


class Themis:
    """
    Agente de Assinaturas — garante que nenhum
    documento fique esquecido sem assinar.

    Integrado com ConectaEventBus para alertas em tempo real.
    """

    async def verificar_pendentes(self, db: AsyncSession) -> list[dict[str, Any]]:
        """
        Verificar documentos pendentes de assinatura.
        Retorna lista ordenada por urgência (critico → alto → normal).
        """
        rows = await db.execute(
            text("""
                SELECT
                    gkd.id::text          AS doc_id,
                    gkd.document_type     AS tipo,
                    gkd.document_name     AS nome,
                    gkd.created_at        AS criado_em,
                    gdk.client_id::text   AS client_id,
                    gdk.reference_month::text AS competencia
                FROM ged_kit_documents gkd
                JOIN ged_document_kits gdk
                    ON gdk.id = gkd.kit_id
                WHERE gkd.is_signed = FALSE
                ORDER BY gkd.created_at ASC
            """)
        )
        registros = rows.fetchall()

        pendentes: list[dict[str, Any]] = []
        agora = datetime.utcnow()

        for row in registros:
            criado = row.criado_em
            if criado.tzinfo is not None:
                criado = criado.astimezone(UTC).replace(tzinfo=None)

            horas = (agora - criado).total_seconds() / 3600

            if horas >= HORAS_CRITICO:
                nivel = "critico"
            elif horas >= HORAS_ALERTA:
                nivel = "alto"
            else:
                nivel = "normal"

            pendentes.append(
                {
                    "doc_id": row.doc_id,
                    "tipo": row.tipo,
                    "nome": row.nome,
                    "horas_pendente": round(horas, 1),
                    "nivel": nivel,
                    "client_id": row.client_id,
                    "competencia": row.competencia,
                }
            )

        # Ordenar: critico → alto → normal
        ordem = {"critico": 0, "alto": 1, "normal": 2}
        pendentes.sort(key=lambda x: (ordem[x["nivel"]], x["horas_pendente"] * -1))
        return pendentes

    async def calcular_tempo_medio(self, db: AsyncSession, client_id: str | None = None) -> dict[str, Any]:
        """
        Calcular tempo médio de assinatura (documentos já assinados).
        """
        filtro = "AND gdk.client_id = :cid" if client_id else ""
        params = {"cid": client_id} if client_id else {}

        rows = await db.execute(
            text(f"""
                SELECT
                    AVG(
                        EXTRACT(EPOCH FROM
                            (gkd.signed_at - gkd.created_at))
                        / 3600
                    ) AS media_horas,
                    COUNT(*) AS total_assinados
                FROM ged_kit_documents gkd
                JOIN ged_document_kits gdk
                    ON gdk.id = gkd.kit_id
                WHERE gkd.is_signed = TRUE
                  AND gkd.signed_at IS NOT NULL
                  {filtro}
            """),
            params,
        )
        row = rows.fetchone()
        return {
            "media_horas": round(row.media_horas or 0, 1),
            "total_assinados": row.total_assinados or 0,
        }

    async def verificar_e_alertar(self, db: AsyncSession) -> dict[str, Any]:
        """
        Verificar pendências e publicar eventos para críticos.
        """
        from infrastructure.event_bus import (
            ConectaEvent,
            EventTypes,
            event_bus,
        )

        pendentes = await self.verificar_pendentes(db)
        criticos = [p for p in pendentes if p["nivel"] == "critico"]
        altos = [p for p in pendentes if p["nivel"] == "alto"]

        for doc in criticos:
            await event_bus.publish(
                ConectaEvent(
                    event_type=EventTypes.GED_ASSINATURA_PENDENTE,
                    payload={
                        "doc_id": doc["doc_id"],
                        "tipo": doc["tipo"],
                        "horas_pendente": doc["horas_pendente"],
                        "nivel": doc["nivel"],
                    },
                    source_module="themis",
                    cliente_id=doc["client_id"],
                    competencia=doc["competencia"],
                )
            )

        logger.info(
            "THEMIS: %d pendentes | %d críticos | %d altos",
            len(pendentes),
            len(criticos),
            len(altos),
        )
        return {
            "total_pendentes": len(pendentes),
            "criticos": len(criticos),
            "altos": len(altos),
            "normais": len(pendentes) - len(criticos) - len(altos),
        }

    async def resumo(self, db: AsyncSession) -> dict[str, Any]:
        """
        Resumo completo para o dashboard de assinaturas.
        """
        pendentes = await self.verificar_pendentes(db)
        tempo_medio = await self.calcular_tempo_medio(db)

        return {
            "agente": "THEMIS",
            "descricao": "Nenhuma assinatura esquecida",
            "timestamp": datetime.utcnow().isoformat(),
            "pendentes": {
                "total": len(pendentes),
                "critico": len([p for p in pendentes if p["nivel"] == "critico"]),
                "alto": len([p for p in pendentes if p["nivel"] == "alto"]),
                "normal": len([p for p in pendentes if p["nivel"] == "normal"]),
            },
            "tempo_medio_assinatura_horas": tempo_medio["media_horas"],
            "total_assinados": tempo_medio["total_assinados"],
            "proximos_criticos": pendentes[:5],
        }


# Singleton global
themis = Themis()
