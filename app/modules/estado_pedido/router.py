from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.modules.auth.models import Usuario
from app.modules.estado_pedido.schemas import EstadoPedidoCreate, EstadoPedidoUpdate, EstadoPedidoOut
from app.modules.estado_pedido.service import EstadoPedidoService


router = APIRouter(prefix="/estados-pedido", tags=["estados-pedido"])

def get_estado_service(session: SessionDep) -> EstadoPedidoService:
    return EstadoPedidoService(session)


@router.get("/", response_model=list[EstadoPedidoOut])
def listar(_user: CurrentUser, svc: EstadoPedidoService = Depends(get_estado_service)) -> list[EstadoPedidoOut]:
    return svc.get_all()


@router.get("/{codigo}", response_model=EstadoPedidoOut)
def obtener(codigo: str, _user: CurrentUser, svc: EstadoPedidoService = Depends(get_estado_service)) -> EstadoPedidoOut:
    return svc.get_by_codigo(codigo)


@router.post("/", response_model=EstadoPedidoOut, status_code=status.HTTP_201_CREATED)
def crear(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: EstadoPedidoCreate, svc: EstadoPedidoService = Depends(get_estado_service)) -> EstadoPedidoOut:
    return svc.create(data)


@router.patch("/{codigo}", response_model=EstadoPedidoOut)
def actualizar(codigo: str, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: EstadoPedidoUpdate, svc: EstadoPedidoService = Depends(get_estado_service)) -> EstadoPedidoOut:
    return svc.update(codigo, data)


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(codigo: str, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: EstadoPedidoService = Depends(get_estado_service)) -> None:
    svc.delete(codigo)