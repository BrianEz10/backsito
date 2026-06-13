from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from app.core.database import SessionDep
from app.core.deps import require_role
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UsuarioOut, UsuarioUpdate, AsignarRolesRequest, PaginatedUsuarios
from app.modules.usuarios.service import UsuarioService


router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def get_usuario_service(session: SessionDep) -> UsuarioService:
    return UsuarioService(session)


@router.get("/", response_model=PaginatedUsuarios)
def listar_usuarios(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), rol: str | None = Query(default=None), svc: UsuarioService = Depends(get_usuario_service)) -> PaginatedUsuarios:
    return svc.listar(page, size, rol)


@router.get("/{id}", response_model=UsuarioOut)
def obtener_usuario(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: UsuarioService = Depends(get_usuario_service)) -> UsuarioOut:
    return svc.get_by_id(id)


@router.patch("/{id}", response_model=UsuarioOut)
def actualizar_usuario(id: int, data: UsuarioUpdate, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: UsuarioService = Depends(get_usuario_service)) -> UsuarioOut:
    return svc.update(id, data)


@router.patch("/{id}/roles", response_model=UsuarioOut)
def asignar_roles(id: int, data: AsignarRolesRequest, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: UsuarioService = Depends(get_usuario_service)) -> UsuarioOut:
    return svc.asignar_roles(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: UsuarioService = Depends(get_usuario_service)) -> None:
    svc.delete(id, _admin.id)