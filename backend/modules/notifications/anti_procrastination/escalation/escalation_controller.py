"""
Escalation Controller - APIs do Sistema de Escalation
====================================================

Endpoints para gerenciar escalations automáticas de tarefas pendentes.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.auth import get_current_user
from core.database import get_db
from core.models.user import User

from .escalation_engine import (
    Department,
    EscalationAction,
    EscalationEngine,
    EscalationRule,
    TaskCategory,
    TaskPriority,
)

router = APIRouter(prefix="/api/v1/escalation", tags=["Escalation Engine"])


class EscalationRuleRequest(BaseModel):
    """Request para criar/atualizar regra de escalation."""

    name: str = Field(..., min_length=1, max_length=200)
    category: TaskCategory | None = None
    priority: TaskPriority | None = None
    department: Department | None = None

    level_1_days: int = Field(ge=1, le=30, default=1)
    level_2_days: int = Field(ge=1, le=30, default=3)
    level_3_days: int = Field(ge=1, le=30, default=7)
    level_4_days: int = Field(ge=1, le=30, default=10)

    level_1_actions: list[EscalationAction] = Field(default=[EscalationAction.NOTIFY_USER])
    level_2_actions: list[EscalationAction] = Field(
        default=[EscalationAction.NOTIFY_USER, EscalationAction.NOTIFY_SUPERVISOR]
    )
    level_3_actions: list[EscalationAction] = Field(default=[EscalationAction.NOTIFY_MANAGER])
    level_4_actions: list[EscalationAction] = Field(default=[EscalationAction.NOTIFY_DIRECTOR])

    enabled: bool = True
    weekend_escalation: bool = False
    holiday_escalation: bool = False
    description: str = ""


class ManualEscalationRequest(BaseModel):
    """Request para escalation manual."""

    task_id: UUID
    reason: str = Field(..., min_length=10, max_length=500)
    force_level: int | None = Field(None, ge=1, le=4)


def get_escalation_service(db: Session = Depends(get_db)) -> EscalationEngine:
    """Dependency para obter serviço de escalation."""
    return EscalationEngine(db)


@router.get("/summary", summary="Resumo das Escalations")
async def get_escalation_summary(
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Resumo do estado atual das escalations do sistema.

    Retorna:
    - Distribuição por níveis
    - Escalations próximas
    - Estatísticas do dia
    - Status do engine
    """
    try:
        summary = await escalation_engine.get_escalation_summary()
        return JSONResponse(content=summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar resumo de escalations: {str(e)}",
        )


@router.post("/process/{task_id}", summary="Processar Escalation de Tarefa")
async def process_task_escalation(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Processa escalation de uma tarefa específica.

    Verifica se a tarefa precisa ser escalada baseado nas regras
    configuradas e executa as ações necessárias.

    Args:
        task_id: ID da tarefa a ser processada

    Retorna:
    - Status da escalation
    - Nível anterior e novo
    - Ações executadas
    """
    try:
        # Verifica permissão (apenas supervisores+)
        if not _has_escalation_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão de escalation."
            )

        result = await escalation_engine.process_task_escalation(task_id)
        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar escalation: {str(e)}"
        )


@router.post("/manual", summary="Escalation Manual")
async def manual_escalation(
    request: ManualEscalationRequest,
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Executa escalation manual de uma tarefa.

    Permite forçar escalation independente das regras automáticas,
    útil para situações urgentes ou excepcionais.

    Args:
        request: Dados da escalation manual

    Retorna:
    - Resultado da escalation
    - Ações executadas
    - Log da operação
    """
    try:
        # Verifica permissão (apenas managers+)
        if not _has_management_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Requer permissão de gestão para escalation manual.",
            )

        result = await escalation_engine.process_task_escalation(request.task_id)

        # Adiciona informação de escalation manual
        result["manual_escalation"] = True
        result["requested_by"] = str(current_user.id)
        result["reason"] = request.reason

        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro na escalation manual: {str(e)}"
        )


