from sqlalchemy import func
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.repository import BaseRepository
from app.modules.productos.models import Producto
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.productos.associations import ProductoCategoria, ProductoIngrediente
from app.modules.ingredientes.models import Ingrediente


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


    def get_unidad_medida(self, unidad_medida_id: int) -> UnidadMedida | None:
        return self.session.get(UnidadMedida, unidad_medida_id)


    #Para el "catalog_endpoints.py"
    def get_all_unidades_medida(self) -> list[UnidadMedida]:
        return list(self.session.exec(
            select(UnidadMedida).where(UnidadMedida.deleted_at.is_(None))
        ).all())


    def count_by(self, categoria_id: int | None = None, disponible: bool | None = None, buscar: str | None = None) -> int:
        stmt = select(Producto).where(Producto.deleted_at == None)
        if categoria_id is not None:
            stmt = stmt.join(ProductoCategoria).where(ProductoCategoria.categoria_id == categoria_id)
        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)
        if buscar:
            stmt = stmt.where(Producto.nombre.ilike(f"%{buscar}%"))
        return self.session.exec(
            select(func.count()).select_from(stmt.subquery())
        ).one()


    def find_by(self, categoria_id: int | None = None, disponible: bool | None = None, buscar: str | None = None, offset: int = 0, limit: int = 20) -> list[Producto]:
        stmt = select(Producto).where(Producto.deleted_at == None)
        if categoria_id is not None:
            stmt = stmt.join(ProductoCategoria).where(
                ProductoCategoria.categoria_id == categoria_id
            ).distinct()
        if disponible is not None:
            stmt = stmt.where(Producto.disponible == disponible)
        if buscar:
            stmt = stmt.where(Producto.nombre.ilike(f"%{buscar}%"))
        stmt = stmt.offset(offset).limit(limit).order_by(Producto.id)
        return list(self.session.exec(stmt).all())


    def get_categoria_links(self, producto_id: int) -> list[ProductoCategoria]:
        return list(self.session.exec(
            select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
        ).all())


    def get_ingrediente_links(self, producto_id: int) -> list[ProductoIngrediente]:
        return list(self.session.exec(
            select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
        ).all())
    

    def get_ingredientes_detalle(self, producto_id: int) -> list[tuple[Ingrediente, bool]]:
        return list(self.session.exec(
            select(Ingrediente, ProductoIngrediente.es_removible)
            .join(ProductoIngrediente, Ingrediente.id == ProductoIngrediente.ingrediente_id)
            .where(ProductoIngrediente.producto_id == producto_id)
        ).all())