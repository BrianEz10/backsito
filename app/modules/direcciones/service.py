from sqlmodel import Session
from app.modules.direcciones.models import DireccionEntrega
from app.modules.direcciones.schemas import DireccionCreate, DireccionUpdate, DireccionOut
from app.modules.direcciones.uow import DireccionUnitOfWork
from app.core.errors import http_error

class DireccionService:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def _get_mia_or_404(self, uow: DireccionUnitOfWork, usuario_id: int, direccion_id: int) -> DireccionEntrega:
        direccion = uow.direcciones.get_by_id(direccion_id)
        if not direccion or direccion.usuario_id != usuario_id:
            raise http_error(404, "Direccion no encontrada", "NOT_FOUND")
        return direccion
    
    def get_mis_direcciones(self, usuario_id: int) -> list[DireccionOut]:
        with DireccionUnitOfWork(self._session) as uow:
            direcciones = uow.direcciones.get_by_usuario(usuario_id)
            result = [DireccionOut.model_validate(d) for d in direcciones]
        return result
    
    def get_by_id(self, usuario_id: int, direccion_id: int) -> DireccionOut:
        with DireccionUnitOfWork(self._session) as uow:
            direccion = self._get_mia_or_404(uow, usuario_id, direccion_id)
            result = DireccionOut.model_validate(direccion)
        return result
    
    def marcar_principal(self, usuario_id: int, direccion_id: int) -> DireccionOut:
        with DireccionUnitOfWork(self._session) as uow:
            direccion = self._get_mia_or_404(uow, usuario_id, direccion_id)
            actual_principal = uow.direcciones.get_principal(usuario_id)
            if actual_principal and actual_principal.id != direccion_id:
                actual_principal.es_principal = False
            direccion.es_principal = True
            result = DireccionOut.model_validate(direccion)
        return result
    
    def create(self, usuario_id: int, data: DireccionCreate) -> DireccionOut:
        with DireccionUnitOfWork(self._session) as uow:
            datos = data.model_dump()
            datos["usuario_id"] = usuario_id
            direccion = DireccionEntrega(**datos)
            uow.direcciones.add(direccion)
            result = DireccionOut.model_validate(direccion)
        return result
    
    def update(self, usuario_id: int, direccion_id: int, data: DireccionUpdate) -> DireccionOut:
        with DireccionUnitOfWork(self._session) as uow:
            direccion = self._get_mia_or_404(uow, usuario_id, direccion_id)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(direccion, field, value)
            uow.direcciones.add(direccion)
            result = DireccionOut.model_validate(direccion)
        return result
    
    def admin_get_by_id(self, direccion_id: int) -> DireccionOut:
        with DireccionUnitOfWork(self._session) as uow:
            direccion = uow.direcciones.get_by_id(direccion_id)
            if not direccion:
                raise http_error(404, "Direccion no encontrada", "NOT_FOUND")
            result = DireccionOut.model_validate(direccion)
        return result

    def delete(self, usuario_id: int, direccion_id: int) -> None:
        with DireccionUnitOfWork(self._session) as uow:
            direccion = self._get_mia_or_404(uow, usuario_id, direccion_id)
            uow.direcciones.soft_delete(direccion)