@router.get("/history", summary="Histórico de Escalations")
async def get_escalation_history(
    days: int = Query(30, ge=1, le=365, description="Período em dias"),
    task_id: UUID | None = Query(None, description="Filtrar por tarefa específica"),
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> list[dict[str, Any]]:
    """
    Histórico de escalations executadas.

    Args:
        days: Período de análise em dias
        task_id: Filtrar por tarefa específica (opcional)

    Retorna:
    - Lista de escalations executadas
    - Detalhes de cada escalation
    - Resultados e ações tomadas
    """
    try:
        history = await escalation_engine.get_escalation_history(days, task_id)
        return history

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao carregar histórico: {str(e)}"
        )


@router.get("/rules", summary="Listar Regras de Escalation")
async def get_escalation_rules(
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> list[dict[str, Any]]:
    """
    Lista todas as regras de escalation configuradas.

    Retorna:
    - Regras padrão do sistema
    - Regras customizadas
    - Status de cada regra
    """
    try:
        # Verifica permissão administrativa
        if not _has_admin_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão administrativa."
            )

        default_rules = [
            {
                "id": "default-compliance",
                "name": "Compliance Critical",
                "category": "compliance",
                "priority": "critical",
                "level_1_days": 1,
                "level_2_days": 2,
                "level_3_days": 3,
                "level_4_days": 5,
                "enabled": True,
                "type": "default",
            },
            {
                "id": "default-financial",
                "name": "Financial Tasks",
                "category": "financial",
                "level_1_days": 1,
                "level_2_days": 3,
                "level_3_days": 7,
                "level_4_days": 10,
                "enabled": True,
                "type": "default",
            },
            {
                "id": "default-security",
                "name": "Security Tasks",
                "category": "security",
                "level_1_days": 1,
                "level_2_days": 2,
                "level_3_days": 5,
                "level_4_days": 7,
                "enabled": True,
                "type": "default",
            },
        ]

        return default_rules

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao listar regras: {str(e)}"
        )


@router.post("/rules", summary="Criar Regra de Escalation")
async def create_escalation_rule(
    rule_request: EscalationRuleRequest,
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Cria nova regra customizada de escalation.

    Args:
        rule_request: Dados da nova regra

    Retorna:
    - ID da regra criada
    - Confirmação de criação
    - Detalhes da regra
    """
    try:
        # Verifica permissão administrativa
        if not _has_admin_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão administrativa."
            )

        # Cria regra
        rule = EscalationRule(
            name=rule_request.name,
            category=rule_request.category,
            priority=rule_request.priority,
            department=rule_request.department,
            level_1_days=rule_request.level_1_days,
            level_2_days=rule_request.level_2_days,
            level_3_days=rule_request.level_3_days,
            level_4_days=rule_request.level_4_days,
            level_1_actions=rule_request.level_1_actions,
            level_2_actions=rule_request.level_2_actions,
            level_3_actions=rule_request.level_3_actions,
            level_4_actions=rule_request.level_4_actions,
            enabled=rule_request.enabled,
            weekend_escalation=rule_request.weekend_escalation,
            holiday_escalation=rule_request.holiday_escalation,
            description=rule_request.description,
            created_by=current_user.id,
        )

        rule_id = escalation_engine.add_custom_rule(rule)

        return JSONResponse(
            content={
                "rule_id": str(rule_id),
                "message": f"✅ Regra {rule_request.name} criada com sucesso.",
                "rule": {
                    "name": rule.name,
                    "category": rule.category.value if rule.category else None,
                    "priority": rule.priority.value if rule.priority else None,
                    "department": rule.department.value if rule.department else None,
                    "enabled": rule.enabled,
                },
            }
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar regra: {str(e)}")


@router.put("/rules/{rule_id}", summary="Atualizar Regra de Escalation")
async def update_escalation_rule(
    rule_id: UUID,
    rule_request: EscalationRuleRequest,
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Atualiza regra existente de escalation.

    Args:
        rule_id: ID da regra a atualizar
        rule_request: Dados atualizados

    Retorna:
    - Confirmação de atualização
    - Detalhes da regra atualizada
    """
    try:
        # Verifica permissão administrativa
        if not _has_admin_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão administrativa."
            )

        # Cria regra atualizada
        updated_rule = EscalationRule(
            id=rule_id,
            name=rule_request.name,
            category=rule_request.category,
            priority=rule_request.priority,
            department=rule_request.department,
            level_1_days=rule_request.level_1_days,
            level_2_days=rule_request.level_2_days,
            level_3_days=rule_request.level_3_days,
            level_4_days=rule_request.level_4_days,
            level_1_actions=rule_request.level_1_actions,
            level_2_actions=rule_request.level_2_actions,
            level_3_actions=rule_request.level_3_actions,
            level_4_actions=rule_request.level_4_actions,
            enabled=rule_request.enabled,
            weekend_escalation=rule_request.weekend_escalation,
            holiday_escalation=rule_request.holiday_escalation,
            description=rule_request.description,
        )

        success = escalation_engine.update_rule(rule_id, updated_rule)

        if success:
            return JSONResponse(
                content={"message": f"✅ Regra {rule_id} atualizada com sucesso.", "rule_id": str(rule_id)}
            )
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Regra {rule_id} não encontrada.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao atualizar regra: {str(e)}"
        )


