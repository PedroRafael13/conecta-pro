"""
Auto Healer for OpenClaw - Correções automáticas de problemas comuns.

Detecta e corrige automaticamente issues conhecidos baseado
em padrões de falhas dos checks.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AutoHealer:
    """Auto-healing de problemas comuns detectados pelo OpenClaw."""

    def __init__(
        self,
        project_root: Path,
        dry_run: bool = False,
        auto_fix_enabled: bool = True,
    ):
        """
        Initialize auto healer.

        Args:
            project_root: Raiz do projeto
            dry_run: Se True, apenas simula correções sem executar
            auto_fix_enabled: Se False, apenas reporta sem corrigir
        """
        self.project_root = Path(project_root)
        self.frontend_dir = self.project_root / "frontend"
        self.backend_dir = self.project_root / "backend"
        self.dry_run = dry_run
        self.auto_fix_enabled = auto_fix_enabled

    def _run_command(
        self, cmd: str, cwd: Optional[Path] = None, timeout: int = 300
    ) -> Tuple[int, str, str]:
        """
        Executa comando shell.

        Args:
            cmd: Comando a executar
            cwd: Diretório de trabalho
            timeout: Timeout em segundos

        Returns:
            Tuple (returncode, stdout, stderr)
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Executaria: {cmd}")
            return 0, "", ""

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout executando: {cmd}")
            return -1, "", f"Timeout após {timeout}s"
        except Exception as e:
            logger.error(f"Erro executando {cmd}: {e}")
            return -1, "", str(e)

    def can_fix(self, check_name: str, check_details: Dict[str, Any]) -> bool:
        """
        Verifica se pode corrigir automaticamente um check.

        Args:
            check_name: Nome do check
            check_details: Detalhes do check result

        Returns:
            True se pode corrigir
        """
        healable_checks = {
            "Dependency Audit (Frontend)": self._can_fix_npm_vulnerabilities,
            "Dependency Audit (Backend)": self._can_fix_pip_vulnerabilities,
            "Docker Status": self._can_fix_docker_unhealthy,
            "Backend Lint": self._can_fix_lint_issues,
            "Frontend Lint": self._can_fix_lint_issues,
            "Disk Space": self._can_fix_disk_space,
        }

        check_key = check_name.strip()
        if check_key in healable_checks:
            return healable_checks[check_key](check_details)

        return False

    def heal(self, check_name: str, check_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tenta corrigir automaticamente um problema.

        Args:
            check_name: Nome do check
            check_details: Detalhes do check result

        Returns:
            Dict com resultado da correção
        """
        if not self.auto_fix_enabled:
            return {"fixed": False, "reason": "Auto-fix desabilitado", "actions": []}

        healers = {
            "Dependency Audit (Frontend)": self._heal_npm_vulnerabilities,
            "Dependency Audit (Backend)": self._heal_pip_vulnerabilities,
            "Docker Status": self._heal_docker_unhealthy,
            "Backend Lint": self._heal_lint_issues,
            "Frontend Lint": self._heal_lint_issues,
            "Disk Space": self._heal_disk_space,
        }

        check_key = check_name.strip()
        if check_key not in healers:
            return {
                "fixed": False,
                "reason": f"Sem healer disponível para '{check_name}'",
                "actions": [],
            }

        logger.info(f"Tentando auto-healing para: {check_name}")
        return healers[check_key](check_details)

    # ========================================================================
    # NPM Vulnerabilities
    # ========================================================================

    def _can_fix_npm_vulnerabilities(self, details: Dict[str, Any]) -> bool:
        """Verifica se pode corrigir vulnerabilidades npm."""
        # Apenas auto-fix se não houver critical (muito arriscado)
        critical = details.get("critical", 0)
        high = details.get("high", 0)
        return critical == 0 and high > 0

    def _heal_npm_vulnerabilities(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Tenta corrigir vulnerabilidades npm com npm audit fix."""
        actions = []

        # Tentar npm audit fix (safe fixes)
        logger.info("Executando npm audit fix...")
        code, stdout, stderr = self._run_command("npm audit fix", cwd=self.frontend_dir, timeout=180)

        actions.append(
            {
                "action": "npm audit fix",
                "success": code == 0,
                "output": stdout[-500:] if stdout else stderr[-500:],
            }
        )

        if code == 0:
            return {
                "fixed": True,
                "reason": "npm audit fix aplicado com sucesso",
                "actions": actions,
                "recommendation": "Revisar mudanças e testar aplicação",
            }
        else:
            return {
                "fixed": False,
                "reason": "npm audit fix falhou",
                "actions": actions,
                "recommendation": "Revisar manualmente com npm audit fix --force (CUIDADO)",
            }

    # ========================================================================
    # Pip Vulnerabilities
    # ========================================================================

    def _can_fix_pip_vulnerabilities(self, details: Dict[str, Any]) -> bool:
        """Verifica se pode corrigir vulnerabilidades pip."""
        # Pip-audit não tem auto-fix, apenas reporta
        return False

    def _heal_pip_vulnerabilities(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Pip-audit não tem auto-fix automático."""
        packages = details.get("packages", [])
        return {
            "fixed": False,
            "reason": "pip-audit não suporta auto-fix",
            "actions": [],
            "recommendation": f"Atualizar manualmente os pacotes: {', '.join(packages[:5])}",
        }

    # ========================================================================
    # Docker Unhealthy
    # ========================================================================

    def _can_fix_docker_unhealthy(self, details: Dict[str, Any]) -> bool:
        """Verifica se pode reiniciar containers unhealthy."""
        # Extrair lista de containers unhealthy
        containers = details.get("containers", [])
        unhealthy = [
            c["name"]
            for c in containers
            if isinstance(c, dict) and "unhealthy" in c.get("status", "").lower()
        ]

        # Fallback: verificar unhealthy_containers direto
        if not unhealthy:
            unhealthy = details.get("unhealthy_containers", [])

        return len(unhealthy) > 0

    def _heal_docker_unhealthy(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Reinicia containers unhealthy."""
        # Extrair lista de containers unhealthy
        containers = details.get("containers", [])
        unhealthy = [
            c["name"]
            for c in containers
            if isinstance(c, dict) and "unhealthy" in c.get("status", "").lower()
        ]

        # Fallback: verificar unhealthy_containers direto
        if not unhealthy:
            unhealthy = details.get("unhealthy_containers", [])

        actions = []
        fixed_count = 0

        for container_name in unhealthy:
            logger.info(f"Reiniciando container unhealthy: {container_name}")
            code, stdout, stderr = self._run_command(
                f"docker restart {container_name}", timeout=60
            )

            success = code == 0
            if success:
                fixed_count += 1

            actions.append(
                {"action": f"docker restart {container_name}", "success": success, "output": stdout}
            )

        return {
            "fixed": fixed_count > 0,
            "reason": f"Reiniciados {fixed_count}/{len(unhealthy)} containers",
            "actions": actions,
            "recommendation": "Verificar logs dos containers com: docker logs <container>",
        }

    # ========================================================================
    # Lint Issues
    # ========================================================================

    def _can_fix_lint_issues(self, details: Dict[str, Any]) -> bool:
        """Verifica se pode corrigir issues de linting."""
        # Ruff e eslint têm --fix
        return True

    def _heal_lint_issues(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica auto-fix de linting."""
        actions = []

        # Detectar se é backend ou frontend pelo details
        output = details.get("output_tail", "")

        if "ruff" in output.lower():
            # Backend: ruff format + ruff check --fix
            logger.info("Aplicando ruff format...")
            code1, stdout1, _ = self._run_command(
                "ruff format .", cwd=self.backend_dir, timeout=60
            )
            actions.append({"action": "ruff format", "success": code1 == 0, "output": stdout1[-200:]})

            logger.info("Aplicando ruff check --fix...")
            code2, stdout2, _ = self._run_command(
                "ruff check --fix .", cwd=self.backend_dir, timeout=60
            )
            actions.append(
                {"action": "ruff check --fix", "success": code2 == 0, "output": stdout2[-200:]}
            )

            fixed = code1 == 0 or code2 == 0

        else:
            # Frontend: npm run lint:fix
            logger.info("Aplicando eslint --fix...")
            code, stdout, _ = self._run_command(
                "npm run lint:fix", cwd=self.frontend_dir, timeout=120
            )
            actions.append({"action": "npm run lint:fix", "success": code == 0, "output": stdout[-200:]})
            fixed = code == 0

        return {
            "fixed": fixed,
            "reason": "Auto-fix de linting aplicado" if fixed else "Auto-fix falhou",
            "actions": actions,
            "recommendation": "Revisar mudanças com git diff antes de commitar",
        }

    # ========================================================================
    # Disk Space
    # ========================================================================

    def _can_fix_disk_space(self, details: Dict[str, Any]) -> bool:
        """Verifica se pode liberar espaço."""
        free_gb = details.get("free_gb", 999)
        return free_gb < 10  # Apenas se crítico

    def _heal_disk_space(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Tenta liberar espaço em disco."""
        actions = []

        # 1. Docker system prune
        logger.info("Limpando recursos Docker não usados...")
        code1, stdout1, _ = self._run_command(
            "docker system prune -af --volumes", timeout=300
        )
        actions.append(
            {"action": "docker system prune", "success": code1 == 0, "output": stdout1[-200:]}
        )

        # 2. Limpar node_modules/.next cache
        logger.info("Limpando cache frontend...")
        code2, _, _ = self._run_command(
            "rm -rf frontend/.next frontend/node_modules/.cache", timeout=60
        )
        actions.append({"action": "clean frontend cache", "success": code2 == 0})

        # 3. Limpar __pycache__
        logger.info("Limpando __pycache__...")
        code3, _, _ = self._run_command("find . -type d -name __pycache__ -exec rm -rf {} +", timeout=60)
        actions.append({"action": "clean __pycache__", "success": code3 == 0})

        fixed = any(a["success"] for a in actions)

        return {
            "fixed": fixed,
            "reason": "Limpeza de disco executada",
            "actions": actions,
            "recommendation": "Verificar espaço liberado com df -h",
        }

    # ========================================================================
    # Batch Healing
    # ========================================================================

    def heal_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tenta corrigir todos os problemas de um relatório.

        Args:
            report: Relatório OpenClaw completo

        Returns:
            Dict com resultados de todas as correções
        """
        if not self.auto_fix_enabled:
            return {"total_checks": 0, "healed": 0, "results": []}

        checks = report.get("checks", [])
        failed_checks = [c for c in checks if c.get("status") in ["fail", "error", "warn"]]

        results = []
        healed_count = 0

        for check in failed_checks:
            check_name = check.get("name", "Unknown")
            check_details = check.get("details", {})

            if self.can_fix(check_name, check_details):
                logger.info(f"Tentando corrigir: {check_name}")
                result = self.heal(check_name, check_details)
                result["check_name"] = check_name
                results.append(result)

                if result.get("fixed"):
                    healed_count += 1

        return {
            "total_checks": len(failed_checks),
            "healable": len(results),
            "healed": healed_count,
            "results": results,
        }
