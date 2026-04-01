"""
DataQualityAgent — Verifica integridade e qualidade dos dados.
Detecta: CPFs/CNPJs inválidos, duplicatas, campos vazios.
"""

import json
import re
import urllib.request


BASE_URL = "http://127.0.0.1:8080"


def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r"\D", "", cpf or "")
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        if (soma * 10 % 11) % 10 != int(cpf[i]):
            return False
    return True


def validar_cnpj(cnpj: str) -> bool:
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

    def _items(self, data) -> list:
        if isinstance(data, dict):
            return data.get("items", data.get("data", []))
        return data if isinstance(data, list) else []

    def verificar_funcionarios(self) -> list:
        problemas = []
        data = self._get("/api/v1/people-management/hr/employees?page_size=100")
        cpfs_vistos = {}
        for f in self._items(data):
            fid = f.get("id", "?")
            nome = f.get("nome") or f.get("name", "?")
            cpf = f.get("cpf", "")
            if cpf and not validar_cpf(cpf):
                problemas.append(
                    {
                        "tabela": "employees",
                        "id": fid,
                        "campo": "cpf",
                        "descricao": f"CPF inválido: {nome}",
                    }
                )
            if cpf:
                if cpf in cpfs_vistos:
                    problemas.append(
                        {
                            "tabela": "employees",
                            "id": fid,
                            "campo": "cpf",
                            "descricao": f"CPF duplicado: {nome} e {cpfs_vistos[cpf]}",
                        }
                    )
                else:
                    cpfs_vistos[cpf] = nome
            is_active = f.get("is_active")
            status = f.get("status", "")
            if is_active is not None and status:
                esperado = status in ["ativo", "active"]
                if bool(is_active) != esperado:
                    problemas.append(
                        {
                            "tabela": "employees",
                            "id": fid,
                            "campo": "is_active",
                            "descricao": f"is_active diverge de status: {nome} (is_active={is_active}, status={status})",
                            "autocorrigivel": True,
                        }
                    )
        return problemas

    def verificar_clientes(self) -> list:
        problemas = []
        data = self._get("/api/v1/crm/clients?page_size=50")
        for c in self._items(data):
            cid = c.get("id", "?")
            nome = c.get("nome") or c.get("name", "?")
            cnpj = c.get("cnpj", "")
            if cnpj and not validar_cnpj(cnpj):
                problemas.append(
                    {
                        "tabela": "clients",
                        "id": cid,
                        "campo": "cnpj",
                        "descricao": f"CNPJ inválido: {nome}",
                    }
                )
        return problemas

    def verificar_alocacoes(self) -> list:
        problemas = []
        data = self._get("/api/v1/operacional/allocations/?page_size=100")
        for a in self._items(data):
            aid = a.get("id", "?")
            if not a.get("employee_id") and not a.get("funcionario_id"):
                problemas.append(
                    {
                        "tabela": "allocations",
                        "id": aid,
                        "campo": "employee_id",
                        "descricao": "Alocação sem funcionário vinculado",
                    }
                )
            if not a.get("post_id") and not a.get("posto_id"):
                problemas.append(
                    {
                        "tabela": "allocations",
                        "id": aid,
                        "campo": "post_id",
                        "descricao": "Alocação sem posto vinculado",
                    }
                )
        return problemas

    def auditar(self) -> dict:
        print("🔍 DataQualityAgent: verificando dados...")
        todos = []
        todos.extend(self.verificar_funcionarios())
        todos.extend(self.verificar_clientes())
        todos.extend(self.verificar_alocacoes())
        autocorrigiveis = sum(1 for p in todos if p.get("autocorrigivel"))
        score = max(0, 10 - len(todos) * 0.5)
        resultado = {
            "agente": "data_quality",
            "score": round(min(score, 10.0), 1),
            "total_problemas": len(todos),
            "autocorrigiveis": autocorrigiveis,
            "problemas": todos[:20],
            "bugs": [
                {
                    "tipo": p.get("campo", "data"),
                    "tabela": p.get("tabela"),
                    "descricao": p.get("descricao"),
                    "autocorrigivel": p.get("autocorrigivel", False),
                }
                for p in todos[:10]
            ],
        }
        print(
            f"  Problemas: {len(todos)} ({autocorrigiveis} autocorrigíveis), Score: {resultado['score']}/10"
        )
        return resultado
