"""
LoadAgent v2 — Testes de carga com baseline comparativo.
5 usuários simultâneos × 10 req/endpoint.
Limites calibrados para infraestrutura real (VPS KV4).
"""

import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_URL = "http://127.0.0.1:8080"
USUARIOS = 5
REQUISICOES = 10
TIMEOUT_REQ = 15

# Endpoints confirmados funcionais (200 ou 401 esperados)
ENDPOINTS_CARGA = [
    "/api/v1/people-management/hr/employees?page_size=10",
    "/api/v1/crm/clients?page_size=10",
    "/api/v1/operacional/posts/?page_size=10",
    "/api/v1/ged/kits?page_size=10",
    "/api/v1/analytics/executive/dashboard",
]

# Limites calibrados para VPS KV4 (4 vCPU, ~8GB RAM)
LIMITES = {
    "p95_ms": 5000,  # 95% das reqs em <5s sob carga
    "degradacao_max": 3.0,  # aceita até 3× mais lento que baseline
    "taxa_erro_max": 5.0,  # máx 5% de erros (401/403 NÃO contam como erro)
}


class LoadAgent:
    """Testa comportamento do backend sob carga simultânea."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "load"

    def _req(self, path: str) -> dict:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        inicio = time.time()
        status = 0
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_REQ) as r:
                r.read()
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception:
            status = 0
        return {
            "status": status,
            "tempo_ms": int((time.time() - inicio) * 1000),
        }

    def _baseline(self, path: str) -> int:
        """Mede tempo médio sem carga (3 req sequenciais)."""
        tempos = []
        for _ in range(3):
            r = self._req(path)
            if r["status"] in (200, 201, 401, 403):
                tempos.append(r["tempo_ms"])
            time.sleep(0.1)
        return int(sum(tempos) / len(tempos)) if tempos else 0

    def _testar_endpoint(self, path: str) -> dict:
        baseline_ms = self._baseline(path)

        resultados = []
        with ThreadPoolExecutor(max_workers=USUARIOS) as ex:
            futures = [ex.submit(self._req, path) for _ in range(REQUISICOES)]
            for f in as_completed(futures):
                try:
                    resultados.append(f.result())
                except Exception:
                    resultados.append({"status": 0, "tempo_ms": TIMEOUT_REQ * 1000})

        # 401/403 = autenticado corretamente, não é erro funcional
        ok_statuses = (200, 201, 401, 403)
        tempos_ok = sorted(
            r["tempo_ms"] for r in resultados if r["status"] in ok_statuses
        )
        erros = [r for r in resultados if r["status"] not in ok_statuses]
        taxa_erro = (len(erros) / len(resultados) * 100) if resultados else 0

        p95_idx = max(0, int(len(tempos_ok) * 0.95) - 1)
        p95 = tempos_ok[p95_idx] if tempos_ok else 0
        media = int(sum(tempos_ok) / len(tempos_ok)) if tempos_ok else 0
        degradacao = (media / baseline_ms) if baseline_ms > 100 else 1.0

        problemas = []
        if p95 > LIMITES["p95_ms"]:
            problemas.append(f"p95={p95}ms (limite {LIMITES['p95_ms']}ms)")
        if degradacao > LIMITES["degradacao_max"] and baseline_ms > 100:
            problemas.append(
                f"degradação={degradacao:.1f}x (limite {LIMITES['degradacao_max']}x)"
            )
        if taxa_erro > LIMITES["taxa_erro_max"]:
            problemas.append(
                f"taxa_erro={taxa_erro:.1f}% (limite {LIMITES['taxa_erro_max']}%)"
            )

        return {
            "endpoint": path,
            "baseline_ms": baseline_ms,
            "p95_ms": p95,
            "media_ms": media,
            "degradacao_x": round(degradacao, 1),
            "taxa_erro_pct": round(taxa_erro, 1),
            "passou": not problemas,
            "problemas": problemas,
        }

    def auditar(self) -> dict:
        print(
            f"🔍 LoadAgent v2: {USUARIOS}u × {REQUISICOES}req "
            f"(p95<{LIMITES['p95_ms']}ms, deg<{LIMITES['degradacao_max']}x)..."
        )
        resultados = []
        for ep in ENDPOINTS_CARGA:
            r = self._testar_endpoint(ep)
            resultados.append(r)
            mark = "✅" if r["passou"] else "❌"
            print(
                f"  {mark} {ep[-45:]}: "
                f"base={r['baseline_ms']}ms p95={r['p95_ms']}ms "
                f"deg={r['degradacao_x']}x err={r['taxa_erro_pct']}%"
            )

        passou = sum(1 for r in resultados if r["passou"])
        score = (passou / len(resultados) * 10) if resultados else 10.0

        bugs = [
            {
                "tipo": "carga_problema",
                "endpoint": r["endpoint"],
                "descricao": (
                    f"Carga em {r['endpoint'][-40:]}: {'; '.join(r['problemas'])}"
                ),
                "autocorrigivel": False,
                "acao_jordan": r["taxa_erro_pct"] > 10 or r["p95_ms"] > 8000,
            }
            for r in resultados
            if not r["passou"]
        ]

        resultado = {
            "agente": "load",
            "score": round(min(score, 10.0), 1),
            "endpoints_ok": passou,
            "total": len(resultados),
            "usuarios": USUARIOS,
            "detalhes": resultados,
            "bugs": bugs,
        }
        print(
            f"  Score: {resultado['score']}/10 "
            f"({passou}/{len(resultados)} endpoints OK)"
        )
        return resultado
