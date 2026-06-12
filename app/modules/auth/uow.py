from sqlmodel import Session
from app.core.uow import UnitOfWork
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.auth.refresh_repository import RefreshTokenRepository

class AuthUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.usuarios = UsuarioRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)