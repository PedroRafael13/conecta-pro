"""
Notification Service for OpenClaw.

Sends notifications to Discord, Email, Slack, etc when quality checks fail.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import logging
from datetime import datetime

import aiohttp

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço de notificações (Discord, Email, Slack, etc)."""

    def __init__(self, discord_webhook_url: str | None = None):
        """
        Initialize notification service.

        Args:
            discord_webhook_url: Discord webhook URL for notifications
        """
        self.discord_webhook = discord_webhook_url

    async def send_discord(self, report: dict) -> bool:
        """
        Envia notificação para Discord via webhook.

        Args:
            report: Relatório OpenClaw completo

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.discord_webhook:
            logger.warning("Discord webhook não configurado")
            return False

        # Monta embed
        embed = self._build_discord_embed(report)

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    self.discord_webhook, json={"embeds": [embed]}, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp,
            ):
                if resp.status == 204:
                    logger.info("Notificação Discord enviada com sucesso")
                    return True
                else:
                    logger.warning(f"Discord webhook retornou status {resp.status}")
                    return False
        except aiohttp.ClientError as e:
            logger.error(f"Erro ao conectar ao Discord: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Discord: {e}")
            return False

    def _build_discord_embed(self, report: dict) -> dict:
        """
        Constrói Discord embed com formatação rica.

        Args:
            report: Relatório OpenClaw

        Returns:
            Discord embed dict
        """
        status = report.get("overall_status", "unknown")

        # Cores baseadas em status
        colors = {
            "pass": 0x00FF00,  # Verde
            "fail": 0xFF0000,  # Vermelho
            "warn": 0xFFA500,  # Laranja
            "error": 0x8B0000,  # Vermelho escuro
        }

        # Emojis
        emojis = {"pass": "✅", "fail": "❌", "warn": "⚠️", "error": "🔴"}

        # Monta campos
        summary = report.get("summary", {})
        counts = summary.get("status_counts", {})

        fields = [
            {"name": "⏱️ Duração", "value": f"{report.get('duration_seconds', 0):.1f}s", "inline": True},
            {
                "name": "📊 Resultados",
                "value": (
                    f"✅ Pass: {counts.get('pass', 0)}\n"
                    f"❌ Fail: {counts.get('fail', 0)}\n"
                    f"⚠️ Warn: {counts.get('warn', 0)}\n"
                    f"🔴 Error: {counts.get('error', 0)}"
                ),
                "inline": True,
            },
        ]

        # Health Score (se disponível)
        health_score = report.get("health_score")
        if health_score is not None:
            fields.append({"name": "💯 Health Score", "value": f"{health_score}/100", "inline": True})

        # Adiciona falhas críticas
        critical_checks = [c for c in report.get("checks", []) if c.get("status") in ["fail", "error"]]

        if critical_checks:
            failures = "\n".join(
                [f"❌ {c.get('name', 'Unknown')}: {c.get('message', '')[:50]}" for c in critical_checks[:5]]
            )

            if len(critical_checks) > 5:
                failures += f"\n... e mais {len(critical_checks) - 5} falhas"

            fields.append({"name": "🚨 Falhas Críticas", "value": failures, "inline": False})

        # Link para relatório (se em produção)
        cycle_id = report.get("cycle_id", "N/A")
        fields.append(
            {
                "name": "📋 Relatório",
                "value": f"Ciclo: `{cycle_id}`\nVeja detalhes no dashboard OpenClaw",
                "inline": False,
            }
        )

        return {
            "title": f"{emojis.get(status, '❓')} OpenClaw - {status.upper()}",
            "description": f"**Quality Monitor - Conecta PRO**\n{report.get('environment', 'production').upper()}",
            "color": colors.get(status, 0x808080),
            "fields": fields,
            "timestamp": report.get("timestamp", datetime.utcnow().isoformat()),
            "footer": {
                "text": "OpenClaw Quality Monitor",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/5968/5968866.png",
            },
        }

    def should_notify(self, report: dict, last_report: dict | None = None) -> bool:
        """
        Decide se deve enviar notificação.

        Notifica quando:
        1. Status é fail ou error
        2. Status mudou do último relatório
        3. Há checks críticos falhando (security, health)

        Args:
            report: Relatório atual
            last_report: Relatório anterior (opcional)

        Returns:
            True se deve notificar
        """
        status = report.get("overall_status", "unknown")

        # Sempre notifica em fail ou error
        if status in ["fail", "error"]:
            return True

        # Notifica se status mudou
        if last_report:
            last_status = last_report.get("overall_status")
            if last_status and last_status != status:
                logger.info(f"Status mudou de {last_status} para {status} - notificando")
                return True

        # Notifica se há checks críticos falhando
        critical_check_names = ["security_bandit", "health_check", "backend_tests"]
        critical_failures = [
            c
            for c in report.get("checks", [])
            if c.get("name") in critical_check_names and c.get("status") in ["fail", "error"]
        ]

        if critical_failures:
            logger.info(f"{len(critical_failures)} checks críticos falharam - notificando")
            return True

        return False
