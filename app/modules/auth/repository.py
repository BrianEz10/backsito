from sqlmodel import select
from app.core.repository import BaseRepository
from app.modules.auth.models import Usuario

class UsuarioRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Usuario)
    
    def get_by_email(self, email: str) -> Usuario | None:
        stmt = select(Usuario).where(
            Usuario.email == email, Usuario.deleted_at == None
        )
        return self.session.exec(stmt).first()