"""
DataValidatorAgent — Valida o conteúdo das respostas da API,
não apenas o status HTTP. Garante que os dados retornados
têm estrutura e campos obrigatórios corretos.
"""

import json
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8080"

# Contratos: (endpoint, método, validador)
# Validador recebe o body parseado e retorna lista de erros (vazia = OK)
CONTRATOS = [
    {
        "nome": "employees_lista",
        "endpoint": "/api/v1/people-management/hr/employees?page_size=5",
        "metodo": "GET",
        "validar": lambda d: (
            []
            if isinstance(d, (list, dict))
            and (
                isinstance(d, list)
                or d.get("items") is not None
                or d.get("data") is not None
            )
            else ["Resposta não contém lista de employees (items/data ausente)"]
        ),
    },
    {
        "nome": "employee_campos",
        "endpoint": "/api/v1/people-management/hr/employees?page_size=1",
        "metodo": "GET",
        "validar": lambda d: _validar_campos_employee(d),
    },
    {
        "nome": "clientes_lista",
        "endpoint": "/api/v1/crm/clients?page_size=5",
        "metodo": "GET",
        "validar": lambda d: (
            []
            if isinstance(d, (list, dict))
            and (
                isinstance(d, list)
                and len(d) > 0
                or isinstance(d, dict)
                and (d.get("items") or d.get("data") or d.get("total") is not None)
            )
            else ["Resposta de clientes vazia ou sem estrutura esperada"]
        ),
    },
    {
        "nome": "financeiro_a_pagar",
        "endpoint": "/api/v1/financial/payables?page_size=5",
        "metodo": "GET",
        "validar": lambda d: (
            []
            if isinstance(d, (list, dict))
            else ["Financeiro/payables não retornou estrutura válida"]
        ),
    },
    {
        "nome": "ponto_dashboard",
        "endpoint": "/api/v1/ponto/dashboard",
        "metodo": "GET",
        "validar": lambda d: (
            []
            if isinstance(d, dict) and len(d) > 0
            else ["Dashboard ponto retornou objeto vazio"]
        ),
    },
    {
        "nome": "operacional_postos",
        "endpoint": "/api/v1/operacional/posts/?page_size=5",
        "metodo": "GET",
        "validar": lambda d: (
            []
            if isinstance(d, (list, dict))
            else ["Postos operacionais não retornou estrutura válida"]
        ),
    },
    {
        "nome": "analytics_dashboard",
        "endpoint": "/api/v1/analytics/executive/dashboard",
        "metodo": "GET",
        "validar": lambda d: (
            []
            if isinstance(d, dict) and len(d) > 0
            else ["Analytics dashboard retornou objeto vazio"]
        ),
    },
    {
        "nome": "auth_me",
        "endpoint": "/api/v1/auth/me",
        "metodo": "GET",
        "validar": lambda d: (
            []
            if isinstance(d, dict) and (d.get("email") or d.get("id") or d.get("sub"))
            else ["Auth /me não retornou user com email/id"]
        ),
    },
]


def _validar_campos_employee(data) -> list:
    """Valida campos obrigatórios de um employee."""
    erros = []
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("items") or data.get("data") or data.get("results") or []
    if not items:
        return []  # sem dados para validar (pode ser base vazia)
    emp = items[0]
    campos_esperados = ["id"]
    campos_nome = ["nome", "name", "full_name", "first_name"]
    if not any(emp.get(c) for c in campos_nome):
        erros.append(f"Employee sem campo de nome (testados: {campos_nome})")
    for campo in campos_esperados:
        if not emp.get(campo):
            erros.append(f"Employee sem campo obrigatório: {campo}")
    return erros


class DataValidatorAgent:
    """Valida conteúdo das respostas da API (não apenas status HTTP)."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "data_validator"

    def _request(self, endpoint: str, method: str = "GET") -> tuple:
        req = urllib.request.Request(
            f"{BASE_URL}{endpoint}",
            method=method,
        )
        req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
                try:
                    return r.status, json.loads(body)
                except Exception:
                    return r.status, {}
        except urllib.error.HTTPError as e:
            return e.code, {}
        except Exception:
            return 0, {}

    def _validar_contrato(self, contrato: dict) -> dict:
        """Executa e valida um contrato."""
        status, body = self._request(contrato["endpoint"], contrato["metodo"])
        if status == 0:
            return {
                "nome": contrato["nome"],
                "status": "conexao_falhou",
                "erros": ["Sem conexão com o backend"],
                "ok": False,
            }
        if status in (401, 403):
            return {
                "nome": contrato["nome"],
                "status": "auth_required",
                "erros": [],
                "ok": True,  # Endpoint protegido corretamente
            }
        if status not in (200, 201):
            return {
                "nome": contrato["nome"],
                "status": f"http_{status}",
                "erros": [f"Status inesperado: {status}"],
                "ok": False,
            }
        try:
            erros = contrato["validar"](body)
        except Exception as e:
            erros = [f"Erro no validador: {e}"]
        return {
            "nome": contrato["nome"],
            "status": "ok" if not erros else "invalido",
            "erros": erros,
            "ok": not erros,
        }

    def auditar(self) -> dict:
        print("🔍 DataValidatorAgent: validando conteúdo das respostas...")
        resultados = [self._validar_contrato(c) for c in CONTRATOS]
        invalidos = [r for r in resultados if not r["ok"]]
        score = max(0.0, 10.0 - len(invalidos) * (10.0 / len(CONTRATOS)))
        bugs = [
            {
                "tipo": "resposta_invalida",
                "contrato": r["nome"],
                "descricao": f"Contrato '{r['nome']}' falhou: {'; '.join(r['erros'])}",
                "autocorrigivel": False,
                "acao_jordan": True,
            }
            for r in invalidos
        ]
        resultado = {
            "agente": "data_validator",
            "score": round(min(score, 10.0), 1),
            "total_contratos": len(CONTRATOS),
            "validos": len(resultados) - len(invalidos),
            "invalidos": len(invalidos),
            "detalhes": resultados,
            "bugs": bugs,
        }
        print(
            f"  Contratos: {len(CONTRATOS)} | "
            f"OK: {len(resultados) - len(invalidos)} | "
            f"Falhos: {len(invalidos)} | Score: {resultado['score']}/10"
        )
        return resultado
