from sqlmodel import Field, Relationship, Column
from sqlalchemy import ARRAY, String
from app.core.base import Base
from app.modules.productos.associations import ProductoCategoria, ProductoIngrediente
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.modules.categorias.models import Categoria
    from app.modules.ingredientes.models import Ingrediente


class Producto(Base, table=True):
    __tablename__: str = "productos"

    nombre: str
    descripcion: str | None = None
    precio_base: float = Field(default=0)
    imagenes_url: list[str] | None = Field(default=None, sa_column=Column(ARRAY(String)))
    stock_cantidad: int = Field(default=0)
    disponible: bool = Field(default=True)
    unidad_venta_id: int | None = Field(default=None, foreign_key="unidad_medida.id")
    
    categorias: list["Categoria"] = Relationship(
        back_populates="productos", link_model=ProductoCategoria
    )
    ingredientes: list["Ingrediente"] = Relationship(
        back_populates="productos", link_model=ProductoIngrediente
    )
    producto_ingredientes: list["ProductoIngrediente"] = Relationship(
        back_populates="producto"
    )