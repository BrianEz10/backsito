from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.modules.auth.models import Usuario
from app.modules.unidad_medida.schemas import UnidadMedidaCreate, UnidadMedidaUpdate, UnidadMedidaOut
from app.modules.unidad_medida.service import UnidadMedidaService


router = APIRouter(prefix="/unidades-medida", tags=["unidades-medida"])


def get_unidad_medida_service(session: SessionDep) -> UnidadMedidaService:
    return UnidadMedidaService(session)


@router.get("/", response_model=list[UnidadMedidaOut])
def listar(_user: CurrentUser, svc: UnidadMedidaService = Depends(get_unidad_medida_service)) -> list[UnidadMedidaOut]:
    return svc.get_all()


@router.get("/{id}", response_model=UnidadMedidaOut)
def obtener(id: int, _user: CurrentUser, svc: UnidadMedidaService = Depends(get_unidad_medida_service)) -> UnidadMedidaOut:
    return svc.get_by_id(id)


@router.post("/", response_model=UnidadMedidaOut, status_code=status.HTTP_201_CREATED)
def crear(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: UnidadMedidaCreate, svc: UnidadMedidaService = Depends(get_unidad_medida_service)) -> UnidadMedidaOut:
    return svc.create(data)


@router.patch("/{id}", response_model=UnidadMedidaOut)
def actualizar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: UnidadMedidaUpdate, svc: UnidadMedidaService = Depends(get_unidad_medida_service)) -> UnidadMedidaOut:
    return svc.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: UnidadMedidaService = Depends(get_unidad_medida_service)) -> None:
    svc.delete(id)