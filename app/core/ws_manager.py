import logging
from typing import Any
from fastapi import WebSocket

logger = logging.getLogger("app.core.ws_manager")


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        await websocket.accept()
        if channel not in self.connections:
            self.connections[channel] = set()
        self.connections[channel].add(websocket)
        logger.info(f"Conectado al canal {channel}. Total en canal: {len(self.connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        if channel in self.connections:
            self.connections[channel].discard(websocket)
            if not self.connections[channel]:
                del self.connections[channel]
            logger.info(f"Desconectado del canal {channel}")

    async def broadcast_pedido(self, pedido_id: int, evento: dict[str, Any], usuario_id: int | None = None) -> None:
        channel = str(pedido_id)
        await self._broadcast_to_channel(channel, evento)
        await self._broadcast_to_channel("admin", evento)
        if usuario_id is not None:
            await self._broadcast_to_channel(f"user:{usuario_id}", evento)

    async def broadcast_to_role(self, rol: str, evento: dict[str, Any]) -> None:
        await self._broadcast_to_channel(rol, evento)

    async def _broadcast_to_channel(self, channel: str, evento: dict[str, Any]) -> None:
        if channel not in self.connections:
            return
        logger.info(f"Broadcast a canal {channel}: {len(self.connections[channel])} conexiones")
        for ws in list(self.connections[channel]):
            try:
                await ws.send_json(evento)
            except Exception as e:
                logger.warning(f"Error en broadcast a canal {channel}, removiendo: {e}")
                self.connections[channel].discard(ws)
        if channel in self.connections and not self.connections[channel]:
            del self.connections[channel]


manager = ConnectionManager()