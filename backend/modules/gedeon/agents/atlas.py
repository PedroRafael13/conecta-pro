"""
ATLAS — Agente de Aprendizado Contínuo do GEDEON
"O sistema fica mais inteligente a cada kit montado"

Responsabilidades:
- Registrar histórico de cada kit montado
- Identificar padrões por cliente e sazonalidade
- Sugerir docs extras frequentes no checklist
- Detectar anomalias (kit muito diferente do padrão)
- Gerar insights mensais para o gestor
- Alimentar outros agentes com contexto histórico

Aprende com:
- Kits concluídos (documentos, scores, tempo)
- Documentos recusados pelo cliente
- Observações do checklist
- Movimentações sazonais por cliente
"""

import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

MESES_CRITICOS: dict[int, str] = {
    3: "Março/RAIS",
    12: "Dezembro/13º salário",
    7: "Julho/férias coletivas",
}


class Atlas:
    """
    Agente de Aprendizado — registra e aprende com
    cada ciclo de montagem de kit.
    Persiste em gedeon_kit_history e gedeon_client_patterns
    via SyncSessionLocal (psycopg2, sem subprocess).
    """

    # ── INFRA DE BANCO ────────────────────────────────────────────────────────

    def _get_session(self):  # type: ignore[return]
        from core.database.session import SyncSessionLocal

        return SyncSessionLocal()

    def _exec_sql(self, query: str, params: dict[str, Any] | None = None) -> bool:
        """Executar DML com parâmetros nomeados; retorna True em sucesso."""
        from sqlalchemy import text

        try:
            session = self._get_session()
            try:
                session.execute(text(query), params or {})
                session.commit()
                return True
            finally:
                session.close()
        except Exception as exc:  # noqa: BLE001
            logger.warning("ATLAS._exec_sql falhou: %s", exc)
            return False

    def _fetch_sql(self, query: str, params: dict[str, Any] | None = None) -> list[Any]:
        """Executar SELECT e retornar lista de mappings."""
        from sqlalchemy import text

        try:
            session = self._get_session()
            try:
                result = session.execute(text(query), params or {})
                return [dict(row) for row in result.mappings()]
            finally:
                session.close()
        except Exception as exc:  # noqa: BLE001
            logger.warning("ATLAS._fetch_sql falhou: %s", exc)
            return []

    def _atualizar_padroes(
        self,
        client_id: str,
        tipo_kit: str,
        score: int,
    ) -> None:
        """Atualizar gedeon_client_patterns com média incremental (UPSERT)."""
        self._exec_sql(
            """
            INSERT INTO gedeon_client_patterns
                (client_id, tipo_kit, score_medio, total_kits, ultimo_kit, updated_at)
            VALUES
                (:client_id, :tipo_kit, :score, 1, NOW(), NOW())
            ON CONFLICT (client_id) DO UPDATE SET
                total_kits  = gedeon_client_patterns.total_kits + 1,
                score_medio = (
                    gedeon_client_patterns.score_medio
                    * gedeon_client_patterns.total_kits
                    + :score
                ) / (gedeon_client_patterns.total_kits + 1),
                tipo_kit    = EXCLUDED.tipo_kit,
                ultimo_kit  = NOW(),
                updated_at  = NOW()
            """,
            {"client_id": client_id, "tipo_kit": tipo_kit, "score": score},
        )

    # ── REGISTRO DE APRENDIZADO ───────────────────────────────────────────────

    def registrar_kit_concluido(
        self,
        client_id: str,
        competencia: str,
        tipo_kit: str,
        score_final: int,
        docs_total: int,
        docs_auto: int,
        observacoes: str = "",
        checklist_respostas: dict[str, Any] | None = None,
        movimentacoes: list[Any] | None = None,
        pendencias: list[Any] | None = None,
        criado_por: str = "sistema",
        tempo_min: int = 0,
    ) -> bool:
        """
        Registrar kit concluído em gedeon_kit_history e
        atualizar padrão do cliente em gedeon_client_patterns.
        """
        try:
            taxa = round(docs_auto / docs_total * 100, 1) if docs_total else 0.0

            ok = self._exec_sql(
                """
                INSERT INTO gedeon_kit_history (
                    client_id, competencia, tipo_kit, score_final,
                    docs_total, docs_auto, tempo_montagem_min,
                    observacoes, checklist_respostas,
                    movimentacoes, pendencias, criado_por
                ) VALUES (
                    :client_id, :competencia, :tipo_kit, :score_final,
                    :docs_total, :docs_auto, :tempo_min,
                    :observacoes, :checklist_respostas::jsonb,
                    :movimentacoes::jsonb, :pendencias::jsonb, :criado_por
                )
                ON CONFLICT (client_id, competencia) DO UPDATE SET
                    tipo_kit            = EXCLUDED.tipo_kit,
                    score_final         = EXCLUDED.score_final,
                    docs_total          = EXCLUDED.docs_total,
                    docs_auto           = EXCLUDED.docs_auto,
                    tempo_montagem_min  = EXCLUDED.tempo_montagem_min,
                    observacoes         = EXCLUDED.observacoes,
                    checklist_respostas = EXCLUDED.checklist_respostas,
                    movimentacoes       = EXCLUDED.movimentacoes,
                    pendencias          = EXCLUDED.pendencias,
                    criado_por          = EXCLUDED.criado_por,
                    updated_at          = NOW()
                """,
                {
                    "client_id": client_id,
                    "competencia": competencia,
                    "tipo_kit": tipo_kit,
                    "score_final": score_final,
                    "docs_total": docs_total,
                    "docs_auto": docs_auto,
                    "tempo_min": tempo_min,
                    "observacoes": observacoes or "",
                    "checklist_respostas": json.dumps(checklist_respostas or {}),
                    "movimentacoes": json.dumps((movimentacoes or [])[:20]),
                    "pendencias": json.dumps((pendencias or [])[:20]),
                    "criado_por": criado_por,
                },
            )

            if ok:
                self._atualizar_padroes(client_id, tipo_kit, score_final)
                logger.info(
                    "ATLAS: kit registrado — %s %s score=%d taxa_auto=%.1f%%",
                    client_id[:8],
                    competencia,
                    score_final,
                    taxa,
                )
            return ok
        except Exception as exc:  # noqa: BLE001
            logger.warning("ATLAS: erro ao registrar kit: %s", exc)
            return False

    # ── CONTEXTO HISTÓRICO ────────────────────────────────────────────────────

    def obter_contexto_historico(
        self,
        client_id: str,
        competencia: str,
    ) -> dict[str, Any]:
        """
        Obter contexto histórico para pré-preencher
        o checklist do próximo kit.
        Busca os 6 kits anteriores + padrão do cliente.
        """
        rows = self._fetch_sql(
            """
            SELECT competencia, score_final AS score, docs_total AS docs
            FROM gedeon_kit_history
            WHERE client_id = :client_id
              AND competencia <> :competencia
            ORDER BY competencia DESC
            LIMIT 6
            """,
            {"client_id": client_id, "competencia": competencia},
        )
        kits_anteriores = [{"competencia": r["competencia"], "score": r["score"], "docs": r["docs"]} for r in rows]

        padrao = self._fetch_sql(
            """
            SELECT score_medio, total_kits, tipo_kit
            FROM gedeon_client_patterns
            WHERE client_id = :client_id
            """,
            {"client_id": client_id},
        )
        score_medio = int(padrao[0]["score_medio"]) if padrao else 100
        total_kits = int(padrao[0]["total_kits"]) if padrao else 0

        mes = int(competencia.split("-")[1]) if "-" in competencia else 0
        sazonalidade = MESES_CRITICOS.get(mes)

        return {
            "total_kits_historico": total_kits,
            "score_medio": score_medio,
            "kits_anteriores": kits_anteriores,
            "sazonalidade": sazonalidade,
            "insights": [],
            "aviso": (f"Mês especial: {sazonalidade} — atenção a documentos extras" if sazonalidade else None),
        }

    # ── DETECÇÃO DE ANOMALIA ──────────────────────────────────────────────────

    def detectar_anomalia(
        self,
        client_id: str,
        docs_atual: int,
        score_atual: int,
    ) -> str | None:
        """
        Detectar se o kit atual é muito diferente do padrão histórico.
        Requer mínimo de 3 kits para ativar (evita falsos positivos).
        """
        rows = self._fetch_sql(
            """
            SELECT score_medio, total_kits
            FROM gedeon_client_patterns
            WHERE client_id = :client_id
            """,
            {"client_id": client_id},
        )
        if not rows or int(rows[0]["total_kits"]) < 3:
            return None

        score_medio = float(rows[0]["score_medio"])
        diff = abs(score_atual - score_medio)
        if diff > 30:
            return f"ATLAS: score {score_atual}% muito diferente do histórico ({score_medio:.0f}%)"
        return None

    # ── INSIGHTS MENSAIS ──────────────────────────────────────────────────────

    def gerar_insights_mensais(self) -> list[dict[str, Any]]:
        """
        Gerar insights mensais para o gestor a partir
        dos padrões persistidos em gedeon_client_patterns.
        """
        insights: list[dict[str, Any]] = []
        mes_atual = datetime.utcnow().strftime("%Y-%m")

        # Clientes com score médio < 80 e pelo menos 2 kits
        rows = self._fetch_sql(
            """
            SELECT
                gcp.client_id,
                COALESCE(c.name, gcp.client_id) AS nome,
                gcp.score_medio,
                gcp.total_kits
            FROM gedeon_client_patterns gcp
            LEFT JOIN clients c ON c.id::text = gcp.client_id
            WHERE gcp.score_medio < 80
              AND gcp.total_kits >= 2
            ORDER BY gcp.score_medio ASC
            LIMIT 20
            """
        )
        for r in rows:
            insights.append(
                {
                    "tipo": "score_baixo",
                    "cliente": r["nome"],
                    "score": round(float(r["score_medio"]), 1),
                    "mensagem": (
                        f"Cliente {r['nome']} com score médio {float(r['score_medio']):.0f}% — revisar processo"
                    ),
                    "prioridade": "alta",
                }
            )

        # Total de kits registrados este mês
        total_rows = self._fetch_sql(
            """
            SELECT COUNT(*) AS total
            FROM gedeon_kit_history
            WHERE competencia = :competencia
            """,
            {"competencia": mes_atual},
        )
        total_mes = int(total_rows[0]["total"]) if total_rows else 0

        total_clientes = self._fetch_sql("SELECT COUNT(*) AS total FROM gedeon_client_patterns")
        total_hist = int(total_clientes[0]["total"]) if total_clientes else 0

        insights.append(
            {
                "tipo": "resumo_mes",
                "mensagem": f"{total_mes} kits registrados em {mes_atual}",
                "prioridade": "info",
                "competencia": mes_atual,
                "total_clientes_historico": total_hist,
            }
        )

        return insights


# Singleton global
atlas = Atlas()
