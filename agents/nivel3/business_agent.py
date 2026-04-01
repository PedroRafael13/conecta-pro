"""
BusinessAgent — Valida regras de negócio específicas do Conecta PRO.
Verifica: CCT aplicado corretamente, cálculos de folha,
alocações válidas, escalas completas.
"""
import json
import urllib.request


BASE_URL = "http://127.0.0.1:8080"

# Pisos salariais CCT 2026 SINDECOMPRESTS
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
        """Normaliza resposta paginada ou lista direta."""
        if isinstance(data, dict):
            return data.get("items", data.get("data", []))
        return data if isinstance(data, list) else []

    def verificar_cct_conformidade(self) -> list:
        """Verifica se todos os funcionários atendem ao piso CCT."""
        problemas = []
        data = self._get(
            "/api/v1/people-management/hr/employees?page_size=100"
        )
        for f in self._items(data):
            cargo = (
                f.get("cargo")
                or f.get("position")
                or f.get("job_title", "")
            )
            salario = float(
                f.get("salario") or f.get("salary") or f.get("wage", 0) or 0
            )
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
                        f"{f.get('nome', '?')} "
                        f"(R${salario:.2f} < R${piso:.2f})"
                    ),
                    "acao_jordan": True,
                })
        return problemas

    def verificar_contagem_funcionarios(self) -> list:
        """Verifica se há exatamente 52 funcionários ativos."""
        problemas = []
        data = self._get(
            "/api/v1/people-management/hr/employees?page_size=200"
        )
        funcionarios = self._items(data)
        ativos = [
            f for f in funcionarios
            if f.get("status") in ["ativo", "active"]
            or f.get("is_active") is True
        ]
        if len(ativos) != FUNCIONARIOS_ATIVOS_ESPERADO:
            problemas.append({
                "tipo": "contagem_funcionarios",
                "esperado": FUNCIONARIOS_ATIVOS_ESPERADO,
                "encontrado": len(ativos),
                "descricao": (
                    f"Funcionários ativos: {len(ativos)} "
                    f"(esperado: {FUNCIONARIOS_ATIVOS_ESPERADO})"
                ),
                "acao_jordan": len(ativos) < 40,
            })
        return problemas

    def verificar_alocacoes_ativas(self) -> list:
        """Verifica se postos críticos estão cobertos."""
        problemas = []

        postos = self._items(
            self._get("/api/v1/operacional/posts/?page_size=50")
        )
        alocacoes = self._items(
            self._get("/api/v1/operacional/allocations/?page_size=100")
        )

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
                    "descricao": (
                        f"Posto sem alocação ativa: "
                        f"{posto.get('nome', '?')}"
                    ),
                    "acao_jordan": True,
                })

        return problemas

    def verificar_clientes_ativos(self) -> list:
        """Verifica se os 13 clientes ativos estão no sistema."""
        problemas = []
        data = self._get("/api/v1/crm/clients?page_size=50")
        clientes = self._items(data)
        ativos = [
            c for c in clientes
            if c.get("status") in ["ativo", "active"]
            or c.get("is_active") is True
            or c.get("status") is None
        ]
        if len(ativos) < CLIENTES_ESPERADOS:
            problemas.append({
                "tipo": "clientes_insuficientes",
                "esperado": CLIENTES_ESPERADOS,
                "encontrado": len(ativos),
                "descricao": (
                    f"Clientes ativos: {len(ativos)} "
                    f"(esperado: ≥{CLIENTES_ESPERADOS})"
                ),
                "acao_jordan": True,
            })
        return problemas

    def auditar(self) -> dict:
        """Executa todas as verificações de negócio."""
        print("🔍 BusinessAgent: validando regras de negócio...")

        todos_problemas = []
        todos_problemas.extend(self.verificar_cct_conformidade())
        todos_problemas.extend(self.verificar_contagem_funcionarios())
        todos_problemas.extend(self.verificar_alocacoes_ativas())
        todos_problemas.extend(self.verificar_clientes_ativos())

        jordan_action = [p for p in todos_problemas if p.get("acao_jordan")]
        score = max(0, 10.0 - len(todos_problemas) * 1.0)

        resultado = {
            "agente": "business",
            "score": round(min(score, 10.0), 1),
            "total_problemas": len(todos_problemas),
            "acao_jordan": len(jordan_action),
            "problemas": todos_problemas,
            "bugs": [
                {
                    "tipo": p.get("tipo"),
                    "descricao": p.get("descricao"),
                    "acao_jordan": p.get("acao_jordan", False),
                    "autocorrigivel": False,
                }
                for p in todos_problemas
            ],
        }

        print(
            f"  Problemas: {len(todos_problemas)} "
            f"({len(jordan_action)} precisam de Jordan)"
        )
        print(f"  Score: {resultado['score']}/10")
        return resultado
