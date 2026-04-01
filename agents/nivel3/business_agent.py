"""
BusinessAgent v2 — Valida regras de negócio do Conecta PRO.
Verifica: CCT, contagem funcionários, alocações, clientes,
férias vencidas, eSocial pendente.
"""

import json
import urllib.error
import urllib.request
from datetime import date


BASE_URL = "http://127.0.0.1:8080"

PISOS_CCT_2026 = {
    "Agente de Portaria": 1670.00,
    "Agente de Serviços Gerais": 1670.00,
    "Artífice": 1742.52,
    "Líder de Portaria": 1787.53,
}
FUNCIONARIOS_ATIVOS_ESPERADO = 52
CLIENTES_ESPERADOS = 13
FERIAS_LIMITE_DIAS = 330  # ~11 meses — período aquisitivo quase vencido


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
        except urllib.error.HTTPError:
            return {}
        except Exception:
            return {}

    def _get_todos(self, base_path: str, page_size: int = 100) -> list:
        """Busca todos os registros paginados."""
        todos = []
        page = 1
        sep = "&" if "?" in base_path else "?"
        while True:
            data = self._get(f"{base_path}{sep}page={page}&page_size={page_size}")
            if isinstance(data, list):
                todos.extend(data)
                break
            items = data.get("items") or data.get("data") or data.get("results") or []
            if not items:
                break
            todos.extend(items)
            total = data.get("total") or data.get("count") or 0
            if len(todos) >= total or len(items) < page_size:
                break
            page += 1
        return todos

    def _items(self, data) -> list:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("items") or data.get("data") or data.get("results") or []
        return []

    def verificar_cct_conformidade(self) -> list:
        problemas = []
        for f in self._get_todos("/api/v1/people-management/hr/employees", 200):
            cargo = (
                f.get("cargo")
                or f.get("position")
                or f.get("job_title")
                or f.get("funcao")
                or ""
            )
            salario = float(
                f.get("salario")
                or f.get("salary")
                or f.get("wage")
                or f.get("salario_base")
                or 0
            )
            piso = PISOS_CCT_2026.get(cargo)
            if piso and salario > 0 and salario < piso:
                nome = f.get("nome") or f.get("name") or f.get("full_name") or "?"
                problemas.append(
                    {
                        "tipo": "cct_abaixo_piso",
                        "funcionario": nome,
                        "cargo": cargo,
                        "salario_atual": salario,
                        "piso_cct": piso,
                        "diferenca": round(piso - salario, 2),
                        "descricao": (
                            f"Salário abaixo do piso CCT: {nome} "
                            f"(R${salario:.2f} < R${piso:.2f})"
                        ),
                        "acao_jordan": True,
                    }
                )
        return problemas

    def verificar_contagem_funcionarios(self) -> list:
        todos = self._get_todos("/api/v1/people-management/hr/employees", 200)
        ativos = [
            f
            for f in todos
            if (
                f.get("status") in ["ativo", "active", "ATIVO", "ACTIVE"]
                or f.get("is_active") is True
                or (f.get("status") is None and f.get("id"))
            )
        ]
        if not ativos and todos:
            # Se nenhum status field, assume todos ativos
            ativos = todos
        n = len(ativos)
        if n != FUNCIONARIOS_ATIVOS_ESPERADO:
            return [
                {
                    "tipo": "contagem_funcionarios",
                    "esperado": FUNCIONARIOS_ATIVOS_ESPERADO,
                    "encontrado": n,
                    "descricao": (
                        f"Funcionários ativos: {n} "
                        f"(esperado: {FUNCIONARIOS_ATIVOS_ESPERADO})"
                    ),
                    "acao_jordan": n < 45 or n > 60,
                }
            ]
        return []

    def verificar_alocacoes_ativas(self) -> list:
        problemas = []
        postos = self._get_todos("/api/v1/operacional/posts/", 50)
        alocacoes = self._get_todos("/api/v1/operacional/allocations/", 100)
        postos_alocados = {
            a.get("post_id") or a.get("posto_id")
            for a in alocacoes
            if a.get("status") in ["ativo", "active", None] or a.get("is_active")
        }
        for posto in postos:
            pid = posto.get("id")
            nome = posto.get("nome") or posto.get("name") or "?"
            if pid and pid not in postos_alocados:
                problemas.append(
                    {
                        "tipo": "posto_sem_alocacao",
                        "posto": nome,
                        "descricao": f"Posto sem alocação ativa: {nome}",
                        "acao_jordan": True,
                    }
                )
        return problemas

    def verificar_clientes_ativos(self) -> list:
        todos = self._get_todos("/api/v1/crm/clients", 50)
        ativos = [
            c
            for c in todos
            if (
                c.get("status") in ["ativo", "active", "ATIVO", None]
                or c.get("is_active") is True
            )
        ]
        if not ativos:
            ativos = todos  # assume todos ativos se sem status
        if len(ativos) < CLIENTES_ESPERADOS:
            return [
                {
                    "tipo": "clientes_insuficientes",
                    "esperado": CLIENTES_ESPERADOS,
                    "encontrado": len(ativos),
                    "descricao": (
                        f"Clientes ativos: {len(ativos)} "
                        f"(esperado: ≥{CLIENTES_ESPERADOS})"
                    ),
                    "acao_jordan": True,
                }
            ]
        return []

    def verificar_ferias_vencidas(self) -> list:
        """Detecta funcionários com período aquisitivo quase vencido (>330 dias)."""
        problemas = []
        today = date.today()
        todos = self._get_todos("/api/v1/people-management/hr/employees", 200)
        for f in todos:
            data_admissao = (
                f.get("data_admissao")
                or f.get("admission_date")
                or f.get("hire_date")
                or f.get("admissao")
                or ""
            )
            if not data_admissao:
                continue
            try:
                admissao = date.fromisoformat(str(data_admissao)[:10])
            except Exception:
                continue
            # Período aquisitivo: 12 meses. Alerta se >330 dias sem férias registradas
            ferias_gozadas = f.get("ferias_gozadas") or f.get("vacations_taken") or []
            ultima_ferias = None
            if ferias_gozadas and isinstance(ferias_gozadas, list):
                datas = [
                    date.fromisoformat(str(v.get("data_inicio", ""))[:10])
                    for v in ferias_gozadas
                    if v.get("data_inicio")
                ]
                if datas:
                    ultima_ferias = max(datas)

            ref = ultima_ferias or admissao
            dias_desde_ferias = (today - ref).days
            if dias_desde_ferias > FERIAS_LIMITE_DIAS:
                nome = f.get("nome") or f.get("name") or "?"
                problemas.append(
                    {
                        "tipo": "ferias_vencendo",
                        "funcionario": nome,
                        "dias_sem_ferias": dias_desde_ferias,
                        "descricao": (
                            f"Férias vencendo: {nome} "
                            f"({dias_desde_ferias} dias sem férias)"
                        ),
                        "acao_jordan": dias_desde_ferias > 365,
                    }
                )
        return problemas

    def verificar_esocial_pendente(self) -> list:
        """Verifica se há pendências eSocial via endpoint de compliance DP."""
        pendencias = []
        data = self._get("/api/v1/people-management/dp/esocial/pendencias")
        items = self._items(data)
        for p in items:
            if p.get("status") in ["pendente", "pending", "PENDENTE"]:
                pendencias.append(
                    {
                        "tipo": "esocial_pendente",
                        "evento": p.get("evento") or p.get("event") or "?",
                        "descricao": (
                            f"eSocial pendente: "
                            f"{p.get('evento', p.get('descricao', '?'))}"
                        ),
                        "acao_jordan": True,
                    }
                )
        # Tenta endpoint alternativo
        if not items:
            data2 = self._get("/api/v1/people-management/dp/compliance")
            for p in self._items(data2):
                if p.get("tipo") == "esocial" and p.get("status") != "ok":
                    pendencias.append(
                        {
                            "tipo": "esocial_pendente",
                            "descricao": f"eSocial: {p.get('descricao', '?')}",
                            "acao_jordan": True,
                        }
                    )
        return pendencias

    def auditar(self) -> dict:
        print("🔍 BusinessAgent v2: validando regras de negócio...")
        todos = []
        todos.extend(self.verificar_cct_conformidade())
        todos.extend(self.verificar_contagem_funcionarios())
        todos.extend(self.verificar_alocacoes_ativas())
        todos.extend(self.verificar_clientes_ativos())
        todos.extend(self.verificar_ferias_vencidas())
        todos.extend(self.verificar_esocial_pendente())
        jordan = sum(1 for p in todos if p.get("acao_jordan"))
        score = max(0.0, 10.0 - len(todos) * 0.8)
        resultado = {
            "agente": "business",
            "score": round(min(score, 10.0), 1),
            "total_problemas": len(todos),
            "acao_jordan": jordan,
            "problemas": todos,
            "bugs": [
                {
                    "tipo": p.get("tipo"),
                    "descricao": p.get("descricao"),
                    "acao_jordan": p.get("acao_jordan", False),
                    "autocorrigivel": False,
                }
                for p in todos
            ],
        }
        print(
            f"  Problemas: {len(todos)} ({jordan} precisam Jordan) | "
            f"Score: {resultado['score']}/10"
        )
        return resultado


