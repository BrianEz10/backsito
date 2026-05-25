from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from app.core.database import SessionDep
from app.core.deps import CurrentUser, require_role
from app.modules.auth.models import Usuario
from app.modules.productos.schemas import DisponibilidadRequest, ProductoCreate, ProductoUpdate, ProductoOut
from app.modules.productos.service import ProductoService


router = APIRouter(prefix="/productos", tags=["productos"])

def get_producto_service(session: SessionDep) -> ProductoService:
    return ProductoService(session)

@router.get("/", response_model=list[ProductoOut])
def listar(_user: CurrentUser, categoria_id: int | None = Query(default=None), disponible: bool | None = Query(default=None), buscar: str | None = Query(default=None), offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), svc: ProductoService = Depends(get_producto_service)) -> list[ProductoOut]:
    return svc.get_all(categoria_id, disponible, buscar, offset, limit)


@router.get("/{id}", response_model=ProductoOut)
def obtener(id: int, _user: CurrentUser, svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.get_by_id(id)


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear(_admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: ProductoCreate, svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.create(data)


@router.patch("/{id}", response_model=ProductoOut)
def actualizar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], data: ProductoUpdate, svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.update(id, data)

@router.patch("/{id}/disponibilidad", response_model=ProductoOut)
def toggle_disponibilidad(id: int, data: DisponibilidadRequest, _admin_stock: Annotated[Usuario, Depends(require_role(["ADMIN", "STOCK"]))], svc: ProductoService = Depends(get_producto_service)) -> ProductoOut:
    return svc.toggle_disponibilidad(id, data.disponible)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id: int, _admin: Annotated[Usuario, Depends(require_role(["ADMIN"]))], svc: ProductoService = Depends(get_producto_service)) -> None:
    svc.delete(id)