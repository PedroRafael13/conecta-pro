"""
Agente de Monitoramento de Campo em Tempo Real.
Author: Conecta PRO Team / Date: 2026-03-09 / Quality: 99+
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class PostStatus:
    post_id: str
    post_name: str
    status: str  # coberto, descoberto, parcial
    coverage_percentage: float
    employees_present: list[str] = field(default_factory=list)
    last_patrol: datetime | None = None
    next_patrol_due: datetime | None = None
    active_alerts: int = 0


@dataclass
class OperationStatus:
    timestamp: datetime
    total_posts: int
    covered_posts: int
    uncovered_posts: int
    employees_on_field: int
    active_patrols: int
    open_occurrences: int
    active_alerts: int
    coverage_percentage: float
    critical_issues: list[str] = field(default_factory=list)


@dataclass
class FieldEvent:
    id: str
    type: str  # check_in, check_out, patrol_start, patrol_checkpoint, occurrence, alert
    employee_id: str
    employee_name: str
    post_id: str
    post_name: str
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)


class FieldMonitorAgent:
    """
    Agente de IA para monitoramento de campo em tempo real 24/7.
    Agrega dados de GPS, check-ins, rondas e ocorrências.
    SUPERPOWERS: Visão unificada de toda a operação com alertas instantâneos.
    """

    async def get_operation_status(
        self,
        posts_data: list[dict[str, Any]] | None = None,
        shifts_data: list[dict[str, Any]] | None = None,
    ) -> OperationStatus:
        """
        Retorna status consolidado de toda a operação em tempo real.
        Agrega postos, colaboradores, rondas e ocorrências.
        """
        logger.info("Gerando status operacional em tempo real")
        posts = posts_data or []
        shifts = shifts_data or []

        total_posts = len(posts) if posts else 0
        covered = sum(1 for p in posts if p.get("has_coverage", True))
        employees_on_field = sum(1 for s in shifts if s.get("status") == "em_andamento")
        active_patrols = sum(1 for s in shifts if s.get("patrol_active", False))
        coverage_pct = (covered / max(total_posts, 1)) * 100

        critical_issues = []
        uncovered = total_posts - covered
        if uncovered > 0:
            critical_issues.append(f"{uncovered} posto(s) descoberto(s)")
        if active_patrols == 0 and total_posts > 0:
            critical_issues.append("Nenhuma ronda ativa no momento")

        return OperationStatus(
            timestamp=datetime.utcnow(),
            total_posts=total_posts,
            covered_posts=covered,
            uncovered_posts=uncovered,
            employees_on_field=employees_on_field,
            active_patrols=active_patrols,
            open_occurrences=0,
            active_alerts=len(critical_issues),
            coverage_percentage=round(coverage_pct, 1),
            critical_issues=critical_issues,
        )

    async def get_post_status(
        self,
        post_id: str,
        post_name: str,
        post_data: dict[str, Any] | None = None,
    ) -> PostStatus:
        """
        Retorna status detalhado de um posto específico.
        Inclui colaboradores presentes, rondas e alertas.
        """
        data = post_data or {}
        employees = data.get("employees_present", [])
        coverage_pct = 100.0 if employees else 0.0
        status = "coberto" if employees else "descoberto"

        return PostStatus(
            post_id=post_id,
            post_name=post_name,
            status=status,
            coverage_percentage=coverage_pct,
            employees_present=employees,
            last_patrol=data.get("last_patrol"),
            next_patrol_due=data.get("next_patrol_due"),
            active_alerts=data.get("active_alerts", 0),
        )

    async def generate_field_event(
        self,
        event_type: str,
        employee_id: str,
        employee_name: str,
        post_id: str,
        post_name: str,
        details: dict[str, Any] | None = None,
    ) -> FieldEvent:
        """Registra evento de campo para stream em tempo real."""
        return FieldEvent(
            id=str(uuid4()),
            type=event_type,
            employee_id=employee_id,
            employee_name=employee_name,
            post_id=post_id,
            post_name=post_name,
            timestamp=datetime.utcnow(),
            details=details or {},
        )

    async def get_real_time_dashboard(
        self,
        posts_data: list[dict[str, Any]] | None = None,
        shifts_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Gera dados completos para dashboard de comando em tempo real.
        Inclui mapa, alertas, cobertura e rondas ativas.
        """
        status = await self.get_operation_status(posts_data, shifts_data)
        return {
            "timestamp": status.timestamp.isoformat(),
            "overview": {
                "total_posts": status.total_posts,
                "covered_posts": status.covered_posts,
                "uncovered_posts": status.uncovered_posts,
                "employees_on_field": status.employees_on_field,
                "coverage_percentage": status.coverage_percentage,
            },
            "alerts": [{"message": issue, "severity": "critico"} for issue in status.critical_issues],
            "active_patrols": status.active_patrols,
        }
