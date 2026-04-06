"""
Mixin reutilizável para qualquer service que precise publicar eventos
no ConectaEventBus sem boilerplate.

Uso:
    class MeuService(PublisherMixin):
        async def meu_metodo(self):
            await self.publish_event(
                tipo=EventTypes.DP_FUNCIONARIO_ADMITIDO,
                payload={"employee_id": "..."},
                origem="dp",
            )
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PublisherMixin:
    """Adiciona capacidade de publicar eventos ao ConectaEventBus."""

    async def publish_event(
        self,
        tipo: str,
        payload: dict[str, Any],
        origem: str,
        cliente_id: str | None = None,
        funcionario_id: str | None = None,
        competencia: str | None = None,
    ) -> bool:
        """Publica evento no barramento. Nunca lança exceção."""
        try:
            from infrastructure.event_bus import ConectaEvent, event_bus

            evento = ConectaEvent(
                event_type=tipo,
                payload=payload,
                source_module=origem,
                cliente_id=cliente_id,
                funcionario_id=funcionario_id,
                competencia=competencia,
            )
            result = await event_bus.publish(evento)
            logger.debug(
                "Evento publicado: %s | cliente=%s | func=%s",
                tipo,
                cliente_id,
                funcionario_id,
            )
            return bool(result)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Falha ao publicar evento %s: %s", tipo, exc)
            return False
