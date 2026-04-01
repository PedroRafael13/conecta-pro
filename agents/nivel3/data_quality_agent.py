"""
DataQualityAgent — Verifica integridade e qualidade dos dados.
Detecta: registros órfãos, CPFs/CNPJs inválidos, duplicatas,
campos obrigatórios vazios, inconsistências.
"""
import json
import re
import urllib.request


BASE_URL = "http://127.0.0.1:8080"


def validar_cpf(cpf: str) -> bool:
    """Valida CPF com dígitos verificadores."""
    cpf = re.sub(r"\D", "", cpf or "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ com dígitos verificadores."""
    cnpj = re.sub(r"\D", "", cnpj or "")
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    for pesos in [pesos1, pesos2]:
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
        digito = 0 if soma % 11 < 2 else 11 - soma % 11
        if digito != int(cnpj[len(pesos)]):
            return False
    return True


class DataQualityAgent:
    """Verifica qualidade e integridade dos dados."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "data_quality"

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

    def verificar_funcionarios(self) -> list:
        """Verifica qualidade dos dados de funcionários."""
        problemas = []

        data = self._get(
            "/api/v1/people-management/hr/employees?page_size=100"
        )
        funcionarios = (
            data.get("items", data) if isinstance(data, dict) else data
        )
        if not isinstance(funcionarios, list):
            return problemas

        cpfs_vistos = {}
        for f in funcionarios:
            fid = f.get("id", "?")
            nome = f.get("nome") or f.get("name", "?")

            cpf = f.get("cpf", "")
            if cpf and not validar_cpf(cpf):
                problemas.append({
                    "tabela": "employees",
                    "id": fid,
                    "campo": "cpf",
                    "valor": cpf,
                    "descricao": f"CPF inválido: {nome}",
                })

            if cpf:
                if cpf in cpfs_vistos:
                    problemas.append({
                        "tabela": "employees",
                        "id": fid,
                        "campo": "cpf",
                        "descricao": (
                            f"CPF duplicado: {nome} e {cpfs_vistos[cpf]}"
                        ),
                    })
                else:
                    cpfs_vistos[cpf] = nome

            for campo in ["nome", "cpf", "cargo", "status"]:
                val = f.get(campo) or f.get(
                    campo.replace("nome", "name"), ""
                )
                if not val:
                    problemas.append({
                        "tabela": "employees",
                        "id": fid,
                        "campo": campo,
                        "descricao": (
                            f"Campo obrigatório vazio: {campo} em {nome}"
                        ),
                    })

            is_active = f.get("is_active")
            status = f.get("status", "")
            if is_active is not None and status:
                esperado = status in ["ativo", "active"]
                if bool(is_active) != esperado:
                    problemas.append({
                        "tabela": "employees",
                        "id": fid,
                        "campo": "is_active",
                        "descricao": (
                            f"is_active diverge de status: {nome} "
                            f"(is_active={is_active}, status={status})"
                        ),
                        "autocorrigivel": True,
                    })

        return problemas

    def verificar_clientes(self) -> list:
        """Verifica qualidade dos dados de clientes."""
        problemas = []

        data = self._get("/api/v1/crm/clients?page_size=50")
        clientes = (
            data.get("items", data) if isinstance(data, dict) else data
        )
        if not isinstance(clientes, list):
            return problemas

        for c in clientes:
            cid = c.get("id", "?")
            nome = c.get("nome") or c.get("name", "?")

            cnpj = c.get("cnpj", "")
            if cnpj and not validar_cnpj(cnpj):
                problemas.append({
                    "tabela": "clients",
                    "id": cid,
                    "campo": "cnpj",
                    "descricao": f"CNPJ inválido: {nome}",
                })

            for campo in ["nome", "cnpj"]:
                val = c.get(campo) or c.get(
                    campo.replace("nome", "name"), ""
                )
                if not val:
                    problemas.append({
                        "tabela": "clients",
                        "id": cid,
                        "campo": campo,
                        "descricao": (
                            f"Campo obrigatório vazio: {campo} em {nome}"
                        ),
                    })

        return problemas

    def verificar_alocacoes(self) -> list:
        """Detecta alocações órfãs (sem funcionário ou posto)."""
        problemas = []

        data = self._get("/api/v1/operacional/allocations/?page_size=100")
        alocacoes = (
            data.get("items", data) if isinstance(data, dict) else data
        )
        if not isinstance(alocacoes, list):
            return problemas

        for a in alocacoes:
            aid = a.get("id", "?")

            if not a.get("employee_id") and not a.get("funcionario_id"):
                problemas.append({
                    "tabela": "allocations",
                    "id": aid,
                    "campo": "employee_id",
                    "descricao": "Alocação sem funcionário vinculado",
                })

            if not a.get("post_id") and not a.get("posto_id"):
                problemas.append({
                    "tabela": "allocations",
                    "id": aid,
                    "campo": "post_id",
                    "descricao": "Alocação sem posto vinculado",
                })

        return problemas

    def auditar(self) -> dict:
        """Executa auditoria completa de qualidade de dados."""
        print("🔍 DataQualityAgent: verificando dados...")

        todos_problemas = []
        todos_problemas.extend(self.verificar_funcionarios())
        todos_problemas.extend(self.verificar_clientes())
        todos_problemas.extend(self.verificar_alocacoes())

        autocorrigiveis = [
            p for p in todos_problemas if p.get("autocorrigivel")
        ]
        score = max(0, 10 - len(todos_problemas) * 0.5)

        resultado = {
            "agente": "data_quality",
            "score": round(min(score, 10.0), 1),
            "total_problemas": len(todos_problemas),
            "autocorrigiveis": len(autocorrigiveis),
            "problemas": todos_problemas[:20],
            "bugs": [
                {
                    "tipo": p.get("campo", "data"),
                    "tabela": p.get("tabela"),
                    "descricao": p.get("descricao"),
                    "autocorrigivel": p.get("autocorrigivel", False),
                }
                for p in todos_problemas[:10]
            ],
        }

        print(
            f"  Problemas: {len(todos_problemas)} "
            f"({len(autocorrigiveis)} autocorrigíveis)"
        )
        print(f"  Score: {resultado['score']}/10")
        return resultado
