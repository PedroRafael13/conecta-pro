"""
OpenClaw Alert Webhook Controller.

Recebe alertas do Alertmanager, executa diagnóstico automático,
toma ações corretivas e notifica via Telegram.
"""

import time
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from loguru import logger
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.session import get_db

from . import memory_service, telegram_service
from .models import Intervention, InterventionSeverity, InterventionStatus
from .remediation_service import RemediationService
from .schemas import AlertmanagerPayload, InterventionResponse

router = APIRouter(prefix="/openclaw", tags=["AI - OpenClaw Alert Response"])

remediation = RemediationService()


@router.post("/alert-webhook", response_model=list[InterventionResponse])
async def receive_alert_webhook(
    payload: AlertmanagerPayload,
    db: AsyncSession = Depends(get_db),
):
    """
    Webhook para o Alertmanager.

    Recebe alertas, executa diagnóstico, toma ações e notifica via Telegram.
    Cada alerta gera um registro de intervenção (memória episódica).
    """
    logger.info(f"OpenClaw webhook: status={payload.status}, alerts={len(payload.alerts)}, receiver={payload.receiver}")

    results = []

    for alert in payload.alerts:
        # Ignorar alertas resolvidos (Alertmanager já notifica via Telegram nativo)
        if alert.status == "resolved":
            logger.info(f"Alerta resolvido ignorado: {alert.labels.alertname}")
            continue

        alert_name = alert.labels.alertname
        severity = alert.labels.severity or "warning"
        start_time = time.time()

        # Criar registro de intervenção
        intervention = Intervention(
            id=uuid.uuid4(),
            alert_name=alert_name,
            alert_fingerprint=alert.fingerprint,
            severity=InterventionSeverity(severity.lower())
            if severity.lower() in [s.value for s in InterventionSeverity]
            else InterventionSeverity.WARNING,
            status=InterventionStatus.DIAGNOSING,
            raw_payload={
                "status": alert.status,
                "labels": alert.labels.model_dump(),
                "annotations": alert.annotations.model_dump(),
                "startsAt": alert.startsAt,
                "fingerprint": alert.fingerprint,
            },
        )
        db.add(intervention)
        await db.flush()  # Para obter o ID

        logger.info(f"OpenClaw intervenção {intervention.id}: diagnosticando {alert_name}")

        try:
            # 1. Consultar memoria episodica — solucao cached?
            cached_pattern = await memory_service.find_matching_pattern(db, alert_name)

            if cached_pattern and cached_pattern.auto_action:
                logger.info(
                    f"OpenClaw: padrao encontrado '{cached_pattern.pattern_name}' "
                    f"(confianca: {cached_pattern.confidence_score:.0%}) — usando solucao cached"
                )
                diagnosis = cached_pattern.diagnosis_template or f"Padrao conhecido: {cached_pattern.pattern_name}"
                actions = cached_pattern.auto_action if isinstance(cached_pattern.auto_action, list) else []
                intervention.used_cached_solution = True

                # Re-executar as acoes do padrao
                intervention.status = InterventionStatus.ACTING
                _, fresh_actions = await remediation.diagnose_and_act(
                    alert_name=alert_name,
                    severity=severity,
                    annotations=alert.annotations.model_dump(),
                )
                actions = fresh_actions
            else:
                # 2. Buscar episodios anteriores para contexto
                similar = await memory_service.find_similar_episodes(db, alert_name, limit=3)
                if similar:
                    logger.info(f"OpenClaw: {len(similar)} episodios similares encontrados para contexto")

                # 3. Sem padrao cached — diagnostico completo
                intervention.status = InterventionStatus.ACTING
                diagnosis, actions = await remediation.diagnose_and_act(
                    alert_name=alert_name,
                    severity=severity,
                    annotations=alert.annotations.model_dump(),
                )

            elapsed = int(time.time() - start_time)

            # Determinar status final
            has_restart = any(a.get("step", "").startswith("restart") for a in actions)
            post_check_ok = any(
                a.get("step", "").startswith("post_restart") and "OK" in str(a.get("result", "")) for a in actions
            )
            failed_post = any(
                a.get("step", "").startswith("post_restart") and "FALHA" in str(a.get("result", "")) for a in actions
            )

            if failed_post:
                final_status = InterventionStatus.ESCALATED
            elif has_restart and post_check_ok:
                final_status = InterventionStatus.RESOLVED
            elif not has_restart:
                # Diagnóstico sem restart necessário = resolved (informativo)
                final_status = InterventionStatus.RESOLVED
            else:
                final_status = InterventionStatus.ACTING

            intervention.status = final_status
            intervention.diagnosis = diagnosis
            intervention.actions_taken = actions
            intervention.response_time_seconds = elapsed
            if final_status == InterventionStatus.RESOLVED:
                intervention.resolved_at = datetime.now(UTC)
                intervention.resolution = "Resolvido automaticamente pelo OpenClaw"

            # Notificar via Telegram
            msg_id = await telegram_service.send_diagnosis(
                alert_name=alert_name,
                severity=severity,
                status=final_status.value,
                diagnosis=diagnosis,
                actions=actions,
                intervention_id=str(intervention.id),
            )
            intervention.telegram_sent = msg_id is not None
            intervention.telegram_message_id = msg_id

            logger.info(
                f"OpenClaw intervenção {intervention.id}: "
                f"status={final_status}, tempo={elapsed}s, "
                f"cached={'sim' if intervention.used_cached_solution else 'nao'}, "
                f"telegram={'sim' if msg_id else 'nao'}"
            )

            # 4. Registrar aprendizado se resolvido
            if final_status == InterventionStatus.RESOLVED:
                root_cause = _extract_root_cause(diagnosis, actions)
                await memory_service.record_learning(
                    db=db,
                    intervention=intervention,
                    root_cause=root_cause,
                    learned_pattern=f"{alert_name}:{root_cause}",
                    prevention_action=_suggest_prevention(alert_name, root_cause),
                )

        except Exception as e:
            intervention.status = InterventionStatus.FAILED
            intervention.diagnosis = f"Erro durante remediação: {str(e)[:500]}"
            intervention.response_time_seconds = int(time.time() - start_time)
            logger.error(f"OpenClaw falha na intervenção {intervention.id}: {e}")

        await db.commit()
        await db.refresh(intervention)

        results.append(
            InterventionResponse(
                intervention_id=str(intervention.id),
                alert_name=alert_name,
                status=intervention.status.value,
                diagnosis=intervention.diagnosis,
                actions_taken=[a.get("step", "") for a in (intervention.actions_taken or [])],
                telegram_sent=intervention.telegram_sent,
            )
        )

    return results


