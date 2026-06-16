from sqlalchemy import func
from sqlmodel import Session, select
from app.modules.categorias.schemas import CategoriaOut
from app.modules.ingredientes.schemas import IngredienteOut
from app.modules.productos.models import Producto
from app.modules.productos.schemas import IngredienteEnProductoOut, IngredienteEnProductoRequest, IngredientePersonalizadoOut, ProductoCreate, ProductoDetail, ProductoIngredienteRead, ProductoUpdate, ProductoOut, PaginatedProductos
from app.modules.productos.uow import ProductoUnitOfWork
from app.modules.productos.associations import ProductoCategoria, ProductoIngrediente
from app.modules.categorias.models import Categoria
from app.modules.ingredientes.models import Ingrediente
from app.modules.unidad_medida.models import UnidadMedida
from app.core.errors import http_error


class ProductoService:
    def __init__(self, session: Session) -> None:
        self._session = session
    

    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise http_error(404, "Producto no encontrado", "NOT_FOUND", "producto_id")
        return producto
    

    def create(self, data: ProductoCreate) -> ProductoOut:
        with ProductoUnitOfWork(self._session) as uow:
            producto = Producto(**data.model_dump(exclude={"categorias", "ingredientes"}))
            uow.productos.add(producto)
            if data.unidad_venta_id is not None:
                um = uow.productos.session.get(UnidadMedida, data.unidad_venta_id)
                if not um:
                    raise http_error(400, "Unidad de medida no encontrada", "NOT_FOUND", "unidad_venta_id")
            principales = [c for c in data.categorias if c.es_principal]
            if len(principales) > 1:
                raise http_error(400, "Solo puede haber una categoría principal por producto", "BAD_REQUEST", "categorias")
            for cat_data in data.categorias:
                cat = uow.productos.session.get(Categoria, cat_data.categoria_id)
                if not cat:
                    raise http_error(404, "Categoria no encontrada", "NOT_FOUND", "categoria_id")
                link = ProductoCategoria(
                    producto_id=producto.id,
                    categoria_id=cat_data.categoria_id,
                    es_principal=cat_data.es_principal,
                )
                uow.productos.session.add(link)
            for ing_data in data.ingredientes:
                ing = uow.productos.session.get(Ingrediente, ing_data.ingrediente_id)
                if not ing:
                    raise http_error(404, "Ingrediente no encontrado", "NOT_FOUND", "ingrediente_id")
                if ing_data.cantidad <= 0:
                    raise http_error(400, "La cantidad debe ser mayor a 0", "BAD_REQUEST", "cantidad")
                link = ProductoIngrediente(
                    producto_id=producto.id,
                    ingrediente_id=ing_data.ingrediente_id,
                    cantidad=ing_data.cantidad,
                    unidad_medida_id=ing_data.unidad_medida_id,
                    es_removible=ing_data.es_removible,
                )
                uow.productos.session.add(link)
            result = ProductoOut.model_validate(producto)
        return result
    

    def get_all(self, categoria_id: int | None = None, disponible: bool | None = None,
                buscar: str | None = None, page: int = 1, size: int = 20) -> PaginatedProductos:
        with ProductoUnitOfWork(self._session) as uow:
            stmt = select(Producto).where(Producto.deleted_at == None)
            if categoria_id is not None:
                stmt = stmt.join(ProductoCategoria).where(
                    ProductoCategoria.categoria_id == categoria_id
                ).distinct()
            if disponible is not None:
                stmt = stmt.where(Producto.disponible == disponible)
            if buscar:
                stmt = stmt.where(Producto.nombre.ilike(f"%{buscar}%"))

            total = uow.productos.session.exec(
                select(func.count()).select_from(stmt.subquery())
            ).one()

            stmt = stmt.offset((page - 1) * size).limit(size).order_by(Producto.id)
            productos = uow.productos.session.exec(stmt).all()
            result = [ProductoOut.model_validate(p) for p in productos]
            pages = (total + size - 1) // size

        return PaginatedProductos(items=result, total=total, page=page, size=size, pages=pages)


    def get_by_id(self, producto_id: int) -> ProductoDetail:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = ProductoDetail.model_validate(producto)
            
            ingredientes = []
            for pi in producto.producto_ingredientes:
                ing = IngredienteEnProductoOut(
                    id=pi.ingrediente.id,
                    nombre=pi.ingrediente.nombre,
                    descripcion=pi.ingrediente.descripcion,
                    es_alergeno=pi.ingrediente.es_alergeno,
                    stock_cantidad=pi.ingrediente.stock_cantidad,
                    es_removible=pi.es_removible,
                )
                ingredientes.append(ing)
            
            result.ingredientes = ingredientes
        return result
    
    def get_ingredientes(self, producto_id: int) -> list[IngredientePersonalizadoOut]:
        with ProductoUnitOfWork(self._session) as uow:
            self._get_or_404(uow, producto_id)
            stmt = (
                select(Ingrediente, ProductoIngrediente.es_removible)
                .join(ProductoIngrediente, Ingrediente.id == ProductoIngrediente.ingrediente_id)
                .where(ProductoIngrediente.producto_id == producto_id)
            )
            rows = uow.productos.session.exec(stmt).all()
            result = [
                IngredientePersonalizadoOut(
                    id=ing.id,
                    nombre=ing.nombre,
                    es_alergeno=ing.es_alergeno,
                    es_removible=es_removible,
                )
                for ing, es_removible in rows
            ]
        return result


    def agregar_ingrediente(self, producto_id: int, data: IngredienteEnProductoRequest) -> ProductoIngredienteRead:
        with ProductoUnitOfWork(self._session) as uow:
            self._get_or_404(uow, producto_id)
            ing = uow.productos.session.get(Ingrediente, data.ingrediente_id)
            if not ing:
                raise http_error(404, "Ingrediente no encontrado", "NOT_FOUND", "ingrediente_id")
            if data.cantidad <= 0:
                raise http_error(400, "La cantidad debe ser mayor a 0", "BAD_REQUEST", "cantidad")
            link = ProductoIngrediente(
                producto_id=producto_id,
                ingrediente_id=data.ingrediente_id,
                cantidad=data.cantidad,
                unidad_medida_id=data.unidad_medida_id,
                es_removible=data.es_removible,
            )
            uow.productos.session.add(link)
            result = ProductoIngredienteRead(
                producto_id=producto_id,
                ingrediente_id=data.ingrediente_id,
                cantidad=data.cantidad,
                unidad_medida_id=data.unidad_medida_id,
                es_removible=data.es_removible,
            )
        return result


    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoOut:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            update_data = data.model_dump(exclude_unset=True, exclude={"categorias", "ingredientes"})
            for field, value in update_data.items():
                setattr(producto, field, value)
            if data.categorias is not None:
                principales = [c for c in data.categorias if c.es_principal]
                if len(principales) > 1:
                    raise http_error(400, "Solo puede haber una categoría principal por producto", "BAD_REQUEST", "categorias")
                old_cat_links = uow.productos.session.exec(
                    select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
                ).all()
                for link in old_cat_links:
                    uow.productos.session.delete(link)

                for cat_data in data.categorias:
                    cat = uow.productos.session.get(Categoria, cat_data.categoria_id)
                    if not cat:
                        raise http_error(404, "Categoria no encontrada", "NOT_FOUND", "categoria_id")
                    link = ProductoCategoria(
                        producto_id=producto.id,
                        categoria_id=cat_data.categoria_id,
                        es_principal=cat_data.es_principal,
                    )
                    uow.productos.session.add(link)

            if data.ingredientes is not None:
                old_ing_links = uow.productos.session.exec(
                    select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
                ).all()
                for link in old_ing_links:
                    uow.productos.session.delete(link)
                for ing_data in data.ingredientes:
                    ing = uow.productos.session.get(Ingrediente, ing_data.ingrediente_id)
                    if not ing:
                        raise http_error(404, f"Ingrediente {ing_data.ingrediente_id} no encontrado", "NOT_FOUND", "ingrediente_id")
                    if ing_data.cantidad <= 0:
                        raise http_error(400, "La cantidad debe ser mayor a 0", "BAD_REQUEST", "cantidad")
                    link = ProductoIngrediente(
                        producto_id=producto_id,
                        ingrediente_id=ing_data.ingrediente_id,
                        cantidad=ing_data.cantidad,
                        unidad_medida_id=ing_data.unidad_medida_id,
                        es_removible=ing_data.es_removible,
                    )
                    uow.productos.session.add(link)
            uow.productos.add(producto)
            result = ProductoOut.model_validate(producto)
        return result
    

    def update_imagenes(self, producto_id: int, imagenes_url: list[str]) -> ProductoOut:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.imagenes_url = imagenes_url
            result = ProductoOut.model_validate(producto)
        return result
    

    def toggle_disponibilidad(self, producto_id: int, disponible: bool) -> ProductoOut:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.disponible = disponible
            result = ProductoOut.model_validate(producto)
        return result
    
    
    def delete(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            uow.productos.soft_delete(producto)