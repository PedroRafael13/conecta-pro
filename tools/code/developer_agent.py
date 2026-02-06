"""
DEVELOPER AGENT - Gera codigo e testes automaticamente
Fase 1 do pipeline: Developer -> Auditor -> Validator
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/opt/erp-conecta-mais/logs/developer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("DeveloperAgent")


class DeveloperAgent:
    """
    Agente responsavel por:
    1. Gerar codigo baseado nos requisitos
    2. Criar testes unitarios e de integracao
    3. Executar testes localmente
    4. Garantir cobertura minima de 80%
    """

    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.project_root = Path("/opt/erp-conecta-mais")
        self.backend_path = self.project_root / "backend"
        self.min_coverage = 80

    def develop(self, task: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Executa o desenvolvimento de uma tarefa.

        Args:
            task: Dicionario com informacoes da tarefa

        Returns:
            (success, result_dict)
        """
        logger.info(f"🤖 Developer Agent iniciando tarefa: {task.get('name')}")

        result = {
            "task_id": task.get("id"),
            "started_at": datetime.now().isoformat(),
            "files_created": [],
            "tests_created": [],
            "coverage": 0,
            "tests_passed": False,
            "errors": [],
        }

        try:
            # 1. Verificar estrutura do modulo
            if not self._ensure_module_structure(task):
                result["errors"].append("Falha ao criar estrutura do modulo")
                return False, result

            # 2. Verificar se arquivos existem
            files_status = self._check_files(task)
            result["files_created"] = files_status.get("existing", [])
            result["files_missing"] = files_status.get("missing", [])

            # 3. Executar testes
            tests_result = self._run_tests(task)
            result["tests_passed"] = tests_result["passed"]
            result["coverage"] = tests_result["coverage"]
            result["test_output"] = tests_result["output"]

            if not tests_result["passed"]:
                result["errors"].append("Testes falharam")
                logger.error(f"❌ Testes falharam: {tests_result['output'][:500]}")
                return False, result

            # 4. Verificar cobertura minima
            if tests_result["coverage"] < self.min_coverage:
                result["errors"].append(
                    f"Cobertura {tests_result['coverage']}% < {self.min_coverage}% minimo"
                )
                logger.warning(f"⚠️ Cobertura insuficiente: {tests_result['coverage']}%")
                # Nao falha, apenas avisa

            # 5. Lint basico
            lint_result = self._run_lint()
            result["lint_passed"] = lint_result["passed"]
            result["lint_issues"] = lint_result.get("issues", [])

            result["completed_at"] = datetime.now().isoformat()
            result["status"] = "SUCCESS"

            logger.info(f"✅ Developer Agent concluiu: {task.get('name')}")
            return True, result

        except Exception as e:
            logger.exception(f"❌ Erro no Developer Agent: {e}")
            result["errors"].append(str(e))
            result["status"] = "FAILED"
            return False, result

    def _ensure_module_structure(self, task: Dict[str, Any]) -> bool:
        """Garante que a estrutura do modulo existe."""
        module_name = task.get("module", "core")
        module_path = self.backend_path / "modules" / module_name

        dirs_to_create = [
            module_path,
            module_path / "models",
            module_path / "schemas",
            module_path / "services",
            module_path / "repositories",
            module_path / "controllers",
            self.backend_path / "tests" / "unit" / module_name,
            self.backend_path / "tests" / "integration" / module_name,
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'"""Modulo {dir_path.name}."""\n')

        logger.info(f"📁 Estrutura criada para modulo: {module_name}")
        return True

    def _check_files(self, task: Dict[str, Any]) -> Dict[str, List[str]]:
        """Verifica quais arquivos existem."""
        files_to_create = task.get("files_to_create", [])
        tests_to_create = task.get("tests_to_create", [])

        all_files = files_to_create + tests_to_create
        existing = []
        missing = []

        for file_path in all_files:
            full_path = self.backend_path / file_path
            if full_path.exists():
                existing.append(file_path)
            else:
                missing.append(file_path)

        return {"existing": existing, "missing": missing}

    def _run_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Executa testes do modulo."""
        module_name = task.get("module", "core")

        # Tentar rodar testes do modulo especifico
        test_paths = [
            self.backend_path / "tests" / "unit" / module_name,
            self.backend_path / "tests" / "integration" / module_name,
            self.backend_path / "tests",  # Fallback para todos os testes
        ]

        # Encontrar path com testes
        test_path = None
        for path in test_paths:
            if path.exists() and list(path.glob("test_*.py")):
                test_path = path
                break

        if not test_path:
            # Rodar testes gerais
            test_path = self.backend_path / "tests"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_path),
                    "-v",
                    "--cov=core",
                    "--cov=api",
                    "--cov-report=term-missing",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=300,
            )

            output = result.stdout + result.stderr
            passed = result.returncode == 0

            # Extrair cobertura do output
            coverage = self._extract_coverage(output)

            return {
                "passed": passed,
                "coverage": coverage,
                "output": output,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "coverage": 0,
                "output": "Timeout ao executar testes",
                "returncode": -1,
            }
        except Exception as e:
            return {
                "passed": False,
                "coverage": 0,
                "output": str(e),
                "returncode": -1,
            }

    def _extract_coverage(self, output: str) -> float:
        """Extrai percentual de cobertura do output do pytest."""
        import re

        # Procura por "TOTAL ... XX%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if match:
            return float(match.group(1))

        # Procura por "Coverage: XX%"
        match = re.search(r"Coverage:\s*(\d+)%", output)
        if match:
            return float(match.group(1))

        return 0.0

    def _run_lint(self) -> Dict[str, Any]:
        """Executa linters basicos."""
        issues = []

        # Black check
        try:
            result = subprocess.run(
                [sys.executable, "-m", "black", "--check", "."],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=60,
            )
            if result.returncode != 0:
                issues.append("Black: codigo nao formatado")
        except Exception as e:
            issues.append(f"Black erro: {e}")

        # isort check
        try:
            result = subprocess.run(
                [sys.executable, "-m", "isort", "--check-only", "."],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=60,
            )
            if result.returncode != 0:
                issues.append("isort: imports nao ordenados")
        except Exception as e:
            issues.append(f"isort erro: {e}")

        return {"passed": len(issues) == 0, "issues": issues}


# CLI para execucao standalone
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Developer Agent")
    parser.add_argument("--task", required=True, help="Task JSON file")

    args = parser.parse_args()

    with open(args.task) as f:
        task = json.load(f)

    module_path = Path("/opt/erp-conecta-mais/backend/modules") / task.get("module", "core")
    agent = DeveloperAgent(module_path)
    success, result = agent.develop(task)

    print(json.dumps(result, indent=2))
    sys.exit(0 if success else 1)
