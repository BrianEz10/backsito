from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.categorias.models import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Categoria)
    
    def get_by_id(self, id: int) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None)
        ).first()
    
    def get_by_name(self, nombre: str) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(Categoria.nombre == nombre, Categoria.deleted_at == None)
        ).first()
    
    def get_all(self, offset: int = 0, limit: int = 20) -> list[Categoria]:
        return list(
            self.session.exec(
                select(Categoria).where(Categoria.deleted_at == None)
                .offset(offset).limit(limit)
            ).all()
        )
    
    def get_all_active(self) -> list[Categoria]:
        return list(
            self.session.exec(
                select(Categoria).where(Categoria.deleted_at == None)
            ).all()
        )