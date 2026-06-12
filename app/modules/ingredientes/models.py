from sqlmodel import Field, Relationship
from app.core.base import Base
from app.modules.productos.associations import ProductoIngrediente
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.modules.productos.models import Producto


class Ingrediente(Base, table=True):
    __tablename__: str = "ingredientes"

    nombre: str = Field(unique=True)
    descripcion: str | None = None
    es_alergeno: bool = Field(default=False)
    stock_cantidad: int = Field(default=0, ge=0)

    productos: list["Producto"] = Relationship(
        back_populates="ingredientes", link_model=ProductoIngrediente
    )