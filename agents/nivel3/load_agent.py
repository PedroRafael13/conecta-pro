"""
LoadAgent — Testes de carga básicos.
Simula 5 usuários simultâneos × 10 requisições por endpoint.
Detecta degradação sob carga e taxa de erros.
"""

import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_URL = "http://127.0.0.1:8080"
USUARIOS_SIMULTANEOS = 5
REQUISICOES_POR_USUARIO = 10
TIMEOUT_REQ = 10

ENDPOINTS_CARGA = [
    "/api/v1/people-management/hr/employees?page_size=10",
    "/api/v1/operacional/posts/?page_size=10",
    "/api/v1/crm/clients?page_size=10",
    "/api/v1/financial/payables?page_size=10",
    "/api/v1/ponto/dashboard",
]

LIMITES = {
    "p95_ms": 3000,  # 95% das requisições deve completar em <3s
    "erro_max_pct": 5.0,  # taxa de erro máxima aceitável: 5%
    "degradacao_max": 2.0,  # fator máximo de degradação vs sem carga
}


class LoadAgent:
    """Testa comportamento do backend sob carga simultânea."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "load"

    def _uma_requisicao(self, path: str) -> dict:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        inicio = time.time()
        status = 0
        erro = None
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_REQ) as r:
                r.read()
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:
            status = 0
            erro = str(e)[:50]
        return {
            "status": status,
            "tempo_ms": int((time.time() - inicio) * 1000),
            "erro": erro,
        }

    def _medir_sem_carga(self, path: str) -> float:
        """Mede tempo base sem carga (média de 3 requisições)."""
        tempos = []
        for _ in range(3):
            r = self._uma_requisicao(path)
            if r["status"] == 200:
                tempos.append(r["tempo_ms"])
            time.sleep(0.1)
        return sum(tempos) / len(tempos) if tempos else 0

    def _testar_endpoint_sob_carga(self, path: str) -> dict:
        """Dispara N usuários × M requisições em paralelo."""
        total_reqs = USUARIOS_SIMULTANEOS * REQUISICOES_POR_USUARIO

        # Mede baseline sem carga
        baseline_ms = self._medir_sem_carga(path)

        # Dispara carga
        resultados = []
        with ThreadPoolExecutor(max_workers=USUARIOS_SIMULTANEOS) as ex:
            futures = [ex.submit(self._uma_requisicao, path) for _ in range(total_reqs)]
            for f in as_completed(futures):
                try:
                    resultados.append(f.result())
                except Exception as e:
                    resultados.append(
                        {"status": 0, "tempo_ms": TIMEOUT_REQ * 1000, "erro": str(e)}
                    )

        tempos_ok = sorted([r["tempo_ms"] for r in resultados if r["status"] == 200])
        erros = [r for r in resultados if r["status"] not in (200, 201, 401, 403)]
        taxa_erro = (len(erros) / total_reqs * 100) if total_reqs > 0 else 0

        p50 = tempos_ok[len(tempos_ok) // 2] if tempos_ok else 0
        p95_idx = int(len(tempos_ok) * 0.95)
        p95 = tempos_ok[p95_idx] if tempos_ok and p95_idx < len(tempos_ok) else 0
        media = int(sum(tempos_ok) / len(tempos_ok)) if tempos_ok else 0

        degradacao = (media / baseline_ms) if baseline_ms > 0 else 1.0

        problemas = []
        if p95 > LIMITES["p95_ms"]:
            problemas.append(f"p95={p95}ms (limite: {LIMITES['p95_ms']}ms)")
        if taxa_erro > LIMITES["erro_max_pct"]:
            problemas.append(
                f"taxa_erro={taxa_erro:.1f}% (limite: {LIMITES['erro_max_pct']}%)"
            )
        if degradacao > LIMITES["degradacao_max"] and baseline_ms > 0:
            problemas.append(
                f"degradação={degradacao:.1f}x sob carga "
                f"(limite: {LIMITES['degradacao_max']}x)"
            )

        return {
            "endpoint": path,
            "total_reqs": total_reqs,
            "taxa_erro_pct": round(taxa_erro, 1),
            "p50_ms": p50,
            "p95_ms": p95,
            "media_ms": media,
            "baseline_ms": int(baseline_ms),
            "degradacao_fator": round(degradacao, 2),
            "problemas": problemas,
            "ok": len(problemas) == 0,
        }

    def auditar(self) -> dict:
        print(
            f"🔍 LoadAgent: {USUARIOS_SIMULTANEOS} usuários × "
            f"{REQUISICOES_POR_USUARIO} reqs por endpoint..."
        )
        resultados = []
        for ep in ENDPOINTS_CARGA:
            print(f"  Testando: {ep}")
            r = self._testar_endpoint_sob_carga(ep)
            resultados.append(r)

        com_problemas = [r for r in resultados if not r["ok"]]
        score = max(0.0, 10.0 - len(com_problemas) * (10.0 / len(ENDPOINTS_CARGA)))

        bugs = [
            {
                "tipo": "carga_problema",
                "endpoint": r["endpoint"],
                "descricao": (f"Carga em {r['endpoint']}: {'; '.join(r['problemas'])}"),
                "autocorrigivel": False,
                "acao_jordan": r["taxa_erro_pct"] > 10 or r["p95_ms"] > 5000,
            }
            for r in com_problemas
        ]

        resultado = {
            "agente": "load",
            "score": round(min(score, 10.0), 1),
            "endpoints_testados": len(ENDPOINTS_CARGA),
            "com_problemas": len(com_problemas),
            "usuarios_simultaneos": USUARIOS_SIMULTANEOS,
            "reqs_por_usuario": REQUISICOES_POR_USUARIO,
            "detalhes": resultados,
            "bugs": bugs,
        }
        print(
            f"  Endpoints: {len(ENDPOINTS_CARGA)} | "
            f"Problemas: {len(com_problemas)} | "
            f"Score: {resultado['score']}/10"
        )
        return resultado
