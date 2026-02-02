"""Skill OpenClaw - Agente de Qualidade e DevOps"""

import json
import logging
from pathlib import Path
from typing import Any

from ..services.openclaw_analyzer import OpenClawAnalyzer
from .base_skill import BaseSkill

logger = logging.getLogger(__name__)

OPENCLAW_REPORTS_DIR = Path("/opt/conecta-pro/reports/openclaw")


class OpenClawSkill(BaseSkill):
    """Skill para interagir com o OpenClaw (Quality Checks, Deploy, Daemon)"""

    name = "openclaw"
    description = "Agente de qualidade e DevOps - testes, lint, security, deploy"
    commands = [
        "",  # help/default
        "status",
        "report",
        "historico",
        "analyze",  # NEW: AI analysis
        "testes",
        "testes-front",
        "lint",
        "security",
        "coverage",
        "health",
        "ciclo",
        "deploy",
        "config",
        "daemon",
    ]

    async def execute(self, command: str, args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        """Executa comando da skill OpenClaw"""

        if not command or command == "help":
            return self._show_help()

        handlers = {
            "status": self._status,
            "report": self._report,
            "historico": self._historico,
            "analyze": self._analyze,  # NEW: AI analysis
            "testes": self._testes,
            "testes-front": self._testes_front,
            "lint": self._lint,
            "security": self._security,
            "coverage": self._coverage,
            "health": self._health,
            "ciclo": self._ciclo,
            "deploy": self._deploy,
            "config": self._config,
            "daemon": self._daemon,
        }

        handler = handlers.get(command, self._show_help)
        return await handler(args, context)

    def get_help(self) -> str:
        """Retorna texto de ajuda"""
        return """**OpenClaw - Agente de Qualidade**

Comandos disponíveis:

**📊 Consulta:**
- `/openclaw status` - Status geral do sistema
- `/openclaw report` - Último relatório detalhado
- `/openclaw historico [N]` - Últimos N ciclos (padrão: 10)
- `/openclaw analyze` - 🤖 Análise IA das falhas (NOVO!)

**🔍 Quality Checks:**
- `/openclaw testes` - Executar testes backend (pytest)
- `/openclaw testes-front` - Executar testes frontend (vitest)
- `/openclaw lint` - Verificar qualidade (ruff + eslint)
- `/openclaw security` - Scan de segurança (bandit)
- `/openclaw coverage` - Verificar cobertura (meta: 60%)
- `/openclaw health` - Health check dos serviços
- `/openclaw ciclo` - Ciclo completo (todos os checks)

**🚀 Deploy:**
- `/openclaw deploy [staging|production]` - Disparar deploy

**⚙️ Sistema:**
- `/openclaw config` - Ver/alterar configuração
- `/openclaw daemon [start|stop|status]` - Controlar modo daemon
"""

    def _show_help(self, args=None, context=None) -> dict[str, Any]:
        """Mostra ajuda"""
        return {
            "response": self.get_help(),
            "intent": "openclaw_help",
            "suggestions": ["/openclaw status", "/openclaw testes", "/openclaw ciclo"],
        }

    async def _status(self, args: list[str], context: dict) -> dict[str, Any]:
        """Mostra status geral do último ciclo"""

        latest_json = OPENCLAW_REPORTS_DIR / "latest.json"

        if not latest_json.exists():
            return {
                "response": "⚠️ Nenhum relatório OpenClaw encontrado. Execute `/openclaw ciclo` para gerar.",
                "intent": "openclaw_status",
                "suggestions": ["/openclaw ciclo"],
            }

        try:
            report = json.loads(latest_json.read_text())

            overall_status = report.get("overall_status", "unknown").upper()
            cycle_id = report.get("cycle_id", "N/A")
            duration = report.get("duration_seconds", 0)
            summary = report.get("summary", {})
            counts = summary.get("status_counts", {})

            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "ERROR": "🔴",
            }.get(overall_status, "❓")

            response = f"""**{status_emoji} Status OpenClaw: {overall_status}**

**Último Ciclo:** {cycle_id}
**Duração:** {duration:.1f}s

**Resultados:**
- ✅ Pass: {counts.get("pass", 0)}
- ❌ Fail: {counts.get("fail", 0)}
- ⚠️ Warn: {counts.get("warn", 0)}
- ⏭️ Skip: {counts.get("skip", 0)}
- 🔴 Error: {counts.get("error", 0)}
"""

            return {
                "response": response,
                "intent": "openclaw_status",
                "data": {"cycle_id": cycle_id, "status": overall_status, "summary": summary},
                "suggestions": ["/openclaw report", "/openclaw historico"],
            }

        except Exception as e:
            logger.error(f"Erro ao ler status OpenClaw: {e}")
            return {
                "response": f"❌ Erro ao ler status: {e}",
                "intent": "openclaw_status",
                "error": str(e),
            }

    async def _report(self, args: list[str], context: dict) -> dict[str, Any]:
        """Mostra último relatório detalhado"""

        latest_json = OPENCLAW_REPORTS_DIR / "latest.json"

        if not latest_json.exists():
            return {
                "response": "⚠️ Nenhum relatório encontrado.",
                "intent": "openclaw_report",
            }

        try:
            report = json.loads(latest_json.read_text())

            checks = report.get("checks", [])
            lines = [f"**📋 Relatório OpenClaw - {report.get('cycle_id')}**\n"]

            for check in checks:
                name = check.get("name", "Unknown")
                status = check.get("status", "unknown").upper()
                duration = check.get("duration_seconds", 0)
                message = check.get("message", "")

                emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️", "ERROR": "🔴"}.get(status, "❓")

                lines.append(f"{emoji} **{name}** ({duration:.1f}s)")
                if message:
                    lines.append(f"   └─ {message}")

            response = "\n".join(lines)

            return {
                "response": response,
                "intent": "openclaw_report",
                "data": {"checks": checks},
                "suggestions": ["/openclaw status", "/openclaw ciclo"],
            }

        except Exception as e:
            logger.error(f"Erro ao ler relatório: {e}")
            return {
                "response": f"❌ Erro ao ler relatório: {e}",
                "intent": "openclaw_report",
                "error": str(e),
            }

    async def _historico(self, args: list[str], context: dict) -> dict[str, Any]:
        """Mostra histórico de ciclos"""

        limit = int(args[0]) if args and args[0].isdigit() else 10

        reports = sorted(OPENCLAW_REPORTS_DIR.glob("cycle_*.json"), reverse=True)[:limit]

        if not reports:
            return {
                "response": "⚠️ Nenhum relatório histórico encontrado.",
                "intent": "openclaw_historico",
            }

        lines = [f"**📜 Últimos {len(reports)} Ciclos OpenClaw:**\n"]

        for report_path in reports:
            try:
                data = json.loads(report_path.read_text())
                cycle_id = data.get("cycle_id", "N/A")
                status = data.get("overall_status", "unknown").upper()
                duration = data.get("duration_seconds", 0)

                emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(status, "❓")

                lines.append(f"{emoji} {cycle_id} - {status} ({duration:.1f}s)")
            except Exception as e:
                logger.warning(f"Erro ao ler {report_path}: {e}")

        response = "\n".join(lines)

        return {
            "response": response,
            "intent": "openclaw_historico",
            "data": {"total": len(reports)},
            "suggestions": ["/openclaw report"],
        }

    async def _analyze(self, args: list[str], context: dict) -> dict[str, Any]:
        """🤖 Analisa falhas com IA e sugere correções."""

        latest_json = OPENCLAW_REPORTS_DIR / "latest.json"

        if not latest_json.exists():
            return {
                "response": "⚠️ Nenhum relatório encontrado para analisar.\n\nExecute `/openclaw ciclo` primeiro para gerar um relatório.",
                "intent": "openclaw_analyze",
                "suggestions": ["/openclaw ciclo", "/openclaw status"],
            }

        try:
            report = json.loads(latest_json.read_text())

            # Verifica se há problemas
            problems = [c for c in report["checks"] if c["status"] in ["fail", "error", "warn"]]

            if not problems:
                return {
                    "response": "✅ Nenhuma falha para analisar!\n\nTodos os checks passaram. Sistema está saudável.",
                    "intent": "openclaw_analyze",
                    "suggestions": ["/openclaw status"],
                }

            # Analisa com IA
            analyzer = OpenClawAnalyzer()
            analysis = await analyzer.analyze_failures(report)

            return {
                "response": analysis,
                "intent": "openclaw_analyze",
                "data": {"problems_count": len(problems), "cycle_id": report["cycle_id"]},
                "suggestions": ["/openclaw status", "/openclaw report"],
            }

        except Exception as e:
            logger.error(f"Erro ao analisar: {e}")
            return {
                "response": f"❌ Erro ao analisar relatório: {str(e)}\n\nTente novamente em alguns minutos.",
                "intent": "openclaw_analyze",
                "error": str(e),
            }

    async def _testes(self, args: list[str], context: dict) -> dict[str, Any]:
        """Redireciona para action OPENCLAW_RUN_TESTS"""
        return {
            "response": "Para executar testes, confirme a ação sugerida abaixo.",
            "intent": "openclaw_testes",
            "action_type": "openclaw_run_tests",
            "suggestions": ["Confirmar", "Cancelar"],
        }

    async def _testes_front(self, args: list[str], context: dict) -> dict[str, Any]:
        """Frontend tests"""
        return {
            "response": "⚠️ Testes frontend ainda não integrados ao OpenClaw. Use `npm run test` manualmente.",
            "intent": "openclaw_testes_front",
        }

    async def _lint(self, args: list[str], context: dict) -> dict[str, Any]:
        """Redireciona para action OPENCLAW_RUN_LINT"""
        return {
            "response": "Para executar lint, confirme a ação sugerida abaixo.",
            "intent": "openclaw_lint",
            "action_type": "openclaw_run_lint",
            "suggestions": ["Confirmar", "Cancelar"],
        }

    async def _security(self, args: list[str], context: dict) -> dict[str, Any]:
        """Redireciona para action OPENCLAW_RUN_SECURITY"""
        return {
            "response": "Para executar security scan, confirme a ação sugerida abaixo.",
            "intent": "openclaw_security",
            "action_type": "openclaw_run_security",
            "suggestions": ["Confirmar", "Cancelar"],
        }

    async def _coverage(self, args: list[str], context: dict) -> dict[str, Any]:
        """Redireciona para action OPENCLAW_RUN_COVERAGE"""
        return {
            "response": "Para verificar cobertura, confirme a ação sugerida abaixo.",
            "intent": "openclaw_coverage",
            "action_type": "openclaw_run_coverage",
            "suggestions": ["Confirmar", "Cancelar"],
        }

    async def _health(self, args: list[str], context: dict) -> dict[str, Any]:
        """Redireciona para action OPENCLAW_RUN_HEALTH"""
        return {
            "response": "Para executar health check, confirme a ação sugerida abaixo.",
            "intent": "openclaw_health",
            "action_type": "openclaw_run_health",
            "suggestions": ["Confirmar", "Cancelar"],
        }

    async def _ciclo(self, args: list[str], context: dict) -> dict[str, Any]:
        """Redireciona para action OPENCLAW_RUN_FULL_CYCLE"""
        return {
            "response": "Para executar ciclo completo, confirme a ação sugerida abaixo. Pode levar até 5 minutos.",
            "intent": "openclaw_ciclo",
            "action_type": "openclaw_run_full_cycle",
            "suggestions": ["Confirmar", "Cancelar"],
        }

    async def _deploy(self, args: list[str], context: dict) -> dict[str, Any]:
        """Redireciona para action OPENCLAW_DEPLOY"""
        env = args[0] if args else "production"

        if env == "staging":
            action_type = "openclaw_deploy_staging"
            msg = "Deploy para staging"
        else:
            action_type = "openclaw_deploy_production"
            msg = "⚠️ Deploy para PRODUÇÃO (ação crítica)"

        return {
            "response": f"{msg} - confirme a ação sugerida abaixo.",
            "intent": "openclaw_deploy",
            "action_type": action_type,
            "suggestions": ["Confirmar", "Cancelar"],
        }

    async def _config(self, args: list[str], context: dict) -> dict[str, Any]:
        """Mostra configuração do OpenClaw"""
        return {
            "response": """**⚙️ Configuração OpenClaw**

**Daemon:** Desativado
**Intervalo:** 1 hora
**Timeout:** 5 minutos por ciclo
**Relatórios:** /opt/conecta-pro/reports/openclaw/

Use `/openclaw daemon start` para ativar o modo automático.
""",
            "intent": "openclaw_config",
            "suggestions": ["/openclaw daemon start"],
        }

    async def _daemon(self, args: list[str], context: dict) -> dict[str, Any]:
        """Controla daemon"""
        action = args[0] if args else "status"

        if action == "start":
            return {
                "response": "Para iniciar o daemon OpenClaw, confirme a ação sugerida abaixo.",
                "intent": "openclaw_daemon_start",
                "action_type": "openclaw_daemon_start",
                "suggestions": ["Confirmar", "Cancelar"],
            }
        elif action == "stop":
            return {
                "response": "Para parar o daemon OpenClaw, confirme a ação sugerida abaixo.",
                "intent": "openclaw_daemon_stop",
                "action_type": "openclaw_daemon_stop",
                "suggestions": ["Confirmar", "Cancelar"],
            }
        else:
            return {
                "response": "**Daemon OpenClaw:** Desativado\n\nUse `/openclaw daemon start` para ativar.",
                "intent": "openclaw_daemon_status",
                "suggestions": ["/openclaw daemon start"],
            }
