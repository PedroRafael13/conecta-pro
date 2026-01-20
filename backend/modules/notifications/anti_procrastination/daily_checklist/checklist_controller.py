"""
Checklist Controller - APIs do Sistema de Checklist Diário
=========================================================

Endpoints para gerenciar checklists diários obrigatórios.

Autor: Conecta PRO Team + Claude AI  
Data: 2026-01-10
"""

from datetime import date
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from core.auth import get_current_user
from core.models.user import User

from .checklist_manager import ChecklistManager, TaskAction
from ..dashboard.unified_dashboard import UnifiedDashboard
from ..integration.module_integrator import ModuleIntegrator

router = APIRouter(prefix="/api/v1/daily-checklist", tags=["Daily Checklist"])


class TaskActionRequest(BaseModel):
    """Request para ação em tarefa do checklist."""
    
    task_id: UUID
    action: TaskAction
    comment: Optional[str] = ""
    scheduled_date: Optional[date] = None
    delegated_to: Optional[UUID] = None


class ChecklistFeedback(BaseModel):
    """Feedback de conclusão do checklist."""
    
    feedback: str = ""
    satisfaction_score: int = Field(ge=1, le=5, default=5)


def get_checklist_service(db: Session = Depends(get_db)) -> ChecklistManager:
    """Dependency para obter serviço do checklist."""
    integrator = ModuleIntegrator(db)
    dashboard = UnifiedDashboard(db, integrator)
    return ChecklistManager(db, dashboard)


@router.get("/requirement", summary="Verificar Requirement de Checklist")
async def check_daily_requirement(
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> Dict[str, Any]:
    """
    Verifica se usuário precisa completar checklist diário.
    
    Este endpoint deve ser chamado no login para determinar se o usuário
    precisa revisar suas pendências antes de acessar o sistema.
    
    Retorna:
    - required: Se checklist é obrigatório
    - blocked: Se acesso está bloqueado  
    - checklist_id: ID do checklist (se existir)
    - message: Mensagem para o usuário
    """
    try:
        user_dept = getattr(current_user, "department", "operations")
        
        requirement = await checklist_service.check_daily_requirement(
            current_user.id, 
            user_dept
        )
        
        return JSONResponse(content=requirement)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar requirement: {str(e)}"
        )


@router.post("/generate", summary="Gerar Checklist Diário")
async def generate_daily_checklist(
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> Dict[str, Any]:
    """
    Gera checklist diário personalizado para o usuário.
    
    Cria um novo checklist com todas as tarefas pendentes que requerem
    atenção do usuário, organizadas por prioridade e urgência.
    
    Retorna:
    - checklist_id: ID do checklist criado
    - total_items: Número de itens no checklist
    - critical_items: Número de itens críticos
    """
    try:
        user_dept = getattr(current_user, "department", "operations")
        user_name = getattr(current_user, "name", current_user.email)
        
        checklist_id = await checklist_service.generate_daily_checklist(
            current_user.id,
            user_name,
            user_dept
        )
        
        # Retorna dados básicos do checklist criado
        checklist_data = await checklist_service.get_checklist(checklist_id)
        
        return JSONResponse(content={
            "checklist_id": str(checklist_id),
            "total_items": checklist_data["total_items"],
            "critical_items": checklist_data["critical_items"],
            "message": f"✅ Checklist gerado com {checklist_data[total_items]} itens."
        })
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar checklist: {str(e)}"
        )


@router.get("/{checklist_id}", summary="Obter Checklist")
async def get_checklist(
    checklist_id: UUID,
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> Dict[str, Any]:
    """
    Busca checklist completo por ID.
    
    Args:
        checklist_id: ID do checklist
        
    Retorna:
    - Dados completos do checklist
    - Lista de itens com status
    - Progresso atual
    - Métricas de tempo
    """
    try:
        checklist_data = await checklist_service.get_checklist(checklist_id)
        return JSONResponse(content=checklist_data)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar checklist: {str(e)}"
        )


@router.post("/{checklist_id}/start", summary="Iniciar Checklist")
async def start_checklist(
    checklist_id: UUID,
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> Dict[str, Any]:
    """
    Inicia um checklist (marca como em andamento).
    
    Args:
        checklist_id: ID do checklist
        
    Retorna:
    - success: Se operação foi bem sucedida
    - message: Mensagem de status
    """
    try:
        success = await checklist_service.start_checklist(checklist_id)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "✅ Checklist iniciado. Revise cada item com atenção."
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Checklist não pode ser iniciado. Verifique se já foi concluído."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao iniciar checklist: {str(e)}"
        )


