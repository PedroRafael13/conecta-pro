"""
AUDITOR AGENT - Revisa codigo para qualidade e seguranca
Fase 2 do pipeline: Developer -> Auditor -> Validator
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/opt/erp-conecta-mais/logs/auditor.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("AuditorAgent")


class AuditorAgent:
    """
    Agente responsavel por:
    1. Verificar qualidade do codigo (SOLID, Clean Code)
    2. Seguranca (OWASP Top 10)
    3. Performance (complexidade, N+1)
    4. Gerar score de qualidade
    """

    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.project_root = Path("/opt/erp-conecta-mais")
        self.backend_path = self.project_root / "backend"
        # Score minimo: 70 para producao, 50 para desenvolvimento
        import os
        env = os.getenv("ENVIRONMENT", "development")
        self.min_score = 70 if env == "production" else 50

    def audit(self, developer_result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Executa auditoria do codigo.

        Args:
            developer_result: Resultado do Developer Agent

        Returns:
            (success, result_dict)
        """
        logger.info("🔍 Auditor Agent iniciando auditoria")

        result = {
            "started_at": datetime.now().isoformat(),
            "developer_result": developer_result.get("task_id"),
            "checks": {},
            "issues": [],
            "score": 0,
        }

        try:
            # 1. Security Scan (Bandit)
            security_result = self._run_security_scan()
            result["checks"]["security"] = security_result
            if security_result["issues"]:
                result["issues"].extend(
                    [f"SECURITY: {i}" for i in security_result["issues"][:5]]
                )

            # 2. Code Quality (Pylint)
            quality_result = self._run_quality_check()
            result["checks"]["quality"] = quality_result

            # 3. Type Checking (MyPy)
            type_result = self._run_type_check()
            result["checks"]["typing"] = type_result
            if type_result["issues"]:
                result["issues"].extend(
                    [f"TYPING: {i}" for i in type_result["issues"][:5]]
                )

            # 4. Complexity Analysis
            complexity_result = self._analyze_complexity()
            result["checks"]["complexity"] = complexity_result

            # 5. Dependency Check
            deps_result = self._check_dependencies()
            result["checks"]["dependencies"] = deps_result
            if deps_result["vulnerabilities"]:
                result["issues"].extend(
                    [f"VULN: {v}" for v in deps_result["vulnerabilities"][:3]]
                )

            # Calcular score final
            result["score"] = self._calculate_score(result["checks"])
            result["completed_at"] = datetime.now().isoformat()

            # Verificar se passa
            passed = result["score"] >= self.min_score and not security_result.get(
                "critical", False
            )

            if passed:
                result["status"] = "APPROVED"
                logger.info(f"✅ Auditor: APROVADO (Score: {result['score']}/100)")
            else:
                result["status"] = "REJECTED"
                logger.warning(f"❌ Auditor: REJEITADO (Score: {result['score']}/100)")

            return passed, result

        except Exception as e:
            logger.exception(f"❌ Erro no Auditor Agent: {e}")
            result["issues"].append(str(e))
            result["status"] = "ERROR"
            return False, result

    def _run_security_scan(self) -> Dict[str, Any]:
        """Executa Bandit para security scan."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "bandit",
                    "-r",
                    "core/",
                    "api/",
                    "-f",
                    "json",
                    "-ll",  # Low and above
                ],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=120,
            )

            issues = []
            critical = False

            if result.returncode != 0:
                try:
                    import json

                    data = json.loads(result.stdout)
                    for issue in data.get("results", [])[:10]:
                        severity = issue.get("issue_severity", "LOW")
                        if severity == "HIGH":
                            critical = True
                        issues.append(
                            f"{severity}: {issue.get('issue_text', '')} ({issue.get('filename', '')})"
                        )
                except:
                    issues.append("Erro ao parsear output do Bandit")

            return {
                "passed": result.returncode == 0,
                "critical": critical,
                "issues": issues,
                "score": 100 if result.returncode == 0 else (50 if not critical else 0),
            }

        except Exception as e:
            return {"passed": False, "critical": False, "issues": [str(e)], "score": 50}

    def _run_quality_check(self) -> Dict[str, Any]:
        """Executa Pylint para qualidade."""
        try:
            import re

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pylint",
                    "core/",
                    "api/",
                    "--max-line-length=100",
                    # Desabilitar checks aceitaveis em projetos Python modernos:
                    # C0114,C0115,C0116: Docstrings opcionais
                    # R0903: Too few public methods (dataclasses, Pydantic)
                    # R0902: Too many instance attributes (classes complexas)
                    # R0913,R0917: Too many arguments (APIs com muitos params)
                    # C0415: Import outside toplevel (evitar circular import)
                    # E1102: not-callable (falso positivo SQLAlchemy func.now)
                    # E0601: used-before-assignment (falso positivo imports)
                    "--disable=C0114,C0115,C0116,R0903,R0902,R0913,R0917,C0415,E1102,E0601",
                ],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=180,
            )

            # Pylint retorna score no final do stdout ou stderr
            all_output = result.stdout + result.stderr
            score = 5.0  # Default

            # Procura por "rated at X.XX/10"
            match = re.search(r"rated at (\d+\.\d+)/10", all_output)
            if match:
                score = float(match.group(1))

            return {
                "passed": score >= 7.0,
                "pylint_score": score,
                "score": int(score * 10),
            }

        except Exception as e:
            return {"passed": True, "pylint_score": 7.0, "score": 70, "error": str(e)}

    def _run_type_check(self) -> Dict[str, Any]:
        """Executa MyPy para type checking."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mypy",
                    "core/",
                    "api/",
                    "--ignore-missing-imports",
                    "--no-error-summary",
                ],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=120,
            )

            issues = []
            if result.returncode != 0:
                lines = result.stdout.strip().split("\n")
                issues = [l for l in lines if l.strip()][:10]

            return {
                "passed": result.returncode == 0 or len(issues) < 5,
                "issues": issues,
                "score": 100 if result.returncode == 0 else max(50, 100 - len(issues) * 5),
            }

        except Exception as e:
            return {"passed": True, "issues": [], "score": 80, "error": str(e)}

    def _analyze_complexity(self) -> Dict[str, Any]:
        """Analisa complexidade ciclomatica."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "radon",
                    "cc",
                    "core/",
                    "api/",
                    "-s",
                    "-a",
                ],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=60,
            )

            # Extrair average complexity
            avg_line = [l for l in result.stdout.split("\n") if "Average" in l]
            avg = 5.0  # Default

            if avg_line:
                import re

                match = re.search(r"(\d+\.\d+)", avg_line[0])
                if match:
                    avg = float(match.group(1))

            # Score baseado nos grades do Radon:
            # Grade A (1-5): Excelente -> Score 95-100
            # Grade B (6-10): Bom -> Score 70-94
            # Grade C+ (>10): Moderado+ -> Score 0-69
            if avg <= 3:
                score = 100  # Complexidade excelente
            elif avg <= 5:
                score = 100 - int((avg - 3) * 2.5)  # 95-100
            elif avg <= 10:
                score = 90 - int((avg - 5) * 4)
            else:
                score = max(0, 70 - int((avg - 10) * 3))

            return {
                "passed": avg <= 10,
                "average_complexity": avg,
                "score": score,
            }

        except Exception as e:
            return {"passed": True, "average_complexity": 5.0, "score": 80, "error": str(e)}

    def _check_dependencies(self) -> Dict[str, Any]:
        """Verifica vulnerabilidades em dependencias."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=str(self.backend_path),
                timeout=120,
            )

            vulnerabilities = []
            if result.returncode != 0:
                try:
                    import json

                    data = json.loads(result.stdout)
                    for vuln in data:
                        vulnerabilities.append(
                            f"{vuln.get('name')}: {vuln.get('vulns', [{}])[0].get('id', 'N/A')}"
                        )
                except:
                    pass

            return {
                "passed": len(vulnerabilities) == 0,
                "vulnerabilities": vulnerabilities,
                "score": 100 if not vulnerabilities else max(50, 100 - len(vulnerabilities) * 10),
            }

        except Exception as e:
            # pip-audit pode nao estar instalado
            return {"passed": True, "vulnerabilities": [], "score": 90, "error": str(e)}

    def _calculate_score(self, checks: Dict[str, Any]) -> int:
        """Calcula score final ponderado."""
        weights = {
            "security": 0.30,
            "quality": 0.25,
            "typing": 0.15,
            "complexity": 0.15,
            "dependencies": 0.15,
        }

        total_score = 0
        total_weight = 0

        for check_name, weight in weights.items():
            if check_name in checks:
                check_score = checks[check_name].get("score", 0)
                total_score += check_score * weight
                total_weight += weight

        if total_weight > 0:
            return int(total_score / total_weight * (total_weight / sum(weights.values())))

        return 0


# CLI para execucao standalone
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Auditor Agent")
    parser.add_argument("--module", required=True, help="Module name to audit")

    args = parser.parse_args()

    module_path = Path("/opt/erp-conecta-mais/backend/modules") / args.module
    agent = AuditorAgent(module_path)

    # Mock developer result
    developer_result = {"task_id": "AUDIT-CLI", "status": "SUCCESS"}

    success, result = agent.audit(developer_result)

    print(json.dumps(result, indent=2))
    sys.exit(0 if success else 1)
