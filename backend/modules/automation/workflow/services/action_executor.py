"""
Action Executor - Executa acoes de workflow.

Implementa executores para cada tipo de acao.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from modules._deprecated_workflows_dataclass.models.action import (
    Action,
    ActionResult,
    ActionStatus,
    ActionType,
)

logger = logging.getLogger(__name__)


class BaseActionHandler(ABC):
    """Handler base para acoes."""

    @abstractmethod
    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Executa acao."""
        pass

    def render_template(
        self,
        template: str,
        context: dict[str, Any],
    ) -> str:
        """Renderiza template com contexto."""
        if not template:
            return ""

        try:
            # Substituicao simples de variaveis
            # Formato: {{variable}} ou {{object.property}}
            result = template
            for key, value in context.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        result = result.replace(
                            f"{{{{{key}.{sub_key}}}}}",
                            str(sub_value),
                        )
                result = result.replace(f"{{{{{key}}}}}", str(value))

            return result
        except Exception as e:
            logger.error(f"Erro ao renderizar template: {e}")
            return template


class SendEmailHandler(BaseActionHandler):
    """Handler para envio de email."""

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Envia email."""
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        config = action.email_config
        if not config:
            result.status = ActionStatus.FAILED
            result.error = "Configuracao de email ausente"
            return result

        try:
            # Renderiza templates
            subject = self.render_template(config.subject, context)
            self.render_template(config.body, context)
            self.render_template(config.body_html, context)

            # Processa destinatarios
            to = [self.render_template(t, context) for t in config.to]

            # Simula envio (integrar com servico real)
            # await email_service.send(to, subject, body, body_html)

            result.status = ActionStatus.COMPLETED
            result.success = True
            result.output = {
                "to": to,
                "subject": subject,
                "sent_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"Email enviado para {to}: {subject}")

        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
            logger.error(f"Erro ao enviar email: {e}")

        result.completed_at = datetime.utcnow()
        result.execution_time_ms = (result.completed_at - result.started_at).total_seconds() * 1000

        return result


class SendWhatsAppHandler(BaseActionHandler):
    """Handler para envio de WhatsApp."""

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Envia mensagem WhatsApp."""
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        config = action.whatsapp_config
        if not config:
            result.status = ActionStatus.FAILED
            result.error = "Configuracao de WhatsApp ausente"
            return result

        try:
            # Renderiza mensagem
            message = self.render_template(config.message, context)

            # Processa telefones
            phones = [self.render_template(p, context) for p in config.phone_numbers]

            # Simula envio (integrar com Evolution API ou similar)
            # await whatsapp_service.send(phones, message)

            result.status = ActionStatus.COMPLETED
            result.success = True
            result.output = {
                "phones": phones,
                "message": message,
                "sent_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"WhatsApp enviado para {phones}")

        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
            logger.error(f"Erro ao enviar WhatsApp: {e}")

        result.completed_at = datetime.utcnow()
        result.execution_time_ms = (result.completed_at - result.started_at).total_seconds() * 1000

        return result


class HTTPRequestHandler(BaseActionHandler):
    """Handler para requisicoes HTTP."""

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Executa requisicao HTTP."""
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        config = action.http_config
        if not config:
            result.status = ActionStatus.FAILED
            result.error = "Configuracao HTTP ausente"
            return result

        try:
            # Renderiza URL e headers
            url = self.render_template(config.url, context)

            headers = {k: self.render_template(v, context) for k, v in config.headers.items()}

            # Renderiza body
            body = None
            if config.body:
                body = json.dumps(self._render_dict(config.body, context))
                headers.setdefault("Content-Type", "application/json")

            # Query params
            params = {k: self.render_template(v, context) for k, v in config.query_params.items()}

            # Autenticacao
            auth = None
            if config.auth_type == "basic":
                import aiohttp

                auth = aiohttp.BasicAuth(
                    config.auth_credentials.get("username", ""),
                    config.auth_credentials.get("password", ""),
                )
            elif config.auth_type == "bearer":
                headers["Authorization"] = f"Bearer {config.auth_credentials.get('token', '')}"
            elif config.auth_type == "api_key":
                headers[config.auth_credentials.get("header", "X-API-Key")] = config.auth_credentials.get("key", "")

            # Executa requisicao
            timeout = aiohttp.ClientTimeout(total=action.config.timeout_seconds)

            async with (
                aiohttp.ClientSession(timeout=timeout) as session,
                session.request(
                    method=config.method,
                    url=url,
                    headers=headers,
                    data=body,
                    params=params,
                    auth=auth,
                    ssl=config.validate_ssl,
                    allow_redirects=config.follow_redirects,
                ) as response,
            ):
                response_text = await response.text()

                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    response_data = {"raw": response_text}

                result.output = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": response_data,
                }

                if 200 <= response.status < 300:
                    result.status = ActionStatus.COMPLETED
                    result.success = True
                else:
                    result.status = ActionStatus.FAILED
                    result.error = f"HTTP {response.status}"

            logger.info(f"HTTP {config.method} {url}: {result.output.get('status_code')}")

        except TimeoutError:
            result.status = ActionStatus.FAILED
            result.error = "Timeout na requisicao"
            logger.error(f"Timeout ao executar HTTP: {config.url}")

        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
            logger.error(f"Erro ao executar HTTP: {e}")

        result.completed_at = datetime.utcnow()
        result.execution_time_ms = (result.completed_at - result.started_at).total_seconds() * 1000

        return result

    def _render_dict(
        self,
        data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Renderiza dicionario com variaveis."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.render_template(value, context)
            elif isinstance(value, dict):
                result[key] = self._render_dict(value, context)
            elif isinstance(value, list):
                result[key] = [self.render_template(v, context) if isinstance(v, str) else v for v in value]
            else:
                result[key] = value
        return result


class CreateTaskHandler(BaseActionHandler):
    """Handler para criacao de tarefas."""

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Cria tarefa."""
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        config = action.task_config
        if not config:
            result.status = ActionStatus.FAILED
            result.error = "Configuracao de tarefa ausente"
            return result

        try:
            # Renderiza campos
            title = self.render_template(config.title, context)
            self.render_template(config.description, context)
            assignee_id = self.render_template(config.assignee_id, context)

            # Simula criacao (integrar com servico real)
            import uuid

            task_id = str(uuid.uuid4())

            result.status = ActionStatus.COMPLETED
            result.success = True
            result.output = {
                "task_id": task_id,
                "title": title,
                "assignee_id": assignee_id,
                "created_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"Tarefa criada: {title}")

        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)
            logger.error(f"Erro ao criar tarefa: {e}")

        result.completed_at = datetime.utcnow()
        result.execution_time_ms = (result.completed_at - result.started_at).total_seconds() * 1000

        return result


class SetVariableHandler(BaseActionHandler):
    """Handler para definir variavel."""

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Define variavel no contexto."""
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        try:
            # Extrai variaveis do input_mapping
            variables = {}
            for var_name, expression in action.input_mapping.items():
                value = self.render_template(expression, context)
                variables[var_name] = value

            result.status = ActionStatus.COMPLETED
            result.success = True
            result.output = {
                "variables": variables,
            }

        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)

        result.completed_at = datetime.utcnow()
        return result


class LogMessageHandler(BaseActionHandler):
    """Handler para log de mensagem."""

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Registra log."""
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        try:
            message = self.render_template(action.message_template, context)
            logger.info(f"[Workflow Log] {message}")

            result.status = ActionStatus.COMPLETED
            result.success = True
            result.output = {"message": message}

        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)

        result.completed_at = datetime.utcnow()
        return result


