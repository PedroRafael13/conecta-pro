"""
InterCategorizacaoService
Categorização de transações Inter para o GEDEON.
Decisão Jordan (2026-05-05): categorizar por tipo para o GEDEON
saber o que vai pro kit (salário, VT, VA) vs o que não vai (diárias, outros).
"""

import calendar
import logging
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Mapeamento categoria → document_type GED
CATEGORIA_PARA_DOC_TYPE: dict[str, str | None] = {
    "salario": "comp_salario_individual",
    "vale_transporte": "comp_vt_individual",
    "vale_alimentacao": "comp_va_solides",
    "vt_va_combinado": "comp_vt_va_combinado",
    "diaria_avulsa": None,
    "adiantamento": None,
    "reembolso": None,
    "fgts": None,
    "inss": None,
    "outros": None,
}

# Categorias que entram no kit documental (INV-5)
CATEGORIAS_KIT: set[str] = {cat for cat, doc in CATEGORIA_PARA_DOC_TYPE.items() if doc is not None}

_STOP_WORDS = {"DA", "DE", "DO", "DOS", "DAS", "E"}


def _split_nome(nome: str) -> tuple[str, str]:
    partes = [p for p in nome.upper().split() if p not in _STOP_WORDS]
    if not partes:
        partes = nome.upper().split()
    return partes[0], partes[-1] if len(partes) > 1 else partes[0]


