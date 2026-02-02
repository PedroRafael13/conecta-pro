#!/usr/bin/env python3
"""
OpenClaw Runner - Orquestrador de qualidade continua do Conecta PRO.

Executa ciclos continuos de validacao:
- Testes unitarios (backend + frontend)
- Linting e formatacao
- Security scans
- Coverage analysis
- Health checks
- Performance checks
- Geracao de relatorio consolidado

Uso:
    python runner.py                    # Ciclo completo
    python runner.py --only tests       # Apenas testes
    python runner.py --only security    # Apenas seguranca
    python runner.py --only health      # Apenas health check
    python runner.py --only lint        # Apenas linting
    python runner.py --only coverage    # Apenas cobertura
    python runner.py --only performance # Apenas performance
    python runner.py --report           # Gerar relatorio sem executar
    python runner.py --daemon           # Modo daemon (ciclos continuos)
    python runner.py --interval 3600    # Intervalo entre ciclos (segundos)
"""

import argparse
import asyncio
import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Tuple, Callable, Dict, Any

# OpenClaw parallel execution
try:
    from checks.parallel_executor import ParallelExecutor
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False
    logging.warning("ParallelExecutor not available, falling back to sequential execution")


# ============================================================================
# Constantes e Paths
# ============================================================================

PROJECT_ROOT = Path("/opt/conecta-pro")
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
REPORTS_DIR = PROJECT_ROOT / "reports" / "openclaw"
LOGS_DIR = PROJECT_ROOT / "logs" / "openclaw"
CONFIG_PATH = Path(__file__).parent / "config.json"

VERSION = "1.0.0"
BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║  OpenClaw Runner v{VERSION} - Conecta PRO Quality Monitor       ║
║  Orquestrador de qualidade continua                         ║
╚══════════════════════════════════════════════════════════════╝
"""


# ============================================================================
# Enums e Dataclasses
# ============================================================================

class CheckStatus(Enum):
    """Status possivel de cada verificacao."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class CheckResult:
    """Resultado de uma verificacao individual."""
    name: str
    status: CheckStatus
    duration_seconds: float
    message: str
    details: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CycleReport:
    """Relatorio completo de um ciclo de verificacao."""
    cycle_id: str
    started_at: str
    finished_at: str = ""
    duration_seconds: float = 0.0
    overall_status: CheckStatus = CheckStatus.PASS
    checks: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def add_check(self, result: CheckResult):
        """Adiciona resultado de check ao relatorio e atualiza status geral."""
        # Converter para dict e garantir que status e string
        check_dict = asdict(result)
        if isinstance(check_dict.get("status"), CheckStatus):
            check_dict["status"] = check_dict["status"].value
        self.checks.append(check_dict)
        if result.status == CheckStatus.FAIL:
            self.overall_status = CheckStatus.FAIL
        elif result.status == CheckStatus.WARN and self.overall_status != CheckStatus.FAIL:
            self.overall_status = CheckStatus.WARN
        elif result.status == CheckStatus.ERROR and self.overall_status not in (
            CheckStatus.FAIL, CheckStatus.WARN
        ):
            self.overall_status = CheckStatus.ERROR

    def compute_summary(self):
        """Calcula resumo estatistico do ciclo e health score."""
        status_counts = {"pass": 0, "fail": 0, "warn": 0, "skip": 0, "error": 0}
        for check in self.checks:
            status_val = check.get("status", "error")
            # Garantir que e string, nao Enum
            if isinstance(status_val, CheckStatus):
                status_val = status_val.value
            if status_val in status_counts:
                status_counts[status_val] += 1

        # Calcular health score (0-100)
        health_score = self._calculate_health_score(status_counts)

        self.summary = {
            "total_checks": len(self.checks),
            "status_counts": status_counts,
            "overall_status": self.overall_status.value,
            "health_score": health_score,
        }

    def _calculate_health_score(self, status_counts: dict) -> int:
        """
        Calcula health score 0-100 baseado nos resultados.

        Pontuação:
        - Começa com 100
        - -15 por cada fail
        - -10 por cada error
        - -5 por cada warn
        - -2 por cada skip

        Returns:
            Score entre 0 e 100
        """
        score = 100
        score -= status_counts.get("fail", 0) * 15
        score -= status_counts.get("error", 0) * 10
        score -= status_counts.get("warn", 0) * 5
        score -= status_counts.get("skip", 0) * 2

        # Garantir limites
        return max(0, min(100, score))


# ============================================================================
# Configuracao
# ============================================================================

def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """Carrega configuracao do arquivo JSON."""
    default_config = {
        "project_root": str(PROJECT_ROOT),
        "cycle_interval_seconds": 3600,
        "checks": {
            "backend_tests": {"enabled": True, "timeout": 120},
            "frontend_tests": {"enabled": True, "timeout": 120},
            "backend_lint": {"enabled": True, "timeout": 60},
            "frontend_lint": {"enabled": True, "timeout": 60},
            "security_bandit": {"enabled": True, "timeout": 60},
            "coverage": {"enabled": True, "timeout": 180, "min_coverage": 60},
            "health": {"enabled": True, "timeout": 30},
            "docker_status": {"enabled": True, "timeout": 15},
            "disk_space": {"enabled": True, "timeout": 5, "min_free_gb": 5},
            "lighthouse": {"enabled": False, "timeout": 120},
        },
        "notifications": {
            "discord_webhook": "",
            "slack_webhook": "",
            "notify_on": ["fail", "error"],
        },
        "retention": {
            "reports_days": 30,
            "logs_days": 14,
        },
    }

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            # Merge: user_config sobrescreve defaults
            for key, value in user_config.items():
                if isinstance(value, dict) and key in default_config:
                    default_config[key].update(value)
                else:
                    default_config[key] = value
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] Erro ao carregar config {config_path}: {e}. Usando defaults.")

    return default_config


# ============================================================================
# Classe Principal
# ============================================================================

