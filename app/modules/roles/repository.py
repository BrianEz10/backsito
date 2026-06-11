from sqlmodel import Session
from app.core.repository import BaseRepository
from app.modules.roles.models import Rol

# Se creo el repository, ya que el modulo admin en el service necesita consumir los datos de roles

class RolRepository(BaseRepository[Rol]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Rol)