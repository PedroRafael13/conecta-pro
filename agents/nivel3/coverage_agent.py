"""
CoverageAgent — Verifica se o frontend cobre os endpoints do backend.
Detecta:
- Endpoints no backend sem chamada no frontend
- Chamadas no frontend para endpoints inexistentes
"""
import json
import re
import urllib.request
from pathlib import Path


FRONTEND_DIR = Path("/opt/conecta-pro/frontend/src")
BASE_URL = "http://127.0.0.1:8080"


class CoverageAgent:
    """Cruza cobertura frontend ↔ backend."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "coverage"

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read())
        except Exception:
            return {}

    def ler_endpoints_backend(self) -> dict:
        """
        Lê endpoints do backend.
        Tenta OpenAPI primeiro; em produção (openapi desabilitado),
        varre os controllers diretamente.
        """
        # Tentar OpenAPI
        spec = self._get("/openapi.json")
        if spec.get("paths"):
            endpoints = {}
            for path, methods in spec["paths"].items():
                for method, details in methods.items():
                    if method in ["get", "post", "put", "delete", "patch"]:
                        endpoints[f"{method.upper()} {path}"] = {
                            "path": path, "method": method.upper(),
                        }
            return endpoints

        # Fallback: varrer controllers do backend
        return self._ler_endpoints_controllers()

    def _ler_endpoints_controllers(self) -> dict:
        """Extrai endpoints lendo os arquivos de controller."""
        endpoints = {}
        backend_dir = Path("/opt/conecta-pro/backend/modules")
        route_pattern = re.compile(
            r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            re.IGNORECASE,
        )
        prefix_pattern = re.compile(
            r'APIRouter\([^)]*prefix\s*=\s*["\']([^"\']+)["\']',
        )
        for fpath in backend_dir.rglob("*controller*.py"):
            if "__pycache__" in str(fpath):
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            prefix_match = prefix_pattern.search(content)
            prefix = prefix_match.group(1) if prefix_match else ""
            for m in route_pattern.finditer(content):
                method = m.group(1).upper()
                path = prefix + m.group(2)
                endpoints[f"{method} {path}"] = {
                    "path": path, "method": method,
                }
        return endpoints

    def ler_chamadas_frontend(self) -> dict:
        """Varre o frontend buscando todas as chamadas de API."""
        chamadas = {}
        patterns = [
            re.compile(r'fetch\(["\']([^"\']*api/v1[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'axios\.\w+\(["\']([^"\']*api/v1[^"\']*)["\']', re.IGNORECASE),
            re.compile(r'api(?:Client)?\.\w+\(["\']([^"\']+)["\']', re.IGNORECASE),
            re.compile(r'["\`](/api/v1/[^"\'`\s?]+)'),
        ]

        for fpath in FRONTEND_DIR.rglob("*.tsx"):
            if "node_modules" in str(fpath):
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pattern in patterns:
                for match in pattern.finditer(content):
                    url = match.group(1)
                    url_clean = re.sub(r"\?.*$", "", url)
                    url_clean = re.sub(
                        r"/[0-9a-f-]{8,}|/\$\{[^}]+\}|/\[[^\]]+\]",
                        "/{id}", url_clean,
                    )
                    rel = str(fpath).replace(str(FRONTEND_DIR), "")
                    chamadas.setdefault(url_clean, [])
                    if rel not in chamadas[url_clean]:
                        chamadas[url_clean].append(rel)
        return chamadas

    def _paths_match(self, path1: str, path2: str) -> bool:
        p1 = re.sub(r"/\{[^}]+\}|/[0-9a-f-]{8,}", "/{id}", path1)
        p2 = re.sub(r"/\{[^}]+\}|/[0-9a-f-]{8,}", "/{id}", path2)
        return p1 == p2 or path1 in path2 or path2 in path1

    def auditar(self) -> dict:
        """Executa auditoria completa de cobertura."""
        print("🔍 CoverageAgent: auditando cobertura API...")

        endpoints_backend = self.ler_endpoints_backend()
        chamadas_frontend = self.ler_chamadas_frontend()

        paths_backend = {
            re.sub(r"/\{[^}]+\}", "/{id}", key.split(" ", 1)[1])
            for key in endpoints_backend
        }
        paths_frontend = set(chamadas_frontend.keys())

        sem_frontend = [
            p for p in paths_backend
            if not any(self._paths_match(p, fp) for fp in paths_frontend)
            and not any(x in p for x in ["/health", "/docs", "/openapi", "/auth"])
        ]
        sem_backend = [
            p for p in paths_frontend
            if not any(self._paths_match(p, bp) for bp in paths_backend)
        ]

        total_backend = len(paths_backend)
        cobertos = total_backend - len(sem_frontend)
        cobertura_pct = (cobertos / total_backend * 100) if total_backend else 0

        resultado = {
            "agente": "coverage",
            "score": round(min(cobertura_pct / 10, 10.0), 1),
            "cobertura_pct": round(cobertura_pct, 1),
            "total_endpoints_backend": total_backend,
            "endpoints_cobertos": cobertos,
            "sem_frontend": sem_frontend[:20],
            "sem_backend": sem_backend[:10],
            "bugs": [],
        }
        if sem_frontend:
            resultado["bugs"].append({
                "tipo": "endpoints_sem_ui",
                "quantidade": len(sem_frontend),
                "descricao": f"{len(sem_frontend)} endpoints backend sem chamada no frontend",
            })
        if sem_backend:
            resultado["bugs"].append({
                "tipo": "chamadas_sem_endpoint",
                "quantidade": len(sem_backend),
                "descricao": f"{len(sem_backend)} chamadas frontend para endpoints inexistentes",
            })

        print(f"  Cobertura: {cobertura_pct:.1f}% ({cobertos}/{total_backend})")
        print(f"  Score: {resultado['score']}/10")
        return resultado
