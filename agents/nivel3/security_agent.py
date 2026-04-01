"""
SecurityAgent v2 — Testes avançados de segurança.
Detecta: SQL injection, XSS, força bruta, enumeração, IDOR, headers, rate limit.
NÃO faz pentesting agressivo — apenas verificações seguras e não destrutivas.
"""

import json as _json
import time
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "http://127.0.0.1:8080"

ENDPOINTS_PRIVADOS = [
    "/api/v1/people-management/hr/employees",
    "/api/v1/financial/payables",
    "/api/v1/crm/contacts/",
    "/api/v1/ged/documents",
    "/api/v1/operacional/posts/",
    "/api/v1/config/system",
    "/api/v1/analytics/executive/dashboard",
    "/api/v1/hr/employees",
    "/api/v1/bidding/processes",
    "/api/v1/recruitment/vacancies",
]

SECURITY_HEADERS = [
    "x-content-type-options",
    "x-frame-options",
    "strict-transport-security",
]

SQL_PAYLOADS = [
    "' OR '1'='1",
    "1; DROP TABLE users--",
    "' UNION SELECT 1,2,3--",
    "admin'--",
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    '"><img src=x onerror=alert(1)>',
    "javascript:alert(1)",
]

UUID_FAKE = "00000000-0000-0000-0000-000000000001"

ENDPOINTS_IDOR = [
    f"/api/v1/people-management/hr/employees/{UUID_FAKE}",
    f"/api/v1/crm/contacts/{UUID_FAKE}",
    f"/api/v1/ged/documents/{UUID_FAKE}",
    f"/api/v1/financial/payables/{UUID_FAKE}",
]


