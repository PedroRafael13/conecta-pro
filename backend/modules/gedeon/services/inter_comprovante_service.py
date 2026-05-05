"""G9.1 — InterComprovanteService: busca comprovantes de pagamento via inter_transactions."""

import logging
from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def _normalizar_nome(nome: str) -> str:
    """Remove acentos e normaliza para busca ILIKE."""
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", nome)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).upper().strip()


def _mes_ref_para_datas(mes_ref: str) -> tuple[date, date]:
    """
    Converte MM.YYYY → (data_inicio, data_fim) do mês.
    Ex: '03.2026' → (2026-03-01, 2026-03-31)
    """
    import calendar

    partes = mes_ref.split(".")
    if len(partes) != 2:
        raise ValueError(f"mes_ref inválido: {mes_ref!r} — esperado MM.YYYY")
    mes, ano = int(partes[0]), int(partes[1])
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo_dia)


class InterComprovanteService:
    """Busca transações de débito no Banco Inter filtrando por nome do colaborador."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def buscar_por_nome(
        self,
        nome: str,
        mes_ref: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Retorna transações de débito que contêm `nome` na descrição ou em
        raw_payload->>'counterpart_name'.

        Args:
            nome: Nome (parcial) do colaborador — ex: "GRACIENE" ou "JONHATA DINIZ"
            mes_ref: Filtro de mês no formato MM.YYYY — ex: "03.2026"
            limit: Máximo de registros retornados (default 50)
        """
        pattern = f"%{nome.upper()}%"
        params: dict = {"pattern": pattern, "limit": limit}
        date_filter = ""

        if mes_ref:
            inicio, fim = _mes_ref_para_datas(mes_ref)
            date_filter = "AND data_lancamento BETWEEN :inicio AND :fim"
            params["inicio"] = inicio
            params["fim"] = fim

        sql = text(f"""
            SELECT
                id,
                data_lancamento,
                tipo_operacao,
                tipo_transacao,
                valor,
                descricao,
                raw_payload,
                detalhes_destinatario,
                created_at
            FROM inter_transactions
            WHERE tipo_operacao = 'D'
              AND (
                  UPPER(descricao) ILIKE :pattern
                  OR UPPER(raw_payload->>'counterpart_name') ILIKE :pattern
              )
              {date_filter}
            ORDER BY data_lancamento DESC, valor DESC
            LIMIT :limit
        """)

        rows = (await self.db.execute(sql, params)).mappings().all()
        return [dict(r) for r in rows]

    async def gerar_resumo_pagamentos(
        self,
        nome: str,
        mes_ref: str | None = None,
    ) -> dict:
        """
        Resumo agregado dos pagamentos encontrados para um colaborador.

        Returns:
            {
                nome_buscado, mes_ref,
                total_transacoes, total_valor,
                transacoes: [...]
            }
        """
        txs = await self.buscar_por_nome(nome, mes_ref)
        total_valor = sum(float(t.get("valor") or 0) for t in txs)

        transacoes_fmt = []
        for t in txs:
            raw = t.get("raw_payload") or {}
            detalhes = t.get("detalhes_destinatario") or {}
            transacoes_fmt.append(
                {
                    "id": str(t["id"]),
                    "data": str(t["data_lancamento"]),
                    "tipo_transacao": t.get("tipo_transacao"),
                    "valor": float(t["valor"]) if t.get("valor") else None,
                    "descricao": t.get("descricao"),
                    "nome_beneficiario": (detalhes.get("nome") or raw.get("counterpart_name")),
                    "banco_beneficiario": detalhes.get("banco") or raw.get("counterpart_bank"),
                }
            )

        return {
            "nome_buscado": nome,
            "mes_ref": mes_ref,
            "total_transacoes": len(txs),
            "total_valor": round(total_valor, 2),
            "transacoes": transacoes_fmt,
        }
