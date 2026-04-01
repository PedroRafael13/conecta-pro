"""
ContractAgent — Valida se os payloads que o frontend envia
batem com os schemas que o backend espera.
Detecta mismatch de campos, campos faltando, tipos errados.
"""
import json
import re
import urllib.request
from pathlib import Path
from typing import Optional


FRONTEND_DIR = Path("/opt/conecta-pro/frontend/src")
BASE_URL = "http://127.0.0.1:8080"

ENDPOINTS_CRITICOS = [
    ("POST", "/api/v1/people-management/hr/admissions"),
    ("POST", "/api/v1/crm/leads"),
    ("POST", "/api/v1/crm/clients"),
    ("POST", "/api/v1/operacional/posts/"),
    ("POST", "/api/v1/operacional/scales/"),
    ("POST", "/api/v1/financial/payables"),
    ("POST", "/api/v1/financial/receivables"),
    ("PUT", "/api/v1/people-management/hr/employees/{id}"),
    ("POST", "/api/v1/ged/kits"),
    ("POST", "/api/v1/ged/documents"),
]


class ContractAgent:
    """Valida contratos de API frontend ↔ backend."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "contract"

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

    def ler_schema_backend(self, method: str, path: str) -> dict:
        """Extrai schema esperado do OpenAPI para um endpoint."""
        spec = self._get("/openapi.json")
        path_spec = spec.get("paths", {}).get(path, {})
        method_spec = path_spec.get(method.lower(), {})
        body = method_spec.get("requestBody", {})
        schema = (
            body.get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        if "$ref" in schema:
            ref = schema["$ref"].split("/")[-1]
            schema = (
                spec.get("components", {})
                .get("schemas", {})
                .get(ref, {})
            )
        return schema

    def extrair_campos_frontend(self, endpoint_path: str) -> list:
        """Encontra campos enviados no frontend para um endpoint."""
        campos = []
        endpoint_slug = endpoint_path.split("/")[-1].replace("-", "_")

        patterns = [
            re.compile(r'body:\s*JSON\.stringify\(\s*\{([^}]+)\}', re.DOTALL),
            re.compile(r'(?:data|body|payload):\s*\{([^}]+)\}', re.DOTALL),
            re.compile(r'JSON\.stringify\(\s*\{([^}]+)\}', re.DOTALL),
        ]

        for fpath in FRONTEND_DIR.rglob("*.tsx"):
            if "node_modules" in str(fpath):
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if endpoint_slug not in content and endpoint_path not in content:
                continue

            for pattern in patterns:
                for match in pattern.finditer(content):
                    obj_content = match.group(1)
                    field_pattern = re.compile(r"(\w+)\s*:")
                    for fm in field_pattern.finditer(obj_content):
                        campo = fm.group(1)
                        if campo not in [
                            "headers", "method", "body",
                            "cache", "mode", "credentials",
                        ]:
                            campos.append(campo)

        return list(set(campos))

    def auditar(self) -> dict:
        """Valida contratos dos endpoints críticos."""
        print("🔍 ContractAgent: validando contratos API...")

        mismatches = []
        ok = 0

        for method, path in ENDPOINTS_CRITICOS:
            schema_backend = self.ler_schema_backend(method, path)
            if not schema_backend:
                continue

            campos_esperados = set(schema_backend.get("properties", {}).keys())
            obrigatorios = set(schema_backend.get("required", []))
            campos_frontend = set(self.extrair_campos_frontend(path))

            if not campos_frontend:
                continue

            faltando = obrigatorios - campos_frontend
            sobrando = campos_frontend - campos_esperados

            if faltando or sobrando:
                mismatches.append({
                    "endpoint": f"{method} {path}",
                    "campos_faltando": list(faltando),
                    "campos_sobrando": list(sobrando),
                    "esperados": list(campos_esperados),
                    "enviados": list(campos_frontend),
                })
            else:
                ok += 1

        total = ok + len(mismatches)
        score = (ok / total * 10) if total else 10.0

        resultado = {
            "agente": "contract",
            "score": round(score, 1),
            "endpoints_validados": total,
            "contratos_ok": ok,
            "mismatches": mismatches,
            "bugs": [
                {
                    "tipo": "contract_mismatch",
                    "endpoint": m["endpoint"],
                    "descricao": (
                        f"Mismatch: faltando={m['campos_faltando']}, "
                        f"sobrando={m['campos_sobrando']}"
                    ),
                    "autocorrigivel": False,
                }
                for m in mismatches
            ],
        }

        print(f"  Contratos OK: {ok}/{total}")
        print(f"  Mismatches: {len(mismatches)}")
        print(f"  Score: {resultado['score']}/10")
        return resultado
