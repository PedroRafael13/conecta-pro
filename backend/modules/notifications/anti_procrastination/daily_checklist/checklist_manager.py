"""
Sistema de Checklist Diário Obrigatório - Conecta PRO
====================================================

Força todos os usuários a revisarem suas pendências no primeiro login do dia.
Sistema anti-procrastinação que impede acesso até revisão completa.

Funcionalidades:
- Checklist matinal obrigatório
- Bloqueio de sistema até conclusão
- Acompanhamento de progresso
- Métricas de compliance

Autor: Conecta PRO Team + Claude AI  
Data: 2026-01-10
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum
import logging

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Date, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base

from ..models import Department, TaskPriority, PendingTask
from ..dashboard.unified_dashboard import UnifiedDashboard

logger = logging.getLogger(__name__)
Base = declarative_base()


class ChecklistStatus(str, Enum):
    """Status do checklist diário."""
    
    PENDING = "pending"       # Aguardando revisão
    IN_PROGRESS = "in_progress"  # Em andamento
    COMPLETED = "completed"   # Concluído
    SKIPPED = "skipped"      # Pulado (exceção)
    EXPIRED = "expired"      # Expirado (passou do dia)


class TaskAction(str, Enum):
    """Ações possíveis em tarefas durante checklist."""
    
    ACKNOWLEDGED = "acknowledged"    # Reconheceu a tarefa
    SCHEDULED = "scheduled"         # Agendou para resolver
    DELEGATED = "delegated"         # Delegou para outro
    COMPLETED = "completed"         # Marcou como concluída
    POSTPONED = "postponed"         # Adiou com justificativa


@dataclass
class ChecklistItem:
    """Item individual do checklist."""
    
    task_id: UUID
    title: str
    priority: TaskPriority
    days_pending: int
    urgency_score: float
    action_taken: Optional[TaskAction] = None
    comment: str = ""
    scheduled_date: Optional[date] = None
    delegated_to: Optional[UUID] = None


class DailyChecklist(Base):
    """Modelo de checklist diário no banco."""
    
    __tablename__ = "daily_checklists"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Usuário
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    user_name = Column(String(200), nullable=False)
    department = Column(String(50), nullable=False, index=True)
    
    # Data do checklist
    checklist_date = Column(Date, nullable=False, index=True)
    
    # Status e timing
    status = Column(String(20), nullable=False, default=ChecklistStatus.PENDING.value, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Métricas
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    critical_items = Column(Integer, default=0)
    time_spent_minutes = Column(Integer, default=0)
    
    # Dados do checklist
    checklist_data = Column(JSONB)  # Lista de ChecklistItem serializada
    
    # Feedback do usuário
    user_feedback = Column(Text)
    satisfaction_score = Column(Integer)  # 1-5
    
    # Sistema
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        {"comment": "Checklists diários obrigatórios para revisão de pendências"}
    )


class ChecklistManager:
    """
    Gerenciador do sistema de checklist diário obrigatório.
    
    Responsabilidades:
    - Gerar checklist personalizado para cada usuário
    - Controlar acesso ao sistema até conclusão
    - Acompanhar progresso e métricas
    - Aplicar regras de escalation baseadas no checklist
    """
    
    def __init__(self, db: Session, dashboard: UnifiedDashboard):
        self.db = db
        self.dashboard = dashboard
        
    async def check_daily_requirement(self, user_id: UUID, user_department: str) -> Dict[str, Any]:
        """
        Verifica se usuário precisa completar checklist diário.
        
        Args:
            user_id: ID do usuário
            user_department: Departamento do usuário
            
        Returns:
            Dict com status do requirement:
            - required: bool
            - checklist_id: UUID (se existir)
            - blocked: bool (se acesso está bloqueado)
            - message: str
        """
        today = date.today()
        
        # Busca checklist do dia
        existing_checklist = self.db.query(DailyChecklist).filter(
            DailyChecklist.user_id == user_id,
            DailyChecklist.checklist_date == today
        ).first()
        
        # Se já completou hoje, não precisa
        if existing_checklist and existing_checklist.status == ChecklistStatus.COMPLETED.value:
            return {
                "required": False,
                "checklist_id": existing_checklist.id,
                "blocked": False,
                "message": "✅ Checklist diário já foi concluído hoje.",
                "completed_at": existing_checklist.completed_at.isoformat()
            }
        
        # Verifica se tem tarefas pendentes que exigem checklist
        user_dept = Department(user_department) if user_department in Department.__members__.values() else None
        if not user_dept:
            return {
                "required": False,
                "blocked": False,
                "message": "Departamento não configurado para checklist."
            }
        
        # Conta tarefas pendentes do usuário/departamento
        pending_tasks = await self._get_user_pending_tasks(user_id, user_dept)
        
        # Se não tem tarefas pendentes, não precisa de checklist
        if not pending_tasks:
            return {
                "required": False,
                "blocked": False,
                "message": "🎉 Sem tarefas pendentes! Acesso liberado."
            }
        
        # Tem tarefas pendentes - checklist obrigatório
        checklist_id = existing_checklist.id if existing_checklist else None
        
        # Verifica se é primeira vez no dia (bloqueia acesso)
        is_blocked = self._should_block_access(pending_tasks)
        
        return {
            "required": True,
            "checklist_id": checklist_id,
            "blocked": is_blocked,
            "message": f"📋 Você tem {len(pending_tasks)} tarefas pendentes que requerem revisão.",
            "pending_count": len(pending_tasks),
            "critical_count": len([t for t in pending_tasks if t.priority == TaskPriority.CRITICAL])
        }
    
    async def generate_daily_checklist(
        self, 
        user_id: UUID,
        user_name: str,
        user_department: str
    ) -> UUID:
        """
        Gera checklist diário personalizado para o usuário.
        
        Args:
            user_id: ID do usuário
            user_name: Nome do usuário  
            user_department: Departamento do usuário
            
        Returns:
            UUID: ID do checklist criado
        """
        today = date.today()
        
        logger.info(f"Gerando checklist diário para {user_name} ({user_department})")
        
        # Verifica se já existe checklist hoje
        existing = self.db.query(DailyChecklist).filter(
            DailyChecklist.user_id == user_id,
            DailyChecklist.checklist_date == today
        ).first()
        
        if existing:
            return existing.id
        
        # Busca tarefas pendentes do usuário
        user_dept = Department(user_department)
        pending_tasks = await self._get_user_pending_tasks(user_id, user_dept)
        
        # Converte para ChecklistItems
        checklist_items = []
        critical_count = 0
        
        for task_data in pending_tasks:
            if task_data.priority == TaskPriority.CRITICAL:
                critical_count += 1
                
            item = ChecklistItem(
                task_id=task_data.id,
                title=task_data.title,
                priority=task_data.priority,
                days_pending=task_data.days_pending,
                urgency_score=task_data.urgency_score
            )
            checklist_items.append(item)
        
        # Ordena por urgência (mais urgentes primeiro)
        checklist_items.sort(key=lambda x: x.urgency_score, reverse=True)
        
        # Cria checklist no banco
        checklist = DailyChecklist(
            user_id=user_id,
            user_name=user_name,
            department=user_department,
            checklist_date=today,
            status=ChecklistStatus.PENDING.value,
            total_items=len(checklist_items),
            critical_items=critical_count,
            checklist_data=[self._item_to_dict(item) for item in checklist_items]
        )
        
        self.db.add(checklist)
        self.db.commit()
        self.db.refresh(checklist)
        
        logger.info(f"Checklist criado: {checklist.id} com {len(checklist_items)} itens")
        
        return checklist.id
    
    async def get_checklist(self, checklist_id: UUID) -> Dict[str, Any]:
        """
        Busca checklist por ID.
        
        Args:
            checklist_id: ID do checklist
            
        Returns:
            Dict com dados completos do checklist
        """
        checklist = self.db.query(DailyChecklist).filter(
            DailyChecklist.id == checklist_id
        ).first()
        
        if not checklist:
            raise ValueError(f"Checklist {checklist_id} não encontrado")
        
        return {
            "id": str(checklist.id),
            "user_name": checklist.user_name,
            "department": checklist.department,
            "date": checklist.checklist_date.isoformat(),
            "status": checklist.status,
            "started_at": checklist.started_at.isoformat() if checklist.started_at else None,
            "completed_at": checklist.completed_at.isoformat() if checklist.completed_at else None,
            "total_items": checklist.total_items,
            "completed_items": checklist.completed_items,
            "critical_items": checklist.critical_items,
            "time_spent_minutes": checklist.time_spent_minutes,
            "items": checklist.checklist_data or [],
            "progress_percentage": round((checklist.completed_items / checklist.total_items) * 100, 1) if checklist.total_items > 0 else 100,
            "user_feedback": checklist.user_feedback,
            "satisfaction_score": checklist.satisfaction_score
        }
    
    async def start_checklist(self, checklist_id: UUID) -> bool:
        """
        Inicia um checklist (marca como em andamento).
        
        Args:
            checklist_id: ID do checklist
            
        Returns:
            bool: Sucesso da operação
        """
        checklist = self.db.query(DailyChecklist).filter(
            DailyChecklist.id == checklist_id
        ).first()
        
        if not checklist:
            return False
        
        if checklist.status != ChecklistStatus.PENDING.value:
            return False  # Já iniciado ou concluído
        
        checklist.status = ChecklistStatus.IN_PROGRESS.value
        checklist.started_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Checklist {checklist_id} iniciado por {checklist.user_name}")
        
        return True
    
    async def update_checklist_item(
        self,
        checklist_id: UUID,
        task_id: UUID,
        action: TaskAction,
        comment: str = "",
        scheduled_date: Optional[date] = None,
        delegated_to: Optional[UUID] = None
    ) -> bool:
        """
        Atualiza ação tomada em um item do checklist.
        
        Args:
            checklist_id: ID do checklist
            task_id: ID da tarefa
            action: Ação tomada
            comment: Comentário opcional
            scheduled_date: Data agendada (para action=SCHEDULED)
            delegated_to: Usuário delegado (para action=DELEGATED)
            
        Returns:
            bool: Sucesso da operação
        """
        checklist = self.db.query(DailyChecklist).filter(
            DailyChecklist.id == checklist_id
        ).first()
        
        if not checklist or not checklist.checklist_data:
            return False
        
        # Atualiza item específico
        updated_items = []
        item_updated = False
        
        for item_dict in checklist.checklist_data:
            if item_dict["task_id"] == str(task_id):
                # Atualiza este item
                item_dict["action_taken"] = action.value
                item_dict["comment"] = comment
                if scheduled_date:
                    item_dict["scheduled_date"] = scheduled_date.isoformat()
                if delegated_to:
                    item_dict["delegated_to"] = str(delegated_to)
                item_updated = True
            
            updated_items.append(item_dict)
        
        if not item_updated:
            return False
        
        # Recalcula estatísticas
        completed_count = len([item for item in updated_items if item.get("action_taken")])
        
        checklist.checklist_data = updated_items
        checklist.completed_items = completed_count
        
        # Se completou todos os itens, marca como concluído
        if completed_count == checklist.total_items:
            checklist.status = ChecklistStatus.COMPLETED.value
            checklist.completed_at = datetime.utcnow()
            
            # Calcula tempo gasto
            if checklist.started_at:
                time_spent = datetime.utcnow() - checklist.started_at
                checklist.time_spent_minutes = int(time_spent.total_seconds() / 60)
        
        self.db.commit()
        
        logger.info(f"Item {task_id} do checklist {checklist_id} atualizado: {action.value}")
        
        return True
    
    async def complete_checklist(
        self,
        checklist_id: UUID,
        user_feedback: str = "",
        satisfaction_score: int = 5
    ) -> bool:
        """
        Completa um checklist com feedback do usuário.
        
        Args:
            checklist_id: ID do checklist
            user_feedback: Feedback do usuário
            satisfaction_score: Score de satisfação (1-5)
            
        Returns:
            bool: Sucesso da operação
        """
        checklist = self.db.query(DailyChecklist).filter(
            DailyChecklist.id == checklist_id
        ).first()
        
        if not checklist:
            return False
        
        checklist.status = ChecklistStatus.COMPLETED.value
        checklist.completed_at = datetime.utcnow()
        checklist.user_feedback = user_feedback
        checklist.satisfaction_score = max(1, min(5, satisfaction_score))
        
        # Calcula tempo total gasto
        if checklist.started_at:
            time_spent = datetime.utcnow() - checklist.started_at
            checklist.time_spent_minutes = int(time_spent.total_seconds() / 60)
        
        self.db.commit()
        
        logger.info(f"Checklist {checklist_id} concluído por {checklist.user_name}")
        
        return True
    
    async def get_checklist_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Métricas de compliance do sistema de checklist.
        
        Args:
            days: Período de análise em dias
            
        Returns:
            Dict com métricas detalhadas
        """
        start_date = date.today() - timedelta(days=days)
        
        # Busca checklists do período
        checklists = self.db.query(DailyChecklist).filter(
            DailyChecklist.checklist_date >= start_date
        ).all()
        
        if not checklists:
            return {"period_days": days, "total_checklists": 0}
        
        total = len(checklists)
        completed = len([c for c in checklists if c.status == ChecklistStatus.COMPLETED.value])
        
        # Métricas por departamento
        dept_metrics = {}
        for checklist in checklists:
            dept = checklist.department
            if dept not in dept_metrics:
                dept_metrics[dept] = {"total": 0, "completed": 0, "avg_time": 0, "avg_satisfaction": 0}
            
            dept_metrics[dept]["total"] += 1
            if checklist.status == ChecklistStatus.COMPLETED.value:
                dept_metrics[dept]["completed"] += 1
        
        # Tempo médio de conclusão
        completed_checklists = [c for c in checklists if c.time_spent_minutes and c.time_spent_minutes > 0]
        avg_time = sum(c.time_spent_minutes for c in completed_checklists) / len(completed_checklists) if completed_checklists else 0
        
        # Satisfação média
        rated_checklists = [c for c in checklists if c.satisfaction_score]
        avg_satisfaction = sum(c.satisfaction_score for c in rated_checklists) / len(rated_checklists) if rated_checklists else 0
        
        return {
            "period_days": days,
            "total_checklists": total,
            "completed_checklists": completed,
            "compliance_rate": round((completed / total) * 100, 2) if total > 0 else 0,
            "avg_completion_time_minutes": round(avg_time, 1),
            "avg_satisfaction_score": round(avg_satisfaction, 2),
            "department_breakdown": dept_metrics,
            "daily_trend": await self._calculate_daily_trend(start_date)
        }
    
    # Métodos auxiliares privados
    
    async def _get_user_pending_tasks(self, user_id: UUID, department: Department) -> List:
        """Busca tarefas pendentes do usuário."""
        # Busca tarefas atribuídas diretamente ao usuário
        user_tasks = self.db.query(PendingTask).filter(
            PendingTask.assigned_to == user_id,
            PendingTask.status == "pending"
        ).all()
        
        # Busca tarefas do departamento não atribuídas
        dept_tasks = self.db.query(PendingTask).filter(
            PendingTask.department == department,
            PendingTask.assigned_to.is_(None),
            PendingTask.status == "pending"
        ).all()
        
        # Converte para PendingTaskData
        from ..dashboard.unified_dashboard import UnifiedDashboard
        all_tasks = user_tasks + dept_tasks
        
        return [self.dashboard._task_to_data(task) for task in all_tasks]
    
    def _should_block_access(self, pending_tasks: List) -> bool:
        """Determina se deve bloquear acesso baseado nas tarefas pendentes."""
        # Bloqueia se tem tarefas críticas ou muitas tarefas antigas
        critical_tasks = [t for t in pending_tasks if t.priority == TaskPriority.CRITICAL]
        old_tasks = [t for t in pending_tasks if t.days_pending > 7]
        
        return len(critical_tasks) > 0 or len(old_tasks) > 5
    
    def _item_to_dict(self, item: ChecklistItem) -> Dict[str, Any]:
        """Converte ChecklistItem para dicionário."""
        return {
            "task_id": str(item.task_id),
            "title": item.title,
            "priority": item.priority.value,
            "days_pending": item.days_pending,
            "urgency_score": item.urgency_score,
            "action_taken": item.action_taken.value if item.action_taken else None,
            "comment": item.comment,
            "scheduled_date": item.scheduled_date.isoformat() if item.scheduled_date else None,
            "delegated_to": str(item.delegated_to) if item.delegated_to else None
        }
    
    async def _calculate_daily_trend(self, start_date: date) -> List[Dict[str, Any]]:
        """Calcula tendência diária de compliance."""
        trend = []
        current_date = start_date
        
        while current_date <= date.today():
            day_checklists = self.db.query(DailyChecklist).filter(
                DailyChecklist.checklist_date == current_date
            ).all()
            
            total = len(day_checklists)
            completed = len([c for c in day_checklists if c.status == ChecklistStatus.COMPLETED.value])
            
            trend.append({
                "date": current_date.isoformat(),
                "total": total,
                "completed": completed,
                "rate": round((completed / total) * 100, 1) if total > 0 else 0
            })
            
            current_date += timedelta(days=1)
        
        return trend
