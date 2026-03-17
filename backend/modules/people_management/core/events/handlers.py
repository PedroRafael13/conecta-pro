"""Base Handler para eventos de Gestao de Pessoas."""

import logging
from abc import ABC, abstractmethod

from .event_bus import Event, GPEventBus

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    """
    Classe base para handlers de eventos.
    Cada Agent deve herdar desta classe e implementar os metodos abstratos.
    """

    def __init__(self, event_bus: GPEventBus) -> None:
        self.event_bus = event_bus
        self._register_handlers()

    @property
    @abstractmethod
    def handled_events(self) -> list[str]:
        """Lista de tipos de eventos que este handler processa."""

    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Processa um evento."""

    def _register_handlers(self) -> None:
        """Registra este handler para os eventos que ele processa."""
        for event_type in self.handled_events:
            self.event_bus.subscribe(event_type, self.handle)
            logger.debug(f"{self.__class__.__name__} inscrito para {event_type}")
