from sqlmodel import Field, Relationship
from app.core.base import Base
from app.modules.productos.associations import ProductoCategoria
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.productos.models import Producto

class Categoria(Base, table = True):
    __tablename__: str = "categorias"

    nombre: str
    descripcion: str | None = None
    imagen_url: str | None = None
    parent_id: int | None = Field(default = None, foreign_key = "categorias.id")

    parent: "Categoria" = Relationship(
        back_populates="hijos",
        sa_relationship_kwargs={
            "remote_side": "Categoria.id",
            "lazy": "select",
        }
    )
    hijos: list["Categoria"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"lazy": "select"}
    )

    productos: list["Producto"] = Relationship(
        back_populates="categorias", link_model=ProductoCategoria
    )