"""
modules/fase5/agents/cct_agent.py - CCT Compliance Agent
========================================================
Agente de compliance CCT SINDCOND 2026
"""

import logging
from decimal import Decimal
from typing import Any

from ..cct_compliance.enums import TipoBeneficio, TipoCargo, TipoJornada
from ..cct_compliance.service import CCTComplianceService
from .base import AgentMessage, AgentTask, AgentType, BaseAgent

logger = logging.getLogger(__name__)


class CCTComplianceAgent(BaseAgent):
    """
    Agente de compliance CCT.

    Responsabilidades:
    1. Validar salarios contra CCT
    2. Verificar beneficios obrigatorios
    3. Calcular custos de funcionarios
    4. Gerar alertas de nao conformidade
    5. Suportar propostas comerciais
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(AgentType.CCT_COMPLIANCE, config)
        self.cct_service = CCTComplianceService()

    async def process_task(self, task: AgentTask) -> dict[str, Any]:
        """Processa tarefa de CCT."""
        task_type = task.task_type

        if task_type == "validar_salario":
            return await self._validar_salario(task.data)
        elif task_type == "validar_completo":
            return await self._validar_completo(task.data)
        elif task_type == "calcular_custo":
            return await self._calcular_custo(task.data)
        elif task_type == "gerar_proposta":
            return await self._gerar_proposta(task.data)
        elif task_type == "listar_cargos":
            return {"cargos": self.cct_service.listar_cargos()}
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def handle_message(self, message: AgentMessage) -> None:
        """Lida com mensagem de outro agente."""
        msg_type = message.message_type

        if msg_type == "validar_funcionario":
            # Validar funcionario e responder
            result = await self._validar_completo(message.payload)
            reply = AgentMessage(
                from_agent=self.agent_type,
                to_agent=message.from_agent,
                message_type="validacao_resultado",
                payload=result,
                reply_to=message.message_id,
            )
            await self.send_message(reply)

        elif msg_type == "solicitar_proposta":
            # Gerar proposta comercial
            result = await self._gerar_proposta(message.payload)
            reply = AgentMessage(
                from_agent=self.agent_type,
                to_agent=message.from_agent,
                message_type="proposta_gerada",
                payload=result,
                reply_to=message.message_id,
            )
            await self.send_message(reply)

    async def _validar_salario(self, data: dict[str, Any]) -> dict[str, Any]:
        """Valida salario contra CCT."""
        cargo = TipoCargo(data["cargo"])
        salario = Decimal(str(data["salario"]))

        return self.cct_service.validar_salario(cargo, salario)

    async def _validar_completo(self, data: dict[str, Any]) -> dict[str, Any]:
        """Executa validacao completa."""
        cargo = TipoCargo(data["cargo"])
        salario = Decimal(str(data["salario"]))
        jornada = TipoJornada(data.get("jornada", "44h_semanais"))
        beneficios = [TipoBeneficio(b) for b in data.get("beneficios", [])]

        validacao = self.cct_service.validar_completo(
            cargo=cargo, salario=salario, jornada=jornada, beneficios=beneficios
        )

        # Enviar alerta se nao conforme
        if validacao.status.value == "nao_conforme":
            await self.send_message(
                AgentMessage(
                    from_agent=self.agent_type,
                    to_agent=AgentType.INTEGRATION_HUB,
                    message_type="alerta_cct",
                    payload={"cargo": cargo.value, "status": validacao.status.value, "alertas": validacao.alertas},
                )
            )

        return validacao.model_dump()

    async def _calcular_custo(self, data: dict[str, Any]) -> dict[str, Any]:
        """Calcula custo de funcionario."""
        cargo = TipoCargo(data["cargo"])
        salario = Decimal(str(data["salario"])) if "salario" in data else None
        jornada = TipoJornada(data.get("jornada", "44h_semanais"))
        incluir_encargos = data.get("incluir_encargos", True)

        return self.cct_service.calcular_custo_funcionario(
            cargo=cargo, salario_base=salario, jornada=jornada, incluir_encargos=incluir_encargos
        )

    async def _gerar_proposta(self, data: dict[str, Any]) -> dict[str, Any]:
        """Gera proposta comercial."""
        cargos = data.get("cargos", [])
        margem = Decimal(str(data.get("margem", "15")))

        return self.cct_service.gerar_proposta_comercial(cargos=cargos, margem_lucro_percentual=margem)