class InterCategorizacaoService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ─── CATEGORIZAÇÃO MANUAL ───────────────────────────────────

    def categorizar(
        self,
        transaction_id: str,
        categoria: str,
        observacao: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        """
        Categoriza manualmente uma transação Inter.
        Sempre sobrescreve sugestão de IA (INV-6).
        Idempotente — ON CONFLICT atualiza (INV-7).
        """
        if categoria not in CATEGORIA_PARA_DOC_TYPE:
            raise ValueError(f"Categoria inválida: {categoria!r}. Válidas: {list(CATEGORIA_PARA_DOC_TYPE.keys())}")

        doc_type = CATEGORIA_PARA_DOC_TYPE[categoria]
        incluir = categoria in CATEGORIAS_KIT

        result = self.db.execute(
            text("""
                INSERT INTO inter_transaction_categorias
                    (transaction_id, categoria, document_type, observacao,
                     incluir_no_kit, sugerido_por_ia, confianca_sugestao,
                     categorizado_por, categorizado_em, updated_at)
                VALUES
                    (CAST(:tid AS uuid), :cat, :doc, :obs,
                     :kit, false, NULL,
                     CAST(:uid AS uuid), NOW(), NOW())
                ON CONFLICT (transaction_id) DO UPDATE SET
                    categoria = EXCLUDED.categoria,
                    document_type = EXCLUDED.document_type,
                    observacao = EXCLUDED.observacao,
                    incluir_no_kit = EXCLUDED.incluir_no_kit,
                    sugerido_por_ia = false,
                    confianca_sugestao = NULL,
                    categorizado_por = EXCLUDED.categorizado_por,
                    categorizado_em = NOW(),
                    updated_at = NOW()
                RETURNING id, transaction_id, categoria, document_type,
                          incluir_no_kit, sugerido_por_ia, categorizado_em
            """),
            {
                "tid": str(transaction_id),
                "cat": categoria,
                "doc": doc_type,
                "obs": observacao,
                "kit": incluir,
                "uid": str(user_id) if user_id else None,
            },
        )
        self.db.commit()
        row = result.fetchone()
        return dict(row._mapping) if row else {}

    # ─── AUTO-CATEGORIZAÇÃO ─────────────────────────────────────

    def sugerir_categoria(
        self,
        nome_colaborador: str,
        valor: float,
        mes_ref: str,
    ) -> dict:
        """
        Sugere categoria baseada em:
        1. Histórico do colaborador — últimos 3 meses — confiança 0.9
        2. Heurísticas por valor — confiança 0.5-0.7
        3. Fallback: 'outros' — confiança 0.2
        """
        primeiro, ultimo = _split_nome(nome_colaborador)

        historico = self.db.execute(
            text("""
                SELECT itc.categoria, it.valor, COUNT(*) as freq
                FROM inter_transactions it
                JOIN inter_transaction_categorias itc ON itc.transaction_id = it.id
                WHERE it.data_lancamento >= NOW() - INTERVAL '3 months'
                  AND itc.sugerido_por_ia = false
                  AND (
                    UPPER(it.raw_payload->>'counterpart_name') ILIKE :nome
                    OR (
                      UPPER(it.raw_payload->>'counterpart_name') ILIKE :primeiro
                      AND UPPER(it.raw_payload->>'counterpart_name') ILIKE :ultimo
                    )
                  )
                GROUP BY itc.categoria, it.valor
                ORDER BY freq DESC
                LIMIT 10
            """),
            {
                "nome": f"%{nome_colaborador.upper()}%",
                "primeiro": f"%{primeiro}%",
                "ultimo": f"%{ultimo}%",
            },
        ).fetchall()

        for row in historico:
            diff = abs(float(row.valor) - valor)
            pct = diff / max(valor, 0.01)
            if pct <= 0.05:
                return {
                    "categoria": row.categoria,
                    "confianca": 0.9,
                    "fonte": "historico",
                    "incluir_no_kit": row.categoria in CATEGORIAS_KIT,
                }

        # Heurísticas por valor
        v = float(valor)
        if 8 <= v <= 12:
            return {
                "categoria": "vale_transporte",
                "confianca": 0.65,
                "fonte": "heuristica_valor",
                "incluir_no_kit": True,
            }
        if 20 <= v <= 25:
            return {
                "categoria": "vale_alimentacao",
                "confianca": 0.65,
                "fonte": "heuristica_valor",
                "incluir_no_kit": True,
            }
        if 28 <= v <= 40:
            return {
                "categoria": "vt_va_combinado",
                "confianca": 0.70,
                "fonte": "heuristica_valor",
                "incluir_no_kit": True,
            }
        if v >= 800:
            return {"categoria": "salario", "confianca": 0.50, "fonte": "heuristica_valor", "incluir_no_kit": True}

        return {"categoria": "outros", "confianca": 0.20, "fonte": "fallback", "incluir_no_kit": False}

    def auto_categorizar_colaborador(
        self,
        nome_colaborador: str,
        mes_ref: str,
        apenas_sem_categoria: bool = True,
    ) -> dict:
        """
        Auto-categoriza todas as transações de um colaborador no mês.
        Se apenas_sem_categoria=True, pula as já categorizadas manualmente (INV-6).
        """
        primeiro, ultimo = _split_nome(nome_colaborador)
        mes, ano = mes_ref.split(".")
        inicio = f"{ano}-{mes}-01"
        ultimo_dia = calendar.monthrange(int(ano), int(mes))[1]
        fim = f"{ano}-{mes}-{ultimo_dia}"

        filtro_manual = ""
        if apenas_sem_categoria:
            filtro_manual = """
              AND NOT EXISTS (
                SELECT 1 FROM inter_transaction_categorias itc
                WHERE itc.transaction_id = it.id
                  AND itc.sugerido_por_ia = false
              )
            """

        txs = self.db.execute(
            text(f"""
                SELECT it.id, it.valor, it.raw_payload->>'counterpart_name' as nome
                FROM inter_transactions it
                WHERE it.data_lancamento BETWEEN :inicio AND :fim
                  AND it.tipo_operacao = 'D'
                  AND (
                    UPPER(it.raw_payload->>'counterpart_name') ILIKE :nome
                    OR (
                      UPPER(it.raw_payload->>'counterpart_name') ILIKE :primeiro
                      AND UPPER(it.raw_payload->>'counterpart_name') ILIKE :ultimo
                    )
                  )
                  {filtro_manual}
            """),
            {
                "inicio": inicio,
                "fim": fim,
                "nome": f"%{nome_colaborador.upper()}%",
                "primeiro": f"%{primeiro}%",
                "ultimo": f"%{ultimo}%",
            },
        ).fetchall()

        sugeridas = 0
        for tx in txs:
            sugestao = self.sugerir_categoria(nome_colaborador, float(tx.valor), mes_ref)
            self.db.execute(
                text("""
                    INSERT INTO inter_transaction_categorias
                        (transaction_id, categoria, document_type, observacao,
                         incluir_no_kit, sugerido_por_ia, confianca_sugestao,
                         categorizado_por, categorizado_em, updated_at)
                    VALUES
                        (CAST(:tid AS uuid), :cat, :doc, NULL,
                         :kit, true, :conf, NULL, NOW(), NOW())
                    ON CONFLICT (transaction_id) DO UPDATE SET
                        categoria = EXCLUDED.categoria,
                        document_type = EXCLUDED.document_type,
                        incluir_no_kit = EXCLUDED.incluir_no_kit,
                        sugerido_por_ia = true,
                        confianca_sugestao = EXCLUDED.confianca_sugestao,
                        updated_at = NOW()
                    WHERE inter_transaction_categorias.sugerido_por_ia = true
                """),
                {
                    "tid": str(tx.id),
                    "cat": sugestao["categoria"],
                    "doc": CATEGORIA_PARA_DOC_TYPE.get(sugestao["categoria"]),
                    "kit": sugestao["incluir_no_kit"],
                    "conf": sugestao["confianca"],
                },
            )
            sugeridas += 1

        self.db.commit()
        return {
            "colaborador": nome_colaborador,
            "mes_ref": mes_ref,
            "total_transacoes": len(txs),
            "auto_categorizadas": sugeridas,
        }

    # ─── CONSULTAS ──────────────────────────────────────────────

    def listar_por_colaborador(
        self,
        nome_colaborador: str,
        mes_ref: str,
        apenas_kit: bool = False,
    ) -> list[dict]:
        """Lista transações de um colaborador no mês com sua categorização."""
        primeiro, ultimo = _split_nome(nome_colaborador)
        mes, ano = mes_ref.split(".")
        ultimo_dia = calendar.monthrange(int(ano), int(mes))[1]
        filtro_kit = "AND itc.incluir_no_kit = true" if apenas_kit else ""

        rows = self.db.execute(
            text(f"""
                SELECT
                    it.id,
                    it.data_lancamento::date as data,
                    it.valor,
                    it.raw_payload->>'counterpart_name' as beneficiario,
                    it.descricao,
                    itc.categoria,
                    itc.document_type,
                    itc.observacao,
                    itc.incluir_no_kit,
                    itc.sugerido_por_ia,
                    itc.confianca_sugestao,
                    itc.categorizado_em
                FROM inter_transactions it
                LEFT JOIN inter_transaction_categorias itc
                    ON itc.transaction_id = it.id
                WHERE it.data_lancamento BETWEEN :inicio AND :fim
                  AND it.tipo_operacao = 'D'
                  AND (
                    UPPER(it.raw_payload->>'counterpart_name') ILIKE :nome
                    OR (
                      UPPER(it.raw_payload->>'counterpart_name') ILIKE :primeiro
                      AND UPPER(it.raw_payload->>'counterpart_name') ILIKE :ultimo
                    )
                  )
                  {filtro_kit}
                ORDER BY it.data_lancamento, it.valor DESC
            """),
            {
                "inicio": f"{ano}-{mes}-01",
                "fim": f"{ano}-{mes}-{ultimo_dia}",
                "nome": f"%{nome_colaborador.upper()}%",
                "primeiro": f"%{primeiro}%",
                "ultimo": f"%{ultimo}%",
            },
        ).fetchall()

        return [dict(r._mapping) for r in rows]

    def resumo_kit_colaborador(
        self,
        nome_colaborador: str,
        mes_ref: str,
    ) -> dict:
        """
        Retorna resumo dos pagamentos que VÃO para o kit.
        Usado pelo HERMES para decidir o que vincular.
        """
        txs = self.listar_por_colaborador(nome_colaborador, mes_ref, apenas_kit=True)
        por_tipo: dict[str, dict] = {}
        total = Decimal("0")

        for tx in txs:
            doc = tx.get("document_type") or "outros"
            if doc not in por_tipo:
                por_tipo[doc] = {"total": Decimal("0"), "count": 0}
            por_tipo[doc]["total"] += Decimal(str(tx["valor"]))
            por_tipo[doc]["count"] += 1
            total += Decimal(str(tx["valor"]))

        return {
            "colaborador": nome_colaborador,
            "mes_ref": mes_ref,
            "total_pago_kit": float(total),
            "por_tipo_documento": {k: {"total": float(v["total"]), "count": v["count"]} for k, v in por_tipo.items()},
            "transacoes": txs,
        }

    def stats_mes(self, mes_ref: str) -> dict:
        """Estatísticas de categorização do mês."""
        mes, ano = mes_ref.split(".")
        ultimo_dia = calendar.monthrange(int(ano), int(mes))[1]

        rows = self.db.execute(
            text("""
                SELECT
                    itc.categoria,
                    itc.incluir_no_kit,
                    COUNT(*) as qtd,
                    SUM(it.valor) as total_valor
                FROM inter_transaction_categorias itc
                JOIN inter_transactions it ON it.id = itc.transaction_id
                WHERE it.data_lancamento BETWEEN :inicio AND :fim
                GROUP BY itc.categoria, itc.incluir_no_kit
                ORDER BY total_valor DESC
            """),
            {
                "inicio": f"{ano}-{mes}-01",
                "fim": f"{ano}-{mes}-{ultimo_dia}",
            },
        ).fetchall()

        sem_cat = self.db.execute(
            text("""
                SELECT COUNT(*) as sem_categoria
                FROM inter_transactions it
                WHERE it.data_lancamento BETWEEN :inicio AND :fim
                  AND it.tipo_operacao = 'D'
                  AND NOT EXISTS (
                    SELECT 1 FROM inter_transaction_categorias itc
                    WHERE itc.transaction_id = it.id
                  )
            """),
            {
                "inicio": f"{ano}-{mes}-01",
                "fim": f"{ano}-{mes}-{ultimo_dia}",
            },
        ).scalar()

        return {
            "mes_ref": mes_ref,
            "sem_categoria": sem_cat or 0,
            "por_categoria": [dict(r._mapping) for r in rows],
        }