class OpenClawRunner:
    """Orquestrador principal do OpenClaw."""

    def __init__(self, project_root: Path = PROJECT_ROOT, config: Optional[dict] = None):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.reports_dir = self.project_root / "reports" / "openclaw"
        self.logs_dir = self.project_root / "logs" / "openclaw"
        self.config = config or load_config()
        self.logger = self._setup_logging()
        self._ensure_dirs()
        self._running = True

        # Registrar handler para parada limpa
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handler para sinais de parada."""
        self.logger.info(f"Sinal {signum} recebido. Encerrando OpenClaw...")
        self._running = False

    def _setup_logging(self) -> logging.Logger:
        """Configura logging com saida em arquivo e console."""
        logger = logging.getLogger("openclaw")
        logger.setLevel(logging.DEBUG)

        # Limpar handlers existentes para evitar duplicacao
        logger.handlers.clear()

        # Formato
        fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(fmt)
        logger.addHandler(console_handler)

        # File handler
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            log_file = self.logs_dir / f"runner_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(fmt)
            logger.addHandler(file_handler)
        except OSError as e:
            logger.warning(f"Nao foi possivel criar log em arquivo: {e}")

        return logger

    def _ensure_dirs(self):
        """Garante que diretorios necessarios existem."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _is_check_enabled(self, check_name: str) -> bool:
        """Verifica se um check esta habilitado na configuracao."""
        checks_config = self.config.get("checks", {})
        check_cfg = checks_config.get(check_name, {})
        return check_cfg.get("enabled", True)

    def _get_check_timeout(self, check_name: str, default: int = 120) -> int:
        """Retorna timeout configurado para um check."""
        checks_config = self.config.get("checks", {})
        check_cfg = checks_config.get(check_name, {})
        return check_cfg.get("timeout", default)

    def _run_command(
        self,
        cmd: str,
        cwd: Optional[Path] = None,
        timeout: int = 300,
    ) -> Tuple[int, str, str, float]:
        """
        Executa comando shell e retorna (returncode, stdout, stderr, duration_seconds).
        Trata timeouts e erros de execucao.
        """
        start = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(cwd) if cwd else str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            duration = time.monotonic() - start
            return result.returncode, result.stdout, result.stderr, duration
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start
            return -1, "", f"Timeout apos {timeout}s", duration
        except FileNotFoundError as e:
            duration = time.monotonic() - start
            return -2, "", f"Comando nao encontrado: {e}", duration
        except OSError as e:
            duration = time.monotonic() - start
            return -3, "", f"Erro de SO: {e}", duration

    # ========================================================================
    # CHECKS - Testes
    # ========================================================================

    def check_backend_tests(self) -> CheckResult:
        """Roda pytest no backend e analisa resultados."""
        name = "Backend Tests (pytest)"

        if not self._is_check_enabled("backend_tests"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        if not (self.backend_dir / "tests").exists():
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Diretorio de testes nao encontrado"
            )

        timeout = self._get_check_timeout("backend_tests", 120)
        cmd = "python3 -m pytest tests/ -v --tb=short --no-header -q 2>&1"
        code, stdout, stderr, duration = self._run_command(cmd, cwd=self.backend_dir, timeout=timeout)

        output = stdout + stderr
        details = {"returncode": code, "output_tail": output[-2000:] if len(output) > 2000 else output}

        if code == -1:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Timeout apos {timeout}s", details=details
            )

        # Tentar parsear resultados do pytest
        passed = failed = errors = 0
        for line in output.splitlines():
            line_lower = line.lower().strip()
            if "passed" in line_lower or "failed" in line_lower or "error" in line_lower:
                # Linha de resumo do pytest: "X passed, Y failed, Z errors"
                import re
                p = re.search(r"(\d+)\s+passed", line_lower)
                f = re.search(r"(\d+)\s+failed", line_lower)
                e = re.search(r"(\d+)\s+error", line_lower)
                if p:
                    passed = int(p.group(1))
                if f:
                    failed = int(f.group(1))
                if e:
                    errors = int(e.group(1))

        details["passed"] = passed
        details["failed"] = failed
        details["errors"] = errors

        if code == 0:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message=f"{passed} testes passaram", details=details
            )
        elif code == 5:
            # pytest retorna 5 quando nenhum teste e coletado
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message="Nenhum teste coletado pelo pytest", details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.FAIL, duration_seconds=duration,
                message=f"{failed} falhas, {errors} erros de {passed + failed + errors} testes",
                details=details
            )

    def check_frontend_tests(self) -> CheckResult:
        """Roda vitest no frontend e analisa resultados."""
        name = "Frontend Tests (vitest)"

        if not self._is_check_enabled("frontend_tests"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        if not self.frontend_dir.exists():
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Diretorio frontend nao encontrado"
            )

        # Verificar se vitest esta disponivel
        package_json = self.frontend_dir / "package.json"
        has_vitest = False
        if package_json.exists():
            try:
                with open(package_json, "r") as f:
                    pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                has_vitest = "vitest" in deps
            except (json.JSONDecodeError, IOError):
                pass

        if not has_vitest:
            # Tentar jest como fallback
            cmd = "npx jest --passWithNoTests --json 2>&1"
        else:
            cmd = "npx vitest run --reporter=json 2>&1"

        timeout = self._get_check_timeout("frontend_tests", 120)
        code, stdout, stderr, duration = self._run_command(cmd, cwd=self.frontend_dir, timeout=timeout)

        output = stdout + stderr
        details = {"returncode": code, "output_tail": output[-2000:] if len(output) > 2000 else output}

        if code == -1:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Timeout apos {timeout}s", details=details
            )
        if code == -2:
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=duration,
                message="Node/npx nao encontrado", details=details
            )

        # Tentar parsear JSON do vitest/jest
        test_passed = 0
        test_failed = 0
        try:
            # vitest/jest output pode ter texto antes do JSON
            json_start = output.find("{")
            if json_start >= 0:
                json_str = output[json_start:]
                # Encontrar o fim do JSON de nivel superior
                brace_count = 0
                json_end = 0
                for i, c in enumerate(json_str):
                    if c == "{":
                        brace_count += 1
                    elif c == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                if json_end > 0:
                    parsed = json.loads(json_str[:json_end])
                    if "numPassedTests" in parsed:
                        test_passed = parsed.get("numPassedTests", 0)
                        test_failed = parsed.get("numFailedTests", 0)
                    elif "testResults" in parsed:
                        for suite in parsed.get("testResults", []):
                            test_passed += suite.get("numPassingTests", 0)
                            test_failed += suite.get("numFailingTests", 0)
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

        details["passed"] = test_passed
        details["failed"] = test_failed

        if code == 0:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message=f"{test_passed} testes passaram", details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.FAIL, duration_seconds=duration,
                message=f"{test_failed} falhas de {test_passed + test_failed} testes",
                details=details
            )

    # ========================================================================
    # CHECKS - Linting
    # ========================================================================

    def check_backend_lint(self) -> CheckResult:
        """Roda ruff check no backend."""
        name = "Backend Lint (ruff)"

        if not self._is_check_enabled("backend_lint"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        timeout = self._get_check_timeout("backend_lint", 60)

        # Verificar se ruff esta instalado
        ruff_check = "python3 -m ruff --version 2>&1"
        rc, _, _, _ = self._run_command(ruff_check, timeout=10)

        if rc != 0:
            # Tentar flake8 como fallback
            cmd = "python3 -m flake8 modules/ core/ api/ --max-line-length=120 --count --statistics 2>&1"
        else:
            ruff_toml = self.backend_dir / "ruff.toml"
            pyproject = self.backend_dir / "pyproject.toml"
            if ruff_toml.exists():
                cmd = f"python3 -m ruff check . --config ruff.toml 2>&1"
            elif pyproject.exists():
                cmd = f"python3 -m ruff check . 2>&1"
            else:
                cmd = "python3 -m ruff check . --line-length=120 2>&1"

        code, stdout, stderr, duration = self._run_command(cmd, cwd=self.backend_dir, timeout=timeout)
        output = stdout + stderr

        # Contar problemas
        issue_count = 0
        for line in output.splitlines():
            stripped = line.strip()
            if stripped and ":" in stripped and not stripped.startswith(("Found", "All", "error", "warning")):
                issue_count += 1

        # Tentar pegar contagem da linha de resumo do ruff
        import re
        found_match = re.search(r"Found (\d+)", output)
        if found_match:
            issue_count = int(found_match.group(1))

        details = {
            "returncode": code,
            "issues_found": issue_count,
            "output_tail": output[-2000:] if len(output) > 2000 else output,
        }

        if code == -1:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Timeout apos {timeout}s", details=details
            )
        if code == 0:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message="Sem problemas de linting", details=details
            )
        else:
            severity = CheckStatus.FAIL if issue_count > 20 else CheckStatus.WARN
            return CheckResult(
                name=name, status=severity, duration_seconds=duration,
                message=f"{issue_count} problemas encontrados", details=details
            )

    def check_frontend_lint(self) -> CheckResult:
        """Roda eslint no frontend."""
        name = "Frontend Lint (eslint)"

        if not self._is_check_enabled("frontend_lint"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        if not self.frontend_dir.exists():
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Diretorio frontend nao encontrado"
            )

        timeout = self._get_check_timeout("frontend_lint", 60)
        cmd = "npx eslint . --max-warnings=0 --format=json 2>&1"
        code, stdout, stderr, duration = self._run_command(cmd, cwd=self.frontend_dir, timeout=timeout)

        output = stdout + stderr
        error_count = 0
        warning_count = 0

        # Tentar parsear JSON do eslint
        try:
            json_start = output.find("[")
            if json_start >= 0:
                parsed = json.loads(output[json_start:])
                for file_result in parsed:
                    error_count += file_result.get("errorCount", 0)
                    warning_count += file_result.get("warningCount", 0)
        except (json.JSONDecodeError, TypeError, KeyError):
            # Contagem heuristica
            for line in output.splitlines():
                if "error" in line.lower():
                    error_count += 1
                elif "warning" in line.lower():
                    warning_count += 1

        details = {
            "returncode": code,
            "errors": error_count,
            "warnings": warning_count,
            "output_tail": output[-2000:] if len(output) > 2000 else output,
        }

        if code == -1:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Timeout apos {timeout}s", details=details
            )
        if code == -2:
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=duration,
                message="Node/npx nao encontrado", details=details
            )
        if code == 0:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message="Sem problemas de linting", details=details
            )
        else:
            severity = CheckStatus.FAIL if error_count > 0 else CheckStatus.WARN
            return CheckResult(
                name=name, status=severity, duration_seconds=duration,
                message=f"{error_count} erros, {warning_count} avisos", details=details
            )

    # ========================================================================
    # CHECKS - Seguranca
    # ========================================================================

    def check_security_bandit(self) -> CheckResult:
        """Roda bandit (analise de seguranca) no backend."""
        name = "Security Scan (bandit)"

        if not self._is_check_enabled("security_bandit"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        timeout = self._get_check_timeout("security_bandit", 60)

        # Verificar quais diretorios existem
        scan_dirs = []
        for d in ["modules", "core", "api", "application"]:
            if (self.backend_dir / d).exists():
                scan_dirs.append(d)

        if not scan_dirs:
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Nenhum diretorio de codigo encontrado para scan"
            )

        dirs_str = " ".join(scan_dirs)
        cmd = f"python3 -m bandit -r {dirs_str} -ll -f json 2>&1"
        code, stdout, stderr, duration = self._run_command(cmd, cwd=self.backend_dir, timeout=timeout)

        output = stdout + stderr
        high_issues = 0
        medium_issues = 0
        low_issues = 0

        # Parsear JSON do bandit
        try:
            json_start = output.find("{")
            if json_start >= 0:
                brace_count = 0
                json_end = 0
                for i, c in enumerate(output[json_start:]):
                    if c == "{":
                        brace_count += 1
                    elif c == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = json_start + i + 1
                            break
                if json_end > 0:
                    parsed = json.loads(output[json_start:json_end])
                    metrics = parsed.get("metrics", {}).get("_totals", {})
                    high_issues = metrics.get("SEVERITY.HIGH", 0) + metrics.get("CONFIDENCE.HIGH", 0)
                    medium_issues = metrics.get("SEVERITY.MEDIUM", 0)
                    low_issues = metrics.get("SEVERITY.LOW", 0)

                    results = parsed.get("results", [])
                    if results:
                        high_issues = sum(1 for r in results if r.get("issue_severity") == "HIGH")
                        medium_issues = sum(1 for r in results if r.get("issue_severity") == "MEDIUM")
                        low_issues = sum(1 for r in results if r.get("issue_severity") == "LOW")
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

        details = {
            "returncode": code,
            "high": high_issues,
            "medium": medium_issues,
            "low": low_issues,
            "output_tail": output[-2000:] if len(output) > 2000 else output,
        }

        if code == -1:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Timeout apos {timeout}s", details=details
            )
        if code == -2:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message="Bandit nao instalado. Execute: pip install bandit",
                details=details
            )

        if high_issues > 0:
            return CheckResult(
                name=name, status=CheckStatus.FAIL, duration_seconds=duration,
                message=f"{high_issues} problemas HIGH, {medium_issues} MEDIUM, {low_issues} LOW",
                details=details
            )
        elif medium_issues > 0:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message=f"{medium_issues} problemas MEDIUM, {low_issues} LOW", details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message=f"Nenhum problema critico. {low_issues} LOW", details=details
            )

    # ========================================================================
    # CHECKS - Cobertura
    # ========================================================================

    def check_coverage(self) -> CheckResult:
        """Verifica cobertura de codigo com pytest-cov."""
        name = "Code Coverage"

        if not self._is_check_enabled("coverage"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        min_coverage = self.config.get("checks", {}).get("coverage", {}).get("min_coverage", 60)
        timeout = self._get_check_timeout("coverage", 180)

        # Detectar diretorios de codigo para cobertura
        cov_dirs = []
        for d in ["modules", "core", "api", "application", "domains"]:
            if (self.backend_dir / d).exists():
                cov_dirs.append(f"--cov={d}")

        if not cov_dirs:
            cov_dirs = ["--cov=."]

        cov_str = " ".join(cov_dirs)
        cov_json_path = self.backend_dir / "coverage.json"
        cmd = (
            f"python3 -m pytest tests/ {cov_str} "
            f"--cov-report=json:{cov_json_path} "
            f"--cov-fail-under={min_coverage} -q --no-header 2>&1"
        )

        code, stdout, stderr, duration = self._run_command(cmd, cwd=self.backend_dir, timeout=timeout)
        output = stdout + stderr

        coverage_pct = 0.0
        details = {"returncode": code, "min_coverage": min_coverage}

        # Tentar ler coverage.json
        try:
            if cov_json_path.exists():
                with open(cov_json_path, "r") as f:
                    cov_data = json.load(f)
                totals = cov_data.get("totals", {})
                coverage_pct = totals.get("percent_covered", 0.0)
                details["coverage_percent"] = round(coverage_pct, 2)
                details["covered_lines"] = totals.get("covered_lines", 0)
                details["missing_lines"] = totals.get("missing_lines", 0)
                details["total_statements"] = totals.get("num_statements", 0)
        except (json.JSONDecodeError, IOError, KeyError):
            # Tentar parsear da saida do pytest
            import re
            match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
            if match:
                coverage_pct = float(match.group(1))
                details["coverage_percent"] = coverage_pct

        details["output_tail"] = output[-1500:] if len(output) > 1500 else output

        if code == -1:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Timeout apos {timeout}s", details=details
            )

        if coverage_pct >= min_coverage:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message=f"Cobertura: {coverage_pct:.1f}% (minimo: {min_coverage}%)",
                details=details
            )
        elif coverage_pct >= min_coverage * 0.8:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message=f"Cobertura baixa: {coverage_pct:.1f}% (minimo: {min_coverage}%)",
                details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.FAIL, duration_seconds=duration,
                message=f"Cobertura insuficiente: {coverage_pct:.1f}% (minimo: {min_coverage}%)",
                details=details
            )

    # ========================================================================
    # CHECKS - Health
    # ========================================================================

    def check_health(self) -> CheckResult:
        """Health check dos servicos (API, frontend, Redis, Postgres)."""
        name = "Health Check (servicos)"

        if not self._is_check_enabled("health"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        timeout = self._get_check_timeout("health", 30)
        start = time.monotonic()
        services_status = {}
        all_ok = True
        has_warn = False

        # Check 1: Backend API
        endpoints_to_check = [
            ("Backend API", "http://localhost:8080/health"),
            ("Backend API (alt)", "http://localhost:8000/health"),
        ]

        backend_ok = False
        for svc_name, url in endpoints_to_check:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    status_code = resp.getcode()
                    if status_code == 200:
                        services_status["backend_api"] = {"status": "ok", "url": url}
                        backend_ok = True
                        break
            except (urllib.error.URLError, urllib.error.HTTPError, OSError):
                continue

        if not backend_ok:
            services_status["backend_api"] = {"status": "down"}
            all_ok = False

        # Check 2: Frontend
        frontend_urls = [
            ("Frontend", "http://localhost:3000"),
            ("Frontend (alt)", "http://localhost:3001"),
        ]

        frontend_ok = False
        for svc_name, url in frontend_urls:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.getcode() in (200, 301, 302, 304):
                        services_status["frontend"] = {"status": "ok", "url": url}
                        frontend_ok = True
                        break
            except (urllib.error.URLError, urllib.error.HTTPError, OSError):
                continue

        if not frontend_ok:
            services_status["frontend"] = {"status": "down"}
            has_warn = True  # Frontend down e warning, nao fail critico

        # Check 3: Redis
        redis_cmd = "python3 -c \"import redis; r = redis.Redis(); r.ping(); print('ok')\" 2>&1"
        rc, out, _, _ = self._run_command(redis_cmd, timeout=10)
        if rc == 0 and "ok" in out.lower():
            services_status["redis"] = {"status": "ok"}
        else:
            services_status["redis"] = {"status": "down"}
            has_warn = True

        # Check 4: PostgreSQL
        pg_cmd = (
            "python3 -c \""
            "import subprocess; "
            "r = subprocess.run(['pg_isready', '-h', 'localhost'], capture_output=True, text=True, timeout=5); "
            "print('ok' if r.returncode == 0 else 'down')\" 2>&1"
        )
        rc, out, _, _ = self._run_command(pg_cmd, timeout=10)
        if rc == 0 and "ok" in out.lower():
            services_status["postgresql"] = {"status": "ok"}
        else:
            # Tentar via docker
            pg_docker_cmd = "docker exec conecta-pro-db-1 pg_isready 2>&1 || docker exec conecta-pro_db_1 pg_isready 2>&1"
            rc2, out2, _, _ = self._run_command(pg_docker_cmd, timeout=10)
            if rc2 == 0:
                services_status["postgresql"] = {"status": "ok", "via": "docker"}
            else:
                services_status["postgresql"] = {"status": "down"}
                all_ok = False

        duration = time.monotonic() - start

        # Contar servicos
        up_count = sum(1 for s in services_status.values() if s.get("status") == "ok")
        total_count = len(services_status)

        details = {"services": services_status, "up": up_count, "total": total_count}

        if all_ok and not has_warn:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message=f"Todos os {total_count} servicos ativos", details=details
            )
        elif all_ok and has_warn:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message=f"{up_count}/{total_count} servicos ativos (alguns secundarios indisponiveis)",
                details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.FAIL, duration_seconds=duration,
                message=f"Apenas {up_count}/{total_count} servicos ativos",
                details=details
            )

    def check_docker_status(self) -> CheckResult:
        """Verifica status dos containers Docker."""
        name = "Docker Status"

        if not self._is_check_enabled("docker_status"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        timeout = self._get_check_timeout("docker_status", 15)
        cmd = 'docker ps --format "{{.Names}}|{{.Status}}|{{.State}}" 2>&1'
        code, stdout, stderr, duration = self._run_command(cmd, timeout=timeout)

        output = stdout + stderr

        if code != 0:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Erro ao consultar Docker: {output[:200]}",
                details={"returncode": code, "output": output[:1000]}
            )

        containers = []
        running = 0
        unhealthy = 0
        total = 0

        for line in stdout.strip().splitlines():
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 3:
                cname = parts[0].strip()
                cstatus = parts[1].strip()
                cstate = parts[2].strip()
                containers.append({
                    "name": cname,
                    "status": cstatus,
                    "state": cstate,
                })
                total += 1
                if cstate.lower() == "running":
                    running += 1
                if "unhealthy" in cstatus.lower():
                    unhealthy += 1

        details = {"containers": containers, "running": running, "total": total, "unhealthy": unhealthy}

        if total == 0:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message="Nenhum container Docker em execucao", details=details
            )

        if unhealthy > 0:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message=f"{unhealthy} container(s) unhealthy de {total} total",
                details=details
            )

        if running == total:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message=f"Todos os {total} containers rodando", details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.FAIL, duration_seconds=duration,
                message=f"Apenas {running}/{total} containers rodando", details=details
            )

    def check_disk_space(self) -> CheckResult:
        """Verifica espaco em disco disponivel."""
        name = "Disk Space"

        if not self._is_check_enabled("disk_space"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        min_free_gb = self.config.get("checks", {}).get("disk_space", {}).get("min_free_gb", 5)
        start = time.monotonic()

        try:
            stat = shutil.disk_usage(str(self.project_root))
            total_gb = stat.total / (1024 ** 3)
            used_gb = stat.used / (1024 ** 3)
            free_gb = stat.free / (1024 ** 3)
            pct_used = (stat.used / stat.total) * 100
        except OSError as e:
            duration = time.monotonic() - start
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Erro ao verificar disco: {e}"
            )

        duration = time.monotonic() - start
        details = {
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "percent_used": round(pct_used, 1),
            "min_free_gb": min_free_gb,
        }

        if free_gb >= min_free_gb:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message=f"{free_gb:.1f}GB livres de {total_gb:.1f}GB ({pct_used:.0f}% usado)",
                details=details
            )
        elif free_gb >= min_free_gb * 0.5:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message=f"Espaco baixo: {free_gb:.1f}GB livres (minimo: {min_free_gb}GB)",
                details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.FAIL, duration_seconds=duration,
                message=f"Espaco critico: {free_gb:.1f}GB livres (minimo: {min_free_gb}GB)",
                details=details
            )

    # ========================================================================
    # CHECKS - Performance
    # ========================================================================

    def check_performance_lighthouse(self) -> CheckResult:
        """Roda Lighthouse CI se disponivel."""
        name = "Performance (Lighthouse)"

        if not self._is_check_enabled("lighthouse"):
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Check desabilitado na configuracao"
            )

        timeout = self._get_check_timeout("lighthouse", 120)

        # Verificar se lhci esta disponivel
        check_cmd = "npx lhci --version 2>&1"
        rc, _, _, _ = self._run_command(check_cmd, timeout=15)

        if rc != 0:
            return CheckResult(
                name=name, status=CheckStatus.SKIP, duration_seconds=0,
                message="Lighthouse CI nao instalado. Execute: npm install -g @lhci/cli"
            )

        # Verificar se lighthouserc existe
        lhrc = self.project_root / "lighthouserc.json"
        if lhrc.exists():
            cmd = "npx lhci autorun 2>&1"
        else:
            # Rodar manualmente contra localhost
            cmd = (
                "npx lhci collect --url=http://localhost:3000 "
                "--numberOfRuns=1 2>&1"
            )

        code, stdout, stderr, duration = self._run_command(cmd, cwd=self.project_root, timeout=timeout)
        output = stdout + stderr
        details = {"returncode": code, "output_tail": output[-2000:] if len(output) > 2000 else output}

        if code == -1:
            return CheckResult(
                name=name, status=CheckStatus.ERROR, duration_seconds=duration,
                message=f"Timeout apos {timeout}s", details=details
            )

        # Tentar extrair scores
        import re
        perf_match = re.search(r"Performance:\s*(\d+)", output)
        if perf_match:
            perf_score = int(perf_match.group(1))
            details["performance_score"] = perf_score

            if perf_score >= 90:
                status = CheckStatus.PASS
            elif perf_score >= 50:
                status = CheckStatus.WARN
            else:
                status = CheckStatus.FAIL

            return CheckResult(
                name=name, status=status, duration_seconds=duration,
                message=f"Performance score: {perf_score}/100", details=details
            )

        if code == 0:
            return CheckResult(
                name=name, status=CheckStatus.PASS, duration_seconds=duration,
                message="Lighthouse executado com sucesso", details=details
            )
        else:
            return CheckResult(
                name=name, status=CheckStatus.WARN, duration_seconds=duration,
                message="Lighthouse executado com avisos", details=details
            )

    # ========================================================================
    # CICLO DE EXECUCAO
    # ========================================================================

    def run_cycle(self, only: Optional[str] = None) -> CycleReport:
        """Executa um ciclo completo de verificacao."""
        cycle_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        start_time = datetime.now(timezone.utc)
        report = CycleReport(cycle_id=cycle_id, started_at=start_time.isoformat())

        self.logger.info("=" * 62)
        self.logger.info(f"  OpenClaw - Ciclo {cycle_id}")
        self.logger.info(f"  Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        self.logger.info("=" * 62)

        checks_map: Dict[str, List[Callable[[], CheckResult]]] = {
            "tests": [self.check_backend_tests, self.check_frontend_tests],
            "lint": [self.check_backend_lint, self.check_frontend_lint],
            "security": [self.check_security_bandit],
            "coverage": [self.check_coverage],
            "health": [self.check_health, self.check_docker_status, self.check_disk_space],
            "performance": [self.check_performance_lighthouse],
        }

        if only:
            if only not in checks_map:
                self.logger.error(f"Grupo de checks desconhecido: '{only}'")
                self.logger.info(f"Opcoes validas: {', '.join(checks_map.keys())}")
                return report
            checks_to_run = checks_map[only]
            self.logger.info(f"  Modo: apenas '{only}' ({len(checks_to_run)} check(s))")
        else:
            checks_to_run = [check for checks in checks_map.values() for check in checks]
            self.logger.info(f"  Modo: ciclo completo ({len(checks_to_run)} checks)")

        self.logger.info("-" * 62)

        for check_fn in checks_to_run:
            if not self._running:
                self.logger.info("Execucao interrompida por sinal de parada.")
                break

            check_display_name = check_fn.__name__.replace("check_", "").replace("_", " ").title()
            self.logger.info(f"  Executando: {check_display_name}...")

            try:
                result = check_fn()
                report.add_check(result)

                # Status formatado com cores ANSI
                status_str = result.status.value.upper()
                color_map = {
                    "PASS": "\033[92m",   # Verde
                    "FAIL": "\033[91m",   # Vermelho
                    "WARN": "\033[93m",   # Amarelo
                    "SKIP": "\033[90m",   # Cinza
                    "ERROR": "\033[91m",  # Vermelho
                }
                reset = "\033[0m"
                color = color_map.get(status_str, "")
                self.logger.info(
                    f"    {color}{status_str:5s}{reset} | {result.name} "
                    f"({result.duration_seconds:.1f}s) - {result.message}"
                )

            except Exception as e:
                self.logger.error(f"    Erro inesperado em {check_fn.__name__}: {e}")
                error_result = CheckResult(
                    name=check_fn.__name__,
                    status=CheckStatus.ERROR,
                    duration_seconds=0,
                    message=f"Excecao nao tratada: {str(e)}",
                    details={"exception": str(e), "type": type(e).__name__},
                )
                report.add_check(error_result)

        # Finalizar relatorio
        end_time = datetime.now(timezone.utc)
        report.finished_at = end_time.isoformat()
        report.duration_seconds = (end_time - start_time).total_seconds()
        report.compute_summary()

        # Salvar e exibir
        self._save_report(report)
        self._print_summary(report)

        # Salvar última referência para notificações
        self.last_report = report

        # Notificacoes
        self._send_notifications(report)

        # Limpeza de relatorios antigos
        self._cleanup_old_reports()

        return report

    # ========================================================================
    # RELATORIOS
    # ========================================================================

    def _save_report(self, report: CycleReport):
        """Salva relatorio em JSON e texto legivel."""
        # JSON
        json_path = self.reports_dir / f"cycle_{report.cycle_id}.json"
        report_dict = asdict(report)
        # Converter enums para string
        report_dict["overall_status"] = report.overall_status.value
        for check in report_dict.get("checks", []):
            if isinstance(check.get("status"), CheckStatus):
                check["status"] = check["status"].value

        json_path.write_text(json.dumps(report_dict, indent=2, ensure_ascii=False, default=str))
        self.logger.debug(f"Relatorio JSON salvo: {json_path}")

        # Latest symlink
        latest = self.reports_dir / "latest.json"
        try:
            if latest.exists() or latest.is_symlink():
                latest.unlink()
            latest.symlink_to(json_path.name)
        except OSError as e:
            self.logger.warning(f"Nao foi possivel criar symlink latest.json: {e}")

        # Texto legivel
        txt_path = self.reports_dir / f"cycle_{report.cycle_id}.txt"
        lines = [
            "=" * 62,
            f"  OpenClaw - Relatorio do Ciclo {report.cycle_id}",
            "=" * 62,
            f"  Inicio:    {report.started_at}",
            f"  Fim:       {report.finished_at}",
            f"  Duracao:   {report.duration_seconds:.1f}s",
            f"  Status:    {report.overall_status.value.upper()}",
            "-" * 62,
            "  RESULTADOS:",
            "-" * 62,
        ]

        for check in report.checks:
            status_val = check.get("status", "error")
            if isinstance(status_val, CheckStatus):
                status_val = status_val.value
            name = check.get("name", "?")
            msg = check.get("message", "")
            dur = check.get("duration_seconds", 0)
            lines.append(f"  {status_val.upper():5s} | {name} ({dur:.1f}s)")
            lines.append(f"         {msg}")

        lines.append("-" * 62)

        summary = report.summary
        if summary:
            counts = summary.get("status_counts", {})
            lines.append("  RESUMO:")
            lines.append(f"    Total:   {summary.get('total_checks', 0)}")
            lines.append(f"    Pass:    {counts.get('pass', 0)}")
            lines.append(f"    Fail:    {counts.get('fail', 0)}")
            lines.append(f"    Warn:    {counts.get('warn', 0)}")
            lines.append(f"    Skip:    {counts.get('skip', 0)}")
            lines.append(f"    Error:   {counts.get('error', 0)}")

        lines.append("=" * 62)
        txt_path.write_text("\n".join(lines), encoding="utf-8")
        self.logger.debug(f"Relatorio TXT salvo: {txt_path}")

    def _print_summary(self, report: CycleReport):
        """Imprime resumo no console."""
        self.logger.info("-" * 62)
        self.logger.info("  RESUMO DO CICLO")
        self.logger.info("-" * 62)

        summary = report.summary
        counts = summary.get("status_counts", {})

        overall = report.overall_status.value.upper()
        color_map = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m", "ERROR": "\033[91m"}
        reset = "\033[0m"
        color = color_map.get(overall, "")

        self.logger.info(f"  Status geral: {color}{overall}{reset}")
        self.logger.info(f"  Duracao total: {report.duration_seconds:.1f}s")

        # Health Score com cor
        health_score = summary.get("health_score", 0)
        if health_score >= 80:
            health_color = "\033[92m"  # Verde
        elif health_score >= 60:
            health_color = "\033[93m"  # Amarelo
        else:
            health_color = "\033[91m"  # Vermelho
        self.logger.info(f"  Health Score: {health_color}{health_score}/100{reset}")

        self.logger.info(
            f"  Checks: {counts.get('pass', 0)} pass | "
            f"{counts.get('fail', 0)} fail | "
            f"{counts.get('warn', 0)} warn | "
            f"{counts.get('skip', 0)} skip | "
            f"{counts.get('error', 0)} error"
        )

        json_path = self.reports_dir / f"cycle_{report.cycle_id}.json"
        self.logger.info(f"  Relatorio: {json_path}")
        self.logger.info("=" * 62)

    def show_latest_report(self):
        """Exibe o ultimo relatorio gerado."""
        latest = self.reports_dir / "latest.json"

        if not latest.exists():
            # Tentar encontrar o relatorio mais recente
            json_files = sorted(self.reports_dir.glob("cycle_*.json"), reverse=True)
            if not json_files:
                self.logger.info("Nenhum relatorio encontrado.")
                return
            latest = json_files[0]

        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Erro ao ler relatorio: {e}")
            return

        print()
        print("=" * 62)
        print(f"  Ultimo Relatorio OpenClaw")
        print("=" * 62)
        print(f"  Ciclo:     {data.get('cycle_id', '?')}")
        print(f"  Inicio:    {data.get('started_at', '?')}")
        print(f"  Fim:       {data.get('finished_at', '?')}")
        print(f"  Duracao:   {data.get('duration_seconds', 0):.1f}s")
        print(f"  Status:    {data.get('overall_status', '?').upper()}")
        print("-" * 62)

        for check in data.get("checks", []):
            status_val = check.get("status", "error").upper()
            name = check.get("name", "?")
            msg = check.get("message", "")
            dur = check.get("duration_seconds", 0)
            print(f"  {status_val:5s} | {name} ({dur:.1f}s) - {msg}")

        summary = data.get("summary", {})
        if summary:
            counts = summary.get("status_counts", {})
            print("-" * 62)
            print(f"  Total: {summary.get('total_checks', 0)} | "
                  f"Pass: {counts.get('pass', 0)} | "
                  f"Fail: {counts.get('fail', 0)} | "
                  f"Warn: {counts.get('warn', 0)} | "
                  f"Skip: {counts.get('skip', 0)} | "
                  f"Error: {counts.get('error', 0)}")

        print("=" * 62)
        print(f"  Arquivo: {latest}")
        print()

    # ========================================================================
    # NOTIFICACOES
    # ========================================================================

    def _send_notifications(self, report: CycleReport):
        """Envia notificacoes via webhooks configurados."""
        notify_config = self.config.get("notifications", {})
        notify_on = notify_config.get("notify_on", ["fail", "error"])

        if report.overall_status.value not in notify_on:
            return

        message = self._build_notification_message(report)

        # Discord
        discord_url = notify_config.get("discord_webhook", "")
        if discord_url:
            self._send_discord(discord_url, message)

        # Slack
        slack_url = notify_config.get("slack_webhook", "")
        if slack_url:
            self._send_slack(slack_url, message)

    def _build_notification_message(self, report: CycleReport) -> str:
        """Constroi mensagem de notificacao."""
        status = report.overall_status.value.upper()
        emoji_map = {"PASS": "OK", "FAIL": "ALERTA", "WARN": "ATENCAO", "ERROR": "ERRO"}
        prefix = emoji_map.get(status, "INFO")

        lines = [
            f"[{prefix}] OpenClaw - Ciclo {report.cycle_id}",
            f"Status: {status}",
            f"Duracao: {report.duration_seconds:.1f}s",
            "",
        ]

        failed_checks = [
            c for c in report.checks
            if c.get("status") in ("fail", "error")
        ]
        if failed_checks:
            lines.append("Checks com problema:")
            for c in failed_checks:
                lines.append(f"  - {c.get('name', '?')}: {c.get('message', '')}")

        return "\n".join(lines)

    def _send_discord(self, webhook_url: str, message: str):
        """Envia notificacao via Discord webhook com embed rico."""
        try:
            # Importar NotificationService
            import sys
            sys.path.insert(0, str(PROJECT_ROOT / "backend"))
            from modules.ai.bartolo.services.notification_service import NotificationService

            # Converter CycleReport para dict
            report_dict = asdict(self.last_report) if hasattr(self, 'last_report') else {}

            # Se não tem relatório salvo, usa mensagem simples
            if not report_dict:
                payload = json.dumps({"content": message}).encode("utf-8")
                req = urllib.request.Request(
                    webhook_url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                urllib.request.urlopen(req, timeout=10)
                return

            # Usa NotificationService para embed rico
            notifier = NotificationService(discord_webhook_url=webhook_url)

            # Executar código async de forma síncrona
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(notifier.send_discord(report_dict))
            loop.close()

            if success:
                self.logger.info("Notificacao Discord enviada com sucesso (embed rico)")
            else:
                self.logger.warning("Falha ao enviar notificacao Discord")

        except Exception as e:
            self.logger.warning(f"Erro ao enviar notificacao Discord: {e}")

    def _send_slack(self, webhook_url: str, message: str):
        """Envia notificacao via Slack webhook."""
        try:
            payload = json.dumps({"text": message}).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
            self.logger.debug("Notificacao Slack enviada com sucesso")
        except Exception as e:
            self.logger.warning(f"Erro ao enviar notificacao Slack: {e}")

    # ========================================================================
    # LIMPEZA
    # ========================================================================

    def _cleanup_old_reports(self):
        """Remove relatorios e logs antigos conforme politica de retencao."""
        retention = self.config.get("retention", {})
        reports_days = retention.get("reports_days", 30)
        logs_days = retention.get("logs_days", 14)

        cutoff_reports = datetime.now(timezone.utc) - timedelta(days=reports_days)
        cutoff_logs = datetime.now(timezone.utc) - timedelta(days=logs_days)

        # Limpar relatorios
        removed_reports = 0
        for f in self.reports_dir.glob("cycle_*"):
            if f.is_symlink():
                continue
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff_reports:
                    f.unlink()
                    removed_reports += 1
            except OSError:
                pass

        # Limpar logs
        removed_logs = 0
        for f in self.logs_dir.glob("runner_*.log"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                if mtime < cutoff_logs:
                    f.unlink()
                    removed_logs += 1
            except OSError:
                pass

        if removed_reports > 0 or removed_logs > 0:
            self.logger.debug(
                f"Limpeza: {removed_reports} relatorios e {removed_logs} logs removidos"
            )

    # ========================================================================
    # MODO DAEMON
    # ========================================================================

    def run_daemon(self, interval: int = 3600):
        """Modo daemon - executa ciclos continuos com intervalo configuravel."""
        self.logger.info(BANNER)
        self.logger.info(f"OpenClaw daemon iniciado")
        self.logger.info(f"  Intervalo entre ciclos: {interval}s ({interval // 60}min)")
        self.logger.info(f"  Project root: {self.project_root}")
        self.logger.info(f"  Relatorios: {self.reports_dir}")
        self.logger.info(f"  Logs: {self.logs_dir}")
        self.logger.info(f"  PID: {os.getpid()}")
        self.logger.info("")

        cycle_count = 0

        while self._running:
            cycle_count += 1
            self.logger.info(f"--- Iniciando ciclo #{cycle_count} ---")

            try:
                report = self.run_cycle()
                self.logger.info(
                    f"--- Ciclo #{cycle_count} finalizado: "
                    f"{report.overall_status.value.upper()} "
                    f"({report.duration_seconds:.1f}s) ---"
                )
            except Exception as e:
                self.logger.error(f"Erro critico no ciclo #{cycle_count}: {e}", exc_info=True)

            if not self._running:
                break

            # Aguardar proximo ciclo com verificacao periodica de sinal
            self.logger.info(f"Proximo ciclo em {interval}s...")
            wait_start = time.monotonic()
            while self._running and (time.monotonic() - wait_start) < interval:
                time.sleep(min(10, interval))

        self.logger.info("OpenClaw daemon encerrado.")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="OpenClaw Runner - Orquestrador de qualidade continua do Conecta PRO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python runner.py                    # Ciclo completo
  python runner.py --only tests       # Apenas testes
  python runner.py --only security    # Apenas seguranca
  python runner.py --only health      # Apenas health check
  python runner.py --only lint        # Apenas linting
  python runner.py --only coverage    # Apenas cobertura
  python runner.py --only performance # Apenas performance
  python runner.py --report           # Exibir ultimo relatorio
  python runner.py --daemon           # Modo daemon (ciclos continuos)
  python runner.py --interval 1800   # Intervalo de 30min entre ciclos
        """,
    )
    parser.add_argument(
        "--only",
        choices=["tests", "lint", "security", "coverage", "health", "performance"],
        help="Executar apenas um grupo especifico de checks",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Executar em modo daemon (ciclos continuos)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Intervalo em segundos entre ciclos no modo daemon (padrao: config ou 3600)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Exibir o ultimo relatorio gerado",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Caminho para arquivo de configuracao JSON",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"OpenClaw Runner v{VERSION}",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Executar checks em paralelo (3x mais rapido)",
    )

    args = parser.parse_args()

    # Carregar configuracao
    config_path = Path(args.config) if args.config else CONFIG_PATH
    config = load_config(config_path)

    # Determinar intervalo
    interval = args.interval or config.get("cycle_interval_seconds", 3600)

    # Criar runner
    runner = OpenClawRunner(
        project_root=Path(config.get("project_root", str(PROJECT_ROOT))),
        config=config,
    )

    if args.report:
        runner.show_latest_report()
    elif args.daemon:
        runner.run_daemon(interval=interval)
    else:
        print(BANNER)
        report = runner.run_cycle(only=args.only)
        # Exit code baseado no status
        if report.overall_status == CheckStatus.FAIL:
            sys.exit(1)
        elif report.overall_status == CheckStatus.ERROR:
            sys.exit(2)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
