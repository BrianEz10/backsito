from sqlmodel import select
from app.core.repository import BaseRepository
from app.modules.roles.models import Rol

class RolRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Rol)
    
    def get_by_codigo(self, codigo: str) -> Rol | None:
        stmt = select(Rol).where(Rol.codigo == codigo)
        return self.session.exec(stmt).first()
    
    def get_all(self):
        stmt = select(Rol)
        return self.session.exec(stmt).all()