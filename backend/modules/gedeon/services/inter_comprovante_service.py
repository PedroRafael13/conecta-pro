"""G9.1 — InterComprovanteService: busca comprovantes de pagamento via inter_transactions."""

import calendar
import logging
from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

_STOP_WORDS = {"DA", "DE", "DO", "DOS", "DAS", "E"}


def _mes_ref_para_datas(mes_ref: str) -> tuple[date, date]:
    """
    Converte MM.YYYY → (data_inicio, data_fim) do mês.
    Ex: '03.2026' → (2026-03-01, 2026-03-31)
    """
    partes = mes_ref.split(".")
    if len(partes) != 2:
        raise ValueError(f"mes_ref inválido: {mes_ref!r} — esperado MM.YYYY")
    mes, ano = int(partes[0]), int(partes[1])
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo_dia)


def _extrair_primeiro_ultimo(nome: str) -> tuple[str, str]:
    """
    Extrai primeiro e último nome ignorando stop words.
    Decisão Jordan (INV-10): tolerante a variações — stop words filtradas.
    Ex: "GRACIENE SILVA MAIA" → ("GRACIENE", "MAIA")
    Ex: "JONHATA DE BENAION" → ("JONHATA", "BENAION")
    """
    partes = nome.upper().split()
    validas = [p for p in partes if p not in _STOP_WORDS]
    if not validas:
        validas = partes
    primeiro = validas[0] if validas else nome.upper()
    ultimo = validas[-1] if len(validas) > 1 else primeiro
    return primeiro, ultimo


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

        Matching (INV-10): nome_completo ILIKE OU (primeiro ILIKE AND último ILIKE).
        Stop words filtradas: DA, DE, DO, DOS, DAS, E.

        INV-11: retorna TODOS os tipos de pagamento — salário, VA, VT, outros.
        """
        nome_upper = nome.upper()
        primeiro, ultimo = _extrair_primeiro_ultimo(nome)
        params: dict = {
            "nome_completo": f"%{nome_upper}%",
            "primeiro": f"%{primeiro}%",
            "ultimo": f"%{ultimo}%",
            "limit": limit,
        }
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
                  UPPER(descricao) ILIKE :nome_completo
                  OR UPPER(raw_payload->>'counterpart_name') ILIKE :nome_completo
                  OR (
                      (UPPER(descricao) ILIKE :primeiro OR UPPER(raw_payload->>'counterpart_name') ILIKE :primeiro)
                      AND
                      (UPPER(descricao) ILIKE :ultimo OR UPPER(raw_payload->>'counterpart_name') ILIKE :ultimo)
                  )
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
        INV-11: todos os tipos de pagamento incluídos (salário + VA + VT + outros).
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
                    "nome_beneficiario": detalhes.get("nome") or raw.get("counterpart_name"),
                    "banco_beneficiario": detalhes.get("banco") or raw.get("counterpart_bank"),
                }
            )

        return {
            "colaborador": nome,
            "mes_ref": mes_ref,
            "total_transacoes": len(txs),
            "total_pago": round(total_valor, 2),
            "transacoes": transacoes_fmt,
            "encontrado": len(txs) > 0,
        }
