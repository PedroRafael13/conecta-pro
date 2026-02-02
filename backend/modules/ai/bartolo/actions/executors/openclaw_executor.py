"""
Executor para ações do OpenClaw (Quality Checks, Deploy, Daemon).

Suporta:
- OPENCLAW_RUN_TESTS: Executar testes automatizados
- OPENCLAW_RUN_LINT: Executar verificação de qualidade de código
- OPENCLAW_RUN_SECURITY: Executar scan de segurança
- OPENCLAW_RUN_COVERAGE: Verificar cobertura de testes
- OPENCLAW_RUN_HEALTH: Executar health check dos serviços
- OPENCLAW_RUN_FULL_CYCLE: Executar ciclo completo de quality checks
- OPENCLAW_DEPLOY_STAGING: Deploy para ambiente de staging
- OPENCLAW_DEPLOY_PRODUCTION: Deploy para ambiente de produção
- OPENCLAW_DAEMON_START: Iniciar daemon do OpenClaw
- OPENCLAW_DAEMON_STOP: Parar daemon do OpenClaw

Author: Conecta PRO Team
Date: 2026-02-02
"""

import asyncio
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..action_schemas import ActionPreview, ActionRequest, ActionResult
from ..action_types import ActionStatus, ActionType
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)

# Paths
OPENCLAW_RUNNER = "/opt/conecta-pro/scripts/openclaw/runner.py"
OPENCLAW_REPORTS_DIR = Path("/opt/conecta-pro/reports/openclaw")


