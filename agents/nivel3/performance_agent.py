"""
PerformanceAgent — Monitora performance do sistema.
Mede tempo de resposta e detecta degradação.
"""

import subprocess
import time
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8080"
LIMITE_LENTO_MS = 2000
LIMITE_CRITICO_MS = 5000

ENDPOINTS_PERF = [
    "/api/v1/people-management/hr/employees?page_size=10",
    "/api/v1/operacional/posts/",
    "/api/v1/operacional/scales/",
    "/api/v1/ged/kits",
    "/api/v1/crm/clients",
    "/api/v1/crm/leads",
    "/api/v1/analytics/executive/dashboard",
    "/api/v1/ponto/dashboard",
]


class PerformanceAgent:
    """Monitora performance e tempo de resposta."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "performance"

    def medir_endpoint(self, path: str) -> dict:
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
            status = 0
        tempo_ms = int((time.time() - inicio) * 1000)
        return {
            "endpoint": path,
            "status": status,
            "tempo_ms": tempo_ms,
            "classificacao": (
                "critico"
                if tempo_ms > LIMITE_CRITICO_MS
                else "lento"
                if tempo_ms > LIMITE_LENTO_MS
                else "ok"
            ),
        }

    def verificar_memoria_container(self) -> dict:
        try:
            result = subprocess.run(
                [
                    "docker",
                    "stats",
                    "--no-stream",
                    "--format",
                    "{{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            containers = {}
            for line in result.stdout.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 4:
                    containers[parts[0]] = {
                        "memoria": parts[1],
                        "mem_pct": parts[2],
                        "cpu_pct": parts[3],
                    }
            return containers
        except Exception as e:
            return {"erro": str(e)}

    def auditar(self) -> dict:
        print("🔍 PerformanceAgent: medindo performance...")
        medicoes = [self.medir_endpoint(ep) for ep in ENDPOINTS_PERF]
        tempos_ok = [m["tempo_ms"] for m in medicoes if m["status"] == 200]
        tempo_medio = int(sum(tempos_ok) / len(tempos_ok)) if tempos_ok else 0
        tempo_max = max(tempos_ok) if tempos_ok else 0
        lentos = [m for m in medicoes if m["classificacao"] in ["lento", "critico"]]
        criticos = [m for m in medicoes if m["classificacao"] == "critico"]
        score = max(0, min(10.0, 10.0 - len(lentos) * 1.0 - len(criticos) * 2.0))
        resultado = {
            "agente": "performance",
            "score": round(score, 1),
            "tempo_medio_ms": tempo_medio,
            "tempo_max_ms": tempo_max,
            "endpoints_lentos": len(lentos),
            "endpoints_criticos": len(criticos),
            "total_testados": len(medicoes),
            "memoria_containers": self.verificar_memoria_container(),
            "detalhes": medicoes,
            "bugs": [
                {
                    "tipo": f"endpoint_{m['classificacao']}",
                    "endpoint": m["endpoint"],
                    "tempo_ms": m["tempo_ms"],
                    "descricao": f"Endpoint {m['classificacao']}: {m['endpoint']} ({m['tempo_ms']}ms)",
                    "autocorrigivel": False,
                }
                for m in lentos
            ],
        }
        print(
            f"  Médio: {tempo_medio}ms, Lentos: {len(lentos)}, Score: {resultado['score']}/10"
        )
        return resultado
