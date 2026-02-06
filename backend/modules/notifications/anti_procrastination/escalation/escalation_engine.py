"""
Engine de Escalation Automático - Conecta PRO
============================================

Sistema que automaticamente escala tarefas pendentes através de níveis
crescentes de pressão, garantindo que nada seja esquecido ou procrastinado.

Níveis de Escalation:
- Nível 1: Notificação suave (1 dia)
- Nível 2: Alerta + supervisão (3 dias)  
- Nível 3: Alerta crítico + gestão (7 dias)
- Nível 4: Bloqueio preventivo (10 dias)

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import logging

from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base

from ..models import (
    PendingTask, TaskCategory, TaskPriority, TaskStatus, 
    EscalationLevel, Department
)

logger = logging.getLogger(__name__)
Base = declarative_base()


class EscalationAction(str, Enum):
    """Tipos de ação de escalation."""
    
    NOTIFY_USER = "notify_user"              # Notificar usuário
    NOTIFY_SUPERVISOR = "notify_supervisor"  # Notificar supervisor
    NOTIFY_MANAGER = "notify_manager"        # Notificar gerente
    NOTIFY_DIRECTOR = "notify_director"      # Notificar diretor
    BLOCK_USER = "block_user"               # Bloquear usuário
    REASSIGN_TASK = "reassign_task"         # Reatribuir tarefa
    SEND_EMAIL = "send_email"               # Enviar email
    SEND_SMS = "send_sms"                   # Enviar SMS
    SCHEDULE_MEETING = "schedule_meeting"    # Agendar reunião
    CREATE_INCIDENT = "create_incident"      # Criar incidente


class EscalationTrigger(str, Enum):
    """Gatilhos para escalation."""
    
    TIME_BASED = "time_based"           # Baseado em tempo
    PRIORITY_BASED = "priority_based"   # Baseado em prioridade  
    CATEGORY_BASED = "category_based"   # Baseado em categoria
    CUSTOM_RULE = "custom_rule"         # Regra customizada
    MANUAL_TRIGGER = "manual_trigger"   # Gatilho manual


@dataclass
class EscalationRule:
    """Regra de escalation configurável."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    category: Optional[TaskCategory] = None
    priority: Optional[TaskPriority] = None
    department: Optional[Department] = None
    
    # Configuração de tempo (dias)
    level_1_days: int = 1
    level_2_days: int = 3
    level_3_days: int = 7
    level_4_days: int = 10
    
    # Ações por nível
    level_1_actions: List[EscalationAction] = field(default_factory=lambda: [EscalationAction.NOTIFY_USER])
    level_2_actions: List[EscalationAction] = field(default_factory=lambda: [EscalationAction.NOTIFY_USER, EscalationAction.NOTIFY_SUPERVISOR])
    level_3_actions: List[EscalationAction] = field(default_factory=lambda: [EscalationAction.NOTIFY_MANAGER, EscalationAction.SEND_EMAIL])
    level_4_actions: List[EscalationAction] = field(default_factory=lambda: [EscalationAction.NOTIFY_DIRECTOR, EscalationAction.BLOCK_USER])
    
    # Configuração
    enabled: bool = True
    weekend_escalation: bool = False
    holiday_escalation: bool = False
    
    # Metadados
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    description: str = ""


class EscalationLog(Base):
    """Log de escalations executadas."""
    
    __tablename__ = "escalation_logs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Tarefa relacionada
    task_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    task_title = Column(String(500))
    
    # Escalation
    escalation_level = Column(Integer, nullable=False, index=True)
    rule_id = Column(PGUUID(as_uuid=True), index=True)
    trigger = Column(String(50), nullable=False)
    
    # Ações executadas
    actions_executed = Column(JSONB)
    
    # Pessoas notificadas
    notified_users = Column(JSONB)  # Lista de user_ids
    
    # Resultado
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Metadados
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)
    executed_by = Column(String(100), default="system")
    
    __table_args__ = (
        {"comment": "Log de escalations automáticas executadas"}
    )


