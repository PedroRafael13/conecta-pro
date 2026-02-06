"""
Fila de Reprocessamento para documentos com erro.

Gerencia documentos que falharam e precisam ser reprocessados.
"""

from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import json
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .error_classifier import ErroIntegracao, CategoriaErro

logger = logging.getLogger(__name__)


class StatusReprocessamento(Enum):
    """Status de item na fila de reprocessamento."""
    PENDENTE = "pendente"
    EM_PROCESSAMENTO = "em_processamento"
    SUCESSO = "sucesso"
    FALHA_PERMANENTE = "falha_permanente"


@dataclass
class ItemReprocessamento:
    """Item na fila de reprocessamento."""
    id: UUID
    tipo_documento: str
    documento_id: UUID
    tenant_id: str
    status: StatusReprocessamento
    tentativas: int
    proxima_tentativa: Optional[datetime]
    ultimo_erro: Optional[Dict[str, Any]]
    dados_originais: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    worker_id: Optional[str]


class FilaReprocessamento:
    """Gerencia fila de documentos para reprocessamento."""

    MAX_TENTATIVAS = 5
    INTERVALO_BASE = timedelta(minutes=15)

    # Multiplicadores de delay por categoria de erro
    DELAY_MULTIPLIERS = {
        CategoriaErro.TIMEOUT: 1.0,
        CategoriaErro.INDISPONIVEL: 2.0,
        CategoriaErro.RATE_LIMIT: 3.0,
        CategoriaErro.REDE: 1.5,
    }

    @classmethod
    async def adicionar(
        cls,
        db_session: AsyncSession,
        tipo_documento: str,
        documento_id: UUID,
        tenant_id: str,
        erro: ErroIntegracao,
        dados_originais: Dict[str, Any]
    ) -> UUID:
        """
        Adiciona documento à fila de reprocessamento.

        Args:
            db_session: Sessão do banco
            tipo_documento: Tipo do documento (nfe, cte, esocial, etc)
            documento_id: ID do documento original
            tenant_id: ID do tenant
            erro: Informações do erro
            dados_originais: Dados para reprocessamento

        Returns:
            ID do item na fila
        """
        tentativa_atual = erro.tentativas + 1

        # Determinar status e próxima tentativa
        if tentativa_atual >= cls.MAX_TENTATIVAS:
            status = StatusReprocessamento.FALHA_PERMANENTE
            proxima_tentativa = None
            logger.error(
                f"Documento {documento_id} marcado como falha permanente "
                f"após {tentativa_atual} tentativas"
            )
        else:
            status = StatusReprocessamento.PENDENTE

            # Calcular delay com multiplicador por categoria
            multiplier = cls.DELAY_MULTIPLIERS.get(erro.categoria, 1.0)
            delay = cls.INTERVALO_BASE * (2 ** tentativa_atual) * multiplier
            proxima_tentativa = datetime.utcnow() + delay

        item_id = uuid4()

        await db_session.execute(
            text("""
            INSERT INTO fila_reprocessamento (
                id, tipo_documento, documento_id, tenant_id, status,
                tentativas, proxima_tentativa, ultimo_erro,
                dados_originais, created_at
            ) VALUES (
                :id, :tipo, :doc_id, :tenant_id, :status,
                :tentativas, :proxima, :erro, :dados, NOW()
            )
            ON CONFLICT (documento_id) DO UPDATE SET
                tentativas = EXCLUDED.tentativas,
                proxima_tentativa = EXCLUDED.proxima_tentativa,
                ultimo_erro = EXCLUDED.ultimo_erro,
                status = EXCLUDED.status,
                updated_at = NOW()
            """),
            {
                "id": item_id,
                "tipo": tipo_documento,
                "doc_id": documento_id,
                "tenant_id": tenant_id,
                "status": status.value,
                "tentativas": tentativa_atual,
                "proxima": proxima_tentativa,
                "erro": json.dumps(erro.to_dict()),
                "dados": json.dumps(dados_originais),
            }
        )

        logger.info(
            f"Documento {documento_id} adicionado à fila de reprocessamento. "
            f"Tentativa {tentativa_atual}, próxima em {proxima_tentativa}"
        )

        return item_id

    @classmethod
    async def obter_pendentes(
        cls,
        db_session: AsyncSession,
        worker_id: str,
        limite: int = 10,
        tipo_documento: Optional[str] = None
    ) -> List[ItemReprocessamento]:
        """
        Obtém itens pendentes para processamento.

        Usa FOR UPDATE SKIP LOCKED para concorrência segura.

        Args:
            db_session: Sessão do banco
            worker_id: ID do worker que está processando
            limite: Máximo de itens a retornar
            tipo_documento: Filtrar por tipo (opcional)

        Returns:
            Lista de itens para processar
        """
        filtro_tipo = "AND tipo_documento = :tipo" if tipo_documento else ""

        result = await db_session.execute(
            text(f"""
            UPDATE fila_reprocessamento
            SET status = :em_proc, worker_id = :worker, updated_at = NOW()
            WHERE id IN (
                SELECT id FROM fila_reprocessamento
                WHERE status = :pendente
                AND proxima_tentativa <= NOW()
                {filtro_tipo}
                ORDER BY proxima_tentativa
                LIMIT :limite
                FOR UPDATE SKIP LOCKED
            )
            RETURNING *
            """),
            {
                "em_proc": StatusReprocessamento.EM_PROCESSAMENTO.value,
                "pendente": StatusReprocessamento.PENDENTE.value,
                "worker": worker_id,
                "limite": limite,
                "tipo": tipo_documento,
            }
        )

        rows = result.fetchall()
        return [cls._row_to_item(row) for row in rows]

    @classmethod
    async def marcar_sucesso(
        cls,
        db_session: AsyncSession,
        item_id: UUID
    ):
        """Marca item como processado com sucesso."""
        await db_session.execute(
            text("""
            UPDATE fila_reprocessamento
            SET status = :status, updated_at = NOW()
            WHERE id = :id
            """),
            {
                "id": item_id,
                "status": StatusReprocessamento.SUCESSO.value,
            }
        )

        logger.info(f"Item {item_id} processado com sucesso")

    @classmethod
    async def marcar_falha(
        cls,
        db_session: AsyncSession,
        item_id: UUID,
        erro: ErroIntegracao
    ):
        """
        Marca item como falha e reagenda se possível.

        Se atingiu máximo de tentativas, marca como falha permanente.
        """
        # Obter item atual
        result = await db_session.execute(
            text("SELECT tentativas FROM fila_reprocessamento WHERE id = :id"),
            {"id": item_id}
        )
        row = result.fetchone()
        if not row:
            return

        tentativas = row[0] + 1

        if tentativas >= cls.MAX_TENTATIVAS or not erro.pode_retentar:
            # Falha permanente
            await db_session.execute(
                text("""
                UPDATE fila_reprocessamento
                SET status = :status, tentativas = :tent,
                    ultimo_erro = :erro, updated_at = NOW()
                WHERE id = :id
                """),
                {
                    "id": item_id,
                    "status": StatusReprocessamento.FALHA_PERMANENTE.value,
                    "tent": tentativas,
                    "erro": json.dumps(erro.to_dict()),
                }
            )
            logger.error(f"Item {item_id} marcado como falha permanente")
        else:
            # Reagendar
            multiplier = cls.DELAY_MULTIPLIERS.get(erro.categoria, 1.0)
            delay = cls.INTERVALO_BASE * (2 ** tentativas) * multiplier
            proxima = datetime.utcnow() + delay

            await db_session.execute(
                text("""
                UPDATE fila_reprocessamento
                SET status = :status, tentativas = :tent,
                    proxima_tentativa = :proxima, ultimo_erro = :erro,
                    worker_id = NULL, updated_at = NOW()
                WHERE id = :id
                """),
                {
                    "id": item_id,
                    "status": StatusReprocessamento.PENDENTE.value,
                    "tent": tentativas,
                    "proxima": proxima,
                    "erro": json.dumps(erro.to_dict()),
                }
            )
            logger.warning(
                f"Item {item_id} reagendado para {proxima} "
                f"(tentativa {tentativas})"
            )

    @classmethod
    async def obter_estatisticas(
        cls,
        db_session: AsyncSession,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtém estatísticas da fila de reprocessamento."""
        filtro = "WHERE tenant_id = :tenant_id" if tenant_id else ""

        result = await db_session.execute(
            text(f"""
            SELECT
                status,
                tipo_documento,
                COUNT(*) as total,
                AVG(tentativas) as media_tentativas
            FROM fila_reprocessamento
            {filtro}
            GROUP BY status, tipo_documento
            """),
            {"tenant_id": tenant_id} if tenant_id else {}
        )

        stats = {}
        for row in result.fetchall():
            status = row[0]
            tipo = row[1]
            if status not in stats:
                stats[status] = {}
            stats[status][tipo] = {
                "total": row[2],
                "media_tentativas": float(row[3]) if row[3] else 0,
            }

        return stats

    @classmethod
    async def limpar_antigos(
        cls,
        db_session: AsyncSession,
        dias: int = 30
    ) -> int:
        """
        Remove itens antigos processados com sucesso.

        Args:
            db_session: Sessão do banco
            dias: Itens mais antigos que isso serão removidos

        Returns:
            Número de itens removidos
        """
        resultado = await db_session.execute(
            text("""
            DELETE FROM fila_reprocessamento
            WHERE status = :sucesso
            AND updated_at < NOW() - INTERVAL ':dias days'
            """),
            {
                "sucesso": StatusReprocessamento.SUCESSO.value,
                "dias": dias,
            }
        )

        count = resultado.rowcount
        if count > 0:
            logger.info(f"Removidos {count} itens antigos da fila")

        return count

    @classmethod
    def _row_to_item(cls, row) -> ItemReprocessamento:
        """Converte row do banco para ItemReprocessamento."""
        return ItemReprocessamento(
            id=row.id,
            tipo_documento=row.tipo_documento,
            documento_id=row.documento_id,
            tenant_id=row.tenant_id,
            status=StatusReprocessamento(row.status),
            tentativas=row.tentativas,
            proxima_tentativa=row.proxima_tentativa,
            ultimo_erro=json.loads(row.ultimo_erro) if row.ultimo_erro else None,
            dados_originais=json.loads(row.dados_originais) if row.dados_originais else {},
            created_at=row.created_at,
            updated_at=row.updated_at,
            worker_id=row.worker_id,
        )
