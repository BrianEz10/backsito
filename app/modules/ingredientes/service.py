from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from datetime import datetime, timezone
from app.modules.ingredientes.models import Ingrediente
from app.modules.ingredientes.schemas import IngredienteCreate, IngredienteUpdate, IngredienteOut
from app.modules.ingredientes.uow import IngredienteUnitOfWork

class IngredienteService:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def _get_or_404(self, uow: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingrediente con id {ingrediente_id} no encontrado")
        return ingrediente
    
    def create(self, data: IngredienteCreate) -> IngredienteOut:
        with IngredienteUnitOfWork(self._session) as uow:
            existing = uow.ingredientes.get_by_nombre(data.nombre)
            if existing:
                raise HTTPException(409, "Ya existe un ingrediente con ese nombre")
            ingrediente = Ingrediente.model_validate(data)
            uow.ingredientes.add(ingrediente)
            result = IngredienteOut.model_validate(ingrediente)
        return result

    def get_by_id(self, ingrediente_id: int) -> IngredienteOut:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            result = IngredienteOut.model_validate(ingrediente)
        return result
    
    def get_all(self) -> list[IngredienteOut]:
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingredientes.get_all()
            result = [IngredienteOut.model_validate(i) for i in ingredientes]
        return result
    
    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredienteOut:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(ingrediente, field, value)
            uow.ingredientes.add(ingrediente)
            result = IngredienteOut.model_validate(ingrediente)
        return result
    
    def delete(self, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            ingrediente.deleted_at = datetime.now(timezone.utc)