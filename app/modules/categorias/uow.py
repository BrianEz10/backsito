from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.categorias.repository import CategoriaRepository

class CategoriaUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.categorias = CategoriaRepository(session)