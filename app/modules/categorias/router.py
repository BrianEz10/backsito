from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.modules.auth.models import Usuario
from app.modules.categorias.schemas import CategoriaCreate, CategoriaUpdate, CategoriaOut, CategoriaWithHijos
from app.modules.categorias.service import CategoriaService


router = APIRouter(prefix="/categorias", tags=["categorias"])


def get_categoria_service(session: SessionDep) -> CategoriaService:
    return CategoriaService(session)


@router.get("/", response_model=list[CategoriaOut])
def listar(_user: CurrentUser, parent_id: int = Query(default=None), offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), svc: CategoriaService = Depends(get_categoria_service)):
    return svc.get_all(parent_id, offset, limit)


@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: CategoriaCreate, svc: CategoriaService = Depends(get_categoria_service)):
    return svc.create(data)


@router.get("/{id}", response_model=CategoriaWithHijos)
def obtener(id: int, _user: CurrentUser, svc: CategoriaService = Depends(get_categoria_service)):
    return svc.get_by_id(id)


@router.patch("/{id}", response_model=CategoriaOut)
def actualizar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: CategoriaUpdate, svc: CategoriaService = Depends(get_categoria_service)):
    return svc.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: CategoriaService = Depends(get_categoria_service)):
    svc.delete(id)