"""
WebSocket para atualizações em tempo real de disputas de pregão.

Eventos emitidos:
- lance_enviado: Novo lance registrado
- lance_coberto: Nosso lance foi coberto
- melhor_colocado: Assumimos a liderança
- convocacao: Pregoeiro convocou para documentos
- fim_disputa: Disputa encerrada
- status_update: Atualização geral de status
"""

import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class DisputeConnectionManager:
    """Gerenciador de conexões WebSocket por sessão de disputa."""

    def __init__(self):
        # {sessao_id: Set[WebSocket]}
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, sessao_id: str):
        await websocket.accept()
        if sessao_id not in self.active_connections:
            self.active_connections[sessao_id] = set()
        self.active_connections[sessao_id].add(websocket)
        logger.info(f"WebSocket conectado: sessao={sessao_id}, total={len(self.active_connections[sessao_id])}")

    def disconnect(self, websocket: WebSocket, sessao_id: str):
        if sessao_id in self.active_connections:
            self.active_connections[sessao_id].discard(websocket)
            if not self.active_connections[sessao_id]:
                del self.active_connections[sessao_id]
        logger.info(f"WebSocket desconectado: sessao={sessao_id}")

    async def broadcast_to_session(self, sessao_id: str, event: str, data: dict):
        """Envia evento para todos os clientes conectados a uma sessão."""
        if sessao_id not in self.active_connections:
            return

        message = json.dumps(
            {
                "event": event,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        disconnected: set[WebSocket] = set()
        for connection in self.active_connections[sessao_id]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Erro ao enviar WebSocket: {e}")
                disconnected.add(connection)

        for conn in disconnected:
            self.active_connections[sessao_id].discard(conn)

    async def broadcast_all(self, event: str, data: dict):
        """Envia evento para TODAS as sessões ativas."""
        for sessao_id in list(self.active_connections.keys()):
            await self.broadcast_to_session(sessao_id, event, data)


# Instância global do gerenciador
manager = DisputeConnectionManager()


@router.websocket("/ws/disputas/{sessao_id}")
async def websocket_disputa(websocket: WebSocket, sessao_id: str):
    """
    WebSocket endpoint para acompanhamento de disputa em tempo real.

    Args:
        sessao_id: ID da sessão de disputa (pregão)

    Eventos recebidos do cliente:
        - ping: Keep-alive
        - request_status: Solicita status atual

    Eventos enviados ao cliente:
        - connected: Confirmação de conexão
        - lance_enviado: {item_id, valor, posicao, timestamp}
        - lance_coberto: {item_id, valor_anterior, valor_novo, concorrente}
        - melhor_colocado: {item_id, valor, mensagem}
        - convocacao: {tipo, prazo_minutos, mensagem}
        - fim_disputa: {resultado, itens_ganhos, valor_total}
        - status_update: {status, mensagem}
        - pong: Resposta a ping
        - error: {code, message}
    """
    await manager.connect(websocket, sessao_id)

    try:
        # Envia status inicial
        await websocket.send_text(
            json.dumps(
                {
                    "event": "connected",
                    "data": {
                        "sessao_id": sessao_id,
                        "message": "Conectado ao WebSocket de disputa",
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        # Loop de recebimento de mensagens
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0,
                )

                message = json.loads(data)
                event = message.get("event", "")

                if event == "ping":
                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "pong",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )

                elif event == "pong":
                    pass  # Resposta ao nosso ping, conexão viva

                elif event == "request_status":
                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "status_update",
                                "data": {
                                    "status": "em_andamento",
                                    "sessao_id": sessao_id,
                                },
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )

            except TimeoutError:
                # Envia ping para manter conexão viva
                try:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "ping",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )
                except Exception:
                    break

    except WebSocketDisconnect:
        logger.info(f"Cliente desconectou: sessao={sessao_id}")
    except Exception as e:
        logger.error(f"Erro no WebSocket disputa: {e}")
    finally:
        manager.disconnect(websocket, sessao_id)


# ─── Funções para serem chamadas pelo warrior_agent ─────────────────


async def notify_lance_enviado(sessao_id: str, item_id: str, valor: float, posicao: int):
    """Notifica que um lance foi enviado."""
    await manager.broadcast_to_session(
        sessao_id,
        "lance_enviado",
        {
            "item_id": item_id,
            "valor": valor,
            "posicao": posicao,
        },
    )


async def notify_lance_coberto(sessao_id: str, item_id: str, valor_anterior: float, valor_novo: float):
    """Notifica que nosso lance foi coberto."""
    await manager.broadcast_to_session(
        sessao_id,
        "lance_coberto",
        {
            "item_id": item_id,
            "valor_anterior": valor_anterior,
            "valor_novo": valor_novo,
        },
    )


async def notify_melhor_colocado(sessao_id: str, item_id: str, valor: float):
    """Notifica que assumimos a liderança."""
    await manager.broadcast_to_session(
        sessao_id,
        "melhor_colocado",
        {
            "item_id": item_id,
            "valor": valor,
            "mensagem": "Você está em primeiro lugar!",
        },
    )


async def notify_convocacao(sessao_id: str, tipo: str, prazo_minutos: int, mensagem: str):
    """Notifica convocação do pregoeiro."""
    await manager.broadcast_to_session(
        sessao_id,
        "convocacao",
        {
            "tipo": tipo,
            "prazo_minutos": prazo_minutos,
            "mensagem": mensagem,
            "urgente": True,
        },
    )


async def notify_fim_disputa(sessao_id: str, resultado: str, itens_ganhos: list, valor_total: float):
    """Notifica fim da disputa."""
    await manager.broadcast_to_session(
        sessao_id,
        "fim_disputa",
        {
            "resultado": resultado,
            "itens_ganhos": itens_ganhos,
            "valor_total": valor_total,
        },
    )
