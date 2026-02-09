"""
Workflow Designer - Construtor visual de workflows.

Gerencia layout, conexoes e validacao de workflows visuais.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from modules._deprecated_workflows_dataclass.models.action import BUILTIN_ACTIONS, Action, ActionType
from modules._deprecated_workflows_dataclass.models.condition import Condition, ConditionType
from modules._deprecated_workflows_dataclass.models.trigger import Trigger, TriggerType
from modules._deprecated_workflows_dataclass.models.workflow import (
    Workflow,
    WorkflowCategory,
    WorkflowStatus,
)
from modules._deprecated_workflows_dataclass.models.workflow_step import (
    StepConnection,
    StepPosition,
    StepType,
    WorkflowStep,
)

logger = logging.getLogger(__name__)


@dataclass
class CanvasNode:
    """No do canvas visual."""

    id: str
    type: str  # step, trigger, action, condition
    position: StepPosition
    data: dict[str, Any] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass
class CanvasEdge:
    """Conexao entre nos do canvas."""

    id: str
    source_id: str
    target_id: str
    source_handle: str = "output"
    target_handle: str = "input"
    label: str = ""
    condition: str = ""
    animated: bool = False


@dataclass
class CanvasLayout:
    """Layout do canvas."""

    nodes: list[CanvasNode] = field(default_factory=list)
    edges: list[CanvasEdge] = field(default_factory=list)
    viewport: dict[str, float] = field(
        default_factory=lambda: {
            "x": 0,
            "y": 0,
            "zoom": 1,
        }
    )


class WorkflowDesigner:
    """
    Designer de workflows.

    Responsavel por:
    - Criar e editar workflows visualmente
    - Gerenciar layout de steps
    - Validar fluxo do workflow
    - Exportar/importar templates
    """

    # Configuracoes de layout
    STEP_WIDTH = 200
    STEP_HEIGHT = 80
    STEP_GAP_X = 100
    STEP_GAP_Y = 80
    START_X = 100
    START_Y = 100

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}
        self._steps: dict[str, WorkflowStep] = {}
        self._triggers: dict[str, Trigger] = {}
        self._actions: dict[str, Action] = {}
        self._conditions: dict[str, Condition] = {}

    def create_workflow(
        self,
        name: str,
        description: str = "",
        category: WorkflowCategory = WorkflowCategory.CUSTOM,
        tenant_id: str = "",
    ) -> Workflow:
        """Cria novo workflow."""
        workflow = Workflow(
            tenant_id=tenant_id,
            name=name,
            description=description,
            category=category,
        )

        # Adiciona steps iniciais (START e END)
        start_step = self.add_step(
            workflow,
            name="Inicio",
            step_type=StepType.START,
            position=StepPosition(x=self.START_X, y=self.START_Y),
        )

        end_step = self.add_step(
            workflow,
            name="Fim",
            step_type=StepType.END,
            position=StepPosition(
                x=self.START_X + self.STEP_WIDTH + self.STEP_GAP_X,
                y=self.START_Y,
            ),
        )

        # Conecta inicio ao fim
        self.connect_steps(workflow.id, start_step.id, end_step.id)

        self._workflows[workflow.id] = workflow
        return workflow

    def add_step(
        self,
        workflow: Workflow,
        name: str,
        step_type: StepType,
        position: StepPosition = None,
        action_id: str = None,
        condition_id: str = None,
    ) -> WorkflowStep:
        """Adiciona step ao workflow."""
        step = WorkflowStep(
            workflow_id=workflow.id,
            name=name,
            step_type=step_type,
            action_id=action_id,
            condition_id=condition_id,
            position=position or self._calculate_next_position(workflow),
            order=len(workflow.step_ids),
        )

        # Define icone e cor baseado no tipo
        step.icon, step.color = self._get_step_style(step_type)

        workflow.step_ids.append(step.id)
        self._steps[step.id] = step

        logger.info(f"Step {name} adicionado ao workflow {workflow.name}")
        return step

    def remove_step(self, workflow_id: str, step_id: str) -> bool:
        """Remove step do workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return False

        step = self._steps.get(step_id)
        if not step:
            return False

        # Nao permite remover START ou END
        if step.step_type in (StepType.START, StepType.END):
            logger.warning("Nao e possivel remover steps START ou END")
            return False

        # Remove conexoes
        for other_step in self._steps.values():
            if other_step.workflow_id == workflow_id:
                other_step.remove_connection(step_id)

        # Remove da lista
        if step_id in workflow.step_ids:
            workflow.step_ids.remove(step_id)

        del self._steps[step_id]
        return True

    def connect_steps(
        self,
        workflow_id: str,
        from_step_id: str,
        to_step_id: str,
        condition: str = "",
        label: str = "",
        is_default: bool = False,
    ) -> StepConnection | None:
        """Conecta dois steps."""
        from_step = self._steps.get(from_step_id)
        to_step = self._steps.get(to_step_id)

        if not from_step or not to_step:
            return None

        if from_step.workflow_id != workflow_id or to_step.workflow_id != workflow_id:
            return None

        # Nao permite conectar END a outro step
        if from_step.step_type == StepType.END:
            logger.warning("Step END nao pode ter conexoes de saida")
            return None

        # Nao permite conectar a START
        if to_step.step_type == StepType.START:
            logger.warning("Step START nao pode receber conexoes")
            return None

        connection = from_step.add_connection(
            to_step_id=to_step_id,
            condition=condition,
            label=label,
            is_default=is_default,
        )

        return connection

    def disconnect_steps(
        self,
        workflow_id: str,
        from_step_id: str,
        to_step_id: str,
    ) -> bool:
        """Remove conexao entre steps."""
        from_step = self._steps.get(from_step_id)
        if not from_step or from_step.workflow_id != workflow_id:
            return False

        return from_step.remove_connection(to_step_id)

    def move_step(
        self,
        step_id: str,
        x: float,
        y: float,
    ) -> bool:
        """Move step no canvas."""
        step = self._steps.get(step_id)
        if not step:
            return False

        step.set_position(x, y)
        return True

    def add_action_step(
        self,
        workflow: Workflow,
        action_type: ActionType,
        name: str = "",
        config: dict[str, Any] = None,
        position: StepPosition = None,
    ) -> tuple[WorkflowStep, Action]:
        """Adiciona step de acao com action configurada."""
        # Usa action builtin se existir
        builtin_key = action_type.value.replace("_", "_")
        builtin = BUILTIN_ACTIONS.get(builtin_key)

        if builtin:
            action = Action(
                name=name or builtin.name,
                action_type=action_type,
                icon=builtin.icon,
                color=builtin.color,
                category=builtin.category,
            )
        else:
            action = Action(
                name=name or action_type.value,
                action_type=action_type,
            )

        # Aplica configuracao
        if config:
            self._apply_action_config(action, config)

        self._actions[action.id] = action

        # Cria step
        step = self.add_step(
            workflow=workflow,
            name=action.name,
            step_type=StepType.ACTION,
            action_id=action.id,
            position=position,
        )
        step.icon = action.icon
        step.color = action.color

        return step, action

    def add_condition_step(
        self,
        workflow: Workflow,
        expression: str,
        name: str = "Condicao",
        true_step_id: str = "",
        false_step_id: str = "",
        position: StepPosition = None,
    ) -> tuple[WorkflowStep, Condition]:
        """Adiciona step de condicao."""
        condition = Condition(
            name=name,
            condition_type=ConditionType.EXPRESSION,
            expression=expression,
            true_step_id=true_step_id,
            false_step_id=false_step_id,
        )
        self._conditions[condition.id] = condition

        step = self.add_step(
            workflow=workflow,
            name=name,
            step_type=StepType.CONDITION,
            condition_id=condition.id,
            position=position,
        )

        return step, condition

    def add_trigger(
        self,
        workflow: Workflow,
        trigger_type: TriggerType,
        name: str = "",
        config: dict[str, Any] = None,
    ) -> Trigger:
        """Adiciona trigger ao workflow."""
        trigger = Trigger(
            workflow_id=workflow.id,
            name=name or f"Trigger {trigger_type.value}",
            trigger_type=trigger_type,
        )

        if config:
            self._apply_trigger_config(trigger, config)

        workflow.trigger_ids.append(trigger.id)
        self._triggers[trigger.id] = trigger

        return trigger

    def validate_workflow(self, workflow: Workflow) -> list[str]:
        """
        Valida workflow.

        Returns:
            Lista de erros encontrados
        """
        errors = []

        if not workflow.name:
            errors.append("Nome do workflow e obrigatorio")

        if not workflow.step_ids:
            errors.append("Workflow deve ter pelo menos um step")
            return errors

        # Verifica START
        start_count = sum(
            1 for sid in workflow.step_ids if self._steps.get(sid, WorkflowStep()).step_type == StepType.START
        )
        if start_count == 0:
            errors.append("Workflow deve ter um step START")
        elif start_count > 1:
            errors.append("Workflow deve ter apenas um step START")

        # Verifica END
        end_count = sum(
            1 for sid in workflow.step_ids if self._steps.get(sid, WorkflowStep()).step_type == StepType.END
        )
        if end_count == 0:
            errors.append("Workflow deve ter um step END")

        # Verifica conexoes
        for step_id in workflow.step_ids:
            step = self._steps.get(step_id)
            if not step:
                errors.append(f"Step {step_id} nao encontrado")
                continue

            # Steps que nao sao END devem ter conexao de saida
            if step.step_type not in (StepType.END, StepType.PARALLEL):
                if not step.next_step_ids and not step.connections:
                    errors.append(f"Step '{step.name}' nao tem conexao de saida")

            # Valida action
            if step.step_type == StepType.ACTION:
                if not step.action_id:
                    errors.append(f"Step '{step.name}' nao tem action configurada")
                elif step.action_id not in self._actions:
                    errors.append(f"Action {step.action_id} nao encontrada")

            # Valida condition
            if step.step_type == StepType.CONDITION:
                if not step.condition_id:
                    errors.append(f"Step '{step.name}' nao tem condition configurada")
                else:
                    condition = self._conditions.get(step.condition_id)
                    if not condition:
                        errors.append(f"Condition {step.condition_id} nao encontrada")
                    elif not condition.true_step_id or not condition.false_step_id:
                        errors.append(f"Condition '{step.name}' deve ter branches true e false")

        # Verifica ciclos (simplificado)
        visited = set()
        start_step = next(
            (
                self._steps[sid]
                for sid in workflow.step_ids
                if self._steps.get(sid, WorkflowStep()).step_type == StepType.START
            ),
            None,
        )

        if start_step:
            has_path_to_end = self._check_path_to_end(
                start_step.id,
                workflow.step_ids,
                visited,
            )
            if not has_path_to_end:
                errors.append("Workflow deve ter caminho do START ao END")

        return errors

    def _check_path_to_end(
        self,
        step_id: str,
        all_step_ids: list[str],
        visited: set,
    ) -> bool:
        """Verifica se ha caminho ate END (DFS)."""
        if step_id in visited:
            return False

        visited.add(step_id)
        step = self._steps.get(step_id)

        if not step:
            return False

        if step.step_type == StepType.END:
            return True

        for next_id in step.next_step_ids:
            if self._check_path_to_end(next_id, all_step_ids, visited):
                return True

        return False

    def get_canvas_layout(self, workflow: Workflow) -> CanvasLayout:
        """Gera layout do canvas para visualizacao."""
        layout = CanvasLayout()

        # Adiciona nodes
        for step_id in workflow.step_ids:
            step = self._steps.get(step_id)
            if not step:
                continue

            node = CanvasNode(
                id=step.id,
                type=f"step_{step.step_type.value}",
                position=step.position,
                data={
                    "name": step.name,
                    "step_type": step.step_type.value,
                    "icon": step.icon,
                    "color": step.color,
                    "action_id": step.action_id,
                    "condition_id": step.condition_id,
                },
            )
            layout.nodes.append(node)

            # Adiciona edges
            for conn in step.connections:
                edge = CanvasEdge(
                    id=f"{conn.from_step_id}_{conn.to_step_id}",
                    source_id=conn.from_step_id,
                    target_id=conn.to_step_id,
                    label=conn.label,
                    condition=conn.condition or "",
                    animated=step.step_type == StepType.CONDITION,
                )
                layout.edges.append(edge)

        # Usa canvas_data salvo se existir
        if workflow.canvas_data and "viewport" in workflow.canvas_data:
            layout.viewport = workflow.canvas_data["viewport"]

        return layout

    def apply_canvas_layout(
        self,
        workflow: Workflow,
        layout: CanvasLayout,
    ) -> None:
        """Aplica layout do canvas ao workflow."""
        for node in layout.nodes:
            step = self._steps.get(node.id)
            if step:
                step.position = node.position

        workflow.canvas_data = {
            "viewport": layout.viewport,
            "updated_at": datetime.utcnow().isoformat(),
        }

    def auto_layout(self, workflow: Workflow) -> CanvasLayout:
        """Calcula layout automatico."""
        layout = CanvasLayout()
        visited = set()
        levels: dict[int, list[str]] = {}  # nivel -> [step_ids]

        # Encontra START
        start_step = next(
            (
                self._steps[sid]
                for sid in workflow.step_ids
                if self._steps.get(sid, WorkflowStep()).step_type == StepType.START
            ),
            None,
        )

        if not start_step:
            return layout

        # Organiza por niveis (BFS)
        self._assign_levels(start_step.id, 0, levels, visited)

        # Posiciona nodes
        for level, step_ids in levels.items():
            x = self.START_X + level * (self.STEP_WIDTH + self.STEP_GAP_X)

            for i, step_id in enumerate(step_ids):
                y = self.START_Y + i * (self.STEP_HEIGHT + self.STEP_GAP_Y)
                step = self._steps.get(step_id)
                if step:
                    step.set_position(x, y)

        return self.get_canvas_layout(workflow)

    def _assign_levels(
        self,
        step_id: str,
        level: int,
        levels: dict[int, list[str]],
        visited: set,
    ) -> None:
        """Atribui niveis para layout."""
        if step_id in visited:
            return

        visited.add(step_id)

        if level not in levels:
            levels[level] = []
        levels[level].append(step_id)

        step = self._steps.get(step_id)
        if step:
            for next_id in step.next_step_ids:
                self._assign_levels(next_id, level + 1, levels, visited)

    def export_workflow(self, workflow: Workflow) -> dict[str, Any]:
        """Exporta workflow para JSON."""
        steps = [self._steps[sid].to_dict() for sid in workflow.step_ids if sid in self._steps]

        actions = {
            aid: self._actions[aid].to_dict()
            for step in steps
            if step.get("action_id")
            for aid in [step["action_id"]]
            if aid in self._actions
        }

        conditions = {
            cid: self._conditions[cid].to_dict()
            for step in steps
            if step.get("condition_id")
            for cid in [step["condition_id"]]
            if cid in self._conditions
        }

        triggers = [self._triggers[tid].to_dict() for tid in workflow.trigger_ids if tid in self._triggers]

        return {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "workflow": workflow.to_dict(),
            "steps": steps,
            "actions": actions,
            "conditions": conditions,
            "triggers": triggers,
        }

    def import_workflow(
        self,
        data: dict[str, Any],
        tenant_id: str,
        new_name: str = None,
    ) -> Workflow:
        """Importa workflow de JSON."""
        workflow_data = data.get("workflow", {})

        workflow = Workflow.from_dict(workflow_data)
        workflow.id = str(uuid.uuid4())  # Novo ID
        workflow.tenant_id = tenant_id
        if new_name:
            workflow.name = new_name
        workflow.status = WorkflowStatus.DRAFT
        workflow.step_ids = []

        # Mapeamento de IDs antigos para novos
        id_map: dict[str, str] = {}

        # Importa steps
        for step_data in data.get("steps", []):
            old_id = step_data.get("id")
            step = WorkflowStep.from_dict(step_data)
            step.id = str(uuid.uuid4())
            step.workflow_id = workflow.id
            id_map[old_id] = step.id

            workflow.step_ids.append(step.id)
            self._steps[step.id] = step

        # Atualiza referencias
        for step in [self._steps[sid] for sid in workflow.step_ids]:
            step.next_step_ids = [id_map.get(sid, sid) for sid in step.next_step_ids]
            for conn in step.connections:
                conn.from_step_id = id_map.get(conn.from_step_id, conn.from_step_id)
                conn.to_step_id = id_map.get(conn.to_step_id, conn.to_step_id)

        # Importa actions
        for old_id, action_data in data.get("actions", {}).items():
            action = Action.from_dict(action_data)
            action.id = str(uuid.uuid4())
            id_map[old_id] = action.id
            self._actions[action.id] = action

        # Atualiza action_ids nos steps
        for step in [self._steps[sid] for sid in workflow.step_ids]:
            if step.action_id and step.action_id in id_map:
                step.action_id = id_map[step.action_id]

        self._workflows[workflow.id] = workflow
        return workflow

    def _calculate_next_position(self, workflow: Workflow) -> StepPosition:
        """Calcula posicao para novo step."""
        if not workflow.step_ids:
            return StepPosition(x=self.START_X, y=self.START_Y)

        # Encontra posicao mais a direita
        max_x = self.START_X
        max_y = self.START_Y

        for step_id in workflow.step_ids:
            step = self._steps.get(step_id)
            if step:
                max_x = max(max_x, step.position.x)
                max_y = max(max_y, step.position.y)

        return StepPosition(
            x=max_x + self.STEP_WIDTH + self.STEP_GAP_X,
            y=self.START_Y,
        )

    def _get_step_style(self, step_type: StepType) -> tuple[str, str]:
        """Retorna icone e cor para tipo de step."""
        styles = {
            StepType.START: ("play", "#10B981"),
            StepType.END: ("stop", "#EF4444"),
            StepType.ACTION: ("zap", "#3B82F6"),
            StepType.CONDITION: ("git-branch", "#8B5CF6"),
            StepType.LOOP: ("repeat", "#F59E0B"),
            StepType.PARALLEL: ("git-merge", "#EC4899"),
            StepType.DELAY: ("clock", "#6B7280"),
            StepType.SUBPROCESS: ("box", "#14B8A6"),
            StepType.ERROR_HANDLER: ("alert-triangle", "#EF4444"),
        }
        return styles.get(step_type, ("circle", "#6B7280"))

    def _apply_action_config(self, action: Action, config: dict[str, Any]) -> None:
        """Aplica configuracao a action."""
        from modules._deprecated_workflows_dataclass.models.action import (
            EmailConfig,
            HTTPConfig,
            TaskConfig,
            WhatsAppConfig,
        )

        if action.action_type == ActionType.SEND_EMAIL and "email" in config:
            action.email_config = EmailConfig(**config["email"])

        elif action.action_type == ActionType.SEND_WHATSAPP and "whatsapp" in config:
            action.whatsapp_config = WhatsAppConfig(**config["whatsapp"])

        elif action.action_type in (ActionType.HTTP_REQUEST, ActionType.WEBHOOK):
            if "http" in config:
                action.http_config = HTTPConfig(**config["http"])

        elif action.action_type == ActionType.CREATE_TASK and "task" in config:
            action.task_config = TaskConfig(**config["task"])

    def _apply_trigger_config(self, trigger: Trigger, config: dict[str, Any]) -> None:
        """Aplica configuracao a trigger."""
        from modules._deprecated_workflows_dataclass.models.trigger import (
            ScheduleConfig,
            TriggerEvent,
            WebhookConfig,
        )

        if "event" in config:
            trigger.event = TriggerEvent(config["event"])

        if "schedule" in config:
            trigger.schedule_config = ScheduleConfig(**config["schedule"])

        if "webhook" in config:
            trigger.webhook_config = WebhookConfig(**config["webhook"])

        if "filter_conditions" in config:
            trigger.filter_conditions = config["filter_conditions"]
