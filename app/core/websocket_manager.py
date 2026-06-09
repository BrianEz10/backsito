import logging
from typing import Any
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger("app.core.websocket_manager")


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Nueva conexión. Total activas: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logger.info(f"Conexión finalizada. Total activas: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict[str, Any]) -> None:
        payload = {
            "event": event_type,
            "data": jsonable_encoder(data),
        }
        if not self.active_connections:
            logger.info(f"Broadcast {event_type} descartado (sin conexiones activas)")
            return

        logger.info(f"Broadcast {event_type} a {len(self.active_connections)} conexiones.")
        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception as e:
                logger.warning(f"Error broadcast, removiendo conexión: {e}")
                self.active_connections.discard(connection)


manager = ConnectionManager()