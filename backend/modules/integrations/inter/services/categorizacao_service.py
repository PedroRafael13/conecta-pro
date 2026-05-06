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
    if not partes:
        return ("", "")
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
        2. Heurísticas H1-H6 por valor (tabela real Conecta Mais)
        3. Faixa salarial CLT R$1.500-R$3.000
        4. Fallback: 'outros' — confiança 0.2

        Prioridade: histórico > H1 > H2 > H5 > H6 > H3 > H4 > salário > fallback
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

        v = float(valor)

        # H1 — R$32,00 exato = VT R$10 + VR R$22 (valor único e específico da tabela)
        if v == 32.0:
            return {
                "categoria": "vt_va_combinado",
                "confianca": 0.92,
                "fonte": "H1_vt_va_32_exato",
                "incluir_no_kit": True,
            }

        # H2 — Múltiplos de R$32 (N dias de VT+VR combinados; máximo 20 dias/mês)
        if v > 32.0 and round(v % 32, 2) == 0 and v <= 32 * 20:
            return {
                "categoria": "vt_va_combinado",
                "confianca": 0.85,
                "fonte": "H2_multiplo_32",
                "incluir_no_kit": True,
            }

        # H5 — Valores exatos da tabela de diárias da empresa
        # Portaria Diurno=R$90, Portaria Noturno=R$100, ASG/Ajudante/Supervisão=R$70, Jardineiro=R$80
        if v in {70.0, 80.0, 90.0, 100.0}:
            return {
                "categoria": "diaria_avulsa",
                "confianca": 0.88,
                "fonte": "H5_diaria_exata",
                "incluir_no_kit": False,
            }

        # H6 — Múltiplos dos valores de diária (N dias; máximo 20 diárias/mês)
        for base in [100.0, 90.0, 80.0, 70.0]:
            if v > base and round(v % base, 2) == 0 and v / base <= 20:
                return {
                    "categoria": "diaria_avulsa",
                    "confianca": 0.80,
                    "fonte": "H6_multiplo_diaria",
                    "incluir_no_kit": False,
                }

        # H3 — Múltiplos de R$10 entre R$10 e R$200, não múltiplos de R$22 (VT unitário = R$10/dia)
        if round(v % 10, 2) == 0 and 10 <= v <= 200 and round(v % 22, 2) != 0:
            return {
                "categoria": "vale_transporte",
                "confianca": 0.75,
                "fonte": "H3_multiplo_10_vt",
                "incluir_no_kit": True,
            }

        # H4 — Múltiplos de R$22 entre R$22 e R$440 (VA unitário = R$22/dia)
        if round(v % 22, 2) == 0 and 22 <= v <= 440:
            return {
                "categoria": "vale_alimentacao",
                "confianca": 0.75,
                "fonte": "H4_multiplo_22_va",
                "incluir_no_kit": True,
            }

        # Faixa salarial CLT Conecta Mais: R$1.670 a R$2.700 com margem
        if 1500 <= v <= 3000:
            return {
                "categoria": "salario",
                "confianca": 0.65,
                "fonte": "heuristica_faixa_salarial",
                "incluir_no_kit": True,
            }

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

    def auto_processar(self, mes_ref: str | None = None) -> dict:
        """
        Processa todas as transações com confiança < 0.8 (ou sem categoria).
        mes_ref: 'YYYY-MM' ou None para todos os meses.
        Respeita INV-4: não toca em transações com confiança >= 0.8.
        """
        filtro_mes = ""
        params: dict = {}
        if mes_ref:
            # Aceita YYYY-MM e converte para filtro de data
            ano, mes = mes_ref.split("-")
            import calendar as _cal

            ultimo_dia = _cal.monthrange(int(ano), int(mes))[1]
            filtro_mes = "AND it.data_lancamento BETWEEN :inicio AND :fim"
            params["inicio"] = f"{ano}-{mes}-01"
            params["fim"] = f"{ano}-{mes}-{ultimo_dia}"

        pares = self.db.execute(
            text(f"""
                SELECT
                    it.raw_payload->>'counterpart_name' as nome,
                    TO_CHAR(it.data_lancamento, 'MM.YYYY') as mes_ref_fmt,
                    COUNT(*) as qtd
                FROM inter_transactions it
                LEFT JOIN inter_transaction_categorias itc ON itc.transaction_id = it.id
                WHERE it.tipo_operacao = 'D'
                  AND (
                    itc.id IS NULL
                    OR (itc.sugerido_por_ia = true AND itc.confianca_sugestao < 0.8)
                  )
                  {filtro_mes}
                GROUP BY nome, mes_ref_fmt
                ORDER BY mes_ref_fmt, qtd DESC
            """),
            params,
        ).fetchall()

        total_processadas = 0
        total_categorizadas = 0

        for par in pares:
            nome = par.nome or ""
            mes_fmt = par.mes_ref_fmt

            if nome:
                res = self.auto_categorizar_colaborador(nome, mes_fmt, apenas_sem_categoria=False)
                total_processadas += res.get("total_transacoes", 0)
                total_categorizadas += res.get("auto_categorizadas", 0)
            else:
                # Sem nome: heurística por valor diretamente
                txs = self.db.execute(
                    text(f"""
                        SELECT it.id, it.valor
                        FROM inter_transactions it
                        LEFT JOIN inter_transaction_categorias itc ON itc.transaction_id = it.id
                        WHERE it.tipo_operacao = 'D'
                          AND (it.raw_payload->>'counterpart_name' IS NULL OR it.raw_payload->>'counterpart_name' = '')
                          AND (
                            itc.id IS NULL
                            OR (itc.sugerido_por_ia = true AND itc.confianca_sugestao < 0.8)
                          )
                          AND TO_CHAR(it.data_lancamento, 'MM.YYYY') = :mes_fmt
                          {filtro_mes}
                    """),
                    {"mes_fmt": mes_fmt, **params},
                ).fetchall()

                for tx in txs:
                    sugestao = self.sugerir_categoria("", float(tx.valor), mes_fmt)
                    doc_type = CATEGORIA_PARA_DOC_TYPE.get(sugestao["categoria"])
                    self.db.execute(
                        text("""
                            INSERT INTO inter_transaction_categorias
                                (transaction_id, categoria, document_type, observacao,
                                 incluir_no_kit, sugerido_por_ia, confianca_sugestao,
                                 categorizado_por, categorizado_em, updated_at)
                            VALUES (CAST(:tid AS uuid), :cat, :doc, NULL, :kit, true, :conf, NULL, NOW(), NOW())
                            ON CONFLICT (transaction_id) DO UPDATE SET
                                categoria = EXCLUDED.categoria,
                                document_type = EXCLUDED.document_type,
                                incluir_no_kit = EXCLUDED.incluir_no_kit,
                                confianca_sugestao = EXCLUDED.confianca_sugestao,
                                updated_at = NOW()
                            WHERE inter_transaction_categorias.sugerido_por_ia = true
                              AND inter_transaction_categorias.confianca_sugestao < 0.8
                        """),
                        {
                            "tid": str(tx.id),
                            "cat": sugestao["categoria"],
                            "doc": doc_type,
                            "kit": sugestao["incluir_no_kit"],
                            "conf": sugestao["confianca"],
                        },
                    )
                    total_processadas += 1
                    total_categorizadas += 1
                self.db.commit()

        # Breakdown final
        filtro_data_breakdown = ""
        if mes_ref:
            ano, mes = mes_ref.split("-")
            import calendar as _cal2

            ultimo_dia = _cal2.monthrange(int(ano), int(mes))[1]
            filtro_data_breakdown = f"AND it.data_lancamento BETWEEN '{ano}-{mes}-01' AND '{ano}-{mes}-{ultimo_dia}'"

        rows = self.db.execute(
            text(f"""
                SELECT itc.categoria, COUNT(*) as qtd
                FROM inter_transaction_categorias itc
                JOIN inter_transactions it ON it.id = itc.transaction_id
                WHERE it.tipo_operacao = 'D'
                  {filtro_data_breakdown}
                GROUP BY itc.categoria ORDER BY qtd DESC
            """)
        ).fetchall()

        return {
            "processadas": total_processadas,
            "categorizadas": total_categorizadas,
            "mes_ref": mes_ref or "todos",
            "breakdown": {r.categoria: r.qtd for r in rows},
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