class EscalationEngine:
    """
    Engine principal do sistema de escalation automático.
    
    Responsabilidades:
    - Monitorar tarefas pendentes continuamente
    - Aplicar regras de escalation baseadas em tempo e prioridade
    - Executar ações de escalation (notificações, bloqueios, etc.)
    - Manter histórico detalhado de escalations
    - Permitir configuração personalizada de regras
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._default_rules = self._load_default_rules()
        self._custom_rules: Dict[UUID, EscalationRule] = {}
        self._running = False
        
    async def start_monitoring(self):
        """Inicia monitoramento contínuo de escalations."""
        if self._running:
            logger.warning("Engine de escalation já está rodando")
            return
        
        self._running = True
        logger.info("🚨 Engine de escalation iniciado")
        
        # Loop principal de monitoramento
        while self._running:
            try:
                await self._process_escalations()
                await asyncio.sleep(300)  # Verifica a cada 5 minutos
            except Exception as e:
                logger.error(f"Erro no engine de escalation: {e}")
                await asyncio.sleep(60)  # Espera 1 minuto em caso de erro
    
    def stop_monitoring(self):
        """Para monitoramento contínuo."""
        self._running = False
        logger.info("🛑 Engine de escalation parado")
    
    async def process_task_escalation(self, task_id: UUID) -> Dict[str, Any]:
        """
        Processa escalation de uma tarefa específica.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Dict com resultado do processamento
        """
        task = self.db.query(PendingTask).filter(PendingTask.id == task_id).first()
        if not task:
            raise ValueError(f"Tarefa {task_id} não encontrada")
        
        # Verifica se precisa de escalation
        escalation_needed, new_level = self._check_escalation_needed(task)
        
        if not escalation_needed:
            return {
                "task_id": str(task_id),
                "escalation_needed": False,
                "current_level": task.escalation_level.value,
                "message": "Nenhuma escalation necessária no momento"
            }
        
        # Executa escalation
        result = await self._execute_escalation(task, new_level)
        
        return {
            "task_id": str(task_id),
            "escalation_needed": True,
            "previous_level": task.escalation_level.value,
            "new_level": new_level.value,
            "actions_executed": result["actions"],
            "success": result["success"],
            "message": result["message"]
        }
    
    async def get_escalation_summary(self) -> Dict[str, Any]:
        """
        Resumo do estado atual das escalations.
        
        Returns:
            Dict com estatísticas e métricas
        """
        # Conta tarefas por nível de escalation
        level_counts = {}
        for level in EscalationLevel:
            count = self.db.query(PendingTask).filter(
                PendingTask.escalation_level == level,
                PendingTask.status == TaskStatus.PENDING
            ).count()
            level_counts[level.name] = count
        
        # Tarefas próximas de escalar
        upcoming_escalations = await self._get_upcoming_escalations()
        
        # Estatísticas de hoje
        today = datetime.utcnow().date()
        today_escalations = self.db.query(EscalationLog).filter(
            EscalationLog.executed_at >= datetime.combine(today, datetime.min.time())
        ).count()
        
        # Tarefas críticas não resolvidas
        critical_unresolved = self.db.query(PendingTask).filter(
            PendingTask.priority == TaskPriority.CRITICAL,
            PendingTask.status == TaskStatus.PENDING,
            PendingTask.escalation_level >= EscalationLevel.LEVEL_2
        ).count()
        
        return {
            "level_distribution": level_counts,
            "upcoming_escalations": len(upcoming_escalations),
            "escalations_today": today_escalations,
            "critical_unresolved": critical_unresolved,
            "engine_status": "running" if self._running else "stopped",
            "last_check": datetime.utcnow().isoformat()
        }
    
    def add_custom_rule(self, rule: EscalationRule) -> UUID:
        """
        Adiciona regra customizada de escalation.
        
        Args:
            rule: Regra de escalation
            
        Returns:
            UUID: ID da regra criada
        """
        self._custom_rules[rule.id] = rule
        
        logger.info(f"Regra de escalation adicionada: {rule.name} ({rule.id})")
        
        return rule.id
    
    def update_rule(self, rule_id: UUID, updated_rule: EscalationRule) -> bool:
        """
        Atualiza regra existente.
        
        Args:
            rule_id: ID da regra
            updated_rule: Regra atualizada
            
        Returns:
            bool: Sucesso da operação
        """
        if rule_id in self._custom_rules:
            self._custom_rules[rule_id] = updated_rule
            logger.info(f"Regra {rule_id} atualizada")
            return True
        
        return False
    
    def remove_rule(self, rule_id: UUID) -> bool:
        """
        Remove regra customizada.
        
        Args:
            rule_id: ID da regra
            
        Returns:
            bool: Sucesso da operação
        """
        if rule_id in self._custom_rules:
            del self._custom_rules[rule_id]
            logger.info(f"Regra {rule_id} removida")
            return True
        
        return False
    
    async def get_escalation_history(
        self, 
        days: int = 30,
        task_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Histórico de escalations.
        
        Args:
            days: Período em dias
            task_id: Filtrar por tarefa específica
            
        Returns:
            Lista de escalations executadas
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(EscalationLog).filter(
            EscalationLog.executed_at >= start_date
        )
        
        if task_id:
            query = query.filter(EscalationLog.task_id == task_id)
        
        logs = query.order_by(EscalationLog.executed_at.desc()).all()
        
        return [
            {
                "id": str(log.id),
                "task_id": str(log.task_id),
                "task_title": log.task_title,
                "escalation_level": log.escalation_level,
                "trigger": log.trigger,
                "actions_executed": log.actions_executed,
                "notified_users": log.notified_users,
                "success": log.success,
                "error_message": log.error_message,
                "executed_at": log.executed_at.isoformat()
            }
            for log in logs
        ]
    
    # Métodos privados
    
    async def _process_escalations(self):
        """Processa todas as escalations pendentes."""
        logger.debug("Verificando escalations pendentes...")
        
        # Busca tarefas que podem precisar de escalation
        pending_tasks = self.db.query(PendingTask).filter(
            PendingTask.status == TaskStatus.PENDING
        ).all()
        
        escalations_processed = 0
        
        for task in pending_tasks:
            try:
                escalation_needed, new_level = self._check_escalation_needed(task)
                
                if escalation_needed:
                    await self._execute_escalation(task, new_level)
                    escalations_processed += 1
                    
                    # Pausa entre escalations para não sobrecarregar
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Erro ao processar escalation da tarefa {task.id}: {e}")
        
        if escalations_processed > 0:
            logger.info(f"✅ {escalations_processed} escalations processadas")
    
    def _check_escalation_needed(self, task: PendingTask) -> Tuple[bool, Optional[EscalationLevel]]:
        """
        Verifica se tarefa precisa ser escalada.
        
        Args:
            task: Tarefa a verificar
            
        Returns:
            Tuple: (precisa_escalar, novo_nivel)
        """
        # Encontra regra aplicável
        rule = self._find_applicable_rule(task)
        if not rule or not rule.enabled:
            return False, None
        
        # Calcula dias pendente
        days_pending = (datetime.utcnow() - task.created_at).days
        current_level = task.escalation_level
        
        # Verifica se deve escalar para próximo nível
        new_level = None
        
        if current_level == EscalationLevel.LEVEL_0 and days_pending >= rule.level_1_days:
            new_level = EscalationLevel.LEVEL_1
        elif current_level == EscalationLevel.LEVEL_1 and days_pending >= rule.level_2_days:
            new_level = EscalationLevel.LEVEL_2
        elif current_level == EscalationLevel.LEVEL_2 and days_pending >= rule.level_3_days:
            new_level = EscalationLevel.LEVEL_3
        elif current_level == EscalationLevel.LEVEL_3 and days_pending >= rule.level_4_days:
            new_level = EscalationLevel.LEVEL_4
        
        return new_level is not None, new_level
    
    def _find_applicable_rule(self, task: PendingTask) -> Optional[EscalationRule]:
        """Encontra regra aplicável para a tarefa."""
        # Primeiro verifica regras customizadas (mais específicas)
        for rule in self._custom_rules.values():
            if self._rule_matches_task(rule, task):
                return rule
        
        # Depois verifica regras padrão
        for rule in self._default_rules:
            if self._rule_matches_task(rule, task):
                return rule
        
        # Retorna regra padrão genérica
        return self._get_default_rule()
    
    def _rule_matches_task(self, rule: EscalationRule, task: PendingTask) -> bool:
        """Verifica se regra se aplica à tarefa."""
        # Verifica categoria
        if rule.category and task.category != rule.category:
            return False
        
        # Verifica prioridade
        if rule.priority and task.priority != rule.priority:
            return False
        
        # Verifica departamento
        if rule.department and task.department != rule.department:
            return False
        
        return True
    
    async def _execute_escalation(self, task: PendingTask, new_level: EscalationLevel) -> Dict[str, Any]:
        """
        Executa escalation de uma tarefa.
        
        Args:
            task: Tarefa a ser escalada
            new_level: Novo nível de escalation
            
        Returns:
            Dict com resultado da execução
        """
        logger.info(f"🚨 Escalando tarefa {task.id} para nível {new_level.value}")
        
        # Encontra regra aplicável
        rule = self._find_applicable_rule(task)
        if not rule:
            rule = self._get_default_rule()
        
        # Determina ações a executar
        actions = self._get_actions_for_level(rule, new_level)
        
        # Executa ações
        executed_actions = []
        notified_users = []
        success = True
        error_message = None
        
        try:
            for action in actions:
                action_result = await self._execute_action(action, task, new_level)
                executed_actions.append({
                    "action": action.value,
                    "success": action_result["success"],
                    "details": action_result.get("details", "")
                })
                
                if action_result.get("notified_users"):
                    notified_users.extend(action_result["notified_users"])
        
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Erro ao executar escalation: {e}")
        
        # Atualiza tarefa
        if success:
            task.escalation_level = new_level
            task.escalation_count += 1
            task.last_escalation = datetime.utcnow()
            self.db.commit()
        
        # Registra log
        log = EscalationLog(
            task_id=task.id,
            task_title=task.title,
            escalation_level=new_level.value,
            rule_id=rule.id,
            trigger=EscalationTrigger.TIME_BASED.value,
            actions_executed=executed_actions,
            notified_users=list(set(notified_users)),
            success=success,
            error_message=error_message
        )
        
        self.db.add(log)
        self.db.commit()
        
        return {
            "success": success,
            "actions": executed_actions,
            "notified_users": notified_users,
            "message": f"Tarefa escalada para nível {new_level.value}" if success else f"Erro: {error_message}"
        }
    
    async def _execute_action(self, action: EscalationAction, task: PendingTask, level: EscalationLevel) -> Dict[str, Any]:
        """
        Executa ação específica de escalation.
        
        Args:
            action: Ação a executar
            task: Tarefa relacionada
            level: Nível de escalation
            
        Returns:
            Dict com resultado da ação
        """
        try:
            if action == EscalationAction.NOTIFY_USER:
                return await self._notify_user(task, level)
            elif action == EscalationAction.NOTIFY_SUPERVISOR:
                return await self._notify_supervisor(task, level)
            elif action == EscalationAction.NOTIFY_MANAGER:
                return await self._notify_manager(task, level)
            elif action == EscalationAction.NOTIFY_DIRECTOR:
                return await self._notify_director(task, level)
            elif action == EscalationAction.SEND_EMAIL:
                return await self._send_escalation_email(task, level)
            elif action == EscalationAction.BLOCK_USER:
                return await self._block_user_access(task, level)
            else:
                return {"success": False, "details": f"Ação {action.value} não implementada"}
        
        except Exception as e:
            return {"success": False, "details": str(e)}
    
    async def _notify_user(self, task: PendingTask, level: EscalationLevel) -> Dict[str, Any]:
        """Notifica usuário responsável."""
        # Implementar integração com sistema de notificações
        logger.info(f"📱 Notificando usuário sobre tarefa {task.title} (nível {level.value})")
        
        return {
            "success": True,
            "details": f"Usuário notificado sobre escalation nível {level.value}",
            "notified_users": [str(task.assigned_to)] if task.assigned_to else []
        }
    
    async def _notify_supervisor(self, task: PendingTask, level: EscalationLevel) -> Dict[str, Any]:
        """Notifica supervisor do departamento."""
        logger.info(f"👨‍💼 Notificando supervisor sobre tarefa {task.title}")
        
        # Buscar supervisor do departamento
        # Por enquanto mock
        return {
            "success": True,
            "details": f"Supervisor do {task.department.value} notificado",
            "notified_users": ["supervisor_id"]
        }
    
    async def _notify_manager(self, task: PendingTask, level: EscalationLevel) -> Dict[str, Any]:
        """Notifica gerente."""
        logger.info(f"👔 Notificando gerente sobre tarefa {task.title}")
        
        return {
            "success": True,
            "details": f"Gerente notificado sobre tarefa crítica",
            "notified_users": ["manager_id"]
        }
    
    async def _notify_director(self, task: PendingTask, level: EscalationLevel) -> Dict[str, Any]:
        """Notifica diretor."""
        logger.info(f"🏢 Notificando diretor sobre tarefa {task.title}")
        
        return {
            "success": True,
            "details": f"Diretor notificado sobre tarefa em nível crítico",
            "notified_users": ["director_id"]
        }
    
    async def _send_escalation_email(self, task: PendingTask, level: EscalationLevel) -> Dict[str, Any]:
        """Envia email de escalation."""
        logger.info(f"📧 Enviando email de escalation para tarefa {task.title}")
        
        # Implementar integração com sistema de email
        return {
            "success": True,
            "details": f"Email de escalation enviado",
            "notified_users": []
        }
    
    async def _block_user_access(self, task: PendingTask, level: EscalationLevel) -> Dict[str, Any]:
        """Bloqueia acesso do usuário até resolução."""
        logger.warning(f"🔒 Bloqueando acesso devido à tarefa {task.title}")
        
        # Implementar bloqueio de acesso
        return {
            "success": True,
            "details": f"Acesso bloqueado até resolução da tarefa",
            "notified_users": [str(task.assigned_to)] if task.assigned_to else []
        }
    
    def _load_default_rules(self) -> List[EscalationRule]:
        """Carrega regras padrão de escalation."""
        return [
            # Compliance - Mais rigoroso
            EscalationRule(
                name="Compliance Critical",
                category=TaskCategory.COMPLIANCE,
                priority=TaskPriority.CRITICAL,
                level_1_days=1,
                level_2_days=2,
                level_3_days=3,
                level_4_days=5
            ),
            
            # Financeiro - Rigoroso
            EscalationRule(
                name="Financial Tasks",
                category=TaskCategory.FINANCIAL,
                level_1_days=1,
                level_2_days=3,
                level_3_days=7,
                level_4_days=10
            ),
            
            # Segurança - Muito rigoroso
            EscalationRule(
                name="Security Tasks",
                category=TaskCategory.SECURITY,
                level_1_days=1,
                level_2_days=2,
                level_3_days=5,
                level_4_days=7
            ),
            
            # Operacional - Moderado
            EscalationRule(
                name="Operational Tasks",
                category=TaskCategory.OPERATIONAL,
                level_1_days=3,
                level_2_days=7,
                level_3_days=14,
                level_4_days=21
            )
        ]
    
    def _get_actions_for_level(self, rule: EscalationRule, level: EscalationLevel) -> List[EscalationAction]:
        """Retorna ações para um nível específico."""
        if level == EscalationLevel.LEVEL_1:
            return rule.level_1_actions
        elif level == EscalationLevel.LEVEL_2:
            return rule.level_2_actions
        elif level == EscalationLevel.LEVEL_3:
            return rule.level_3_actions
        elif level == EscalationLevel.LEVEL_4:
            return rule.level_4_actions
        else:
            return [EscalationAction.NOTIFY_USER]
    
    def _get_default_rule(self) -> EscalationRule:
        """Retorna regra padrão genérica."""
        return EscalationRule(
            name="Default Rule",
            level_1_days=3,
            level_2_days=7,
            level_3_days=14,
            level_4_days=21
        )
    
    async def _get_upcoming_escalations(self) -> List[Dict[str, Any]]:
        """Lista tarefas que vão escalar em breve."""
        # Implementar lógica para prever escalations
        return []
