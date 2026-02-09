"""
AIWorkflow Executor Service - Sprint 55.

Servico para execucao de workflows.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class StepExecutor:
    """Executor de steps individuais."""

    def __init__(self):
        """Inicializa o executor de steps."""
        self._handlers: dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Registra handlers padrao."""
        self._handlers = {
            "action": self._execute_action,
            "condition": self._execute_condition,
            "wait": self._execute_wait,
            "notification": self._execute_notification,
            "data_transform": self._execute_data_transform,
            "api_call": self._execute_api_call,
            "script": self._execute_script,
            "loop": self._execute_loop,
            "parallel": self._execute_parallel,
            "approval": self._execute_approval,
        }

    def register_handler(
        self,
        step_type: str,
        handler: Callable,
    ):
        """Registra handler customizado."""
        self._handlers[step_type] = handler

    async def execute_step(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Executa um step.

        Args:
            step: Definicao do step
            context: Contexto de execucao

        Returns:
            Dict com resultado do step
        """
        step_type = step.get("step_type", "action")
        handler = self._handlers.get(step_type)

        if not handler:
            return {
                "status": "failed",
                "error": f"Handler nao encontrado para tipo: {step_type}",
            }

        start_time = datetime.utcnow()

        try:
            result = await handler(step, context)
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return {
                "status": "completed",
                "output": result,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(f"Erro executando step {step.get('id')}: {e}")

            return {
                "status": "failed",
                "error": str(e),
                "execution_time_ms": execution_time,
            }

    async def _execute_action(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa acao generica."""
        config = step.get("config", {})
        action_type = config.get("action_type", "noop")

        if action_type == "set_variable":
            var_name = config.get("variable")
            var_value = config.get("value")
            context["variables"][var_name] = var_value
            return {"variable_set": var_name}

        elif action_type == "log":
            message = config.get("message", "")
            logger.info(f"AIWorkflow log: {message}")
            return {"logged": message}

        return {"action": action_type, "status": "completed"}

    async def _execute_condition(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa condicao."""
        config = step.get("config", {})
        condition = config.get("condition", "true")

        # Avalia condicao simples
        result = self._evaluate_condition(condition, context)

        return {
            "condition": condition,
            "result": result,
            "next_step": config.get("true_step") if result else config.get("false_step"),
        }

    def _evaluate_condition(
        self,
        condition: str,
        context: dict[str, Any],
    ) -> bool:
        """Avalia condicao."""
        try:
            # Substitui variaveis
            variables = context.get("variables", {})
            for key, value in variables.items():
                condition = condition.replace(f"${{{key}}}", json.dumps(value))

            # Avaliacao segura (simplificada)
            if condition.lower() == "true":
                return True
            elif condition.lower() == "false":
                return False

            # Comparacoes simples
            if "==" in condition:
                parts = condition.split("==")
                return parts[0].strip() == parts[1].strip()
            elif "!=" in condition:
                parts = condition.split("!=")
                return parts[0].strip() != parts[1].strip()
            elif ">" in condition:
                parts = condition.split(">")
                try:
                    return float(parts[0].strip()) > float(parts[1].strip())
                except ValueError:
                    return False

            return False

        except Exception as e:
            logger.error(f"Erro avaliando condicao: {e}")
            return False

    async def _execute_wait(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa espera."""
        config = step.get("config", {})
        wait_seconds = config.get("seconds", 1)
        max_wait = min(wait_seconds, 300)  # Max 5 minutos

        await asyncio.sleep(max_wait)

        return {"waited_seconds": max_wait}

    async def _execute_notification(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa notificacao."""
        config = step.get("config", {})
        channels = config.get("channels", ["log"])
        message = config.get("message", "")
        recipients = config.get("recipients", [])

        # Substitui variaveis
        variables = context.get("variables", {})
        for key, value in variables.items():
            message = message.replace(f"${{{key}}}", str(value))

        results = {}
        for channel in channels:
            if channel == "log":
                logger.info(f"Notification: {message}")
                results["log"] = "sent"
            elif channel == "email":
                # Simulacao - em producao integra com servico de email
                results["email"] = f"sent to {len(recipients)} recipients"
            elif channel == "push":
                results["push"] = "sent"

        return {"channels": results, "message": message}

    async def _execute_data_transform(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa transformacao de dados."""
        config = step.get("config", {})
        transform_type = config.get("type", "copy")
        source = config.get("source", "")
        target = config.get("target", "")

        variables = context.get("variables", {})

        if transform_type == "copy":
            if source in variables:
                variables[target] = variables[source]
                context["variables"] = variables
                return {"copied": {source: target}}

        elif transform_type == "format":
            template = config.get("template", "")
            for key, value in variables.items():
                template = template.replace(f"${{{key}}}", str(value))
            variables[target] = template
            context["variables"] = variables
            return {"formatted": target}

        elif transform_type == "json_path":
            # Simplificado
            pass

        return {"transform": transform_type}

    async def _execute_api_call(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa chamada de API."""
        config = step.get("config", {})
        url = config.get("url", "")
        method = config.get("method", "GET")
        config.get("headers", {})
        body = config.get("body")

        # Substitui variaveis
        variables = context.get("variables", {})
        for key, value in variables.items():
            url = url.replace(f"${{{key}}}", str(value))
            if body and isinstance(body, str):
                body = body.replace(f"${{{key}}}", str(value))

        # Simulacao - em producao usa httpx/aiohttp
        logger.info(f"API Call: {method} {url}")

        return {
            "method": method,
            "url": url,
            "status_code": 200,
            "response": {"simulated": True},
        }

    async def _execute_script(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa script."""
        config = step.get("config", {})
        script_type = config.get("type", "python")
        config.get("code", "")

        # Por seguranca, apenas log
        logger.info(f"Script execution requested: {script_type}")

        return {
            "script_type": script_type,
            "status": "simulated",
        }

    async def _execute_loop(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa loop."""
        config = step.get("config", {})
        iterations = config.get("iterations", 1)
        max_iterations = min(iterations, 100)

        results = []
        for i in range(max_iterations):
            context["loop_index"] = i
            results.append({"iteration": i, "status": "completed"})

        return {"iterations": len(results), "results": results}

    async def _execute_parallel(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa steps em paralelo."""
        config = step.get("config", {})
        parallel_steps = config.get("steps", [])

        # Simulacao
        return {
            "parallel_count": len(parallel_steps),
            "status": "completed",
        }

    async def _execute_approval(
        self,
        step: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Executa step de aprovacao."""
        config = step.get("config", {})

        # Verifica aprovacao automatica
        auto_condition = config.get("auto_approve_condition")
        if auto_condition:
            # Avalia condicao
            if auto_condition == "low_risk":
                risk_level = context.get("variables", {}).get("risk_level", "low")
                if risk_level == "low":
                    return {"auto_approved": True, "reason": "low_risk"}

        # Requer aprovacao manual
        return {
            "status": "waiting",
            "requires_approval": True,
            "approvers": config.get("approvers", []),
        }


class WorkflowExecutor:
    """
    Executor de workflows.

    Gerencia a execucao completa de workflows.
    """

    def __init__(self):
        """Inicializa o executor."""
        self._step_executor = StepExecutor()

    async def execute_workflow(
        self,
        workflow: dict[str, Any],
        input_data: dict[str, Any],
        execution_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Executa workflow completo.

        Args:
            workflow: Definicao do workflow
            input_data: Dados de entrada
            execution_id: ID da execucao

        Returns:
            Dict com resultado da execucao
        """
        execution_id = execution_id or uuid4()
        start_time = datetime.utcnow()

        # Inicializa contexto
        context = {
            "workflow_id": workflow.get("id"),
            "execution_id": str(execution_id),
            "input": input_data,
            "variables": {**workflow.get("variables", {}), **input_data},
            "step_results": {},
            "logs": [],
        }

        steps = workflow.get("steps", [])
        total_steps = len(steps)
        current_step = 0
        status = "running"
        error_message = None
        error_step = None

        try:
            # Executa steps
            step_index = 0
            while step_index < len(steps):
                step = steps[step_index]
                step_id = step.get("id", f"step_{step_index}")
                current_step = step_index + 1

                # Log
                self._add_log(context, "info", f"Executando step: {step.get('name', step_id)}")

                # Verifica timeout
                timeout = step.get("timeout") or workflow.get("timeout_seconds", 300)
                timeout = min(timeout, 600)  # Max 10 min

                try:
                    # Executa step com timeout
                    result = await asyncio.wait_for(
                        self._step_executor.execute_step(step, context),
                        timeout=timeout,
                    )
                except TimeoutError:
                    result = {
                        "status": "timeout",
                        "error": f"Step timeout apos {timeout}s",
                    }

                # Salva resultado
                context["step_results"][step_id] = result

                # Verifica status
                if result.get("status") == "failed":
                    # Verifica retry
                    retry_count = step.get("config", {}).get("retry_count", 0)
                    current_retry = context.get(f"retry_{step_id}", 0)

                    if current_retry < retry_count:
                        context[f"retry_{step_id}"] = current_retry + 1
                        delay = step.get("config", {}).get("retry_delay", 5000) / 1000
                        await asyncio.sleep(delay)
                        continue  # Retry

                    status = "failed"
                    error_message = result.get("error", "Unknown error")
                    error_step = step_id
                    break

                elif result.get("status") == "waiting":
                    status = "waiting"
                    break

                # Determina proximo step
                next_step = result.get("output", {}).get("next_step")
                if next_step:
                    # Busca step por ID
                    found = False
                    for i, s in enumerate(steps):
                        if s.get("id") == next_step:
                            step_index = i
                            found = True
                            break
                    if not found:
                        step_index += 1
                else:
                    step_index += 1

            if status == "running":
                status = "completed"

        except Exception as e:
            logger.error(f"Erro executando workflow: {e}")
            status = "failed"
            error_message = str(e)

        # Calcula tempo
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return {
            "id": str(execution_id),
            "workflow_id": workflow.get("id"),
            "status": status,
            "current_step": current_step,
            "total_steps": total_steps,
            "progress_percent": (current_step / total_steps * 100) if total_steps > 0 else 0,
            "input_data": input_data,
            "output_data": context.get("variables", {}),
            "context": context,
            "step_results": context.get("step_results", {}),
            "logs": context.get("logs", []),
            "error_message": error_message,
            "error_step": error_step,
            "started_at": start_time.isoformat(),
            "completed_at": datetime.utcnow().isoformat() if status in ["completed", "failed"] else None,
            "execution_time_ms": execution_time,
        }

    def _add_log(
        self,
        context: dict[str, Any],
        level: str,
        message: str,
        step: str | None = None,
    ):
        """Adiciona log ao contexto."""
        context.setdefault("logs", []).append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "message": message,
                "step": step,
            }
        )

    async def cancel_execution(
        self,
        execution_id: UUID,
    ) -> bool:
        """Cancela execucao."""
        # Implementacao requer estado persistido
        logger.info(f"Cancel requested for execution: {execution_id}")
        return True

    async def pause_execution(
        self,
        execution_id: UUID,
    ) -> bool:
        """Pausa execucao."""
        logger.info(f"Pause requested for execution: {execution_id}")
        return True

    async def resume_execution(
        self,
        execution_id: UUID,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Retoma execucao pausada."""
        logger.info(f"Resume requested for execution: {execution_id}")
        return {"status": "resumed"}
