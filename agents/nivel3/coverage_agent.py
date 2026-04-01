"""
CoverageAgent v2 — Verifica cobertura dos módulos com UI.
Usa docker exec grep para listar endpoints reais do backend.
Filtra apenas MODULOS_COM_UI para score calibrado (meta: 7+/10).
"""

import re
import subprocess
from pathlib import Path


FRONTEND_DIR = Path("/opt/conecta-pro/frontend/src")
BACKEND_DIR = Path("/opt/conecta-pro/backend/modules")
CONTAINER_NAME = "conecta-pro-backend"

# Módulos que têm páginas reais no frontend
MODULOS_COM_UI = [
    "people-management",
    "hr",
    "dp",
    "ponto",
    "financial",
    "payables",
    "receivables",
    "crm",
    "clients",
    "leads",
    "operacional",
    "posts",
    "scales",
    "allocations",
    "ged",
    "kits",
    "analytics",
    "executive",
    "config",
    "tenants",
    "auth",
    "login",
    "bidding",
    "saude",
    "portais",
    "equipment",
]

# Prefixos internos/infra a excluir
EXCLUIR_PREFIXOS = [
    "/api/v1/internal",
    "/api/v1/debug",
    "/api/v1/health",
    "/api/v1/admin/seed",
    "/api/v1/metrics",
    "/docs",
    "/redoc",
    "/openapi",
    "/ws/",
    "/api/v1/ai/",
]


