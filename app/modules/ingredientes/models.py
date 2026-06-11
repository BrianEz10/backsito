from sqlmodel import Field, Relationship
from app.core.base import Base
from app.modules.productos.associations import ProductoIngrediente
from typing import TYPE_CHECKING #Para que no rompa los  el Pylance

if TYPE_CHECKING:
    from app.modules.productos.models import Producto

class Ingrediente(Base, table=True):
    __tablename__: str = "ingredientes"

    nombre: str = Field(unique=True)
    descripcion: str | None = None
    es_alergeno: bool = Field(default=False)

    productos: list["Producto"] = Relationship(
        back_populates="ingredientes", link_model=ProductoIngrediente
    )