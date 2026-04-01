"""
WebSocket endpoint para eventos de Gestao de Pessoas.
Permite que o frontend receba eventos em tempo real.
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..events import GPEventBus, get_event_bus

logger = logging.getLogger(__name__)
router = APIRouter()


class GPWebSocketManager:
    """Gerenciador de conexoes WebSocket de Gestao de Pessoas."""

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str, event_bus: GPEventBus) -> None:
        """Aceita e registra uma conexao."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        await event_bus.register_websocket(websocket)
        logger.info(f"WebSocket conectado: user={user_id}")

    async def disconnect(self, user_id: str, event_bus: GPEventBus) -> None:
        """Remove uma conexao."""
        if user_id in self.active_connections:
            ws = self.active_connections.pop(user_id)
            await event_bus.unregister_websocket(ws)
            logger.info(f"WebSocket desconectado: user={user_id}")

    async def send_personal(self, user_id: str, message: dict) -> None:
        """Envia mensagem para um usuario especifico."""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


manager = GPWebSocketManager()


@router.websocket("/ws/gp/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    """
    Endpoint WebSocket para eventos de Gestao de Pessoas.

    Conectar em: ws://server/api/v1/gp/ws/gp/{user_id}

    Mensagens aceitas:
    - {"type": "ping"} -> responde {"type": "pong"}
    - {"type": "subscribe", "events": ["gp.ponto.*"]} -> filtra eventos
    """
    event_bus = get_event_bus()
    await manager.connect(websocket, user_id, event_bus)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "subscribe":
                    await websocket.send_json(
                        {
                            "type": "subscribed",
                            "events": message.get("events", []),
                        }
                    )
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    except WebSocketDisconnect:
        await manager.disconnect(user_id, event_bus)