# ─── EXTENSÃO: VALIDAÇÃO DE FOLHA SALARIAL ────────────────


class BusinessPayrollAgent(BusinessAgent):
    """
    Estende BusinessAgent com validação de folha salarial brasileira.
    Verifica INSS, IRRF, FGTS, férias e piso CCT via PayrollValidator.
    """

    def verificar_calculos_folha(self) -> list:
        """Valida cálculos de INSS, IRRF e FGTS nos holerites recentes."""
        problemas = []
        try:
            from payroll_validator import PayrollValidator

            validator = PayrollValidator()
        except ImportError:
            return problemas

        # Endpoints alternativos para holerites
        endpoints = [
            "/api/v1/people-management/hr/payroll/payslips?page_size=10&mes=3&ano=2026",
            "/api/v1/people-management/hr/payroll/payslips?page_size=10",
            "/api/v1/people-management/hr/payroll/benefits?page_size=5",
        ]
        holerites = []
        for ep in endpoints:
            data = self._get(ep)
            holerites = self._items(data)
            if holerites:
                break

        erros_calculo = []
        for h in holerites[:10]:
            erros = validator.validar_holerite(h)
            if erros:
                nome = (
                    h.get("funcionario_nome")
                    or h.get("employee_name")
                    or h.get("nome")
                    or "?"
                )
                erros_calculo.extend([f"{nome}: {e}" for e in erros])

        if erros_calculo:
            problemas.append(
                {
                    "tipo": "calculo_folha_incorreto",
                    "quantidade": len(erros_calculo),
                    "descricao": f"{len(erros_calculo)} erro(s) de cálculo em holerites",
                    "detalhes": erros_calculo[:5],
                    "acao_jordan": True,
                }
            )

        return problemas

    def verificar_ferias_calculo(self) -> list:
        """Verifica se cálculos de férias programadas estão corretos."""
        problemas = []
        try:
            from payroll_validator import PayrollValidator
            from decimal import Decimal

            validator = PayrollValidator()
        except ImportError:
            return problemas

        endpoints = [
            "/api/v1/people-management/hr/employees/ferias?page_size=5&status=programada",
            "/api/v1/people-management/hr/payroll/ferias?page_size=5",
        ]
        ferias_list = []
        for ep in endpoints:
            data = self._get(ep)
            ferias_list = self._items(data)
            if ferias_list:
                break

        for f in ferias_list[:5]:
            salario = float(
                f.get("salario_bruto") or f.get("salary") or f.get("salario") or 0
            )
            if salario <= 0:
                continue
            calculo = validator.calcular_ferias(Decimal(str(salario)))
            valor_api = float(
                f.get("valor_ferias")
                or f.get("total_ferias")
                or f.get("valor_total")
                or 0
            )
            if valor_api > 0:
                diferenca = abs(valor_api - float(calculo["total_bruto"]))
                if diferenca > 1.0:
                    nome = f.get("nome") or f.get("employee_name") or "?"
                    problemas.append(
                        {
                            "tipo": "ferias_calculo_incorreto",
                            "funcionario": nome,
                            "valor_api": round(valor_api, 2),
                            "valor_esperado": float(calculo["total_bruto"]),
                            "diferenca": round(diferenca, 2),
                            "descricao": (
                                f"Férias incorretas: {nome} — "
                                f"API R${valor_api:.2f} vs "
                                f"esperado R${calculo['total_bruto']:.2f}"
                            ),
                            "acao_jordan": True,
                        }
                    )

        return problemas

    def verificar_piso_cct_com_decimal(self) -> list:
        """
        Verifica piso CCT em todos os funcionários usando Decimal.
        Complementa verificar_cct_conformidade() com precisão monetária.
        """
        from decimal import Decimal

        problemas = []
        funcionarios = self._get_todos("/api/v1/people-management/hr/employees", 200)
        abaixo = []
        for f in funcionarios:
            cargo = (
                f.get("cargo")
                or f.get("position")
                or f.get("job_title")
                or f.get("funcao")
                or ""
            )
            from payroll_validator import PISOS_CCT

            piso = PISOS_CCT.get(cargo)
            if not piso:
                continue
            salario_raw = (
                f.get("salario")
                or f.get("salary")
                or f.get("wage")
                or f.get("salario_base")
                or 0
            )
            try:
                salario = Decimal(str(salario_raw))
            except Exception:
                continue
            if salario > 0 and salario < piso:
                nome = f.get("nome") or f.get("name") or f.get("full_name") or "?"
                abaixo.append(
                    {
                        "nome": nome,
                        "cargo": cargo,
                        "salario": float(salario),
                        "piso_cct": float(piso),
                        "diferenca": float(piso - salario),
                    }
                )

        if abaixo:
            problemas.append(
                {
                    "tipo": "piso_cct_violado",
                    "quantidade": len(abaixo),
                    "descricao": (
                        f"CRÍTICO: {len(abaixo)} funcionário(s) "
                        f"com salário abaixo do piso CCT 2026"
                    ),
                    "detalhes": abaixo[:5],
                    "acao_jordan": True,
                }
            )

        return problemas

    def auditar(self) -> dict:
        """Auditoria completa: negócio + validação de folha salarial."""
        print("🔍 BusinessPayrollAgent: negócio + folha salarial 2026...")
        todos = []
        todos.extend(self.verificar_cct_conformidade())
        todos.extend(self.verificar_contagem_funcionarios())
        todos.extend(self.verificar_alocacoes_ativas())
        todos.extend(self.verificar_clientes_ativos())
        todos.extend(self.verificar_ferias_vencidas())
        todos.extend(self.verificar_esocial_pendente())
        todos.extend(self.verificar_calculos_folha())
        todos.extend(self.verificar_ferias_calculo())
        todos.extend(self.verificar_piso_cct_com_decimal())

        jordan = sum(1 for p in todos if p.get("acao_jordan"))
        score = round(min(max(0.0, 10.0 - len(todos) * 0.8), 10.0), 1)

        resultado = {
            "agente": "business_payroll",
            "score": score,
            "total_problemas": len(todos),
            "acao_jordan": jordan,
            "problemas": todos,
            "bugs": [
                {
                    "tipo": p.get("tipo"),
                    "descricao": p.get("descricao"),
                    "acao_jordan": p.get("acao_jordan", False),
                    "autocorrigivel": False,
                }
                for p in todos
            ],
        }
        print(f"  Problemas: {len(todos)} ({jordan} para Jordan) | Score: {score}/10")
        return resultado