@router.get("/interventions")
async def list_interventions(
    limit: int = Query(default=20, le=100),
    alert_name: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Lista intervenções recentes (memória episódica)."""
    query = select(Intervention).order_by(desc(Intervention.created_at)).limit(limit)

    if alert_name:
        query = query.where(Intervention.alert_name == alert_name)
    if status:
        query = query.where(Intervention.status == status)

    result = await db.execute(query)
    interventions = result.scalars().all()

    return [
        {
            "id": str(i.id),
            "alert_name": i.alert_name,
            "severity": i.severity.value if i.severity else None,
            "status": i.status.value if i.status else None,
            "diagnosis": i.diagnosis,
            "actions_taken": i.actions_taken,
            "resolution": i.resolution,
            "response_time_seconds": i.response_time_seconds,
            "telegram_sent": i.telegram_sent,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
        }
        for i in interventions
    ]


@router.get("/interventions/stats")
async def intervention_stats(db: AsyncSession = Depends(get_db)):
    """Estatísticas das intervenções."""
    from sqlalchemy import func as sqlfunc

    result = await db.execute(select(sqlfunc.count(Intervention.id)))
    total = result.scalar() or 0

    result = await db.execute(
        select(sqlfunc.count(Intervention.id)).where(Intervention.status == InterventionStatus.RESOLVED)
    )
    resolved = result.scalar() or 0

    result = await db.execute(
        select(sqlfunc.avg(Intervention.response_time_seconds)).where(Intervention.response_time_seconds.isnot(None))
    )
    avg_time = result.scalar()

    result = await db.execute(
        select(Intervention.alert_name, sqlfunc.count(Intervention.id))
        .group_by(Intervention.alert_name)
        .order_by(sqlfunc.count(Intervention.id).desc())
        .limit(10)
    )
    by_alert = [{"alert_name": row[0], "count": row[1]} for row in result.all()]

    # Padroes aprendidos
    from .models import AgentPattern

    pattern_result = await db.execute(
        select(sqlfunc.count(AgentPattern.id)).where(AgentPattern.is_active == True)  # noqa: E712
    )
    total_patterns = pattern_result.scalar() or 0

    cached_result = await db.execute(
        select(sqlfunc.count(Intervention.id)).where(Intervention.used_cached_solution == True)  # noqa: E712
    )
    cached_solutions = cached_result.scalar() or 0

    return {
        "total_interventions": total,
        "resolved": resolved,
        "resolution_rate": round(resolved / total * 100, 1) if total > 0 else 0,
        "avg_response_time_seconds": round(avg_time, 1) if avg_time else None,
        "by_alert": by_alert,
        "patterns_learned": total_patterns,
        "cached_solutions_used": cached_solutions,
    }


# =============================================================================
# HELPERS
# =============================================================================


def _extract_root_cause(diagnosis: str, actions: list[dict]) -> str:
    """Extrai causa raiz a partir do diagnostico e acoes."""
    if not diagnosis:
        return "unknown"

    # Heuristicas simples baseadas em keywords
    keywords = {
        "permiss": "permission_error",
        "disco": "disk_space",
        "memoria": "memory_pressure",
        "timeout": "timeout",
        "conexao": "connection_failure",
        "reinici": "service_crash",
        "unhealthy": "health_check_failure",
        "lock": "lock_contention",
        "cpu": "cpu_saturation",
    }
    diag_lower = diagnosis.lower()
    for keyword, cause in keywords.items():
        if keyword in diag_lower:
            return cause

    return "resolved_no_root_cause"


def _suggest_prevention(alert_name: str, root_cause: str) -> str:
    """Sugere acao preventiva com base no alerta e causa raiz."""
    suggestions = {
        "permission_error": "Verificar ownership de /app/logs/ no Dockerfile (USER erp)",
        "disk_space": "Configurar logrotate mais agressivo ou expandir disco",
        "memory_pressure": "Revisar pool_size do SQLAlchemy ou limits no docker-compose",
        "timeout": "Aumentar timeout no nginx ou uvicorn",
        "connection_failure": "Verificar pool_pre_ping e pool_recycle no SQLAlchemy",
        "service_crash": "Verificar logs de startup e dependencias entre containers",
        "health_check_failure": "Revisar start_period do healthcheck",
        "cpu_saturation": "Escalar workers ou otimizar queries lentas",
    }
    return suggestions.get(root_cause, f"Monitorar recorrencia de {alert_name}")
