from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.direcciones.repository import DireccionRepository

class DireccionUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.direcciones = DireccionRepository(session)