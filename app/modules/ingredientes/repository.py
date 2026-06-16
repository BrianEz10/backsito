from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.ingredientes.models import Ingrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)
    

    def get_by_id(self, id: int) -> Ingrediente | None:
        return self.session.exec(
            select(Ingrediente).where(Ingrediente.id == id, Ingrediente.deleted_at == None)
        ).first()
    

    def get_all(self, offset: int = 0, limit: int = 200) -> list[Ingrediente]:
        return list(
            self.session.exec(
                select(Ingrediente).where(Ingrediente.deleted_at == None)
                .order_by(Ingrediente.id)
                .offset(offset).limit(limit)
            ).all()
        )
    
    
    def get_by_nombre(self, nombre: str) -> Ingrediente | None:
        return self.session.exec(
            select(Ingrediente).where(Ingrediente.nombre == nombre)
        ).first()