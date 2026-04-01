"""
ConhecimentoTotal — Interface unificada para todo o conhecimento do Conecta PRO.

O CTO consulta esta classe para qualquer informação sobre o sistema:
código, banco, integrações, infraestrutura, agentes.

"Onde está o código que processa folha?"
"Quais endpoints existem para /employees?"
"Qual tabela guarda os pagamentos?"
"Como funciona a integração com a Cora?"
"Qual agente monitora performance?"
"""
import json
import re
import subprocess
from pathlib import Path
from typing import Optional

KNOWLEDGE_DIR = Path("/opt/conecta-pro/agents/cto/knowledge")
CODIGO_DIR   = KNOWLEDGE_DIR / "codigo"
BANCO_DIR    = KNOWLEDGE_DIR / "banco"
INTEGRACOES_DIR = KNOWLEDGE_DIR / "integracoes"
FRONTEND_DIR = KNOWLEDGE_DIR / "frontend"
INFRA_DIR    = KNOWLEDGE_DIR / "infraestrutura"


class ConhecimentoTotal:
    """
    Interface unificada para todo conhecimento do sistema.
    O CTO consulta aqui antes de qualquer diagnóstico.
    """

    def __init__(self):
        self._backend   = None
        self._banco     = None
        self._integracoes = None
        self._frontend  = None
        self._infra     = None
        self._agents    = None
        print("[ConhecimentoTotal] Inicializado")

    def _carregar(self, path: Path) -> dict:
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return {}

    @property
    def backend(self) -> dict:
        if self._backend is None:
            self._backend = self._carregar(CODIGO_DIR / "backend_completo.json")
        return self._backend

    @property
    def banco(self) -> dict:
        if self._banco is None:
            self._banco = self._carregar(BANCO_DIR / "banco_completo.json")
        return self._banco

    @property
    def integracoes(self) -> dict:
        if self._integracoes is None:
            self._integracoes = self._carregar(INTEGRACOES_DIR / "integracoes_completo.json")
        return self._integracoes

    @property
    def frontend(self) -> dict:
        if self._frontend is None:
            self._frontend = self._carregar(FRONTEND_DIR / "frontend_completo.json")
        return self._frontend

    @property
    def infra(self) -> dict:
        if self._infra is None:
            self._infra = self._carregar(INFRA_DIR / "infraestrutura_completo.json")
        return self._infra

    # ─── BUSCA NO CÓDIGO ──────────────────────────────────────────────────────

    def buscar_codigo(self, termo: str, tipo: str = "todos") -> list:
        """
        Busca no código indexado por termo.
        Retorna arquivos e funções relacionadas.

        Uso: buscar_codigo("folha", "service")
             buscar_codigo("redis", "todos")
        """
        resultados = []
        modulos = self.backend.get("modulos", {})

        for arquivo, info in modulos.items():
            if tipo != "todos":
                if tipo == "service" and "service" not in arquivo.lower():
                    continue
                elif tipo == "model" and "model" not in arquivo.lower():
                    continue
                elif tipo == "controller" and "controller" not in arquivo.lower():
                    continue

            funcoes_match = [
                f for f in info.get("funcoes", [])
                if termo.lower() in f["nome"].lower()
                or termo.lower() in f.get("docstring", "").lower()
            ]
            classes_match = [
                c for c in info.get("classes", [])
                if termo.lower() in c["nome"].lower()
                or termo.lower() in c.get("docstring", "").lower()
            ]
            endpoints_match = [
                e for e in info.get("endpoints", [])
                if termo.lower() in e["path"].lower()
            ]

            if funcoes_match or classes_match or endpoints_match:
                resultados.append({
                    "arquivo": arquivo,
                    "funcoes": funcoes_match[:5],
                    "classes": classes_match[:3],
                    "endpoints": endpoints_match[:5],
                })

        return resultados[:10]

    def buscar_endpoint(self, path: str) -> list:
        """
        Encontra onde um endpoint está implementado.

        Uso: buscar_endpoint("/employees")
             buscar_endpoint("/folha/calcular")
        """
        endpoints = self.backend.get("endpoints", [])
        return [e for e in endpoints if path.lower() in e["path"].lower()][:10]

    def buscar_no_codigo_real(self, termo: str, extensao: str = "py") -> list:
        """
        Busca diretamente nos arquivos com grep.
        Mais poderoso que o índice — busca texto real.
        """
        r = subprocess.run(
            f"grep -rn '{termo}' /opt/conecta-pro/backend "
            f"--include='*.{extensao}' "
            f"--exclude-dir=__pycache__ --exclude-dir=alembic "
            f"-l 2>/dev/null | head -10",
            shell=True, capture_output=True, text=True
        )
        return [l.strip() for l in r.stdout.split("\n") if l.strip()]

    def ver_funcao(self, arquivo: str, funcao: str) -> str:
        """
        Retorna o código real de uma função específica.

        Uso: ver_funcao("modules/financeiro/services/folha.py", "calcular_folha")
        """
        for base in ["/opt/conecta-pro/backend", "/opt/conecta-pro"]:
            fpath = Path(f"{base}/{arquivo}")
            if fpath.exists():
                break
        else:
            return f"Arquivo não encontrado: {arquivo}"

        content = fpath.read_text(encoding="utf-8", errors="ignore")
        linhas = content.split("\n")

        inicio = None
        for i, linha in enumerate(linhas):
            if re.search(rf'def {re.escape(funcao)}\s*\(', linha):
                inicio = i
                break

        if inicio is None:
            return f"Função '{funcao}' não encontrada"

        trecho = []
        for i in range(inicio, min(inicio + 80, len(linhas))):
            linha = linhas[i]
            trecho.append(f"{i+1}: {linha}")
            if i > inicio and (
                linha.strip().startswith("def ") or
                linha.strip().startswith("class ")
            ) and not linha.startswith(" "):
                break

        return "\n".join(trecho[:60])

    # ─── BUSCA NO BANCO ───────────────────────────────────────────────────────

    def buscar_tabela(self, nome: str) -> dict:
        """
        Retorna estrutura completa de uma tabela.

        Uso: buscar_tabela("employees")
             buscar_tabela("payable_accounts")
        """
        tabelas = self.banco.get("tabelas", {})

        if nome in tabelas:
            return tabelas[nome]

        matches = {k: v for k, v in tabelas.items() if nome.lower() in k.lower()}
        return matches

    def buscar_fk(self, tabela: str) -> list:
        """Retorna todas as FK relacionadas a uma tabela."""
        fks = self.banco.get("foreign_keys", [])
        return [
            fk for fk in fks
            if tabela.lower() in fk.get("tabela_origem", "").lower()
            or tabela.lower() in fk.get("tabela_destino", "").lower()
        ]

    def tabelas_com_mais_registros(self, top: int = 10) -> list:
        """Tabelas com mais dados."""
        est = self.banco.get("estatisticas", {})
        return est.get("tabelas_por_registros", [])[:top]

    # ─── BUSCA EM INTEGRAÇÕES ─────────────────────────────────────────────────

    def info_integracao(self, nome: str) -> dict:
        """
        Retorna tudo sobre uma integração.

        Uso: info_integracao("cora")
             info_integracao("esocial")
        """
        lista = self.integracoes.get("lista", {})
        if nome.lower() in lista:
            return lista[nome.lower()]

        matches = {k: v for k, v in lista.items() if nome.lower() in k.lower()}
        return matches

    # ─── BUSCA NO FRONTEND ────────────────────────────────────────────────────

    def buscar_pagina(self, rota: str) -> list:
        """
        Encontra a página que implementa uma rota.

        Uso: buscar_pagina("/modulos/dp/folha")
             buscar_pagina("/modulos/financeiro")
        """
        paginas = self.frontend.get("paginas", [])
        return [
            p for p in paginas
            if rota.lower() in p.get("rota", "").lower()
            or rota.lower() in p.get("arquivo", "").lower()
        ]

    def chamadas_api_frontend(self, endpoint: str) -> list:
        """Quais páginas do frontend chamam um endpoint?"""
        paginas = self.frontend.get("paginas", [])
        return [
            {"pagina": p["arquivo"], "rota": p.get("rota", "")}
            for p in paginas
            if any(endpoint.lower() in c.lower() for c in p.get("chamadas_api", []))
        ]

    # ─── DIAGNÓSTICO CONTEXTUALIZADO ──────────────────────────────────────────

    def diagnosticar_com_contexto(self, problema: str) -> dict:
        """
        Diagnóstico usando conhecimento total do sistema.

        Uso: diagnosticar_com_contexto("Redis lento")
             diagnosticar_com_contexto("folha incorreta")
             diagnosticar_com_contexto("NFS-e não emite")
        """
        p = problema.lower()
        resultado = {
            "problema": problema,
            "codigo_relacionado": [],
            "tabelas_relacionadas": [],
            "integracao_relacionada": None,
            "endpoints_relacionados": [],
            "causa_provavel": "",
            "onde_corrigir": [],
        }

        if "redis" in p:
            resultado["codigo_relacionado"] = self.buscar_no_codigo_real("redis")
            resultado["integracao_relacionada"] = self.info_integracao("redis")
            resultado["causa_provavel"] = "Verificar: swap alto, maxmemory, conexões não fechadas"

        elif any(k in p for k in ["folha", "salario", "payroll", "holerite"]):
            resultado["codigo_relacionado"] = self.buscar_codigo("folha", "service")
            resultado["tabelas_relacionadas"] = [
                self.buscar_tabela("payslip"),
                self.buscar_tabela("payroll"),
                self.buscar_tabela("employee"),
            ]
            resultado["endpoints_relacionados"] = (
                self.buscar_endpoint("/folha") + self.buscar_endpoint("/payroll")
            )
            resultado["causa_provavel"] = (
                "Verificar: cálculo INSS/IRRF, campo total_proventos vs total_bruto, "
                "período de competência"
            )

        elif any(k in p for k in ["nfs", "nota", "fiscal", "nfse"]):
            resultado["codigo_relacionado"] = self.buscar_no_codigo_real("nfse")
            resultado["integracao_relacionada"] = self.info_integracao("nfse")
            resultado["causa_provavel"] = "Verificar: certificado A1, Celery ativo, SEFAZ disponível"

        elif "esocial" in p:
            resultado["codigo_relacionado"] = self.buscar_no_codigo_real("esocial")
            resultado["integracao_relacionada"] = self.info_integracao("esocial")
            resultado["tabelas_relacionadas"] = [self.buscar_tabela("esocial")]

        elif "celery" in p:
            resultado["codigo_relacionado"] = self.buscar_no_codigo_real("celery")
            resultado["integracao_relacionada"] = self.info_integracao("celery")
            resultado["causa_provavel"] = "Verificar: broker Redis, workers ativos, filas travadas"

        elif any(k in p for k in ["banco", "cora", "inter", "pagamento", "boleto"]):
            resultado["codigo_relacionado"] = self.buscar_no_codigo_real("cora")
            resultado["integracao_relacionada"] = self.info_integracao("cora")
            resultado["tabelas_relacionadas"] = [
                self.buscar_tabela("bank_transactions"),
                self.buscar_tabela("payable_accounts"),
            ]
            resultado["causa_provavel"] = "Verificar: credenciais Cora/Inter, certificado, timeout"

        return resultado

    def resumo_conhecimento(self) -> dict:
        """Resumo do que o CTO conhece."""
        backend_resumo  = self._carregar(CODIGO_DIR / "backend_resumo.json")
        banco_resumo    = self._carregar(BANCO_DIR / "banco_resumo.json")
        frontend_resumo = self._carregar(FRONTEND_DIR / "frontend_resumo.json")
        infra_data      = self._carregar(INFRA_DIR / "infraestrutura_completo.json")
        agents_data     = self._carregar(CODIGO_DIR / "agents_index.json")

        return {
            "backend": {
                "arquivos":  backend_resumo.get("total_arquivos", 0),
                "linhas":    backend_resumo.get("total_linhas", 0),
                "endpoints": backend_resumo.get("total_endpoints", 0),
                "funcoes":   backend_resumo.get("total_funcoes", 0),
                "classes":   backend_resumo.get("total_classes", 0),
            },
            "banco": {
                "tabelas": banco_resumo.get("total_tabelas", 0),
                "fks":     banco_resumo.get("total_fks", 0),
                "indices": banco_resumo.get("total_indices", 0),
                "enums":   banco_resumo.get("total_enums", 0),
            },
            "frontend": {
                "paginas":     frontend_resumo.get("total_paginas", 0),
                "componentes": frontend_resumo.get("total_componentes", 0),
                "rotas":       frontend_resumo.get("total_rotas", 0),
                "hooks":       frontend_resumo.get("total_hooks", 0),
            },
            "integracoes": len(self.integracoes.get("lista", {})),
            "infra": {
                "containers": len(infra_data.get("containers", {})),
                "crons":      len(infra_data.get("crons", [])),
                "vars_env":   len(infra_data.get("variaveis_ambiente", [])),
            },
            "agents": {
                "modulos":      len(agents_data.get("modulos", [])),
                "cto_arquivos": len(agents_data.get("cto", [])),
                "migrations":   len(self._carregar(CODIGO_DIR / "migrations_index.json")),
            },
        }
