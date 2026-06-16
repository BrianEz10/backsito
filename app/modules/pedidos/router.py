from typing import Annotated
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.core.security import decode_access_token
from app.modules.usuarios.models import Usuario
from app.modules.pedidos.schemas import HistorialOut, PedidoCreate, PedidoOut, AvanceEstadoRequest, PaginatedPedidos
from app.modules.pedidos.service import PedidoService
from app.core.ws_manager import manager


router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def get_pedido_service(session: SessionDep) -> PedidoService:
    return PedidoService(session)


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
async def crear(data: PedidoCreate, current_user: Annotated[Usuario, Depends(require_role(["CLIENT", "CAJERO", "ADMIN", "PEDIDOS"]))], svc: PedidoService = Depends(get_pedido_service)) -> PedidoOut:
    roles = [rol.codigo for rol in current_user.roles]
    return await svc.create(data, current_user.id, roles)


@router.get("/", response_model=PaginatedPedidos)
def listar(current_user: CurrentUser, page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), svc: PedidoService = Depends(get_pedido_service)) -> PaginatedPedidos:
    roles = [rol.codigo for rol in current_user.roles]
    return svc.get_all(current_user.id, roles, page, size)


@router.get("/{id}", response_model=PedidoOut)
def obtener(id: int, current_user: CurrentUser,svc: PedidoService = Depends(get_pedido_service)) -> PedidoOut:
    roles = [rol.codigo for rol in current_user.roles]
    return svc.get_by_id(id, current_user.id, roles)


@router.get("/{id}/historial", response_model=list[HistorialOut])
def obtener_historial(id: int, current_user: CurrentUser, svc: PedidoService = Depends(get_pedido_service)) -> list[HistorialOut]:
    roles = [rol.codigo for rol in current_user.roles]
    return svc.get_historial(id, current_user.id, roles)


@router.patch("/{id}/estado", response_model=PedidoOut)
async def avanzar_estado(id: int, data: AvanceEstadoRequest, current_user: Annotated[Usuario, Depends(require_role(["ADMIN", "PEDIDOS"]))], svc: PedidoService = Depends(get_pedido_service)) -> PedidoOut:
    roles = [rol.codigo for rol in current_user.roles]
    return await svc.avanzar_estado(id, data, current_user.id, roles)


@router.delete("/{id}", response_model=PedidoOut)
async def cancelar_pedido(id: int, current_user: CurrentUser, svc: PedidoService = Depends(get_pedido_service)) -> PedidoOut:
    roles = [rol.codigo for rol in current_user.roles]
    return await svc.avanzar_estado(id, AvanceEstadoRequest(estado_hacia="CANCELADO", motivo="Cancelado por el cliente"), current_user.id, roles,)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...), pedido_id: int | None = Query(None)):
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Token inválido o expirado")
        return

    roles: list[str] = payload.get("roles", [])
    is_admin = any(r in ("ADMIN", "PEDIDOS", "CAJERO") for r in roles)
    usuario_id: int | None = payload.get("usuario_id")

    channel = str(pedido_id) if pedido_id else ("admin" if is_admin else f"user:{usuario_id}" if usuario_id else "user:unknown")
    await manager.connect(websocket, channel)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, channel)