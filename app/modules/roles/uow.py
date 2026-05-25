from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.roles.repository import RolRepository
class RolUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.roles = RolRepository(session)