"""
SolidesBenefitService — Sincronização de pedidos VT/VA Sólides → kit GED.

Contexto:
- A API Sólides (Tangerino/employer.tangerino.com.br) NÃO expõe endpoint de
  benefit-orders — apenas HR/DP (employees, absences, occurrences).
- Pagamentos Sólides chegam ao Inter como PIX lump-sum para "SOLIDES"
  (counterpart_name='SOLIDES', counterpart_document=null).
- Sem breakdown por CPF/funcionário no payload Inter, não é possível popular
  solides_benefit_order_items automaticamente.
- Este serviço cria solides_benefit_orders a partir das inter_transactions
  reais e aguarda enriquecimento futuro via upload de relatório Sólides.

INV-4: Nunca simular dados — apenas dados reais.
"""

import logging
import os
from datetime import timedelta

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_SOLIDES_BASE_URL = "https://employer.tangerino.com.br"
_SOLIDES_BENEFIT_ENDPOINTS = [
    "/benefit-orders",
    "/v1/benefit-orders",
    "/benefits/orders",
    "/api/v1/benefit-orders",
    "/benefit/find-all",
    "/order/find-all",
]


def _get_solides_token() -> str:
    return os.getenv("SOLIDES_API_TOKEN", "")


def _tentar_api_benefit_orders(mes_ref: str | None) -> list[dict]:
    """
    Tenta buscar pedidos de benefícios na API Sólides.
    Retorna lista vazia se endpoint não existir (404) — documentado em §122.
    """
    token = _get_solides_token()
    if not token:
        logger.warning("[SolidesBenefit] SOLIDES_API_TOKEN não configurado")
        return []

    headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
    params = {}
    if mes_ref:
        mes, ano = mes_ref.split(".")
        import calendar

        ultimo = calendar.monthrange(int(ano), int(mes))[1]
        params["startDate"] = f"{ano}-{mes}-01"
        params["endDate"] = f"{ano}-{mes}-{ultimo}"

    for endpoint in _SOLIDES_BENEFIT_ENDPOINTS:
        try:
            resp = httpx.get(
                f"{_SOLIDES_BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("content", data) if isinstance(data, dict) else data
                logger.info("[SolidesBenefit] API OK em %s: %d pedidos", endpoint, len(items))
                return items if isinstance(items, list) else []
            logger.debug("[SolidesBenefit] %s → %d", endpoint, resp.status_code)
        except Exception as exc:
            logger.debug("[SolidesBenefit] %s → erro: %s", endpoint, exc)

    logger.info(
        "[SolidesBenefit] API Sólides não expõe endpoint de benefit-orders "
        "(todos retornaram 404). Usando fallback Inter transactions."
    )
    return []


class SolidesBenefitService:
    """
    Sincroniza pedidos de benefícios VT/VA Sólides com o kit GED.

    Métodos principais:
      sync_benefit_orders(mes_ref)  — tenta API, fallback Inter transactions
      match_inter_transactions()    — vincula orders às inter_transactions SOLIDES
      vincular_kits(mes_ref)        — preenche slots kit por CPF (requer items)
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ─── SYNC ────────────────────────────────────────────────────

    def sync_benefit_orders(self, mes_ref: str | None = None) -> dict:
        """
        Sincroniza pedidos de benefícios.

        1. Tenta API Sólides (benefit-orders) — pode retornar [] se endpoint 404
        2. Fallback: cria orders a partir das inter_transactions com SOLIDES
           como beneficiário (dados reais do extrato Inter)
        """
        # Tentativa na API
        api_orders = _tentar_api_benefit_orders(mes_ref)
        from_api = 0
        if api_orders:
            from_api = self._inserir_orders_api(api_orders)

        # Fallback: Inter transactions SOLIDES → benefit_orders
        from_inter = self._sync_from_inter_transactions(mes_ref)

        total = from_api + from_inter
        logger.info(
            "[SolidesBenefit] sync_benefit_orders: %d da API + %d do Inter = %d total",
            from_api,
            from_inter,
            total,
        )
        return {
            "synced_total": total,
            "from_api": from_api,
            "from_inter_fallback": from_inter,
            "api_available": from_api > 0,
            "mes_ref": mes_ref or "todos",
            "nota": (
                "API Sólides não expõe benefit-orders. Orders criadas a partir "
                "das inter_transactions SOLIDES (lump-sum). Items por funcionário "
                "requerem upload de relatório Sólides (PDF/CSV)."
            )
            if from_api == 0
            else None,
        }

    def _inserir_orders_api(self, api_orders: list[dict]) -> int:
        """Insere pedidos vindos da API Sólides (quando disponível)."""
        inseridos = 0
        for o in api_orders:
            order_number = str(o.get("id") or o.get("orderId") or o.get("order_id") or "")
            if not order_number:
                continue
            self.db.execute(
                text("""
                    INSERT INTO solides_benefit_orders
                        (order_number, data_pedido, data_pagamento, valor_total, status, raw_payload)
                    VALUES (:num, :dp, :dpg, :vt, :st, CAST(:rp AS JSONB))
                    ON CONFLICT (order_number) DO NOTHING
                """),
                {
                    "num": order_number,
                    "dp": o.get("orderDate") or o.get("data_pedido"),
                    "dpg": o.get("paymentDate") or o.get("data_pagamento"),
                    "vt": o.get("totalAmount") or o.get("valor_total"),
                    "st": o.get("status", "DESCONHECIDO"),
                    "rp": __import__("json").dumps(o),
                },
            )
            inseridos += 1
        if inseridos:
            self.db.commit()
        return inseridos

    def _sync_from_inter_transactions(self, mes_ref: str | None = None) -> int:
        """
        Cria solides_benefit_orders a partir das inter_transactions SOLIDES.
        Cada PIX lump-sum para SOLIDES = um pedido de benefício.
        inter_transaction_id é preenchido diretamente (já é a origem).
        """
        date_filter = ""
        params: dict = {}
        if mes_ref:
            mes, ano = mes_ref.split(".")
            import calendar

            ultimo = calendar.monthrange(int(ano), int(mes))[1]
            date_filter = "AND it.data_lancamento BETWEEN :inicio AND :fim"
            params["inicio"] = f"{ano}-{mes}-01"
            params["fim"] = f"{ano}-{mes}-{ultimo}"

        txs = self.db.execute(
            text(f"""
                SELECT it.id::text, it.data_lancamento, it.valor,
                       it.raw_payload->>'description' AS descricao
                FROM inter_transactions it
                WHERE it.tipo_operacao = 'D'
                  AND (
                    it.raw_payload->>'counterpart_name' ILIKE '%solides%'
                    OR it.raw_payload->>'counterpart_name' ILIKE '%swap%'
                    OR it.detalhes_destinatario->>'nome' ILIKE '%solides%'
                    OR it.raw_payload->>'counterpart_document' ILIKE '%10461302%'
                  )
                  {date_filter}
                ORDER BY it.data_lancamento
            """),
            params,
        ).fetchall()

        inseridos = 0
        for tx in txs:
            order_number = f"INTER-{tx[0][:8].upper()}"
            self.db.execute(
                text("""
                    INSERT INTO solides_benefit_orders
                        (order_number, data_pagamento, valor_total, status,
                         inter_transaction_id, raw_payload)
                    VALUES (:num, :dpg, :vt, 'PAGO',
                            CAST(:tx_id AS uuid), CAST(:rp AS JSONB))
                    ON CONFLICT (order_number) DO UPDATE
                      SET updated_at = NOW()
                """),
                {
                    "num": order_number,
                    "dpg": tx[1],
                    "vt": tx[2],
                    "tx_id": tx[0],
                    "rp": __import__("json").dumps({"inter_tx": tx[0], "descricao": tx[3] or ""}),
                },
            )
            inseridos += 1

        if inseridos:
            self.db.commit()
        return inseridos

    # ─── MATCH INTER ─────────────────────────────────────────────

    def match_inter_transactions(self) -> dict:
        """
        Para cada order sem inter_transaction_id: busca inter_transaction
        por valor ± 0.01 e data_pagamento ± 1 dia.
        Orders criadas via fallback já têm inter_transaction_id preenchido.
        """
        orders_sem_link = self.db.execute(
            text("""
                SELECT id::text, data_pagamento, valor_total
                FROM solides_benefit_orders
                WHERE inter_transaction_id IS NULL
            """)
        ).fetchall()

        matched = 0
        for order in orders_sem_link:
            if not order[1] or not order[2]:
                continue
            dpg = order[1]
            valor = float(order[2])
            dpg_ini = dpg - timedelta(days=1)
            dpg_fim = dpg + timedelta(days=1)

            tx = self.db.execute(
                text("""
                    SELECT id::text FROM inter_transactions
                    WHERE tipo_operacao = 'D'
                      AND data_lancamento BETWEEN :ini AND :fim
                      AND ABS(valor - :valor) <= 0.01
                      AND (
                        raw_payload->>'counterpart_name' ILIKE '%solides%'
                        OR raw_payload->>'counterpart_name' ILIKE '%swap%'
                        OR detalhes_destinatario->>'nome' ILIKE '%solides%'
                      )
                    LIMIT 1
                """),
                {"ini": dpg_ini, "fim": dpg_fim, "valor": valor},
            ).fetchone()

            if tx:
                self.db.execute(
                    text("""
                        UPDATE solides_benefit_orders
                        SET inter_transaction_id = CAST(:tx_id AS uuid), updated_at = NOW()
                        WHERE id = CAST(:oid AS uuid)
                    """),
                    {"tx_id": tx[0], "oid": order[0]},
                )
                matched += 1

        if matched:
            self.db.commit()

        total_orders = self.db.execute(text("SELECT COUNT(*) FROM solides_benefit_orders")).scalar()
        linked = self.db.execute(
            text("SELECT COUNT(*) FROM solides_benefit_orders WHERE inter_transaction_id IS NOT NULL")
        ).scalar()

        return {
            "matched_now": matched,
            "total_orders": total_orders,
            "com_inter_tx": linked,
            "sem_inter_tx": total_orders - linked,
        }

    # ─── VINCULAR KITS ───────────────────────────────────────────

    def vincular_kits(self, mes_ref: str | None = None) -> dict:
        """
        Para cada order_item com employee_id e sem kit_document_id:
          1. Encontra ged_kit do funcionário no mês correto
          2. Encontra slot vazio para comp_vt_individual ou comp_va_solides
          3. UPDATE kit_document_id + file_path

        Requer solides_benefit_order_items populados com employee_id.
        Sem a API de benefit-orders, items ficam vazios e nenhum slot é vinculado.
        """
        date_filter = ""
        params: dict = {}
        if mes_ref:
            mes, ano = mes_ref.split(".")
            import calendar

            ultimo = calendar.monthrange(int(ano), int(mes))[1]
            date_filter = "AND o.data_pagamento BETWEEN :inicio AND :fim"
            params["inicio"] = f"{ano}-{mes}-01"
            params["fim"] = f"{ano}-{mes}-{ultimo}"

        items = self.db.execute(
            text(f"""
                SELECT
                    i.id::text AS item_id,
                    i.employee_id::text,
                    i.valor_mobilidade,
                    i.valor_refeicao,
                    o.data_pagamento
                FROM solides_benefit_order_items i
                JOIN solides_benefit_orders o ON o.id = i.order_id
                WHERE i.kit_document_id IS NULL
                  AND i.employee_id IS NOT NULL
                  {date_filter}
            """),
            params,
        ).fetchall()

        vinculados = 0
        sem_slot = 0

        for item in items:
            item_id = item[0]
            employee_id = item[1]
            val_mob = float(item[2] or 0)
            val_ref = float(item[3] or 0)
            ref_date = item[4].replace(day=1).strftime("%Y-%m-%d") if item[4] else None

            if not ref_date:
                sem_slot += 1
                continue

            # Determinar document_type prioritário
            if val_mob > 0 and val_ref > 0:
                doc_type = "comp_vt_va_combinado"
            elif val_mob > 0:
                doc_type = "comp_vt_individual"
            else:
                doc_type = "comp_va_solides"

            slot = self.db.execute(
                text("""
                    SELECT gkd.id::text
                    FROM ged_kit_documents gkd
                    JOIN ged_document_kits gdk ON gdk.id = gkd.kit_id
                    WHERE gkd.employee_id = CAST(:emp_id AS uuid)
                      AND gkd.document_type = :dt
                      AND gkd.file_path IS NULL
                      AND gdk.reference_month::date = CAST(:ref AS date)
                    LIMIT 1
                """),
                {"emp_id": employee_id, "dt": doc_type, "ref": ref_date},
            ).fetchone()

            if not slot:
                sem_slot += 1
                continue

            slot_id = slot[0]
            self.db.execute(
                text("""
                    UPDATE solides_benefit_order_items
                    SET kit_document_id = CAST(:kid AS uuid)
                    WHERE id = CAST(:iid AS uuid)
                """),
                {"kid": slot_id, "iid": item_id},
            )
            self.db.execute(
                text("""
                    UPDATE ged_kit_documents
                    SET file_path = :fp,
                        source_record_id = CAST(:iid AS uuid),
                        source_module = 'solides',
                        updated_at = NOW()
                    WHERE id = CAST(:kid AS uuid)
                """),
                {
                    "fp": f"/solides/beneficio/{item_id}",
                    "iid": item_id,
                    "kid": slot_id,
                },
            )
            vinculados += 1

        if vinculados:
            self.db.commit()

        total_items = self.db.execute(text("SELECT COUNT(*) FROM solides_benefit_order_items")).scalar()

        return {
            "vinculados": vinculados,
            "sem_slot": sem_slot,
            "total_items": total_items,
            "mes_ref": mes_ref or "todos",
            "nota": (
                "solides_benefit_order_items vazio — API Sólides não expõe breakdown "
                "por funcionário. Vincular kits requer upload de relatório Sólides "
                "(PDF/CSV) e processamento manual dos items."
            )
            if total_items == 0
            else None,
        }
