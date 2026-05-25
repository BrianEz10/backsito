from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.modules.auth.models import Usuario
from app.modules.roles.schemas import RolCreate, RolUpdate, RolOut
from app.modules.roles.service import RolService
router = APIRouter(prefix="/roles", tags=["roles"])
def get_rol_service(session: SessionDep) -> RolService:
    return RolService(session)
@router.get("/", response_model=list[RolOut])
def listar(
    _user: CurrentUser,
    svc: RolService = Depends(get_rol_service),
) -> list[RolOut]:
    return svc.get_all()
@router.get("/{codigo}", response_model=RolOut)
def obtener(
    codigo: str,
    _user: CurrentUser,
    svc: RolService = Depends(get_rol_service),
) -> RolOut:
    return svc.get_by_codigo(codigo)
@router.post("/", response_model=RolOut, status_code=status.HTTP_201_CREATED)
def crear(
    _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))],
    data: RolCreate,
    svc: RolService = Depends(get_rol_service),
) -> RolOut:
    return svc.create(data)
@router.patch("/{codigo}", response_model=RolOut)
def actualizar(
    codigo: str,
    _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))],
    data: RolUpdate,
    svc: RolService = Depends(get_rol_service),
) -> RolOut:
    return svc.update(codigo, data)