@router.post("/{checklist_id}/items/{task_id}/action", summary="Atualizar Item do Checklist")
async def update_checklist_item(
    checklist_id: UUID,
    task_id: UUID,
    action_request: TaskActionRequest,
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> Dict[str, Any]:
    """
    Atualiza ação tomada em um item específico do checklist.
    
    Args:
        checklist_id: ID do checklist
        task_id: ID da tarefa
        action_request: Dados da ação tomada
        
    Ações disponíveis:
    - ACKNOWLEDGED: Reconheceu a tarefa
    - SCHEDULED: Agendou para resolver (requer data)
    - DELEGATED: Delegou para outro usuário (requer user_id)
    - COMPLETED: Marcou como concluída
    - POSTPONED: Adiou com justificativa (requer comentário)
    """
    try:
        success = await checklist_service.update_checklist_item(
            checklist_id,
            task_id,
            action_request.action,
            action_request.comment,
            action_request.scheduled_date,
            action_request.delegated_to
        )
        
        if success:
            # Verifica progresso atualizado
            checklist_data = await checklist_service.get_checklist(checklist_id)
            
            message = f"✅ Ação {action_request.action.value} registrada."
            if checklist_data["status"] == "completed":
                message += " 🎉 Checklist concluído!"
            
            return JSONResponse(content={
                "success": True,
                "message": message,
                "progress": checklist_data["progress_percentage"],
                "completed_items": checklist_data["completed_items"],
                "total_items": checklist_data["total_items"]
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível atualizar o item. Verifique se existe."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar item: {str(e)}"
        )


@router.post("/{checklist_id}/complete", summary="Concluir Checklist")
async def complete_checklist(
    checklist_id: UUID,
    feedback: ChecklistFeedback,
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> Dict[str, Any]:
    """
    Conclui checklist com feedback do usuário.
    
    Args:
        checklist_id: ID do checklist
        feedback: Feedback e satisfação do usuário
        
    Retorna:
    - success: Se operação foi bem sucedida
    - message: Mensagem de congratulações
    - access_granted: Se acesso ao sistema foi liberado
    """
    try:
        success = await checklist_service.complete_checklist(
            checklist_id,
            feedback.feedback,
            feedback.satisfaction_score
        )
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "🎉 Parabéns! Checklist concluído com sucesso. Acesso ao sistema liberado!",
                "access_granted": True,
                "satisfaction_score": feedback.satisfaction_score
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível concluir o checklist."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao concluir checklist: {str(e)}"
        )


@router.get("/metrics/compliance", summary="Métricas de Compliance")
async def get_compliance_metrics(
    days: int = Query(30, ge=1, le=365, description="Período em dias"),
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> Dict[str, Any]:
    """
    Métricas de compliance do sistema de checklist.
    
    Args:
        days: Período de análise em dias
        
    Retorna:
    - Taxa de compliance por período
    - Tempo médio de conclusão
    - Satisfação média dos usuários
    - Breakdown por departamento
    - Tendências diárias
    """
    try:
        # Verifica permissão (apenas executivos)
        if not _has_management_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Requer permissão de gestão."
            )
        
        metrics = await checklist_service.get_checklist_metrics(days)
        return JSONResponse(content=metrics)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar métricas: {str(e)}"
        )


@router.get("/history/user", summary="Histórico do Usuário")
async def get_user_history(
    limit: int = Query(30, ge=1, le=100, description="Limite de registros"),
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
) -> List[Dict[str, Any]]:
    """
    Histórico de checklists do usuário atual.
    
    Args:
        limit: Número máximo de checklists no histórico
        
    Retorna:
    - Lista de checklists passados
    - Estatísticas de performance
    - Tendência de melhoria
    """
    try:
        # Implementar busca de histórico
        # Por enquanto retorna mock data
        return [{
            "date": "2026-01-10",
            "status": "completed",
            "total_items": 5,
            "completion_time_minutes": 8,
            "satisfaction_score": 4
        }]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar histórico: {str(e)}"
        )


# Middleware para checklist obrigatório
async def enforce_daily_checklist(
    request,
    current_user: User = Depends(get_current_user),
    checklist_service: ChecklistManager = Depends(get_checklist_service)
):
    """
    Middleware que verifica se usuário completou checklist diário.
    Bloqueia acesso a rotas protegidas se checklist não foi feito.
    
    IMPORTANTE: Este middleware deve ser aplicado globalmente
    nas rotas que requerem checklist completo.
    """
    # Lista de rotas que não requerem checklist
    bypass_routes = [
        "/api/v1/daily-checklist",
        "/api/v1/auth",
        "/api/v1/health",
        "/docs",
        "/redoc"
    ]
    
    # Verifica se rota pode ser acessada sem checklist
    if any(request.url.path.startswith(route) for route in bypass_routes):
        return  # Permite acesso
    
    # Verifica requirement de checklist
    user_dept = getattr(current_user, "department", "operations")
    requirement = await checklist_service.check_daily_requirement(
        current_user.id, 
        user_dept
    )
    
    # Se é obrigatório e está bloqueado, nega acesso
    if requirement.get("required") and requirement.get("blocked"):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "error": "checklist_required",
                "message": "Complete seu checklist diário para acessar o sistema.",
                "checklist_id": requirement.get("checklist_id"),
                "pending_count": requirement.get("pending_count", 0)
            }
        )


# Função auxiliar de permissão
def _has_management_permission(user: User) -> bool:
    """Verifica se usuário tem permissão de gestão."""
    return user.role in ["admin", "director", "ceo", "manager", "supervisor"]
