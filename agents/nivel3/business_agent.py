"""
BusinessAgent — Valida regras de negócio específicas do Conecta PRO.
Verifica: CCT, contagem de funcionários, alocações, clientes.
"""
import json
import urllib.request


BASE_URL = "http://127.0.0.1:8080"

PISOS_CCT_2026 = {
    "Agente de Portaria": 1670.00,
    "Agente de Serviços Gerais": 1670.00,
    "Artífice": 1742.52,
    "Líder de Portaria": 1787.53,
}
FUNCIONARIOS_ATIVOS_ESPERADO = 52
CLIENTES_ESPERADOS = 13


class BusinessAgent:
    """Valida regras de negócio do Conecta PRO."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "business"

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except Exception:
            return {}

    def _items(self, data) -> list:
        if isinstance(data, dict):
            return data.get("items", data.get("data", []))
        return data if isinstance(data, list) else []

    def verificar_cct_conformidade(self) -> list:
        problemas = []
        for f in self._items(self._get("/api/v1/people-management/hr/employees?page_size=100")):
            cargo = f.get("cargo") or f.get("position") or f.get("job_title", "")
            salario = float(f.get("salario") or f.get("salary") or f.get("wage", 0) or 0)
            piso = PISOS_CCT_2026.get(cargo)
            if piso and salario > 0 and salario < piso:
                problemas.append({
                    "tipo": "cct_abaixo_piso",
                    "funcionario": f.get("nome") or f.get("name", "?"),
                    "cargo": cargo,
                    "salario_atual": salario,
                    "piso_cct": piso,
                    "diferenca": round(piso - salario, 2),
                    "descricao": (
                        f"Salário abaixo do piso CCT: "
                        f"{f.get('nome', '?')} (R${salario:.2f} < R${piso:.2f})"
                    ),
                    "acao_jordan": True,
                })
        return problemas

    def verificar_contagem_funcionarios(self) -> list:
        data = self._get("/api/v1/people-management/hr/employees?page_size=200")
        ativos = [
            f for f in self._items(data)
            if f.get("status") in ["ativo", "active"] or f.get("is_active") is True
        ]
        if len(ativos) != FUNCIONARIOS_ATIVOS_ESPERADO:
            return [{
                "tipo": "contagem_funcionarios",
                "esperado": FUNCIONARIOS_ATIVOS_ESPERADO,
                "encontrado": len(ativos),
                "descricao": f"Funcionários ativos: {len(ativos)} (esperado: {FUNCIONARIOS_ATIVOS_ESPERADO})",
                "acao_jordan": len(ativos) < 40,
            }]
        return []

    def verificar_alocacoes_ativas(self) -> list:
        problemas = []
        postos = self._items(self._get("/api/v1/operacional/posts/?page_size=50"))
        alocacoes = self._items(self._get("/api/v1/operacional/allocations/?page_size=100"))
        postos_com_aloc = {
            a.get("post_id") or a.get("posto_id")
            for a in alocacoes
            if a.get("status") in ["ativo", "active", None]
        }
        for posto in postos:
            pid = posto.get("id")
            if pid and pid not in postos_com_aloc:
                problemas.append({
                    "tipo": "posto_sem_alocacao",
                    "posto": posto.get("nome") or posto.get("name", "?"),
                    "descricao": f"Posto sem alocação ativa: {posto.get('nome', '?')}",
                    "acao_jordan": True,
                })
        return problemas

    def verificar_clientes_ativos(self) -> list:
        data = self._get("/api/v1/crm/clients?page_size=50")
        ativos = [
            c for c in self._items(data)
            if c.get("status") in ["ativo", "active"] or c.get("is_active") is True
            or c.get("status") is None
        ]
        if len(ativos) < CLIENTES_ESPERADOS:
            return [{
                "tipo": "clientes_insuficientes",
                "esperado": CLIENTES_ESPERADOS,
                "encontrado": len(ativos),
                "descricao": f"Clientes ativos: {len(ativos)} (esperado: ≥{CLIENTES_ESPERADOS})",
                "acao_jordan": True,
            }]
        return []

    def auditar(self) -> dict:
        print("🔍 BusinessAgent: validando regras de negócio...")
        todos = []
        todos.extend(self.verificar_cct_conformidade())
        todos.extend(self.verificar_contagem_funcionarios())
        todos.extend(self.verificar_alocacoes_ativas())
        todos.extend(self.verificar_clientes_ativos())
        jordan = sum(1 for p in todos if p.get("acao_jordan"))
        score = max(0, 10.0 - len(todos) * 1.0)
        resultado = {
            "agente": "business",
            "score": round(min(score, 10.0), 1),
            "total_problemas": len(todos),
            "acao_jordan": jordan,
            "problemas": todos,
            "bugs": [{"tipo": p.get("tipo"), "descricao": p.get("descricao"),
                      "acao_jordan": p.get("acao_jordan", False), "autocorrigivel": False}
                     for p in todos],
        }
        print(f"  Problemas: {len(todos)} ({jordan} precisam de Jordan), Score: {resultado['score']}/10")
        return resultado
