"""
modules/fase5/agents/email_agent.py - Email Intelligence Agent
=============================================================
Agente de inteligencia para processamento de emails
"""

import logging
from typing import Any
from uuid import UUID

from ..email_intelligence.models import EmailMessage
from ..email_intelligence.service import EmailIntelligenceService
from .base import AgentMessage, AgentTask, AgentType, BaseAgent

logger = logging.getLogger(__name__)


class EmailAgent(BaseAgent):
    """
    Agente de inteligencia para emails.

    Responsabilidades:
    1. Processar emails recebidos
    2. Classificar e priorizar
    3. Extrair entidades e intencao
    4. Gerar sugestoes de resposta
    5. Notificar outros agentes
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(AgentType.EMAIL_INTELLIGENCE, config)
        self.email_service = EmailIntelligenceService()

    async def process_task(self, task: AgentTask) -> dict[str, Any]:
        """Processa tarefa de email."""
        task_type = task.task_type

        if task_type == "analyze_email":
            return await self._analyze_email(task.data)
        elif task_type == "generate_response":
            return await self._generate_response(task.data)
        elif task_type == "get_context":
            return await self._get_email_context(task.data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def handle_message(self, message: AgentMessage) -> None:
        """Lida com mensagem de outro agente."""
        msg_type = message.message_type

        if msg_type == "new_email_received":
            # Criar tarefa para analisar email
            task = AgentTask(task_type="analyze_email", data=message.payload, priority=3)
            await self.submit_task(task)

        elif msg_type == "request_context":
            # Buscar contexto e responder
            context = await self._get_email_context(message.payload)
            reply = AgentMessage(
                from_agent=self.agent_type,
                to_agent=message.from_agent,
                message_type="context_response",
                payload=context,
                reply_to=message.message_id,
            )
            await self.send_message(reply)

    async def _analyze_email(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analisa um email."""
        email = EmailMessage(**data)
        result = await self.email_service.process_incoming_email(email)

        # Notificar agente de integracao
        if result.get("analysis", {}).get("category") == "proposta_comercial":
            await self.send_message(
                AgentMessage(
                    from_agent=self.agent_type,
                    to_agent=AgentType.INTEGRATION_HUB,
                    message_type="proposta_solicitada",
                    payload={"email_id": result["email_id"], "analysis": result["analysis"]},
                )
            )

        return result

    async def _generate_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Gera resposta para email."""
        # Implementar geracao de resposta com IA
        return {"response_generated": True, "template_used": data.get("template_id")}

    async def _get_email_context(self, data: dict[str, Any]) -> dict[str, Any]:
        """Obtem contexto do email."""
        email_address = data.get("email_address")
        tenant_id = UUID(data.get("tenant_id"))

        context = await self.email_service.get_email_context(email_address, tenant_id)

        return context.model_dump()
