"""Workflow Engine - Motor de Execucao de Workflows.

Sprint 33 - Workflow Engine.
"""

import asyncio
import re
import time
import traceback
from dataclasses import dataclass, field as dataclass_field
from typing import Any, Callable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.automation.workflow.models.workflow import Workflow
from modules.automation.workflow.models.workflow_execution import (
    ExecutionStatus,
    WorkflowExecution,
)
from modules.automation.workflow.models.workflow_log import LogLevel, LogType, WorkflowLog
from modules.automation.workflow.models.workflow_step import StepType, WorkflowStep
from modules.automation.workflow.models.workflow_trigger import WorkflowTrigger


@dataclass
class StepResult:
    """Resultado de execucao de step."""

    success: bool
    output: dict = dataclass_field(default_factory=dict)
    next_step_id: Optional[str] = None
    error_message: Optional[str] = None
    should_continue: bool = True


@dataclass
class ExecutionContext:
    """Contexto de execucao."""

    tenant_id: UUID
    execution_id: UUID
    workflow_id: UUID
    variables: dict = dataclass_field(default_factory=dict)
    trigger_data: dict = dataclass_field(default_factory=dict)
    step_outputs: dict = dataclass_field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Retorna valor do contexto.

        Args:
            key: Chave.
            default: Valor padrao.

        Returns:
            Valor ou default.
        """
        # Busca em variaveis
        if key in self.variables:
            return self.variables[key]

        # Busca em trigger_data
        if key in self.trigger_data:
            return self.trigger_data[key]

        # Busca em step_outputs
        if key in self.step_outputs:
            return self.step_outputs[key]

        return default

    def set(self, key: str, value: Any) -> None:
        """Define valor no contexto.

        Args:
            key: Chave.
            value: Valor.
        """
        self.variables[key] = value

    def resolve_template(self, template: str) -> str:
        """Resolve template com variaveis.

        Suporta {{variavel}} e {{step.output.campo}}.

        Args:
            template: Template string.

        Returns:
            String resolvida.
        """
        if not isinstance(template, str):
            return template

        pattern = r"\{\{([^}]+)\}\}"

        def replace_var(match: re.Match) -> str:
            var_path = match.group(1).strip()

            # Navegacao por pontos: lead.email
            parts = var_path.split(".")
            value: Any = None

            # Primeiro nivel
            first = parts[0]
            if first in self.variables:
                value = self.variables[first]
            elif first in self.trigger_data:
                value = self.trigger_data[first]
            elif first in self.step_outputs:
                value = self.step_outputs[first]
            else:
                return match.group(0)  # Mantem original

            # Navegacao
            for part in parts[1:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return match.group(0)

            return str(value) if value is not None else ""

        return re.sub(pattern, replace_var, template)

    def resolve_config(self, config: dict) -> dict:
        """Resolve config com variaveis.

        Args:
            config: Config dict.

        Returns:
            Config resolvida.
        """
        resolved = {}

        for key, value in config.items():
            if isinstance(value, str):
                resolved[key] = self.resolve_template(value)
            elif isinstance(value, dict):
                resolved[key] = self.resolve_config(value)
            elif isinstance(value, list):
                resolved[key] = [
                    self.resolve_template(v) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                resolved[key] = value

        return resolved


class WorkflowEngine:
    """Motor de execucao de workflows."""

    def __init__(self, session: AsyncSession):
        """Inicializa engine.

        Args:
            session: Sessao do banco.
        """
        self.session = session
        self._step_handlers: dict[StepType, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Registra handlers padrao."""
        # Handlers de acao
        self._step_handlers[StepType.ACTION_EMAIL] = self._handle_email
        self._step_handlers[StepType.ACTION_WHATSAPP] = self._handle_whatsapp
        self._step_handlers[StepType.ACTION_SMS] = self._handle_sms
        self._step_handlers[StepType.ACTION_WEBHOOK] = self._handle_webhook
        self._step_handlers[StepType.ACTION_TASK] = self._handle_task
        self._step_handlers[StepType.ACTION_UPDATE] = self._handle_update
        self._step_handlers[StepType.ACTION_CREATE] = self._handle_create

        # Handlers de controle
        self._step_handlers[StepType.CONDITION] = self._handle_condition
        self._step_handlers[StepType.SWITCH] = self._handle_switch
        self._step_handlers[StepType.LOOP] = self._handle_loop

        # Handlers de espera
        self._step_handlers[StepType.WAIT_TIME] = self._handle_wait_time
        self._step_handlers[StepType.WAIT_EVENT] = self._handle_wait_event

        # Terminadores
        self._step_handlers[StepType.END_SUCCESS] = self._handle_end_success
        self._step_handlers[StepType.END_ERROR] = self._handle_end_error

    def register_handler(
        self,
        step_type: StepType,
        handler: Callable,
    ) -> None:
        """Registra handler customizado.

        Args:
            step_type: Tipo de step.
            handler: Handler.
        """
        self._step_handlers[step_type] = handler

    # ==================== Execucao Principal ====================

    async def execute_workflow(
        self,
        workflow: Workflow,
        trigger_data: Optional[dict] = None,
        initiated_by: Optional[UUID] = None,
        is_test: bool = False,
    ) -> WorkflowExecution:
        """Executa workflow.

        Args:
            workflow: Workflow a executar.
            trigger_data: Dados do trigger.
            initiated_by: Usuario iniciador.
            is_test: Se e teste.

        Returns:
            Execucao.
        """
        # Cria execucao
        execution = WorkflowExecution(
            tenant_id=workflow.tenant_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.PENDING,
            context={"trigger_data": trigger_data or {}},
            is_test=is_test,
            initiated_by=initiated_by,
        )

        self.session.add(execution)
        await self.session.flush()

        # Cria contexto
        context = ExecutionContext(
            tenant_id=workflow.tenant_id,
            execution_id=execution.id,
            workflow_id=workflow.id,
            trigger_data=trigger_data or {},
        )

        # Log inicio
        await self._log(
            context=context,
            log_type=LogType.EXECUTION_STARTED,
            message=f"Workflow '{workflow.name}' started",
            data={"trigger_data": trigger_data},
        )

        # Inicia execucao
        execution.start()
        await self.session.flush()

        start_time = time.time()

        try:
            # Encontra step inicial
            start_step = await self._find_start_step(workflow)

            if not start_step:
                raise ValueError("Workflow has no start step")

            # Executa steps
            await self._execute_steps(
                _workflow=workflow,
                execution=execution,
                context=context,
                current_step=start_step,
            )

            # Calcula tempo
            execution_time = int((time.time() - start_time) * 1000)

            # Sucesso
            execution.complete(
                result={
                    "success": True,
                    "steps_executed": execution.steps_executed,
                }
            )
            execution.execution_time_ms = execution_time

            # Log fim
            await self._log(
                context=context,
                log_type=LogType.EXECUTION_COMPLETED,
                message=f"Workflow completed in {execution_time}ms",
                data={"steps_executed": execution.steps_executed},
            )

            # Atualiza metricas do workflow
            workflow.record_execution(success=True, execution_time_ms=execution_time)

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Falha
            error_message = str(e)
            execution.fail(error_message)

            # Log erro
            await self._log(
                context=context,
                log_type=LogType.EXECUTION_FAILED,
                message=f"Workflow failed: {error_message}",
                level="ERROR",
                data={"traceback": traceback.format_exc()},
            )

            # Atualiza metricas
            workflow.record_execution(success=False)

        await self.session.flush()
        return execution

    async def _execute_steps(  # pylint: disable=too-many-branches
        self,
        _workflow: Workflow,
        execution: WorkflowExecution,
        context: ExecutionContext,
        current_step: WorkflowStep,
    ) -> None:
        """Executa steps sequencialmente.

        Args:
            _workflow: Workflow (reservado para uso futuro).
            execution: Execucao.
            context: Contexto.
            current_step: Step atual.
        """
        visited: set[str] = set()
        max_iterations = 1000  # Previne loops infinitos

        while current_step and len(visited) < max_iterations:
            step_id = str(current_step.id)

            # Previne loops infinitos (exceto para steps de loop)
            if step_id in visited and current_step.step_type != StepType.LOOP:
                break

            visited.add(step_id)

            # Atualiza execucao
            execution.advance_step(current_step.id, current_step.name)

            # Verifica condicao de entrada
            if current_step.entry_condition:
                if not self._evaluate_condition(
                    current_step.entry_condition,
                    context,
                ):
                    # Log skip
                    await self._log(
                        context=context,
                        log_type=LogType.STEP_SKIPPED,
                        message=f"Step '{current_step.name}' skipped (entry condition)",
                        step_id=step_id,
                        step_name=current_step.name,
                    )

                    # Pula para proximo
                    next_id = current_step.next_step_id
                    if next_id:
                        current_step = await self._get_step(next_id)
                    else:
                        break
                    continue

            # Executa step
            start_time = time.time()

            await self._log(
                context=context,
                log_type=LogType.STEP_STARTED,
                message=f"Step '{current_step.name}' started",
                step_id=step_id,
                step_name=current_step.name,
            )

            try:
                result = await self._execute_step(current_step, context)
                duration = int((time.time() - start_time) * 1000)

                # Salva output
                context.step_outputs[current_step.name] = result.output

                # Log sucesso
                await self._log(
                    context=context,
                    log_type=LogType.STEP_COMPLETED,
                    message=f"Step '{current_step.name}' completed",
                    step_id=step_id,
                    step_name=current_step.name,
                    data={"output": result.output, "duration_ms": duration},
                )

                if not result.should_continue:
                    break

                # Proximo step
                next_id = result.next_step_id or current_step.next_step_id
                if next_id:
                    current_step = await self._get_step(next_id)
                else:
                    break

            except Exception as e:  # pylint: disable=broad-exception-caught
                error_message = str(e)

                # Log erro
                await self._log(
                    context=context,
                    log_type=LogType.STEP_FAILED,
                    message=f"Step '{current_step.name}' failed: {error_message}",
                    step_id=step_id,
                    step_name=current_step.name,
                    level="ERROR",
                    data={"traceback": traceback.format_exc()},
                )

                if current_step.continue_on_error:
                    # Continua mesmo com erro
                    next_id = current_step.next_step_id
                    if next_id:
                        current_step = await self._get_step(next_id)
                    else:
                        break
                else:
                    raise

            await self.session.flush()

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
    ) -> StepResult:
        """Executa um step.

        Args:
            step: Step.
            context: Contexto.

        Returns:
            Resultado.
        """
        handler = self._step_handlers.get(step.step_type)

        if not handler:
            raise ValueError(f"No handler for step type: {step.step_type}")

        # Resolve config com variaveis
        resolved_config = context.resolve_config(step.config)

        # Executa handler
        return await handler(step, context, resolved_config)

    # ==================== Handlers de Step ====================

    async def _handle_email(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para envio de email.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        # Simulacao - integrar com EmailService real
        to_email = config.get("to")
        subject = config.get("subject")
        template_id = config.get("template_id")

        await self._log(
            context=context,
            log_type=LogType.ACTION_EMAIL_SENT,
            message=f"Email sent to {to_email}",
            step_id=str(step.id),
            step_name=step.name,
            data={"to": to_email, "subject": subject, "template_id": template_id},
        )

        return StepResult(
            success=True,
            output={"sent": True, "to": to_email},
        )

    async def _handle_whatsapp(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para envio de WhatsApp.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        phone = config.get("phone")
        template_id = config.get("template_id")

        await self._log(
            context=context,
            log_type=LogType.ACTION_WHATSAPP_SENT,
            message=f"WhatsApp sent to {phone}",
            step_id=str(step.id),
            step_name=step.name,
            data={"phone": phone, "template_id": template_id},
        )

        return StepResult(
            success=True,
            output={"sent": True, "phone": phone},
        )

    async def _handle_sms(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para envio de SMS.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        phone = config.get("phone")
        message = config.get("message")

        await self._log(
            context=context,
            log_type=LogType.ACTION_SMS_SENT,
            message=f"SMS sent to {phone}",
            step_id=str(step.id),
            step_name=step.name,
            data={"phone": phone},
        )

        return StepResult(
            success=True,
            output={"sent": True, "phone": phone, "message": message},
        )

    async def _handle_webhook(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para chamada de webhook.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        url = config.get("url")
        method = config.get("method", "POST")

        await self._log(
            context=context,
            log_type=LogType.ACTION_WEBHOOK_CALLED,
            message=f"Webhook called: {method} {url}",
            step_id=str(step.id),
            step_name=step.name,
            data={"url": url, "method": method},
        )

        return StepResult(
            success=True,
            output={"called": True, "url": url},
        )

    async def _handle_task(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para criacao de tarefa.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        title = config.get("title")
        assignee = config.get("assignee")

        await self._log(
            context=context,
            log_type=LogType.ACTION_TASK_CREATED,
            message=f"Task created: {title}",
            step_id=str(step.id),
            step_name=step.name,
            data={"title": title, "assignee": assignee},
        )

        return StepResult(
            success=True,
            output={"created": True, "title": title},
        )

    async def _handle_update(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para atualizacao de registro.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        entity = config.get("entity")
        entity_id = config.get("entity_id")
        updates = config.get("updates", {})

        await self._log(
            context=context,
            log_type=LogType.ACTION_RECORD_UPDATED,
            message=f"Record updated: {entity} {entity_id}",
            step_id=str(step.id),
            step_name=step.name,
            data={"entity": entity, "entity_id": entity_id, "updates": updates},
        )

        return StepResult(
            success=True,
            output={"updated": True, "entity": entity, "entity_id": entity_id},
        )

    async def _handle_create(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para criacao de registro.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        entity = config.get("entity")
        data = config.get("data", {})

        await self._log(
            context=context,
            log_type=LogType.ACTION_RECORD_CREATED,
            message=f"Record created: {entity}",
            step_id=str(step.id),
            step_name=step.name,
            data={"entity": entity, "data": data},
        )

        return StepResult(
            success=True,
            output={"created": True, "entity": entity},
        )

    async def _handle_condition(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para condicao.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        condition_result = self._evaluate_condition(config, context)

        await self._log(
            context=context,
            log_type=(
                LogType.CONDITION_TRUE if condition_result else LogType.CONDITION_FALSE
            ),
            message=f"Condition evaluated: {condition_result}",
            step_id=str(step.id),
            step_name=step.name,
            data={"condition": config, "result": condition_result},
        )

        # Proximo step baseado no resultado
        next_step_id = (
            step.true_step_id if condition_result else step.false_step_id
        )

        return StepResult(
            success=True,
            output={"result": condition_result},
            next_step_id=next_step_id,
        )

    async def _handle_switch(
        self,
        _step: WorkflowStep,
        _context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para switch/case.

        Args:
            _step: Step (reservado).
            _context: Contexto (reservado).
            config: Config resolvida.

        Returns:
            Resultado.
        """
        field_value = config.get("value")
        cases = config.get("cases", {})
        default_step = config.get("default")

        next_step_id = cases.get(str(field_value), default_step)

        return StepResult(
            success=True,
            output={"matched": field_value, "next": next_step_id},
            next_step_id=next_step_id,
        )

    async def _handle_loop(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para loop.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        # Implementacao basica de loop
        items = config.get("items", [])
        loop_var = config.get("variable", "item")
        current_index = context.get(f"_loop_{step.id}_index", 0)

        if current_index < len(items):
            # Define variavel do loop
            context.set(loop_var, items[current_index])
            context.set(f"_loop_{step.id}_index", current_index + 1)

            # Vai para o corpo do loop
            body_step_id = config.get("body_step")

            return StepResult(
                success=True,
                output={"index": current_index, "item": items[current_index]},
                next_step_id=body_step_id,
            )

        # Loop terminado
        return StepResult(
            success=True,
            output={"completed": True, "total": len(items)},
        )

    async def _handle_wait_time(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para espera por tempo.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        seconds = config.get("seconds", 0)
        minutes = config.get("minutes", 0)
        hours = config.get("hours", 0)

        total_seconds = seconds + (minutes * 60) + (hours * 3600)

        # Em producao, isso seria agendado, nao sleep
        if 0 < total_seconds <= 60:
            await asyncio.sleep(total_seconds)

        await self._log(
            context=context,
            log_type=LogType.WAIT_COMPLETED,
            message=f"Wait completed: {total_seconds}s",
            step_id=str(step.id),
            step_name=step.name,
        )

        return StepResult(
            success=True,
            output={"waited_seconds": total_seconds},
        )

    async def _handle_wait_event(
        self,
        step: WorkflowStep,
        context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para espera por evento.

        Args:
            step: Step.
            context: Contexto.
            config: Config resolvida.

        Returns:
            Resultado.
        """
        event_type = config.get("event_type")

        await self._log(
            context=context,
            log_type=LogType.WAIT_STARTED,
            message=f"Waiting for event: {event_type}",
            step_id=str(step.id),
            step_name=step.name,
        )

        # Em producao, marcaria execucao como WAITING
        return StepResult(
            success=True,
            output={"waiting_for": event_type},
            should_continue=False,  # Para execucao ate evento
        )

    async def _handle_end_success(
        self,
        _step: WorkflowStep,
        _context: ExecutionContext,
        _config: dict,
    ) -> StepResult:
        """Handler para fim com sucesso.

        Args:
            _step: Step (reservado).
            _context: Contexto (reservado).
            _config: Config (reservado).

        Returns:
            Resultado.
        """
        return StepResult(
            success=True,
            output={"ended": True, "status": "success"},
            should_continue=False,
        )

    async def _handle_end_error(
        self,
        _step: WorkflowStep,
        _context: ExecutionContext,
        config: dict,
    ) -> StepResult:
        """Handler para fim com erro.

        Args:
            _step: Step (reservado).
            _context: Contexto (reservado).
            config: Config resolvida.

        Returns:
            Resultado.
        """
        error_message = config.get("message", "Workflow ended with error")
        raise ValueError(error_message)

    # ==================== Helpers ====================

    async def _find_start_step(self, workflow: Workflow) -> Optional[WorkflowStep]:
        """Encontra step inicial.

        Args:
            workflow: Workflow.

        Returns:
            Step inicial ou None.
        """
        # Busca step marcado como start
        for step in workflow.steps:
            if step.is_start:
                return step

        # Se nao encontrou, pega o primeiro por ordem
        if workflow.steps:
            return sorted(workflow.steps, key=lambda s: s.order)[0]

        return None

    async def _get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Busca step por ID.

        Args:
            step_id: ID do step.

        Returns:
            Step ou None.
        """
        query = select(WorkflowStep).where(WorkflowStep.id == step_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    def _evaluate_condition(
        self,
        condition: dict,
        context: ExecutionContext,
    ) -> bool:
        """Avalia condicao.

        Args:
            condition: Config da condicao.
            context: Contexto.

        Returns:
            Resultado booleano.
        """
        field_name = condition.get("field")
        operator = condition.get("operator", "==")
        expected = condition.get("value")

        # Resolve valor do campo
        actual = context.get(field_name)

        # Resolve valor esperado (pode ter variaveis)
        if isinstance(expected, str):
            expected = context.resolve_template(expected)

        # Operadores
        operators = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: float(a) > float(b) if a and b else False,
            ">=": lambda a, b: float(a) >= float(b) if a and b else False,
            "<": lambda a, b: float(a) < float(b) if a and b else False,
            "<=": lambda a, b: float(a) <= float(b) if a and b else False,
            "in": lambda a, b: a in b if b else False,
            "not_in": lambda a, b: a not in b if b else True,
            "contains": lambda a, b: b in a if a and b else False,
            "starts_with": lambda a, b: str(a).startswith(str(b)) if a else False,
            "ends_with": lambda a, b: str(a).endswith(str(b)) if a else False,
            "is_null": lambda a, _: a is None,
            "is_not_null": lambda a, _: a is not None,
            "is_empty": lambda a, _: not a,
            "is_not_empty": lambda a, _: bool(a),
        }

        op_func = operators.get(operator)
        if op_func:
            try:
                return op_func(actual, expected)
            except (TypeError, ValueError):
                return False

        return False

    async def _log(
        self,
        context: ExecutionContext,
        log_type: LogType,
        message: str,
        step_id: Optional[str] = None,
        step_name: Optional[str] = None,
        level: str = "INFO",
        data: Optional[dict] = None,
    ) -> None:
        """Cria log.

        Args:
            context: Contexto.
            log_type: Tipo do log.
            message: Mensagem.
            step_id: ID do step.
            step_name: Nome do step.
            level: Nivel.
            data: Dados adicionais.
        """
        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
            "CRITICAL": LogLevel.CRITICAL,
        }

        log = WorkflowLog(
            tenant_id=context.tenant_id,
            execution_id=context.execution_id,
            step_id=step_id,
            step_name=step_name,
            level=level_map.get(level, LogLevel.INFO),
            log_type=log_type,
            message=message,
            data=data,
        )

        self.session.add(log)

    # ==================== Triggers ====================

    async def process_trigger(
        self,
        trigger: WorkflowTrigger,
        entity_data: dict,
    ) -> Optional[WorkflowExecution]:
        """Processa trigger.

        Args:
            trigger: Trigger.
            entity_data: Dados da entidade.

        Returns:
            Execucao ou None.
        """
        # Verifica se trigger esta ativo
        if not trigger.is_active:
            return None

        # Verifica limite
        if trigger.has_reached_limit:
            return None

        # Verifica match
        entity_type = entity_data.get("_type", "")
        if not trigger.matches_entity(entity_type, entity_data):
            return None

        # Busca workflow
        workflow = trigger.workflow

        if not workflow or not workflow.is_active:
            return None

        # Registra trigger
        trigger.record_triggered()

        # Executa workflow
        execution = await self.execute_workflow(
            workflow=workflow,
            trigger_data=entity_data,
        )

        return execution
