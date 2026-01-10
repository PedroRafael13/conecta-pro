"""
modules/fase5/agents/integration_agent.py - Integration Hub Agent
================================================================
Agente de integracao entre todas as fases do sistema
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .base import BaseAgent, AgentType, AgentTask, AgentMessage

logger = logging.getLogger(__name__)


class IntegrationHubAgent(BaseAgent):
    """
    Agente hub de integracao.

    Responsabilidades:
    1. Orquestrar comunicacao entre agentes
    2. Rotear mensagens entre fases
    3. Coordenar workflows cross-phase
    4. Monitorar saude do ecosystem
    5. Agregar metricas
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(AgentType.INTEGRATION_HUB, config)
        self.registered_agents: Dict[AgentType, BaseAgent] = {}
        self.pending_workflows: Dict[str, Dict[str, Any]] = {}
        self.metrics = {
            "messages_routed": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "alerts_generated": 0
        }

    def register_agent(self, agent: BaseAgent) -> None:
        """Registra um agente no hub."""
        self.registered_agents[agent.agent_type] = agent
        logger.info(f"Agent {agent.agent_type.value} registered in hub")

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Processa tarefa de integracao."""
        task_type = task.task_type

        if task_type == "route_message":
            return await self._route_message(task.data)
        elif task_type == "start_workflow":
            return await self._start_workflow(task.data)
        elif task_type == "get_system_status":
            return await self._get_system_status()
        elif task_type == "aggregate_metrics":
            return await self._aggregate_metrics()
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def handle_message(self, message: AgentMessage) -> None:
        """Lida com mensagem de outro agente."""
        msg_type = message.message_type

        # Rotear para agente destino se necessario
        if message.to_agent != self.agent_type:
            await self._forward_message(message)
            return

        if msg_type == "proposta_solicitada":
            # Iniciar workflow de proposta
            await self._handle_proposta_solicitada(message.payload)

        elif msg_type == "alerta_cct":
            # Processar alerta de CCT
            await self._handle_alerta_cct(message.payload)

        elif msg_type == "workflow_completed":
            # Marcar workflow como completo
            workflow_id = message.payload.get("workflow_id")
            if workflow_id in self.pending_workflows:
                self.pending_workflows[workflow_id]["status"] = "completed"
                self.pending_workflows[workflow_id]["completed_at"] = datetime.utcnow().isoformat()
                self.metrics["workflows_completed"] += 1

    async def _route_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Roteia mensagem para agente destino."""
        target_agent = AgentType(data["to_agent"])
        message = AgentMessage(**data["message"])

        if target_agent in self.registered_agents:
            await self.registered_agents[target_agent].receive_message(message)
            self.metrics["messages_routed"] += 1
            return {"routed": True, "to": target_agent.value}
        else:
            return {"routed": False, "error": f"Agent {target_agent.value} not registered"}

    async def _forward_message(self, message: AgentMessage) -> None:
        """Encaminha mensagem para outro agente."""
        if message.to_agent in self.registered_agents:
            await self.registered_agents[message.to_agent].receive_message(message)
            self.metrics["messages_routed"] += 1

    async def _start_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia um workflow cross-phase."""
        workflow_type = data.get("workflow_type")
        workflow_id = f"wf_{workflow_type}_{datetime.utcnow().timestamp()}"

        self.pending_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "type": workflow_type,
            "data": data,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "steps_completed": []
        }

        if workflow_type == "proposta_comercial":
            # Coordenar workflow de proposta
            await self._execute_proposta_workflow(workflow_id, data)

        elif workflow_type == "admissao_funcionario":
            # Coordenar workflow de admissao
            await self._execute_admissao_workflow(workflow_id, data)

        return {"workflow_id": workflow_id, "status": "started"}

    async def _execute_proposta_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Executa workflow de proposta comercial."""
        # Passo 1: Solicitar validacao CCT
        if AgentType.CCT_COMPLIANCE in self.registered_agents:
            await self.registered_agents[AgentType.CCT_COMPLIANCE].receive_message(
                AgentMessage(
                    from_agent=self.agent_type,
                    to_agent=AgentType.CCT_COMPLIANCE,
                    message_type="solicitar_proposta",
                    payload={
                        "workflow_id": workflow_id,
                        "cargos": data.get("cargos", []),
                        "margem": data.get("margem", 15)
                    }
                )
            )
            self.pending_workflows[workflow_id]["steps_completed"].append("cct_validation")

    async def _execute_admissao_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Executa workflow de admissao."""
        # Passo 1: Validar cargo CCT
        if AgentType.CCT_COMPLIANCE in self.registered_agents:
            await self.registered_agents[AgentType.CCT_COMPLIANCE].receive_message(
                AgentMessage(
                    from_agent=self.agent_type,
                    to_agent=AgentType.CCT_COMPLIANCE,
                    message_type="validar_funcionario",
                    payload={
                        "workflow_id": workflow_id,
                        **data
                    }
                )
            )
            self.pending_workflows[workflow_id]["steps_completed"].append("cct_validation")

    async def _handle_proposta_solicitada(self, data: Dict[str, Any]) -> None:
        """Lida com solicitacao de proposta vinda do email."""
        logger.info(f"Proposta solicitada via email: {data.get('email_id')}")

        # Iniciar workflow de proposta
        await self._start_workflow({
            "workflow_type": "proposta_comercial",
            "source": "email",
            "email_id": data.get("email_id"),
            "analysis": data.get("analysis")
        })

    async def _handle_alerta_cct(self, data: Dict[str, Any]) -> None:
        """Lida com alerta de nao conformidade CCT."""
        logger.warning(f"Alerta CCT: {data.get('cargo')} - {data.get('alertas')}")
        self.metrics["alerts_generated"] += 1

        # Em producao: enviar notificacao, criar tarefa, etc.

    async def _get_system_status(self) -> Dict[str, Any]:
        """Retorna status de todos os agentes."""
        status = {
            "hub_status": self.get_status(),
            "registered_agents": {},
            "pending_workflows": len(self.pending_workflows),
            "metrics": self.metrics
        }

        for agent_type, agent in self.registered_agents.items():
            status["registered_agents"][agent_type.value] = agent.get_status()

        return status

    async def _aggregate_metrics(self) -> Dict[str, Any]:
        """Agrega metricas de todos os agentes."""
        aggregated = {
            "timestamp": datetime.utcnow().isoformat(),
            "hub_metrics": self.metrics,
            "agent_metrics": {}
        }

        for agent_type, agent in self.registered_agents.items():
            agent_status = agent.get_status()
            aggregated["agent_metrics"][agent_type.value] = agent_status.get("stats", {})

        return aggregated
