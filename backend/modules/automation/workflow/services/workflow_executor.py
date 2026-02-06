"""
Workflow Executor - Engine de execucao de workflows.

Orquestra a execucao de workflows, steps e acoes.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
import uuid

from modules._deprecated_workflows_dataclass.models.workflow import Workflow, WorkflowStatus
from modules._deprecated_workflows_dataclass.models.workflow_step import StepType, WorkflowStep
from modules._deprecated_workflows_dataclass.models.trigger import Trigger
from modules._deprecated_workflows_dataclass.models.action import Action, ActionResult
from modules._deprecated_workflows_dataclass.models.condition import Condition
from modules._deprecated_workflows_dataclass.models.execution import (
    ExecutionLog,
    ExecutionStatus,
    LogLevel,
    StepExecution,
    WorkflowExecution,
)
from modules._deprecated_workflows_dataclass.services.action_executor import ActionExecutor
from modules._deprecated_workflows_dataclass.services.condition_evaluator import ConditionEvaluator

logger = logging.getLogger(__name__)


class ExecutionContext:
    """Contexto de execucao do workflow."""

    def __init__(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        input_data: Dict[str, Any] = None,
    ):
        self.workflow = workflow
        self.execution = execution
        self.variables: Dict[str, Any] = {}
        self.input = input_data or {}
        self.output: Dict[str, Any] = {}
        self.step_outputs: Dict[str, Dict[str, Any]] = {}
        self.current_step_id: str = ""
        self.loop_stack: List[Dict[str, Any]] = []

        # Inicializa variaveis do workflow
        for var in workflow.variables:
            self.variables[var.name] = var.default_value

    def get_full_context(self) -> Dict[str, Any]:
        """Retorna contexto completo."""
        return {
            "workflow_id": self.workflow.id,
            "execution_id": self.execution.id,
            "variables": self.variables,
            "input": self.input,
            "output": self.output,
            "step_outputs": self.step_outputs,
            "current_step_id": self.current_step_id,
            "loop": self.loop_stack[-1] if self.loop_stack else {},
        }

    def set_variable(self, name: str, value: Any) -> None:
        """Define variavel."""
        self.variables[name] = value
        self.execution.set_variable(name, value)

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Obtem variavel."""
        return self.variables.get(name, default)

    def set_step_output(self, step_id: str, output: Dict[str, Any]) -> None:
        """Define output de step."""
        self.step_outputs[step_id] = output

    def enter_loop(self, collection: List[Any], variable: str, index_var: str) -> None:
        """Entra em loop."""
        self.loop_stack.append({
            "collection": collection,
            "variable": variable,
            "index_var": index_var,
            "index": 0,
            "item": collection[0] if collection else None,
        })

    def next_iteration(self) -> bool:
        """Avanca para proxima iteracao."""
        if not self.loop_stack:
            return False

        loop = self.loop_stack[-1]
        loop["index"] += 1

        if loop["index"] >= len(loop["collection"]):
            return False

        loop["item"] = loop["collection"][loop["index"]]
        self.variables[loop["variable"]] = loop["item"]
        self.variables[loop["index_var"]] = loop["index"]

        return True

    def exit_loop(self) -> None:
        """Sai do loop atual."""
        if self.loop_stack:
            self.loop_stack.pop()


