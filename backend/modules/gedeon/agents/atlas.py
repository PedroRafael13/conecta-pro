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

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# In-memory store: {client_id: {competencia: {record}}}
_KIT_STORE: dict[str, dict[str, dict]] = {}
# Pattern store: {client_id: {"scores": [int], "total": int, "tipo_kit": str}}
_PATTERN_STORE: dict[str, dict] = {}


class Atlas:
    """
    Agente de Aprendizado — registra e aprende com
    cada ciclo de montagem de kit.
    Armazena em memória (sem subprocess/docker).
    """

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
        Registrar kit concluído para aprendizado (in-memory).
        Persiste em _KIT_STORE enquanto o processo estiver ativo.
        """
        try:
            if client_id not in _KIT_STORE:
                _KIT_STORE[client_id] = {}

            _KIT_STORE[client_id][competencia] = {
                "client_id": client_id,
                "competencia": competencia,
                "tipo_kit": tipo_kit,
                "score_final": score_final,
                "docs_total": docs_total,
                "docs_auto": docs_auto,
                "taxa_automacao": (round(docs_auto / docs_total * 100, 1) if docs_total else 0),
                "tempo_min": tempo_min,
                "observacoes": observacoes or "",
                "checklist_respostas": checklist_respostas or {},
                "movimentacoes": (movimentacoes or [])[:20],
                "pendencias": (pendencias or [])[:20],
                "criado_por": criado_por,
                "concluido_em": datetime.utcnow().isoformat(),
            }

            # Atualizar padrões do cliente
            if client_id not in _PATTERN_STORE:
                _PATTERN_STORE[client_id] = {
                    "scores": [],
                    "total": 0,
                    "tipo_kit": tipo_kit,
                }
            pat = _PATTERN_STORE[client_id]
            pat["scores"].append(score_final)
            pat["scores"] = pat["scores"][-24:]  # manter 24 meses
            pat["total"] += 1
            pat["tipo_kit"] = tipo_kit

            logger.info(
                "ATLAS: kit registrado — %s %s score=%d",
                client_id[:8],
                competencia,
                score_final,
            )
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("ATLAS: erro ao registrar kit: %s", exc)
            return False

    # ── INSIGHTS E SUGESTÕES ──────────────────────────────────────────────────

    def obter_contexto_historico(
        self,
        client_id: str,
        competencia: str,
    ) -> dict[str, Any]:
        """
        Obter contexto histórico para pré-preencher
        o checklist do próximo kit.
        """
        historico_raw = _KIT_STORE.get(client_id, {})
        kits_anteriores = [
            {
                "competencia": comp,
                "score": rec["score_final"],
                "docs": rec["docs_total"],
            }
            for comp, rec in sorted(historico_raw.items(), reverse=True)
            if comp != competencia
        ][:6]

        pat = _PATTERN_STORE.get(client_id, {})
        scores = pat.get("scores", [])
        score_medio = int(sum(scores) / len(scores)) if scores else 100
        total_kits = pat.get("total", 0)

        mes = int(competencia.split("-")[1]) if "-" in competencia else 0
        MESES_CRITICOS = {
            3: "Março/RAIS",
            12: "Dezembro/13º salário",
            7: "Julho/férias coletivas",
        }
        sazonalidade = MESES_CRITICOS.get(mes)

        return {
            "total_kits_historico": total_kits,
            "score_medio": score_medio,
            "kits_anteriores": kits_anteriores,
            "sazonalidade": sazonalidade,
            "insights": [],
            "aviso": (f"Mês especial: {sazonalidade} — atenção a documentos extras" if sazonalidade else None),
        }

    def detectar_anomalia(
        self,
        client_id: str,
        docs_atual: int,
        score_atual: int,
    ) -> str | None:
        """
        Detectar se o kit atual é muito diferente
        do padrão histórico do cliente.
        """
        pat = _PATTERN_STORE.get(client_id)
        if not pat or len(pat.get("scores", [])) < 3:
            return None

        scores = pat["scores"]
        score_medio = sum(scores) / len(scores)
        diff = abs(score_atual - score_medio)
        if diff > 30:
            return f"ATLAS: score {score_atual}% muito diferente do histórico ({score_medio:.0f}%)"
        return None

    def gerar_insights_mensais(self) -> list[dict[str, Any]]:
        """
        Gerar insights mensais para o gestor.
        """
        insights: list[dict[str, Any]] = []
        mes_atual = datetime.utcnow().strftime("%Y-%m")

        # Clientes com score baixo
        for client_id, pat in _PATTERN_STORE.items():
            scores = pat.get("scores", [])
            if len(scores) >= 2:
                score_medio = sum(scores) / len(scores)
                if score_medio < 80:
                    insights.append(
                        {
                            "tipo": "score_baixo",
                            "cliente": client_id[:8],
                            "score": round(score_medio, 1),
                            "mensagem": (
                                f"Cliente {client_id[:8]} com score médio {score_medio:.0f}% — revisar processo"
                            ),
                            "prioridade": "alta",
                        }
                    )

        # Total de kits este mês
        total_mes = sum(1 for recs in _KIT_STORE.values() for comp in recs if comp == mes_atual)
        insights.append(
            {
                "tipo": "resumo_mes",
                "mensagem": f"{total_mes} kits registrados em {mes_atual}",
                "prioridade": "info",
                "competencia": mes_atual,
                "total_clientes_historico": len(_PATTERN_STORE),
            }
        )

        return insights


# Singleton global
atlas = Atlas()
