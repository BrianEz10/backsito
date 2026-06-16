from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from app.core.database import SessionDep
from app.core.deps import require_role
from app.modules.usuarios.models import Usuario
from app.modules.productos.schemas import DisponibilidadRequest, IngredienteEnProductoRequest, ProductoCreate, ProductoDetail, ProductoIngredienteRead, ProductoUpdate, ProductoOut, PaginatedProductos
from app.modules.productos.schemas import IngredientePersonalizadoOut
from app.modules.productos.service import ProductoService
from app.modules.uploads.schemas import ImagenProductoUpdate


router = APIRouter(prefix="/productos", tags=["productos"])


def get_producto_service(session: SessionDep) -> ProductoService:
    return ProductoService(session)


@router.get("/", response_model=PaginatedProductos)
def listar(categoria_id: int | None = Query(default=None), disponible: bool | None = Query(default=None), buscar: str | None = Query(default=None), page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), svc: ProductoService = Depends(get_producto_service)) -> PaginatedProductos:
    return svc.get_all(categoria_id, disponible, buscar, page, size)


@router.get("/{id}", response_model=ProductoDetail)
def obtener(id: int, svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.get_by_id(id)


@router.get("/{id}/ingredientes", response_model=list[IngredientePersonalizadoOut])
def listar_ingredientes(id: int, svc: ProductoService = Depends(get_producto_service)) -> list[IngredientePersonalizadoOut]:
    return svc.get_ingredientes(id)


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: ProductoCreate, svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.create(data)


@router.post("/{id}/ingredientes", response_model=ProductoIngredienteRead, status_code=status.HTTP_201_CREATED)
def agregar_ingrediente(id: int, data: IngredienteEnProductoRequest, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: ProductoService = Depends(get_producto_service)) -> ProductoIngredienteRead:
    return svc.agregar_ingrediente(id, data)


@router.put("/{id}", response_model=ProductoOut)
def actualizar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN","STOCK"]))], data: ProductoUpdate, svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.update(id, data)


@router.patch("/{id}/disponibilidad", response_model=ProductoOut)
def toggle_disponibilidad(id: int, data: DisponibilidadRequest, _admin_stock: Annotated[Usuario, Depends(require_role(["ADMIN", "STOCK"]))], svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.toggle_disponibilidad(id, data.disponible)


@router.patch("/{id}/imagenes", response_model=ProductoOut)
def actualizar_imagenes(id: int, data: ImagenProductoUpdate, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.update_imagenes(id, data.imagenes_url)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: ProductoService = Depends(get_producto_service)) -> None:
    svc.delete(id)