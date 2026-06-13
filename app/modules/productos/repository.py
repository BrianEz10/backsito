from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.repository import BaseRepository
from app.modules.productos.models import Producto


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)
    

    def get_by_id(self, id: int) -> Producto | None:
        return self.session.exec(
            select(Producto)
            .where(Producto.id == id, Producto.deleted_at == None)
            .options(selectinload(Producto.categorias))
            .options(selectinload(Producto.ingredientes))
        ).first()
    
    
    def get_all(self, offset: int = 0, limit: int = 20) -> list[Producto]:
        return list(
            self.session.exec(
                select(Producto)
                .where(Producto.deleted_at == None)
                .options(selectinload(Producto.categorias))
                .options(selectinload(Producto.ingredientes))
                .offset(offset).limit(limit)
            ).all()
        )