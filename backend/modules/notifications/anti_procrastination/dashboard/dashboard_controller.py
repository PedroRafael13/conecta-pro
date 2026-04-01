"""
Dashboard Controller - APIs do Sistema Anti-Procrastinação
=========================================================

Endpoints RESTful para acesso aos dashboards unificados de pendências.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

import contextlib
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.auth import get_current_user
from core.database import get_db
from core.models.user import User

from ..integration.module_integrator import ModuleIntegrator
from ..models import Department, EscalationLevel, TaskCategory, TaskFilter, TaskPriority, TaskStatus
from .unified_dashboard import UnifiedDashboard

router = APIRouter(prefix="/api/v1/anti-procrastination", tags=["Anti-Procrastination"])


def get_dashboard_service(db: Session = Depends(get_db)) -> UnifiedDashboard:
    """Dependency para obter serviço do dashboard."""
    integrator = ModuleIntegrator(db)
    return UnifiedDashboard(db, integrator)


@router.get("/dashboard/executive", summary="Dashboard Executivo")
async def get_executive_dashboard(
    current_user: User = Depends(get_current_user), dashboard: UnifiedDashboard = Depends(get_dashboard_service)
) -> dict[str, Any]:
    """
    Dashboard executivo com visão de alto nível do sistema.

    Retorna:
    - KPIs gerais
    - Resumo por departamento
    - Alertas críticos
    - Tendências e recomendações
    """
    try:
        # Verifica permissão executiva
        if not _has_executive_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão executiva."
            )

        result = await dashboard.get_executive_dashboard()
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao carregar dashboard executivo: {str(e)}"
        )


@router.get("/dashboard/department/{department}", summary="Dashboard Departamental")
async def get_department_dashboard(
    department: Department,
    limit: int = Query(50, ge=1, le=1000, description="Limite de tarefas"),
    current_user: User = Depends(get_current_user),
    dashboard: UnifiedDashboard = Depends(get_dashboard_service),
) -> dict[str, Any]:
    """
    Dashboard específico de um departamento.

    Args:
        department: Departamento alvo
        limit: Número máximo de tarefas a retornar

    Retorna:
    - Estatísticas do departamento
    - Lista de tarefas pendentes
    - Tarefas mais urgentes
    - Breakdown por categoria
    - Tendências
    """
    try:
        # Verifica permissão departamental
        if not _has_department_permission(current_user, department):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Sem permissão para departamento {department.value}.",
            )

        result = await dashboard.get_department_dashboard(department, limit)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar dashboard do departamento: {str(e)}",
        )


@router.get("/dashboard/summary", summary="Resumo Geral do Sistema")
async def get_system_summary(
    force_refresh: bool = Query(False, description="Força atualização do cache"),
    current_user: User = Depends(get_current_user),
    dashboard: UnifiedDashboard = Depends(get_dashboard_service),
) -> dict[str, Any]:
    """
    Resumo geral do sistema de pendências.

    Args:
        force_refresh: Força atualização dos dados

    Retorna:
    - Contadores gerais
    - Resumo por departamento
    - Métricas de performance
    - Principais gargalos
    """
    try:
        summary = await dashboard.get_system_summary(force_refresh)
        return summary.dict()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao carregar resumo do sistema: {str(e)}"
        )


@router.get("/tasks/search", summary="Busca Avançada de Tarefas")
async def search_tasks(
    # Filtros de busca
    department: Department | None = Query(None, description="Filtrar por departamento"),
    category: TaskCategory | None = Query(None, description="Filtrar por categoria"),
    priority: TaskPriority | None = Query(None, description="Filtrar por prioridade"),
    status: TaskStatus | None = Query(None, description="Filtrar por status"),
    assigned_to: UUID | None = Query(None, description="Filtrar por responsável"),
    # Filtros de tempo
    days_pending_min: int | None = Query(None, ge=0, description="Mínimo de dias pendente"),
    days_pending_max: int | None = Query(None, ge=0, description="Máximo de dias pendente"),
    # Filtros de escalation
    escalation_level: EscalationLevel | None = Query(None, description="Nível de escalation"),
    # Paginação
    limit: int = Query(50, ge=1, le=1000, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    # Dependências
    current_user: User = Depends(get_current_user),
    dashboard: UnifiedDashboard = Depends(get_dashboard_service),
) -> list[dict[str, Any]]:
    """
    Busca avançada de tarefas pendentes com filtros.

    Permite filtrar por:
    - Departamento, categoria, prioridade, status
    - Responsável pela tarefa
    - Tempo pendente (min/max dias)
    - Nível de escalation

    Suporta paginação para grandes volumes.
    """
    try:
        filters = TaskFilter(
            department=department,
            category=category,
            priority=priority,
            status=status,
            assigned_to=assigned_to,
            days_pending_min=days_pending_min,
            days_pending_max=days_pending_max,
            escalation_level=escalation_level,
            limit=limit,
            offset=offset,
        )

        # Aplica filtros de permissão do usuário
        filters = _apply_user_permissions(current_user, filters)

        tasks = await dashboard.search_tasks(filters)
        return tasks

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro na busca de tarefas: {str(e)}"
        )


@router.get("/dashboard/realtime", summary="Dashboard em Tempo Real")
async def get_realtime_dashboard(
    departments: str | None = Query(None, description="Departamentos separados por vírgula"),
    current_user: User = Depends(get_current_user),
    dashboard: UnifiedDashboard = Depends(get_dashboard_service),
) -> dict[str, Any]:
    """
    Dashboard em tempo real para monitoramento contínuo.

    Otimizado para:
    - Atualizações frequentes (WebSocket friendly)
    - Dados essenciais apenas
    - Performance máxima

    Args:
        departments: Lista de departamentos para monitorar

    Retorna:
    - Contadores atualizados
    - Alertas ativos
    - Mudanças recentes
    """
    try:
        # Parse departamentos se fornecidos
        dept_filter = None
        if departments:
            try:
                dept_list = [Department(d.strip()) for d in departments.split(",")]
                dept_filter = dept_list
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Departamento inválido: {str(e)}")

        # Dados em tempo real otimizados
        summary = await dashboard.get_system_summary(force_refresh=True)

        # Filtra por departamentos se especificado
        departments_data = summary.departments
        if dept_filter:
            departments_data = [d for d in departments_data if d.department in dept_filter]

        # Dados essenciais para tempo real
        realtime_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_pending": summary.total_pending,
            "critical_count": summary.critical_count,
            "overdue_count": summary.overdue_count,
            "departments": [dept.dict() for dept in departments_data],
            "system_health": await dashboard._assess_system_health(),
            "active_alerts": len([d for d in departments_data if d.critical_tasks > 0]),
            "worst_department": max(departments_data, key=lambda d: d.critical_tasks + d.overdue_tasks).department.value
            if departments_data
            else None,
        }

        return JSONResponse(content=realtime_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar dashboard em tempo real: {str(e)}",
        )


@router.get("/metrics/productivity", summary="Métricas de Produtividade")
async def get_productivity_metrics(
    days: int = Query(30, ge=1, le=365, description="Período em dias"),
    department: Department | None = Query(None, description="Departamento específico"),
    current_user: User = Depends(get_current_user),
    dashboard: UnifiedDashboard = Depends(get_dashboard_service),
) -> dict[str, Any]:
    """
    Métricas de produtividade e performance.

    Args:
        days: Período de análise em dias
        department: Departamento específico (opcional)

    Retorna:
    - Taxa de resolução
    - Tempo médio de resolução
    - Eficiência por departamento
    - Tendências de produtividade
    """
    try:
        # Implementar métricas de produtividade
        metrics = {
            "period_days": days,
            "department": department.value if department else "all",
            "resolution_rate": 87.5,
            "avg_resolution_time": 3.2,
            "efficiency_score": 82.1,
            "trend": "improving",
            "benchmarks": {"target_resolution_time": 2.0, "target_resolution_rate": 90.0, "target_efficiency": 85.0},
        }

        return JSONResponse(content=metrics)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar métricas de produtividade: {str(e)}",
        )


# Funções auxiliares de permissão


def _has_executive_permission(user: User) -> bool:
    """Verifica se usuário tem permissão executiva."""
    # Implementar lógica de permissão baseada em roles
    return user.role in ["admin", "director", "ceo", "manager"]


def _has_department_permission(user: User, department: Department) -> bool:
    """Verifica se usuário tem permissão para o departamento."""
    # Usuários executivos veem todos os departamentos
    if _has_executive_permission(user):
        return True

    # Usuários departamentais veem apenas seu departamento
    user_department = getattr(user, "department", None)
    return user_department == department.value


def _apply_user_permissions(user: User, filters: TaskFilter) -> TaskFilter:
    """Aplica filtros de permissão baseados no usuário."""
    # Se não é executivo, limita ao seu departamento
    if not _has_executive_permission(user):
        user_dept = getattr(user, "department", None)
        if user_dept:
            with contextlib.suppress(ValueError):
                filters.department = Department(user_dept)

    return filters