class WorkflowExecutor:
    """
    Executor de workflows.

    Responsavel por:
    - Iniciar e gerenciar execucoes
    - Processar steps sequencialmente ou em paralelo
    - Gerenciar loops e condicoes
    - Tratar erros e retries
    """

    def __init__(
        self,
        action_executor: ActionExecutor = None,
        condition_evaluator: ConditionEvaluator = None,
    ):
        self.action_executor = action_executor or ActionExecutor()
        self.condition_evaluator = condition_evaluator or ConditionEvaluator()

        # Storage (em producao, usar repositorio)
        self._workflows: Dict[str, Workflow] = {}
        self._steps: Dict[str, WorkflowStep] = {}
        self._actions: Dict[str, Action] = {}
        self._conditions: Dict[str, Condition] = {}
        self._executions: Dict[str, WorkflowExecution] = {}

        # Callbacks
        self._on_execution_start: Optional[Callable] = None
        self._on_execution_complete: Optional[Callable] = None
        self._on_step_complete: Optional[Callable] = None

    def register_workflow(
        self,
        workflow: Workflow,
        steps: List[WorkflowStep],
        actions: Dict[str, Action] = None,
        conditions: Dict[str, Condition] = None,
    ) -> None:
        """Registra workflow para execucao."""
        self._workflows[workflow.id] = workflow

        for step in steps:
            step.workflow_id = workflow.id
            self._steps[step.id] = step

        if actions:
            self._actions.update(actions)

        if conditions:
            self._conditions.update(conditions)

        logger.info(f"Workflow {workflow.name} registrado com {len(steps)} steps")

    async def execute(
        self,
        workflow_id: str,
        input_data: Dict[str, Any] = None,
        trigger_id: str = "",
        triggered_by: str = "system",
    ) -> str:
        """
        Inicia execucao de workflow.

        Args:
            workflow_id: ID do workflow
            input_data: Dados de entrada
            trigger_id: ID do trigger que disparou
            triggered_by: Quem/o que disparou

        Returns:
            ID da execucao
        """
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} nao encontrado")

        if not workflow.can_execute:
            raise ValueError(f"Workflow {workflow_id} nao pode executar")

        # Cria execucao
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            workflow_version=workflow.version,
            tenant_id=workflow.tenant_id,
            trigger_id=trigger_id,
            triggered_by=triggered_by,
            input_data=input_data or {},
            steps_total=len(workflow.step_ids),
        )

        self._executions[execution.id] = execution

        # Inicia execucao em background
        asyncio.create_task(self._run_execution(workflow, execution, input_data))

        logger.info(f"Execucao {execution.id} iniciada para workflow {workflow.name}")
        return execution.id

    async def _run_execution(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        input_data: Dict[str, Any],
    ) -> None:
        """Executa workflow."""
        # Cria contexto
        context = ExecutionContext(workflow, execution, input_data)

        try:
            execution.start()

            if self._on_execution_start:
                await self._on_execution_start(execution)

            # Encontra step inicial
            start_step_id = self._find_start_step(workflow)
            if not start_step_id:
                raise ValueError("Step inicial nao encontrado")

            # Executa steps
            await self._execute_step(start_step_id, context)

            # Completa execucao
            if execution.status == ExecutionStatus.RUNNING:
                execution.complete(context.output)
                workflow.update_statistics(True, execution.duration_ms)

        except Exception as e:
            logger.error(f"Erro na execucao {execution.id}: {e}")
            execution.fail(str(e), context.current_step_id)
            workflow.update_statistics(False, execution.duration_ms)

        finally:
            if self._on_execution_complete:
                await self._on_execution_complete(execution)

    async def _execute_step(
        self,
        step_id: str,
        context: ExecutionContext,
    ) -> Optional[str]:
        """
        Executa um step do workflow.

        Args:
            step_id: ID do step
            context: Contexto de execucao

        Returns:
            ID do proximo step ou None
        """
        step = self._steps.get(step_id)
        if not step:
            logger.warning(f"Step {step_id} nao encontrado")
            return None

        if not step.is_enabled:
            logger.info(f"Step {step_id} desabilitado, pulando")
            return step.get_next_step()

        context.current_step_id = step_id
        context.execution.current_step_id = step_id

        # Cria execucao do step
        step_exec = StepExecution(
            execution_id=context.execution.id,
            step_id=step_id,
            step_name=step.name,
            input_data=context.get_full_context(),
        )
        step_exec.start()
        context.execution.add_step_execution(step_exec)

        try:
            # Timeout do step
            async with asyncio.timeout(step.timeout_seconds):
                next_step_id = await self._process_step(step, context, step_exec)

        except asyncio.TimeoutError:
            step_exec.fail("Timeout na execucao do step")
            if step.on_error == "continue":
                next_step_id = step.get_next_step()
            elif step.error_handler_step_id:
                next_step_id = step.error_handler_step_id
            else:
                raise

        except Exception as e:
            step_exec.fail(str(e))

            if step.on_error == "retry" and step_exec.retry():
                # Aguarda e tenta novamente
                await asyncio.sleep(step.retry_delay_seconds)
                return await self._execute_step(step_id, context)

            elif step.on_error == "continue":
                next_step_id = step.get_next_step()

            elif step.error_handler_step_id:
                next_step_id = step.error_handler_step_id

            else:
                raise

        # Atualiza contexto
        if step_exec.success and step_exec.output_data:
            context.set_step_output(step_id, step_exec.output_data)

            # Aplica output mapping
            if step.output_mapping:
                for target, source in step.output_mapping.items():
                    value = step_exec.output_data.get(source)
                    if value is not None:
                        context.set_variable(target, value)

        # Callback
        if self._on_step_complete:
            await self._on_step_complete(step_exec)

        # Processa proximo step
        if next_step_id:
            return await self._execute_step(next_step_id, context)

        return None

    async def _process_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        step_exec: StepExecution,
    ) -> Optional[str]:
        """Processa step baseado no tipo."""
        if step.step_type == StepType.START:
            step_exec.complete()
            return step.get_next_step()

        elif step.step_type == StepType.END:
            step_exec.complete()
            context.output = context.get_full_context()
            return None

        elif step.step_type == StepType.ACTION:
            return await self._process_action_step(step, context, step_exec)

        elif step.step_type == StepType.CONDITION:
            return await self._process_condition_step(step, context, step_exec)

        elif step.step_type == StepType.LOOP:
            return await self._process_loop_step(step, context, step_exec)

        elif step.step_type == StepType.PARALLEL:
            return await self._process_parallel_step(step, context, step_exec)

        elif step.step_type == StepType.DELAY:
            return await self._process_delay_step(step, context, step_exec)

        elif step.step_type == StepType.SUBPROCESS:
            return await self._process_subprocess_step(step, context, step_exec)

        else:
            step_exec.complete()
            return step.get_next_step()

    async def _process_action_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        step_exec: StepExecution,
    ) -> Optional[str]:
        """Processa step de acao."""
        action = self._actions.get(step.action_id)
        if not action:
            raise ValueError(f"Action {step.action_id} nao encontrada")

        # Aplica input mapping
        action_context = context.get_full_context()
        if step.input_mapping:
            for target, source in step.input_mapping.items():
                value = self._resolve_path(source, action_context)
                if value is not None:
                    action_context[target] = value

        # Executa acao
        result = await self.action_executor.execute(action, action_context)

        if result.success:
            step_exec.complete(result.output)
        else:
            step_exec.fail(result.error, result.error_details)
            if step.on_error != "continue":
                raise Exception(result.error)

        return step.get_next_step()

    async def _process_condition_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        step_exec: StepExecution,
    ) -> Optional[str]:
        """Processa step de condicao."""
        condition = self._conditions.get(step.condition_id)
        if not condition:
            raise ValueError(f"Condition {step.condition_id} nao encontrada")

        # Avalia condicao
        cond_context = context.get_full_context()
        next_step_id = self.condition_evaluator.get_next_step(condition, cond_context)

        step_exec.complete({
            "condition_result": next_step_id == condition.true_step_id,
            "next_step_id": next_step_id,
        })

        return next_step_id

    async def _process_loop_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        step_exec: StepExecution,
    ) -> Optional[str]:
        """Processa step de loop."""
        # Obtem colecao
        full_context = context.get_full_context()
        collection = self._resolve_path(step.loop_collection, full_context)

        if not isinstance(collection, list):
            collection = list(collection) if collection else []

        if not collection:
            step_exec.complete({"iterations": 0})
            return step.get_next_step()

        # Limita iteracoes
        if len(collection) > step.max_iterations:
            collection = collection[:step.max_iterations]

        # Entra no loop
        context.enter_loop(collection, step.loop_variable, step.loop_index_variable)

        iterations = 0
        loop_outputs = []

        try:
            while True:
                # Define variaveis de loop
                loop_data = context.loop_stack[-1]
                context.set_variable(step.loop_variable, loop_data["item"])
                context.set_variable(step.loop_index_variable, loop_data["index"])

                # Executa steps internos
                for inner_step_id in step.next_step_ids:
                    await self._execute_step(inner_step_id, context)

                loop_outputs.append(context.get_full_context().get("output", {}))
                iterations += 1

                # Proxima iteracao
                if not context.next_iteration():
                    break

        finally:
            context.exit_loop()

        step_exec.complete({
            "iterations": iterations,
            "outputs": loop_outputs,
        })

        # Retorna step apos o loop (ultimo da lista ou definido)
        return step.get_next_step()

    async def _process_parallel_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        step_exec: StepExecution,
    ) -> Optional[str]:
        """Processa step paralelo."""
        if not step.parallel_step_ids:
            step_exec.complete()
            return step.get_next_step()

        # Cria tasks paralelas
        tasks = []
        for parallel_id in step.parallel_step_ids:
            # Copia contexto para cada branch
            branch_context = ExecutionContext(
                context.workflow,
                context.execution,
                context.input.copy(),
            )
            branch_context.variables = context.variables.copy()

            tasks.append(self._execute_step(parallel_id, branch_context))

        # Executa em paralelo
        if step.wait_for_all:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            errors = [r for r in results if isinstance(r, Exception)]
            if errors:
                raise errors[0]
        else:
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        step_exec.complete({"parallel_branches": len(tasks)})
        return step.get_next_step()

    async def _process_delay_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        step_exec: StepExecution,
    ) -> Optional[str]:
        """Processa step de delay."""
        delay_seconds = step.delay_seconds

        # Delay dinamico
        if step.delay_expression:
            full_context = context.get_full_context()
            try:
                delay_seconds = int(self._resolve_path(
                    step.delay_expression,
                    full_context,
                ) or 0)
            except (TypeError, ValueError):
                pass

        # Delay ate data/hora especifica
        if step.delay_until:
            now = datetime.utcnow()
            if step.delay_until > now:
                delay_seconds = int((step.delay_until - now).total_seconds())

        if delay_seconds > 0:
            step_exec.add_log(
                f"Aguardando {delay_seconds} segundos",
                LogLevel.INFO,
            )
            await asyncio.sleep(delay_seconds)

        step_exec.complete({"delayed_seconds": delay_seconds})
        return step.get_next_step()

    async def _process_subprocess_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        step_exec: StepExecution,
    ) -> Optional[str]:
        """Processa step de subprocess (workflow aninhado)."""
        if not step.subprocess_workflow_id:
            raise ValueError("Subprocess workflow ID ausente")

        # Executa workflow filho
        exec_id = await self.execute(
            workflow_id=step.subprocess_workflow_id,
            input_data=context.get_full_context(),
            triggered_by=f"subprocess:{context.execution.id}",
        )

        # Aguarda conclusao (simplificado)
        for _ in range(step.timeout_seconds):
            child_exec = self._executions.get(exec_id)
            if child_exec and child_exec.is_finished:
                if child_exec.success:
                    step_exec.complete(child_exec.output_data)
                else:
                    step_exec.fail(child_exec.error)
                break
            await asyncio.sleep(1)
        else:
            step_exec.fail("Timeout aguardando subprocess")

        return step.get_next_step()

    def _find_start_step(self, workflow: Workflow) -> Optional[str]:
        """Encontra step inicial."""
        for step_id in workflow.step_ids:
            step = self._steps.get(step_id)
            if step and step.step_type == StepType.START:
                return step_id

        # Se nao tem START, usa primeiro step
        return workflow.step_ids[0] if workflow.step_ids else None

    def _resolve_path(self, path: str, context: Dict[str, Any]) -> Any:
        """Resolve path de variavel."""
        if not path:
            return None

        if path.startswith("$."):
            path = path[2:]

        parts = path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list):
                try:
                    idx = int(part)
                    value = value[idx]
                except (ValueError, IndexError):
                    return None
            else:
                return None

        return value

    # API de gerenciamento

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Obtem execucao por ID."""
        return self._executions.get(execution_id)

    def get_executions(
        self,
        workflow_id: str = None,
        status: ExecutionStatus = None,
        limit: int = 100,
    ) -> List[WorkflowExecution]:
        """Lista execucoes."""
        executions = list(self._executions.values())

        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]

        if status:
            executions = [e for e in executions if e.status == status]

        # Ordena por data de criacao (mais recente primeiro)
        executions.sort(key=lambda e: e.created_at, reverse=True)

        return executions[:limit]

    async def cancel_execution(self, execution_id: str, reason: str = "") -> bool:
        """Cancela execucao."""
        execution = self._executions.get(execution_id)
        if not execution:
            return False

        if execution.is_finished:
            return False

        execution.cancel(reason)
        return True

    async def retry_execution(self, execution_id: str) -> Optional[str]:
        """Retenta execucao falha."""
        execution = self._executions.get(execution_id)
        if not execution:
            return None

        if execution.status != ExecutionStatus.FAILED:
            return None

        # Cria nova execucao
        return await self.execute(
            workflow_id=execution.workflow_id,
            input_data=execution.input_data,
            trigger_id=execution.trigger_id,
            triggered_by=f"retry:{execution_id}",
        )
