"""
SecurityAgent — Testes básicos de segurança.
Detecta: endpoints expostos sem auth, headers de segurança
ausentes, IDOR básico, /register sem auth.
NÃO faz pentesting agressivo — apenas verificações seguras.
"""
import json as _json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8080"

ENDPOINTS_PRIVADOS = [
    "/api/v1/people-management/hr/employees",
    "/api/v1/financial/payables",
    "/api/v1/crm/clients",
    "/api/v1/ged/documents",
    "/api/v1/operacional/posts/",
    "/api/v1/config/tenants",
    "/api/v1/analytics/executive/dashboard",
]

SECURITY_HEADERS = [
    "x-content-type-options",
    "x-frame-options",
    "strict-transport-security",
]


class SecurityAgent:
    """Testes básicos de segurança."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "security"

    def _request(
        self,
        path: str,
        token: str = None,
        method: str = "GET",
        data: bytes = None,
    ) -> tuple:
        """Faz request e retorna (status, headers, body)."""
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            method=method,
            data=data,
        )
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        if data:
            req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, {}, b""
        except Exception:
            return 0, {}, b""

    def testar_endpoints_sem_auth(self) -> list:
        """Verifica se endpoints privados retornam 401 sem token."""
        vulneraveis = []
        for endpoint in ENDPOINTS_PRIVADOS:
            status, _, _ = self._request(endpoint, token=None)
            if status == 200:
                vulneraveis.append({
                    "endpoint": endpoint,
                    "status_sem_token": status,
                    "descricao": f"Endpoint exposto sem auth: {endpoint}",
                    "severidade": "CRITICO",
                })
        return vulneraveis

    def testar_headers_seguranca(self) -> list:
        """Verifica headers de segurança HTTP."""
        ausentes = []
        status, headers, _ = self._request(
            "/api/v1/people-management/hr/employees",
            token=self.token,
        )
        if status not in (200, 401, 403):
            return ausentes
        headers_lower = {k.lower(): v for k, v in headers.items()}
        for header in SECURITY_HEADERS:
            if header not in headers_lower:
                ausentes.append({
                    "header": header,
                    "descricao": f"Header de segurança ausente: {header}",
                    "severidade": "MEDIO",
                })
        return ausentes

    def testar_idor_basico(self) -> list:
        """Testa IDOR básico com UUID inexistente."""
        vulnerabilidades = []
        uuid_fake = "00000000-0000-0000-0000-000000000001"

        endpoints_id = [
            f"/api/v1/people-management/hr/employees/{uuid_fake}",
            f"/api/v1/crm/clients/{uuid_fake}",
            f"/api/v1/ged/documents/{uuid_fake}",
        ]

        for endpoint in endpoints_id:
            status, _, body = self._request(endpoint, token=self.token)
            if status == 200 and len(body) > 50:
                vulnerabilidades.append({
                    "endpoint": endpoint,
                    "descricao": "Possível IDOR: UUID fake retornou dados",
                    "severidade": "ALTO",
                })

        return vulnerabilidades

    def testar_registro_sem_auth(self) -> list:
        """Verifica se /register cria usuário admin sem auth."""
        vulnerabilidades = []

        payload = _json.dumps({
            "email": "audit_test@conectamais.pro",
            "password": "AuditTest@2026",  # pragma: allowlist secret
            "role": "admin",
        }).encode()

        status, _, _ = self._request(
            "/api/v1/auth/register",
            token=None,
            method="POST",
            data=payload,
        )

        if status in [200, 201]:
            vulnerabilidades.append({
                "endpoint": "/api/v1/auth/register",
                "descricao": "CRÍTICO: /register cria usuário sem auth",
                "severidade": "CRITICO",
            })

        return vulnerabilidades

    def auditar(self) -> dict:
        """Executa todos os testes de segurança."""
        print("🔍 SecurityAgent: testando segurança...")

        todos_bugs = []
        todos_bugs.extend(self.testar_endpoints_sem_auth())
        todos_bugs.extend(self.testar_headers_seguranca())
        todos_bugs.extend(self.testar_idor_basico())
        todos_bugs.extend(self.testar_registro_sem_auth())

        criticos = [b for b in todos_bugs if b.get("severidade") == "CRITICO"]
        altos = [b for b in todos_bugs if b.get("severidade") == "ALTO"]

        score = 10.0 - len(criticos) * 3.0 - len(altos) * 1.5 - len(todos_bugs) * 0.3
        score = max(0, min(10.0, score))

        resultado = {
            "agente": "security",
            "score": round(score, 1),
            "total_vulnerabilidades": len(todos_bugs),
            "criticas": len(criticos),
            "altas": len(altos),
            "bugs": [
                {
                    "tipo": "vulnerabilidade",
                    "severidade": b.get("severidade"),
                    "descricao": b.get("descricao"),
                    "autocorrigivel": False,
                    "acao_jordan": True,
                }
                for b in todos_bugs
            ],
        }

        print(
            f"  Vulnerabilidades: {len(todos_bugs)} "
            f"({len(criticos)} críticas)"
        )
        print(f"  Score: {resultado['score']}/10")
        return resultado
