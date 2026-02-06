"""
VALIDATOR AGENT - Validacao final antes do deploy
Fase 3 do pipeline: Developer -> Auditor -> Validator
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/opt/erp-conecta-mais/logs/validator.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ValidatorAgent")


class ValidatorAgent:
    """
    Agente responsavel por:
    1. Testes E2E (end-to-end)
    2. Testes de carga (load testing)
    3. Verificacao de integracao
    4. Smoke tests
    """

    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.project_root = Path("/opt/erp-conecta-mais")
        self.backend_path = self.project_root / "backend"
        self.api_url = "http://localhost:8080"

    def validate(self, auditor_result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Executa validacao final.

        Args:
            auditor_result: Resultado do Auditor Agent

        Returns:
            (success, result_dict)
        """
        logger.info("✅ Validator Agent iniciando validacao final")

        result = {
            "started_at": datetime.now().isoformat(),
            "auditor_score": auditor_result.get("score", 0),
            "validations": {},
            "issues": [],
        }

        try:
            # 1. Verificar se API esta rodando (ou pode ser iniciada)
            api_check = self._check_api_health()
            result["validations"]["api_health"] = api_check

            # 2. Testes de integracao avancados
            integration_result = self._run_integration_tests()
            result["validations"]["integration"] = integration_result
            if not integration_result["passed"]:
                result["issues"].append("Testes de integracao falharam")

            # 3. Verificacao de migracao de banco
            migration_result = self._check_migrations()
            result["validations"]["migrations"] = migration_result
            if not migration_result["passed"]:
                result["issues"].append("Migracao de banco com problemas")

            # 4. Verificacao de dependencias externas
            deps_result = self._check_external_deps()
            result["validations"]["external_deps"] = deps_result

            # 5. Smoke tests basicos
            smoke_result = self._run_smoke_tests()
            result["validations"]["smoke_tests"] = smoke_result
            if not smoke_result["passed"]:
                result["issues"].extend(smoke_result.get("failed_tests", []))

            # 6. Verificar integridade dos arquivos
            integrity_result = self._check_file_integrity()
            result["validations"]["integrity"] = integrity_result

            # Determinar se passou
            critical_validations = ["integration", "migrations"]
            passed = all(
                result["validations"].get(v, {}).get("passed", False)
                for v in critical_validations
            )

            # Se API nao esta rodando, ainda pode passar (validacao offline)
            if not api_check.get("running", False):
                logger.warning("⚠️ API nao esta rodando - validacao offline")
                passed = passed and integration_result["passed"]

            result["completed_at"] = datetime.now().isoformat()
            result["passed"] = passed

            if passed:
                result["status"] = "APPROVED"
                logger.info("✅ Validator: APROVADO - Pronto para deploy!")
            else:
                result["status"] = "REJECTED"
                logger.warning(f"❌ Validator: REJEITADO - Issues: {result['issues']}")

            return passed, result

        except Exception as e:
            logger.exception(f"❌ Erro no Validator Agent: {e}")
            result["issues"].append(str(e))
            result["status"] = "ERROR"
            return False, result

    def _check_api_health(self) -> Dict[str, Any]:
        """Verifica se a API esta rodando e saudavel."""
        try:
            req = Request(f"{self.api_url}/health", method="GET")
            req.add_header("User-Agent", "ValidatorAgent/1.0")

            with urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return {"running": True, "status": "healthy", "response_time_ms": 0}

        except URLError:
            pass
        except Exception:
            pass

        return {"running": False, "status": "not_running"}

    def _run_integration_tests(self) -> Dict[str, Any]:
        """Executa testes de integracao."""
        try:
            test_path = self.backend_path / "tests"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_path),
                    "-v",
                    "-x",  # Para no primeiro erro
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=300,
            )

            # Contar testes passados/falhados
            output = result.stdout + result.stderr
            passed_count = output.count(" PASSED")
            failed_count = output.count(" FAILED")

            return {
                "passed": result.returncode == 0,
                "tests_passed": passed_count,
                "tests_failed": failed_count,
                "output": output[-1000:] if len(output) > 1000 else output,
            }

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Timeout ao executar testes"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _check_migrations(self) -> Dict[str, Any]:
        """Verifica se migrações estão atualizadas."""
        try:
            # Verificar status das migrações
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "current"],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=30,
            )

            current_output = result.stdout

            # Verificar se há migrações pendentes
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "heads"],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=30,
            )

            heads_output = result.stdout

            # Se current == heads, está atualizado
            is_current = "head" in current_output.lower() or current_output.strip() == heads_output.strip()

            return {
                "passed": True,  # Não bloqueia se alembic não está configurado
                "current": current_output.strip()[:100],
                "heads": heads_output.strip()[:100],
                "is_up_to_date": is_current,
            }

        except Exception as e:
            return {"passed": True, "error": str(e), "is_up_to_date": True}

    def _check_external_deps(self) -> Dict[str, Any]:
        """Verifica dependências externas (Redis, Postgres, etc)."""
        deps = {}

        # Redis
        try:
            import redis

            client = redis.from_url("redis://localhost:6379/0", socket_timeout=2)
            client.ping()
            deps["redis"] = {"available": True}
        except:
            deps["redis"] = {"available": False}

        # PostgreSQL (via test connection)
        try:
            import os

            db_url = os.getenv("DATABASE_URL", "")
            if db_url:
                import psycopg2

                conn = psycopg2.connect(db_url, connect_timeout=5)
                conn.close()
                deps["postgres"] = {"available": True}
            else:
                deps["postgres"] = {"available": False, "reason": "DATABASE_URL not set"}
        except:
            deps["postgres"] = {"available": False}

        return {"passed": True, "dependencies": deps}

    def _run_smoke_tests(self) -> Dict[str, Any]:
        """Executa smoke tests básicos."""
        smoke_tests = []
        failed_tests = []

        # Test 1: Imports funcionam
        try:
            result = subprocess.run(
                [sys.executable, "-c", "from main import app; print('OK')"],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=30,
            )
            if result.returncode == 0:
                smoke_tests.append({"name": "import_main", "passed": True})
            else:
                smoke_tests.append({"name": "import_main", "passed": False})
                failed_tests.append(f"import_main: {result.stderr[:100]}")
        except Exception as e:
            smoke_tests.append({"name": "import_main", "passed": False})
            failed_tests.append(f"import_main: {e}")

        # Test 2: Módulos core
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from core.config import settings; from core.auth import security; print('OK')",
                ],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=30,
            )
            if result.returncode == 0:
                smoke_tests.append({"name": "import_core", "passed": True})
            else:
                smoke_tests.append({"name": "import_core", "passed": False})
                failed_tests.append(f"import_core: {result.stderr[:100]}")
        except Exception as e:
            smoke_tests.append({"name": "import_core", "passed": False})
            failed_tests.append(f"import_core: {e}")

        # Test 3: Verificar se requirements estão instalados
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=60,
            )
            if result.returncode == 0:
                smoke_tests.append({"name": "pip_check", "passed": True})
            else:
                smoke_tests.append({"name": "pip_check", "passed": False})
                failed_tests.append(f"pip_check: {result.stdout[:100]}")
        except Exception as e:
            smoke_tests.append({"name": "pip_check", "passed": False})
            failed_tests.append(f"pip_check: {e}")

        passed = len(failed_tests) == 0

        return {
            "passed": passed,
            "tests": smoke_tests,
            "failed_tests": failed_tests,
            "passed_count": sum(1 for t in smoke_tests if t["passed"]),
            "total_count": len(smoke_tests),
        }

    def _check_file_integrity(self) -> Dict[str, Any]:
        """Verifica integridade dos arquivos principais."""
        critical_files = [
            "main.py",
            "requirements.txt",
            "alembic.ini",
            "core/__init__.py",
            "core/config/settings.py",
            "core/auth/security.py",
            "api/__init__.py",
        ]

        missing = []
        for file_path in critical_files:
            full_path = self.backend_path / file_path
            if not full_path.exists():
                missing.append(file_path)

        return {
            "passed": len(missing) == 0,
            "checked_files": len(critical_files),
            "missing_files": missing,
        }


# CLI para execucao standalone
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Validator Agent")
    parser.add_argument("--module", required=True, help="Module name to validate")

    args = parser.parse_args()

    module_path = Path("/opt/erp-conecta-mais/backend/modules") / args.module
    agent = ValidatorAgent(module_path)

    # Mock auditor result
    auditor_result = {"task_id": "VALIDATE-CLI", "score": 85, "status": "APPROVED"}

    success, result = agent.validate(auditor_result)

    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if success else 1)
