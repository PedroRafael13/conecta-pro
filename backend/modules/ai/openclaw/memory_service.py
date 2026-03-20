"""
Servico de memoria do OpenClaw.

Consulta episodios anteriores, aprende padroes e decide
se pode agir sem LLM (solucao cached) ou precisa chamar IA.
"""

import uuid
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import AgentKnowledgeBase, AgentPattern, Intervention, InterventionStatus

# Threshold de confianca para agir sem LLM
CONFIDENCE_THRESHOLD = 0.80
# Minimo de episodios resolvidos para criar padrao
MIN_EPISODES_FOR_PATTERN = 3


async def find_similar_episodes(db: AsyncSession, alert_name: str, limit: int = 5) -> list[Intervention]:
    """Busca episodios anteriores do mesmo alerta que foram resolvidos."""
    result = await db.execute(
        select(Intervention)
        .where(
            Intervention.alert_name == alert_name,
            Intervention.status == InterventionStatus.RESOLVED,
        )
        .order_by(desc(Intervention.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def find_matching_pattern(db: AsyncSession, alert_name: str) -> AgentPattern | None:
    """Busca padrao aprendido com confianca suficiente para auto-acao."""
    result = await db.execute(
        select(AgentPattern)
        .where(
            AgentPattern.alert_name == alert_name,
            AgentPattern.is_active == True,  # noqa: E712
            AgentPattern.confidence_score >= CONFIDENCE_THRESHOLD,
        )
        .order_by(desc(AgentPattern.confidence_score))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_component_knowledge(db: AsyncSession, component: str) -> AgentKnowledgeBase | None:
    """Busca conhecimento sobre um componente do sistema."""
    result = await db.execute(select(AgentKnowledgeBase).where(AgentKnowledgeBase.component == component))
    return result.scalar_one_or_none()


async def record_learning(
    db: AsyncSession,
    intervention: Intervention,
    root_cause: str,
    learned_pattern: str,
    prevention_action: str,
) -> None:
    """Registra aprendizado apos resolucao de um incidente."""
    intervention.root_cause = root_cause
    intervention.learned_pattern = learned_pattern
    intervention.prevention_action = prevention_action

    # Atualizar ou criar padrao
    await _update_pattern(db, intervention, root_cause, learned_pattern)

    # Atualizar knowledge base do componente
    component = _extract_component(intervention.alert_name)
    await _update_knowledge(db, component, intervention)

    logger.info(
        f"OpenClaw aprendizado registrado: alert={intervention.alert_name}, "
        f"root_cause={root_cause[:50]}, pattern={learned_pattern[:50]}"
    )


async def _update_pattern(
    db: AsyncSession,
    intervention: Intervention,
    root_cause: str,
    learned_pattern: str,
) -> None:
    """Atualiza ou cria padrao a partir de intervencoes repetidas."""
    alert_name = intervention.alert_name
    pattern_name = f"{alert_name}:{root_cause[:100]}"

    # Buscar padrao existente
    result = await db.execute(select(AgentPattern).where(AgentPattern.pattern_name == pattern_name))
    pattern = result.scalar_one_or_none()

    if pattern:
        # Atualizar padrao existente
        pattern.frequency += 1
        pattern.last_seen = datetime.now(UTC)
        pattern.auto_action = intervention.actions_taken
        pattern.diagnosis_template = intervention.diagnosis

        # Calcular media do tempo de resolucao
        if intervention.response_time_seconds:
            if pattern.avg_resolve_time_seconds:
                pattern.avg_resolve_time_seconds = (
                    pattern.avg_resolve_time_seconds + intervention.response_time_seconds
                ) // 2
            else:
                pattern.avg_resolve_time_seconds = intervention.response_time_seconds

        # Aumentar confianca com base na frequencia
        pattern.confidence_score = min(1.0, pattern.frequency / (pattern.frequency + 2))
    else:
        # Contar episodios resolvidos deste alerta
        count_result = await db.execute(
            select(func.count(Intervention.id)).where(
                Intervention.alert_name == alert_name,
                Intervention.status == InterventionStatus.RESOLVED,
            )
        )
        episode_count = count_result.scalar() or 0

        if episode_count >= MIN_EPISODES_FOR_PATTERN:
            pattern = AgentPattern(
                id=uuid.uuid4(),
                pattern_name=pattern_name,
                alert_name=alert_name,
                trigger_conditions={"severity": intervention.severity.value if intervention.severity else "warning"},
                frequency=1,
                last_seen=datetime.now(UTC),
                confidence_score=0.3,
                auto_action=intervention.actions_taken,
                diagnosis_template=intervention.diagnosis,
                avg_resolve_time_seconds=intervention.response_time_seconds,
            )
            db.add(pattern)
            logger.info(f"OpenClaw novo padrao criado: {pattern_name} (confianca: 0.3)")


async def _update_knowledge(db: AsyncSession, component: str, intervention: Intervention) -> None:
    """Atualiza knowledge base do componente afetado."""
    result = await db.execute(select(AgentKnowledgeBase).where(AgentKnowledgeBase.component == component))
    kb = result.scalar_one_or_none()

    if kb:
        # Adicionar issue ao historico
        issues = kb.known_issues or []
        issues.append(
            {
                "date": datetime.now(UTC).isoformat(),
                "alert": intervention.alert_name,
                "root_cause": intervention.root_cause,
                "resolution_time_s": intervention.response_time_seconds,
            }
        )
        # Manter apenas ultimos 20 issues
        kb.known_issues = issues[-20:]
        kb.last_incident_at = datetime.now(UTC)
    else:
        kb = AgentKnowledgeBase(
            id=uuid.uuid4(),
            component=component,
            known_issues=[
                {
                    "date": datetime.now(UTC).isoformat(),
                    "alert": intervention.alert_name,
                    "root_cause": intervention.root_cause,
                    "resolution_time_s": intervention.response_time_seconds,
                }
            ],
            criticality_level=_severity_to_criticality(
                intervention.severity.value if intervention.severity else "warning"
            ),
            last_incident_at=datetime.now(UTC),
        )
        db.add(kb)


def _extract_component(alert_name: str) -> str:
    """Extrai componente do nome do alerta."""
    mapping = {
        "Postgres": "postgresql",
        "Redis": "redis",
        "Celery": "celery",
        "Disk": "filesystem",
        "Memory": "system",
        "Load": "system",
        "SSL": "ssl",
        "Backup": "backup",
        "PM2": "frontend",
        "ERP": "backend",
    }
    for prefix, component in mapping.items():
        if prefix in alert_name:
            return component
    return "unknown"


def _severity_to_criticality(severity: str) -> str:
    return {"critical": "high", "warning": "medium", "info": "low"}.get(severity, "medium")
