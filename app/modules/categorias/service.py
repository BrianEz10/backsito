from sqlmodel import Session, select
from app.modules.categorias.models import Categoria
from app.modules.categorias.schemas import CategoriaCreate, CategoriaUpdate, CategoriaOut, CategoriaWithHijos
from app.modules.categorias.uow import CategoriaUnitOfWork
from app.modules.productos.associations import ProductoCategoria
from app.core.errors import http_error

class CategoriaService:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def _get_or_404(self, uow: CategoriaUnitOfWork, categoria_id: int) -> Categoria:
        categoria = uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise http_error(404, f"Categoria con id {categoria_id} no encontrada", "NOT_FOUND", "categoria_id")
        return categoria
    
    def _assert_name_unique(self, uow: CategoriaUnitOfWork, nombre: str) -> None:
        if uow.categorias.get_by_name(nombre):
            raise http_error(409, f"Ya existe una categoria con nombre '{nombre}'", "ALREADY_EXISTS", "nombre")
    
    def create(self, data: CategoriaCreate) -> CategoriaOut:
        with CategoriaUnitOfWork(self._session) as uow:
            self._assert_name_unique(uow, data.nombre)
            if data.parent_id is not None:
                parent = uow.categorias.get_by_id(data.parent_id)
                if not parent:
                    raise http_error(400, f"Categoria padre no encontrada", "NOT_FOUND", "parent_id")
            categoria = Categoria.model_validate(data)
            uow.categorias.add(categoria)
            result = CategoriaOut.model_validate(categoria)
        return result
    
    def get_all(self, parent_id: int | None = None, offset: int = 0, limit: int = 20) -> list[CategoriaOut]:
        with CategoriaUnitOfWork(self._session) as uow:
            stmt = select(Categoria).where(Categoria.deleted_at == None)
            if parent_id == -1:
                stmt = stmt.where(Categoria.parent_id == None)
            elif parent_id is not None:
                stmt = stmt.where(Categoria.parent_id == parent_id)
            stmt = stmt.offset(offset).limit(limit).order_by(Categoria.id)
            categorias = uow.categorias.session.exec(stmt).all()
            result = [CategoriaOut.model_validate(c) for c in categorias]
        return result

    def get_by_id(self, categoria_id: int) -> CategoriaWithHijos:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            hijos = [h for h in categoria.hijos if h.deleted_at is None]
            categoria.hijos = hijos
            result = CategoriaWithHijos.model_validate(categoria)
        return result
    
    def update(self, categoria_id: int, data: CategoriaUpdate) -> CategoriaOut:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            if data.parent_id is not None:
                if data.parent_id == categoria_id:
                    raise http_error(400, "Una categoria no puede ser padre de si misma", "BAD_REQUEST", "parent_id")
                parent = uow.categorias.get_by_id(data.parent_id)
                if not parent:
                    raise http_error(400, f"Categoria padre no encontrada", "NOT_FOUND", "parent_id")
            patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                if field == "nombre":
                    existing = uow.categorias.get_by_name(value)
                    if existing and existing.id != categoria_id:
                        raise http_error(409, f"Ya existe una categoria con nombre '{value}'", "ALREADY_EXISTS", "nombre")
                setattr(categoria, field, value)
            uow.categorias.add(categoria)
            result = CategoriaOut.model_validate(categoria)
        return result
    
    def delete(self, categoria_id: int) -> None:
        with CategoriaUnitOfWork(self._session) as uow:
            categoria = self._get_or_404(uow, categoria_id)
            productos_asociados = uow.categorias.session.exec(
                select(ProductoCategoria).where(ProductoCategoria.categoria_id == categoria_id)
            ).first()
            if productos_asociados:
                raise http_error(409, "No se puede eliminar: tiene productos asociados", "BAD_REQUEST")
            uow.categorias.soft_delete(categoria)