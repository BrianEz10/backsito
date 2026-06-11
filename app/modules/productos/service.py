from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.modules.productos.models import Producto
from app.modules.productos.schemas import ProductoCreate, ProductoUpdate, ProductoOut
from app.modules.productos.uow import ProductoUnitOfWork
from app.modules.productos.associations import ProductoCategoria, ProductoIngrediente
from app.modules.categorias.models import Categoria
from app.modules.ingredientes.models import Ingrediente
from app.modules.unidad_medida.models import UnidadMedida

class ProductoService:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Producto no encontrado")
        return producto
    
    def create(self, data: ProductoCreate) -> ProductoOut:
        with ProductoUnitOfWork(self._session) as uow:
            producto = Producto(**data.model_dump(exclude={"categorias", "ingredientes"}))
            uow.productos.add(producto)
            if data.unidad_venta_id is not None:
                um = uow.productos.session.get(UnidadMedida, data.unidad_venta_id)
                if not um:
                    raise HTTPException(400, "Unidad de medida no encontrada")
            principales = [c for c in data.categorias if c.es_principal]
            if len(principales) > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Solo puede haber una categoría principal por producto",
                )
            for cat_data in data.categorias:
                cat = uow.productos.session.get(Categoria, cat_data.categoria_id)
                if not cat:
                    raise HTTPException(404, "Categoria no encontrada")
                link = ProductoCategoria(
                    producto_id=producto.id,
                    categoria_id=cat_data.categoria_id,
                    es_principal=cat_data.es_principal,
                )
                uow.productos.session.add(link)
            for ing_data in data.ingredientes:
                ing = uow.productos.session.get(Ingrediente, ing_data.ingrediente_id)
                if not ing:
                    raise HTTPException(404, f"Ingrediente no encontrado")
                if ing_data.cantidad <= 0:
                    raise HTTPException(400, "La cantidad debe ser mayor a 0")
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
    
    def get_all(self, categoria_id: int | None = None, disponible: bool | None = None, buscar: str | None = None, offset: int = 0, limit: int = 20) -> list[ProductoOut]:
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
            stmt = stmt.offset(offset).limit(limit).order_by(Producto.id)
            productos = uow.productos.session.exec(stmt).all()
            result = [ProductoOut.model_validate(p) for p in productos]
        return result

    def get_by_id(self, producto_id: int) -> ProductoOut:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = ProductoOut.model_validate(producto)
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
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Solo puede haber una categoría principal por producto",
                    )
                old_cat_links = uow.productos.session.exec(
                    select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
                ).all()
                for link in old_cat_links:
                    uow.productos.session.delete(link)

                for cat_data in data.categorias:
                    cat = uow.productos.session.get(Categoria, cat_data.categoria_id)
                    if not cat:
                        raise HTTPException(404, "Categoria no encontrada")
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
                        raise HTTPException(404, f"Ingrediente {ing_data.ingrediente_id} no encontrado")
                    if ing_data.cantidad <= 0:
                        raise HTTPException(400, "La cantidad debe ser mayor a 0")
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
    
    def toggle_disponibilidad(self, producto_id: int, disponible: bool) -> ProductoOut:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.disponible = disponible
            result = ProductoOut.model_validate(producto)
        return result
    
    def delete(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.deleted_at = datetime.now(timezone.utc)