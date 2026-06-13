from sqlmodel import Session
from app.modules.ingredientes.models import Ingrediente
from app.modules.ingredientes.schemas import IngredienteCreate, IngredienteUpdate, IngredienteOut
from app.modules.ingredientes.uow import IngredienteUnitOfWork
from app.core.errors import http_error


class IngredienteService:
    def __init__(self, session: Session) -> None:
        self._session = session
    

    def _get_or_404(self, uow: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise http_error(404, f"Ingrediente con id {ingrediente_id} no encontrado", "NOT_FOUND", "ingrediente_id")
        return ingrediente
    

    def create(self, data: IngredienteCreate) -> IngredienteOut:
        with IngredienteUnitOfWork(self._session) as uow:
            existing = uow.ingredientes.get_by_nombre(data.nombre)
            if existing:
                raise http_error(409, "Ya existe un ingrediente con ese nombre", "ALREADY_EXISTS", "nombre")
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
            uow.ingredientes.soft_delete(ingrediente)