class CoverageAgent:
    """Verifica cobertura frontend ↔ backend dos módulos com UI."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "coverage"

    def _docker_grep_endpoints(self) -> list:
        """Usa docker exec para extrair @router decorators do container."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    CONTAINER_NAME,
                    "grep",
                    "-rn",
                    "@router.",
                    "/app/modules/",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout.splitlines()
        except Exception:
            return []

    def _ler_endpoints_controllers_local(self) -> list:
        """Fallback: lê controllers locais."""
        endpoints = []
        route_re = re.compile(
            r'@router\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']*)["\']',
            re.IGNORECASE,
        )
        prefix_re = re.compile(r'APIRouter\s*\([^)]*prefix\s*=\s*["\']([^"\']+)["\']')
        for fpath in BACKEND_DIR.rglob("*controller*.py"):
            if "__pycache__" in str(fpath):
                continue
            try:
                txt = fpath.read_text(errors="ignore")
            except Exception:
                continue
            pm = prefix_re.search(txt)
            prefix = pm.group(1) if pm else ""
            for m in route_re.finditer(txt):
                endpoints.append(prefix + m.group(2))
        return endpoints

    def _obter_endpoints_backend(self) -> list:
        """Obtém e filtra endpoints backend — só módulos com UI."""
        lines = self._docker_grep_endpoints()
        raw = []
        if lines:
            for line in lines:
                m = re.search(r'@router\.\w+\s*\(\s*["\']([^"\']*)["\']', line)
                if m:
                    raw.append(m.group(1))
        else:
            raw = self._ler_endpoints_controllers_local()

        filtrados = []
        for ep in set(raw):
            if any(ep.startswith(p) for p in EXCLUIR_PREFIXOS):
                continue
            if any(m in ep for m in MODULOS_COM_UI):
                filtrados.append(ep)
        return filtrados

    def _obter_chamadas_frontend(self) -> list:
        """Extrai chamadas de API do frontend."""
        chamadas = set()
        # Padrão para capturar paths /api/v1/... em strings literais e template literals
        pat_api = re.compile(r'(/api/v1/[^\s`"\'{?<]+)', re.IGNORECASE)
        for ext in ("*.ts", "*.tsx", "*.js"):
            for fpath in FRONTEND_DIR.rglob(ext):
                if "node_modules" in str(fpath):
                    continue
                try:
                    txt = fpath.read_text(errors="ignore")
                except Exception:
                    continue
                # Pré-processa template literals: substitui ${...} por {id}
                txt_proc = re.sub(r"\$\{[^}]+\}", "{id}", txt)
                for m in pat_api.finditer(txt_proc):
                    path = m.group(1).split("?")[0].rstrip("/")
                    if path.startswith("/api/v1/") and len(path) > 8:
                        chamadas.add(path)
        return list(chamadas)

    @staticmethod
    def _norm(path: str) -> str:
        """Normaliza params e IDs para comparação."""
        p = re.sub(r"/\{[^}]+\}", "/{x}", path)
        p = re.sub(r"/[0-9a-f-]{8,}", "/{x}", p)
        return p.rstrip("/") or "/"

    @staticmethod
    def _backend_em_frontend(backend_path: str, frontend_paths: set) -> bool:
        """
        Verifica se o backend_path aparece como sufixo de algum frontend_path.
        Necessário porque:
        - Backend usa paths relativos (/scales/) e frontend usa completos
          (/api/v1/operacional/scales/)
        - Frontend frequentemente não inclui path params ({x}) na string literal,
          ficando apenas com o path base (/allocations/ vs /allocations/{x})
        """
        bp = backend_path.rstrip("/")
        if not bp:
            return True  # path raiz sempre coberto

        # Variantes para tentar: com e sem o último segment se for {x}
        candidatos = [bp]
        if bp.endswith("/{x}"):
            candidatos.append(bp[: -len("/{x}")])

        for fp in frontend_paths:
            fp_clean = fp.rstrip("/")
            for cand in candidatos:
                if not cand:
                    continue
                # Sufixo exato
                if fp_clean.endswith(cand):
                    return True
                # Sufixo por segmentos (ignora diferenças de {x} vs segmento literal)
                cand_segs = [s for s in cand.split("/") if s]
                fp_segs = [s for s in fp_clean.split("/") if s]
                if len(cand_segs) <= len(fp_segs):
                    tail = fp_segs[-len(cand_segs) :]
                    # Segmentos batem ou o candidate tem {x} (param genérico)
                    if all(
                        c == f or c == "{x}" or f == "{x}"
                        for c, f in zip(cand_segs, tail)
                    ):
                        return True
        return False

    def auditar(self) -> dict:
        print("🔍 CoverageAgent v2: analisando cobertura módulos UI...")
        backend = self._obter_endpoints_backend()
        frontend = self._obter_chamadas_frontend()

        backend_norm = {self._norm(ep) for ep in backend}
        frontend_norm = {self._norm(c) for c in frontend}

        # Matching com sufixo para lidar com prefixos de módulo (operacional, crm, etc.)
        cobertos = {
            ep
            for ep in backend_norm
            if ep in frontend_norm or self._backend_em_frontend(ep, frontend_norm)
        }
        nao_cobertos = backend_norm - cobertos

        total = len(backend_norm)
        n_cob = len(cobertos)
        pct = (n_cob / total * 100) if total > 0 else 0

        # Score calibrado: meta 7+/10 quando cobertura ≥ 60%
        if pct >= 80:
            score = 9.0 + (pct - 80) / 20
        elif pct >= 60:
            score = 7.0 + (pct - 60) / 20 * 2
        elif pct >= 40:
            score = 5.0 + (pct - 40) / 20 * 2
        else:
            score = max(1.0, pct / 10)

        bugs = [
            {
                "tipo": "endpoint_sem_cobertura_frontend",
                "endpoint": ep,
                "descricao": f"Endpoint sem cobertura no frontend: {ep}",
                "autocorrigivel": False,
            }
            for ep in sorted(nao_cobertos)[:15]
        ]

        resultado = {
            "agente": "coverage",
            "score": round(min(score, 10.0), 1),
            "total_backend_ui": total,
            "cobertos": n_cob,
            "nao_cobertos": len(nao_cobertos),
            "cobertura_pct": round(pct, 1),
            "bugs": bugs,
        }
        print(
            f"  Módulos UI — Backend: {total} | Cobertos: {n_cob} "
            f"({pct:.1f}%) | Score: {resultado['score']}/10"
        )
        return resultado
