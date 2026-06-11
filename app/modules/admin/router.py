from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from app.core.database import SessionDep
from app.core.deps import require_role
from app.modules.auth.models import Usuario
from app.modules.admin.schemas import AdminUserOut, AdminUserUpdate, AdminAsignarRolesRequest
from app.modules.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])

def get_admin_service(session: SessionDep) -> AdminService:
    return AdminService(session)


@router.get("/usuarios", response_model=list[AdminUserOut])
def listar_usuarios(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), rol: str | None = None, svc: AdminService = Depends(get_admin_service)) -> list[AdminUserOut]:
    return svc.listar(offset, limit, rol)


@router.get("/usuarios/{id}", response_model=AdminUserOut)
def obtener_usuario(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: AdminService = Depends(get_admin_service)) -> AdminUserOut:
    return svc.get_by_id(id)


@router.patch("/usuarios/{id}", response_model=AdminUserOut)
def actualizar_usuario(id: int, data: AdminUserUpdate, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: AdminService = Depends(get_admin_service)) -> AdminUserOut:
    return svc.update(id, data)


@router.patch("/usuarios/{id}/roles", response_model=AdminUserOut)
def asignar_roles(id: int, data: AdminAsignarRolesRequest, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: AdminService = Depends(get_admin_service)) -> AdminUserOut:
    return svc.asignar_roles(id, data)


@router.delete("/usuarios/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: AdminService = Depends(get_admin_service)) -> None:
    svc.delete(id, _admin.id)