from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.unidad_medida.schemas import UnidadMedidaCreate, UnidadMedidaUpdate, UnidadMedidaOut
from app.modules.unidad_medida.uow import UnidadMedidaUnitOfWork

class UnidadMedidaService:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def _get_or_404(self, uow: UnidadMedidaUnitOfWork, unidad_medida_id: int) -> UnidadMedida:
        unidad_medida = uow.unidad_medida.get_by_id(unidad_medida_id)
        if not unidad_medida:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unidad de medida no encontrada")
        return unidad_medida
   
    def create(self, data: UnidadMedidaCreate) -> UnidadMedidaOut:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            existing = uow.unidad_medida.get_by_simbolo(data.simbolo)
            if existing:
                raise HTTPException(409, "Ya existe una unidad con ese simbolo")
            unidad = UnidadMedida.model_validate(data)
            uow.unidad_medida.add(unidad)
            result = UnidadMedidaOut.model_validate(unidad)
        return result

    def get_all(self) -> list[UnidadMedidaOut]:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidades = uow.unidad_medida.get_all()
            result = [UnidadMedidaOut.model_validate(u) for u in unidades]
        return result

    def get_by_id(self, unidad_medida_id: int) -> UnidadMedidaOut:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidad = self._get_or_404(uow, unidad_medida_id)
            result = UnidadMedidaOut.model_validate(unidad)
        return result
 
    def update(self, unidad_medida_id: int, data: UnidadMedidaUpdate) -> UnidadMedidaOut:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidad = self._get_or_404(uow, unidad_medida_id)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(unidad, field, value)
            uow.unidad_medida.add(unidad)
            result = UnidadMedidaOut.model_validate(unidad)
        return result
  
    def delete(self, unidad_medida_id: int) -> None:
        with UnidadMedidaUnitOfWork(self._session) as uow:
            unidad = self._get_or_404(uow, unidad_medida_id)
            unidad.deleted_at = datetime.now(timezone.utc)