@router.delete("/rules/{rule_id}", summary="Remover Regra de Escalation")
async def delete_escalation_rule(
    rule_id: UUID,
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Remove regra customizada de escalation.

    Args:
        rule_id: ID da regra a remover

    Retorna:
    - Confirmação de remoção
    """
    try:
        # Verifica permissão administrativa
        if not _has_admin_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão administrativa."
            )

        success = escalation_engine.remove_rule(rule_id)

        if success:
            return JSONResponse(content={"message": f"✅ Regra {rule_id} removida com sucesso."})
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Regra {rule_id} não encontrada.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao remover regra: {str(e)}"
        )


@router.post("/engine/start", summary="Iniciar Engine de Escalation")
async def start_escalation_engine(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Inicia monitoramento automático de escalations.

    O engine irá verificar continuamente todas as tarefas
    pendentes e aplicar escalations conforme necessário.
    """
    try:
        # Verifica permissão administrativa
        if not _has_admin_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão administrativa."
            )

        # Inicia engine em background
        background_tasks.add_task(escalation_engine.start_monitoring)

        return JSONResponse(
            content={
                "message": "🚨 Engine de escalation iniciado em background.",
                "status": "starting",
                "started_by": str(current_user.id),
                "started_at": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao iniciar engine: {str(e)}"
        )


@router.post("/engine/stop", summary="Parar Engine de Escalation")
async def stop_escalation_engine(
    current_user: User = Depends(get_current_user),
    escalation_engine: EscalationEngine = Depends(get_escalation_service),
) -> dict[str, Any]:
    """
    Para monitoramento automático de escalations.

    Atenção: Isso vai parar todas as escalations automáticas.
    Use apenas para manutenção ou emergência.
    """
    try:
        # Verifica permissão administrativa
        if not _has_admin_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Requer permissão administrativa."
            )

        escalation_engine.stop_monitoring()

        return JSONResponse(
            content={
                "message": "🛑 Engine de escalation parado.",
                "status": "stopped",
                "stopped_by": str(current_user.id),
                "stopped_at": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao parar engine: {str(e)}")


# Funções auxiliares de permissão


def _has_escalation_permission(user: User) -> bool:
    """Verifica se usuário pode processar escalations."""
    return user.role in ["admin", "director", "ceo", "manager", "supervisor"]


def _has_management_permission(user: User) -> bool:
    """Verifica se usuário tem permissão de gestão."""
    return user.role in ["admin", "director", "ceo", "manager"]


def _has_admin_permission(user: User) -> bool:
    """Verifica se usuário tem permissão administrativa."""
    return user.role in ["admin", "director", "ceo"]
