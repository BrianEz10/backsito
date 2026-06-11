from typing import Annotated
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.core.security import decode_access_token
from app.modules.auth.models import Usuario
from app.modules.pedidos.schemas import PedidoCreate, PedidoOut, AvanceEstadoRequest, PaginatedPedidos
from app.modules.pedidos.service import PedidoService
from app.core.ws_manager import manager

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

def get_pedido_service(session: SessionDep) -> PedidoService:
    return PedidoService(session)


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def crear(data: PedidoCreate, current_user: CurrentUser, svc: PedidoService = Depends(get_pedido_service)) -> PedidoOut:
    roles = [rol.codigo for rol in current_user.roles]
    return svc.create(data, current_user.id, roles)


@router.get("/", response_model=PaginatedPedidos)
def listar(current_user: CurrentUser, page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), svc: PedidoService = Depends(get_pedido_service)) -> PaginatedPedidos:
    roles = [rol.codigo for rol in current_user.roles]
    return svc.get_all(current_user.id, roles, page, size)


@router.get("/{id}", response_model=PedidoOut)
def obtener(id: int, current_user: CurrentUser,svc: PedidoService = Depends(get_pedido_service)) -> PedidoOut:
    roles = [rol.codigo for rol in current_user.roles]
    return svc.get_by_id(id, current_user.id, roles)


@router.patch("/{id}/estado", response_model=PedidoOut)
async def avanzar_estado(id: int, data: AvanceEstadoRequest, current_user: CurrentUser, svc: PedidoService = Depends(get_pedido_service)) -> PedidoOut:
    roles = [rol.codigo for rol in current_user.roles]
    return await svc.avanzar_estado(id, data, current_user.id, roles)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: PedidoService = Depends(get_pedido_service)) -> None:
    svc.delete(id)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    pedido_id: int | None = Query(None),
):
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Token inválido o expirado")
        return

    roles: list[str] = payload.get("roles", [])
    is_admin = any(r in ("ADMIN", "PEDIDOS") for r in roles)

    channel = str(pedido_id) if pedido_id else ("admin" if is_admin else "user:unknown")
    await manager.connect(websocket, channel)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, channel)