"""
TrendAgent — Detecta degradação gradual de performance.
Compara medições atuais com histórico (4 semanas) e alerta
quando algum endpoint degradou mais de 50%.
"""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


BASE_URL = "http://127.0.0.1:8080"
HISTORICO_PATH = Path("/opt/conecta-pro/reports/performance_historico.json")
HISTORICO_MAX_SEMANAS = 4
DEGRADACAO_ALERTA_PCT = 50  # alerta se 50% mais lento que média histórica

ENDPOINTS_MONITORADOS = [
    "/api/v1/people-management/hr/employees?page_size=10",
    "/api/v1/operacional/posts/",
    "/api/v1/financial/payables?page_size=10",
    "/api/v1/crm/clients?page_size=10",
    "/api/v1/analytics/executive/dashboard",
    "/api/v1/ponto/dashboard",
]


class TrendAgent:
    """Detecta degradação gradual de performance via análise histórica."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "trend"

    def _medir(self, path: str) -> dict:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        inicio = time.time()
        status = 0
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception:
            pass
        return {
            "endpoint": path,
            "status": status,
            "tempo_ms": int((time.time() - inicio) * 1000),
        }

    def _carregar_historico(self) -> dict:
        try:
            if HISTORICO_PATH.exists():
                return json.loads(HISTORICO_PATH.read_text())
        except Exception:
            pass
        return {"medicoes": []}

    def _salvar_historico(self, historico: dict):
        try:
            HISTORICO_PATH.parent.mkdir(parents=True, exist_ok=True)
            HISTORICO_PATH.write_text(
                json.dumps(historico, indent=2, ensure_ascii=False)
            )
        except Exception:
            pass

    def _media_historica(self, historico: dict, endpoint: str) -> float | None:
        """Calcula média de tempo_ms para um endpoint nas últimas semanas."""
        tempos = []
        for m in historico.get("medicoes", []):
            for e in m.get("endpoints", []):
                if e["endpoint"] == endpoint and e["status"] == 200:
                    tempos.append(e["tempo_ms"])
        return sum(tempos) / len(tempos) if tempos else None

    def auditar(self) -> dict:
        print("🔍 TrendAgent: analisando tendência de performance...")
        historico = self._carregar_historico()

        # Mede endpoints atuais
        medicoes_atuais = [self._medir(ep) for ep in ENDPOINTS_MONITORADOS]
        timestamp = datetime.now().isoformat()

        # Detecta degradações
        alertas = []
        for m in medicoes_atuais:
            if m["status"] != 200:
                continue
            media = self._media_historica(historico, m["endpoint"])
            if media and media > 0:
                degradacao_pct = ((m["tempo_ms"] - media) / media) * 100
                if degradacao_pct > DEGRADACAO_ALERTA_PCT:
                    alertas.append(
                        {
                            "endpoint": m["endpoint"],
                            "tempo_atual_ms": m["tempo_ms"],
                            "media_historica_ms": round(media, 1),
                            "degradacao_pct": round(degradacao_pct, 1),
                            "descricao": (
                                f"Degradação de {degradacao_pct:.0f}%: "
                                f"{m['endpoint']} "
                                f"({m['tempo_ms']}ms vs média {media:.0f}ms)"
                            ),
                            "autocorrigivel": False,
                            "acao_jordan": degradacao_pct > 100,
                        }
                    )

        # Salva medição atual no histórico
        historico.setdefault("medicoes", [])
        historico["medicoes"].append(
            {
                "timestamp": timestamp,
                "endpoints": medicoes_atuais,
            }
        )
        # Mantém apenas últimas N semanas (aproximado por entradas)
        max_entradas = HISTORICO_MAX_SEMANAS * 7 * 48  # ~30min cada
        if len(historico["medicoes"]) > max_entradas:
            historico["medicoes"] = historico["medicoes"][-max_entradas:]
        self._salvar_historico(historico)

        n_medicoes = len(historico["medicoes"])
        score = max(0.0, 10.0 - len(alertas) * 2.0)

        resultado = {
            "agente": "trend",
            "score": round(min(score, 10.0), 1),
            "endpoints_monitorados": len(ENDPOINTS_MONITORADOS),
            "alertas_degradacao": len(alertas),
            "historico_entradas": n_medicoes,
            "bugs": [
                {
                    "tipo": "degradacao_performance",
                    "endpoint": a["endpoint"],
                    "descricao": a["descricao"],
                    "autocorrigivel": False,
                    "acao_jordan": a.get("acao_jordan", False),
                }
                for a in alertas
            ],
            "detalhes": alertas,
        }
        print(
            f"  Medições: {len(medicoes_atuais)} | "
            f"Alertas: {len(alertas)} | "
            f"Histórico: {n_medicoes} entradas | "
            f"Score: {resultado['score']}/10"
        )
        return resultado
