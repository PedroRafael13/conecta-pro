"""
Outbox Pattern para Garantia de Entrega de Eventos.

Implementa transactional outbox para garantir consistência
entre operações de banco e publicação de eventos.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import Enum
import json
import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .event_bus import Event, EventBus, get_event_bus

logger = logging.getLogger(__name__)


class OutboxStatus(Enum):
    """Status de entrada no outbox."""
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    ENVIADO = "enviado"
    FALHA = "falha"


@dataclass
class OutboxEntry:
    """Entrada no outbox."""
    id: UUID = field(default_factory=uuid4)
    tenant_id: Optional[UUID] = None
    evento_tipo: str = ""
    evento_payload: Dict[str, Any] = field(default_factory=dict)
    status: OutboxStatus = OutboxStatus.PENDENTE
    tentativas: int = 0
    max_tentativas: int = 5
    erro: Optional[str] = None
    agendado_para: datetime = field(default_factory=datetime.utcnow)
    processado_em: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_event(self) -> Event:
        """Converte para Event."""
        return Event.from_dict(self.evento_payload)


class OutboxManager:
    """
    Gerenciador do Outbox para garantia de entrega.

    Características:
    - Transação atômica com banco
    - Retry automático com backoff
    - Dead letter após max tentativas
    - Processamento em batch
    """

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        event_bus: Optional[EventBus] = None
    ):
        self.db = db_session
        self.event_bus = event_bus or get_event_bus()
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def adicionar(
        self,
        evento: Event,
        db_session: Optional[AsyncSession] = None
    ) -> UUID:
        """
        Adiciona evento ao outbox (dentro de transação).

        Args:
            evento: Evento a adicionar
            db_session: Sessão do banco (para transação)

        Returns:
            ID da entrada no outbox
        """
        db = db_session or self.db

        if not db:
            # Fallback: enviar diretamente
            await self.event_bus.publicar(evento)
            return evento.id

        entry_id = uuid4()

        await db.execute(
            text("""
            INSERT INTO event_outbox (
                id, tenant_id, evento_tipo, evento_payload,
                status, tentativas, max_tentativas, agendado_para, created_at
            ) VALUES (
                :id, :tenant_id, :evento_tipo, :evento_payload,
                :status, 0, :max_tentativas, NOW(), NOW()
            )
            """),
            {
                "id": entry_id,
                "tenant_id": evento.tenant_id,
                "evento_tipo": evento.tipo,
                "evento_payload": evento.to_json(),
                "status": OutboxStatus.PENDENTE.value,
                "max_tentativas": 5,
            }
        )

        logger.debug(f"Evento adicionado ao outbox: {entry_id}")
        return entry_id

    async def adicionar_muitos(
        self,
        eventos: List[Event],
        db_session: Optional[AsyncSession] = None
    ) -> List[UUID]:
        """Adiciona múltiplos eventos ao outbox."""
        ids = []
        for evento in eventos:
            entry_id = await self.adicionar(evento, db_session)
            ids.append(entry_id)
        return ids

    async def processar_pendentes(
        self,
        batch_size: int = 100
    ) -> int:
        """
        Processa eventos pendentes no outbox.

        Args:
            batch_size: Tamanho do batch

        Returns:
            Quantidade de eventos processados
        """
        if not self.db:
            return 0

        # Obter eventos pendentes com lock
        result = await self.db.execute(
            text("""
            SELECT id, evento_tipo, evento_payload, tentativas, max_tentativas
            FROM event_outbox
            WHERE status = :status
              AND agendado_para <= NOW()
            ORDER BY created_at ASC
            LIMIT :limite
            FOR UPDATE SKIP LOCKED
            """),
            {
                "status": OutboxStatus.PENDENTE.value,
                "limite": batch_size,
            }
        )

        rows = result.fetchall()
        processados = 0

        for row in rows:
            entry_id = row.id
            tentativas = row.tentativas + 1
            max_tentativas = row.max_tentativas

            try:
                # Marcar como processando
                await self.db.execute(
                    text("""
                    UPDATE event_outbox
                    SET status = :status, tentativas = :tentativas
                    WHERE id = :id
                    """),
                    {
                        "id": entry_id,
                        "status": OutboxStatus.PROCESSANDO.value,
                        "tentativas": tentativas,
                    }
                )

                # Publicar evento
                evento = Event.from_json(row.evento_payload)
                sucesso = await self.event_bus.publicar(evento)

                if sucesso:
                    # Marcar como enviado
                    await self.db.execute(
                        text("""
                        UPDATE event_outbox
                        SET status = :status, processado_em = NOW()
                        WHERE id = :id
                        """),
                        {
                            "id": entry_id,
                            "status": OutboxStatus.ENVIADO.value,
                        }
                    )
                    processados += 1

                else:
                    raise Exception("Falha ao publicar evento")

            except Exception as e:
                logger.error(f"Erro ao processar outbox {entry_id}: {e}")

                # Determinar novo status
                if tentativas >= max_tentativas:
                    novo_status = OutboxStatus.FALHA
                else:
                    novo_status = OutboxStatus.PENDENTE

                # Calcular próxima tentativa (backoff exponencial)
                delay_segundos = min(60 * (2 ** tentativas), 3600)  # Max 1 hora

                await self.db.execute(
                    text("""
                    UPDATE event_outbox
                    SET status = :status,
                        erro = :erro,
                        agendado_para = NOW() + INTERVAL ':delay seconds'
                    WHERE id = :id
                    """),
                    {
                        "id": entry_id,
                        "status": novo_status.value,
                        "erro": str(e)[:500],
                        "delay": delay_segundos,
                    }
                )

        await self.db.commit()

        if processados > 0:
            logger.info(f"Outbox: {processados}/{len(rows)} eventos processados")

        return processados

    async def reprocessar_falhas(
        self,
        tenant_id: Optional[UUID] = None,
        max_age_hours: int = 24
    ) -> int:
        """
        Reprocessa eventos com falha.

        Args:
            tenant_id: Filtrar por tenant
            max_age_hours: Idade máxima dos eventos

        Returns:
            Quantidade de eventos reagendados
        """
        if not self.db:
            return 0

        conditions = [
            "status = :status",
            f"created_at > NOW() - INTERVAL '{max_age_hours} hours'"
        ]
        params = {"status": OutboxStatus.FALHA.value}

        if tenant_id:
            conditions.append("tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id

        result = await self.db.execute(
            text(f"""
            UPDATE event_outbox
            SET status = :novo_status,
                tentativas = 0,
                erro = NULL,
                agendado_para = NOW()
            WHERE {' AND '.join(conditions)}
            """),
            {**params, "novo_status": OutboxStatus.PENDENTE.value}
        )

        await self.db.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Outbox: {count} eventos de falha reagendados")

        return count

    async def limpar_processados(
        self,
        dias_retencao: int = 7
    ) -> int:
        """
        Remove eventos processados antigos.

        Args:
            dias_retencao: Dias para reter eventos processados

        Returns:
            Quantidade de eventos removidos
        """
        if not self.db:
            return 0

        result = await self.db.execute(
            text("""
            DELETE FROM event_outbox
            WHERE status = :status
              AND processado_em < NOW() - INTERVAL ':dias days'
            """),
            {
                "status": OutboxStatus.ENVIADO.value,
                "dias": dias_retencao,
            }
        )

        await self.db.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Outbox: {count} eventos antigos removidos")

        return count

    async def obter_estatisticas(
        self,
        tenant_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Obtém estatísticas do outbox."""
        if not self.db:
            return {}

        conditions = []
        params = {}

        if tenant_id:
            conditions.append("tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        result = await self.db.execute(
            text(f"""
            SELECT
                status,
                COUNT(*) as total,
                AVG(tentativas) as media_tentativas
            FROM event_outbox
            {where_clause}
            GROUP BY status
            """),
            params
        )

        stats = {"por_status": {}}
        for row in result.fetchall():
            stats["por_status"][row.status] = {
                "total": row.total,
                "media_tentativas": float(row.media_tentativas or 0),
            }

        # Totais
        stats["total"] = sum(s["total"] for s in stats["por_status"].values())
        stats["pendentes"] = stats["por_status"].get(
            OutboxStatus.PENDENTE.value, {}
        ).get("total", 0)
        stats["falhas"] = stats["por_status"].get(
            OutboxStatus.FALHA.value, {}
        ).get("total", 0)

        return stats

    async def iniciar_processamento_continuo(
        self,
        intervalo_segundos: int = 5
    ):
        """Inicia processamento contínuo do outbox em background."""
        if self._running:
            logger.warning("Processamento contínuo já está rodando")
            return

        self._running = True
        self._task = asyncio.create_task(
            self._loop_processamento(intervalo_segundos)
        )

        logger.info(f"Processamento contínuo do outbox iniciado (intervalo: {intervalo_segundos}s)")

    async def parar_processamento(self):
        """Para o processamento contínuo."""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Processamento contínuo do outbox parado")

    async def _loop_processamento(self, intervalo: int):
        """Loop de processamento contínuo."""
        while self._running:
            try:
                await self.processar_pendentes()
            except Exception as e:
                logger.error(f"Erro no loop de processamento do outbox: {e}")

            await asyncio.sleep(intervalo)


# Instância singleton
_outbox_manager_instance: Optional[OutboxManager] = None


def get_outbox_manager() -> OutboxManager:
    """Obtém instância do outbox manager."""
    global _outbox_manager_instance
    if _outbox_manager_instance is None:
        _outbox_manager_instance = OutboxManager()
    return _outbox_manager_instance
