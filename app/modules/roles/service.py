from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.roles.models import Rol
from app.modules.roles.schemas import RolCreate, RolUpdate, RolOut
from app.modules.roles.uow import RolUnitOfWork

class RolService:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def _get_or_404(self, uow: RolUnitOfWork, codigo: str) -> Rol:
        rol = uow.roles.get_by_codigo(codigo)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con codigo {codigo} no encontrado"
            )
        return rol
   
    def get_all(self) -> list[RolOut]:
        with RolUnitOfWork(self._session) as uow:
            roles = uow.roles.get_all()
            result = [RolOut.model_validate(r) for r in roles]
        return result
  
    def get_by_codigo(self, codigo: str) -> RolOut:
        with RolUnitOfWork(self._session) as uow:
            rol = self._get_or_404(uow, codigo)
            result = RolOut.model_validate(rol)
        return result
  
    def create(self, data: RolCreate) -> RolOut:
        with RolUnitOfWork(self._session) as uow:
            existing = uow.roles.get_by_codigo(data.codigo)
            if existing:
                raise HTTPException(409, "Ya existe un rol con ese codigo")
            rol = Rol.model_validate(data)
            uow.roles.add(rol)
            result = RolOut.model_validate(rol)
        return result

    def update(self, codigo: str, data: RolUpdate) -> RolOut:
        with RolUnitOfWork(self._session) as uow:
            rol = self._get_or_404(uow, codigo)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(rol, field, value)
            uow.roles.add(rol)
            result = RolOut.model_validate(rol)
        return result