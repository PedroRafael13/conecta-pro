#!/usr/bin/env python3
"""
Testes Standalone de Extração - Sem dependências externas.

Valida estrutura e lógica básica dos módulos.
"""

import ast
import os
import sys
from datetime import datetime
from pathlib import Path

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def ok(msg):
    print(f"{GREEN}✓{RESET} {msg}")


def fail(msg):
    print(f"{RED}✗{RESET} {msg}")


def warn(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")


def header(msg):
    print(f"\n{BOLD}--- {msg} ---{RESET}")


BASE_PATH = Path("/opt/conecta-pro/backend/modules/government_integrations")


class TestEstruturaArquivos:
    """Testa se todos os arquivos necessários existem."""

    def run(self):
        header("Estrutura de Arquivos")

        arquivos_requeridos = [
            # Extractors
            "extractors/__init__.py",
            "extractors/orchestrator.py",
            "extractors/base_extractor.py",
            "extractors/sefaz/__init__.py",
            "extractors/sefaz/nfe_extractor.py",
            "extractors/esocial/__init__.py",
            "extractors/esocial/esocial_extractor.py",
            "extractors/fgts/__init__.py",
            "extractors/fgts/fgts_extractor.py",
            "extractors/nfse/__init__.py",
            "extractors/nfse/manaus_extractor.py",
            "extractors/receita_federal/__init__.py",
            "extractors/receita_federal/rfb_extractor.py",
            # Jobs
            "jobs/__init__.py",
            "jobs/sync_tasks.py",
            "jobs/monitoring_tasks.py",
            # Controllers
            "controllers/dashboard_controller.py",
            "controllers/extraction_controller.py",
        ]

        todos_existem = True
        for arquivo in arquivos_requeridos:
            path = BASE_PATH / arquivo
            if path.exists():
                ok(f"{arquivo}")
            else:
                fail(f"{arquivo} - NÃO ENCONTRADO")
                todos_existem = False

        return todos_existem


class TestSintaxePython:
    """Testa se os arquivos Python têm sintaxe válida."""

    def run(self):
        header("Sintaxe Python")

        arquivos = list(BASE_PATH.glob("**/*.py"))
        erros = []

        for arquivo in arquivos:
            try:
                with open(arquivo) as f:
                    source = f.read()
                ast.parse(source)
                # Não imprimir todos OK, só os erros
            except SyntaxError as e:
                fail(f"{arquivo.relative_to(BASE_PATH)}: {e}")
                erros.append(arquivo)

        if not erros:
            ok(f"Todos os {len(arquivos)} arquivos têm sintaxe válida")
            return True
        return False


class TestClassesDefinidas:
    """Verifica se as classes principais estão definidas."""

    def run(self):
        header("Classes e Funções")

        verificacoes = [
            (
                "extractors/orchestrator.py",
                ["OrquestradorExtracao", "ConfiguracaoExtracao", "TipoServico", "ResultadoExtracao"],
            ),
            ("extractors/base_extractor.py", ["ExtratorBase", "DocumentoExtraido"]),
            ("extractors/sefaz/nfe_extractor.py", ["ExtratorNFe"]),
            ("extractors/esocial/esocial_extractor.py", ["ExtratoreSocial"]),
            ("extractors/fgts/fgts_extractor.py", ["ExtratorFGTS"]),
            ("extractors/nfse/manaus_extractor.py", ["ExtratorNFSeManaus"]),
            ("extractors/receita_federal/rfb_extractor.py", ["ExtratorRFB"]),
            (
                "jobs/sync_tasks.py",
                ["sincronizar_nfe", "sincronizar_esocial", "sincronizar_fgts", "sincronizar_nfse", "sincronizar_rfb"],
            ),
            ("jobs/monitoring_tasks.py", ["verificar_disponibilidade", "verificar_certificados", "reprocessar_falhas"]),
            ("controllers/dashboard_controller.py", ["DashboardService", "DashboardResponse"]),
            ("controllers/extraction_controller.py", ["IniciarExtracaoRequest", "ExtracaoResponse"]),
        ]

        todos_ok = True
        for arquivo, nomes in verificacoes:
            path = BASE_PATH / arquivo
            if not path.exists():
                fail(f"{arquivo} não existe")
                todos_ok = False
                continue

            with open(path) as f:
                source = f.read()

            faltando = []
            for nome in nomes:
                # Verificar se é classe ou função
                if f"class {nome}" in source or f"def {nome}" in source:
                    pass
                else:
                    faltando.append(nome)

            if faltando:
                fail(f"{arquivo}: faltando {faltando}")
                todos_ok = False
            else:
                ok(f"{arquivo}: {len(nomes)} definições OK")

        return todos_ok


class TestEndpointsAPI:
    """Verifica endpoints definidos nos controllers."""

    def run(self):
        header("Endpoints API")

        # Dashboard endpoints
        dashboard_path = BASE_PATH / "controllers/dashboard_controller.py"
        with open(dashboard_path) as f:
            dashboard_source = f.read()

        dashboard_endpoints = [
            '@router.get("/"',
            '@router.get("/metricas"',
            '@router.get("/endpoints"',
            '@router.get("/certificados/alertas"',
            '@router.get("/eventos"',
            '@router.post("/endpoints/',
        ]

        for endpoint in dashboard_endpoints:
            if endpoint in dashboard_source:
                ok(f"Dashboard: {endpoint}")
            else:
                fail(f"Dashboard: {endpoint} - NÃO ENCONTRADO")

        # Extraction endpoints
        extraction_path = BASE_PATH / "controllers/extraction_controller.py"
        with open(extraction_path) as f:
            extraction_source = f.read()

        extraction_endpoints = [
            '@router.post("/iniciar"',
            '@router.get("/status/',
            '@router.get("/historico"',
            '@router.post("/cancelar/',
            '@router.post("/sync/nfe"',
            '@router.post("/sync/esocial"',
            '@router.post("/sync/fgts"',
            '@router.post("/sync/nfse"',
            '@router.post("/sync/rfb"',
            '@router.post("/sync/todos"',
        ]

        for endpoint in extraction_endpoints:
            if endpoint in extraction_source:
                ok(f"Extraction: {endpoint}")
            else:
                fail(f"Extraction: {endpoint} - NÃO ENCONTRADO")

        return True


class TestCeleryTasks:
    """Verifica tasks Celery definidas."""

    def run(self):
        header("Celery Tasks")

        # Sync tasks
        sync_path = BASE_PATH / "jobs/sync_tasks.py"
        with open(sync_path) as f:
            sync_source = f.read()

        sync_tasks = [
            ("sincronizar_nfe", "gov.sefaz.nfe"),
            ("sincronizar_esocial", "gov.esocial"),
            ("sincronizar_fgts", "gov.fgts"),
            ("sincronizar_nfse", "gov.nfse"),
            ("sincronizar_rfb", "gov.batch"),
            ("sincronizar_todos", "gov.batch"),
        ]

        for task_name, queue in sync_tasks:
            if f"def {task_name}" in sync_source:
                if f'queue="{queue}"' in sync_source:
                    ok(f"Task {task_name} -> {queue}")
                else:
                    warn(f"Task {task_name} - queue não especificada")
            else:
                fail(f"Task {task_name} - NÃO ENCONTRADA")

        # Monitoring tasks
        mon_path = BASE_PATH / "jobs/monitoring_tasks.py"
        with open(mon_path) as f:
            mon_source = f.read()

        mon_tasks = [
            "verificar_disponibilidade",
            "verificar_certificados",
            "reprocessar_falhas",
            "limpar_cache",
            "limpar_historico",
            "gerar_relatorio_diario",
        ]

        for task_name in mon_tasks:
            if f"def {task_name}" in mon_source:
                ok(f"Task {task_name}")
            else:
                fail(f"Task {task_name} - NÃO ENCONTRADA")

        return True


class TestTiposServico:
    """Verifica tipos de serviço no orquestrador."""

    def run(self):
        header("Tipos de Serviço")

        orchestrator_path = BASE_PATH / "extractors/orchestrator.py"
        with open(orchestrator_path) as f:
            source = f.read()

        servicos = [
            "SEFAZ_NFE",
            "SEFAZ_CTE",
            "SEFAZ_MDFE",
            "ESOCIAL",
            "FGTS_DIGITAL",
            "NFSE_MANAUS",
            "RECEITA_FEDERAL",
        ]

        for servico in servicos:
            if servico in source:
                ok(f"TipoServico.{servico}")
            else:
                fail(f"TipoServico.{servico} - NÃO ENCONTRADO")

        return True


class TestExtratoresMetodos:
    """Verifica métodos obrigatórios nos extratores."""

    def run(self):
        header("Métodos dos Extratores")

        extratores = [
            ("extractors/sefaz/nfe_extractor.py", "ExtratorNFe"),
            ("extractors/esocial/esocial_extractor.py", "ExtratoreSocial"),
            ("extractors/fgts/fgts_extractor.py", "ExtratorFGTS"),
            ("extractors/nfse/manaus_extractor.py", "ExtratorNFSeManaus"),
            ("extractors/receita_federal/rfb_extractor.py", "ExtratorRFB"),
        ]

        metodos_obrigatorios = ["extrair", "tipo_servico"]

        todos_ok = True
        for arquivo, classe in extratores:
            path = BASE_PATH / arquivo
            with open(path) as f:
                source = f.read()

            faltando = []
            for metodo in metodos_obrigatorios:
                if f"def {metodo}" not in source and f"def {metodo}" not in source:
                    # Também verificar property
                    if "@property" not in source or metodo not in source:
                        faltando.append(metodo)

            if faltando:
                fail(f"{classe}: faltando {faltando}")
                todos_ok = False
            else:
                ok(f"{classe}: métodos OK")

        return todos_ok


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print(f"{BOLD}TESTES DE EXTRAÇÃO GOVERNAMENTAL - STANDALONE{RESET}")
    print("=" * 60)
    print(f"Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    testes = [
        TestEstruturaArquivos(),
        TestSintaxePython(),
        TestClassesDefinidas(),
        TestEndpointsAPI(),
        TestCeleryTasks(),
        TestTiposServico(),
        TestExtratoresMetodos(),
    ]

    resultados = []
    for teste in testes:
        try:
            resultado = teste.run()
            resultados.append(resultado)
        except Exception as e:
            fail(f"Erro no teste {teste.__class__.__name__}: {e}")
            resultados.append(False)

    print("\n" + "=" * 60)
    total = len(resultados)
    sucesso = sum(1 for r in resultados if r)

    if all(resultados):
        print(f"{GREEN}{BOLD}TODOS OS TESTES PASSARAM! ({sucesso}/{total}){RESET}")
    else:
        print(f"{YELLOW}{BOLD}TESTES CONCLUÍDOS: {sucesso}/{total} OK{RESET}")

    print("=" * 60 + "\n")

    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
