from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.categorias.models import Categoria
from app.modules.productos.associations import ProductoCategoria


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
    

    def find_by_parent(self, parent_id: int | None = None, offset: int = 0, limit: int = 20) -> list[Categoria]:
        stmt = select(Categoria).where(Categoria.deleted_at == None)
        if parent_id == -1:
            stmt = stmt.where(Categoria.parent_id == None)
        elif parent_id is not None:
            stmt = stmt.where(Categoria.parent_id == parent_id)
        stmt = stmt.offset(offset).limit(limit).order_by(Categoria.id)
        return list(self.session.exec(stmt).all())


    def check_productos_asociados(self, categoria_id: int) -> bool:
        return self.session.exec(
            select(ProductoCategoria).where(ProductoCategoria.categoria_id == categoria_id)
        ).first()