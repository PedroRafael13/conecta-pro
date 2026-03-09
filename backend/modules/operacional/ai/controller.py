"""
Controller de AI Command Center Operacional.

Author: Conecta PRO Team
Date: 2026-03-09
"""

import logging
from datetime import date, timedelta
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.operacional.models import Post

from .agents import (
    Bartolo3Agent,
    CostPredictorAgent,
    CoveragePredictorAgent,
    FieldMonitorAgent,
    IncidentClassifierAgent,
    PerformanceAnalyzerAgent,
    PredictiveAnalyzer,
)

logger = logging.getLogger(__name__)

ai_router = APIRouter(prefix="/ai", tags=["Operacional - AI Command Center"])

_coverage_agent = CoveragePredictorAgent()
_performance_agent = PerformanceAnalyzerAgent()
_predictive_agent = PredictiveAnalyzer()
_field_monitor = FieldMonitorAgent()
_incident_classifier = IncidentClassifierAgent()
_bartolo = Bartolo3Agent()
_cost_predictor = CostPredictorAgent()


@ai_router.get("/command-center")
async def get_command_center_data(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Retorna dados consolidados para o AI Command Center Operacional.

    Agrega informações de todos os agentes de IA para um dashboard
    unificado de inteligência operacional.
    """
    try:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Contar postos ativos
        posts_count = await db.scalar(select(func.count()).select_from(Post).where(Post.is_active)) or 0

        # Previsão de cobertura para amanhã
        tomorrow = today + timedelta(days=1)
        coverage_risks = await _coverage_agent.predict_coverage(tomorrow)
        high_risks = [r for r in coverage_risks if r.risk_percentage > 40]

        # Mapa de risco semanal
        weekly_map = await _coverage_agent.generate_weekly_risk_map(week_start)

        # Status geral
        active_alerts = len(high_risks)
        coverage_score = weekly_map.overall_coverage_probability

        return {
            "status": "operational",
            "generated_at": today.isoformat(),
            "overview": {
                "posts_active": posts_count,
                "coverage_score": coverage_score,
                "active_alerts": active_alerts,
                "high_risk_shifts_tomorrow": len(high_risks),
            },
            "coverage_prediction": {
                "date": tomorrow.isoformat(),
                "risks": [
                    {
                        "post_name": r.post_name,
                        "shift_type": r.shift_type,
                        "risk_percentage": r.risk_percentage,
                        "risk_level": r.risk_level,
                        "risk_factors": r.risk_factors,
                    }
                    for r in coverage_risks[:5]
                ],
            },
            "weekly_risk_map": {
                "week_start": weekly_map.week_start.isoformat(),
                "week_end": weekly_map.week_end.isoformat(),
                "coverage_probability": weekly_map.overall_coverage_probability,
                "high_risk_count": len(weekly_map.high_risk_shifts),
                "recommended_actions": weekly_map.recommended_actions,
                "summary": weekly_map.summary,
            },
            "agents_status": {
                "scale_optimizer": "active",
                "coverage_predictor": "active",
                "performance_analyzer": "active",
                "substitution_optimizer": "active",
                "occurrence_analyzer": "active",
                "predictive_analyzer": "active",
            },
        }
    except Exception as exc:
        logger.error("Erro no AI Command Center: %s", exc)
        return {
            "status": "degraded",
            "generated_at": date.today().isoformat(),
            "overview": {
                "posts_active": 0,
                "coverage_score": 0,
                "active_alerts": 0,
                "high_risk_shifts_tomorrow": 0,
            },
            "coverage_prediction": {"date": date.today().isoformat(), "risks": []},
            "weekly_risk_map": {
                "week_start": date.today().isoformat(),
                "week_end": date.today().isoformat(),
                "coverage_probability": 0,
                "high_risk_count": 0,
                "recommended_actions": [],
                "summary": "Sistema em modo degradado",
            },
            "agents_status": {},
        }


@ai_router.get("/coverage-prediction")
async def get_coverage_prediction(
    target_date: str | None = Query(None, description="Data YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Previsão detalhada de cobertura para uma data específica.
    """
    try:
        if target_date:
            pred_date = date.fromisoformat(target_date)
        else:
            pred_date = date.today() + timedelta(days=1)

        risks = await _coverage_agent.predict_coverage(pred_date)
        weekly = await _coverage_agent.generate_weekly_risk_map(pred_date - timedelta(days=pred_date.weekday()))

        return {
            "date": pred_date.isoformat(),
            "overall_coverage_probability": weekly.overall_coverage_probability,
            "risks": [
                {
                    "post_name": r.post_name,
                    "shift_type": r.shift_type,
                    "risk_percentage": r.risk_percentage,
                    "risk_level": r.risk_level,
                    "risk_factors": r.risk_factors,
                    "contingency_options": r.contingency_options,
                }
                for r in risks
            ],
            "weekly_summary": weekly.summary,
            "recommended_actions": weekly.recommended_actions,
        }
    except Exception as exc:
        logger.error("Erro na previsão de cobertura: %s", exc)
        return {
            "date": date.today().isoformat(),
            "overall_coverage_probability": 0,
            "risks": [],
            "weekly_summary": "Erro ao calcular previsão",
            "recommended_actions": [],
        }


@ai_router.get("/performance-overview")
async def get_performance_overview(
    period_days: int = Query(90, ge=30, le=365),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Visão geral de performance da equipe.
    """
    try:
        # Simular dados de performance (em produção: consulta banco)
        sample_employees = [
            {
                "id": str(uuid4()),
                "name": "Pedro Santos",
                "absences": 0,
                "lates": 1,
                "total_shifts": 30,
                "patrol_completion_rate": 98,
                "trainings_completed": 2,
                "average_feedback": 95,
                "substitution_accept_rate": 90,
            },
            {
                "id": str(uuid4()),
                "name": "Ana Lima",
                "absences": 1,
                "lates": 2,
                "total_shifts": 30,
                "patrol_completion_rate": 92,
                "trainings_completed": 1,
                "average_feedback": 88,
                "substitution_accept_rate": 75,
            },
            {
                "id": str(uuid4()),
                "name": "Carlos Souza",
                "absences": 2,
                "lates": 3,
                "total_shifts": 28,
                "patrol_completion_rate": 85,
                "trainings_completed": 1,
                "average_feedback": 80,
                "substitution_accept_rate": 65,
            },
        ]

        scores = []
        for emp in sample_employees:
            score = await _performance_agent.calculate_performance_score(
                employee_id=emp["id"],
                employee_name=emp["name"],
                period_days=period_days,
                metrics=emp,
            )
            scores.append(score)

        top_performers = await _performance_agent.identify_top_performers(scores, top_n=5)
        team_avg = sum(s.total_score for s in scores) / len(scores) if scores else 0

        return {
            "period_days": period_days,
            "team_average_score": round(team_avg, 1),
            "total_analyzed": len(scores),
            "top_performers": [
                {
                    "employee_name": tp.employee_name,
                    "score": tp.score,
                    "rank": tp.rank,
                    "highlights": tp.highlights,
                    "eligible_for_promotion": tp.eligible_for_promotion,
                }
                for tp in top_performers
            ],
            "score_distribution": {
                "excelente": sum(1 for s in scores if s.total_score >= 90),
                "bom": sum(1 for s in scores if 80 <= s.total_score < 90),
                "satisfatorio": sum(1 for s in scores if 70 <= s.total_score < 80),
                "atencao": sum(1 for s in scores if 60 <= s.total_score < 70),
                "critico": sum(1 for s in scores if s.total_score < 60),
            },
        }
    except Exception as exc:
        logger.error("Erro no overview de performance: %s", exc)
        return {
            "period_days": period_days,
            "team_average_score": 0,
            "total_analyzed": 0,
            "top_performers": [],
            "score_distribution": {},
        }


@ai_router.get("/absence-risks")
async def get_absence_risks(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Retorna scores de risco de ausência para a equipe.
    """
    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Simular dados de colaboradores
        sample_employees = [
            {
                "id": str(uuid4()),
                "name": "João Silva",
                "absence_count": 4,
                "late_count": 6,
                "tenure_days": 45,
                "next_shift": "Amanhã 06h - Posto Central",
            },
            {
                "id": str(uuid4()),
                "name": "Maria Oliveira",
                "absence_count": 0,
                "late_count": 1,
                "tenure_days": 730,
                "next_shift": "Amanhã 14h - Posto Norte",
            },
            {
                "id": str(uuid4()),
                "name": "Ricardo Costa",
                "absence_count": 2,
                "late_count": 3,
                "tenure_days": 180,
                "next_shift": "Amanhã 22h - Posto Industrial",
            },
        ]

        risks = await _coverage_agent.calculate_team_absence_risks(sample_employees)

        return {
            "analysis_date": tomorrow.isoformat(),
            "total_employees_analyzed": len(risks),
            "high_risk_count": sum(1 for r in risks if r.risk_level in ("alto_risco", "critico")),
            "risks": [
                {
                    "employee_name": r.employee_name,
                    "risk_score": r.risk_score,
                    "risk_level": r.risk_level,
                    "pattern_factors": r.pattern_factors,
                    "next_shift": r.next_shift,
                    "recommendation": r.recommendation,
                }
                for r in risks
            ],
        }
    except Exception as exc:
        logger.error("Erro nos riscos de ausência: %s", exc)
        return {
            "analysis_date": date.today().isoformat(),
            "total_employees_analyzed": 0,
            "high_risk_count": 0,
            "risks": [],
        }


@ai_router.get("/field-monitor")
async def get_field_monitor(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Status em tempo real de toda a operação de campo."""
    try:
        dashboard = await _field_monitor.get_real_time_dashboard()
        return dashboard
    except Exception as exc:
        logger.error("Erro no field monitor: %s", exc)
        return {
            "timestamp": date.today().isoformat(),
            "overview": {},
            "alerts": [],
            "active_patrols": 0,
        }


@ai_router.post("/incident/classify")
async def classify_incident(
    body: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Classifica uma ocorrência automaticamente usando IA."""
    try:
        description = body.get("description", "")
        classification = await _incident_classifier.classify_occurrence(description)
        return {
            "category": classification.category,
            "type": classification.type,
            "severity": classification.severity,
            "confidence": classification.confidence,
            "suggested_actions": classification.suggested_actions,
            "entities_found": classification.entities_found,
        }
    except Exception as exc:
        logger.error("Erro ao classificar ocorrência: %s", exc)
        return {"category": "operacional", "severity": "leve", "confidence": 0}


@ai_router.get("/bartolo/insights")
async def get_bartolo_insights(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Insights proativos gerados pelo Bartolo 3.0."""
    try:
        field_status = await _field_monitor.get_real_time_dashboard()
        insights = await _bartolo.get_proactive_insights(field_status.get("overview", {}))
        return {
            "insights": [
                {
                    "category": i.category,
                    "title": i.title,
                    "description": i.description,
                    "urgency": i.urgency,
                    "action_label": i.action_label,
                }
                for i in insights
            ],
            "count": len(insights),
        }
    except Exception as exc:
        logger.error("Erro nos insights do Bartolo: %s", exc)
        return {"insights": [], "count": 0}


@ai_router.post("/bartolo/chat")
async def bartolo_chat(
    body: dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Chat com Bartolo 3.0 em linguagem natural."""
    try:
        message = body.get("message", "")
        user_id = body.get("user_id", "admin")
        history = body.get("history", [])
        response = await _bartolo.process_message(user_id, message, conversation_history=history)
        return {
            "message": response.message,
            "intent": response.intent,
            "confidence": response.confidence,
            "suggestions": response.suggestions,
            "needs_confirmation": response.needs_confirmation,
        }
    except Exception as exc:
        logger.error("Erro no chat do Bartolo: %s", exc)
        return {
            "message": "Desculpe, tive um problema técnico. Tente novamente.",
            "intent": "erro",
            "confidence": 0,
            "suggestions": [],
        }


@ai_router.get("/cost/forecast")
async def get_cost_forecast(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Previsão de custos operacionais do mês corrente."""
    try:
        today = date.today()
        sample = [{"monthly_salary": 3200, "overtime_hours_estimated": 6}]
        forecast = await _cost_predictor.forecast_post_cost("1", "Posto Central", today, sample, budget=5000)
        return {
            "period": forecast.period_month,
            "total_estimated": forecast.total_estimated,
            "budget": forecast.budget,
            "budget_utilization_pct": forecast.budget_utilization_pct,
            "over_budget": forecast.over_budget,
            "breakdown": forecast.cost_breakdown,
            "recommendations": forecast.recommendations,
        }
    except Exception as exc:
        logger.error("Erro na previsão de custos: %s", exc)
        return {"total_estimated": 0, "budget": 0, "budget_utilization_pct": 0}


@ai_router.post("/maintenance/expire-time-bank")
async def trigger_time_bank_expiration(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Dispara manualmente a expiração de banco de horas vencidos.
    Útil para testes e execução manual sem Celery.
    """
    try:
        from datetime import date, datetime

        from sqlalchemy import and_, select

        from modules.operacional.models import TimeBank, TimeBankEntryType, TimeBankStatus

        today = date.today()
        now = datetime.utcnow()
        result = await db.execute(
            select(TimeBank).where(
                and_(
                    TimeBank.status == TimeBankStatus.APPROVED,
                    TimeBank.expiration_date.isnot(None),
                    TimeBank.expiration_date < today,
                    TimeBank.entry_type == TimeBankEntryType.CREDIT,
                    TimeBank.hours > 0,
                )
            )
        )
        entries = result.scalars().all()
        count = 0
        for e in entries:
            e.status = TimeBankStatus.EXPIRED
            e.description = f"Expirado manualmente em {today.strftime('%d/%m/%Y')}"
            count += 1
        if count:
            await db.commit()
        logger.info("Expiração manual de banco de horas: %d entradas processadas", count)
        return {"expired_count": count, "processed_at": now.isoformat()}
    except Exception as exc:
        logger.error("Erro na expiração manual: %s", exc)
        return {"expired_count": 0, "error": str(exc)}
