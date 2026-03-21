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
from .schemas import AlertmanagerPayload, FeedbackRequest, FeedbackResponse, InterventionResponse

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
                # Restart executado mas post-check inconclusivo (sem OK nem FALHA)
                # Marcar como escalated em vez de ficar preso em acting
                final_status = InterventionStatus.ESCALATED

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
# KNOWLEDGE & PATTERNS — Visualização do conhecimento acumulado
# =============================================================================


@router.get("/knowledge")
async def get_knowledge_base(
    component: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Visualiza o conhecimento acumulado sobre componentes do sistema."""
    from .models import AgentKnowledgeBase

    query = select(AgentKnowledgeBase).where(AgentKnowledgeBase.is_active == True)  # noqa: E712
    if component:
        query = query.where(AgentKnowledgeBase.component.ilike(f"%{component}%"))
    query = query.order_by(AgentKnowledgeBase.component)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": len(items),
        "components": [
            {
                "id": str(kb.id),
                "component": kb.component,
                "criticality_level": kb.criticality_level,
                "known_issues": kb.known_issues,
                "dependencies": kb.dependencies,
                "peak_hours": kb.peak_hours,
                "runbook": kb.runbook,
                "last_incident_at": kb.last_incident_at.isoformat() if kb.last_incident_at else None,
                "updated_at": kb.updated_at.isoformat() if kb.updated_at else None,
            }
            for kb in items
        ],
    }


@router.get("/patterns")
async def get_patterns(
    alert_name: str | None = None,
    min_confidence: float = Query(default=0.0, ge=0, le=100),
    human_validated_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Visualiza padrões aprendidos pelo OpenClaw."""
    from .models import AgentPattern

    query = select(AgentPattern).where(AgentPattern.is_active == True)  # noqa: E712

    if alert_name:
        query = query.where(AgentPattern.alert_name.ilike(f"%{alert_name}%"))
    if min_confidence > 0:
        query = query.where(AgentPattern.confidence_score >= min_confidence / 100.0)
    if human_validated_only:
        query = query.where(AgentPattern.human_validated == True)  # noqa: E712

    query = query.order_by(desc(AgentPattern.confidence_score))
    result = await db.execute(query)
    patterns = result.scalars().all()

    return {
        "total": len(patterns),
        "patterns": [
            {
                "id": str(p.id),
                "pattern_name": p.pattern_name,
                "alert_name": p.alert_name,
                "confidence_score": round(
                    p.confidence_score if p.confidence_score <= 100 else p.confidence_score / 100, 1
                ),
                "frequency": p.frequency,
                "trigger_conditions": p.trigger_conditions,
                "auto_action": p.auto_action,
                "diagnosis_template": p.diagnosis_template,
                "avg_resolve_time_seconds": p.avg_resolve_time_seconds,
                "human_validated": p.human_validated,
                "validated_by": p.validated_by,
                "validated_at": p.validated_at.isoformat() if p.validated_at else None,
                "last_seen": p.last_seen.isoformat() if p.last_seen else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in patterns
        ],
    }


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    body: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Feedback humano sobre uma intervenção.

    Quando aprovada (approved=true):
    - Marca a intervenção como human_validated
    - Se houver um padrão associado, sobe confidence_score para 95%
    - O padrão fica marcado como human_validated

    Quando rejeitada (approved=false):
    - Registra o feedback para análise
    - Reduz confidence_score do padrão associado em 20%
    """
    from .models import AgentPattern

    now = datetime.now(UTC)

    # Buscar intervenção
    result = await db.execute(select(Intervention).where(Intervention.id == body.intervention_id))
    intervention = result.scalar_one_or_none()

    if not intervention:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Intervencao {body.intervention_id} nao encontrada")

    # Marcar intervenção
    intervention.human_validated = body.approved
    intervention.human_feedback = body.feedback or ("Aprovado" if body.approved else "Rejeitado")
    intervention.validated_at = now
    intervention.validated_by = body.validated_by

    # Buscar padrão associado (se houver)
    confidence_updated = False
    pattern_name = None
    new_confidence = None

    if intervention.learned_pattern:
        result = await db.execute(select(AgentPattern).where(AgentPattern.pattern_name == intervention.learned_pattern))
        pattern = result.scalar_one_or_none()

        if pattern:
            pattern_name = pattern.pattern_name

            if body.approved:
                # Validação positiva: confidence sobe para 95%
                pattern.confidence_score = 0.95
                pattern.human_validated = True
                pattern.validated_at = now
                pattern.validated_by = body.validated_by
                new_confidence = 95.0
                confidence_updated = True
                logger.info(
                    f"OpenClaw feedback: padrao '{pattern_name}' validado por {body.validated_by}, confidence → 95%"
                )
            else:
                # Validação negativa: confidence cai 20%
                pattern.confidence_score = max(0.0, pattern.confidence_score - 0.20)
                pattern.human_validated = False
                new_confidence = round(pattern.confidence_score * 100, 1)
                confidence_updated = True
                logger.info(
                    f"OpenClaw feedback: padrao '{pattern_name}' rejeitado por {body.validated_by}, "
                    f"confidence → {new_confidence}%"
                )

    await db.commit()

    status_text = "aprovada" if body.approved else "rejeitada"
    message = f"Intervencao {status_text} por {body.validated_by}."
    if confidence_updated:
        message += f" Padrao '{pattern_name}' atualizado para {new_confidence}%."

    return FeedbackResponse(
        intervention_id=body.intervention_id,
        human_validated=body.approved,
        confidence_updated=confidence_updated,
        pattern_name=pattern_name,
        new_confidence=new_confidence,
        message=message,
    )


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
