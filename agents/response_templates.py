"""
Templates de resposta do Assistente Conecta PRO.

Usado pelo Telegram bot e pelo OpenClaw para gerar
mensagens padronizadas em portugues.
"""

from datetime import datetime


def _ts() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


# =============================================================================
# SISTEMA SAUDAVEL
# =============================================================================


def system_healthy(
    containers_total: int = 22,
    containers_healthy: int = 22,
    uptime_backend: str = "",
    uptime_db: str = "",
) -> str:
    return (
        f"✅ <b>Sistema Saudavel</b>\n"
        f"\n"
        f"Containers: {containers_healthy}/{containers_total} healthy\n"
        f"Backend: healthy{f' ({uptime_backend})' if uptime_backend else ''}\n"
        f"PostgreSQL: healthy{f' ({uptime_db})' if uptime_db else ''}\n"
        f"Redis: healthy\n"
        f"Celery: 7/7 workers\n"
        f"Frontend: online (PM2)\n"
        f"\n"
        f"<i>{_ts()}</i>"
    )


# =============================================================================
# CONTAINER DOWN
# =============================================================================


def container_down(
    container_name: str,
    role: str = "",
    last_status: str = "",
    action_taken: str = "",
    resolved: bool = False,
) -> str:
    icon = "✅" if resolved else "🔴"
    status = "RESOLVIDO" if resolved else "CONTAINER DOWN"

    lines = [
        f"{icon} <b>{status}: {container_name}</b>",
        "",
    ]

    if role:
        lines.append(f"Funcao: {role}")
    if last_status:
        lines.append(f"Ultimo status: {last_status}")
    if action_taken:
        lines.append(f"Acao: {action_taken}")

    lines.append("")
    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)


# =============================================================================
# ALERTA CRITICO
# =============================================================================


def critical_alert(
    alert_name: str,
    severity: str = "critical",
    diagnosis: str = "",
    actions: list[dict] | None = None,
    intervention_id: str = "",
    resolve_time_seconds: int = 0,
    resolved: bool = False,
) -> str:
    icon = "✅" if resolved else "🚨"
    status = "RESOLVIDO" if resolved else "CRITICO"

    lines = [
        f"{icon} <b>ALERTA {status}: {alert_name}</b>",
        f"Severidade: {severity}",
        "",
    ]

    if diagnosis:
        lines.append("<b>Diagnostico:</b>")
        for line in diagnosis.split("\n"):
            if line.strip():
                lines.append(f"  {line.strip()}")
        lines.append("")

    if actions:
        lines.append("<b>Acoes:</b>")
        for i, action in enumerate(actions, 1):
            step = action.get("step", "?")
            result = action.get("result", "?")
            ok = "OK" in str(result) or "PONG" in str(result) or "running" in str(result)
            icon_a = "✅" if ok else "⚠️"
            lines.append(f"  {i}. {icon_a} {step}: {result}")
        lines.append("")

    if resolve_time_seconds > 0:
        lines.append(f"Tempo de resolucao: {resolve_time_seconds}s")

    if intervention_id:
        lines.append(f"ID: <code>{intervention_id[:8]}</code>")

    lines.append("")
    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)


# =============================================================================
# TESTES COM FALHA
# =============================================================================


def test_failure(
    total_tests: int,
    passed: int,
    failed: int,
    errors: int = 0,
    coverage_pct: float = 0,
    failing_modules: list[str] | None = None,
) -> str:
    icon = "✅" if failed == 0 else "⚠️"
    lines = [
        f"{icon} <b>Resultado dos Testes</b>",
        "",
        f"Total: {total_tests}",
        f"✅ Passaram: {passed}",
    ]

    if failed > 0:
        lines.append(f"❌ Falharam: {failed}")
    if errors > 0:
        lines.append(f"💥 Erros: {errors}")
    if coverage_pct > 0:
        lines.append(f"📊 Cobertura: {coverage_pct:.1f}%")

    if failing_modules:
        lines.append("")
        lines.append("<b>Modulos afetados:</b>")
        for mod in failing_modules[:5]:
            lines.append(f"  - {mod}")

    lines.append("")
    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)


# =============================================================================
# BACKUP BEM-SUCEDIDO
# =============================================================================


