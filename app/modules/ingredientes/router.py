from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.modules.auth.models import Usuario
from app.modules.ingredientes.schemas import IngredienteCreate, IngredienteUpdate, IngredienteOut
from app.modules.ingredientes.service import IngredienteService


router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])

def get_ingrediente_service(session: SessionDep) -> IngredienteService:
    return IngredienteService(session)


@router.get("/", response_model=list[IngredienteOut])
def listar( _user: CurrentUser, svc: IngredienteService = Depends(get_ingrediente_service)):
    return svc.get_all()


@router.post("/", response_model=IngredienteOut, status_code=201)
def crear(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: IngredienteCreate, svc: IngredienteService = Depends(get_ingrediente_service)):
    return svc.create(data)


@router.get("/{id}", response_model=IngredienteOut)
def obtener(id: int, _user: CurrentUser, svc: IngredienteService = Depends(get_ingrediente_service)):
    return svc.get_by_id(id)


@router.patch("/{id}", response_model=IngredienteOut)
def actualizar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: IngredienteUpdate, svc: IngredienteService = Depends(get_ingrediente_service)):
    return svc.update(id, data)


@router.delete("/{id}", status_code=204)
def eliminar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: IngredienteService = Depends(get_ingrediente_service)):
    svc.delete(id)