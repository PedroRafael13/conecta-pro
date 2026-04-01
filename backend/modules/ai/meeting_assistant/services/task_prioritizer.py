"""
Task Prioritizer Service - Sprint 49.

Serviço de priorização inteligente de tarefas.
"""

import uuid
from datetime import datetime
from typing import Any

from modules.ai.meeting_assistant.models import (
    DependencyTypeEnum,
    Task,
    TaskDependency,
    TaskPriorityEnum,
    TaskStatusEnum,
    TaskTypeEnum,
)
from modules.ai.meeting_assistant.schemas import TaskPrioritySuggestion


class TaskPrioritizer:
    """Serviço de priorização de tarefas."""

    def __init__(self):
        self.weights = {
            "deadline": 0.30,
            "dependencies": 0.20,
            "task_type": 0.15,
            "visibility": 0.10,
            "age": 0.10,
            "effort": 0.10,
            "context": 0.05,
        }

    def calculate_priority(self, task: Task, dependencies: list[TaskDependency] = None) -> dict[str, Any]:
        """
        Calcula prioridade de uma tarefa.

        Args:
            task: Tarefa a ser avaliada
            dependencies: Dependências da tarefa

        Returns:
            Dict com score, prioridade sugerida e fatores
        """
        factors = {}
        scores = {}

        # 1. Fator Prazo (Deadline)
        deadline_score = self._calculate_deadline_score(task)
        scores["deadline"] = deadline_score
        factors["deadline"] = self._get_deadline_factor(task)

        # 2. Fator Dependências
        dependency_score = self._calculate_dependency_score(task, dependencies)
        scores["dependencies"] = dependency_score
        factors["dependencies"] = self._get_dependency_factor(task, dependencies)

        # 3. Fator Tipo de Tarefa
        type_score = self._calculate_type_score(task)
        scores["task_type"] = type_score
        factors["task_type"] = {"type": task.task_type.value, "score": type_score}

        # 4. Fator Visibilidade
        visibility_score = self._calculate_visibility_score(task)
        scores["visibility"] = visibility_score
        factors["visibility"] = self._get_visibility_factor(task)

        # 5. Fator Idade
        age_score = self._calculate_age_score(task)
        scores["age"] = age_score
        factors["age"] = self._get_age_factor(task)

        # 6. Fator Esforço
        effort_score = self._calculate_effort_score(task)
        scores["effort"] = effort_score
        factors["effort"] = self._get_effort_factor(task)

        # 7. Fator Contexto
        context_score = self._calculate_context_score(task)
        scores["context"] = context_score
        factors["context"] = {"has_context": bool(task.context)}

        # Calcula score final ponderado
        final_score = sum(scores[factor] * self.weights[factor] for factor in scores)

        # Normaliza para 0-100
        final_score = min(100, max(0, final_score))

        # Determina prioridade sugerida
        suggested_priority = self._score_to_priority(final_score)

        return {
            "score": round(final_score, 2),
            "suggested_priority": suggested_priority,
            "factors": factors,
            "scores": scores,
        }

    def prioritize_tasks(
        self, tasks: list[Task], dependencies_map: dict[uuid.UUID, list[TaskDependency]] = None
    ) -> list[TaskPrioritySuggestion]:
        """
        Prioriza lista de tarefas.

        Args:
            tasks: Lista de tarefas
            dependencies_map: Mapa de dependências por tarefa

        Returns:
            Lista de sugestões de prioridade ordenadas
        """
        suggestions = []

        for task in tasks:
            deps = dependencies_map.get(task.id, []) if dependencies_map else []
            result = self.calculate_priority(task, deps)

            suggestion = TaskPrioritySuggestion(
                task_id=task.id,
                task_code=task.task_code,
                current_priority=task.priority,
                suggested_priority=result["suggested_priority"],
                priority_score=result["score"],
                factors=result["factors"],
                recommendation=self._generate_recommendation(task, result),
            )
            suggestions.append(suggestion)

        # Ordena por score
        suggestions.sort(key=lambda x: x.priority_score, reverse=True)

        return suggestions

    def _calculate_deadline_score(self, task: Task) -> float:
        """Calcula score baseado no prazo."""
        if not task.due_date:
            return 50  # Score neutro se não tem prazo

        now = datetime.utcnow()
        days_until_due = (task.due_date - now).days

        if days_until_due < 0:
            # Atrasado
            return 100
        elif days_until_due == 0:
            # Vence hoje
            return 95
        elif days_until_due <= 1:
            # Vence amanhã
            return 90
        elif days_until_due <= 3:
            # Vence em 3 dias
            return 80
        elif days_until_due <= 7:
            # Vence essa semana
            return 65
        elif days_until_due <= 14:
            # Vence em 2 semanas
            return 45
        else:
            return 30

    def _get_deadline_factor(self, task: Task) -> dict[str, Any]:
        """Retorna fator de prazo."""
        if not task.due_date:
            return {"has_deadline": False}

        now = datetime.utcnow()
        days_until = (task.due_date - now).days

        return {
            "has_deadline": True,
            "due_date": task.due_date.isoformat(),
            "days_until_due": days_until,
            "is_overdue": days_until < 0,
        }

    def _calculate_dependency_score(self, task: Task, dependencies: list[TaskDependency] = None) -> float:
        """Calcula score baseado em dependências."""
        if task.is_blocked:
            return 20  # Baixa prioridade se bloqueado

        if not dependencies:
            return 50

        blocking_count = 0
        blocked_by_count = 0

        for dep in dependencies:
            if dep.task_id == task.id:
                if dep.dependency_type == DependencyTypeEnum.BLOCKS:
                    blocking_count += 1
            elif dep.related_task_id == task.id:
                if dep.dependency_type == DependencyTypeEnum.BLOCKED_BY:
                    blocked_by_count += 1

        # Tarefas que bloqueiam outras têm maior prioridade
        score = 50 + (blocking_count * 15) - (blocked_by_count * 10)
        return min(100, max(0, score))

    def _get_dependency_factor(self, task: Task, dependencies: list[TaskDependency] = None) -> dict[str, Any]:
        """Retorna fator de dependências."""
        return {
            "is_blocked": task.is_blocked,
            "blocked_reason": task.blocked_reason,
            "dependency_count": len(dependencies) if dependencies else 0,
        }

    def _calculate_type_score(self, task: Task) -> float:
        """Calcula score baseado no tipo."""
        type_scores = {
            TaskTypeEnum.BUG: 85,
            TaskTypeEnum.FEATURE: 60,
            TaskTypeEnum.IMPROVEMENT: 50,
            TaskTypeEnum.MAINTENANCE: 55,
            TaskTypeEnum.DOCUMENTATION: 35,
            TaskTypeEnum.RESEARCH: 40,
            TaskTypeEnum.MEETING_ACTION: 70,
            TaskTypeEnum.FOLLOW_UP: 65,
            TaskTypeEnum.TASK: 50,
            TaskTypeEnum.STORY: 55,
            TaskTypeEnum.EPIC: 45,
            TaskTypeEnum.SUBTASK: 50,
        }
        return type_scores.get(task.task_type, 50)

    def _calculate_visibility_score(self, task: Task) -> float:
        """Calcula score baseado na visibilidade."""
        score = 50

        # Watchers aumentam visibilidade
        if task.watchers:
            watcher_count = len(task.watchers)
            score += min(30, watcher_count * 5)

        # Projeto importante
        if task.project_id:
            score += 10

        return min(100, score)

    def _get_visibility_factor(self, task: Task) -> dict[str, Any]:
        """Retorna fator de visibilidade."""
        return {
            "watcher_count": len(task.watchers) if task.watchers else 0,
            "has_project": bool(task.project_id),
            "comments_count": task.comments_count or 0,
        }

    def _calculate_age_score(self, task: Task) -> float:
        """Calcula score baseado na idade da tarefa."""
        age_days = (datetime.utcnow() - task.created_at).days

        if age_days > 30:
            return 80  # Tarefas antigas precisam atenção
        elif age_days > 14:
            return 65
        elif age_days > 7:
            return 50
        else:
            return 40

    def _get_age_factor(self, task: Task) -> dict[str, Any]:
        """Retorna fator de idade."""
        age_days = (datetime.utcnow() - task.created_at).days
        return {"created_at": task.created_at.isoformat(), "age_days": age_days, "is_stale": age_days > 14}

    def _calculate_effort_score(self, task: Task) -> float:
        """Calcula score baseado no esforço estimado."""
        if not task.estimated_hours:
            return 50

        # Tarefas menores podem ser priorizadas (quick wins)
        if task.estimated_hours <= 2:
            return 70  # Quick wins
        elif task.estimated_hours <= 8:
            return 55  # Tarefas médias
        else:
            return 40  # Tarefas grandes

    def _get_effort_factor(self, task: Task) -> dict[str, Any]:
        """Retorna fator de esforço."""
        return {
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "story_points": task.story_points,
            "progress": task.progress_percentage,
        }

    def _calculate_context_score(self, task: Task) -> float:
        """Calcula score baseado no contexto."""
        score = 50

        # Tarefa veio de reunião
        if task.meeting_id:
            score += 20

        # Tem critérios de aceitação claros
        if task.acceptance_criteria and len(task.acceptance_criteria) > 0:
            score += 10

        # Tem contexto definido
        if task.context:
            score += 10

        return min(100, score)

    def _score_to_priority(self, score: float) -> TaskPriorityEnum:
        """Converte score para prioridade."""
        if score >= 80:
            return TaskPriorityEnum.CRITICAL
        elif score >= 60:
            return TaskPriorityEnum.HIGH
        elif score >= 40:
            return TaskPriorityEnum.MEDIUM
        elif score >= 20:
            return TaskPriorityEnum.LOW
        else:
            return TaskPriorityEnum.NONE

    def _generate_recommendation(self, task: Task, result: dict[str, Any]) -> str:
        """Gera recomendação textual."""
        recommendations = []

        # Verifica prazo
        deadline_factor = result["factors"].get("deadline", {})
        if deadline_factor.get("is_overdue"):
            recommendations.append("URGENTE: Tarefa atrasada!")
        elif deadline_factor.get("days_until_due", 999) <= 1:
            recommendations.append("Prazo iminente")

        # Verifica bloqueio
        if task.is_blocked:
            recommendations.append(f"Bloqueada: {task.blocked_reason}")

        # Verifica mudança de prioridade
        if result["suggested_priority"] != task.priority:
            recommendations.append(
                f"Considere alterar prioridade de {task.priority.value} para {result['suggested_priority'].value}"
            )

        # Verifica idade
        age_factor = result["factors"].get("age", {})
        if age_factor.get("is_stale"):
            recommendations.append("Tarefa antiga - revisar necessidade")

        if not recommendations:
            return "Prioridade adequada"

        return "; ".join(recommendations)

    def suggest_next_tasks(self, tasks: list[Task], assignee_id: uuid.UUID = None, limit: int = 5) -> list[Task]:
        """
        Sugere próximas tarefas a serem trabalhadas.

        Returns:
            Lista de tarefas sugeridas
        """
        # Filtra tarefas elegíveis
        eligible = [
            t
            for t in tasks
            if t.status in [TaskStatusEnum.TODO, TaskStatusEnum.BACKLOG]
            and not t.is_blocked
            and (assignee_id is None or t.assignee_id == assignee_id)
        ]

        # Prioriza
        suggestions = self.prioritize_tasks(eligible)

        # Retorna top N
        return [next(t for t in tasks if t.id == s.task_id) for s in suggestions[:limit]]
