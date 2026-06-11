from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.roles.repository import RolRepository


class AdminUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.usuarios = UsuarioRepository(session)
        self.roles = RolRepository(session)