def backup_success(
    filename: str,
    size: str = "",
    total_backups: int = 0,
    retention_days: int = 30,
) -> str:
    lines = [
        "✅ <b>Backup Concluido</b>",
        "",
        f"Arquivo: <code>{filename}</code>",
    ]

    if size:
        lines.append(f"Tamanho: {size}")
    if total_backups:
        lines.append(f"Total backups: {total_backups}")
    lines.append(f"Retencao: {retention_days} dias")

    lines.append("")
    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)


def backup_failure(error: str) -> str:
    return (
        f"🚨 <b>BACKUP FALHOU</b>\n"
        f"\n"
        f"Erro: {error[:200]}\n"
        f"\n"
        f"Acao necessaria: verificar logs em /var/log/conecta-backup.log\n"
        f"\n"
        f"<i>{_ts()}</i>"
    )


# =============================================================================
# ACAO EXECUTADA COM SUCESSO
# =============================================================================


def action_success(
    action_name: str,
    details: str = "",
    duration_seconds: int = 0,
) -> str:
    lines = [
        f"✅ <b>Acao Executada: {action_name}</b>",
        "",
    ]

    if details:
        lines.append(details)
    if duration_seconds > 0:
        lines.append(f"Duracao: {duration_seconds}s")

    lines.append("")
    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)


# =============================================================================
# ACAO NEGADA POR SEGURANCA
# =============================================================================


def action_denied(
    action_name: str,
    reason: str,
    zone: str = "",
) -> str:
    lines = [
        f"🛑 <b>Acao Negada: {action_name}</b>",
        "",
        f"Motivo: {reason}",
    ]

    if zone:
        lines.append(f"Zona: {zone} (protegida)")

    lines.append("")
    lines.append("Para executar, confirme explicitamente com /confirm")
    lines.append("")
    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)


def action_denied_peak_hours(action_name: str) -> str:
    return action_denied(
        action_name=action_name,
        reason="Horario de pico (07:00-09:00 ou 17:00-19:00 BRT). "
        "Deploys e restarts nao sao permitidos nesses horarios.",
    )


def action_denied_fiscal_zone(action_name: str) -> str:
    return action_denied(
        action_name=action_name,
        reason="Modulo fiscal/governamental protegido. "
        "Alteracoes requerem autorizacao explicita do CEO.",
        zone="financial / government_integrations",
    )


# =============================================================================
# DEPLOY STATUS
# =============================================================================


def deploy_status(
    component: str,
    stage: str,
    success: bool = True,
    details: str = "",
) -> str:
    icon = "✅" if success else "❌"
    lines = [
        f"{icon} <b>Deploy {component}: {stage}</b>",
    ]

    if details:
        lines.append(details)

    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)


# =============================================================================
# PADRAO APRENDIDO
# =============================================================================


def pattern_learned(
    pattern_name: str,
    confidence: float,
    frequency: int,
    avg_resolve_time: int = 0,
) -> str:
    return (
        f"🧠 <b>Padrao Aprendido</b>\n"
        f"\n"
        f"Nome: <code>{pattern_name}</code>\n"
        f"Confianca: {confidence:.0%}\n"
        f"Frequencia: {frequency}x\n"
        f"Tempo medio resolucao: {avg_resolve_time}s\n"
        f"\n"
        f"{'✅ Auto-acao habilitada' if confidence >= 0.8 else '⏳ Precisa mais episodios para auto-acao'}\n"
        f"\n"
        f"<i>{_ts()}</i>"
    )


# =============================================================================
# RELATORIO DIARIO
# =============================================================================


def daily_report(
    containers_healthy: int,
    containers_total: int,
    alerts_today: int,
    alerts_resolved: int,
    backup_ok: bool,
    disk_pct: int,
    memory_pct: int,
    patterns_learned: int = 0,
    interventions_today: int = 0,
) -> str:
    lines = [
        "📊 <b>Relatorio Diario — Conecta PRO</b>",
        "",
        f"🖥 Containers: {containers_healthy}/{containers_total} healthy",
        f"🚨 Alertas hoje: {alerts_today} ({alerts_resolved} resolvidos)",
        f"💾 Backup: {'✅ OK' if backup_ok else '❌ FALHOU'}",
        f"💿 Disco: {disk_pct}% usado",
        f"🧠 Memoria: {memory_pct}% usada",
    ]

    if patterns_learned > 0:
        lines.append(f"🤖 Padroes aprendidos: {patterns_learned}")
    if interventions_today > 0:
        lines.append(f"🔧 Intervencoes OpenClaw: {interventions_today}")

    lines.append("")
    lines.append(f"<i>{_ts()}</i>")
    return "\n".join(lines)
