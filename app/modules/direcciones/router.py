from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.deps import SessionDep, CurrentUser, require_role
from app.modules.direcciones.schemas import DireccionCreate, DireccionUpdate, DireccionOut
from app.modules.direcciones.service import DireccionService
from app.modules.usuarios.models import Usuario


router = APIRouter(tags=["Mis Direcciones"])

def get_direccion_service(session: SessionDep) -> DireccionService:
    return DireccionService(session)


@router.get("/admin/direcciones/{direccion_id}", response_model=DireccionOut)
def admin_obtener_direccion(
    direccion_id: int,
    _admin: Annotated[Usuario, Depends(require_role(["ADMIN", "PEDIDOS"]))],
    svc: DireccionService = Depends(get_direccion_service),
) -> DireccionOut:
    return svc.admin_get_by_id(direccion_id)


@router.get("/mis-direcciones", response_model=list[DireccionOut])
def listar_direcciones(current_user: CurrentUser, svc: DireccionService = Depends(get_direccion_service)) -> list[DireccionOut]:
    return svc.get_mis_direcciones(current_user.id)


@router.get("/mis-direcciones/{direccion_id}", response_model=DireccionOut)
def obtener_direccion(direccion_id: int, current_user: CurrentUser, svc: DireccionService = Depends(get_direccion_service)) -> DireccionOut:
    return svc.get_by_id(current_user.id, direccion_id)


@router.post("/mis-direcciones", response_model=DireccionOut, status_code=status.HTTP_201_CREATED)
def crear_direccion(data: DireccionCreate, current_user: CurrentUser, svc: DireccionService = Depends(get_direccion_service)) -> DireccionOut:
    return svc.create(current_user.id, data)


@router.patch("/mis-direcciones/{direccion_id}", response_model=DireccionOut)
def actualizar_direccion(direccion_id: int, data: DireccionUpdate, current_user: CurrentUser, svc: DireccionService = Depends(get_direccion_service)) -> DireccionOut:
    return svc.update(current_user.id, direccion_id, data)


@router.patch("/mis-direcciones/{direccion_id}/principal", response_model=DireccionOut)
def marcar_principal(direccion_id: int, current_user: CurrentUser, svc: DireccionService = Depends(get_direccion_service)) -> DireccionOut:
    return svc.marcar_principal(current_user.id, direccion_id)


@router.delete("/mis-direcciones/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_direccion(direccion_id: int, current_user: CurrentUser, svc: DireccionService = Depends(get_direccion_service)) -> None:
    svc.delete(current_user.id, direccion_id)