class DelayHandler(BaseActionHandler):
    """Handler para delay."""

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """Aguarda periodo especificado."""
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        try:
            # Obtem delay em segundos
            delay = context.get("delay_seconds", 0)

            if delay > 0:
                await asyncio.sleep(delay)

            result.status = ActionStatus.COMPLETED
            result.success = True
            result.output = {"delayed_seconds": delay}

        except asyncio.CancelledError:
            result.status = ActionStatus.CANCELLED
            result.error = "Delay cancelado"

        except Exception as e:
            result.status = ActionStatus.FAILED
            result.error = str(e)

        result.completed_at = datetime.utcnow()
        result.execution_time_ms = (result.completed_at - result.started_at).total_seconds() * 1000

        return result


class ActionExecutor:
    """
    Executor de acoes de workflow.

    Orquestra a execucao de diferentes tipos de acoes.
    """

    def __init__(self):
        self._handlers: dict[ActionType, BaseActionHandler] = {
            ActionType.SEND_EMAIL: SendEmailHandler(),
            ActionType.SEND_WHATSAPP: SendWhatsAppHandler(),
            ActionType.HTTP_REQUEST: HTTPRequestHandler(),
            ActionType.WEBHOOK: HTTPRequestHandler(),
            ActionType.CREATE_TASK: CreateTaskHandler(),
            ActionType.SET_VARIABLE: SetVariableHandler(),
            ActionType.LOG_MESSAGE: LogMessageHandler(),
            ActionType.DELAY: DelayHandler(),
        }

    def register_handler(
        self,
        action_type: ActionType,
        handler: BaseActionHandler,
    ) -> None:
        """Registra handler customizado."""
        self._handlers[action_type] = handler

    async def execute(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> ActionResult:
        """
        Executa acao.

        Args:
            action: Acao a executar
            context: Contexto com variaveis

        Returns:
            Resultado da execucao
        """
        result = ActionResult(
            action_id=action.id,
            started_at=datetime.utcnow(),
        )

        # Valida acao
        errors = action.validate()
        if errors:
            result.status = ActionStatus.FAILED
            result.error = "; ".join(errors)
            result.completed_at = datetime.utcnow()
            return result

        # Obtem handler
        handler = self._handlers.get(action.action_type)
        if not handler:
            result.status = ActionStatus.FAILED
            result.error = f"Handler nao encontrado para {action.action_type.value}"
            result.completed_at = datetime.utcnow()
            return result

        # Prepara contexto com input mapping
        exec_context = self._prepare_context(action, context)

        # Executa com retry
        for attempt in range(action.config.retry_count + 1):
            try:
                result = await asyncio.wait_for(
                    handler.execute(action, exec_context),
                    timeout=action.config.timeout_seconds,
                )

                if result.success:
                    break

                if attempt < action.config.retry_count:
                    result.retry_count = attempt + 1
                    await asyncio.sleep(action.config.retry_delay_seconds)

            except TimeoutError:
                result.status = ActionStatus.FAILED
                result.error = "Timeout na execucao"
                result.retry_count = attempt

            except Exception as e:
                result.status = ActionStatus.FAILED
                result.error = str(e)
                result.retry_count = attempt

                if attempt < action.config.retry_count:
                    await asyncio.sleep(action.config.retry_delay_seconds)

        # Atualiza estatisticas
        action.update_statistics(
            result.success,
            result.execution_time_ms,
        )

        return result

    async def execute_batch(
        self,
        actions: list[Action],
        context: dict[str, Any],
        parallel: bool = False,
    ) -> list[ActionResult]:
        """
        Executa lista de acoes.

        Args:
            actions: Lista de acoes
            context: Contexto compartilhado
            parallel: Se True, executa em paralelo

        Returns:
            Lista de resultados
        """
        if parallel:
            tasks = [self.execute(action, context.copy()) for action in actions]
            return await asyncio.gather(*tasks)

        results = []
        for action in actions:
            result = await self.execute(action, context)
            results.append(result)

            # Atualiza contexto com output
            if result.success and result.output:
                context.update(result.output)

        return results

    def _prepare_context(
        self,
        action: Action,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Prepara contexto para execucao."""
        exec_context = context.copy()

        # Aplica input mapping
        if action.input_mapping:
            for target, source in action.input_mapping.items():
                value = self._get_value_by_path(context, source)
                if value is not None:
                    exec_context[target] = value

        return exec_context

    def _get_value_by_path(self, data: dict[str, Any], path: str) -> Any:
        """Obtem valor por path."""
        if not path:
            return None

        if path.startswith("$."):
            path = path[2:]

        parts = path.split(".")
        value = data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value