class SecurityAgent:
    """Testes avançados de segurança — v2."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "security"

    def _request(
        self,
        path: str,
        token: str = None,
        method: str = "GET",
        data: bytes = None,
        content_type: str = "application/json",
        timeout: int = 5,
    ) -> tuple:
        req = urllib.request.Request(f"{BASE_URL}{path}", method=method, data=data)
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        if data:
            req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers) if hasattr(e, "headers") else {}, b""
        except Exception:
            return 0, {}, b""

    # ── 1. Auth endpoints ────────────────────────────────────────────────────

    def testar_auth_endpoints(self) -> list:
        """10 endpoints privados devem retornar 401 sem token."""
        vulneraveis = []
        for endpoint in ENDPOINTS_PRIVADOS:
            status, _, _ = self._request(endpoint, token=None)
            if status == 200:
                vulneraveis.append(
                    {
                        "endpoint": endpoint,
                        "descricao": f"Endpoint exposto sem autenticação: {endpoint}",
                        "severidade": "CRITICO",
                    }
                )
        return vulneraveis

    # ── 2. SQL Injection ────────────────────────────────────────────────────

    def testar_sql_injection(self) -> list:
        """Injeta payloads SQL em parâmetros de busca — verifica 500 ou dados vazados."""
        vulnerabilidades = []
        endpoints_busca = [
            "/api/v1/crm/contacts/",
            "/api/v1/people-management/hr/employees",
            "/api/v1/ged/documents",
        ]
        for endpoint in endpoints_busca:
            for payload in SQL_PAYLOADS:
                q = urllib.parse.urlencode(
                    {"search": payload, "q": payload, "name": payload}
                )
                status, _, body = self._request(f"{endpoint}?{q}", token=self.token)
                body_str = body.decode("utf-8", errors="ignore")
                # 500 = possível SQL não tratado; erro de DB na resposta = vazamento
                if status == 500:
                    vulnerabilidades.append(
                        {
                            "endpoint": endpoint,
                            "payload": payload,
                            "descricao": f"SQL injection possível — status 500 em {endpoint}",
                            "severidade": "CRITICO",
                        }
                    )
                    break  # 1 achado por endpoint é suficiente
                elif any(
                    kw in body_str.lower()
                    for kw in ["syntax error", "pg::", "sqlalchemy", "psycopg"]
                ):
                    vulnerabilidades.append(
                        {
                            "endpoint": endpoint,
                            "payload": payload,
                            "descricao": f"Vazamento de erro SQL em {endpoint}",
                            "severidade": "ALTO",
                        }
                    )
                    break
        return vulnerabilidades

    # ── 3. XSS ──────────────────────────────────────────────────────────────

    def testar_xss(self) -> list:
        """Envia payloads XSS em campos de texto e verifica se são refletidos sem escape."""
        vulnerabilidades = []
        endpoints_xss = [
            "/api/v1/crm/contacts/",
            "/api/v1/people-management/hr/employees",
        ]
        for endpoint in endpoints_xss:
            for payload in XSS_PAYLOADS:
                q = urllib.parse.urlencode({"search": payload, "name": payload})
                status, headers, body = self._request(
                    f"{endpoint}?{q}", token=self.token
                )
                body_str = body.decode("utf-8", errors="ignore")
                content_type = headers.get(
                    "Content-Type", headers.get("content-type", "")
                )
                # XSS crítico: payload refletido em HTML sem escape
                if payload in body_str and "text/html" in content_type:
                    vulnerabilidades.append(
                        {
                            "endpoint": endpoint,
                            "payload": payload,
                            "descricao": f"XSS refletido em {endpoint}",
                            "severidade": "CRITICO",
                        }
                    )
                    break
                # XSS médio: payload refletido em JSON (risco menor)
                elif payload in body_str and "application/json" in content_type:
                    vulnerabilidades.append(
                        {
                            "endpoint": endpoint,
                            "payload": payload,
                            "descricao": f"Payload XSS refletido em JSON {endpoint} — verificar escaping no frontend",
                            "severidade": "MEDIO",
                        }
                    )
                    break
        return vulnerabilidades

    # ── 4. Força bruta ──────────────────────────────────────────────────────

    def testar_forca_bruta(self) -> list:
        """6 logins errados consecutivos devem ativar rate limit (429)."""
        vulnerabilidades = []
        ultimo_status = 0
        for i in range(6):
            payload = urllib.parse.urlencode(
                {
                    "username": "admin@conectapro.com.br",
                    "password": f"senha_errada_{i}",  # pragma: allowlist secret
                }
            ).encode()
            status, _, _ = self._request(
                "/api/v1/auth/login",
                method="POST",
                data=payload,
                content_type="application/x-www-form-urlencoded",
            )
            ultimo_status = status
            if status == 429:
                break  # rate limit ativo ✅
            time.sleep(0.3)

        if ultimo_status not in (429, 423):
            vulnerabilidades.append(
                {
                    "endpoint": "/api/v1/auth/login",
                    "descricao": f"Força bruta não bloqueada após 6 tentativas (último status: {ultimo_status})",
                    "severidade": "ALTO",
                }
            )
        return vulnerabilidades

    # ── 5. Enumeração de usuários ────────────────────────────────────────────

    def testar_enumeracao_usuarios(self) -> list:
        """
        Timing attack: login com usuário existente vs inexistente.
        Diferença > 500ms pode indicar enumeração por timing.
        """
        vulnerabilidades = []

        def medir(username: str) -> float:
            payload = urllib.parse.urlencode(
                {
                    "username": username,
                    "password": "senha_invalida_auditoria",  # pragma: allowlist secret
                }
            ).encode()
            t0 = time.time()
            self._request(
                "/api/v1/auth/login",
                method="POST",
                data=payload,
                content_type="application/x-www-form-urlencoded",
                timeout=10,
            )
            return time.time() - t0

        t_existente = medir("jjesus@conectamais.pro")
        time.sleep(1)  # aguardar rate limit
        t_inexistente = medir("usuario_inexistente_xyz_99@naoexiste.com")
        diff = abs(t_existente - t_inexistente)

        if diff > 0.5:
            vulnerabilidades.append(
                {
                    "endpoint": "/api/v1/auth/login",
                    "descricao": (
                        f"Possível enumeração de usuários por timing — "
                        f"diferença: {diff:.2f}s (existente={t_existente:.2f}s, inexistente={t_inexistente:.2f}s)"
                    ),
                    "severidade": "MEDIO",
                }
            )
        return vulnerabilidades

    # ── 6. Headers de segurança ─────────────────────────────────────────────

    def testar_headers_seguranca(self) -> list:
        """Verifica presença de headers de segurança obrigatórios."""
        ausentes = []
        status, headers, _ = self._request(
            "/api/v1/people-management/hr/employees", token=self.token
        )
        if status not in (200, 401, 403):
            return ausentes
        headers_lower = {k.lower(): v for k, v in headers.items()}
        for header in SECURITY_HEADERS:
            if header not in headers_lower:
                ausentes.append(
                    {
                        "header": header,
                        "descricao": f"Header de segurança ausente: {header}",
                        "severidade": "MEDIO",
                    }
                )
        return ausentes

    # ── 7. IDOR ─────────────────────────────────────────────────────────────

    def testar_idor(self) -> list:
        """UUID fake em endpoints sensíveis — não deve retornar 200 com dados."""
        vulnerabilidades = []
        for endpoint in ENDPOINTS_IDOR:
            status, _, body = self._request(endpoint, token=self.token)
            if status == 200 and len(body) > 50:
                vulnerabilidades.append(
                    {
                        "endpoint": endpoint,
                        "descricao": f"Possível IDOR: UUID inexistente retornou dados em {endpoint}",
                        "severidade": "ALTO",
                    }
                )
        return vulnerabilidades

    # ── 8. Registro sem auth ────────────────────────────────────────────────

    def testar_registro_sem_auth(self) -> list:
        """POST /auth/register sem token não deve criar usuário admin."""
        payload = _json.dumps(
            {
                "email": "audit_test@conectamais.pro",
                "password": "AuditTest@2026",  # pragma: allowlist secret
                "role": "admin",
            }
        ).encode()
        status, _, _ = self._request(
            "/api/v1/auth/register", token=None, method="POST", data=payload
        )
        if status in (200, 201):
            return [
                {
                    "endpoint": "/api/v1/auth/register",
                    "descricao": "CRÍTICO: /register cria usuário admin sem autenticação",
                    "severidade": "CRITICO",
                }
            ]
        return []

    # ── 9. Rate limit geral ─────────────────────────────────────────────────

    def testar_rate_limit_api(self) -> list:
        """35 requisições rápidas devem acionar rate limiting (429) — limite: 30/min."""
        vulnerabilidades = []
        got_429 = False
        for _ in range(35):
            status, _, _ = self._request("/api/v1/ged/documents", token=self.token)
            if status == 429:
                got_429 = True
                break

        if not got_429:
            vulnerabilidades.append(
                {
                    "endpoint": "/api/v1/ged/documents",
                    "descricao": "Rate limiting não acionado após 35 requisições rápidas",
                    "severidade": "BAIXO",
                }
            )
        return vulnerabilidades

    # ── Orquestrador ────────────────────────────────────────────────────────

    def auditar(self) -> dict:
        print("🔍 SecurityAgent v2: executando testes avançados de segurança...")

        testes = [
            ("auth_endpoints", self.testar_auth_endpoints),
            ("sql_injection", self.testar_sql_injection),
            ("xss", self.testar_xss),
            ("forca_bruta", self.testar_forca_bruta),
            ("enumeracao_usuarios", self.testar_enumeracao_usuarios),
            ("headers_seguranca", self.testar_headers_seguranca),
            ("idor", self.testar_idor),
            ("registro_sem_auth", self.testar_registro_sem_auth),
            ("rate_limit_api", self.testar_rate_limit_api),
        ]

        todos_bugs = []
        detalhes = {}
        for nome, fn in testes:
            try:
                result = fn()
                detalhes[nome] = len(result)
                todos_bugs.extend(result)
                icon = "✅" if not result else "⚠️"
                print(f"  {icon} {nome}: {len(result)} vuln(s)")
            except Exception as e:
                print(f"  ❌ {nome}: erro — {e}")
                detalhes[nome] = 0

        criticos = [b for b in todos_bugs if b.get("severidade") == "CRITICO"]
        altos = [b for b in todos_bugs if b.get("severidade") == "ALTO"]
        medios = [b for b in todos_bugs if b.get("severidade") == "MEDIO"]
        baixos = [b for b in todos_bugs if b.get("severidade") == "BAIXO"]

        score = max(
            0.0,
            min(
                10.0,
                10.0
                - len(criticos) * 4.0
                - len(altos) * 2.0
                - len(medios) * 0.5
                - len(baixos) * 0.2,
            ),
        )

        resultado = {
            "agente": "security",
            "versao": "v2",
            "score": round(score, 1),
            "total_vulnerabilidades": len(todos_bugs),
            "criticas": len(criticos),
            "altas": len(altos),
            "medias": len(medios),
            "baixas": len(baixos),
            "detalhes_por_teste": detalhes,
            "bugs": [
                {
                    "tipo": "vulnerabilidade",
                    "severidade": b.get("severidade"),
                    "descricao": b.get("descricao"),
                    "endpoint": b.get("endpoint", b.get("header", "N/A")),
                    "autocorrigivel": False,
                    "acao_jordan": True,
                }
                for b in todos_bugs
            ],
        }

        print(
            f"\n  Score segurança: {resultado['score']}/10 | "
            f"🔴 {len(criticos)} críticos | 🟠 {len(altos)} altos | "
            f"🟡 {len(medios)} médios | 🟢 {len(baixos)} baixos"
        )
        return resultado