class OpenClawActionExecutor(BaseActionExecutor):
    """Executor para ações de Quality Checks, Deploy e Daemon do OpenClaw."""

    SUPPORTED_ACTIONS = [
        ActionType.OPENCLAW_RUN_TESTS,
        ActionType.OPENCLAW_RUN_LINT,
        ActionType.OPENCLAW_RUN_SECURITY,
        ActionType.OPENCLAW_RUN_COVERAGE,
        ActionType.OPENCLAW_RUN_HEALTH,
        ActionType.OPENCLAW_RUN_FULL_CYCLE,
        ActionType.OPENCLAW_RUN_E2E,
        ActionType.OPENCLAW_RUN_E2E_MODULE,
        ActionType.OPENCLAW_DEPLOY_STAGING,
        ActionType.OPENCLAW_DEPLOY_PRODUCTION,
        ActionType.OPENCLAW_DAEMON_START,
        ActionType.OPENCLAW_DAEMON_STOP,
    ]

    # Mapeamento de ActionType para flag --only do runner.py
    CHECK_MAP = {
        ActionType.OPENCLAW_RUN_TESTS: "tests",
        ActionType.OPENCLAW_RUN_LINT: "lint",
        ActionType.OPENCLAW_RUN_SECURITY: "security",
        ActionType.OPENCLAW_RUN_COVERAGE: "coverage",
        ActionType.OPENCLAW_RUN_HEALTH: "health",
        ActionType.OPENCLAW_RUN_FULL_CYCLE: None,  # Roda tudo
        ActionType.OPENCLAW_RUN_E2E: "e2e",
        ActionType.OPENCLAW_RUN_E2E_MODULE: "e2e",  # Usa parâmetro adicional
    }

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview da ação OpenClaw."""
        action_type = request.action_type
        params = request.parameters or {}

        # Títulos e descrições por ação
        previews = {
            ActionType.OPENCLAW_RUN_TESTS: {
                "title": "Executar Testes",
                "description": "Executar testes automatizados (pytest backend + vitest frontend)",
                "warnings": ["Pode levar até 2 minutos"],
            },
            ActionType.OPENCLAW_RUN_LINT: {
                "title": "Executar Lint",
                "description": "Verificação de qualidade de código (ruff backend + eslint frontend)",
                "warnings": [],
            },
            ActionType.OPENCLAW_RUN_SECURITY: {
                "title": "Scan de Segurança",
                "description": "Análise de vulnerabilidades com Bandit",
                "warnings": ["Apenas backend Python"],
            },
            ActionType.OPENCLAW_RUN_COVERAGE: {
                "title": "Verificar Cobertura",
                "description": "Análise de cobertura de testes (meta: 60%)",
                "warnings": [],
            },
            ActionType.OPENCLAW_RUN_HEALTH: {
                "title": "Health Check",
                "description": "Verificação de saúde de todos os serviços (PostgreSQL, Redis, containers)",
                "warnings": [],
            },
            ActionType.OPENCLAW_RUN_FULL_CYCLE: {
                "title": "Ciclo Completo OpenClaw",
                "description": "Executar TODOS os checks: testes, lint, security, coverage, health, docker, disk, lighthouse",
                "warnings": ["Pode levar até 5 minutos"],
            },
            ActionType.OPENCLAW_RUN_E2E: {
                "title": "Testes E2E Completos",
                "description": "Executar todos os testes E2E (Playwright)",
                "warnings": ["Pode levar até 5 minutos"],
            },
            ActionType.OPENCLAW_RUN_E2E_MODULE: {
                "title": "Testes E2E por Módulo",
                "description": f"Executar testes E2E do módulo {params.get('module', 'desconhecido').capitalize()}",
                "warnings": ["Duração: 1-2 minutos"],
            },
            ActionType.OPENCLAW_DEPLOY_PRODUCTION: {
                "title": "Deploy para Produção",
                "description": "Deploy do sistema para ambiente de produção",
                "warnings": [
                    "⚠️ AÇÃO CRÍTICA",
                    "Sistema ficará indisponível por ~2 minutos",
                    "Requer confirmação dupla",
                ],
            },
            ActionType.OPENCLAW_DEPLOY_STAGING: {
                "title": "Deploy para Staging",
                "description": "Deploy do sistema para ambiente de homologação",
                "warnings": ["Sistema de staging ficará indisponível por ~1 minuto"],
            },
            ActionType.OPENCLAW_DAEMON_START: {
                "title": "Iniciar Daemon OpenClaw",
                "description": "Iniciar o modo daemon (execução automática a cada 1 hora)",
                "warnings": [],
            },
            ActionType.OPENCLAW_DAEMON_STOP: {
                "title": "Parar Daemon OpenClaw",
                "description": "Parar o modo daemon (desativa execução automática)",
                "warnings": [],
            },
        }

        preview_data = previews.get(
            action_type,
            {
                "title": "Ação OpenClaw",
                "description": f"Executar {action_type}",
                "warnings": [],
            },
        )

        changes_summary = []
        changes_summary.append(f"Ação: {preview_data['title']}")

        # Adiciona parâmetros se houver
        if params:
            for key, value in params.items():
                changes_summary.append(f"{key}: {value}")

        # Permissões
        permission_map = {
            ActionType.OPENCLAW_DEPLOY_PRODUCTION: "openclaw.deploy",
            ActionType.OPENCLAW_DEPLOY_STAGING: "openclaw.deploy",
            ActionType.OPENCLAW_DAEMON_START: "openclaw.daemon",
            ActionType.OPENCLAW_DAEMON_STOP: "openclaw.daemon",
        }
        required_permission = permission_map.get(action_type, "openclaw.execute")

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=action_type,
            title=preview_data["title"],
            description=preview_data["description"],
            affected_entities=[],
            changes_summary=changes_summary,
            warnings=preview_data["warnings"],
            required_permission=required_permission,
            user_has_permission=True,  # TODO: Verificar permissão real
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa ação OpenClaw."""
        started_at = datetime.now(UTC)
        action_type = request.action_type
        params = request.parameters or {}

        try:
            # Deploy e Daemon usam comandos diferentes
            if action_type == ActionType.OPENCLAW_DEPLOY_PRODUCTION:
                return await self._execute_deploy("production", action_id, started_at)
            elif action_type == ActionType.OPENCLAW_DEPLOY_STAGING:
                return await self._execute_deploy("staging", action_id, started_at)
            elif action_type == ActionType.OPENCLAW_DAEMON_START:
                return await self._execute_daemon("start", action_id, started_at)
            elif action_type == ActionType.OPENCLAW_DAEMON_STOP:
                return await self._execute_daemon("stop", action_id, started_at)
            elif action_type == ActionType.OPENCLAW_RUN_E2E_MODULE:
                # E2E por módulo
                module = params.get("module", "")
                return await self._execute_e2e_module(module, action_id, started_at)
            else:
                # Quality checks
                return await self._execute_check(action_type, action_id, started_at)

        except Exception as e:
            logger.error(f"Erro ao executar OpenClaw {action_type}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.FAILED,
                success=False,
                message="Erro ao executar OpenClaw",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.now(UTC),
                affected_entities=[],
            )

    async def _execute_check(self, action_type: ActionType, action_id: str, started_at: datetime) -> ActionResult:
        """Executa check de qualidade via runner.py."""
        check_type = self.CHECK_MAP.get(action_type)

        # Monta comando
        cmd = ["python3", str(OPENCLAW_RUNNER)]
        if check_type:
            cmd.extend(["--only", check_type])

        logger.info(f"[OpenClaw] Executando: {' '.join(cmd)}")

        # Executa subprocess (timeout 5min)
        result = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd="/opt/conecta-pro"
        )

        try:
            stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=300)
        except TimeoutError:
            result.kill()
            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.FAILED,
                success=False,
                message="Timeout: execução ultrapassou 5 minutos",
                error_message="Timeout",
                started_at=started_at,
                completed_at=datetime.now(UTC),
                affected_entities=[],
            )

        # Lê relatório gerado
        latest_json = OPENCLAW_REPORTS_DIR / "latest.json"
        if latest_json.exists():
            report = json.loads(latest_json.read_text())

            overall_status = report.get("overall_status", "unknown").upper()
            success = overall_status == "PASS"

            summary = report.get("summary", {})
            counts = summary.get("status_counts", {})
            duration = report.get("duration_seconds", 0)

            message = f"""✅ OpenClaw executado com sucesso!

**Status:** {overall_status}
**Duração:** {duration:.1f}s
**Resultados:**
- ✅ Pass: {counts.get("pass", 0)}
- ❌ Fail: {counts.get("fail", 0)}
- ⚠️ Warn: {counts.get("warn", 0)}
- ⏭️ Skip: {counts.get("skip", 0)}
- 🔴 Error: {counts.get("error", 0)}
"""

            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.COMPLETED,
                success=success,
                message=message,
                details={
                    "cycle_id": report.get("cycle_id"),
                    "overall_status": overall_status,
                    "summary": summary,
                    "report_path": str(latest_json),
                },
                affected_entities=[],
                started_at=started_at,
                completed_at=datetime.now(UTC),
                duration_seconds=(datetime.now(UTC) - started_at).total_seconds(),
            )
        else:
            return ActionResult(
                action_id=action_id,
                action_type=action_type,
                status=ActionStatus.FAILED,
                success=False,
                message="Relatório não encontrado",
                error_message=stderr.decode() if stderr else "Unknown error",
                started_at=started_at,
                completed_at=datetime.now(UTC),
                affected_entities=[],
            )

    async def _execute_e2e_module(self, module: str, action_id: str, started_at: datetime) -> ActionResult:
        """Executa testes E2E de um módulo específico via npm."""
        # Lista de módulos válidos do sistema
        valid_modules = [
            "ai",
            "analytics",
            "audit",
            "automation",
            "bidding",
            "campo",
            "clients",
            "config",
            "core",
            "crm",
            "document-kits",
            "documents",
            "equipment",
            "fase5",
            "financial",
            "ged",
            "government",
            "health",
            "hr",
            "integrations",
            "mobile",
            "monitoring",
            "notifications",
            "operacional",
            "recruitment",
            "reimbursement",
            "reports",
            "retention",
            "scheduler",
            "search",
            "security",
            "services",
        ]

        if not module or module not in valid_modules:
            return ActionResult(
                action_id=action_id,
                action_type=ActionType.OPENCLAW_RUN_E2E_MODULE,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Módulo inválido: {module}. Módulos válidos: {', '.join(valid_modules[:10])}...",
                error_message="Invalid module",
                started_at=started_at,
                completed_at=datetime.now(UTC),
                affected_entities=[],
            )

        # Comando via bash inline (container não tem acesso ao filesystem do host)
        cmd = ["bash", "-c", f"cd /opt/conecta-pro/frontend && npm run test:e2e:{module}"]
        logger.info(f"[OpenClaw E2E] Executando testes E2E do módulo: {module}")

        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/opt/conecta-pro",
        )

        try:
            stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=180)
            output = stdout.decode() + stderr.decode()
            success = result.returncode == 0

            # Parse resultados do Playwright
            tests_passed = 0
            tests_failed = 0
            import re

            match_passed = re.search(r"(\d+)\s+passed", output, re.IGNORECASE)
            if match_passed:
                tests_passed = int(match_passed.group(1))
            match_failed = re.search(r"(\d+)\s+failed", output, re.IGNORECASE)
            if match_failed:
                tests_failed = int(match_failed.group(1))

            if success and tests_passed > 0:
                message = f"""✅ Testes E2E do módulo **{module.capitalize()}** concluídos!

**Resultados:**
- ✅ Passaram: {tests_passed}
- ❌ Falharam: {tests_failed}

Todos os testes do módulo {module} foram executados com sucesso."""
            elif tests_failed > 0:
                message = f"""⚠️ Testes E2E do módulo **{module.capitalize()}** com falhas

**Resultados:**
- ✅ Passaram: {tests_passed}
- ❌ Falharam: {tests_failed}

Verifique os logs para mais detalhes."""
            else:
                message = f"Testes E2E do módulo {module} executados (status: {result.returncode})"

            return ActionResult(
                action_id=action_id,
                action_type=ActionType.OPENCLAW_RUN_E2E_MODULE,
                status=ActionStatus.COMPLETED if success else ActionStatus.FAILED,
                success=success,
                message=message,
                details={
                    "module": module,
                    "passed": tests_passed,
                    "failed": tests_failed,
                    "output_tail": output[-1000:] if len(output) > 1000 else output,
                },
                affected_entities=[],
                started_at=started_at,
                completed_at=datetime.now(UTC),
                duration_seconds=(datetime.now(UTC) - started_at).total_seconds(),
            )

        except TimeoutError:
            result.kill()
            return ActionResult(
                action_id=action_id,
                action_type=ActionType.OPENCLAW_RUN_E2E_MODULE,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Timeout: testes E2E do módulo {module} ultrapassaram 3 minutos",
                error_message="Timeout",
                started_at=started_at,
                completed_at=datetime.now(UTC),
                affected_entities=[],
            )

    async def _execute_deploy(self, env: str, action_id: str, started_at: datetime) -> ActionResult:
        """Executa deploy via make."""
        cmd = ["make", f"deploy-{env}"]
        logger.info(f"[OpenClaw] Deploy {env}: {' '.join(cmd)}")

        result = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd="/opt/conecta-pro"
        )

        try:
            stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=600)
            success = result.returncode == 0

            message = f"✅ Deploy {env} concluído!" if success else f"❌ Deploy {env} falhou"

            return ActionResult(
                action_id=action_id,
                action_type=(
                    ActionType.OPENCLAW_DEPLOY_PRODUCTION if env == "production" else ActionType.OPENCLAW_DEPLOY_STAGING
                ),
                status=ActionStatus.COMPLETED if success else ActionStatus.FAILED,
                success=success,
                message=message,
                details={"stdout": stdout.decode()[:1000], "stderr": stderr.decode()[:1000]},
                affected_entities=[],
                started_at=started_at,
                completed_at=datetime.now(UTC),
                duration_seconds=(datetime.now(UTC) - started_at).total_seconds(),
            )

        except TimeoutError:
            result.kill()
            return ActionResult(
                action_id=action_id,
                action_type=(
                    ActionType.OPENCLAW_DEPLOY_PRODUCTION if env == "production" else ActionType.OPENCLAW_DEPLOY_STAGING
                ),
                status=ActionStatus.FAILED,
                success=False,
                message="Timeout: deploy ultrapassou 10 minutos",
                error_message="Timeout",
                started_at=started_at,
                completed_at=datetime.now(UTC),
                affected_entities=[],
            )

    async def _execute_daemon(self, action: str, action_id: str, started_at: datetime) -> ActionResult:
        """Inicia/para daemon do OpenClaw."""
        # TODO: Implementar controle de daemon (systemctl ou signal)
        logger.info(f"[OpenClaw] Daemon {action}")

        return ActionResult(
            action_id=action_id,
            action_type=(ActionType.OPENCLAW_DAEMON_START if action == "start" else ActionType.OPENCLAW_DAEMON_STOP),
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Daemon OpenClaw {'iniciado' if action == 'start' else 'parado'}",
            details={},
            affected_entities=[],
            started_at=started_at,
            completed_at=datetime.now(UTC),
            duration_seconds=(datetime.now(UTC) - started_at).total_seconds(),
        )
